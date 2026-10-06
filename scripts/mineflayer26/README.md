# Mineflayer 26.3 test stack

Mineflayer's published npm release does not yet advertise Java 26.3 support. This directory pins the current upstream work needed for a real 26.3 client stack instead of keeping a private one-off patch in a temporary session.

Pinned pieces:

- `minecraft-data` 26.3 protocol/data branch: packet IDs/layouts, blocks/items/entities, player list, light masks.
- `node-minecraft-protocol`: the 26.3 scaffold plus `entityDelta` for stepped entity movement.
- `prismarine-chunk`: 26.3 byte-array light masks.
- `prismarine-physics`: 26.3 liquid-gravity feature mapping.
- `mineflayer`: combined 26.3 branch with teleport-confirm position/rotation, `tick_end`, stepped entity movement, and shifted player-action IDs.

The exact repositories and commit SHAs are in `stack.json`. `dist/` is gitignored, so third-party source and npm output never enter this repository.

## Build

Requirements: Git, Node.js 22+, npm, Python 3.

```bash
python scripts/mineflayer26/bootstrap.py
```

The bootstrap checks out the pinned sources under `dist/mineflayer-26.3-src`, points `node-minecraft-data` at the pinned 26.3 data commit, replaces the forks' `.yalc` development dependencies with sibling `file:` dependencies, installs production dependencies, then verifies protocol 777 and the expected 26.3 data counts.

Useful modes:

```bash
python scripts/mineflayer26/bootstrap.py --skip-install
python scripts/mineflayer26/bootstrap.py --verify-only
python scripts/mineflayer26/bootstrap.py --force
```

## Real connection smoke test

Run against an **offline-mode local test server**, not a production server. By default the script connects three bots (`BotTester`, `BotOp`, `BotOp2`) to `127.0.0.1:25565` and checks:

- all three reach Mineflayer `spawn` and stay connected long enough to exercise 26.3 teleport confirmation and per-tick `tick_end`;
- chunks parse and `blockAt` works (chunk/light stack);
- each bot's `bot.players` contains the other bots (26.3 player-list layout);
- one bot's movement is observed by another (stepped entity movement consumption);
- no Mineflayer error/kick/end occurs during the dwell period.

```bash
node scripts/mineflayer26/smoke.js
```

Configuration is by environment variable:

- `MF26_HOST`, `MF26_PORT`
- `MF26_BOTS=BotTester,BotOp,BotOp2`
- `MF26_DWELL_MS=7000`
- `MF26_STACK=<custom bootstrap destination>`
- `MF26_SMOKE_OUT=<result json>`

For an expendable local world where `BotTester` is OP, `MF26_MUTATION_TESTS=1` additionally creates a dirt fixture and digs it, then starts/stops using a bow and verifies the bow was not dropped. Those two checks directly exercise the shifted 26.3 player-action IDs. Do not enable them against a world you do not want modified.

The result is written to `dist/mineflayer-26.3-smoke.json` and the process exits non-zero on a required check failure.
