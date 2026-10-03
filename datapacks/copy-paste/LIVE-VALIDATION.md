# Copy/Paste 驗證狀態（v1.1 / 2026-10-03）

目前原始碼與已發布版本皆為 **v1.1**，目標 Minecraft Java 26.3（Data Pack 121.0）。這份文件描述「現在主線能證明什麼」，並把 2026-09-30 的真人 client 測試保留成歷史證據，而不是把舊 v0.4.2 結果誤當成 v1.1 的完整驗證。

## 目前自動驗證鏈

| 層級 | 指令 / CI | 目前涵蓋 |
| --- | --- | --- |
| Generic static | `python3 scripts/validate-datapack.py copy-paste` | `pack.mcmeta`、JSON、function/tag 引用、macro 呼叫、Trigger 盤點、ZIP 結構 |
| Pack regression | `python3 scripts/test-copy-paste.py` | Trigger lifecycle、64-player buffer 隔離、五層 Undo/Redo、Blueprint exact-state matcher、材料施工語意、Rotate/Move/Flip/rollback 等 |
| Vanilla smoke | `validate-datapack.py ... --server-jar ...` | 官方 26.3 server 啟動、`/reload`、parser / datapack load error 掃描 |
| Behavioral runtime | `python3 scripts/test-copy-paste-runtime.py ...` | Copy/Paste + Warehouse 在隔離世界中的實際方塊、storage、scoreboard 與材料交易結果 |
| Cross-pack runtime | `python3 scripts/test-datapack-compatibility.py ...` | Utilities + Warehouse + Copy/Paste 同時載入、代表性 objective/storage 與 Warehouse API 共存 |

目前 CI 的 `Validate datapacks` 已包含 Copy/Paste 專用官方 26.3 runtime 與三包合載 compatibility job；`copy-paste-v1.1` 發布流程也使用同一組 release gates。

## v1.1 behavioral runtime 覆蓋

`scripts/test-copy-paste-runtime.py` 目前定義 56 項 runtime assertions，使用非玩家 armor stand actor 走正式內部 function 路徑。主要覆蓋：

- Copy → V 只產生 `block_display` Blueprint，不寫入真實目標方塊，來源也保持不變。
- Blueprint 六方向微調：left / right / forward / backward / up / down；移動後同步更新目標座標與覆蓋重算。
- 覆蓋保護：偵測目標既有非空氣方塊，第一次 Build 只警告，重算後會重置確認狀態。
- `/trigger materials` 對材料只做唯讀統計，不會扣料。
- 材料不足時 Build all-or-nothing：不施工、不扣已有材料、保留 Blueprint。
- 材料足夠時透過 Warehouse 共用 API 扣料並施工，Undo history 保存實際材料交易。
- Build 後世界被外部修改時，material Undo guard 會拒絕退款，避免複製資源。
- 正常 Build Undo 會還原世界並把材料退回 Warehouse `c00`；Redo 會重新扣料後恢復建築。
- Cut (`x`) 直接移除來源；Undo/Redo 可逆；成功 X+V 後 Cut Clipboard 會消耗，不能重複貼。
- Move、直接 Rotate90 與一般真實世界貼上都有 Undo/Redo。
- 五次連續真實編輯可依序 Undo 五次，再 Redo 五次。

這個 headless runtime **不等於真人 client 驗證**：它不驗證聊天控制面板點擊、實際準星手感、鍵鼠操作，也不證明兩位真人玩家同時操作時的所有時序。多人隔離與雙人測試方式見 [MULTIPLAYER-VALIDATION.md](MULTIPLAYER-VALIDATION.md)。

## 2026-09-30 真人 client 歷史驗證

當時測的是 v0.4.1 → v0.4.2 修正，不是目前 v1.1。該次測試在 Minecraft Java 26.3 單人世界中，以真實登入玩家操作 Trigger，修正了兩個問題：

1. Mode 切到 Masked 後同一次 function 又被第二個分支切回 Replace。
2. v0.2 玩家已有 `mcc_id`，導致新版 `mcc_rot` / `mcc_mir` / `mcc_usel` 狀態沒有補齊。

原始 v0.4.1 測試為 49 PASS / 2 FAIL；修正後主流程 80 PASS / 0 FAIL，再加缺欄位 migration probe 共 81 項通過。原始 MCCT 摘錄仍保存在 [`tests/evidence/copy-paste-live-20260930.txt`](../../tests/evidence/copy-paste-live-20260930.txt)。這份 evidence 應視為「真人操作路徑曾經驗過」的歷史紀錄，不應拿來替代 v1.1 新增 Blueprint 材料施工與 Phase 3 功能的現行 runtime gate。

## 重跑目前驗證

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

若要驗真人 Trigger / 準星選取路徑，可另外產生 opt-in client harness：

```console
python3 scripts/build-copy-paste-live-test.py
python3 scripts/build-copy-paste-multiplayer-test.py
```

這兩個 harness 只應放進已備份、可丟棄的測試世界；多人 harness 需要兩位實際登入玩家才算真正的 two-client runtime validation。
