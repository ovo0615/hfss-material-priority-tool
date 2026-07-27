# HFSS Material Priority Tool

自動讀取 HFSS 3D Modeler 中的材料與幾何物件，協助整理與調整材料 Priority，降低複雜模型中的人工檢查與設定時間。

## 主要功能

- 連接目前開啟的 AEDT／HFSS 設計。
- 讀取模型材料資訊。
- 以表格方式檢視與選擇材料項目。
- 執行材料 Priority 整理與套用。
- v4 提供較完整的表格化操作介面。

## 使用環境

- Ansys Electronics Desktop（含 HFSS）
- AEDT IronPython Script 環境

## 使用方式

1. 開啟 AEDT 與 HFSS 設計。
2. 選擇 `Automation > Run Script...`。
3. 載入 `hfss_mat_priority_tool_v4.py`。
4. 依介面確認材料與 Priority 設定。

## 公開範圍

建議公開 v4 腳本與操作說明；AEDT 專案與客戶模型不列入版本控制。

如需材料規則客製化、批次處理或企業流程整合，請來信洽詢。

此工具由虎門科技資深技術工程師 Jeff Hong 洪敬傑提供
