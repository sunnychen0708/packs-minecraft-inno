# Warehouse v4.2

Minecraft Java 26.3 automatic sorting warehouse data pack.

The actual pack source lives directly in this directory. Keep `pack.mcmeta` and `data/` here so Git can track individual changes.

## Release

Repository tag: `warehouse-v4.2`

Release ZIP: `warehouse-v4.2.zip`

## Version history

See [CHANGELOG.md](CHANGELOG.md) for the Warehouse version history and known issues.


## Shared API

Warehouse is the shared inventory backend for other packs that are installed alongside it.

The shared material-source snapshot is rebuilt with:

`function warehouse:api/material_sources/refresh`

It exports registered and valid Warehouse containers to `storage warehouse:api material_sources`, writes the number of exported sources to `material_source_count`, and publishes `material_source_limit:64`. The current Warehouse layout has 61 possible registered containers, so it fits inside the 64-source contract without changing existing registration data.

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

The endpoint consumes only **plain stacks** of the requested item ID. Stacks carrying custom components are intentionally skipped so another pack cannot accidentally consume named/container/custom-data variants merely because the base item ID matches.

The result is written to `storage warehouse:api result` with `requested`, `taken`, `remaining`, `sources_scanned`, and `stale_sources`. `ok:1b,complete:1b` means the full requested amount was removed. A partial withdrawal reports `error:"insufficient_stock"` and leaves the exact partial amount in `taken` so a caller can compensate safely.

### Refund item

```mcfunction
function warehouse:api/refund_item {item_id:"minecraft:stone",count:50}
```

Refund always targets Warehouse entry chest `c00`; Warehouse's normal sorter remains responsible for routing returned items afterward. The endpoint probes the item's vanilla max stack size, merges into existing plain stacks first, then uses empty entry slots. The result exposes `inserted` and `remaining`. A full entry chest returns `error:"entry_full"` rather than deleting the remainder.

`resolve_block` and `highlight` will be added on top of this same API/storage contract in their dedicated implementation phases. They should not duplicate Warehouse registration data.
