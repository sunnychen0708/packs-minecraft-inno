# Copy/Paste 多人隔離與驗證

目標：讓多位玩家可以在同一個伺服器、甚至同一個 tick 送出 Copy/Paste/Move/Flip/Undo，而不共用 Clipboard、Undo 或 Work Buffer。

## 架構

每位玩家第一次使用時取得唯一 `mcc_id`。

五種隱藏 buffer 都以玩家 ID 分配獨立 X lane：

- Clipboard：`X = #base + mcc_id × #slot`，Z lane = `#cbz`
- Undo scratch：相同玩家 X lane，Z lane = `#ubz`
- Undo history：每位玩家 5 個 ring slots，從 `#uhistz` 起、間隔 `#hgap`
- Work：相同玩家 X lane，Z lane = `#workz`
- Redo scratch：相同玩家 X lane，Z lane = `#redoz`
- Redo history：每位玩家 5 個 ring slots，從 `#rhistz` 起、間隔 `#hgap`
- Blueprint 快照：相同玩家 X lane，Z lane = `#bpz`

目前 `#slot = 256`，一般選取每軸上限 128，因此不同玩家的 X 範圍不會碰到；三種 buffer 的 Z lane 也彼此分開。

旋轉／鏡像所用的 Structure Template 名稱同樣包含玩家 ID：

- `mcc:clipboard_<id>`
- `mcc:work_<id>`

玩家的 Pos1、Pos2、Anchor、Mode、Rotate、Mirror 與 history pointer 都存在各自的 scoreboard score；每一層 Undo/Redo metadata 則以玩家 ID + slot 存在 `mcc:history` command storage，不會共用。

## 為什麼共用 mcc:temp 不會把兩個玩家資料混在一起

`mcc:temp` 只是在 function macro 呼叫前暫存本次同步命令的參數。正式 datapack 的世界編輯 function 不使用 `schedule function mcc:...` 把操作延後到下一 tick，因此一個玩家的 function 會完整執行完，再輪到下一個玩家的命令。

Raycast 的 `mcc_temp_hit` marker 也在同一個同步 function 中建立、讀取並刪除，不跨 tick 保存。

CI 會拒絕：
- datapack 內出現會延後 `mcc:` 操作的 schedule
- tick/load 以外的世界操作 function 使用 `@a`
- 64 個玩家的 Clipboard/Undo/Work rectangle 發生任何重疊
- Clipboard/Work Structure Template 缺少 `$(id)`

## 同一區域衝突

多人隔離保證的是「玩家 A 的 Clipboard/Undo/Work 不會變成玩家 B 的」。

如果兩位玩家刻意同時修改同一批世界方塊，兩個合法操作仍可能互相覆蓋；最後世界狀態取決於伺服器實際執行順序。這和一般兩個玩家同時放／拆同一格方塊的衝突相同。

目前不做區域鎖，因為主要用途是多人各自建造中小型建築；加入區域鎖會讓操作與 Undo 複雜很多。

## 靜態 regression

```console
python scripts/validate-datapack.py copy-paste
python scripts/test-copy-paste.py --pack-root datapacks/copy-paste
```

`test-copy-paste.py` 會模擬 64 個玩家的最大 128×128 水平 buffer，逐一檢查三種 buffer rectangle 都不重疊。

## 雙人實機測試

產生 opt-in 測試 datapack：

```console
python scripts/build-copy-paste-multiplayer-test.py
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

測試會讓兩位玩家在同一批 tick 中各自完成 Pos1/Pos2、Copy、Move、Undo、Flip、Paste 與獨立 Undo，並檢查兩人的 `mcc_id`、Clipboard 內容和世界結果沒有互換。

測試只使用遠離正式建築的固定測試區，仍請只在備份過的測試世界執行。

目前 v0.4.3 的 CI 驗證多人隔離架構；真正的雙人 client/server runtime 結果要在兩位真人登入後才算 multiplayer runtime validated。


## v0.5.0 Blueprint

Copy 的 `V` 不再寫入目標世界方塊，而是建立所有玩家可見的 `block_display` Blueprint。每位玩家的 Blueprint 建立前會先快照到自己的 Blueprint Buffer，所以兩位玩家同時 Copy/V 不會混用來源資料。

Cut 改用 `/trigger x`；Cut 的 `V` 仍是真實世界移動，而且成功後 Cut Clipboard 立即消耗。

Undo/Redo history 同樣是 per-player。每位玩家各有 5 個 Undo 與 5 個 Redo ring slots；CI 會檢查 history slot 間距與玩家 X lane 隔離。
