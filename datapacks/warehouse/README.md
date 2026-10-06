# Warehouse v4.5

Minecraft Java 26.3 automatic sorting warehouse data pack.

The actual pack source lives directly in this directory. Keep `pack.mcmeta` and `data/` here so Git can track individual changes.

## Release

Current version: `v4.5`

Latest published release: `warehouse-v4.5.zip`

## 玩家說明

按 **G** 開啟自動分類倉庫主畫面。

### 安裝／升級

1. 移除舊版 Minecraft_Warehouse_26.2_v*.zip、Minecraft_Warehouse_26.3_v*.zip 或舊 warehouse-v*.zip；不要同時載入兩份。
2. 將 warehouse-v4.5.zip 放入世界 datapacks 資料夾。
3. 退出世界再重新進入（Dialog 介面只在進入世界時載入，只打 /reload 不會更新介面）。
4. 既有 61 箱註冊、玩家分類覆寫、自訂箱名、scoreboard 與其他世界資料會沿用；migration 不會重設這些資料。

### 查詢／分類設定

- G →「查詢物品」，或「分類設定」→「打字選擇物品」。
- 支援繁中名稱、分類名稱、Minecraft ID；一個中文字也可搜尋。
- 查詢結果會顯示目前分類箱與有庫存／無庫存／箱未註冊／箱失效狀態。
- 點結果可新增、移動或移除分類，並可直接 Highlight 或取一組。
- 修改分類後，舊主分類箱內相同 base item ID 的既有庫存會背景搬往新分類箱。
- 搬移沿用主箱 → 同區溢位箱 → 放不下保留來源的安全搬運邏輯。
- 每次搜尋最多採用前 30 筆結果。
- 自由文字 Dialog 仍會出現 Minecraft 原版高權限確認頁，純 Vanilla 無法取消。

### 自動整理控制（需 OP）

```mcfunction
/function warehouse:system/on
/function warehouse:system/off
/function warehouse:system/toggle
```

預設開啟。

### 舊資料相容性

- 可從 Minecraft 26.2 v3.2、26.3 v3.3/v3.4、Warehouse v4.0～v4.4 直接升級。
- 不重設 warehouse:chests：61 箱座標、dimension 與其他既有註冊 metadata 保留。
- 不重設 warehouse:boxnames：玩家自訂箱名保留。
- 不重設 warehouse:rules overrides：玩家新增／移動／移除的分類覆寫保留。
- 不更名既有 scoreboard objectives；既有玩家與系統分數可繼續使用。
- v4.0～v4.5 migrations 都以可再生成資料或版本 marker 為主；目前 v4.5 marker 不會清空既有世界資料。
- 搜尋索引屬可重建資料；v4.2 起使用 72-shard 建立流程。

### 目前限制

- 尚未提供「依箱子瀏覽全部分類規則」與「一鍵清空該箱全部分類」。
- 尚未提供入口箱「未分類物品清單 → 直接批次設定」頁面。
- 尚未提供完整的滿箱／溢位滿／箱子失效通知中心與快速重新註冊提示。
- 一般背景整理本身不會永久自動管理所有倉庫 chunk 的 forceload；共用 API 呼叫只會暫時處理它需要的來源 chunk。
- 尚未正式支援自訂維度。
- 查看倉庫遇到名稱表之外的新物品時，可能顯示 Minecraft ID。
- 純 Vanilla Datapack 無法提供伺服器硬崩潰瞬間的資料庫級 transaction 保證。
- 真正的滑鼠中鍵事件無法由純 Vanilla datapack 可靠偵測，因此 Pick 使用 Trigger / Dialog。

### Minecraft 26.3 新物品分類（v4.0 起）

- 28 交通運輸：楊木船、儲物箱楊木船。
- 35 沙岩建材：16 色混凝土階梯、16 色混凝土半磚。
- 36 原木木材：楊木原木、楊木塊、剝皮楊木原木、剝皮楊木塊、楊木材。
- 37 木製建材：楊木階梯、半磚、柵欄、柵欄門、按鈕、壓力板、門、地板門、告示牌、懸掛式告示牌、展示架。
- 41 探索導航：26.3 的 16 種獨立 Explorer Map 物品。
- 52 羊毛織染：16 色羊毛階梯、16 色羊毛半磚、16 色坐墊、乾草床。
- 56 林地生態：楊木樹苗、紅／橙／黃楊木樹葉、層孔菇、紅灌木。

## Version history

See [CHANGELOG.md](CHANGELOG.md) for the Warehouse version history and known issues.


## Shared API

Warehouse is the shared inventory backend for other packs that are installed alongside it.

The shared material-source snapshot is rebuilt with:

`function warehouse:api/material_sources/refresh`

It exports registered and valid Warehouse containers to `storage warehouse:api material_sources`, writes the number of exported sources to `material_source_count`, and publishes `material_source_limit:64`. The current Warehouse layout has 61 registration slots, so it fits inside the 64-source contract without changing existing registration data. If the same physical large chest is registered under multiple codes, the public snapshot exports it only once (including reversed A/B registration) so inventory cannot be double-counted.

### Count item

Call the public macro function with an item ID:

```mcfunction
function warehouse:api/count_item {item_id:"minecraft:stone"}
```

The result is written to `storage warehouse:api result`:

```snbt
{
  ok:1b,
  complete:1b,
  item_id:"minecraft:stone",
  available:128,
  sources_scanned:61,
  stale_sources:0,
  source_limit:64
}
```

The endpoint refreshes the public material-source snapshot first, temporarily force-loads only the chunks needed for each registered source, and never removes a force-load ticket that already existed before the API call. If a source is still registered/valid in storage but the physical large chest is missing or inaccessible, `complete` and `ok` become `0b` and `stale_sources` is incremented instead of silently reporting a trustworthy total.

### Take item

```mcfunction
function warehouse:api/take_item {item_id:"minecraft:stone",count:50}
```

The endpoint consumes only **plain stacks** of the requested item ID. A stack is plain when its `components` compound is absent or has zero direct children; named/container/custom-data variants are skipped.

Withdrawal is **all-or-nothing**. The API first counts the same plain stacks across a deduplicated snapshot of physical Warehouse containers. If any source is stale or the total is below `count`, it removes nothing and reports `error:"source_unavailable"` or `error:"insufficient_stock"`. If preflight succeeds, count and withdrawal run synchronously in the same function call, then the exact requested amount is removed.

### Refund item

```mcfunction
function warehouse:api/refund_item {item_id:"minecraft:stone",count:50}
```

Refund always targets Warehouse entry chest `c00`; Warehouse's normal sorter remains responsible for routing returned items afterward. The endpoint probes the item's vanilla max stack size, merges into existing plain stacks first, then uses empty entry slots.

Refund is durable: if `c00` is full, temporarily unavailable, stale, or not currently registered, the physical remainder is appended to `storage warehouse:api pending_refunds` before the API returns. The result reports `inserted`, `queued`, `deferred`, and leaves `remaining:0` once Warehouse has accepted responsibility for a valid positive refund. `warehouse:tick` retries one pending entry per tick without overwriting the last public API result. This lets callers such as Copy/Paste finish an Undo safely even when the entry chest cannot accept every returned stack immediately.

### Highlight

Warehouse 已提供玩家可見的 Highlight API：

```mcfunction
data modify storage warehouse:api request set value {code:11}
function warehouse:api/highlight
```

API 直接讀取既有 `warehouse:chests` 註冊資料，不建立第二份箱子座標表。有效箱位會只對呼叫玩家顯示 `end_rod` 粒子 Highlight，並在聊天列印箱號、維度與 A/B 兩半座標；未註冊或失效箱位會拒絕 Highlight。

遊戲內「物品查詢」也共用這條路徑：搜尋物品 → 點選結果 → 分類結果頁 →「Highlight 箱子」。因此搜尋與分類設定使用同一份 `wh_rulebox` / Warehouse 註冊資料，不需要額外同步。

### Resolve block

`warehouse:api/resolve_block` 會在目前執行位置讀取方塊，使用 Silk Touch loot 模擬解析其可取得的生存物品，但不破壞來源方塊：

```mcfunction
execute positioned 100 64 100 run function warehouse:api/resolve_block
```

成功時 `storage warehouse:api result` 會包含 `operation:"resolve_block"`、`item_id` 與該物品的 `max_stack`。沒有正常生存掉落對應的方塊會回報 `no_survival_item`，不會憑空建立物品。

## Pick

玩家看著方塊後可直接：

```mcfunction
/trigger pick
```

Pick 最遠約 6 格，會忽略空氣與水／岩漿等流體，解析準星方塊後使用共用 Warehouse `count_item` / `take_item` API 取料。一次最多拿該物品的原版最大堆疊數；若倉庫只有較少數量，會拿現有數量。只消耗 Warehouse API 認定的普通、無自訂 components 堆疊。

真正的滑鼠中鍵事件無法由純 Vanilla datapack 可靠偵測，因此 Phase 4 的入口是 `/trigger pick` 與 Warehouse 主 Dialog 的「Pick 一組」按鈕。物品查詢也共用同一條取料路徑：搜尋物品 → 點選結果 →「取一組」，不另外維護第二套庫存或扣料邏輯。

## Validation

Static and pack-specific checks:

```console
python3 scripts/validate-datapack.py warehouse
python3 scripts/test-warehouse.py
python3 scripts/test-datapack-compatibility.py
```

Official Minecraft 26.3 behavioral regression:

```console
python3 scripts/test-warehouse-runtime.py \
  --java /path/to/java \
  --server-jar /path/to/server.jar \
  --accept-eula
```

CI runs the dedicated Warehouse runtime regression and a second combined runtime gate with Utilities + Warehouse + Copy/Paste loaded together. Datapack release tags rerun the combined compatibility gate, and Warehouse releases also rerun the dedicated Warehouse runtime gate before publishing.
