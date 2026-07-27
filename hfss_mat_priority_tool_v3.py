# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# HFSS Material Priority Subtractor (TableLayout Stability Version v3)
# -------------------------------------------------------------------------

import clr
import os
import time
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
from System.Windows.Forms import (Form, Label, ListBox, Button, DockStyle, 
                                  SelectionMode, MessageBox, Panel, ScrollBars,
                                  Padding, FormBorderStyle, FormStartPosition, 
                                  Application, AnchorStyles, TableLayoutPanel,
                                  RowStyle, SizeType, ColumnStyle, SaveFileDialog, OpenFileDialog, DialogResult)
from System.Drawing import Color, Font, Point, Size, ContentAlignment, FontStyle

# Attribution: 洪敬傑 = 洪敬傑
ATTRIBUTION = u"\u6b64\u5de5\u5177\u7531\u864e\u9580\u79d1\u6280\u8cc7\u6df1\u6280\u8853\u5de5\u7a0b\u5e2bJeff Hong\u6d2a\u656c\u5091\u63d0\u4f9b"

class MaterialPriorityToolV3(Form):
    def __init__(self):
        self.Text = "HFSS Material Priority Tool (IronPython) v3"
        self.Size = Size(550, 850)
        self.MinimumSize = Size(480, 750)
        self.BackColor = Color.FromArgb(44, 62, 80)
        self.FormBorderStyle = FormBorderStyle.Sizable
        self.StartPosition = FormStartPosition.CenterScreen
        self.oDesktop = None
        self.oEditor = None
        self.material_dict = {}
        self.setup_ui()
        self.FormClosing += self.on_form_closing
        
    def setup_ui(self):
        # Master Layout
        master_table = TableLayoutPanel()
        master_table.Dock = DockStyle.Fill
        master_table.RowCount = 5
        master_table.ColumnCount = 1
        
        # Define Rows: Header, TopUI, ListBox, Status, RunArea
        master_table.RowStyles.Add(RowStyle(SizeType.Absolute, 70))  # Header
        master_table.RowStyles.Add(RowStyle(SizeType.Absolute, 100)) # Connect & Hint
        master_table.RowStyles.Add(RowStyle(SizeType.Percent, 100))  # ListBox Area
        master_table.RowStyles.Add(RowStyle(SizeType.Absolute, 30))  # Status Label
        master_table.RowStyles.Add(RowStyle(SizeType.Absolute, 120)) # Run & Footer
        self.Controls.Add(master_table)
        
        # 1. Header
        header = Label()
        header.Text = "HFSS Material Priority Tool v3"
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
        
        # 3. List Area (Split into List and Buttons)
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
        self.btn_up.Size = Size(100, 40)
        self.btn_up.Location = Point(10, 10)
        self.btn_up.BackColor = Color.FromArgb(149, 165, 166)
        self.btn_up.Click += self.on_move_up
        btn_panel.Controls.Add(self.btn_up)
        
        self.btn_down = Button()
        self.btn_down.Text = u"Move Down \u2193"
        self.btn_down.Size = Size(100, 40)
        self.btn_down.Location = Point(10, 60)
        self.btn_down.BackColor = Color.FromArgb(149, 165, 166)
        self.btn_down.Click += self.on_move_down
        btn_panel.Controls.Add(self.btn_down)

        self.btn_ignore = Button()
        self.btn_ignore.Text = "Ignore Mat."
        self.btn_ignore.Size = Size(100, 40)
        self.btn_ignore.Location = Point(10, 110)
        self.btn_ignore.BackColor = Color.FromArgb(231, 76, 60)
        self.btn_ignore.ForeColor = Color.White
        self.btn_ignore.Click += self.on_ignore
        btn_panel.Controls.Add(self.btn_ignore)

        self.btn_save = Button()
        self.btn_save.Text = "Save Order"
        self.btn_save.Size = Size(100, 40)
        self.btn_save.Location = Point(10, 160)
        self.btn_save.BackColor = Color.FromArgb(52, 152, 219)
        self.btn_save.ForeColor = Color.White
        self.btn_save.Click += self.on_save
        btn_panel.Controls.Add(self.btn_save)

        self.btn_load = Button()
        self.btn_load.Text = "Load Order"
        self.btn_load.Size = Size(100, 40)
        self.btn_load.Location = Point(10, 210)
        self.btn_load.BackColor = Color.FromArgb(52, 152, 219)
        self.btn_load.ForeColor = Color.White
        self.btn_load.Click += self.on_load
        btn_panel.Controls.Add(self.btn_load)
        
        # 4. Status Label
        self.lbl_status = Label()
        self.lbl_status.Text = "Ready"
        self.lbl_status.ForeColor = Color.FromArgb(189, 195, 199)
        self.lbl_status.Dock = DockStyle.Fill
        self.lbl_status.TextAlign = ContentAlignment.MiddleCenter
        self.lbl_status.Font = Font("Segoe UI", 9)
        master_table.Controls.Add(self.lbl_status, 0, 3)

        # 5. Bottom Area (Run Button & Attribution)
        bot_panel = Panel()
        bot_panel.Dock = DockStyle.Fill
        bot_panel.Padding = Padding(15, 10, 15, 0)
        master_table.Controls.Add(bot_panel, 0, 4)
        
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

    def on_form_closing(self, sender, args):
        self.Visible = False

    def on_connect(self, sender, args):
        try:
            self.oDesktop = oDesktop 
        except:
            MessageBox.Show("Run inside HFSS.")
            return
            
        oProject = self.oDesktop.GetActiveProject()
        oDesign = oProject.GetActiveDesign()
        self.oEditor = oDesign.SetActiveEditor("3D Modeler")
        
        self.lbl_status.Text = "Scanning objects..."
        Application.DoEvents()
        
        all_objects = self.oEditor.GetMatchedObjectName("*")
        self.material_dict = {}
        
        for obj in all_objects:
            try:
                props = self.oEditor.GetProperties("Geometry3DAttributeTab", obj)
                if props and "Material" in list(props):
                    mat = self.oEditor.GetPropertyValue("Geometry3DAttributeTab", obj, "Material")
                    if mat:
                        if mat not in self.material_dict: 
                            self.material_dict[mat] = []
                        self.material_dict[mat].append(obj)
            except: 
                continue
        
        self.lb_materials.Items.Clear()
        for mat in sorted(self.material_dict.keys()):
            self.lb_materials.Items.Add(mat)
        self.btn_run.Enabled = (self.lb_materials.Items.Count > 0)
        self.btn_connect.Text = "Connected: " + oProject.GetName()
        self.lbl_status.Text = "Connected to " + oProject.GetName()

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

    def on_ignore(self, sender, args):
        idx = self.lb_materials.SelectedIndex
        if idx != -1:
            self.lb_materials.Items.RemoveAt(idx)
            if self.lb_materials.Items.Count > 0:
                self.lb_materials.SelectedIndex = min(idx, self.lb_materials.Items.Count - 1)
            else:
                self.btn_run.Enabled = False

    def on_save(self, sender, args):
        if self.lb_materials.Items.Count == 0:
            MessageBox.Show("No materials in list to save.")
            return
        
        dialog = SaveFileDialog()
        dialog.Filter = "Text Files (*.txt)|*.txt|All Files (*.*)|*.*"
        dialog.Title = "Save Priority Order"
        dialog.DefaultExt = "txt"
        if dialog.ShowDialog() == DialogResult.OK:
            try:
                with open(dialog.FileName, "w") as f:
                    for i in range(self.lb_materials.Items.Count):
                        f.write(str(self.lb_materials.Items[i]) + "\n")
                MessageBox.Show(self, "Saved successfully!")
            except Exception as e:
                MessageBox.Show(self, "Error saving: " + str(e))

    def on_load(self, sender, args):
        dialog = OpenFileDialog()
        dialog.Filter = "Text Files (*.txt)|*.txt|All Files (*.*)|*.*"
        dialog.Title = "Load Priority Order"
        if dialog.ShowDialog() == DialogResult.OK:
            try:
                with open(dialog.FileName, "r") as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                
                if not lines:
                    MessageBox.Show(self, "File is empty.")
                    return
                
                current_items = [self.lb_materials.Items[i] for i in range(self.lb_materials.Items.Count)]
                self.lb_materials.Items.Clear()
                
                # Add items from file first
                for item in lines:
                    if item in current_items:
                        self.lb_materials.Items.Add(item)
                        current_items.remove(item)
                    elif item in self.material_dict:
                        self.lb_materials.Items.Add(item)
                
                # Add remaining items that were in the original list but not in the file
                for item in current_items:
                    self.lb_materials.Items.Add(item)
                    
                self.btn_run.Enabled = (self.lb_materials.Items.Count > 0)
            except Exception as e:
                MessageBox.Show(self, "Error loading: " + str(e))

    def on_run(self, sender, args):
        self.btn_run.Enabled = False
        self.btn_run.Text = "RUNNING..."
        ordered_mats = [self.lb_materials.Items[i] for i in range(self.lb_materials.Items.Count)]
        total_steps = len(ordered_mats)
        
        for i in range(total_steps):
            high_mat = ordered_mats[i]
            all_objs_set = set(self.oEditor.GetMatchedObjectName("*"))
            tool_parts = [p for p in self.material_dict.get(high_mat, []) if p in all_objs_set]
            if not tool_parts: continue
            
            self.lbl_status.Text = "Subtracting from " + high_mat + "..."
            Application.DoEvents()
            
            for j in range(i + 1, total_steps):
                low_mat = ordered_mats[j]
                blank_parts = [p for p in self.material_dict.get(low_mat, []) if p in all_objs_set]
                if not blank_parts: continue
                
                try:
                    self.oEditor.Subtract(
                        ["NAME:Selections", "Blank Parts:=", ",".join(blank_parts), "Tool Parts:=", ",".join(tool_parts)], 
                        ["NAME:SubtractParameters", "KeepOriginals:=", True]
                    )
                except:
                    pass
                Application.DoEvents()
            
            if not self.Visible: break
            
        self.lbl_status.Text = "Operation finished."
        self.btn_run.Text = "RUN SUBTRACTION"
        self.btn_run.Enabled = True
        MessageBox.Show(self, "Boolean Operations Finished!")

if __name__ == "__main__":
    form = MaterialPriorityToolV3()
    form.Show()
    try:
        while form.Visible:
            Application.DoEvents()
            time.sleep(0.02)
    except:
        pass
    finally:
        form.oDesktop = None
        form.oEditor = None
        form.Dispose()
