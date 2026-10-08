# Datapack validation workflow

This repository treats datapack validation as a release gate, not as a player-only task.

## Validation levels

### 1. Generic static validation

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

- A previously reported bug reproduced as a regression test.
- Scoreboard dispatch/reset behavior.
- Storage migration and old-world compatibility.
- Macro instantiation with realistic arguments.
- Block-state transforms, coordinate math, limits, and undo buffers.
- Expected block/entity changes from core functions.

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

For systems that change the world, the preferred final test is an isolated server harness that creates deterministic fixtures and checks results with commands.

Examples:

- Copy a known block cuboid, paste it, then compare destination blocks.
- Cut a known cuboid, verify the source becomes air, run undo, and compare restoration.
- Rotate asymmetric fixtures by 90/180/270 degrees and assert exact output coordinates and block states.
- Mirror asymmetric fixtures and assert exact output coordinates and block states.
- Test positive and negative coordinates.
- Test Overworld/Nether/End paths.
- Preserve existing scoreboard/storage data across an upgrade.

A headless harness should use markers, armor stands, storage, scoreboards, and fixed blocks where possible so a human player is not required.

Warehouse has a dedicated 26.3 harness:

```bash
python3 scripts/test-warehouse-runtime.py \
  --java /path/to/java \
  --server-jar /path/to/server.jar \
  --accept-eula
```

It boots the official server, performs `/reload`, rejects parser/datapack errors, seeds all 61 registration records, runs `warehouse:admin/reset_registrations`, verifies only `registered`/`valid` were cleared, verifies custom box names and classification overrides survived, and re-registers a cleared slot through the normal Warehouse save path.

## 5. Client-only checks

Manual player testing is the last resort, not the default validation strategy.

Use it only for behavior that a vanilla headless server cannot faithfully exercise, such as client UI presentation, keybind feel, or a genuinely player-only interaction. When a client-only check remains, document exactly what was not automated.

## Release rule

For datapacks:

1. Generic static validation must pass.
2. Pack-specific regression tests must pass when present.
3. Behavior-changing releases should also pass the vanilla server smoke/runtime harness when the target server JAR is available.
4. Do not describe a pack as "runtime validated" if only static checks were run.
5. Do not create a release from a known failing validation run.

GitHub Actions runs stages 1 and 2 automatically for repository datapacks. Warehouse and Copy/Paste also run official Minecraft 26.3 runtime regressions on main. The release workflow repeats static/pack-specific validation, verifies the tag version matches `pack.mcmeta`, and reruns the official 26.3 runtime gate for Warehouse and Copy/Paste before building a release ZIP.
