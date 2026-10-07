# Worker Instructions

These instructions apply to the entire repository. Every contributor, coding agent, automation worker, and reviewer must follow them.

## Production-world compatibility is mandatory

The `inno` Minecraft server contains real, persistent player and world data. Treat compatibility with that existing data as a release requirement, not as an optional regression check.

For any datapack that has already been deployed to `inno` — currently including **Warehouse** and **Utilities** — any change that can affect saved world/player state must be validated against a copy of the real production world data before production rollout.

This includes, but is not limited to:

- storage or scoreboard schema changes;
- migrations or version-upgrade logic;
- chest/position registrations;
- player settings, statistics, rules, names, queues, or other persistent state;
- changes that reinterpret existing stored values;
- changes to code that moves, rewrites, deletes, refunds, compacts, or otherwise mutates existing inventory/world data;
- refactors where an incorrect mapping could act on a different registered chest, slot, player, dimension, or stored record.

### Required validation path

For the changes above:

1. Make or obtain a **copy of the current `inno` world data**.
2. Load that copy on **`innotest`**.
3. Apply the candidate datapack/update to that copied world.
4. Verify the upgrade using the copied production data, including the relevant existing registrations, player state, inventories, storage, and migration markers.
5. Only consider production rollout after this upgrade-path test passes.

A newly generated or clean test world is useful for isolated functional tests, but **it is not sufficient evidence for backward compatibility**. Clean-world CI/runtime tests are supplementary and must not replace the `inno`-copy-on-`innotest` upgrade test when existing production data could be affected.

### innotest server lifecycle and credit usage

The default post-test state for `innotest` is **ONLINE**.

- Do **not** stop `innotest` merely because validation or testing is finished. Leave it running unless the user explicitly asks for it to be shut down.
- Avoid unnecessary stop/start and restart cycles. In this project, repeated server lifecycle changes can consume more exaroton credits than simply leaving the test server running.
- A worker may stop or restart `innotest` without separate user approval **only when installing or applying something that cannot be completed correctly without a server restart**.
- When a restart is required for installation or deployment, perform only the minimum necessary stop/restart cycle, then leave `innotest` **ONLINE** after the installation and validation are complete unless the user explicitly requested that it remain off.
- Do not treat shutdown as routine cleanup. Cleaning test blocks, temporary files, scoreboards, forceloads, bots, or other test state does **not** imply stopping the server.

### Safety constraints

- Do not modify or experiment on the live `inno` world merely to test a change.
- Do not reset, rebuild, or migrate production data just because a clean-world test passes.
- Preserve existing persistent-data formats whenever an implementation-only refactor can achieve the same goal.
- Prefer implementation-path changes with no migration over schema changes for Warehouse and Utilities.
- If a change requires a migration, test both upgrade correctness and idempotency on the production-world copy.
- If there is uncertainty about whether a change can affect existing data, treat it as data-affecting and use the production-world-copy test path.

## Datapack performance priority

For datapack implementation, optimization, and code review, optimize for **server tick cost first**.

The default priority is:

1. **Time complexity and hot-path cost**, especially work that runs every tick or at high frequency.
2. **Commands executed per tick / per hot-path invocation**, including failed conditional checks, selector scans, repeated dispatch chains, and unnecessary function calls.
3. **Server-side runtime memory / space complexity** only when the added state is large, grows with input size, is unbounded, creates many entities, or materially increases persistent storage.

In this project, a small fixed amount of extra scoreboard/storage state is normally an acceptable trade for a meaningful reduction in recurring tick work. Do not reject a faster design merely because it uses a small constant or bounded amount of additional server RAM.

Conversely, do not trade unbounded or very large persistent/runtime state for a negligible tick-time improvement.

When comparing or proposing datapack algorithms, workers must report the relevant **before/after hot-path command count or command-count model**, **time complexity**, and **additional server-side runtime/persistent space cost** when those values materially differ. For code that runs in `#minecraft:tick`, scheduled loops, or other background paths, treat recurring command cost as more important than one-time load/reload/build cost unless profiling shows otherwise.

For this repository, “runtime memory” means memory used by the Minecraft **server process** (and therefore by the exaroton server instance when hosted there), not client/player RAM.

Prefer profiling or runtime measurement when practical; theoretical Big-O alone is not sufficient if a supposedly better algorithm performs more expensive Minecraft commands in practice.

## Current project-specific caution

- **Warehouse:** production data is sensitive. Registration, routing, compacting, overrides, names, refunds, migration state, and stored chest coordinates must be treated as existing user data.
- **Utilities:** preserve existing player toggles, statistics, waypoints/shared data used by the combined pack, and other persistent state across upgrades.
- **Copy/Paste:** it has not yet been installed on the `inno` production server as of this instruction, so production backward-compatibility constraints are currently less strict. Re-evaluate this once it is deployed.

When reviewing or implementing a risky change, explicitly state whether it changes persistent data, whether a migration is required, and what production-copy regression was performed.
