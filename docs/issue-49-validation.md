# Issue #49 / PR #52 驗證（2026-10-07）

## 結論與範圍

Copy/Paste v1.7 的 ID tree + per-property matcher 可用於目前 26.3 的 35,720 個支援 state。沿用 `{id, properties}` 與原本 summon 路徑；沒有持久資料格式變更，不需要 migration。未安裝到 inno，也未發布或合併。

本次接手保持原本 generated matcher 不變，補強 report 匯入驗證與 innotest 測試工具。Report 必須包含每一種合法 property 組合且不得重複，不能只靠 state 數量相等推論 Cartesian product。

## 可重查的證據

| 層級 | Commit / workflow | 結果 |
| --- | --- | --- |
| 全 state innotest runtime | `52aaa793` / [37599912705](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37599912705) | `MCCBP_COUNTS states=35724 expected=35724 fail=0 air_ret=0`；`BLUEPRINT_MATCHER_LIVE_TEST=PASS`。35,720 個 state 加 4 個重複案例 |
| 三 Bot 連線 | [37599963189](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37599963189) | `READY 3/3`，penguin0531、geena0701、Felicitypeng 完成 300 秒；SunnyChen 使用 Windows 官方 client |
| 四人在線、兩人同 tick regression | `cf764d7f` / [37600389867](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37600389867) | 18 PASS / 0 FAIL，`COPY_PASTE_MULTIPLAYER_LIVE_TEST=PASS`，通過本次 session 的 server ERROR gate |
| CI | `b716af48` / [37600528601](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37600528601) | validate、Warehouse、Utilities、Copy/Paste runtime、三包 compatibility 全部通過；新增 report 異常組合回歸與 generated 一致性檢查 |
| Windows 真人 UI | 17:27–17:31（Asia/Taipei）；官方 26.3 client、SunnyChen、innotest | 鍵盤 G → 建築工具 → Pos1 / Pos2 / Copy / Paste；樓梯 Blueprint 建立、右轉 90°、清除預覽皆成功 |

真人樣本是測試用 `oak_stairs[facing=east,half=top,shape=inner_left,waterlogged=false]`。透過 UI 建立預覽後，以遊戲 `/data get entity ... block_state` 讀回完整屬性；右轉後只有 facing 變成 south，其他三項保持不變。Client log 記錄：

```text
17:29:40 {id: "minecraft:oak_stairs", properties: {waterlogged: "false", half: "top", shape: "inner_left", facing: "east"}}
17:30:35 {id: "minecraft:oak_stairs", properties: {waterlogged: "false", half: "top", shape: "inner_left", facing: "south"}}
17:31:17 [Copy/Paste] 你的 Blueprint 預覽已清除。
```

完整 state 驗證是 server-side storage 比對；多人 regression 是 server-side trigger 操作，SunnyChen client 實際在線；最後一列才是鍵盤／滑鼠實際點擊 UI。這次沒有把全部歷史 real-client stages 重跑，也沒有驗證兩個真人 client 同時點 UI。

## 修正的測試問題

- 原本 progress probe 會 `schedule clear mcc_bp_live:batch_0`，取消尚未開始的第一批工作。改成唯讀診斷。舊 run 的第一批尚未執行原因未單獨證實；本次有玩家在線的完整 run 已通過。
- [第一輪多人 run](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37600096752) 為 6 PASS / 12 FAIL。遠處 fixture 沒有先 forceload，選點與貼上目標不存在；加上預先載入後重跑為 18 / 0。清理只移除本輪新增的 forceload，保留原有載入設定。
- Bot workflow 增加 `three-bots-with-real-client` 選項，保留 SunnyChen 給真人 client；Bot 名稱和 host 安全限制保留。

## 成本與限制

舊方法對 block group 與完整 state 線性掃描，成本為 `O(G + S_b)`；新方法成本為 `O(D + sum(k_p))`，D 是 ID tree 路徑長度、k_p 是各 property 值的判斷數。對固定 26.3 registry，成本有固定上限。CI 的指令模型要求 stone / dirt 至多 6、全部 state 最差至多 80；這次 CI 通過。PR 原先的 wall-clock benchmark 沒有在本次重測，不應稱為 innotest 效能測量。

額外空間是固定的函式與 block tags；執行時仍用原本的暫存 state，沒有隨玩家操作無限成長的資料。兩值 property 的 default shortcut 依賴已驗證的 Vanilla schema；不承諾未來版本或 modded property 的行為。Block entity NBT、流體及特殊 renderer 的外觀限制仍與本次 matcher 正確性分開。

## 清理

兩個遠端 harness 已由 controller 移除並 reload；單一真人樣本位於 `-280 80 90`，驗完移除，預覽清除、方向重設。SunnyChen 已回到原區域 `588.5 95 -415.5` 並恢復生存模式。測試會改到 innotest 的選區、Clipboard 與 Undo/Redo 測試歷史，不代表還原了所有玩家測試狀態。三個 ops request 維持 noop，innotest 保持 ONLINE。
