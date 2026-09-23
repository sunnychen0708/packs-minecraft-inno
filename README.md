# Minecraft Inno Packs

Monorepo for Minecraft Java data packs and resource packs.

## Packs

| Pack | Type | Current release | Notes |
| --- | --- | --- | --- |
| `utilities` | Data pack | `v3.2` | Originally named **整合_v3.2** |
| `warehouse` | Data pack | `v4.0` | Minecraft Java 26.3 warehouse system |
| `cat-door-sounds` | Resource pack | — | Minecraft Java 26.2 custom cat meow + door-open sound |

## Repository structure

```text
datapacks/
  utilities/
  warehouse/
resourcepacks/
  cat-door-sounds/
scripts/
  build-pack.sh
.github/workflows/
  release-pack.yml
```

Each pack is stored **unpacked** in its own directory. This keeps normal Git diffs useful and lets future updates modify individual functions, JSON files, metadata, sounds, and assets without committing development ZIP files.

## Build a pack locally

```bash
./scripts/build-pack.sh utilities v3.2
./scripts/build-pack.sh warehouse v4.0
./scripts/build-pack.sh cat-door-sounds v1.0
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
cat-door-sounds-v1.0
```

Pushing a matching tag automatically builds the corresponding directory from either `datapacks/` or `resourcepacks/` and creates a GitHub Release with the ZIP attached.

Current releases:

- Utilities v3.2
- Warehouse v4.0
