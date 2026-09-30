Minecraft Copy/Paste Datapack v0.4.2
適用：Minecraft Java Edition 26.3（Data Pack 121.0）

使用 Trigger，不使用 G / ESC / Dialog。

安裝：
1. 把 ZIP 放進 world/datapacks/
2. 移除舊版 Copy/Paste ZIP
3. 重啟伺服器或執行 /reload
4. 輸入 /trigger copypaste 顯示控制面板

主要指令：
/trigger copypaste        控制面板
/trigger pos1             看著方塊設定 Pos1
/trigger pos2             看著方塊設定 Pos2
/trigger anchor           看著方塊設定 Anchor
/trigger anchor set 2     清除 Anchor，恢復使用 Pos1
/trigger c                Copy
/trigger v                Paste
/trigger cut              Cut
/trigger undo             Undo（1 層）
/trigger mode             Replace / Masked
/trigger rotate           0°→90°→180°→270°→0°
/trigger mirror           無→X→Z→無（套用到 Paste）

直接移動目前選取區域：
/trigger right set <n>
/trigger left set <n>
/trigger up set <n>
/trigger down set <n>
/trigger forward set <n>
/trigger backward set <n>

- left/right/forward/backward 依玩家「當下水平朝向」判斷，不受抬頭低頭影響。
- up/down 永遠是世界 Y 軸。
- n 為 1～128。
- Move 會一起更新 Pos1、Pos2、Anchor，並可 Undo。
- Move 會先保存完整快照，因此來源與目的地重疊也安全。

原地鏡像目前選取區域：
/trigger flipx            沿 X 方向原地翻面
/trigger flipz            沿 Z 方向原地翻面

- 選取框保持原位。
- 自訂 Anchor 會跟著翻到對稱位置。
- Flip 可 Undo。
- 因使用 Structure Template，X/Y/Z 每軸必須 ≤ 48 格。

旋轉/鏡像 Paste：
/trigger rotate set 10    0°
/trigger rotate set 20    90°
/trigger rotate set 30    180°
/trigger rotate set 40    270°
/trigger mirror set 10    無
/trigger mirror set 20    X
/trigger mirror set 30    Z

限制：
- Raycast 128 格。
- 一般 Copy / Cut / 無變換 Paste：單軸最多 128 格，總體積受 minecraft:max_block_modifications 限制。
- 旋轉、鏡像 Paste 與 Flip：每軸 ≤ 48 格。
- 旋轉/鏡像 Paste 目前使用 Replace；Masked 只用於無旋轉、無鏡像貼上。
- 支援主世界、地獄、終界 Copy/Paste；Move/Flip 在目前選取區域所在維度內執行。


v0.4.1 stability changes:
- Move / Flip 使用獨立 Work Buffer，不會覆蓋原本的 Clipboard。
- Move / Flip 失敗時會確認自動 rollback 是否成功。
- 若 rollback 也失敗，會保留 Undo 備份供再次嘗試。
- 針對中小型建築優化；未特別處理超大型 Move 的 forceload 邊界。

v0.4.2 fixes:
- 修正 `/trigger mode` 在同一次呼叫中從 Replace 切到 Masked 又切回 Replace 的問題。
- 舊版玩家升級時補上缺少的旋轉、鏡像與 Undo 選取框狀態，保留既有 ID、Clipboard 和選取座標。
- 實機測試方式與結果見 [LIVE-VALIDATION.md](LIVE-VALIDATION.md)。
