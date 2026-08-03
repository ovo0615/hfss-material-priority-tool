# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# HFSS Material Priority Subtractor (TableLayout Bulletproof Version)
# -------------------------------------------------------------------------

import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
from System.Windows.Forms import (Form, Label, ListBox, Button, DockStyle, 
                                  SelectionMode, MessageBox, Panel, ScrollBars,
                                  Padding, FormBorderStyle, FormStartPosition, 
                                  Application, AnchorStyles, TableLayoutPanel,
                                  RowStyle, SizeType, ColumnStyle)
from System.Drawing import Color, Font, Point, Size, ContentAlignment, FontStyle

# Attribution: \u6d2a\u656c\u5091 = 洪敬傑
ATTRIBUTION = u"\u6b64\u5de5\u5177\u7531\u864e\u9580\u79d1\u6280\u8cc7\u6df1\u6280\u8853\u5de5\u7a0b\u5e2bJeff Hong\u6d2a\u656c\u5091\u63d0\u4f9b"

class MaterialPriorityTool(Form):
    def __init__(self):
        self.Text = "HFSS Material Priority Tool (IronPython)"
        self.Size = Size(550, 750)
        self.MinimumSize = Size(480, 650)
        self.BackColor = Color.FromArgb(44, 62, 80)
        self.FormBorderStyle = FormBorderStyle.Sizable
        self.StartPosition = FormStartPosition.CenterScreen
        self.oDesktop = None
        self.oEditor = None
        self.material_dict = {}
        self.setup_ui()
        
    def setup_ui(self):
        # Master Layout
        master_table = TableLayoutPanel()
        master_table.Dock = DockStyle.Fill
        master_table.RowCount = 4
        master_table.ColumnCount = 1
        
        # Define Rows: Header(80), TopUI(100), ListBox(Percent), RunArea(100), Attribution(40)
        master_table.RowStyles.Add(RowStyle(SizeType.Absolute, 70))  # Header
        master_table.RowStyles.Add(RowStyle(SizeType.Absolute, 100)) # Connect & Hint
        master_table.RowStyles.Add(RowStyle(SizeType.Percent, 100))  # ListBox Area
        master_table.RowStyles.Add(RowStyle(SizeType.Absolute, 120)) # Run & Footer
        self.Controls.Add(master_table)
        
        # 1. Header
        header = Label()
        header.Text = "HFSS Material Priority Tool"
        header.Font = Font("Segoe UI", 18, FontStyle.Bold)
        header.ForeColor = Color.White
        header.BackColor = Color.FromArgb(52, 73, 94)
        header.Dock = DockStyle.Fill
        header.TextAlign = ContentAlignment.MiddleCenter
        master_table.Controls.Add(header, 0, 0)
        
        # 2. Top UI (Connect Button & Label)
        top_panel = Panel()
        top_panel.Dock = DockStyle.Fill
        top_panel.Padding = Padding(15, 10, 15, 5)
        master_table.Controls.Add(top_panel, 0, 1)
        
        self.btn_connect = Button()
        self.btn_connect.Text = "1. Connect to Active Design"
        self.btn_connect.Dock = DockStyle.Top
        self.btn_connect.Height = 45
        self.btn_connect.BackColor = Color.FromArgb(52, 152, 219)
        self.btn_connect.ForeColor = Color.White
        self.btn_connect.Font = Font("Segoe UI", 11, FontStyle.Bold)
        self.btn_connect.Click += self.on_connect
        top_panel.Controls.Add(self.btn_connect)
        
        lbl_hint = Label()
        lbl_hint.Text = "Priority Order (Top = Highest Priority):"
        lbl_hint.ForeColor = Color.White
        lbl_hint.Dock = DockStyle.Bottom
        lbl_hint.Height = 30
        lbl_hint.TextAlign = ContentAlignment.BottomLeft
        lbl_hint.Font = Font("Segoe UI", 10, FontStyle.Italic)
        top_panel.Controls.Add(lbl_hint)
        
        # 3. List Area (Split into List and Up/Down Buttons)
        list_table = TableLayoutPanel()
        list_table.Dock = DockStyle.Fill
        list_table.Padding = Padding(15, 0, 15, 0)
        list_table.ColumnCount = 2
        list_table.RowCount = 1
        list_table.ColumnStyles.Add(ColumnStyle(SizeType.Percent, 100))
        list_table.ColumnStyles.Add(ColumnStyle(SizeType.Absolute, 120))
        master_table.Controls.Add(list_table, 0, 2)
        
        self.lb_materials = ListBox()
        self.lb_materials.Dock = DockStyle.Fill
        self.lb_materials.BackColor = Color.White
        self.lb_materials.Font = Font("Segoe UI", 12)
        self.lb_materials.IntegralHeight = False
        list_table.Controls.Add(self.lb_materials, 0, 0)
        
        btn_panel = Panel()
        btn_panel.Dock = DockStyle.Fill
        list_table.Controls.Add(btn_panel, 1, 0)
        
        self.btn_up = Button()
        self.btn_up.Text = u"Move Up \u2191"
        self.btn_up.Size = Size(100, 45)
        self.btn_up.Location = Point(10, 10)
        self.btn_up.BackColor = Color.FromArgb(149, 165, 166)
        self.btn_up.Click += self.on_move_up
        btn_panel.Controls.Add(self.btn_up)
        
        self.btn_down = Button()
        self.btn_down.Text = u"Move Down \u2193"
        self.btn_down.Size = Size(100, 45)
        self.btn_down.Location = Point(10, 65)
        self.btn_down.BackColor = Color.FromArgb(149, 165, 166)
        self.btn_down.Click += self.on_move_down
        btn_panel.Controls.Add(self.btn_down)
        
        # 4. Bottom Area (Run Button & Attribution)
        bot_panel = Panel()
        bot_panel.Dock = DockStyle.Fill
        bot_panel.Padding = Padding(15, 10, 15, 0)
        master_table.Controls.Add(bot_panel, 0, 3)
        
        self.btn_run = Button()
        self.btn_run.Text = "RUN SUBTRACTION"
        self.btn_run.Dock = DockStyle.Top
        self.btn_run.Height = 55
        self.btn_run.BackColor = Color.FromArgb(46, 204, 113)
        self.btn_run.ForeColor = Color.White
        self.btn_run.Font = Font("Segoe UI", 14, FontStyle.Bold)
        self.btn_run.Enabled = False
        self.btn_run.Click += self.on_run
        bot_panel.Controls.Add(self.btn_run)
        
        attr_label = Label()
        attr_label.Text = ATTRIBUTION
        attr_label.Dock = DockStyle.Bottom
        attr_label.Height = 40
        attr_label.ForeColor = Color.FromArgb(189, 195, 199)
        attr_label.TextAlign = ContentAlignment.MiddleCenter
        attr_label.Font = Font("Microsoft JhengHei", 10)
        bot_panel.Controls.Add(attr_label)

    def on_connect(self, sender, args):
        try:
            self.oDesktop = oDesktop 
        except:
            MessageBox.Show("Run inside HFSS.")
            return
            
        oProject = self.oDesktop.GetActiveProject()
        oDesign = oProject.GetActiveDesign()
        self.oEditor = oDesign.SetActiveEditor("3D Modeler")
        
        all_objects = self.oEditor.GetMatchedObjectName("*")
        self.material_dict = {}
        
        for obj in all_objects:
            try:
                mat = self.oEditor.GetPropertyValue("Geometry3DAttributeTab", obj, "Material")
                if mat:
                    if mat not in self.material_dict: self.material_dict[mat] = []
                    self.material_dict[mat].append(obj)
            except: continue
        
        self.lb_materials.Items.Clear()
        for mat in sorted(self.material_dict.keys()):
            self.lb_materials.Items.Add(mat)
        self.btn_run.Enabled = (self.lb_materials.Items.Count > 0)
        self.btn_connect.Text = "Connected: " + oProject.GetName()

    def on_move_up(self, sender, args):
        idx = self.lb_materials.SelectedIndex
        if idx > 0:
            item = self.lb_materials.SelectedItem
            self.lb_materials.Items.RemoveAt(idx)
            self.lb_materials.Items.Insert(idx - 1, item)
            self.lb_materials.SelectedIndex = idx - 1

    def on_move_down(self, sender, args):
        idx = self.lb_materials.SelectedIndex
        if idx != -1 and idx < self.lb_materials.Items.Count - 1:
            item = self.lb_materials.SelectedItem
            self.lb_materials.Items.RemoveAt(idx)
            self.lb_materials.Items.Insert(idx + 1, item)
            self.lb_materials.SelectedIndex = idx + 1

    def on_run(self, sender, args):
        ordered_mats = [self.lb_materials.Items[i] for i in range(self.lb_materials.Items.Count)]
        for i in range(len(ordered_mats)):
            high_mat = ordered_mats[i]
            all_objs = self.oEditor.GetMatchedObjectName("*")
            tool_parts = [p for p in self.material_dict[high_mat] if p in all_objs]
            if not tool_parts: continue
            for j in range(i + 1, len(ordered_mats)):
                low_mat = ordered_mats[j]
                blank_parts = [p for p in self.material_dict[low_mat] if p in all_objs]
                if not blank_parts: continue
                try:
                    self.oEditor.Subtract(["NAME:Selections", "Blank Parts:=", ",".join(blank_parts), "Tool Parts:=", ",".join(tool_parts)], ["NAME:SubtractParameters", "KeepOriginals:=", True])
                except: pass
        MessageBox.Show("Boolean Operations Finished!")

if __name__ == "__main__":
    form = MaterialPriorityTool()
    form.Show()
    while form.Visible:
        Application.DoEvents()
