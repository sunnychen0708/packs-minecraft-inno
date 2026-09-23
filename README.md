# Minecraft Inno Packs

Monorepo for Minecraft Java data packs and resource packs.

## Packs

| Pack | Type | Current release | Notes |
| --- | --- | --- | --- |
| `utilities` | Data pack | `v3.2` | Originally named **整合_v3.2** |
| `warehouse` | Data pack | `v4.0` | Minecraft Java 26.3 warehouse system |

## Repository structure

```text
datapacks/
  utilities/
  warehouse/
resourcepacks/
scripts/
  build-pack.sh
.github/workflows/
  release-pack.yml
```

Each pack is stored **unpacked** in its own directory. This keeps normal Git diffs useful and lets future updates modify individual functions, JSON files, metadata, and assets without committing development ZIP files.

`resourcepacks/` is reserved for resource packs. Put each resource pack in its own subdirectory, using the same layout as the data packs.

## Build a pack locally

```bash
./scripts/build-pack.sh utilities v3.2
./scripts/build-pack.sh warehouse v4.0
```

Output goes to `dist/`, which is ignored by Git.

## Create a release

Release tags use:

```text
<pack-name>-v<version>
```

Examples:

```text
utilities-v3.3
warehouse-v4.1
```

Pushing a matching tag automatically builds the corresponding directory from either `datapacks/` or `resourcepacks/` and creates a GitHub Release with the ZIP attached.

Current releases:

- Utilities v3.2
- Warehouse v4.0
