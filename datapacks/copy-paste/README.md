# Copy/Paste v1.8

Minecraft Java 26.3（Data Pack 121.0）生存建築工具。最新 [copy-paste-v1.8.zip](https://github.com/sunnychen0708/packs-minecraft-inno/releases/tag/copy-paste-v1.8)。按 **G → 建築工具**（需同裝 Warehouse）進入 Dialog；所有玩家指令也可輸入 `/trigger cphelp` 查看。

## 如何使用

```text
Pos1、Pos2 → Copy (/trigger c) → Paste (/trigger v)
                                     ↓
                               Blueprint 預覽
                                     ↓
                            旋轉／翻面／微調
                                     ↓
                           Build (/trigger build)
                                     ↓
                         背包先扣，倉庫補足
```

**Copy + V 只建立 Blueprint，不會免費生成真實方塊。** Build 先計算材料（BOM），不足時不扣料也不施工，並保留預覽。Cut 則會真正移除來源，下次 V 是搬移貼上，成功後 Cut Clipboard 即被消耗。

| 操作 | 指令 |
| --- | --- |
| 選區／自訂 Anchor | `/trigger pos1`、`/trigger pos2`、`/trigger anchor` |
| Copy／Cut／Paste／Build | `/trigger c`、`/trigger x`、`/trigger v`、`/trigger build` |
| 查材料（只讀） | `/trigger materials` |
| Undo／Redo／說明 | `/trigger undo`、`/trigger redo`、`/trigger cphelp` |
| 遊戲內面板 | G →「建築工具」或 `/trigger copypaste` |

**Anchor 規則：** 未設定自訂 Anchor 時，**Pos1** 是 Copy／Blueprint 定位及 Rotate 的預設 pivot；V 會把它對齊準星選定的目標格。**自訂 Anchor 可以在選區外**，可用來做大半徑 Rotate；重新指定 Pos1／Pos2 就會清除舊自訂 Anchor。**Flip 特例**：沒自訂 Anchor 時，Blueprint 與直接 Flip 都以目前外框中心**原地鏡射**；有自訂 Anchor 才繞該 Anchor 鏡射。左右／前後與轉向是**相對玩家面向**，不是以 X/Z 軸或指令輸入位置任意猜方向。

## Blueprint 與直接編輯

以下只改**預覽**，不改來源世界：

```mcfunction
/trigger bpturnright
/trigger bpturnleft
/trigger bpflip
/trigger bpflipfb
/trigger bpreset

/trigger bpleft set 1
/trigger bpright set 1
/trigger bpforward set 1
/trigger bpbackward set 1
/trigger bpup set 1
/trigger bpdown set 1
```

微調距離可用 **1–128**。調整後會重新計算覆蓋區，檢查未完成前不能施工；移除／重建預覽會取消進行中的檢查並釋放暫存 forceload。若目標會覆蓋既有非空氣方塊，首次 Build 僅警告，**再次確認**才會繼續扣料；位置或方向再變更後重置確認。單純 `/trigger materials` 只列材料、背包／Warehouse 庫存與缺額，不會施工。

以下會**直接修改真實選區**：

```mcfunction
/trigger right set 1
/trigger left set 1
/trigger forward set 1
/trigger backward set 1
/trigger up set 1
/trigger down set 1

/trigger turnright
/trigger turnleft
/trigger rotate180
/trigger flip
/trigger flipfb
```

移動距離同樣可用 **1–128**；保留 `rotate180` 這個名字，不改成 `turn180`。自訂 Anchor／外框中心規則與 Blueprint 相同。每次新的 Copy、Cut，或 Cut→Undo→Redo 重建 Clipboard，都會將方向重置為 **0°、未翻面**。

## 材料、安全與多人

- 施工從**玩家主背包 0–35 格＋副手**的一般物品先扣，不足才使用全服共享 Warehouse。無 `components` 或空 `components` 才視為可用材料，改名／自訂資料／附魔物品不拿來消耗。Warehouse 來源最多 64 個、去重大箱，庫存不足或註冊來源 stale 時停止，不會免費施工。
- Blueprint 的 Block Entity 儲物內容不會被複製；不支援沒有安全生存掉落材料的方塊。貼上模式包括 Replace／Masked，Masked 的來源空氣不覆蓋目標。普通 Copy/Build 不是複製箱子內的物品。
- **每位玩家各有獨立** Pos1、Pos2、Anchor、Clipboard、Blueprint、BOM、材料紀錄與最近 **5 筆** Undo／Redo。隱藏工作區依 `mcc_id` 分 lane（間距 256 格，5+5 筆 history），Structure Template 名稱也含玩家 ID；共享暫存 function 同步執行。Warehouse 庫存刻意全服共用。Blueprint `block_display` 是世界實體，附近玩家看得到預覽。
- 不鎖定兩位玩家同時修改的**真實世界區域**；若 A/B 編輯相同方塊，按伺服器執行順序發生衝突是可能的，玩家資料隔離不等於地圖區域 transaction lock。

## Undo／Redo 防複製

每筆真實編輯保留操作完成時的世界快照。**方塊 ID 不同**或容器／Block Entity 內容有變，Undo／Redo 會拒絕，列出缺少／多餘方塊、世界座標等差異；**只改相同 ID 的 block state**（門開關、樓梯方向、水浸等）不阻擋。過大或一 tick 內比不完的區域會退回嚴格一致檢查，避免超出指令上限。

Cut→Undo 會還原來源並作廢目前 Cut Clipboard，避免重複貼上；Cut→Undo→Redo 則會恢復原本 Cut Clipboard。Build→Undo 會退回實際扣除的材料：原本從背包扣的先退背包，放不下的與 Warehouse 來源退到倉庫入口 `c00`；入口滿時由 Warehouse 持久排隊重試。Redo 需重新有足夠材料才施工。舊版沒有防複製快照的 history 會拒絕執行。

## 限制與升級

| 範圍 | 限制 |
| --- | --- |
| 準星 raycast | 128 格 |
| Copy／Cut | 每軸 ≤128 格，且受 `minecraft:max_block_modifications` 限制 |
| Structure Template Rotate／Flip | 每軸 ≤48 格；以外部 Anchor 翻面亦受限 |
| Move／直接 Rotate 的來源＋目標 Undo 範圍 | 每軸 ≤256 格 |
| Blueprint matcher | Java 26.3 的 1,283 種非空氣 block ID／35,720 合法 states |
| 實體 | 不在 Copy/Cut/Blueprint 處理範圍內 |

更新前移除舊 ZIP，**不要同時載入兩份**。升級 v1.3 前後留下的 `rotate`、`mirror`、`rotate90`、`rotate270`、`flipx`、`flipz` 是全域 scoreboard objective，不會自動刪除；**只有管理員確認未被其他包使用**後，才可呼叫 `/function mcc:admin/cleanup_legacy_triggers`。`rotate180` 與現行轉向指令正常保留。

| 版本 | 重點 |
| --- | --- |
| v1.2 | Blueprint、外部 Anchor、Warehouse 材料、材料型 Undo |
| v1.3 | 背包材料優先、多人防複製、玩家相對轉向與精簡 Dialog |
| v1.4–v1.6 | 現行轉向 Trigger、取消殘留覆蓋檢查、舊 Trigger 安全清理 |
| v1.7 | 依 block ID／property 的 matcher 加速；Undo 忽略相同 ID 的 state 改動、列出差異；Flip 原地鏡射；修 Rotate/Flip 吃方塊 |
| **v1.8** | 每次新 Copy／Cut、Cut→Undo→Redo 都重置 Clipboard 方向 |

## 驗證

```bash
python3 scripts/validate-datapack.py copy-paste
python3 scripts/gen-blueprint-matcher.py --check
python3 scripts/test-copy-paste.py
python3 scripts/test-copy-paste-runtime.py --java /path/to/java --server-jar /path/to/server.jar --accept-eula
```

**v1.8 exact-build 已在 innotest 通過**完整兩人 3D-house regression：[run 37718900567](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37718900567)，全部 `MCCMP_CHECK` PASS；全量 35,720 合法 states + 4 重複案例 [run 37719130915](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37719130915) 為 `states=35724 expected=35724 fail=0 air_ret=0`。這是**發佈後補跑**，v1.8 當時由使用者要求走 direct/no-gate，不可聲稱發佈當下 gate PASS。

CI 的靜態 64-player buffer 隔離與 headless runtime **不等於兩位真人 UI**；v1.8 G、Dialog 點擊、準星手感與部分 Warehouse 材料路徑仍須實機驗。完整已驗／未驗清單見 [innotest 覆蓋表](../../docs/innotest-coverage.md)，方法見 [驗證與 Release](../../docs/datapack-validation.md)。
