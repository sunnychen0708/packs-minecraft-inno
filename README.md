# Minecraft Inno Packs

<p align="center">
  Minecraft Java datapacks and resource packs maintained in one repository for clean development, versioning, and releases.
</p>

---

## Packs

| Pack | Type | Version | Minecraft | Description |
| --- | --- | ---: | --- | --- |
| [`utilities`](datapacks/utilities) | Data pack | [`v3.4`](https://github.com/sunnychen0708/packs-minecraft-inno/releases/tag/utilities-v3.4) | Java 26.3 | Teleportation, waypoints, coordinate display, and general survival utility systems. |
| [`warehouse`](datapacks/warehouse) | Data pack | [`v4.0`](https://github.com/sunnychen0708/packs-minecraft-inno/releases/tag/warehouse-v4.0) | Java 26.3 | Automatic item sorting and warehouse-management system. |
| [`copy-paste`](datapacks/copy-paste) | Data pack | [`v0.2`](https://github.com/sunnychen0708/packs-minecraft-inno/releases/tag/copy-paste-v0.2) | Java 26.3 | Crosshair-based rectangular region copy/paste with per-player clipboard snapshots and cross-dimension support. |
| [`cat-door-sounds`](resourcepacks/cat-door-sounds) | Resource pack | [`v1.0`](https://github.com/sunnychen0708/packs-minecraft-inno/releases/tag/cat-door-sounds-v1.0) | Java 26.2 | Custom cat meow replacement and an extra wooden-door opening sound layer. |

Each pack is stored as unpacked source. Release ZIPs are generated artifacts rather than development source.

Copy/Paste source is currently **v0.4.2** (the release link above is the last published v0.2).
See its [live validation report](datapacks/copy-paste/LIVE-VALIDATION.md) for the v0.4.1 fixes.

## Installation

Download the pack you want from [GitHub Releases](https://github.com/sunnychen0708/packs-minecraft-inno/releases).

### Data packs

Place the downloaded ZIP directly in:

```text
<world>/datapacks/
```

Then run:

```mcfunction
/reload
```

or reopen the world.

### Resource packs

Place the downloaded ZIP directly in:

```text
.minecraft/resourcepacks/
```

Then enable it from Minecraft's Resource Packs menu.

## Repository layout

```text
packs-minecraft-inno/
├─ datapacks/
│  ├─ utilities/
│  ├─ warehouse/
│  └─ copy-paste/
├─ resourcepacks/
│  └─ cat-door-sounds/
├─ scripts/
│  ├─ build-pack.sh
│  └─ validate-datapack.py
├─ docs/
│  └─ datapack-validation.md
└─ .github/
   └─ workflows/
      ├─ validate-datapacks.yml
      └─ release-pack.yml
```

Each pack remains self-contained, while shared build and release tooling stays at repository level.

## Development

Edit source directly inside the relevant pack:

```text
datapacks/<pack-name>/
resourcepacks/<pack-name>/
```

Keep `pack.mcmeta` at the root of the pack directory. Functions, JSON files, sounds, assets, and other source files stay unpacked so Git can show useful diffs.

Generated ZIP files go to `dist/`, which is ignored by Git.

### Build locally

```bash
./scripts/build-pack.sh utilities v3.4
./scripts/build-pack.sh warehouse v4.0
./scripts/build-pack.sh copy-paste v0.2
./scripts/build-pack.sh cat-door-sounds v1.0
```

The resulting ZIP is written to `dist/` with the correct Minecraft pack structure at the archive root.

### Validate datapacks

Run the generic validator before treating a datapack build as ready:

```bash
python3 scripts/validate-datapack.py utilities
python3 scripts/validate-datapack.py warehouse
python3 scripts/validate-datapack.py copy-paste
```

If a pack has `scripts/test-<pack-name>.py`, that pack-specific regression suite is also part of the validation gate. GitHub Actions runs both automatically on datapack-related pushes and pull requests, and the release workflow repeats them before building a datapack release.

For an isolated vanilla server smoke test:

```bash
python3 scripts/validate-datapack.py copy-paste \
  --java /path/to/java \
  --server-jar /path/to/server.jar \
  --accept-eula
```

See [`docs/datapack-validation.md`](docs/datapack-validation.md) for the validation levels, release rules, and what each result does or does not prove.

## Releases

All packs use the same tag format:

```text
<pack-name>-v<version>
```

Examples:

```text
utilities-v3.4
warehouse-v4.1
copy-paste-v0.2
cat-door-sounds-v1.1
```

When a matching tag is pushed, `.github/workflows/release-pack.yml` locates the matching datapack or resource pack, builds its ZIP, and publishes a GitHub Release.

## Repository conventions

| Area | Convention |
| --- | --- |
| Data packs | `datapacks/<pack-name>/` |
| Resource packs | `resourcepacks/<pack-name>/` |
| Release tags | `<pack-name>-v<version>` |
| Build output | `dist/<pack-name>-<version>.zip` |
| Source | Unpacked and committed |
| Release ZIPs | Generated and attached to Releases |

New packs should follow the same directory and release conventions so they work with the existing Git workflow without special handling.
