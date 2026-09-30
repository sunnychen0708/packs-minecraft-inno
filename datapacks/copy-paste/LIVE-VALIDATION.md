# Copy/Paste 實機驗證（2026-09-30）

環境：Minecraft Java 26.3，單人世界「測試服」，實際登入玩家。
修正基底：`4910705` 的 v0.4.1。世界在安裝前已完整備份。
原本安裝的 v0.2 已停用。Utilities、Warehouse 與既有 Redstone 測試包仍在世界內。

## 重現與修正

1. **Mode 無法停留在 Masked**：第一個分支修改 `mcc_mask` 後，第二個分支立即符合條件，切回 Replace。將第一個分支改成 `return run`，一次只執行一個切換。
2. **v0.2 玩家升級缺少新版狀態**：既有 `mcc_id` 使 `player_init` 不再執行，旋轉／鏡像面板沒有狀態，初次貼上可能進入錯誤分支。tick 在 dispatch 前補齊 `mcc_rot`、`mcc_mir`、`mcc_usel`，不重設 ID、Clipboard 或選區。

修正版原始碼標為 v0.4.2；沒有覆蓋既有 GitHub Release 或 tag。

## 已執行

原始 v0.4.1：51 項方塊／狀態檢查，49 PASS、2 FAIL。
修正後：80 項檢查，80 PASS、0 FAIL。原始輸出的 MCCT 摘錄見 [evidence](../../tests/evidence/copy-paste-live-20260930.txt)。

v0.4.2 ZIP 安裝後另跑缺欄位遷移檢查，PASS：三個新版欄位由 tick 補齊，既有 ID、Clipboard flag、Pos1 X 保持不變。共 81 項自動實機斷言通過。

| 功能 | 實機檢查 |
| --- | --- |
| 面板、Pos1、Pos2 | UI 輸入 `/trigger copypaste`；準星射線選取，核對負座標與高度 |
| Anchor | 設定、清除、自訂錨點貼上、Move/Flip X 後位置及 Undo |
| Copy、Paste、Cut、Undo | 實際方塊內容、目的地空氣覆蓋、剪下還原 |
| Replace / Masked | 來源空氣位置：Replace 清除、Masked 保留；Undo 還原原目的地 |
| 六方向 Move | 玩家 yaw=0、pitch=70；重疊來源／目的地；選取框跟隨；逐項 Undo |
| Flip X / Z | 非對稱 3×1×2 選區，方塊位置及 Undo |
| Rotate / Mirror | 4×3 全部 12 組 Paste 變換與 Undo；循環選項回到起始值 |
| Clipboard 隔離 | Copy A 後對不同內容的 B 做 Move、Flip、Undo，Paste 仍得到 A |
| 維度 | 主世界→地獄→終界→主世界 Paste/Undo；各維度 Copy、Move、Flip |
| 距離拒絕 | Move 129 被拒絕且來源與選取座標未變 |

測試腳本由遊戲 UI 手動啟動，在真實玩家身上執行 `trigger`，讓正常 tick dispatch 處理，再隔數 tick 用 `execute if block`／score 檢查結果。這是單人世界整合測試；不是多人測試，也不代表所有可能方塊、尺寸與失敗注入情境都通過。

未覆蓋：多人並行、全部水平朝向邊界、48/128 格最大尺寸、超大型 forceload、強制 rollback 失敗、所有方塊 NBT／紅石更新。既有 Warehouse 另有載入錯誤，未納入本次 Copy/Paste 修正。

## 重跑

```console
python scripts/validate-datapack.py copy-paste
python scripts/test-copy-paste.py --pack-root datapacks/copy-paste
python scripts/build-copy-paste-live-test.py
```

將 `dist/mcc-live-test` 放入**已備份的拋棄式創造模式測試世界**之 datapacks，再 `/reload`。
手動執行 `/function mcc_test:start`。測試會傳送玩家、改變 Copy/Paste 狀態，並改寫三維度 x=-205..-175、y=249..255、z=85..105；請勿在正式建築區執行。
等待 `MCCT DONE pass=80 fail=0`。

再執行 `/function mcc_test:upgrade`，它會移除三個新增欄位，讓正常 tick 補齊，並核對 ID、Clipboard flag、Pos1 X 沒有被重設。測試包沒有 load/tick tag，不會自行開始。
