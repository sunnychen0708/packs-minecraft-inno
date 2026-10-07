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

### Safety constraints

- Do not modify or experiment on the live `inno` world merely to test a change.
- Do not reset, rebuild, or migrate production data just because a clean-world test passes.
- Preserve existing persistent-data formats whenever an implementation-only refactor can achieve the same goal.
- Prefer implementation-path changes with no migration over schema changes for Warehouse and Utilities.
- If a change requires a migration, test both upgrade correctness and idempotency on the production-world copy.
- If there is uncertainty about whether a change can affect existing data, treat it as data-affecting and use the production-world-copy test path.

## Current project-specific caution

- **Warehouse:** production data is sensitive. Registration, routing, compacting, overrides, names, refunds, migration state, and stored chest coordinates must be treated as existing user data.
- **Utilities:** preserve existing player toggles, statistics, waypoints/shared data used by the combined pack, and other persistent state across upgrades.
- **Copy/Paste:** it has not yet been installed on the `inno` production server as of this instruction, so production backward-compatibility constraints are currently less strict. Re-evaluate this once it is deployed.

When reviewing or implementing a risky change, explicitly state whether it changes persistent data, whether a migration is required, and what production-copy regression was performed.
