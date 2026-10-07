# exaroton operations and live multiplayer testing

Last updated: **2026-10-07**

This document describes the operational tooling for the two exaroton servers used by this repository.

## Server roles

| Server | Role | Normal policy |
| --- | --- | --- |
| `inno.exaroton.me` | Production world | Do not start it from repository automation. Normal inspection is read-only. The separate offline UUID maintenance workflow is an owner-authorized exception and requires the server to remain OFFLINE before any write. |
| `innotest.exaroton.me` | Test server | May be started/stopped, have datapacks deployed, run commands, and run automated multiplayer regressions. |

The API token is stored only as the GitHub Actions secret `EXAROTON_API_TOKEN`. Never put the token, a replacement token, or any other credential in the repository or an ops request file.

## Request files

The repository keeps operational requests in `ops/` so an action is explicit and auditable.

| File | Workflow | Purpose |
| --- | --- | --- |
| `ops/exaroton-request.json` | `exaroton-innotest.yml` | innotest status/log/start/stop/commands/deploy/live regression and controlled identity operations |
| `ops/mineflayer-request.json` | `mineflayer-innotest.yml` | one-player probe or four-player Mineflayer session on innotest |
| `ops/inno-maintenance-request.json` | `exaroton-inno-maintenance.yml` | owner-authorized production UUID maintenance while inno is OFFLINE |

The checked-in baseline for all request files should be `noop`. Change the request only when intentionally triggering an operation, then return it to `noop` after the operation is complete.

## Current innotest identity model

`innotest` currently runs with `online-mode=false` so four test clients can log in without Microsoft authorization. The four allowed bot identities are:

- `SunnyChen`
- `penguin0531`
- `geena0701`
- `Felicitypeng`

Minecraft offline UUIDs are computed from `OfflinePlayer:<name>` using the standard version-3 UUID algorithm.

The important migration direction is:

**production inno online-mode UUID data -> innotest offline-mode UUID data**

Do not use an old offline UUID from production as the source identity for innotest.

For Minecraft Java 26.3, per-player files are under:

```text
world/players/data/<uuid>.dat
world/players/data/<uuid>.dat_old
world/players/advancements/<uuid>.json
world/players/stats/<uuid>.json
```

The older `world/playerdata`, `world/advancements`, and `world/stats` layout is not the correct 26.3 layout for this server.

The `migrate-inno-online-to-innotest-offline` operation reads the production online UUID identities, copies the matching 26.3 player files to the target offline UUID names on innotest, preserves pre-existing target data as timestamped backups when needed, updates whitelist/ops identity UUIDs, and verifies written file content with SHA-256. Production is the source; innotest is the destination.

## Mineflayer 26.3 test clients

The Mineflayer stack is bootstrapped by `scripts/mineflayer26/bootstrap.py` and is pinned to the 26.3 protocol work used by this repository.

`keepalive.js` is intentionally conservative:

- target is hard-locked to `innotest.exaroton.me`;
- only the four names above are accepted;
- four-player logins are serialized instead of opening all clients at once;
- autonomous physics is disabled;
- client-originated movement packets are suppressed for idle test clients while teleport confirmations, keepalive traffic, chat, and other required protocol traffic continue normally.

The movement suppression exists because the current patched 26.3 Mineflayer stack can emit an invalid movement packet after a server-side teleport. These clients are reliable for presence, `/trigger`-driven datapack state, and server-side multiplayer regression, but they should not be treated as a general-purpose walking client until upstream 26.3 movement support is complete.

## Live Copy/Paste multiplayer regression

The live multiplayer regression is built by:

```text
scripts/build-copy-paste-multiplayer-test.py
```

The innotest controller operation is:

```text
run-copy-paste-multiplayer-test
```

The controller:

1. requires innotest to be ONLINE;
2. deploys the exact checked-out `utilities`, `warehouse`, and `copy-paste` sources;
3. builds and installs a temporary `mcc-multiplayer-test.zip`;
4. waits until at least four players are online;
5. uses `SunnyChen` as player A and `penguin0531` as player B while the other two clients remain online;
6. runs same-tick multiplayer checks;
7. waits for the current run's unique marker and `MCCMP_RESULT` instead of relying on a fixed sleep;
8. removes the test area, tags, scoreboard objective, temporary harness ZIP, and reloads after completion.

The regression covers:

- independent `pos1` / `pos2` selections;
- independent Copy clipboards and unique `mcc_id`;
- simultaneous Blueprint creation and clearing;
- simultaneous Move;
- separate work/Undo/Redo lanes;
- simultaneous Undo and Redo;
- simultaneous direct Rotate and isolated Undo;
- simultaneous `x` Cut and paste;
- A-only Undo/Redo not modifying B;
- B independent Undo.

The final assertion sequence on 2026-10-07 produced `MCCMP_RESULT PASS` with every check above passing while four bot players were online, and the final four-bot hold completed the full five-minute session. The controller places a unique session marker before deployment/reload and rejects any current-session `/ERROR]:` line before accepting PASS. A fresh run on a newly started innotest session passed that gate on 2026-10-07 ([run 37561053135](https://github.com/sunnychen0708/packs-minecraft-inno/actions/runs/37561053135)): all 18 checks passed, `COPY_PASTE_MULTIPLAYER_LIVE_TEST=PASS`, zero `ERROR` lines in the session log, and the four clients held the full five minutes and disconnected normally. This is a clean-log live validation.

Keep only the controller's fixed file names (`utilities.zip`, `warehouse.zip`, `copy-paste.zip`) in innotest's `world/datapacks`. A second copy of the same pack under another name (for example `copy-paste-v1.5.zip`) is loaded alongside it and contaminates the run; that happened once and was cleaned up before the clean run.

## Recommended live-test sequence

For a multiplayer-sensitive Copy/Paste change:

1. Let normal GitHub validation finish first.
2. Start `innotest` only if it is currently OFFLINE.
3. Start a four-player Mineflayer request for 300000 ms.
4. Wait until the Mineflayer log shows `READY 4/4`.
5. Run `run-copy-paste-multiplayer-test` through the innotest controller.
6. Require `COPY_PASTE_MULTIPLAYER_LIVE_TEST=PASS` / `MCCMP_RESULT PASS`.
7. Let the temporary harness clean itself up.
8. Stop `innotest` when testing is finished.
9. Verify a final read-only status of `OFFLINE` and `0/10`.
10. Return all three ops request files to `noop`.

The 2026-10-07 clean run left `innotest` ONLINE with `0/10` players at the owner's request (frequent start/stop costs more credits than idling); stop it when it is no longer needed.

## Production UUID maintenance

Production maintenance is intentionally separate from normal innotest control:

```text
.github/workflows/exaroton-inno-maintenance.yml
scripts/exaroton_inno_uuid_migrate.py
ops/inno-maintenance-request.json
```

Supported request operations are:

```text
noop
uuid-migrate-dry-run
uuid-migrate-apply
```

The production maintenance path is owner-authorized, but it is still constrained to offline UUID maintenance. It must verify that `inno` is OFFLINE and must never start the production server as part of the operation. Run `dry-run` before `apply` whenever the source world or identity set has changed.

## Operational cleanup rules

- Never leave a temporary multiplayer harness installed after a test.
- Never leave a request JSON pointing at the last destructive/state-changing operation; reset it to `noop`.
- Do not claim a live multiplayer pass from the static/runtime CI jobs alone.
- Do not claim a real Windows client pass from the Mineflayer live test; they cover different layers.
- If a live test fails, first distinguish test infrastructure failure (parser error, bot disconnect, timeout, stale log result) from an actual datapack assertion failure before changing datapack behavior.
