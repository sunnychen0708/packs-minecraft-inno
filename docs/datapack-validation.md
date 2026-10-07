# Datapack validation workflow

This repository treats datapack validation as a release gate, not as a player-only task.

## Validation levels

## 1. Generic static validation

Run for every datapack change:

```bash
python3 scripts/validate-datapack.py <pack-name>
```

The validator checks:

- `pack.mcmeta` exists and parses.
- Every JSON file parses.
- `data/` and function paths use valid namespaces/paths.
- Every literal function reference resolves to an existing function.
- Function tags resolve to existing functions or function tags.
- Macro functions are not called without arguments.
- Lines marked as macros with `$` must actually reference at least one `$(...)` variable.
- A `$(...)` placeholder on a line without the `$` prefix fails; Dialog `dynamic/run_command` templates are exempt.
- A `multi_action` Dialog shown from a function must have at least one action.
- Trigger objectives are inventoried; missing obvious enable/reset handling is reported as a warning.
- User-facing trigger lifecycle is enforced in the pack-specific regression test when the pack depends on it.
- A test ZIP can be built with `pack.mcmeta` and `data/` at archive root.
- ZIP CRC passes and there is no accidental extra parent directory.

Passing this stage means **static validated**. It does not prove gameplay behavior.

## 2. Pack-specific regression tests

Behavior that matters to one pack belongs in:

```text
scripts/test-<pack-name>.py
```

Examples include:

- a previously reported bug reproduced as a regression test;
- scoreboard dispatch/reset behavior;
- storage migration and old-world compatibility;
- macro instantiation with realistic arguments;
- block-state transforms, coordinate math, limits, and undo buffers;
- expected block/entity changes from core functions.

If a matching script exists, CI runs it automatically after the generic validator.

A bug fix is not considered complete until its regression case is added when it can be automated.

## 3. Vanilla server smoke test

Before calling a behavior-changing datapack runtime-validated, boot the target vanilla server when an official server JAR is available:

```bash
python3 scripts/validate-datapack.py <pack-name> \
  --java /path/to/java \
  --server-jar /path/to/server.jar \
  --accept-eula
```

This creates an isolated test world, installs a freshly built ZIP, starts vanilla Minecraft, runs `/reload`, asks the server for the enabled datapacks, and scans the console for function/datapack parser failures.

Evidence is saved under:

```text
dist/validation/<pack>-<timestamp>/console.log
```

Passing this stage means the pack can boot and reload on the tested vanilla server without the checked parser/load errors. It still does not prove every gameplay path.

## 4. Runtime regression harness

For systems that change the world, the preferred automated server test is an isolated harness that creates deterministic fixtures and checks results with commands.

Warehouse has a dedicated 26.3 harness:

```bash
python3 scripts/test-warehouse-runtime.py \
  --java /path/to/java \
  --server-jar /path/to/server.jar \
  --accept-eula
```

It boots the official server, performs `/reload`, rejects parser/datapack errors, verifies the sharded search index, exercises reset/re-registration while preserving custom data, tests the shared count/take/refund API including durable queued refunds and stale-source rejection, and covers the Resolve Block / Pick path.

Utilities has a dedicated 26.3 harness:

```bash
python3 scripts/test-utilities.py \
  --java /path/to/java \
  --server-jar /path/to/server.jar \
  --accept-eula
```

It drives tree felling, vein mining, XP ranges, Silk Touch, the pickaxe tier gate, tool durability, crop seeds, the real tick dispatch, waypoint preservation across reload, and macro instantiation.

Copy/Paste has a dedicated 26.3 behavioral harness:

```bash
python3 scripts/test-copy-paste-runtime.py \
  --java /path/to/java \
  --server-jar /path/to/server.jar \
  --accept-eula
```

It loads Copy/Paste together with Warehouse and checks Blueprint-only Copy/V behavior, Blueprint nudges, overwrite confirmation, read-only material reporting, all-or-nothing material-backed Build, inventory-before-Warehouse charging, material-aware Undo/Redo, Cut, Move, direct Rotate, five-level history, and Dialog parsing.

## 5. Cross-pack compatibility gate

Utilities, Warehouse, and Copy/Paste are designed to be installed together:

```bash
python3 scripts/test-datapack-compatibility.py
```

The static mode rejects overlapping non-Minecraft namespaces/resources, duplicate scoreboard objectives, replacement of the shared `minecraft:load` / `minecraft:tick` tags, and undeclared writes into another pack's command storage.

With the official server available:

```bash
python3 scripts/test-datapack-compatibility.py \
  --java /path/to/java \
  --server-jar /path/to/server.jar \
  --accept-eula
```

That boots all three datapacks in one Java 26.3 world and verifies representative Utilities, Warehouse, and Copy/Paste objectives/storage plus the shared Warehouse API.

## 6. innotest live multiplayer regression

Multiplayer-sensitive Copy/Paste changes have an additional live layer on `innotest.exaroton.me`.

The temporary test datapack is generated by:

```text
scripts/build-copy-paste-multiplayer-test.py
```

The server-side controller operation is:

```text
run-copy-paste-multiplayer-test
```

A normal run uses four Mineflayer 26.3 player connections. Two named players perform the regression while the other two stay online, so the test occurs in a real four-player server session rather than an armor-stand-only harness.

The regression checks:

- independent `pos1` / `pos2` selection state;
- independent Copy clipboards;
- unique `mcc_id` allocation;
- two simultaneous Blueprint previews and cleanup;
- simultaneous Move;
- separate work / Undo / Redo lanes;
- simultaneous Undo and Redo;
- simultaneous direct Rotate plus isolated Undo;
- simultaneous `x` Cut and paste;
- A-only Undo/Redo not changing B;
- B independent Undo.

The runner writes `MCCMP_CHECK PASS/FAIL ...` for each assertion and ends with `MCCMP_RESULT PASS` only when the entire current run succeeds.

Important implementation rules:

- wait for four players before starting;
- tag each run with a unique marker so an old `MCCMP_RESULT` cannot be reused accidentally;
- do not use a fixed sleep as completion detection — exaroton can report `Can't keep up` and scheduled functions may run late;
- clean the reserved test area, tags, scoreboard objective, temporary test ZIP, and reload only after the current run has produced a result or timed out;
- distinguish harness/parser/bot infrastructure failures from datapack assertion failures before changing datapack code.

The 2026-10-07 final run passed every check above with `MCCMP_RESULT PASS` while four bot players were online. The corresponding four-bot session also completed a full five-minute hold successfully.

This layer is **not** the same as two Windows users manually operating the UI. It proves multiplayer server-side state separation with real player entities and real `/trigger`-compatible identities, not mouse/UI ergonomics.

Operational details are in [`exaroton-operations.md`](exaroton-operations.md).

## 7. Real-client verification

Some things a headless server or Mineflayer presence test cannot show: G-key flow, whether Dialog buttons can be clicked and fit the window, crosshair raycasts, and Dialog JSON that only loads when a world is opened.

For these, `scripts/real-client/` (Windows) drives the real Minecraft client with OS-level keyboard and mouse input in a disposable test world and judges results from saved world files rather than trusting a datapack's own PASS message.

- `mcdrive.py` sends input only when Minecraft is foreground.
- `realplay.py` verifies real command/trigger/reload feedback.
- `mcworld.py` reads save data; `defaults.json` fills 26.3 block-state defaults omitted from palettes.
- `stage*.py` scripts cover Warehouse registration/sorting, Copy/Paste Build/Undo/Redo, transforms, charging, Dialog navigation, Utilities vein behavior, and combined-pack scenarios.

GitHub Actions does not run these stages. A green CI run or a green Mineflayer multiplayer run therefore does not prove G, Dialog clicks, real mouse targeting, or crosshair raycasts.

Two simultaneous Windows real clients have not been tested yet; when a client-only check remains, document exactly what was not covered.

## Release rule

For datapacks:

1. Generic static validation must pass.
2. Pack-specific regression tests must pass when present.
3. The cross-pack static compatibility gate must pass.
4. Datapack releases must pass the combined official Minecraft 26.3 Utilities + Warehouse + Copy/Paste runtime compatibility gate.
5. Utilities, Warehouse, and Copy/Paste releases must also pass their dedicated 26.3 runtime harnesses.
6. For multiplayer-sensitive Copy/Paste state changes, run the innotest live multiplayer regression before calling the change multiplayer-validated.
7. Do not describe a pack as real-client validated if only CI or Mineflayer testing was run.
8. Do not create a release from a known failing validation run.

GitHub Actions runs generic validation, pack-specific regressions, cross-pack static compatibility, dedicated Utilities/Warehouse/Copy-Paste runtime jobs, and the all-datapacks 26.3 compatibility job on relevant `main` pushes and pull requests.

The release workflow verifies the tag version against `pack.mcmeta`, reruns the combined all-datapacks runtime gate for every datapack tag, reruns the dedicated Utilities, Warehouse or Copy/Paste runtime gate when applicable, then builds and publishes the ZIP. Publishing is idempotent: runs for the same tag are serialized, and when the release already exists the ZIP is uploaded to it instead of failing. A release can also be started manually (`workflow_dispatch` on `main` with a `tag` input such as `utilities-v3.7`): the same gates run first, and only then does the workflow create the annotated tag on that `main` commit; it refuses a tag that already points at another commit. Generated release notes start at the same pack's previous release tag (e.g. `copy-paste-v1.5` for `copy-paste-v1.6`), not at whichever pack was tagged last.
