# Copy/Paste 驗證狀態（v1.3.2）

目前版本 **v1.3.2**。v1.3.1 拿掉載入與第一次使用時的聊天訊息，v1.3.2 移除舊的轉向／翻面指令。目標 Minecraft Java 26.3（Data Pack 121.0）。

這份文件把「官方 server headless regression」和「真人 client 驗證」分開寫。兩者不能互相冒充。

## 驗證鏈

| 層級 | 指令 | 能證明什麼 |
| --- | --- | --- |
| Generic static | `python3 scripts/validate-datapack.py copy-paste` | JSON、function／tag 引用、macro、Dialog 結構、Trigger 盤點、ZIP 結構 |
| Pack regression | `python3 scripts/test-copy-paste.py` | 座標公式、Trigger lifecycle、buffer 隔離、Undo/Redo、Dialog 必要按鈕、名稱表、版本同步 |
| Behavioral runtime | `python3 scripts/test-copy-paste-runtime.py ...` | 在官方 26.3 server 以 armor stand actor 驗真實方塊、display、storage、scoreboard、材料交易 |
| Cross-pack runtime | `python3 scripts/test-datapack-compatibility.py ...` | Utilities + Warehouse + Copy/Paste 同時載入與共用 API 共存 |
| **真人 client** | `scripts/real-client/`（Windows） | 用作業系統層級的鍵盤／滑鼠真的操作遊戲，**讀世界存檔逐格判定** |
| 雙人 harness | `python3 scripts/build-copy-paste-multiplayer-test.py` | 兩位真人同時操作（尚未執行過） |

## Headless behavioral runtime

`scripts/test-copy-paste-runtime.py` 目前 **187 個動態 assertions**，涵蓋：

- Pos1／Pos2／Anchor／V 的 raycast；沒有自訂 Anchor 時以 Pos1 為基準（Pos1 不是最小角也精確對位）。
- 自訂 Anchor（含選區外）的 12 種 Rotate/Mirror 組合與連續大半徑 Rotate、Undo。
- Copy → Blueprint 不改真實世界；Blueprint 預覽落在方塊角；六方向微調與覆蓋重算。
- 材料唯讀報表（材料齊全時也不扣料、不施工）、缺料 all-or-nothing、足料 Build。
- 先從持有者背包／副手扣料（實際從副手扣掉），再用 Warehouse；Undo 退料、Redo 再扣、防複製 guard。
- Cut + V、Move、Flip、Rotate 90/180/270、五層 Undo/Redo、每種編輯的防複製快照。
- Cut → Undo 作廢 Cut Clipboard、Redo 重建；Rotate 後 Masked 貼上；外部 Anchor Flip；長距離 Move。
- 材料工作進行中被擋下的指令會提示；名稱表與貼上模式標籤已載入；所有 Dialog 頁面能被官方 server 解析。

**限制：** runtime 使用 armor stand，直接呼叫多數 `mcc:...` function，所以不能證明玩家 `/trigger` 的 tick dispatch、Dialog 實際可點與版面、準星手感、雙人時序。這些由下一節的真人 client 驗證負責。

## 真人 client 驗證（v1.3，2026-10-06）

在官方 26.3 client 的可丟棄 `MCC-Test` 超平坦世界，用 `scripts/real-client/` 真的打指令、點 Dialog、對箱子按使用鍵，結果一律讀 `.mca` region／entities／`command_storage.dat`／playerdata 判定，不看 datapack 自己印的 PASS。最後一輪在 v1.3 最終程式上重跑，151 項中 149 項通過；兩項失敗是殭屍日出燃燒掉落的腐肉（與建築無關，檢查已改為只計建築相關物品）。

| 腳本 | 驗證內容 |
| --- | --- |
| `stage1_chests` / `stage2_register` | 61 個真實大箱子；透過 Warehouse Dialog ＋實際點擊註冊 |
| `stage3_house` | 自訂分類、2 倍材料分類入庫、Blueprint 預覽 86/86 對齊、Build／Undo／Redo、旋轉 90/180/270 與鏡像施工、Cut→V（含箱子內容物）、Move、Flip、直接 Rotate、Pick |
| `stage4_shortage` | 缺料拒絕施工、補料後成功、Undo 全額退回 |
| `stage5_multisource` | 同一材料分散 2～6 箱時跨箱扣料；Undo 退料經入口箱分類回各自分類箱 |
| `stage6_orient` | 以玩家面向（北、東、西）組合的 `bpturnright`／`bpturnleft`／`bpflip`／`bpflipfb`／`bpreset`，以及直接 `turnright`／`turnleft`／`flip`／`flipfb` |
| `stage7_menu` | 四個 Dialog 頁面、貼上模式切換（從存檔確認） |
| `stage8_names` | 材料檢查與缺料清單顯示 zh_tw 物品名稱 |
| `stage9_checkonly` | 材料齊全時「材料檢查」不扣料、不施工 |
| `stage10_inventory` | 背包／副手優先扣料、改名物品不使用、Undo 退回背包、背包滿時其餘退 Warehouse 且 0 掉落、Redo 同樣先扣背包 |
| `stage12_all_packs` | Utilities + Warehouse + Copy/Paste 一起安裝：三包載入無錯誤、沒有載入訊息、G 開 Warehouse 主畫面、Utilities 設家／回家／返回／說明正常；同時重跑 `stage5`、`stage10`、`stage9` 全數通過 |

**尚未驗證：** 兩位真人 client 同時操作。

2026-10-06 晚間三包一起重跑時，一度出現「材料表是空的、施工沒扣料」：原因是測試用小屋在 18:08 被手動 Cut 搬走，測試等於在複製空氣，並不是 pack 的問題。`stage3_house.snapshot()` 現在發現小屋不完整就直接停止。

## 舊的 Trigger harness

`scripts/build-copy-paste-live-test.py` 產生 `mcc_test:start` 測試 datapack，走真人玩家的 trigger dispatch。它的 **Warehouse 段落不可信**：用兩個 `setblock chest` 單箱並直接寫 `warehouse:chests`，沒有走玩家註冊流程。CI 只檢查它能產生；正式驗證以上一節的真人 client 工具為準。

`tests/evidence/copy-paste-live-20260930.txt` 是 v0.4.2 時期的真人 evidence，只代表當時版本。

## Dialog

`/trigger copypaste` 的介面全部由 function 產生 inline Dialog，`/reload` 就會更新：

- `ui/show`：主畫面 9 顆（Pos1、Pos2、Copy、Cut、Paste、Build、Undo、調整預覽…、更多…）。
- `ui/adjust`（`copypaste set 2`）：轉向、翻面、回原方向、清除預覽、移動預覽、材料檢查、Build。
- `ui/more` → `ui/more_show`（`set 3`）：Anchor、清除 Anchor、貼上模式（顯示目前模式）、直接改原本建築…、Redo、指令教學。
- `ui/edit`（`set 4`）：直接移動／轉向／翻面原本建築。

`test-copy-paste.py` 檢查這些頁面包含所有必要指令、主畫面維持精簡；runtime 會把每一頁交給官方 server 解析。

## 重跑驗證

```console
python3 scripts/validate-datapack.py copy-paste
python3 scripts/test-copy-paste.py
python3 scripts/test-datapack-compatibility.py

python3 scripts/test-copy-paste-runtime.py --java /path/to/java --server-jar /path/to/server.jar --accept-eula
python3 scripts/test-datapack-compatibility.py --java /path/to/java --server-jar /path/to/server.jar --accept-eula
```

真人 client 工具的用法與注意事項見 [`docs/HANDOFF.md`](../../docs/HANDOFF.md)。
