# Copy/Paste v0.2

Minecraft Java 26.3 data pack for selecting, copying, and pasting rectangular block regions without mods or plugins.

The actual pack source lives directly in this directory. Keep `pack.mcmeta` and `data/` here so Git can track individual changes.

## Release

Repository tag: `copy-paste-v0.2`

Release ZIP: `copy-paste-v0.2.zip`

## Commands

| Command | Action |
| --- | --- |
| `/trigger mcc_pos1` | Set the first corner from the block under the crosshair |
| `/trigger mcc_pos2` | Set the second corner from the block under the crosshair |
| `/trigger mcc_anchor` | Optionally set a custom anchor |
| `/trigger mcc_anchor set 2` | Clear the custom anchor and use Pos1 |
| `/trigger mcc_copy` | Save the selected region to the player's clipboard |
| `/trigger mcc_paste` | Paste with the anchor on the adjacent block face under the crosshair |
| `/trigger mcc_mode` | Toggle Replace / Masked paste mode |
| `/trigger mcc_help` | Show in-game help |

## Behavior

- Crosshair raycast range: 128 blocks.
- Pos1, Pos2, and Anchor use the block hit by the crosshair.
- Paste targets the adjacent block outside the hit face.
- Pos1 is used as the anchor when no custom Anchor is set.
- Replace mode includes air; Masked mode pastes only non-air blocks.
- Each player gets an independent clipboard snapshot.
- Supports copy/paste between the Overworld, Nether, and End.
- Maximum selection length is 128 blocks on each axis.
- Total volume must stay within `minecraft:max_block_modifications`.
- Clipboard data is stored in a reserved far-away Overworld area and temporarily force-loaded only during copy/paste operations.

## Version history

| Version | Changes |
| --- | --- |
| **0.1** | Initial copy/paste implementation. |
| **0.2** | Fix crosshair raycasts starting from the tick-function origin instead of the player; align hit positions to exact block coordinates, including negative coordinates. |

## Installation

Download `copy-paste-v0.2.zip`, place it in `<world>/datapacks/`, remove older Copy/Paste versions, then run `/reload` or reopen the world.
