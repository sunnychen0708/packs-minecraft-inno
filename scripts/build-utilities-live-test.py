"""Build the innotest live regression for every Utilities v3.8 feature.

Two Mineflayer bots act as real players through the test driver: they send
their own /trigger commands, dig blocks in survival and sneak.

Covered: help, coords toggle and action bar, the five fixed waypoints in all
three dimensions (set, teleport to the block centre, back), personal and
shared waypoints 1-8 (first set with a name, teleport, list, rename,
overwrite, invalid slot, two-player isolation), deathloc, tree felling for
every log type (and the not-sneaking, switched-off, no-leaves and 64-log
limits), vein mining for every ore (drops, vanilla XP, pickaxe tier gate,
silk touch, not sneaking, switched off) and auto replant for every crop.

Everything the test touches is backed up first and restored by
`function utest:cleanup`: both players' waypoint data, the shared
waypoints, feature switches, coords switch, game mode, main-hand item,
position/dimension and the keep_inventory game rule. Dropped items and
XP orbs from the test fixtures are counted and removed every tick, so the
players' inventories and XP do not change. Dying once for deathloc adds one
to the bot's death statistic on innotest.

Run on innotest with the `run-live-suite` controller operation (suite utilities).
"""
from pathlib import Path
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from innotest_harness import Suite

OUT = ROOT / 'dist/utilities-live-test'
# Default: the key cases only (about 4 minutes on innotest). --full runs every log type, every ore,
# every tier pair, every crop and all 8 waypoint slots (about 40 minutes).
FULL = '--full' in sys.argv
# --recheck: only the checks that have not passed on innotest yet; setup is kept.
RECHECK = '--recheck' in sys.argv
NS = 'utest'
PLAYERS = {'a': 'penguin0531', 'b': 'geena0701'}
s = Suite(NS, 'UTEST', PLAYERS, 'Opt-in Utilities v3.8 innotest live regression')
A, B = s.sel('a'), s.sel('b')
if not FULL:
    s.default_delay = 4
DIMS = {'overworld': 0, 'the_nether': 1, 'the_end': 2}

# ---- areas -------------------------------------------------------------
OW_AREA = (-416, 214, 384, -384, 236, 416)        # 33x23x33
TALL_AREA = (-388, 237, 402, -384, 292, 406)      # the 70-log tree
NE_AREA = (-64, 196, 56, -52, 206, 68)
END_AREA = (296, 196, 296, 304, 206, 304)
BACKUP_CHEST = (-416, 214, 384)                   # holds the main-hand item during the test
HUB = (-400, 220, 400)
HUBC = (HUB[0] + .5, HUB[1], HUB[2] + .5)


def fill(area, block, dim='overworld'):
    x1, y1, z1, x2, y2, z2 = area
    return f'execute in minecraft:{dim} run fill {x1} {y1} {z1} {x2} {y2} {z2} {block}'


def region(area):
    x1, y1, z1, x2, y2, z2 = area
    return f'x={x1},y={y1},z={z1},dx={x2-x1},dy={y2-y1},dz={z2-z1}'


def at_center(p, dim, x, y, z):
    return (f'in minecraft:{dim} positioned {x + .5} {y} {z + .5} if entity @a[name={PLAYERS[p]},distance=..0.01]',
            f'{PLAYERS[p]} not at the centre of {dim} {x} {y} {z}')


def look(bx, by, bz, fx, fy, fz):
    """yaw/pitch for eyes at (fx, fy+1.62, fz) looking at the centre of block (bx, by, bz)."""
    dx, dy, dz = bx + .5 - fx, by + .5 - (fy + 1.62), bz + .5 - fz
    yaw = math.degrees(math.atan2(-dx, dz))
    pitch = -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
    return round(yaw, 2), round(pitch, 2)


# ---- backup and restore -------------------------------------------------
backup = [
    # A run that was stopped before its cleanup left its backup: restore that first, never overwrite it.
    'execute if data storage utest:b all.backed run function utest:restore',
    'data remove storage utest:b all',
    'data modify storage utest:b all set value {fl:0b}',
    f'execute in minecraft:overworld store success storage utest:b all.fl byte 1 run forceload query {BACKUP_CHEST[0]} {BACKUP_CHEST[2]}',
    f'execute if data storage utest:b all{{fl:0b}} in minecraft:overworld run forceload add {BACKUP_CHEST[0]} {BACKUP_CHEST[2]}',
    'execute store result storage utest:b all.ki int 1 run gamerule minecraft:keep_inventory',
    'data modify storage utest:b all.shared set from storage sunny_nav:shared',
]
restore_players = []
verify = ['scoreboard players set #shareddiff htest 0', 'data modify storage utest:arg cmp set from storage sunny_nav:shared',
          'execute store success score #shareddiff htest run data modify storage utest:arg cmp set from storage utest:b all.shared']
for p in PLAYERS:
    sp = s.sel(p)
    backup += [
        f'execute store result storage utest:b all.{p}_id int 1 run scoreboard players get {sp} sunny_id',
        f'data modify storage utest:arg v set value {{key:"{p}"}}',
        f'data modify storage utest:arg v.id set from storage utest:b all.{p}_id',
        'function utest:nav_backup with storage utest:arg v',
        f'data modify storage utest:b all.{p}_pos set from entity {sp} Pos',
        f'data modify storage utest:b all.{p}_rot set from entity {sp} Rotation',
        f'data modify storage utest:b all.{p}_dim set from entity {sp} Dimension',
    ]
    backup.append(f'execute store result storage utest:b all.{p}_bbs double 0.001 run attribute {sp} minecraft:block_break_speed base get 1000')
    for obj in ('su_tree', 'su_vein', 'su_plant', 'c26_show'):
        backup.append(f'execute store result storage utest:b all.{p}_{obj} int 1 run scoreboard players get {sp} {obj}')
    for gm in ('survival', 'creative', 'adventure', 'spectator'):
        backup.append(f'execute if entity @a[name={PLAYERS[p]},gamemode={gm}] run data modify storage utest:b all.{p}_gm set value "{gm}"')
        online = f'execute if entity {sp}'
    restore_players += [
        f'data modify storage utest:arg v set value {{key:"{p}"}}',
        f'data modify storage utest:arg v.id set from storage utest:b all.{p}_id',
        'execute if data storage utest:b all.{0}_id run function utest:nav_restore with storage utest:arg v'.format(p),
        f'scoreboard players set #navdiff_{p} htest 0',
        'execute if data storage utest:b all.{0}_id run function utest:nav_verify with storage utest:arg v'.format(p),
        *[f'execute store result score #{p}_{obj} htest run data get storage utest:b all.{p}_{obj}'
          for obj in ('su_tree', 'su_vein', 'su_plant', 'c26_show')],
        # Scores can be set by name even while the player is offline.
        *[f'execute if data storage utest:b all.{p}_{obj} store result score {PLAYERS[p]} {obj} run data get storage utest:b all.{p}_{obj}'
          for obj in ('su_tree', 'su_vein', 'su_plant', 'c26_show')],
        # Game mode, attribute, main hand and position need the player online; until then the backup stays.
        f'execute unless entity {sp} run say UTEST_RESTORE waiting for {PLAYERS[p]} to come back online',
        *[f'{online} if data storage utest:b all{{{p}_gm:"{gm}"}} run gamemode {gm} {sp}'
          for gm in ('survival', 'creative', 'adventure', 'spectator')],
        f'{online} if data storage utest:b all.{p}_bbs run function utest:restore_bbs {{p:"{p}",name:"{PLAYERS[p]}"}}',
        *([f'{online} in minecraft:overworld if block {BACKUP_CHEST[0]} {BACKUP_CHEST[1]} {BACKUP_CHEST[2]} minecraft:chest run item replace entity {sp} weapon.mainhand from block {BACKUP_CHEST[0]} {BACKUP_CHEST[1]} {BACKUP_CHEST[2]} container.0'] if p == 'a' else []),
        f'{online} if data storage utest:b all.{p}_dim run function utest:return_player {{p:"{p}",name:"{PLAYERS[p]}"}}',
        f'{online} run data modify storage utest:b all.{p}_done set value 1b',
    ]
backup.append('data modify storage utest:b all.backed set value 1b')
restore = [
    'scoreboard players set #sniff htest 0',
    'schedule clear utest:sniff',
    'execute unless data storage utest:b all.backed run return run say UTEST_RESTORE nothing to restore',
    *restore_players,
    'execute if data storage utest:b all{ki:0} run gamerule minecraft:keep_inventory false',
    'execute if data storage utest:b all{ki:1} run gamerule minecraft:keep_inventory true',
    *[f'data remove storage sunny_nav:shared s{k}' for k in range(1, 9)],
    *[f'execute if data storage utest:b all.shared.s{k} run data modify storage sunny_nav:shared s{k} set from storage utest:b all.shared.s{k}' for k in range(1, 9)],
    *verify,
    # Keep the backup (and the chest holding A's main-hand item) until every player has been restored.
    *[f'execute unless data storage utest:b all.{p}_done run return run say UTEST_RESTORE partial: run function utest:restore again when {PLAYERS[p]} is online' for p in PLAYERS],
    fill(OW_AREA, 'air'), fill(TALL_AREA, 'air'), fill(NE_AREA, 'air', 'the_nether'), fill(END_AREA, 'air', 'the_end'),
    f'execute in minecraft:overworld run kill @e[type=minecraft:item,{region(OW_AREA)}]',
    f'execute in minecraft:overworld run kill @e[type=minecraft:experience_orb,{region(OW_AREA)}]',
    f'execute if data storage utest:b all{{fl:0b}} in minecraft:overworld run forceload remove {BACKUP_CHEST[0]} {BACKUP_CHEST[2]}',
    'data remove storage utest:b all',
    'data remove storage utest:arg v',
    'say UTEST_RESTORE done',
]
s.cleanup('function utest:restore')

# ---- item and XP counting ------------------------------------------------
LOGS = ['oak_log', 'spruce_log', 'birch_log', 'jungle_log', 'acacia_log', 'dark_oak_log', 'mangrove_log',
        'cherry_log', 'pale_oak_log', 'poplar_log', 'crimson_stem', 'warped_stem']
DROPS = ['coal', 'raw_iron', 'raw_copper', 'raw_gold', 'redstone', 'lapis_lazuli', 'diamond', 'emerald',
         'quartz', 'gold_nugget', 'ancient_debris', 'diamond_ore']
TRACKED = LOGS + DROPS
G = {item: f'#g{i} htest' for i, item in enumerate(TRACKED)}
sniff = [
    f'execute in minecraft:overworld as @e[type=minecraft:item,{region(OW_AREA)}] run function utest:eat_item',
    f'execute in minecraft:overworld as @e[type=minecraft:item,{region(TALL_AREA)}] run function utest:eat_item',
    f'execute in minecraft:overworld as @e[type=minecraft:experience_orb,{region(OW_AREA)}] run function utest:eat_orb',
    'execute if score #sniff htest matches 1 run schedule function utest:sniff 1t replace',
]
eat_item = ['execute store result score @s htest run data get entity @s Item.count']
eat_item += [f'execute if items entity @s contents minecraft:{item} run scoreboard players operation {G[item]} += @s htest' for item in TRACKED]
eat_item += ['kill @s']
eat_orb = ['execute store result score #v htest run data get entity @s Value',
           'execute store result score #c htest run data get entity @s Count',
           'execute if score #c htest matches ..0 run scoreboard players set #c htest 1',
           'scoreboard players operation #v htest *= #c htest',
           'scoreboard players operation #xp htest += #v htest',
           'kill @s']
reset_counts = [f'scoreboard players set {g} 0' for g in G.values()] + ['scoreboard players set #xp htest 0']

# ---- 0. bring bots into each area so the chunks are loaded, build fixtures ----
s.step('function utest:backup', delay=2)
s.tp('a', -57.5, 201, 61.5, dim='the_nether')
s.tp('b', 300.5, 201, 300.5, dim='the_end')
s.step('say UTEST loading nether/end areas', delay=60 if FULL else 30, realtime=True)
s.step(fill(NE_AREA, 'air', 'the_nether'), fill(END_AREA, 'air', 'the_end'))
s.tp('a', *HUBC)
s.tp('b', HUBC[0] + 2, HUBC[1], HUBC[2])
s.step('say UTEST loading overworld area', delay=60 if FULL else 30, realtime=True)
s.step(fill(OW_AREA, 'air'), fill(TALL_AREA, 'air'),
       f'execute in minecraft:overworld run setblock {BACKUP_CHEST[0]} {BACKUP_CHEST[1]} {BACKUP_CHEST[2]} minecraft:chest',
       f'execute in minecraft:overworld run item replace block {BACKUP_CHEST[0]} {BACKUP_CHEST[1]} {BACKUP_CHEST[2]} container.0 from entity {A} weapon.mainhand',
       f'execute in minecraft:overworld run setblock {HUB[0]} {HUB[1]-1} {HUB[2]} minecraft:stone',
       *[f'gamemode survival {s.sel(p)}' for p in PLAYERS],
       *[f'scoreboard players set {s.sel(p)} {obj} 1' for p in PLAYERS for obj in ('su_tree', 'su_vein', 'su_plant', 'c26_show')])
s.check('backup taken',
        'data storage utest:b all{backed:1b}',
        ('data storage utest:b all.a_dim', 'could not read player A dimension'),
        ('data storage utest:b all.b_dim', 'could not read player B dimension'))

# ---- 1. help and coords ---------------------------------------------------
MARK_PASSED_FROM = len(s.steps)
s.cmdx('a', ['功能總覽'], 'trigger help')
s.cmdx('a', ['[座標]', '已關閉'], 'trigger coords')
s.check('coords off only for A', f'score {A} c26_show matches 0', f'score {B} c26_show matches 1')
s.cmdx('a', ['[座標]', '已開啟'], 'trigger coords')
s.check('coords back on', f'score {A} c26_show matches 1')
s.cmdx('a', ['220', '400', '/'], 'trigger mfack', label='a sees coords action bar')

# ---- 2. fixed waypoints in three dimensions ---------------------------------
FIXED = [('home', '家', 'overworld', -410, 220, 390), ('mine', '礦坑', 'the_nether', -60, 200, 60),
         ('village', '村莊', 'the_end', 300, 200, 300), ('portal', '傳送門', 'the_nether', -56, 200, 64),
         ('temp', '臨時點', 'overworld', -410, 220, 410)]
walls = []
if not FULL:
    FIXED = FIXED[:3]   # one waypoint per dimension: home, mine (nether), village (end)
for name, label, dim, x, y, z in FIXED:
    # A 1x1 shaft: a teleport to the block corner would put the player inside the walls.
    walls += [f'execute in minecraft:{dim} run fill {x-1} {y-1} {z-1} {x+1} {y+2} {z+1} minecraft:stone',
              f'execute in minecraft:{dim} run fill {x} {y} {z} {x} {y+1} {z} minecraft:air']
s.step(*walls)
for name, label, dim, x, y, z in FIXED:
    s.tp('a', x + .2, y, z + .8, dim=dim)
    s.cmdx('a', ['已設定', label], f'trigger set{name}')
    s.tp('a', *HUBC)
    s.trigger('a', name)
    s.check(f'{name} teleports to block centre', at_center('a', dim, x, y, z))
    s.trigger('a', 'back')
    s.check(f'back after {name} returns to hub', at_center('a', 'overworld', *HUB))

# ---- 3. personal waypoints 1-8 -----------------------------------------------
PERSONAL = {k: (-414 + 3 * (k - 1), 220, 386) for k in (range(1, 9) if FULL else (1, 2, 3, 8))}
PB1 = (-414, 220, 392)
QP = (-386, 220, 386)
s.step(*[f'execute in minecraft:overworld run setblock {x} {y-1} {z} minecraft:stone' for x, y, z in [*PERSONAL.values(), PB1, QP]],
       *[f'function utest:nav_clear_custom {{key:"{p}"}}' for p in PLAYERS])


def wp_check(label, p, slot, name, pos, dim='overworld', shared=False):
    x, y, z = pos
    fn = 'utest:shared_is' if shared else 'utest:personal_is'
    s.step(f'data modify storage utest:arg v set value {{slot:{slot},name:"{name}",x:{x},y:{y},z:{z},dim:{DIMS[dim]}}}',
           f'data modify storage utest:arg v.id set from storage utest:b all.{p}_id',
           'scoreboard players set #r htest 0',
           f'function {fn} with storage utest:arg v', delay=1)
    s.check(label, ('score #r htest matches 1', f'{"shared" if shared else PLAYERS[p]} slot {slot} is not name={name} at {x} {y} {z}'))


for k, (x, y, z) in PERSONAL.items():
    s.tp('a', x + .2, y, z + .8)
    s.trigger('a', 'pset', k)                        # first set opens the name dialog; nothing saved yet
    s.cmdx('a', ['已設定個人據點', f'甲據點{k}'], f'function nav:set_personal {{slot:{k},name:"甲據點{k}"}}')
    wp_check(f'personal {k} saved with name and position', 'a', k, f'甲據點{k}', (x, y, z))
for k, (x, y, z) in PERSONAL.items():
    s.tp('a', *HUBC)
    s.trigger('a', 'pgo', k)
    s.check(f'personal {k} teleport', at_center('a', 'overworld', x, y, z))
s.trigger('a', 'back')
# Every pgo above started from the hub, so back returns there.
s.check('back after personal teleport', at_center('a', 'overworld', *HUB))
PL = list(PERSONAL)[-1]                              # rename and overwrite the last slot
s.cmdx('a', [f'甲據點{PL}'], 'trigger plist')
s.cmdx('a', ['改名二'], f'function nav:rename_personal {{slot:{PL},name:"改名二"}}')
wp_check('personal rename keeps position', 'a', PL, '改名二', PERSONAL[PL])
s.tp('a', QP[0] + .7, QP[1], QP[2] + .3)
s.trigger('a', 'pset', PL)                           # already set: overwrite position, keep name
wp_check('personal overwrite keeps name', 'a', PL, '改名二', QP)
s.cmdx('a', ['1～8'], 'trigger pset set 9')
s.tp('b', PB1[0] + .5, PB1[1], PB1[2] + .5)
s.trigger('b', 'pset', 1)
s.cmdx('b', ['乙據點1'], 'function nav:set_personal {slot:1,name:"乙據點1"}')
wp_check('B personal 1 saved', 'b', 1, '乙據點1', PB1)
wp_check('A personal 1 untouched by B', 'a', 1, '甲據點1', PERSONAL[1])
s.tp('a', *HUBC)
s.tp('b', HUBC[0] + 2, HUBC[1], HUBC[2])
s.trigger('a', 'pgo', 1)
s.trigger('b', 'pgo', 1)
s.check('personal waypoints are per player', at_center('a', 'overworld', *PERSONAL[1]), at_center('b', 'overworld', *PB1))

# ---- 4. shared waypoints 1-8 -------------------------------------------------
SHARED = {k: (-414 + 3 * (k - 1), 220, 414) for k in (range(1, 9) if FULL else (1, 4, 5, 8))}
QS = (-386, 220, 414)
s.step(*[f'execute in minecraft:overworld run setblock {x} {y-1} {z} minecraft:stone' for x, y, z in [*SHARED.values(), QS]],
       *[f'data remove storage sunny_nav:shared s{k}' for k in range(1, 9)])
for k, (x, y, z) in SHARED.items():
    s.tp('a', x + .2, y, z + .8)
    s.trigger('a', 'sset', k)
    s.cmdx('a', ['設定了共用據點', f'共用{k}'], f'function nav:set_shared {{slot:{k},name:"共用{k}"}}')
    wp_check(f'shared {k} saved', 'a', k, f'共用{k}', (x, y, z), shared=True)
for k, (x, y, z) in SHARED.items():
    s.tp('b', HUBC[0] + 2, HUBC[1], HUBC[2])
    s.trigger('b', 'sgo', k)
    s.check(f'B uses shared {k} set by A', at_center('b', 'overworld', x, y, z))
SL = list(SHARED)[-1]
s.cmdx('b', [f'共用{SL}'], 'trigger slist')
s.cmdx('b', ['共用改名'], f'function nav:rename_shared {{slot:{SL},name:"共用改名"}}')
wp_check('shared rename by B keeps position', 'b', SL, '共用改名', SHARED[SL], shared=True)
s.tp('b', QS[0] + .7, QS[1], QS[2] + .3)
s.trigger('b', 'sset', SL)
wp_check('shared overwrite keeps name', 'b', SL, '共用改名', QS, shared=True)
s.cmdx('b', ['1～8'], 'trigger sset set 9')

# ---- 5. deathloc ----------------------------------------------------------------
D = (-53, 200, 67)
s.step(f'execute in minecraft:the_nether run setblock {D[0]} {D[1]-1} {D[2]} minecraft:stone',
       'gamerule minecraft:keep_inventory true')
s.tp('a', D[0] + .3, D[1], D[2] + .7, dim='the_nether')
s.step(f'kill {A}', delay=40, realtime=True)
s.wait('A respawned', [f'entity @a[name={PLAYERS["a"]},nbt={{Health:20.0f}}]'], tries=120, realtime=True)
s.step('execute if data storage utest:b all{ki:0} run gamerule minecraft:keep_inventory false')
s.step(f'data modify storage utest:arg v set value {{x:{D[0]},y:{D[1]},z:{D[2]},dim:1}}',
       'data modify storage utest:arg v.id set from storage utest:b all.a_id',
       'scoreboard players set #r htest 0', 'function utest:death_is with storage utest:arg v', delay=1)
s.check('death location recorded', ('score #r htest matches 1', f'death not recorded at nether {D[0]} {D[1]} {D[2]}'))
s.tp('a', *HUBC)
s.trigger('a', 'deathloc')
s.check('deathloc returns to the death block centre', at_center('a', 'the_nether', *D))
s.tp('a', *HUBC)

# ---- 6. survival utilities: A holds tools and sneaks --------------------------
# The bot hangs in the air (no physics), so vanilla mines 5x slower; a higher block_break_speed
# keeps the slowest cases (wrong-tier ancient debris) short. Restored with the rest.
s.step(*reset_counts, 'scoreboard players set #sniff htest 1', 'function utest:sniff',
       f'attribute {A} minecraft:block_break_speed base set 20')
s.bot('a', 'sneak', 1)


def dig_case(label, setup, target, stand, tool, checks_fn, sneak=True, wait=None, tries=200):
    wait = (20 if FULL else 10) if wait is None else wait
    tx, ty, tz = target
    fx, fy, fz = stand
    yaw, pitch = look(tx, ty, tz, fx, fy, fz)
    s.step(*setup, f'item replace entity {A} weapon.mainhand with {tool}', *reset_counts)
    s.tp('a', fx, fy, fz, yaw, pitch)
    if not sneak:
        s.bot('a', 'sneak', 0)
    s.bot('a', 'dig', tx, ty, tz, tries=tries, label=f'a digs {label}')
    s.step(f'say UTEST settle {label.replace(" ", "_")}', delay=wait)
    s.check(label, *checks_fn())
    if not sneak:
        s.bot('a', 'sneak', 1)


def cnt(item, lo, hi=None):
    hi = lo if hi is None else hi
    return (f'score {G[item]} matches {lo}..{hi}', f'{item} dropped is not {lo}..{hi}')


def blocks_are(block, cells, dim='overworld'):
    return [(f'in minecraft:{dim} if block {x} {y} {z} {block}', f'{x} {y} {z} is not {block}') for x, y, z in cells]


LEAVES = {'oak_log': 'oak_leaves', 'spruce_log': 'spruce_leaves', 'birch_log': 'birch_leaves',
          'jungle_log': 'jungle_leaves', 'acacia_log': 'acacia_leaves', 'dark_oak_log': 'dark_oak_leaves',
          'mangrove_log': 'mangrove_leaves', 'cherry_log': 'cherry_leaves', 'pale_oak_log': 'pale_oak_leaves',
          'crimson_stem': 'nether_wart_block', 'warped_stem': 'warped_wart_block'}
TREES = [(log, LEAVES[log]) for log in LOGS if log != 'poplar_log']
TREES += [('poplar_log', f'{c}_poplar_leaves') for c in ('red', 'orange', 'yellow')]
if not FULL:
    # One normal tree, the 26.3 poplar and a nether stem with wart-block foliage.
    TREES = [('oak_log', 'oak_leaves')]


def tree_cmds(x, z, log, leaves, height=4, leaf_y=None):
    y0 = 220
    leaf_y = y0 + height - 2 if leaf_y is None else leaf_y
    leaf_state = f'minecraft:{leaves}' + ('[persistent=true]' if leaves.endswith('_leaves') else '')
    cmds = [f'execute in minecraft:overworld run setblock {x} {y0-1} {z} minecraft:dirt']
    if leaves:
        cmds.append(f'execute in minecraft:overworld run fill {x-1} {leaf_y} {z-1} {x+1} {leaf_y+1} {z+1} {leaf_state}')
    cmds.append(f'execute in minecraft:overworld run fill {x} {y0} {z} {x} {y0+height-1} {z} minecraft:{log}')
    return cmds


def tree_case(label, x, z, log, leaves, chained=True, sneak=True, height=4, cap=None):
    def checks():
        top = 220 + height - 1
        if cap:
            gone = [(x, y, z) for y in range(221, 221 + cap)]
            left = [(x, y, z) for y in range(221 + cap, top + 1)]
            return [*blocks_are('minecraft:air', gone), *blocks_are(f'minecraft:{log}', left), cnt(log, cap + 1)]
        if chained:
            return [*blocks_are('minecraft:air', [(x, y, z) for y in range(220, top + 1)]), cnt(log, height)]
        return [*blocks_are(f'minecraft:{log}', [(x, y, z) for y in range(221, top + 1)]), cnt(log, 1)]
    dig_case(label, tree_cmds(x, z, log, leaves, height, 222 if cap else None), (x, 220, z), (x + .5, 220, z - 1.5),
             'minecraft:iron_axe', checks, sneak=sneak)


for i, (log, leaves) in enumerate(TREES):
    row, col = divmod(i, 7)
    tree_case(f'tree felling {log} with {leaves}', -414 + 4 * col, 396 + 6 * row, log, leaves)
tree_case('tree not sneaking only breaks one log', -414, 408, 'oak_log', 'oak_leaves', chained=False, sneak=False)
s.cmdx('a', ['連鎖砍樹：關閉'], 'trigger treecap')
s.check('treecap switch only for A', f'score {A} su_tree matches 0', f'score {B} su_tree matches 1')
tree_case('tree felling switched off', -410, 408, 'oak_log', 'oak_leaves', chained=False)
s.cmdx('a', ['連鎖砍樹：開啟'], 'trigger treecap')
# Far from every other fixture's leaves (the foliage search reaches 5 blocks sideways).
tree_case('log pillar without leaves is not felled', -388, 416, 'oak_log', '', chained=False)
tree_case('tree felling stops at 64 logs', -386, 404, 'oak_log', 'oak_leaves', height=70, cap=64)

# Vein mining. Vanilla drops and XP per ore (no Fortune); three ores in a line, A digs the first.
ORES = {
    'coal': (['coal_ore', 'deepslate_coal_ore'], 'coal', (1, 1), (0, 2), 'wooden_pickaxe'),
    'iron': (['iron_ore', 'deepslate_iron_ore'], 'raw_iron', (1, 1), (0, 0), 'stone_pickaxe'),
    'copper': (['copper_ore', 'deepslate_copper_ore'], 'raw_copper', (2, 5), (0, 0), 'stone_pickaxe'),
    'gold': (['gold_ore', 'deepslate_gold_ore'], 'raw_gold', (1, 1), (0, 0), 'iron_pickaxe'),
    'redstone': (['redstone_ore', 'deepslate_redstone_ore'], 'redstone', (4, 5), (1, 5), 'iron_pickaxe'),
    'lapis': (['lapis_ore', 'deepslate_lapis_ore'], 'lapis_lazuli', (4, 9), (2, 5), 'stone_pickaxe'),
    'diamond': (['diamond_ore', 'deepslate_diamond_ore'], 'diamond', (1, 1), (3, 7), 'iron_pickaxe'),
    'emerald': (['emerald_ore', 'deepslate_emerald_ore'], 'emerald', (1, 1), (3, 7), 'iron_pickaxe'),
    'quartz': (['nether_quartz_ore'], 'quartz', (1, 1), (2, 5), 'wooden_pickaxe'),
    'nether_gold': (['nether_gold_ore'], 'gold_nugget', (2, 6), (0, 1), 'wooden_pickaxe'),
    'ancient': (['ancient_debris'], 'ancient_debris', (1, 1), (0, 0), 'diamond_pickaxe'),
}
WRONG_TIER = [('diamond_ore', 'stone_pickaxe'), ('deepslate_diamond_ore', 'copper_pickaxe'),
              ('diamond_ore', 'golden_pickaxe'), ('diamond_ore', 'wooden_pickaxe'),
              ('ancient_debris', 'iron_pickaxe'), ('ancient_debris', 'stone_pickaxe'),
              ('emerald_ore', 'stone_pickaxe'), ('gold_ore', 'copper_pickaxe'),
              ('redstone_ore', 'stone_pickaxe'), ('iron_ore', 'wooden_pickaxe'),
              ('lapis_ore', 'golden_pickaxe'), ('copper_ore', 'wooden_pickaxe')]
RIGHT_TIER = [('diamond_ore', 'iron_pickaxe'), ('ancient_debris', 'diamond_pickaxe'),
              ('ancient_debris', 'netherite_pickaxe'), ('iron_ore', 'stone_pickaxe'),
              ('iron_ore', 'copper_pickaxe'), ('coal_ore', 'wooden_pickaxe'),
              ('nether_quartz_ore', 'golden_pickaxe')]
ORE_INFO = {ore: (g, *v[1:4]) for g, v in ORES.items() for ore in v[0]}
VX, VY, VZ = -414, 228, 388
vein_slot = [0]


def vein_case(label, ore, tool, chained=True, sneak=True, silk=False, tries=200):
    i = vein_slot[0]
    vein_slot[0] += 1
    x = VX + 3 * (i % 10)
    z = VZ + 5 * (i // 10)
    cells = [(x, VY, z + d) for d in range(3)]
    group, drop, (dlo, dhi), (xlo, xhi) = ORE_INFO[ore]

    def checks():
        out = []
        if chained:
            out += blocks_are('minecraft:air', cells)
            if silk:
                out += [cnt('diamond_ore', 3), ('score #xp htest matches 0', 'silk touch gave XP')]
            else:
                out += [cnt(drop, 3 * dlo, 3 * dhi),
                        (f'score #xp htest matches {3*xlo}..{3*xhi}', f'XP is not {3*xlo}..{3*xhi}')]
        else:
            out += blocks_are(f'minecraft:{ore}', cells[1:])
            if 'wrong tier' in label:
                out += [cnt(drop, 0), ('score #xp htest matches 0', 'wrong tier gave XP')]
            else:
                out += [cnt(drop, dlo, dhi), (f'score #xp htest matches {xlo}..{xhi}', f'XP is not {xlo}..{xhi} for one ore')]
        return out
    setup = [f'execute in minecraft:overworld run fill {x} {VY} {z} {x} {VY} {z+2} minecraft:{ore}']
    dig_case(label, setup, cells[0], (x + .5, VY, z - 1.5), tool, checks, sneak=sneak, wait=20 if FULL else 10, tries=tries)


if not FULL:
    # XP ore, deepslate variant, multi-drop ore, nether ore and the no-XP diamond-tier ore.
    RIGHT_TIER = [('diamond_ore', 'iron_pickaxe')]
    WRONG_TIER = [('diamond_ore', 'stone_pickaxe')]
ORE_CASES = [ore for _g, (ores, *_r) in ORES.items() for ore in ores] if FULL else \
    ['deepslate_diamond_ore', 'ancient_debris']
for ore in ORE_CASES:
    vein_case(f'vein mining {ore}', ore, 'minecraft:diamond_pickaxe')
for ore, tool in RIGHT_TIER:
    vein_case(f'vein mining {ore} with lowest tier {tool}', ore, f'minecraft:{tool}')
for ore, tool in WRONG_TIER:
    vein_case(f'vein mining {ore} wrong tier {tool}', ore, f'minecraft:{tool}', chained=False, tries=900)
vein_case('vein mining silk touch drops ores and no XP', 'diamond_ore',
          'minecraft:diamond_pickaxe[minecraft:enchantments={"minecraft:silk_touch":1}]', silk=True)
vein_case('vein mining not sneaking only breaks one', 'coal_ore', 'minecraft:diamond_pickaxe', chained=False, sneak=False)
s.cmdx('a', ['礦脈連鎖挖掘：關閉'], 'trigger veinmine')
s.check('veinmine switch only for A', f'score {A} su_vein matches 0', f'score {B} su_vein matches 1')
vein_case('vein mining switched off', 'coal_ore', 'minecraft:diamond_pickaxe', chained=False)
s.cmdx('a', ['礦脈連鎖挖掘：開啟'], 'trigger veinmine')

# Auto replant: the dropped seed is planted back. Item counting is off so the drop stays on the ground.
s.step('scoreboard players set #sniff htest 0')
s.bot('a', 'sneak', 0)
CROPS = [('wheat', 'wheat[age=7]', 'wheat[age=0]', 'farmland'),
         ('carrots', 'carrots[age=7]', 'carrots[age=0]', 'farmland'),
         ('potatoes', 'potatoes[age=7]', 'potatoes[age=0]', 'farmland'),
         ('beetroots', 'beetroots[age=3]', 'beetroots[age=0]', 'farmland'),
         ('nether_wart', 'nether_wart[age=3]', 'nether_wart[age=0]', 'soul_sand')]
if not FULL:
    CROPS = [CROPS[0]]
CZ = 412
for i, (name, ripe, young, soil) in enumerate(CROPS + [('wheat switched off', 'wheat[age=7]', 'air', 'farmland')]):
    x = -398 + 3 * i
    off = 'switched off' in name
    if off:
        s.cmdx('a', ['自動補種：關閉'], 'trigger replant')
    setup = [f'execute in minecraft:overworld run setblock {x} 219 {CZ} minecraft:{soil}',
             f'execute in minecraft:overworld run setblock {x} 220 {CZ} minecraft:{ripe}']
    expect = 'minecraft:air' if off else f'minecraft:{young}'
    dig_case(f'replant {name}', setup, (x, 220, CZ), (x + .5, 220, CZ - 2.5), 'minecraft:iron_hoe',
             lambda x=x, expect=expect: blocks_are(expect, [(x, 220, CZ)]), sneak=True, wait=20 if FULL else 14)
    s.step(f'execute in minecraft:overworld run kill @e[type=minecraft:item,{region(OW_AREA)}]')
    if off:
        s.cmdx('a', ['自動補種：開啟'], 'trigger replant')

MARK_PASSED_TO = len(s.steps)
if RECHECK:
    rc_from = len(s.steps)
    s.cmdx('a', ['220', '400', '/'], 'trigger mfack', label='a sees coords action bar')
    P1 = (-414, 220, 386)
    s.step(f'execute in minecraft:overworld run setblock {P1[0]} {P1[1]-1} {P1[2]} minecraft:stone', 'function utest:nav_clear_custom {key:"a"}')
    s.tp('a', P1[0] + .2, P1[1], P1[2] + .8)
    s.trigger('a', 'pset', 1)
    s.cmdx('a', ['甲據點1'], 'function nav:set_personal {slot:1,name:"甲據點1"}')
    s.tp('a', *HUBC)
    s.trigger('a', 'pgo', 1)
    s.trigger('a', 'back')
    s.check('back after personal teleport', at_center('a', 'overworld', *HUB))
    rc = s.steps[rc_from:], s.realtime[rc_from:]
    del s.steps[MARK_PASSED_FROM:], s.realtime[MARK_PASSED_FROM:]
    s.steps += rc[0]; s.realtime += rc[1]
s.step('function utest:restore', delay=20)
s.check('player data restored after the test',
        *[(f'score #navdiff_{p} htest matches 0', f'{PLAYERS[p]} waypoint data differs from the backup') for p in PLAYERS],
        ('score #shareddiff htest matches 0', 'shared waypoints differ from the backup'),
        *[(f'score {s.sel(p)} {obj} = #{p}_{obj} htest', f'{PLAYERS[p]} {obj} not restored') for p in PLAYERS for obj in ('su_tree', 'su_vein', 'su_plant', 'c26_show')])

n = s.write(OUT)
s.extra_function(OUT, 'backup', backup)
s.extra_function(OUT, 'restore', restore)
s.extra_function(OUT, 'sniff', sniff)
s.extra_function(OUT, 'eat_item', eat_item)
s.extra_function(OUT, 'eat_orb', eat_orb)
s.extra_function(OUT, 'nav_backup', [
    '$data remove storage utest:b all.nav_$(key)',
    '$execute if data storage sunny_nav:players p$(id) run data modify storage utest:b all.nav_$(key) set from storage sunny_nav:players p$(id)',
])
s.extra_function(OUT, 'nav_restore', [
    '$data remove storage sunny_nav:players p$(id)',
    '$execute if data storage utest:b all.nav_$(key) run data modify storage sunny_nav:players p$(id) set from storage utest:b all.nav_$(key)',
])
s.extra_function(OUT, 'nav_clear_custom', [
    'data modify storage utest:arg c set value {}',
    '$data modify storage utest:arg c.id set from storage utest:b all.$(key)_id',
    'function utest:nav_clear_custom_id with storage utest:arg c',
])
s.extra_function(OUT, 'nav_verify', [
    'data modify storage utest:arg cmp set value {}',
    '$data modify storage utest:arg cmp set from storage sunny_nav:players p$(id)',
    '$execute if data storage utest:b all.nav_$(key) store success score #navdiff_$(key) htest run data modify storage utest:arg cmp set from storage utest:b all.nav_$(key)',
    '$execute unless data storage utest:b all.nav_$(key) if data storage sunny_nav:players p$(id) run scoreboard players set #navdiff_$(key) htest 1',
])
s.extra_function(OUT, 'death_is', [
    '$execute if data storage sunny_nav:players p$(id).death{x:$(x),y:$(y),z:$(z),dim:$(dim),set:1b} run scoreboard players set #r htest 1'])
s.extra_function(OUT, 'nav_clear_custom_id', ['$data remove storage sunny_nav:players p$(id).custom'])
s.extra_function(OUT, 'personal_is', [
    '$execute if data storage sunny_nav:players p$(id).custom.s$(slot){name:"$(name)",x:$(x),y:$(y),z:$(z),dim:$(dim),set:1b} run scoreboard players set #r htest 1'])
s.extra_function(OUT, 'shared_is', [
    '$execute if data storage sunny_nav:shared s$(slot){name:"$(name)",x:$(x),y:$(y),z:$(z),dim:$(dim),set:1b} run scoreboard players set #r htest 1'])
s.extra_function(OUT, 'return_player', [
    '$data modify storage utest:arg r set value {name:"$(name)"}',
    '$data modify storage utest:arg r.dim set from storage utest:b all.$(p)_dim',
    '$data modify storage utest:arg r.x set from storage utest:b all.$(p)_pos[0]',
    '$data modify storage utest:arg r.y set from storage utest:b all.$(p)_pos[1]',
    '$data modify storage utest:arg r.z set from storage utest:b all.$(p)_pos[2]',
    '$data modify storage utest:arg r.yaw set from storage utest:b all.$(p)_rot[0]',
    '$data modify storage utest:arg r.pitch set from storage utest:b all.$(p)_rot[1]',
    'function utest:tp_back with storage utest:arg r',
])
s.extra_function(OUT, 'restore_bbs', [
    '$data modify storage utest:arg q set value {name:"$(name)"}',
    '$data modify storage utest:arg q.v set from storage utest:b all.$(p)_bbs',
    'function utest:set_bbs with storage utest:arg q',
])
s.extra_function(OUT, 'set_bbs', ['$attribute @a[name=$(name),limit=1] minecraft:block_break_speed base set $(v)'])
s.extra_function(OUT, 'tp_back', ['$execute in $(dim) run tp @a[name=$(name),limit=1] $(x) $(y) $(z) $(yaw) $(pitch)'])
(OUT / 'suite.json').write_text(json.dumps({
    'ns': NS, 'prefix': 'UTEST', 'players': PLAYERS, 'timeout_s': 2700 if FULL else 480,
}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Built {n} Utilities live-test steps at {OUT}')
