"""Build the Warehouse innotest live regression, reused from the earlier all-feature harness.

It runs on innotest with the four agent players of scripts/mineflayer26/agent.js online:
every feature is driven the way a player drives it (/trigger as the player, server-side
aim through tp, and real client actions - sneak, dig, use - requested from the agent
player). Results are judged from server state and printed as
    LIVE_CHECK PASS|FAIL <label>      ...      LIVE_RESULT PASS|FAIL pass=<n> fail=<n>

Players A (SunnyChen) and B (penguin0531) are used; their inventories, positions,
game modes, the waypoint storage, the Warehouse registration/name/rule storage and
keep_inventory are saved before the run and restored at the end (function
livetest:restore, also safe to run again by hand; a player who is offline is restored
the next time it runs). The test area is an empty sky box near the innotest spawn.

    /function livetest:start        (run from the console)
"""
from pathlib import Path
import json
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist/warehouse-live-test"
F = OUT / "data/livetest/function"
for old in F.rglob("*.mcfunction") if F.exists() else []:
    old.unlink()
F.mkdir(parents=True, exist_ok=True)
(OUT / "pack.mcmeta").write_text(json.dumps(
    {"pack": {"description": "Opt-in Warehouse innotest live regression", "min_format": 121, "max_format": 121}},
    ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

A, B = "penguin0531", "geena0701"
SA, SB = f"@a[name={A},limit=1]", f"@a[name={B},limit=1]"
OW = "in minecraft:overworld"
# Test area: empty sky box near the innotest spawn (-279, 253, 90).
X0, X1, Y0, Y1, Z0, Z1 = -440, -340, 279, 300, 140, 240
FLOOR = 279
O = (-400, 280, 160)                     # where the players wait between tests
INV_A = [(-430, 280, 145), (-429, 280, 145)]
INV_B = [(-427, 280, 145), (-426, 280, 145)]
DIMENSIONS = ("overworld", "the_nether", "the_end")
GAMEMODES = ("survival", "creative", "adventure", "spectator")

steps = []            # each: {"cmds": [...], "wait": None | (condition, label, max_ticks), "gap": ticks}
labels = []
marks = {}            # section name -> index of its first step


def section(name):
    marks[name] = len(steps)
_ack = [0]


def step(*cmds, gap=2):
    steps.append({"cmds": list(cmds), "wait": None, "gap": gap})


def wait(cond, label, max_ticks=200):
    """Hold the chain until `execute <cond>` passes; a timeout is a failed check."""
    labels.append("wait " + label)
    steps.append({"cmds": [], "wait": (cond, label, max_ticks), "gap": 1})


def check(label, *conds):
    labels.append(label)
    c = " ".join(conds)
    step("scoreboard players set #ok live 0",
         f"execute {c} run scoreboard players set #ok live 1",
         f"execute if score #ok live matches 1 run say LIVE_CHECK PASS {label}",
         f"execute unless score #ok live matches 1 run say LIVE_CHECK FAIL {label}",
         "execute if score #ok live matches 1 run scoreboard players add #pass live 1",
         "execute unless score #ok live matches 1 run scoreboard players add #fail live 1", gap=1)


def act(player, action, *args, label=None):
    """Ask the common Mineflayer driver to perform a client-side action."""
    _ack[0] += 1
    i = _ack[0]
    name = player
    mapped = {"sneak_on": ("sneak", 1), "sneak_off": ("sneak", 0)}
    if action in mapped:
        action, only = mapped[action]
        args = (only,)
    text = " ".join(["MFBOT", name, str(i), action, *map(str, args)])
    step(f"scoreboard players enable @a[name={name},limit=1] mfack",
         f"scoreboard players set @a[name={name},limit=1] mfack 0",
         f'tellraw @a[name={name},limit=1] "{text}"', gap=1)
    wait(f"if score @a[name={name},limit=1] mfack matches {i}",
         label or f"{name} {action} {' '.join(map(str, args))}", 1200)


def trig(player, name, value=None):
    step(f"execute as @a[name={player},limit=1] run trigger {name}" + (f" set {value}" if value is not None else ""), gap=3)


def tp(player, x, y, z, *facing):
    """Teleport; with a facing point, aim the (standing) eyes at it using absolute yaw/pitch."""
    rot = ""
    if facing:
        fx, fy, fz = facing
        dx, dy, dz = fx - x, fy - (y + 1.62), fz - z
        yaw = -math.degrees(math.atan2(dx, dz))
        pitch = -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
        rot = f" {yaw:.3f} {pitch:.3f}"
    step(f"execute {OW} run tp @a[name={player},limit=1] {x} {y} {z}{rot}", gap=2)


def at(player, x, y, z, r=0.3):
    return f"{OW} positioned {x} {y} {z} if entity @a[name={player},distance=..{r}]"


def blk(x, y, z, b):
    return f"{OW} if block {x} {y} {z} {b}"


# ---------------------------------------------------------------- setup
step(
    "scoreboard objectives add live dummy",
    "scoreboard objectives add mfack trigger",
    "scoreboard players set #pass live 0",
    "scoreboard players set #fail live 0",
    f"execute {OW} run forceload add {X0} {Z0} {X1} {Z1}",
    gap=40)
# start from an empty test area whatever an earlier (possibly interrupted) run left behind
step("function livetest:clear_area", f"execute {OW} run forceload add {X0} {Z0} {X1} {Z1}", gap=20)
step(
    # back up exactly what the run changes (restore is function livetest:restore)
    "data remove storage livetest:backup state",
    f"execute store result storage livetest:backup ids.a int 1 run scoreboard players get {SA} sunny_id",
    f"execute store result storage livetest:backup ids.b int 1 run scoreboard players get {SB} sunny_id",
    "function livetest:backup with storage livetest:backup ids",
    # where A and B stood (dimension too) and their game mode, to put them back at the end
    "data remove storage livetest:backup home",
    "data remove storage livetest:backup restored",
    *[f"execute store result storage livetest:backup home.{k}.{a} double 0.001 run data get entity @a[name={n},limit=1] Pos[{i}] 1000"
      for k, n in (("a", A), ("b", B)) for i, a in enumerate("xyz")],
    *[f'execute in minecraft:{d} if entity @a[name={n},distance=0..] run data modify storage livetest:backup home.{k}.dim set value "minecraft:{d}"'
      for k, n in (("a", A), ("b", B)) for d in DIMENSIONS],
    *[f'execute if entity @a[name={n},gamemode={m}] run data modify storage livetest:backup home.{k}.mode set value "{m}"'
      for k, n in (("a", A), ("b", B)) for m in GAMEMODES],
    "execute store result score #keepinv live run gamerule keep_inventory",
    "gamerule keep_inventory true",
    f"execute {OW} run fill {X0} {FLOOR} {Z0} {X1} {FLOOR} {Z1} minecraft:glass",
    *[f"execute {OW} run setblock {x} {y} {z} minecraft:chest" for x, y, z in INV_A + INV_B],
    gap=4)
for who, chests in ((A, INV_A), (B, INV_B)):
    sel = f"@a[name={who},limit=1]"
    (c1, c2) = chests
    cmds = [f"execute {OW} run item replace block {c1[0]} {c1[1]} {c1[2]} container.{n} from entity {sel} container.{n}" for n in range(27)]
    cmds += [f"execute {OW} run item replace block {c2[0]} {c2[1]} {c2[2]} container.{n - 27} from entity {sel} container.{n}" for n in range(27, 36)]
    for k, slot in enumerate(("armor.feet", "armor.legs", "armor.chest", "armor.head", "weapon.offhand")):
        cmds.append(f"execute {OW} run item replace block {c2[0]} {c2[1]} {c2[2]} container.{9 + k} from entity {sel} {slot}")
    # levitation keeps the server from kicking a player that is held in the air to aim
    cmds += [f"clear {sel}", f"gamemode survival {sel}", f"effect give {sel} minecraft:resistance infinite 255 true",
             f"effect give {sel} minecraft:levitation infinite 255 true",
             f"effect give {sel} minecraft:saturation infinite 255 true"]
    step(*cmds, gap=2)
step("data modify storage livetest:backup active set value 1b",
     f"execute {OW} run tp @a[name={A}] {O[0] + .5} {O[1]} {O[2] + .5}", f"execute {OW} run tp @a[name={B}] {O[0] + 2.5} {O[1]} {O[2] + .5}",
     "scoreboard players set @a[name=SunnyChen] su_tree 1", "scoreboard players set @a[name=SunnyChen] su_vein 1",
     "scoreboard players set @a[name=SunnyChen] su_plant 1", "say LIVE_SETUP_DONE", gap=20)
check("player A inventory saved and cleared", f"unless items entity {SA} container.* *")

# ================================================================ Utilities
section("utilities")
trig(A, "help")
check("help trigger handled", f"if score {SA} help matches 0")
for trg, obj in (("treecap", "su_tree"), ("veinmine", "su_vein"), ("replant", "su_plant"), ("coords", "c26_show")):
    step(f"scoreboard players operation #before live = {SA} {obj}", gap=1)
    trig(A, trg)
    check(f"{trg} toggles", f"unless score {SA} {obj} = #before live")
    trig(A, trg)
    check(f"{trg} toggles back", f"if score {SA} {obj} = #before live")

# fixed waypoints: set at P, go back to O, teleport home lands on P (block centre)
for k, (s, g) in enumerate((("sethome", "home"), ("setmine", "mine"), ("setvillage", "village"), ("setportal", "portal"), ("settemp", "temp"))):
    px, pz = -392 + 3 * k, 172
    tp(A, px + .5, 280, pz + .5)
    trig(A, s)
    tp(A, O[0] + .5, O[1], O[2] + .5)
    trig(A, g)
    check(f"{s} + {g} return to the saved spot", at(A, px + .5, 280, pz + .5, 1.0))
    check(f"{g} lands in the block centre", at(A, px + .5, 280, pz + .5, 0.05))
# back: return to where the last waypoint teleport started
tp(A, O[0] + .5, O[1], O[2] + 6.5)
trig(A, "home")
trig(A, "back")
check("back returns to the spot before the teleport", at(A, O[0] + .5, O[1], O[2] + 6.5, 1.0))
# personal waypoint: function API set (with name), trigger go, trigger overwrite
tp(A, -380.5, 280, 176.5)
step(f'execute as {SA} at @s run function nav:set_personal {{slot:1,name:"LiveP"}}', gap=3)
step(f"execute store result storage livetest:tmp id int 1 run scoreboard players get {SA} sunny_id",
     "function livetest:nav/p1_named with storage livetest:tmp", gap=1)
check("personal waypoint saved with its name", "if score #p1 live matches 1")
tp(A, O[0] + .5, O[1], O[2] + .5)
trig(A, "pgo", 1)
check("pgo goes to personal slot 1", at(A, -380.5, 280, 176.5, 1.0))
tp(A, -378.5, 280, 178.5)
trig(A, "pset", 1)
tp(A, O[0] + .5, O[1], O[2] + .5)
trig(A, "pgo", 1)
check("pset overwrites an existing personal slot", at(A, -378.5, 280, 178.5, 1.0))
trig(A, "plist")
check("plist handled", f"if score {SA} plist matches 0")
# shared waypoint: set by A, used by B
tp(A, -376.5, 280, 180.5)
step(f'execute as {SA} at @s run function nav:set_shared {{slot:8,name:"LiveS"}}', gap=3)
trig(B, "sgo", 8)
check("shared waypoint set by A takes B there", at(B, -376.5, 280, 180.5, 1.0))
trig(B, "slist")
check("slist handled", f"if score {SB} slist matches 0")
# death location
tp(B, -372.5, 280, 182.5)
step(f"kill {SB}", gap=20)
act(B, "respawn")          # a moment after dying, like a player clicking Respawn
wait(f"if entity @a[name={B},nbt=!{{Health:0.0f}}] {OW} positioned -372.5 280 182.5 unless entity @a[name={B},distance=..20]",
     "B respawned away from the death spot", 600)
step(f"effect give {SB} minecraft:levitation infinite 255 true", f"effect give {SB} minecraft:resistance infinite 255 true", gap=10)
trig(B, "deathloc")
check("deathloc returns to the death spot", at(B, -372.5, 280, 182.5, 1.5))
step(f"execute {OW} run tp @a[name={B}] {O[0] + 2.5} {O[1]} {O[2] + .5}", gap=2)

# tree felling: sneak + axe + break the bottom log of a leafy oak
TX, TZ = -366, 200
step(f"execute {OW} run fill {TX} 280 {TZ} {TX} 283 {TZ} minecraft:oak_log",
     f"execute {OW} run fill {TX - 1} 284 {TZ - 1} {TX + 1} 285 {TZ + 1} minecraft:oak_leaves",
     f"item replace entity {SA} weapon.mainhand with minecraft:diamond_axe", gap=5)
tp(A, TX + 2.5, 280, TZ + .5, TX + .5, 280.5, TZ + .5)
act(A, "sneak_on")
act(A, "dig", TX, 280, TZ)
step(gap=10)
act(A, "sneak_off")
check("tree felling chains the whole trunk", blk(TX, 280, TZ, "minecraft:air"), blk(TX, 281, TZ, "minecraft:air"), blk(TX, 283, TZ, "minecraft:air"))
check("tree felling drops the logs", f"{OW} positioned {TX} 281 {TZ} if entity @e[type=minecraft:item,distance=..4,nbt={{Item:{{id:\"minecraft:oak_log\"}}}}]")
# vein mining: sneak + pickaxe + break one ore of a vein
VX, VZ = -366, 206
step(f"execute {OW} run fill {VX} 280 {VZ} {VX} 282 {VZ} minecraft:diamond_ore",
     f"execute {OW} run kill @e[type=minecraft:experience_orb,x={VX},y=280,z={VZ},distance=..8]",
     f"item replace entity {SA} weapon.mainhand with minecraft:diamond_pickaxe", gap=5)
tp(A, VX + 2.5, 280, VZ + .5, VX + .5, 280.5, VZ + .5)
act(A, "sneak_on")
act(A, "dig", VX, 280, VZ)
step(gap=10)
act(A, "sneak_off")
check("vein mining chains the whole vein", blk(VX, 281, VZ, "minecraft:air"), blk(VX, 282, VZ, "minecraft:air"))
check("vein mining drops diamonds", f"{OW} positioned {VX} 281 {VZ} if entity @e[type=minecraft:item,distance=..4,nbt={{Item:{{id:\"minecraft:diamond\"}}}}]")
check("vein mining gives experience", f"{OW} positioned {VX} 281 {VZ} if entity @e[type=minecraft:experience_orb,distance=..5]")
# auto-replant: break ripe wheat on farmland
WX, WZ = -366, 212
step(f"execute {OW} run setblock {WX} 279 {WZ} minecraft:farmland",
     f"execute {OW} run setblock {WX} 280 {WZ} minecraft:wheat[age=7]",
     f"item replace entity {SA} weapon.mainhand with minecraft:air", gap=5)
tp(A, WX + 2.5, 280, WZ + .5, WX + .5, 280.2, WZ + .5)
act(A, "dig", WX, 280, WZ)
wait(blk(WX, 280, WZ, "minecraft:wheat[age=0]"), "wheat replanted", 100)
check("auto-replant plants the crop again", blk(WX, 280, WZ, "minecraft:wheat[age=0]"))
step(f"execute {OW} run kill @e[type=minecraft:item,x=-370,y=280,z=200,distance=..20]",
     f"execute {OW} run kill @e[type=minecraft:experience_orb,x=-370,y=280,z=200,distance=..20]", f"clear {SA}", gap=2)

# ================================================================ Warehouse
section("warehouse")
WH = "livetest:wh"
# sorting: an item put into the entry box ends up in the warehouse, nothing lost
wait(f"if function {WH}/entry_empty", "entry box empty before the sort test", 400)
step(f'function warehouse:api/count_item {{item_id:"minecraft:cobblestone"}}',
     "execute store result score #c0 live run data get storage warehouse:api result.available", gap=1)
step(f"function {WH}/entry_insert with storage warehouse:chests c00", gap=5)
wait(f"if function {WH}/entry_empty", "entry box sorted", 600)
step(f'function warehouse:api/count_item {{item_id:"minecraft:cobblestone"}}',
     "execute store result score #c1 live run data get storage warehouse:api result.available",
     "scoreboard players operation #c1 live -= #c0 live", gap=1)
check("sorting moves the entry box into the warehouse without loss", "if score #c1 live matches 40")
# search from a player
step(f'execute as {SA} run function warehouse:search/run {{q:"minecraft:cobblestone"}}', gap=3)
check("search finds the item and reports stock", 'if data storage warehouse:runtime search{item_id:"minecraft:cobblestone",stock:"有庫存"}')
# Pick: look at a block and take one stack
step(f"execute {OW} run setblock -380 280 190 minecraft:cobblestone",
     f'function warehouse:api/count_item {{item_id:"minecraft:cobblestone"}}',
     "execute store result score #c0 live run data get storage warehouse:api result.available", gap=2)
tp(A, -377.5, 280, 190.5, -379.5, 280.5, 190.5)
trig(A, "pick")
step(f"execute store result score #got live if items entity {SA} container.* minecraft:cobblestone",
     f'function warehouse:api/count_item {{item_id:"minecraft:cobblestone"}}',
     "execute store result score #c1 live run data get storage warehouse:api result.available",
     "scoreboard players operation #c0 live -= #c1 live", gap=1)
check("pick gives one stack of the looked-at block", "if score #got live matches 64")
check("pick takes exactly that stack from the warehouse", "if score #c0 live matches 64")
step(f"clear {SA} minecraft:cobblestone", f"function {WH}/entry_refund with storage warehouse:chests c00", gap=5)
# view a box and highlight it
trig(A, "wh_view", 31)
check("view lists a box's contents", f"if score {SA} wh_viewlines matches 1..", "if data storage warehouse:runtime viewer.lines[0]")
step("data modify storage warehouse:api request set value {code:31}",
     f"execute as {SA} store result score #hl live run function warehouse:api/highlight", gap=3)
check("highlight marks a registered box", "if score #hl live matches 1")
# classification rule change on an item without stock (no real stock moves), then remove it
step(f'execute as {SA} run function warehouse:search/run {{q:"minecraft:dragon_egg"}}', gap=3)
trig(A, "wh_search_pick", 458)
trig(A, "wh_rule_dest", 13)
check("changing a classification writes the player override", 'if data storage warehouse:rules {overrides:{"minecraft:dragon_egg":13}}')
trig(A, "wh_rule", 2)
check("removing the classification sets the item to no box", 'if data storage warehouse:rules {overrides:{"minecraft:dragon_egg":0}}')
# rename a box with a named item, then reset the name
step(f'item replace entity {SA} weapon.mainhand with minecraft:paper[minecraft:custom_name="LiveName"]', gap=2)
trig(A, "wh_rename_target", 31)
trig(A, "wh_rename", 1)
check("rename stores the custom box name", "if data storage warehouse:boxnames c31")
trig(A, "wh_rename", 2)
step(f"clear {SA}", gap=1)
# register a box through the player flow (select code, start, right-click the chest), then unregister it
RX, RY, RZ = -385, 280, 196
step(f"execute {OW} run setblock {RX} {RY} {RZ} minecraft:chest[facing=south,type=right]",
     f"execute {OW} run setblock {RX + 1} {RY} {RZ} minecraft:chest[facing=south,type=left]", gap=4)
trig(A, "wh_register", 13)
trig(A, "wh_action", 4)
tp(A, RX + .5, RY, RZ + 2.5, RX + .5, RY + .5, RZ + .5)
act(A, "use", RX, RY, RZ)
wait(f"if data storage warehouse:chests c13{{registered:1b,a_z:{RZ}}}", "c13 registered", 100)
check("registering a box by right-clicking it saves the chest", f"if data storage warehouse:chests c13{{registered:1b,valid:1b,a_y:{RY},a_z:{RZ}}}")
trig(A, "wh_unreg", 13)
trig(A, "wh_unreg_do", 1)
check("unregister clears the registration", "if data storage warehouse:chests c13{registered:0b}")
step("data modify storage warehouse:chests c13 set from storage livetest:backup state.c13", gap=2)

# ================================================================ Copy/Paste
section("copypaste")
# Source: a 3x3x3 build with a stair; its top-left corner is visible from above (Pos1) and the
# opposite bottom corner is the only block in its column (Pos2), so both are aimable from above.
SX, SY, SZ = -400, 281, 200
DX, DZ = -400, 215                 # target: the copy occupies DX..DX+2, 280..282, DZ..DZ+2
DY = FLOOR + 1
step(f"execute {OW} run fill {SX} {SY} {SZ} {SX + 2} {SY} {SZ + 2} minecraft:stone",
     f"execute {OW} run fill {SX} {SY + 1} {SZ} {SX + 1} {SY + 1} {SZ + 1} minecraft:cobblestone",
     f"execute {OW} run setblock {SX} {SY + 1} {SZ} minecraft:oak_stairs[facing=east]",
     f"execute {OW} run fill {SX} {SY + 2} {SZ} {SX + 1} {SY + 2} {SZ + 1} minecraft:glass",
     "scoreboard players set @a[name=SunnyChen] mcc_rot 0", "scoreboard players set @a[name=SunnyChen] mcc_mir 0", gap=4)
tp(A, SX + 2.5, SY + 6, SZ + 2.5, SX + 2.5, SY, SZ + 2.5)
trig(A, "pos1")
tp(A, SX + .5, SY + 6, SZ + .5, SX + .5, SY + 2, SZ + .5)
trig(A, "pos2")
check("pos1/pos2 from the crosshair", f"if score {SA} mcc_p1x matches {SX + 2}", f"if score {SA} mcc_p1y matches {SY}",
      f"if score {SA} mcc_p2x matches {SX}", f"if score {SA} mcc_p2y matches {SY + 2}")
trig(A, "c")
check("copy keeps the source untouched", blk(SX, SY + 1, SZ, "minecraft:oak_stairs[facing=east]"))
# blueprint at the target: aim at the floor below the target cell
tp(A, DX + 2.5, DY + 6, DZ + 2.5, DX + 2.5, FLOOR + .5, DZ + 2.5)
trig(A, "v")
step(gap=20)
check("V only previews (no real blocks)", blk(DX, DY, DZ, "minecraft:air"), blk(DX + 2, DY, DZ + 2, "minecraft:air"))
# the player carries everything except 4 of the 9 stone, which must come from the warehouse
step(f"item replace entity {SA} container.0 with minecraft:stone 5", f"item replace entity {SA} container.1 with minecraft:glass 4",
     f"item replace entity {SA} container.2 with minecraft:cobblestone 3", f"item replace entity {SA} container.3 with minecraft:oak_stairs 1",
     'function warehouse:api/count_item {item_id:"minecraft:stone"}',
     "execute store result score #st0 live run data get storage warehouse:api result.available", gap=2)
trig(A, "materials")
step(gap=10)
step(f"execute store result score #s live if items entity {SA} container.* minecraft:stone", gap=1)
check("materials check takes nothing", "if score #s live matches 5")
trig(A, "build")
wait(f"{OW} if blocks {SX} {SY} {SZ} {SX + 2} {SY + 2} {SZ + 2} {DX} {DY} {DZ} all", "build finished", 600)
check("build places the copy at the blueprint", f"{OW} if blocks {SX} {SY} {SZ} {SX + 2} {SY + 2} {SZ + 2} {DX} {DY} {DZ} all")
check("build used the player's stone first", f"unless items entity {SA} container.* minecraft:stone")
step('function warehouse:api/count_item {item_id:"minecraft:stone"}',
     "execute store result score #st1 live run data get storage warehouse:api result.available",
     "scoreboard players operation #st0 live -= #st1 live", gap=1)
check("build took only the missing 4 stone from the warehouse", "if score #st0 live matches 4")
trig(A, "undo")
step(gap=20)
check("undo removes the build", blk(DX, DY, DZ, "minecraft:air"), blk(DX, DY + 1, DZ, "minecraft:air"))
check("undo refunds the player's stone", f"if items entity {SA} container.* minecraft:stone")
trig(A, "redo")
wait(f"{OW} if blocks {SX} {SY} {SZ} {SX + 2} {SY + 2} {SZ + 2} {DX} {DY} {DZ} all", "redo finished", 600)
check("redo builds it again", f"{OW} if blocks {SX} {SY} {SZ} {SX + 2} {SY + 2} {SZ + 2} {DX} {DY} {DZ} all")
trig(A, "undo")
step(gap=20)
# direct edit of the source: move right by 3 (A faces south: right = west), undo
tp(A, SX + 1.5, SY + 6, SZ - 3.5, SX + 1.5, SY + 6, SZ + 10)
trig(A, "right", 3)
step(gap=20)
check("move shifts the real build", blk(SX - 3, SY + 1, SZ, "minecraft:oak_stairs[facing=east]"), blk(SX, SY + 1, SZ, "minecraft:air"))
trig(A, "undo")
step(gap=20)
check("undo restores the moved build", blk(SX, SY + 1, SZ, "minecraft:oak_stairs[facing=east]"), blk(SX - 3, SY + 1, SZ, "minecraft:air"))
# direct turn right (clockwise seen from above): the east-facing stair now faces south
trig(A, "turnright")
step(gap=20)
# clockwise about the anchor (SX+2, SZ+2): (dx, dz) -> (-dz, dx); the stair at (-2, -2) goes to (+2, -2)
check("turnright rotates the real build", blk(SX + 4, SY + 1, SZ, "minecraft:oak_stairs[facing=south]"), blk(SX, SY + 1, SZ, "minecraft:air"))
trig(A, "undo")
step(gap=20)
check("undo restores the rotated build", blk(SX, SY + 1, SZ, "minecraft:oak_stairs[facing=east]"))
# cut and paste
trig(A, "x")
step(gap=20)
check("cut removes the source", blk(SX, SY, SZ, "minecraft:air"), blk(SX, SY + 1, SZ, "minecraft:air"))
tp(A, DX + 2.5, DY + 6, DZ + 2.5, DX + 2.5, FLOOR + .5, DZ + 2.5)
trig(A, "v")
wait(blk(DX, DY + 1, DZ, "minecraft:oak_stairs[facing=east]"), "paste after cut finished", 600)
check("paste after cut places the build", blk(DX, DY + 1, DZ, "minecraft:oak_stairs[facing=east]"), blk(SX, SY, SZ, "minecraft:air"))
trig(A, "undo")
step(gap=30)
check("undo removes the pasted cut", blk(DX, DY + 1, DZ, "minecraft:air"))
trig(A, "undo")
step(gap=30)
check("undo of the cut puts the source back", blk(SX, SY + 1, SZ, "minecraft:oak_stairs[facing=east]"))
# material shortage: B has nothing and the warehouse has no target block -> nothing is built
step(f"execute {OW} run setblock {SX + 6} {SY} {SZ} minecraft:target",
     "scoreboard players set #sc live -1",
     'function warehouse:api/count_item {item_id:"minecraft:target"}',
     "execute store result score #sc live run data get storage warehouse:api result.available",
     f"scoreboard players set {SB} mcc_rot 0", f"scoreboard players set {SB} mcc_mir 0", gap=2)
check("shortage precondition: the warehouse has no target block", "if score #sc live matches 0")
tp(B, SX + 6.5, SY + 6, SZ + .5, SX + 6.5, SY, SZ + .5)
trig(B, "pos1")
trig(B, "pos2")
trig(B, "c")
tp(B, DX + 6.5, DY + 6, DZ + .5, DX + 6.5, FLOOR + .5, DZ + .5)
trig(B, "v")
step(gap=20)
trig(B, "build")
step(gap=30)
check("build without materials changes nothing", blk(DX + 6, DY, DZ, "minecraft:air"))
trig(B, "previewclear")

# ---------------------------------------------------------------- finish
section("finish")
step("function livetest:restore", gap=10)
check("player A inventory restored", f"unless items block {INV_A[0][0]} {INV_A[0][1]} {INV_A[0][2]} container.* *")
step(f'tellraw @a [{{"text":"LIVE DONE pass="}},{{"score":{{"name":"#pass","objective":"live"}}}},{{"text":" fail="}},{{"score":{{"name":"#fail","objective":"live"}}}}]',
     "execute if score #fail live matches 0 run say LIVE_RESULT PASS",
     "execute unless score #fail live matches 0 run say LIVE_RESULT FAIL", gap=1)

# ---------------------------------------------------------------- emit
def emit(prefix, chain):
    """Write one chain of step functions: livetest:<prefix>step_<i>, started by livetest:start<suffix>."""
    for i, s in enumerate(chain):
        # the controller sets #abort when it gives up, so a late step cannot undo its restore
        body = ["execute if score #abort live matches 1 run return 0"]
        if s["wait"]:
            cond, label, max_ticks = s["wait"]
            body += ["scoreboard players set #wok live 0",
                     f"execute {cond} run scoreboard players set #wok live 1",
                     "scoreboard players add #wait live 1",
                     f"execute if score #wok live matches 0 if score #wait live matches ..{max_ticks // 2} run return run schedule function livetest:{prefix}step_{i} 2t replace",
                     f"execute if score #wok live matches 0 run say LIVE_CHECK FAIL wait {label}",
                     "execute if score #wok live matches 0 run scoreboard players add #fail live 1",
                     "execute if score #wok live matches 1 run scoreboard players add #pass live 1",
                     "scoreboard players set #wait live 0"]
        body += s["cmds"]
        if i + 1 < len(chain):
            body.append(f"schedule function livetest:{prefix}step_{i + 1} {s['gap']}t replace")
        path = F / f"{prefix}step_{i}.mcfunction"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(body) + "\n", encoding="utf-8")
    name = "start" + ("_" + prefix.rstrip("/") if prefix else "")
    (F / f"{name}.mcfunction").write_text("\n".join([
        "scoreboard objectives add live dummy",
        # the previous run's inventories are still parked in the chests: setup would overwrite them
        "execute if data storage livetest:backup {active:1b} run return run say LIVE_RESULT FAIL previous run not restored; run function livetest:restore with both players online",
        "scoreboard players set #abort live 0",
        "scoreboard players set #wait live 0",
        f"function livetest:{prefix}step_0",
    ]) + "\n", encoding="utf-8")


setup = steps[:marks["utilities"]]
parts = {k: steps[marks[k]:marks[n]] for k, n in (("utilities", "warehouse"), ("warehouse", "copypaste"), ("copypaste", "finish"))}
finish = steps[marks["finish"]:]
emit("", setup + parts["utilities"] + parts["warehouse"] + parts["copypaste"] + finish)
for k, part in parts.items():          # one section alone: livetest:start_<section>
    emit(k + "/", setup + part + finish)
(F / "wh").mkdir(exist_ok=True)
(F / "wh/entry_insert.mcfunction").write_text("$item replace block $(a_x) $(a_y) $(a_z) container.13 with minecraft:cobblestone 40\n", encoding="utf-8")
# the sort test adds 40 and Pick takes 64: putting 24 back leaves the warehouse's cobblestone as it was
(F / "wh/entry_refund.mcfunction").write_text("$item replace block $(a_x) $(a_y) $(a_z) container.13 with minecraft:cobblestone 24\n", encoding="utf-8")
(F / "wh/entry_empty.mcfunction").write_text(
    "function livetest:wh/entry_count with storage warehouse:chests c00\nreturn run execute if score #entry live matches 0\n", encoding="utf-8")
(F / "wh/entry_count.mcfunction").write_text(
    "scoreboard players set #entry live 0\n"
    "$execute store result score #entry live if items block $(a_x) $(a_y) $(a_z) container.* *\n"
    "$execute store result score #entry_b live if items block $(b_x) $(b_y) $(b_z) container.* *\n"
    "scoreboard players operation #entry live += #entry_b live\n", encoding="utf-8")
(F / "nav").mkdir(exist_ok=True)
(F / "nav/p1_named.mcfunction").write_text(
    "scoreboard players set #p1 live 0\n"
    '$execute if data storage sunny_nav:players p$(id).custom.s1{name:{text:"LiveP"}} run scoreboard players set #p1 live 1\n'
    '$execute if data storage sunny_nav:players p$(id).custom.s1{name:"LiveP"} run scoreboard players set #p1 live 1\n', encoding="utf-8")
# (backup key, live storage, live path) for every value the run changes
SAVED = [("pa", "sunny_nav:players", "p$(a)"), ("pb", "sunny_nav:players", "p$(b)"), ("s8", "sunny_nav:shared", "s8"),
         ("c13", "warehouse:chests", "c13"), ("n31", "warehouse:boxnames", "c31"),
         ("egg", "warehouse:rules", 'overrides."minecraft:dragon_egg"')]
(F / "backup.mcfunction").write_text("".join(
    ("$" if "$(" in path else "") + f"execute if data storage {st} {path} run data modify storage livetest:backup state.{key} set from storage {st} {path}\n"
    for key, st, path in SAVED), encoding="utf-8")
(F / "restore_state.mcfunction").write_text("".join(
    ("$" if "$(" in path else "") + f"execute if data storage livetest:backup state.{key} run data modify storage {st} {path} set from storage livetest:backup state.{key}\n"
    + ("$" if "$(" in path else "") + f"execute unless data storage livetest:backup state.{key} run data remove storage {st} {path}\n"
    for key, st, path in SAVED), encoding="utf-8")
restore = [
    # only while a run is active: a second restore would copy the emptied chests back over the players
    "execute unless data storage livetest:backup {active:1b} run return 0",
    "execute unless data storage livetest:backup {restored:{world:1b}} run function livetest:restore_world",
    # a player is restored only while online; their chests are emptied only after that, so an
    # offline player's inventory stays parked and restore can simply be run again later
    *[f"execute unless data storage livetest:backup {{restored:{{{k}:1b}}}} as @a[name={n},limit=1] run function livetest:restore_{k}"
      for k, n in (("a", A), ("b", B))],
    "execute if data storage livetest:backup {restored:{world:1b,a:1b,b:1b}} run return run data modify storage livetest:backup active set value 0b",
    "say LIVE_RESTORE_PENDING a test player is offline; their inventory is still in the livetest chests. Run function livetest:restore again once they are online",
]
(F / "restore.mcfunction").write_text("\n".join(restore) + "\n", encoding="utf-8")
(F / "restore_world.mcfunction").write_text("\n".join([
    "function livetest:restore_state with storage livetest:backup ids",
    "execute if score #keepinv live matches 0 run gamerule keep_inventory false",
    f"execute {OW} run kill @e[type=!minecraft:player,x={X0},y={FLOOR},z={Z0},dx={X1 - X0},dy={Y1 - FLOOR},dz={Z1 - Z0}]",
    "data modify storage livetest:backup restored.world set value 1b",
]) + "\n", encoding="utf-8")
for k, chests in (("a", INV_A), ("b", INV_B)):
    c1, c2 = chests
    body = ["clear @s"]
    body += [f"execute {OW} run item replace entity @s container.{n} from block {c1[0]} {c1[1]} {c1[2]} container.{n}" for n in range(27)]
    body += [f"execute {OW} run item replace entity @s container.{n} from block {c2[0]} {c2[1]} {c2[2]} container.{n - 27}" for n in range(27, 36)]
    for j, slot in enumerate(("armor.feet", "armor.legs", "armor.chest", "armor.head", "weapon.offhand")):
        body.append(f"execute {OW} run item replace entity @s {slot} from block {c2[0]} {c2[1]} {c2[2]} container.{9 + j}")
    body += [f"execute {OW} run data modify block {c[0]} {c[1]} {c[2]} Items set value []" for c in chests]
    body += [f"effect clear @s minecraft:{e}" for e in ("resistance", "saturation", "levitation")]
    body += [f'execute if data storage livetest:backup home.{k}{{mode:"{m}"}} run gamemode {m} @s' for m in GAMEMODES]
    body += [f"function livetest:go_home with storage livetest:backup home.{k}",
             f"data modify storage livetest:backup restored.{k} set value 1b"]
    (F / f"restore_{k}.mcfunction").write_text("\n".join(body) + "\n", encoding="utf-8")
(F / "go_home.mcfunction").write_text("$execute in $(dim) run tp @s $(x) $(y) $(z)\n", encoding="utf-8")
# Clearing the area is separate so the controller can run it after restore; the inventory chests
# are emptied by restore first, so no item is lost.
(F / "clear_area.mcfunction").write_text("\n".join(
    # never while the players' inventories are still parked in the chests of this area
    ["execute if data storage livetest:backup {active:1b} run return run say LIVE_CLEAR_REFUSED restore first"] +
    # fill is limited to 32768 blocks per command: 101 x 22 x 10 slices
    [f"execute {OW} run fill {X0} {FLOOR} {Z0 + k * 10} {X1} {Y1} {min(Z0 + k * 10 + 9, Z1)} minecraft:air strict" for k in range((Z1 - Z0) // 10 + 1)]
    + [f"execute {OW} run forceload remove {X0} {Z0} {X1} {Z1}"]) + "\n", encoding="utf-8")
print(f"Built {len(steps)} live feature steps ({len(labels)} checks) at {OUT}")

(OUT / "suite.json").write_text(json.dumps({
    "ns": "livetest", "prefix": "LIVE",
    "players": {"a": A, "b": B}, "timeout_s": 1200,
    "start_function": "livetest:start_warehouse",
    "cleanup_function": "livetest:restore"
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
