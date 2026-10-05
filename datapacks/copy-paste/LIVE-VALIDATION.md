# Copy/Paste 驗證狀態（v1.3 source / 2026-10-05）

目前原始碼為 **v1.3（尚未發布）**；最新已發布 ZIP 仍是 **v1.2**。目標 Minecraft Java 26.3（Data Pack 121.0）。

這份文件刻意把「官方 server headless regression」和「真人玩家 Trigger / Dialog 驗證」分開。兩者不能互相冒充。

## 目前驗證鏈

| 層級 | 指令 / CI | 能證明什麼 |
| --- | --- | --- |
| Generic static | `python3 scripts/validate-datapack.py copy-paste` | JSON、function/tag 引用、macro、Trigger 盤點、ZIP 結構 |
| Pack regression | `python3 scripts/test-copy-paste.py` | 座標公式、Trigger lifecycle、buffer 隔離、Undo/Redo、active Dialog 必要操作、版本同步 |
| Vanilla smoke | `validate-datapack.py ... --server-jar ...` | 官方 26.3 server 能啟動、reload，沒有被掃到的 parser/load error |
| Behavioral runtime | `python3 scripts/test-copy-paste-runtime.py ...` | 在官方 26.3 server 以非玩家 actor 驗真實方塊、display、storage、scoreboard、Warehouse 材料交易 |
| Cross-pack runtime | `python3 scripts/test-datapack-compatibility.py ...` | Utilities + Warehouse + Copy/Paste 同時載入與共用 API 共存 |
| Real-player harness | `python3 scripts/build-copy-paste-live-test.py` | 需要真人登入後，才會真正走 `/trigger` → tick dispatch → player raycast 的操作路徑 |
| Two-player harness | `python3 scripts/build-copy-paste-multiplayer-test.py` | 需要兩位真人登入後，才能驗兩 client 同時操作 |

## Headless behavioral runtime 的實際範圍

`scripts/test-copy-paste-runtime.py` 是 v1.3 source 的官方-server regression，目前為 **133 個動態 assertions**，涵蓋：

- Pos1 / Pos2 / Anchor / V 的 raycast function。
- 沒有自訂 Anchor 時，Pos1 為預設 Anchor，即使 Pos1 不是選區最小角也要精確對位。
- 自訂 Anchor 精確對位與 12 種 Rotate/Mirror 組合。
- 選區重新設定會清掉舊自訂 Anchor。
- 選區外 Anchor 的連續大半徑 Rotate 與 Undo。
- Copy → Blueprint 不改真實世界。
- Blueprint 六方向微調與覆蓋重算。
- 材料唯讀報表、缺料 all-or-nothing、足料 Build。
- Warehouse 扣料、Undo 退款、Redo 重新扣料、防複製 guard。
- Cut + V、Move、Flip X/Z、Rotate 90/180/270。
- 五層 Undo/Redo。
- 每種世界編輯的 Undo/Redo 防複製快照：操作後區域（含容器內容物）被改過時拒絕 Undo/Redo。
- Cut → Undo 作廢 Cut Clipboard、Cut → Undo → Redo 重建原本的 Cut Clipboard（中間做過別的 Copy 也一樣）。
- Rotate 後的 Masked Cut 貼上保留目標既有方塊。
- 自訂（外部）Anchor 的 Flip X/Z：Anchor 固定、結構繞 Anchor 平面鏡像。
- 來源加目的地 Z 跨度超過 200 格的長距離 Move 與 Undo（內部暫存區不互相覆蓋）。
- 材料工作進行中被擋下的指令會觸發提示。

**限制：這個 runtime 使用 armor stand actor，並直接呼叫多數內部 `mcc:...` functions。**  
因此它不能證明以下玩家路徑：

- 玩家輸入 `/trigger ...` 後是否由 `tick.mcfunction` 正確 dispatch。
- Dialog 按鈕是否真的可點、命令是否正確、版面是否可用。
- 真人準星、滑鼠、鍵盤的實際手感。
- 兩位真人玩家同時操作的 client/server 時序。

所以「headless runtime PASS」不能再被描述成「玩家實機全部驗過」。

## v1.3 真人 Trigger harness

`scripts/build-copy-paste-live-test.py` 已更新到 v1.3。它會產生 opt-in 測試 datapack，使用**真人玩家本人的 trigger objective**，每一步交給正常 Minecraft tick dispatch 處理。

目前生成案例包含：

- Pos1 / Pos2 真人 raycast。
- 選區外自訂 Anchor。
- `/trigger anchor set 2` 清 Anchor。
- 重新設定 Pos1 後舊 Anchor 必須失效。
- Pos1 非最小角時的預設 Anchor Blueprint 精確位置。
- Copy / Blueprint。
- Warehouse 材料支援的 Build。
- Cut → Undo 作廢 Cut Clipboard、Redo 重建 Cut Clipboard。
- Cut + V。
- Move / Flip / Rotate 與 Undo/Redo。
- 跨維度 Copy / Cut。

執行方式：

```console
python3 scripts/build-copy-paste-live-test.py
```

把 `dist/mcc-live-test` 放進**已備份、可丟棄的真人測試世界**後，由實際登入玩家執行：

```mcfunction
/function mcc_test:start
```

目前 repo **尚未提交一份 v1.3 真人 harness 全 PASS 的 client evidence**。在那之前，只能說 v1.3 source 已通過官方 server headless regression，不能說真人 Trigger / Dialog 已完整驗證。

## Dialog 檢查

`/trigger copypaste` 的 active UI 是 `data/mcc/dialog/main.json`，不是舊的 `panel.mcfunction`。

v1.3 active Dialog 必須至少包含：

- Pos1 / Pos2 / Anchor / 清 Anchor。
- Copy / Cut / Blueprint。
- Build / Materials / Clear Blueprint。
- Undo / Redo。
- 指令教學。

CI 現在直接檢查 active Dialog，不再拿沒有被 `/trigger copypaste` 呼叫的 legacy `panel.mcfunction` 當成玩家 UI 正確的證據。

## 歷史真人 evidence

`tests/evidence/copy-paste-live-20260930.txt` 是 2026-09-30 的真人 client evidence，當時修的是 v0.4.1 → v0.4.2 的 Mode 與舊玩家 migration 問題。

那份 evidence 只能證明當時版本的真人路徑曾跑過，**不能替代 v1.3 的 Blueprint / Build / external Anchor / Dialog 驗證**。

## 重跑自動驗證

```console
python3 scripts/validate-datapack.py copy-paste
python3 scripts/test-copy-paste.py
python3 scripts/test-datapack-compatibility.py

python3 scripts/test-copy-paste-runtime.py \
  --java /path/to/java \
  --server-jar /path/to/server.jar \
  --accept-eula

python3 scripts/test-datapack-compatibility.py \
  --java /path/to/java \
  --server-jar /path/to/server.jar \
  --accept-eula
```

發布規則仍是：static、pack regression、三包 compatibility、Copy/Paste 專用官方 26.3 runtime 全部必須通過；真人 client-only 項目若沒有 evidence，就必須明確標成未驗，而不是用 headless PASS 代替。
