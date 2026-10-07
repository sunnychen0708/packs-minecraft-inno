# Minecraft Inno Packs

<p align="center">
  Minecraft Java datapacks and resource packs maintained in one repository for clean development, versioning, releases, CI, and live server validation.
</p>

---

## Packs

| Pack | Type | Source | Latest release | Minecraft | Description |
| --- | --- | ---: | ---: | --- | --- |
| [`utilities`](datapacks/utilities) | Data pack | v3.7 | [`v3.6`](https://github.com/sunnychen0708/packs-minecraft-inno/releases/tag/utilities-v3.6) | Java 26.3 | Teleportation, waypoints, coordinate display, and general survival utility systems. |
| [`warehouse`](datapacks/warehouse) | Data pack | v4.5 | [`v4.5`](https://github.com/sunnychen0708/packs-minecraft-inno/releases/tag/warehouse-v4.5) | Java 26.3 | Automatic sorting, shared inventory API, durable refunds, search/Highlight, and survival Pick. |
| [`copy-paste`](datapacks/copy-paste) | Data pack | v1.6 | [`v1.5`](https://github.com/sunnychen0708/packs-minecraft-inno/releases/tag/copy-paste-v1.5) | Java 26.3 | Survival building editor: Blueprint preview/micro-adjust, construction from the player's inventory and Warehouse, player-relative turn/flip, Cut/Move, and material-aware Undo/Redo. |
| [`cat-door-sounds`](resourcepacks/cat-door-sounds) | Resource pack | v1.0 | [`v1.0`](https://github.com/sunnychen0708/packs-minecraft-inno/releases/tag/cat-door-sounds-v1.0) | Java 26.2 | Custom cat meow replacement and an extra wooden-door opening sound layer. |

Each pack is stored as unpacked source. Release ZIPs are generated artifacts rather than development source.

Source versions: Utilities **v3.7**, Warehouse **v4.5**, Copy/Paste **v1.6**, cat-door-sounds **v1.0**. Latest releases: Utilities **v3.6**, Warehouse **v4.5**, Copy/Paste **v1.5**, cat-door-sounds **v1.0**. Utilities v3.7 and Copy/Paste v1.6 are currently source-only and have not been tagged or released.

Copy/Paste builds from a Blueprint preview using materials from the player's own inventory first and the shared Warehouse second. Warehouse is the shared sorting/storage backend and its API is what Copy/Paste and Pick use.

Per-pack details and version history: [Utilities](datapacks/utilities/README.md), [Warehouse](datapacks/warehouse/CHANGELOG.md), [Copy/Paste](datapacks/copy-paste/README.md).

## Current validation status

The current Java 26.3 source has passed:

- generic static validation and pack-specific regressions;
- dedicated Utilities, Warehouse, and Copy/Paste official-server runtime regressions;
- all-datapacks Java 26.3 compatibility runtime;
- an `innotest` live multiplayer Copy/Paste regression with four Mineflayer player connections online, including independent selection/clipboard state, Blueprint, simultaneous Move, Undo/Redo, Rotate, Cut/Paste, and per-player history isolation.

The final assertion sequence of the latest live multiplayer session ended with `MCCMP_RESULT PASS`, but the same persistent server log also contains earlier failed attempts from that debugging session. A stricter current-session server-error gate has since been added; until a fresh run passes that gate, do not describe the live validation as a clean-log pass. After testing, `innotest.exaroton.me` was stopped and verified `OFFLINE`, `0/10`.

This does **not** replace the Windows real-client stages for UI clicks, G-key flow, Dialog behavior, or crosshair raycasts. See [`docs/datapack-validation.md`](docs/datapack-validation.md) for the validation layers and [`docs/HANDOFF.md`](docs/HANDOFF.md) for the current handoff state.

## Installation

Download the pack you want from [GitHub Releases](https://github.com/sunnychen0708/packs-minecraft-inno/releases).

### Data packs

Place the downloaded ZIP directly in:

```text
<world>/datapacks/
```

Then leave and re-enter the world. `/reload` refreshes functions only; Dialog pages stored as JSON are loaded when the world opens, so after an update always re-enter the world when Dialog registry JSON changed.

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
│  ├─ validate-datapack.py
│  ├─ test-<pack>.py
│  ├─ test-*-runtime.py
│  ├─ test-datapack-compatibility.py
│  ├─ build-copy-paste-multiplayer-test.py
│  ├─ exaroton_innotest.py
│  ├─ exaroton_inno_uuid_migrate.py
│  ├─ mineflayer26/
│  └─ real-client/
├─ ops/
│  ├─ exaroton-request.json
│  ├─ mineflayer-request.json
│  └─ inno-maintenance-request.json
├─ tests/evidence/
├─ docs/
│  ├─ datapack-validation.md
│  ├─ exaroton-operations.md
│  └─ HANDOFF.md
└─ .github/workflows/
   ├─ validate-datapacks.yml
   ├─ release-pack.yml
   ├─ exaroton-innotest.yml
   ├─ mineflayer-innotest.yml
   └─ exaroton-inno-maintenance.yml
```

Each pack remains self-contained, while shared build, validation, live-test, and release tooling stays at repository level.

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
./scripts/build-pack.sh utilities v3.7
./scripts/build-pack.sh warehouse v4.5
./scripts/build-pack.sh copy-paste v1.6
./scripts/build-pack.sh cat-door-sounds v1.0
```

The resulting ZIP is written to `dist/` with the correct Minecraft pack structure at the archive root. `build-pack.sh` needs the `zip` command; the release workflow runs it on Linux.

### Validate datapacks

Run the generic validator before treating a datapack build as ready:

```bash
python3 scripts/validate-datapack.py utilities
python3 scripts/validate-datapack.py warehouse
python3 scripts/validate-datapack.py copy-paste
```

If a pack has `scripts/test-<pack-name>.py`, that pack-specific regression suite is also part of the validation gate. GitHub Actions runs both automatically on datapack-related pushes and pull requests.

Cross-pack compatibility is a separate gate for the three datapacks that are intended to coexist:

```bash
python3 scripts/test-datapack-compatibility.py
```

That static check rejects namespace/resource collisions, duplicate scoreboard objectives, unsafe foreign storage writes, and load/tick tag replacement. CI also boots **Utilities + Warehouse + Copy/Paste together on the official Minecraft 26.3 server** and verifies their representative objectives, storage initialization, and shared Warehouse API coexist.

For isolated runtime validation, the repository also has dedicated Utilities, Warehouse, and Copy/Paste harnesses. Example:

```bash
python3 scripts/validate-datapack.py copy-paste \
  --java /path/to/java \
  --server-jar /path/to/server.jar \
  --accept-eula
```

See [`docs/datapack-validation.md`](docs/datapack-validation.md) for exact coverage and release rules.

## exaroton and live multiplayer testing

Operational automation is kept separate from normal pack source:

- `.github/workflows/exaroton-innotest.yml` controls only `innotest.exaroton.me` for normal test-server work.
- `.github/workflows/mineflayer-innotest.yml` provides one-player probes or four-player 26.3 test sessions.
- `.github/workflows/exaroton-inno-maintenance.yml` is the separate owner-authorized **offline production UUID maintenance** path.

All three workflows are request-driven through `ops/*.json`. The checked-in clean baseline is `noop`; request files are operation triggers, not a queue of unfinished work.

The GitHub secret `EXAROTON_API_TOKEN` must never be committed or copied into an ops request.

For the complete safety model, Java 26.3 player-data layout, online-UUID -> offline-UUID test-world migration, Mineflayer constraints, and the four-player live regression sequence, read [`docs/exaroton-operations.md`](docs/exaroton-operations.md).

## Releases

All packs use the same tag format:

```text
<pack-name>-v<version>
```

Examples:

```text
utilities-v3.4
warehouse-v4.4
copy-paste-v1.2
cat-door-sounds-v1.0
```

When a matching tag is pushed, `.github/workflows/release-pack.yml` locates the matching datapack or resource pack, validates it, builds its ZIP, and publishes a GitHub Release.

## Repository conventions

| Area | Convention |
| --- | --- |
| Data packs | `datapacks/<pack-name>/` |
| Resource packs | `resourcepacks/<pack-name>/` |
| Release tags | `<pack-name>-v<version>` |
| Build output | `dist/<pack-name>-<version>.zip` |
| Source | Unpacked and committed |
| Release ZIPs | Generated and attached to Releases |
| Operational requests | `ops/*.json`, clean baseline = `noop` |
| Server-operation docs | `docs/exaroton-operations.md` |
| Maintainer handoff | `docs/HANDOFF.md` |

New packs should follow the same directory and release conventions so they work with the existing Git workflow without special handling.
