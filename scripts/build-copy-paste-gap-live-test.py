#!/usr/bin/env python3
"""Isolated innotest-only Copy/Paste coverage shards using a full 5x4x5 stateful house.

Run only through exaroton innotest control, with real Mineflayer /trigger commands.
Each shard is independently cleaned up and limited to <240 seconds.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/real-client"))
import mcc_house as house
import xform
from innotest_harness import Suite

ap = argparse.ArgumentParser()
ap.add_argument("--case", choices=("external", "modes", "dimensions"), required=True)
CASE = ap.parse_args().case

OUT = ROOT / "dist" / "copy-paste-gap-live-test"
s = Suite("cpg", "CPG", {"a": "penguin0531"},
          "Opt-in 3D Copy/Paste innotest coverage " + CASE)
s.default_delay = 3
WHO = s.sel("a")
S = (-300, 250, 88)
T = (-286, 250, 88)
DIMS = ("the_nether", "the_end")
CELLS = {(x, y, z): state for x, y, z, state in house.BLOCKS}
SIZE = house.SIZE
EMPTY = "minecraft:air"

def run_dim(dim: str, cmd: str) -> str:
    return "execute in minecraft:" + dim + " run " + cmd

def state_conditions(dim: str, origin: tuple[int, int, int],
                     transform=None, anchor=None, exceptions=None):
    exceptions = exceptions or {}
    cmds = []
    for y in range(SIZE[1]):
        for x in range(SIZE[0]):
            for z in range(SIZE[2]):
                state = CELLS.get((x, y, z), EMPTY)
                wx, wy, wz = origin[0] + x, origin[1] + y, origin[2] + z
                if transform == "rotate":
                    assert anchor
                    wx, wz = anchor[0] - (wz - anchor[2]), anchor[2] + (wx - anchor[0])
                    state = xform.rotate_state(state, 1)
                elif transform == "mirror":
                    assert anchor
                    wx = 2 * anchor[0] - wx
                    state = xform.mirror_state(state, "x")
                state = exceptions.get((wx, wy, wz), state)
                cmds.append((f"in minecraft:{dim} if block {wx} {wy} {wz} {state}",
                             f"mismatch {dim} {wx} {wy} {wz} expected {state}"))
    return cmds

def source_select(dim: str, origin: tuple[int, int, int]):
    x, y, z = origin
    s.tp("a", x + .5, y - 4, z + .5, 0, -90, dim)
    s.trigger("a", "pos1")
    s.tp("a", x + SIZE[0] - .5, y + SIZE[1] + 4, z + SIZE[2] - .5, 0, 90, dim)
    s.trigger("a", "pos2")
    s.check("selection corners " + dim,
            f"score {WHO} mcc_p1x matches {x}",
            f"score {WHO} mcc_p1y matches {y}",
            f"score {WHO} mcc_p1z matches {z}",
            f"score {WHO} mcc_p2x matches {x + SIZE[0] - 1}",
            f"score {WHO} mcc_p2y matches {y + SIZE[1] - 1}",
            f"score {WHO} mcc_p2z matches {z + SIZE[2] - 1}")

def prepare(dim: str, source: tuple[int, int, int], target: tuple[int, int, int]):
    x, y, z = source
    tx, ty, tz = target
    # The dedicated high-altitude test region is not used for player buildings.
    s.tp("a", x + .5, y + 7, z + .5, 0, 90, dim)
    s.step(run_dim(dim, f"fill {x-4} {y-4} {z-15} {x+34} {y+10} {z+19} air"))
    s.step(*house.place_commands(x, y, z, dim))
    s.step(run_dim(dim, f"fill {tx} {ty-1} {tz} {tx+SIZE[0]-1} {ty-1} {tz+SIZE[2]-1} stone"))
    s.check("3D fixture exact " + dim, *state_conditions(dim, source))

# Restore test bot's original location, direction and dimension (int block precision).
s.step(
    f"execute store result storage cpg:save a.x int 1 run data get entity {WHO} Pos[0] 1",
    f"execute store result storage cpg:save a.y int 1 run data get entity {WHO} Pos[1] 1",
    f"execute store result storage cpg:save a.z int 1 run data get entity {WHO} Pos[2] 1",
    f"execute store result storage cpg:save a.yaw int 1 run data get entity {WHO} Rotation[0] 1",
    f"execute store result storage cpg:save a.pitch int 1 run data get entity {WHO} Rotation[1] 1",
    f"data modify storage cpg:save a.dim set from entity {WHO} Dimension")
s.step(f"execute as {WHO} run trigger previewclear")
s.step(f"scoreboard players set {WHO} mcc_mask 0",
       f"scoreboard players set {WHO} mcc_hasa 0",
       f"scoreboard players set {WHO} mcc_rot 0",
       f"scoreboard players set {WHO} mcc_mir 0")

if CASE == "external":
    dim = "overworld"
    anchor = (S[0] + 12, S[1], S[2])
    prepare(dim, S, T)
    source_select(dim, S)
    s.step(f"scoreboard players set {WHO} mcc_hasa 1",
           f"scoreboard players set {WHO} mcc_anx {anchor[0]}",
           f"scoreboard players set {WHO} mcc_any {anchor[1]}",
           f"scoreboard players set {WHO} mcc_anz {anchor[2]}",
           f"scoreboard players set {WHO} mcc_and 1")
    s.trigger("a", "turnright")
    s.check("external anchor rotate full 3D states",
            *state_conditions(dim, S, "rotate", anchor))
    s.check("rotate emptied source", *state_conditions(dim, S, exceptions={
        (S[0] + x, S[1] + y, S[2] + z): EMPTY
        for y in range(SIZE[1]) for x in range(SIZE[0]) for z in range(SIZE[2])}))
    s.trigger("a", "undo")
    s.check("external rotate undo exact", *state_conditions(dim, S))
    s.trigger("a", "flip")
    s.check("external anchor mirror full 3D states",
            *state_conditions(dim, S, "mirror", anchor))
    s.trigger("a", "undo")
    s.check("external mirror undo exact", *state_conditions(dim, S))

elif CASE == "modes":
    dim = "overworld"
    ix = (T[0]+2, T[1]+1, T[2]+1)  # Air inside house
    nonair = (T[0]+2, T[1], T[2]+1)
    for masked in (False, True):
        prepare(dim, S, T)
        source_select(dim, S)
        s.trigger("a", "x")
        s.check("cut removed 3D house", *state_conditions(dim, S, exceptions={
            (S[0]+x, S[1]+y, S[2]+z): EMPTY
            for y in range(SIZE[1]) for x in range(SIZE[0]) for z in range(SIZE[2])}))
        s.step(run_dim(dim, f"setblock {ix[0]} {ix[1]} {ix[2]} stone"),
               run_dim(dim, f"setblock {nonair[0]} {nonair[1]} {nonair[2]} stone"),
               f"scoreboard players set {WHO} mcc_mask {1 if masked else 0}")
        s.tp("a", T[0]+.5, T[1]+5, T[2]+.5, 0, 90, dim)
        s.trigger("a", "v")
        exceptions = {ix: "minecraft:stone"} if masked else {}
        s.check(("masked" if masked else "replace") + " overwrites solid and handles air correctly",
                *state_conditions(dim, T, exceptions=exceptions))
        s.trigger("a", "undo")
        s.trigger("a", "undo")
        s.step(f"scoreboard players set {WHO} mcc_mask 0")

elif CASE == "dimensions":
    for dim in DIMS:
        src = (S[0], 220, S[2])
        dst = (T[0], 220, T[2])
        prepare(dim, src, dst)
        source_select(dim, src)
        s.trigger("a", "c")
        s.tp("a", dst[0]+.5, dst[1]+5, dst[2]+.5, 0, 90, dim)
        s.trigger("a", "v")
        s.wait("blueprint settles " + dim,
               [f"score {WHO} mcc_bpready matches 1",
                f"score {WHO} mcc_bpscan matches 0"], tries=200)
        s.check("copy shows entire 3D blueprint " + dim, *[
            (f"in minecraft:{dim} positioned {dst[0]+x}.0 {dst[1]+y}.0 {dst[2]+z}.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.01]",
             f"missing preview {dim} {x} {y} {z}")
            for x, y, z, _ in house.BLOCKS])
        s.trigger("a", "previewclear")
        s.trigger("a", "x")
        s.tp("a", dst[0]+.5, dst[1]+5, dst[2]+.5, 0, 90, dim)
        s.trigger("a", "v")
        s.check("cut paste whole 3D house " + dim, *state_conditions(dim, dst))
        s.check("cut source empty " + dim, *state_conditions(dim, src, exceptions={
            (src[0]+x, src[1]+y, src[2]+z): EMPTY
            for y in range(SIZE[1]) for x in range(SIZE[0]) for z in range(SIZE[2])}))
        s.trigger("a", "undo")
        s.trigger("a", "undo")
        s.check("dimension undo restores source " + dim, *state_conditions(dim, src))

# Independently remove temporary buildings in all worlds; never touch inno.
worlds = ("overworld",) if CASE != "dimensions" else DIMS
for dim in worlds:
    y = 250 if dim == "overworld" else 220
    s.cleanup(run_dim(dim, f"fill -305 {y-1} 71 -265 {y+6} 111 air"))
s.cleanup("execute if data storage cpg:save a run function cpg:restore with storage cpg:save a",
          "data remove storage cpg:save a",
          f"scoreboard players set {WHO} mcc_mask 0",
          f"scoreboard players set {WHO} mcc_hasa 0")
steps = s.write(OUT)
s.extra_function(OUT, "restore", [
    "$execute in $(dim) run tp @a[name=penguin0531,limit=1] $(x) $(y) $(z) $(yaw) $(pitch)"
])
(OUT / "suite.json").write_text(json.dumps({
    "ns":"cpg", "prefix":"CPG", "players":{"a":"penguin0531"},
    "start_function":"cpg:start", "cleanup_function":"cpg:cleanup",
    "timeout_s":210
},indent=2) + "\n",encoding="utf-8")
print(f"Built {CASE} gap shard with {steps} steps")
