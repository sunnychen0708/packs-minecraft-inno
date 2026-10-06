# Warehouse v4.4.1

Minecraft Java 26.3 automatic sorting warehouse data pack.

The actual pack source lives directly in this directory. Keep `pack.mcmeta` and `data/` here so Git can track individual changes.

## Release

Current version: `v4.4.1`

Latest published release: `warehouse-v4.4.1.zip`

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
