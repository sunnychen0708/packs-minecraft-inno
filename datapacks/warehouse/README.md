# Warehouse v4.7

Minecraft Java 26.3 自動分類倉庫 Datapack。最新 [warehouse-v4.7.zip](https://github.com/sunnychen0708/packs-minecraft-inno/releases/tag/warehouse-v4.7)。

按 **G** 開倉庫主畫面：查詢物品、分類設定、箱子管理、查看倉庫、Pick；也可導向 Copy/Paste 建築工具。

## 安裝與玩家操作

1. 從世界 `datapacks/` 移除舊 `Minecraft_Warehouse_*.zip`／`warehouse-v*.zip`，只保留新版 ZIP。
2. 放入 `warehouse-v4.7.zip`，**退出世界再進入**以載入 Dialog registry；`/reload` 不保證更新這類 Dialog。
3. 不會重置既有 **61 箱註冊、箱名、玩家自訂分類覆寫、scoreboard**。移除 Warehouse 前，先執行 `/function warehouse:chunks/release` 釋放本包擁有的 forceload。

在 G →「查詢物品」可搜尋繁中名稱、分類名稱、Minecraft ID 或一個中文字；上限 30 筆。點結果可調整分類、Highlight 箱子或「取一組」。分類修改後，舊主箱的相同 item ID 會背景搬移，依序主箱 → 溢位箱 → 保留在入口箱，**滿箱不刪物品**。原版自由文字 Dialog 的權限確認頁無法用純 Vanilla 隱藏。

玩家看著約 6 格內方塊，可用 `/trigger pick`（或 Dialog「Pick 一組」）從 Warehouse 取最多一組原版堆疊。不能可靠偵測滑鼠中鍵，故不用滑鼠中鍵當入口。

管理員開關：

```mcfunction
/function warehouse:system/on
/function warehouse:system/off
/function warehouse:system/toggle
```

倉庫 chunk 自 v4.6 起會依註冊維持 forceload，背景 sorting、查詢、Pick 與 API 不必玩家在場；**如果整個 server 因無玩家而暫停 tick，背景整理仍不會進行**。只支援原版三維度，未正式支援自訂維度。

## 舊資料／版本

- 可以從 26.2 v3.2、26.3 v3.3/v3.4、Warehouse v4.0–v4.6 升級，玩家自訂分類優先於預設規則；索引是可重建資料。
- v4.2 起將搜尋索引拆為 72 shard，每 tick 一份，避免 65,536 command-chain 上限。
- v4.7 修正背景 Compact 與跨維度搬運讀取來源／主箱／溢位箱時，誤把地獄或終界註冊箱當主世界座標的問題；**不改既有存檔格式、不需 migration**。

| 版本 | 主要變更 |
| --- | --- |
| v0.x–v1.x | 61 箱架構、倉庫註冊、54 分類箱／6 溢位、查詢與玩家覆寫 |
| v2.x–v3.x | Dialog 搜尋、分類搬移／庫存狀態、Minecraft 26.3 相容 |
| v4.0–v4.2 | 26.3 物品（Poplar、混凝土／羊毛階梯與半磚、Explorer Maps 等）、reset hotfix、72-shard 搜尋 |
| v4.3 | 64-source 去重材料 API、持久退款 queue、Highlight |
| v4.4–v4.5 | Pick、Resolve Block、分類／Dialog／Runtime 修正 |
| v4.6 | 註冊箱 chunk forceload、遠端庫存查詢與 Compact 最佳化 |
| **v4.7** | 修正主世界／地獄／終界跨維度讀取與合併 |

## 給其他 Datapack 的共用 API

Warehouse 是 Copy/Paste 的共享材料後端。有效的註冊容器會去重（同一個大箱兩半／重複編號不重複算），最多 **64 個來源**；目前設計有 61 個註冊箱位。

```mcfunction
function warehouse:api/material_sources/refresh
function warehouse:api/count_item {item_id:"minecraft:stone"}
function warehouse:api/take_item {item_id:"minecraft:stone",count:50}
function warehouse:api/refund_item {item_id:"minecraft:stone",count:50}
```

`material_sources/refresh` 更新 `storage warehouse:api material_sources`，並公開 `material_source_count`／`material_source_limit:64`。其他 API 以 `storage warehouse:api result` 回傳狀態。

- **Count**：回傳 `ok`、`complete`、`available`、`sources_scanned`、`stale_sources`、`source_limit`。實體箱缺失或不可讀時 `complete=0b`、`ok=0b`，不能把不完整數量當可用庫存。
- **Take**：僅取普通 stack（無 `components` 或為空），**all-or-nothing**。任何來源 stale／總數不足時不移動物品，回傳 `source_unavailable`／`insufficient_stock`；成功 preflight 後同步扣足指定數量。
- **Refund**：先歸還至 `c00` 入口箱；空間不足、箱子暫時不可用或未註冊時，剩餘材料記錄到 `storage warehouse:api pending_refunds`，由 `warehouse:tick` 重試，每 tick 處理一筆。不以掉到地上的物品替代退款。
- **Highlight**：對執行的玩家顯示註冊箱的 `end_rod` 粒子與箱號／維度／A+B 座標；未註冊／失效會拒絕。

```mcfunction
data modify storage warehouse:api request set value {code:11}
function warehouse:api/highlight

execute positioned 100 64 100 run function warehouse:api/resolve_block
```

`resolve_block` 讀取執行座標上的方塊，模擬 Silk Touch loot 解析可生存取得的 item ID／原版最大堆疊，不破壞方塊；無對應時回傳 `no_survival_item`。

## 已知限制與驗證

尚無分類規則全覽／一鍵清空分類、未分類物品批次設定、完整滿箱通知中心；部分新物品可能以 Minecraft ID 顯示。純 Vanilla 不提供硬崩潰瞬間的資料庫級交易保證。

```bash
python3 scripts/validate-datapack.py warehouse
python3 scripts/test-warehouse.py
python3 scripts/test-warehouse-runtime.py --java /path/to/java --server-jar /path/to/server.jar --accept-eula
```

v4.7 三維度 Compact／merge 在 innotest 通過 27 checkpoints。詳見 [驗證證據與限制](../../docs/innotest-coverage.md)；不要把 API 驗證直接當成 Highlight 的玩家視覺確認。
