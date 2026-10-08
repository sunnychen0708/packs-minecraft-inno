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

The first public API endpoint is:

`function warehouse:api/material_sources/refresh`

It rebuilds a snapshot of registered and valid Warehouse containers in `storage warehouse:api material_sources`, writes the number of exported sources to `material_source_count`, and publishes `material_source_limit:64`. The current Warehouse layout has 61 possible registered containers, so it fits inside the 64-source contract without changing existing registration data.

Later inventory APIs (count/take/refund/resolve/highlight) should consume this public snapshot instead of reading Warehouse internals directly.
