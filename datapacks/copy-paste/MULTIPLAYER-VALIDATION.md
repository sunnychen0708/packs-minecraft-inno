# Copy/Paste v1.7 多人隔離與驗證

2026-10-07：SunnyChen 使用 Windows 官方 client，另外三人使用 Bot；innotest 同 tick regression **18 PASS / 0 FAIL**，通過 current-session server ERROR gate。[完整證據與限制](../../docs/issue-49-validation.md)。這不是兩個真人同時點 UI 的驗證。

目標：多位玩家可在同一個伺服器使用 Copy/Paste、Blueprint、Move/Rotate/Flip、Undo/Redo，而不把彼此的 Clipboard、歷史紀錄或材料工作狀態混在一起。Warehouse 庫存則刻意是全服共用資產。

## Per-player 狀態

每位玩家第一次使用時取得唯一 `mcc_id`。Pos1、Pos2、Anchor、Mode、Rotate、Mirror、Blueprint 目標、Undo/Redo 指標與材料流程狀態都以玩家自己的 scoreboard / storage key 保存。

隱藏世界空間分成 **7 個基礎 Z lane 類型**：

- Clipboard：`#cbz`
- Undo scratch：`#ubz`
- Work：`#workz`
- Redo scratch：`#redoz`
- Blueprint snapshot：`#bpz`
- Undo history 基底：`#uhistz`，每位玩家 5 個 ring slots
- Redo history 基底：`#rhistz`，每位玩家 5 個 ring slots

玩家 X lane 使用 `X = #base + mcc_id × #slot`。目前 `#slot = 256`，一般 Copy/Cut 每軸上限 128；history slot 以 `#hgap >= 256` 分隔。`scripts/test-copy-paste.py` 會對 64 個玩家的最大一般 buffer 範圍做碰撞檢查，也會確認 5+5 個 history slots 互不重疊且不撞 Blueprint lane。

旋轉／鏡像使用的 Structure Template 名稱也含玩家 ID：

- `mcc:clipboard_<id>`
- `mcc:work_<id>`

材料 BOM 保存在玩家 ID 對應的 `mcc:materials` 路徑；Undo/Redo metadata 則用玩家 ID + history slot 存在 `mcc:history`。因此 Build 的材料紀錄不會只靠一份全域玩家資料。

## 共用 scratch 為什麼不互串

`mcc:temp` 與 Warehouse API 的 request/result 屬於短生命週期 scratch。正式世界編輯流程不使用 `schedule function mcc:...` 把共享 scratch 延後到下一 tick；單次 function 呼叫會同步完成後才輪到下一個命令。

CI 也會拒絕非 load/tick 世界操作 function 使用 `@a`，避免某位玩家的操作直接掃到所有玩家。Raycast 的 `mcc_temp_hit` marker 會在同一次同步操作內建立、讀取並刪除。

材料庫存是例外中的「刻意共用」：Warehouse 是全服共用財產（每位玩家自己的背包則只扣自己的）。Copy/Paste 的 Build / Redo 會在真正扣料時先扣該玩家背包，不夠的部分再透過 Warehouse API 做 count/take；若另一位玩家先取走材料，後一個操作會因庫存不足而停止，不會免費施工。

## Blueprint 可見性

每位玩家有自己的 Blueprint snapshot 與目標座標，但 `block_display` 預覽本身是世界實體，因此其他附近玩家也看得到。這是設計行為，不代表 Blueprint 的來源 buffer 被共享。

## 同一世界區域的衝突

多人隔離保證的是「玩家 A 的內部資料不會變成玩家 B 的」，不是對世界方塊做 transaction lock。

如果兩位玩家刻意同時修改同一批真實方塊，兩個合法操作仍可能依伺服器實際執行順序互相覆蓋。現在不做區域鎖；Undo/Redo 也只保證自己的歷史資料隔離，不能替另一位玩家鎖住建築區。

## CI / 靜態驗證

```console
python3 scripts/validate-datapack.py copy-paste
python3 scripts/test-copy-paste.py
python3 scripts/test-datapack-compatibility.py
```

`test-copy-paste.py` 目前會檢查：

- 64-player hidden buffer address 不碰撞；Undo/Redo 暫存 lane 以 Move/Rotate 聯集上限 256 格計算，其餘 lane 以 128 格計算。
- 5 層 Undo + 5 層 Redo history spacing 正確。
- Clipboard / Work template 名稱含 `$(id)`。
- 正式 `mcc:` 世界編輯沒有跨 tick `schedule function`。
- load/tick 以外的操作 function 不使用 `@a`。
- Blueprint / material history 與五層 Undo/Redo 的 per-player metadata 路徑存在。

此外，`test-datapack-compatibility.py` 會確認 Utilities、Warehouse、Copy/Paste 沒有 namespace/resource/objective 衝突，並在官方 Minecraft 26.3 server 上把三包一起載入驗證共存。

## v1.3 雙人真人測試

產生 opt-in 測試 datapack：

```console
python3 scripts/build-copy-paste-multiplayer-test.py
```

把 `dist/mcc-multiplayer-test` 放進已備份的測試世界 datapacks，`/reload` 後：

玩家 A：

```mcfunction
/function mcc_mp_test:join_a
```

玩家 B：

```mcfunction
/function mcc_mp_test:join_b
```

任一位再執行：

```mcfunction
/function mcc_mp_test:start
```

測試會讓兩位玩家在同一批 tick 中，各自對一棟 3D 測試房子（`scripts/mcc_house.py`）完成 Pos1/Pos2、Copy → Blueprint → Build（背包材料）、Move、Undo/Redo、Rotate、Flip、Cut/Paste 與獨立 Undo，每一步逐格比對整棟房子的 blockstate，並檢查 `mcc_id`、Clipboard 與世界結果沒有互換。結束後執行 `/function mcc_mp_test:cleanup` 清掉測試區、收回測試給的材料。實際流程在 `innotest` 由 `run-copy-paste-multiplayer-test` 跑（見 `docs/HANDOFF.md`）。

repo 目前沒有提交一份 **v1.3** 兩位真人 client 的成功 evidence，因此應描述為：**64-player 隔離架構已由 regression 證明，單 actor / 官方 server 行為已有自動 runtime 覆蓋，但 two-real-player client/server concurrency 尚未留下正式驗證證據。**

`scripts/build-copy-paste-multiplayer-test.py` 的產生器版本已同步到 v1.3；它仍屬 opt-in 真人測試，不會被 headless CI 假裝成 two-client evidence。
