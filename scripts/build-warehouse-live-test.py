"""Build the Warehouse innotest live regression (about 3 minutes).

Runs against the real warehouse on the inno map copy: the registered boxes, the
player's own classification overrides and the real stock. Server-only stretches
run at the fastest tick rate; only the right-click registration waits for a bot.

Covered: sorting by the current rules (player overrides first, default
classification otherwise; main box or its overflow box), a rule change and a
rule removal through the player UI triggers, search (Chinese name, Minecraft ID,
one character with the 30-result cap), Pick, the shared API (count, take
all-or-nothing, refund, plain-stacks-only, material sources, resolve_block,
highlight), the box view, box rename/reset, right-click registration and
unregistration, the v4.6 chunk forceloads, the system off/on switch and a
re-run of the load/migrations that must not change any saved data.

Test items carry custom_data {wtest:1b} so they never merge with real stock and
are removed from every box afterwards. warehouse:chests, rules overrides,
boxnames, the system switch and player A's main-hand item are backed up and
restored by `function wtest:cleanup`; real stock taken by Pick and the API is
put back through the entry box.

Run with the `run-live-suite` controller operation (pack warehouse).
"""
from pathlib import Path
import glob
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from innotest_harness import Suite

# --recheck: only the checks that have not passed on innotest yet; setup is kept.
RECHECK = '--recheck' in sys.argv

WH = ROOT / 'datapacks/warehouse/data/warehouse'
OUT = ROOT / 'dist/warehouse-live-test'
NS = 'wtest'
PLAYERS = {'a': 'penguin0531'}
s = Suite(NS, 'WTEST', PLAYERS, 'Opt-in Warehouse innotest live regression')
s.default_delay = 2
A = s.sel('a')
OW = 'in minecraft:overworld'
O = (-400, 280, 160)                        # sky box near the innotest spawn, nothing built there
AREA = (-412, 276, 150, -388, 286, 172)
BK = (-412, 276, 150)                       # chest holding A's main-hand item during the test
CODES = ['00'] + [f'{r}{c}' for r in range(1, 7) for c in range(10)]

# Default classification: the first box tag (in classify order) that lists the item.
def tag_items(code):
    vals = json.loads((WH / f'tags/item/box_{code}.json').read_text())['values']
    return [v['id'] if isinstance(v, dict) else v for v in vals]
DEFAULT = {}
for code in sorted(int(os.path.basename(p)[4:6]) for p in glob.glob(str(WH / 'tags/item/box_*.json'))):
    for item in tag_items(code):
        DEFAULT.setdefault(item, code)
SORT_ITEMS = ['minecraft:diamond', 'minecraft:wheat', 'minecraft:stone', 'minecraft:oak_log',
              'minecraft:white_wool', 'minecraft:netherrack', 'minecraft:ender_pearl', 'minecraft:cobblestone']
RULE_ITEM, RULE_INDEX = 'minecraft:reinforced_deepslate', 1224   # unobtainable in survival: no real stock moves
assert 'reinforced_deepslate' in (WH / f'function/rule/item/{RULE_INDEX - 1}.mcfunction').read_text()


def region(a):
    x1, y1, z1, x2, y2, z2 = a
    return f'x={x1},y={y1},z={z1},dx={x2-x1},dy={y2-y1},dz={z2-z1}'


def count(item, score):
    return [f'function warehouse:api/count_item {{item_id:"{item}"}}',
            f'execute store result score {score} htest run data get storage warehouse:api result.available']


def entry_empty_wait(label, tries=400):
    s.step('function wtest:entry_count with storage warehouse:chests c00', delay=1)
    s.wait(label, ['function wtest:entry_is_empty'], tries=tries)


def find(i, item, label):
    """Where did test item i end up? Compare with the current rule (override first, default otherwise)."""
    d = DEFAULT.get(item, 0)
    s.step('scoreboard players set #found htest -1', f'data modify storage wtest:arg p set value {{i:{i}}}',
           'function wtest:probe_all',
           f'scoreboard players set #exp htest {d}',
           f'execute if data storage warehouse:rules overrides."{item}" store result score #exp htest run data get storage warehouse:rules overrides."{item}"',
           'scoreboard players operation #ov htest = #exp htest', 'scoreboard players operation #ov htest /= #ten htest',
           'scoreboard players operation #ov htest *= #ten htest',
           'execute if score #exp htest matches 0 run scoreboard players set #exp htest 100',
           'scoreboard players set #r htest 0',
           'execute if score #found htest = #exp htest run scoreboard players set #r htest 1',
           'execute unless score #exp htest matches 100 if score #found htest = #ov htest run scoreboard players set #r htest 1',
           f'execute if score #found htest = #ov htest unless score #exp htest matches 100 run say WTEST_NOTE {label.replace(" ", "_")} went to the overflow box (main box full)', delay=1)
    s.check(label, ('score #r htest matches 1', f'{item} found in box code (#found) not the rule box; default {d}, player override wins'))


# ---- backup / restore -----------------------------------------------------------
backup = [
    'execute if data storage wtest:b all.backed run function wtest:restore',
    'data remove storage wtest:b all',
    'data modify storage wtest:b all set value {}',
    'data modify storage wtest:b all.chests set from storage warehouse:chests',
    'data modify storage wtest:b all.overrides set from storage warehouse:rules overrides',
    'data modify storage wtest:b all.boxnames set from storage warehouse:boxnames',
    'execute store result storage wtest:b all.enabled int 1 run scoreboard players get #enabled wh_sys',
    'data modify storage wtest:b all.backed set value 1b',
]
restore = [
    'execute unless data storage wtest:b all.backed run return run say WTEST_RESTORE nothing to restore',
    'function wtest:remove_tagged_all',
    'data remove storage warehouse:chests c13',
    'data modify storage warehouse:chests c13 set from storage wtest:b all.chests.c13',
    'data remove storage warehouse:rules overrides',
    'data modify storage warehouse:rules overrides set from storage wtest:b all.overrides',
    *[f'data remove storage warehouse:boxnames c{c}' for c in CODES],
    *[f'execute if data storage wtest:b all.boxnames.c{c} run data modify storage warehouse:boxnames c{c} set from storage wtest:b all.boxnames.c{c}' for c in CODES],
    'execute store result score #enabled wh_sys run data get storage wtest:b all.enabled',
    'function warehouse:chunks/refresh',
    f'execute if entity {A} {OW} if block {BK[0]} {BK[1]} {BK[2]} minecraft:chest run item replace entity {A} weapon.mainhand from block {BK[0]} {BK[1]} {BK[2]} container.0',
    f'execute unless entity {A} run return run say WTEST_RESTORE partial: run function wtest:restore again when {PLAYERS["a"]} is online',
    f'execute {OW} run fill {AREA[0]} {AREA[1]} {AREA[2]} {AREA[3]} {AREA[4]} {AREA[5]} air',
    f'execute {OW} run kill @e[type=minecraft:item,{region(AREA)}]',
    'data remove storage wtest:b all',
    'say WTEST_RESTORE done',
]
s.cleanup('function wtest:restore')

# ---- 0. fixtures ---------------------------------------------------------------
s.step('function wtest:backup', 'scoreboard players set #ten htest 10')
s.tp('a', O[0] + .5, O[1], O[2] + .5)
s.step('say WTEST loading test area', delay=40, realtime=True)
s.step(f'execute {OW} run fill {AREA[0]} {AREA[1]} {AREA[2]} {AREA[3]} {AREA[4]} {AREA[5]} air',
       f'execute {OW} run setblock {BK[0]} {BK[1]} {BK[2]} minecraft:chest',
       f'execute {OW} run item replace block {BK[0]} {BK[1]} {BK[2]} container.0 from entity {A} weapon.mainhand',
       f'execute {OW} run setblock {O[0]} {O[1]-1} {O[2]} minecraft:stone')
s.check('backup taken', 'data storage wtest:b all{backed:1b}', 'data storage warehouse:chests c00{registered:1b,valid:1b}')

if RECHECK:
    s.speed(True)
    s.step(f'execute as {A} run function warehouse:search/run {{q:"鵝卵石"}}')
    s.check('search by Chinese name lists the item (鵝卵石 matches 8 items)',
            ('data storage warehouse:runtime search{ids:["642"]}', '鵝卵石 results do not include minecraft:cobblestone'),
            'data storage warehouse:runtime search{total:8}')
    s.step(*count('minecraft:cobblestone', '#a1'),
           'execute store result storage wtest:arg big.count int 1 run scoreboard players add #a1 htest 1',
           'data modify storage wtest:arg big.item_id set value "minecraft:cobblestone"',
           'function warehouse:api/take_item with storage wtest:arg big', *count('minecraft:cobblestone', '#a2'),
           'scoreboard players remove #a1 htest 1')
    s.check('take_item over the stock is refused', 'data storage warehouse:api result{ok:0b}')
    s.check('take_item over the stock reports insufficient_stock', 'data storage warehouse:api result{error:"insufficient_stock"}')
    s.check('take_item over the stock takes nothing', 'score #a2 htest = #a1 htest')
    s.step('function warehouse:api/material_sources/refresh',
           'execute store result score #msc htest run data get storage warehouse:api material_source_count')
    s.check('material sources list the registered boxes within the 64 limit',
            'data storage warehouse:api meta{material_source_limit:64}', 'data storage warehouse:api material_sources[0]',
            'score #msc htest matches 1..64')
    s.step('function wtest:restore', delay=4)
else:
    # ---- 1. register / unregister by right-click (real bot) ------------------------
    RX, RY, RZ = O[0] + 6, O[1], O[2] + 4
    s.step(f'execute {OW} run setblock {RX} {RY} {RZ} minecraft:chest[facing=south,type=right]',
           f'execute {OW} run setblock {RX+1} {RY} {RZ} minecraft:chest[facing=south,type=left]',
           f'execute as {A} run trigger wh_register set 13')
    s.step(f'execute as {A} run trigger wh_action set 4')
    s.tp('a', RX + .5, RY, RZ + 2.5, 180, 29.2)
    s.bot('a', 'use', RX, RY, RZ)
    s.bot('a', 'close')
    s.wait('c13 registered', [f'data storage warehouse:chests c13{{registered:1b,a_z:{RZ}}}'], tries=40)
    s.check('right-click registration saves the chest', f'data storage warehouse:chests c13{{registered:1b,valid:1b,a_y:{RY},a_z:{RZ}}}')
    s.step(f'execute in minecraft:overworld store success score #fl htest run forceload query {RX} {RZ}')
    s.check('the registered chest chunk is forceloaded (v4.6)', 'score #fl htest matches 1')
    s.step(f'execute as {A} run trigger wh_unreg set 13')
    s.step(f'execute as {A} run trigger wh_unreg_do set 1')
    s.check('unregister clears the registration', 'data storage warehouse:chests c13{registered:0b}')
    s.step('data modify storage warehouse:chests c13 set from storage wtest:b all.chests.c13', 'function warehouse:chunks/refresh')

    # Everything after this waits only for the server: run it at the fastest tick rate.
    s.speed(True)

    # ---- 1. sorting by the current rules ----------------------------------------
    entry_empty_wait('entry box empty before the sort test')
    s.step(*count('minecraft:cobblestone', '#cob0'))
    s.step(*[f'function wtest:entry_put {{slot:{i},item:"{item}",i:{i}}}' for i, item in enumerate(SORT_ITEMS)])
    entry_empty_wait('entry box sorted')
    for i, item in enumerate(SORT_ITEMS):
        find(i, item, f'sort {item.split(":")[1]} into its rule box')
    s.step(*count('minecraft:cobblestone', '#cob1'))
    s.check('tagged (non-plain) stacks are not counted as stock', 'score #cob1 htest = #cob0 htest')

    # ---- 2. rule change and removal through the player UI triggers ---------------
    s.step(f'execute as {A} run trigger wh_search_pick set {RULE_INDEX}')
    s.step(f'execute as {A} run trigger wh_rule_dest set 13')
    s.check('rule change writes the player override', f'data storage warehouse:rules {{overrides:{{"{RULE_ITEM}":13}}}}')
    s.step(f'function wtest:entry_put {{slot:0,item:"{RULE_ITEM}",i:20}}')
    entry_empty_wait('entry box sorted after the rule change')
    find(20, RULE_ITEM, 'changed rule routes the item to the new box')
    s.step(f'execute as {A} run trigger wh_rule set 2')
    s.check('rule removal sets the item to no box', f'data storage warehouse:rules {{overrides:{{"{RULE_ITEM}":0}}}}')
    s.step(f'function wtest:entry_put {{slot:0,item:"{RULE_ITEM}",i:21}}', delay=200)
    find(21, RULE_ITEM, 'an item with no box stays in the entry box')
    s.step('function wtest:remove_tagged_entry with storage warehouse:chests c00')

    # ---- 3. search --------------------------------------------------------------
    s.step(f'execute as {A} run function warehouse:search/run {{q:"鵝卵石"}}')
    s.check('search by Chinese name lists the item (鵝卵石 matches 8 items)',
            ('data storage warehouse:runtime search{ids:["642"]}', '鵝卵石 results do not include minecraft:cobblestone'),
            'data storage warehouse:runtime search{total:8}')
    s.step(f'execute as {A} run function warehouse:search/run {{q:"minecraft:cobblestone"}}')
    s.check('search by Minecraft ID', 'data storage warehouse:runtime search{item_id:"minecraft:cobblestone"}')
    s.step(f'execute as {A} run function warehouse:search/run {{q:"石"}}',
           'execute store result score #tot htest run data get storage warehouse:runtime search.total')
    s.check('one character searches and caps the list at 30', 'score #tot htest matches 31..', 'score #search_lines wh_search matches ..30')

    # ---- 4. Pick ----------------------------------------------------------------
    PX, PY, PZ = O[0] + 3, O[1], O[2]
    s.step(f'execute {OW} run setblock {PX} {PY} {PZ} minecraft:cobblestone', *count('minecraft:cobblestone', '#c0'),
           f'execute store result score #inv0 htest run clear {A} minecraft:cobblestone 0')
    s.tp('a', O[0] + .5, O[1], O[2] + .5, -90, 20.5)
    s.step(f'execute as {A} at {A} run trigger pick', delay=4)
    s.step(*count('minecraft:cobblestone', '#c1'), f'execute store result score #inv1 htest run clear {A} minecraft:cobblestone 0',
           'scoreboard players operation #got htest = #inv1 htest', 'scoreboard players operation #got htest -= #inv0 htest',
           'scoreboard players operation #taken htest = #c0 htest', 'scoreboard players operation #taken htest -= #c1 htest',
           'scoreboard players set #want htest 64', 'execute if score #c0 htest matches ..63 run scoreboard players operation #want htest = #c0 htest')
    s.check('pick gives one stack of the looked-at block', 'score #got htest = #want htest')
    s.check('pick takes exactly that stack from the warehouse', 'score #taken htest = #got htest')
    s.step('execute store result storage wtest:arg n.n int 1 run scoreboard players get #got htest',
           f'execute as {A} run function wtest:clear_n with storage wtest:arg n',
           'execute store result storage wtest:arg r.count int 1 run scoreboard players get #got htest',
           'data modify storage wtest:arg r.item_id set value "minecraft:cobblestone"',
           'function warehouse:api/refund_item with storage wtest:arg r')
    entry_empty_wait('picked stack returned and sorted')
    s.step(*count('minecraft:cobblestone', '#c2'))
    s.check('stock is back after returning the picked stack', 'score #c2 htest = #c0 htest')

    # ---- 5. shared API ----------------------------------------------------------
    s.step(*count('minecraft:cobblestone', '#a0'), 'function warehouse:api/take_item {item_id:"minecraft:cobblestone",count:5}')
    s.check('take_item takes exactly the requested amount', 'data storage warehouse:api result{ok:1b}')
    s.step(*count('minecraft:cobblestone', '#a1'), 'scoreboard players operation #a0 htest -= #a1 htest')
    s.check('stock drops by the amount taken', 'score #a0 htest matches 5')
    s.step('execute store result storage wtest:arg big.count int 1 run scoreboard players add #a1 htest 1',
           'data modify storage wtest:arg big.item_id set value "minecraft:cobblestone"',
           'function warehouse:api/take_item with storage wtest:arg big', *count('minecraft:cobblestone', '#a2'),
           'scoreboard players remove #a1 htest 1')
    s.check('take_item over the stock is refused', 'data storage warehouse:api result{ok:0b}')
    s.check('take_item over the stock reports insufficient_stock', 'data storage warehouse:api result{error:"insufficient_stock"}')
    s.check('take_item over the stock takes nothing', 'score #a2 htest = #a1 htest')
    s.step('function warehouse:api/refund_item {item_id:"minecraft:cobblestone",count:5}')
    s.check('refund_item accepts the stack', 'data storage warehouse:api result{remaining:0}')
    entry_empty_wait('refund sorted')
    s.step(*count('minecraft:cobblestone', '#a3'), 'scoreboard players operation #a3 htest -= #a1 htest')
    s.check('stock is back after the refund', 'score #a3 htest matches 5')
    s.step('function warehouse:api/material_sources/refresh',
           'execute store result score #msc htest run data get storage warehouse:api material_source_count')
    s.check('material sources list the registered boxes within the 64 limit',
            'data storage warehouse:api meta{material_source_limit:64}', 'data storage warehouse:api material_sources[0]',
            'score #msc htest matches 1..64')
    s.step(f'execute {OW} run setblock {PX} {PY} {PZ} minecraft:oak_stairs', f'execute {OW} positioned {PX} {PY} {PZ} run function warehouse:api/resolve_block')
    s.check('resolve_block gives the survival item and stack size',
            'data storage warehouse:api result{ok:1b,item_id:"minecraft:oak_stairs",max_stack:64}')
    s.step(f'execute {OW} run setblock {PX} {PY} {PZ} minecraft:bedrock', f'execute {OW} positioned {PX} {PY} {PZ} run function warehouse:api/resolve_block')
    s.check('resolve_block refuses blocks with no survival item', 'data storage warehouse:api result{ok:0b}')
    s.step('data modify storage warehouse:api request set value {code:31}',
           f'execute as {A} store result score #hl htest run function warehouse:api/highlight')
    s.check('highlight marks a registered box', 'score #hl htest matches 1')

    # ---- 6. view, rename ------------------------------------------------------------
    s.step(f'execute as {A} run trigger wh_view set 31', delay=4)
    s.check('view lists a box', f'score {A} wh_viewlines matches 1..', 'data storage warehouse:runtime viewer.lines[0]')
    s.step(f'item replace entity {A} weapon.mainhand with minecraft:paper[minecraft:custom_name="WTest箱"]',
           f'execute as {A} run trigger wh_rename_target set 31')
    s.step(f'execute as {A} run trigger wh_rename set 1')
    s.check('rename stores the custom box name', 'data storage warehouse:boxnames c31')
    s.step(f'execute as {A} run trigger wh_rename set 2', f'item replace entity {A} weapon.mainhand with minecraft:air')

    # ---- 8. every real box chunk is forceloaded ---------------------------------
    s.step('scoreboard players set #nofl htest 0', 'function wtest:forceload_all')
    s.check('every registered box chunk is forceloaded', ('score #nofl htest matches 0', 'some registered box chunk is not forceloaded'))

    # ---- 9. system off / on -------------------------------------------------------
    s.step('function warehouse:system/off', 'function wtest:entry_put {slot:0,item:"minecraft:diamond",i:30}', delay=100)
    s.step('function wtest:entry_count with storage warehouse:chests c00')
    s.check('nothing is sorted while the system is off', 'score #entry htest matches 1')
    s.step('function warehouse:system/on')
    entry_empty_wait('sorting resumes when switched on')
    find(30, 'minecraft:diamond', 'sorting after switching back on')

    # ---- 10. load / migrations re-run changes no saved data -------------------------
    s.step('function wtest:remove_tagged_all',
           'data modify storage wtest:arg cmp set value {}',
           'data modify storage wtest:arg cmp.chests set from storage warehouse:chests',
           'data modify storage wtest:arg cmp.overrides set from storage warehouse:rules overrides',
           'data modify storage wtest:arg cmp.boxnames set from storage warehouse:boxnames',
           'function warehouse:load', 'function warehouse:load',
           'execute store success score #d1 htest run data modify storage wtest:arg cmp.chests set from storage warehouse:chests',
           'execute store success score #d2 htest run data modify storage wtest:arg cmp.overrides set from storage warehouse:rules overrides',
           'execute store success score #d3 htest run data modify storage wtest:arg cmp.boxnames set from storage warehouse:boxnames')
    s.check('re-running load/migrations keeps registrations, rules and names',
            ('score #d1 htest matches 0', 'warehouse:chests changed'), ('score #d2 htest matches 0', 'overrides changed'),
            ('score #d3 htest matches 0', 'boxnames changed'))

    s.step('function wtest:restore', delay=4)
    s.check('test items removed and registrations restored', 'function wtest:no_tagged_left')

# ---- write -------------------------------------------------------------------
n = s.write(OUT)
x = s.extra_function
x(OUT, 'backup', backup)
x(OUT, 'restore', restore)
x(OUT, 'entry_put', ['$data modify storage wtest:arg put set value {slot:$(slot),item:"$(item)",i:$(i)}',
                     'data modify storage wtest:arg put.a_x set from storage warehouse:chests c00.a_x',
                     'data modify storage wtest:arg put.a_y set from storage warehouse:chests c00.a_y',
                     'data modify storage wtest:arg put.a_z set from storage warehouse:chests c00.a_z',
                     'data modify storage wtest:arg put.dimension set from storage warehouse:chests c00.dimension',
                     'function wtest:entry_put_at with storage wtest:arg put'])
x(OUT, 'entry_put_at', ['$execute in $(dimension) run item replace block $(a_x) $(a_y) $(a_z) container.$(slot) with $(item)[minecraft:custom_data={wtest:1b,i:$(i)}] 1'])
x(OUT, 'entry_count', ['scoreboard players set #entry htest 0',
                       '$execute in $(dimension) store result score #entry htest if items block $(a_x) $(a_y) $(a_z) container.* *',
                       '$execute in $(dimension) store result score #entry_b htest if items block $(b_x) $(b_y) $(b_z) container.* *',
                       'scoreboard players operation #entry htest += #entry_b htest'])
x(OUT, 'entry_is_empty', ['function wtest:entry_count with storage warehouse:chests c00',
                          'return run execute if score #entry htest matches 0'])
probe_all = []
for c in CODES:
    code = 100 if c == '00' else int(c)
    probe_all += [f'data modify storage wtest:arg q set from storage warehouse:chests c{c}',
                  f'data modify storage wtest:arg q.i set from storage wtest:arg p.i',
                  f'data modify storage wtest:arg q.code set value {code}',
                  f'execute if data storage wtest:arg q{{registered:1b}} run function wtest:probe with storage wtest:arg q']
x(OUT, 'probe_all', probe_all)
x(OUT, 'probe', ['$execute in $(dimension) if data block $(a_x) $(a_y) $(a_z) Items[{components:{"minecraft:custom_data":{wtest:1b,i:$(i)}}}] run scoreboard players set #found htest $(code)',
                 '$execute in $(dimension) if data block $(b_x) $(b_y) $(b_z) Items[{components:{"minecraft:custom_data":{wtest:1b,i:$(i)}}}] run scoreboard players set #found htest $(code)'])
rm_all = []
for c in CODES:
    rm_all += [f'data modify storage wtest:arg q set from storage warehouse:chests c{c}',
               f'execute if data storage wtest:arg q{{registered:1b}} run function wtest:remove_tagged_entry with storage wtest:arg q']
x(OUT, 'remove_tagged_all', rm_all)
x(OUT, 'remove_tagged_entry', ['$execute in $(dimension) run data remove block $(a_x) $(a_y) $(a_z) Items[{components:{"minecraft:custom_data":{wtest:1b}}}]',
                               '$execute in $(dimension) run data remove block $(b_x) $(b_y) $(b_z) Items[{components:{"minecraft:custom_data":{wtest:1b}}}]'])
no_left = ['scoreboard players set #left htest 0']
for c in CODES:
    no_left += [f'data modify storage wtest:arg q set from storage warehouse:chests c{c}',
                f'execute if data storage wtest:arg q{{registered:1b}} run function wtest:tagged_in with storage wtest:arg q']
no_left.append('return run execute if score #left htest matches 0')
x(OUT, 'no_tagged_left', no_left)
x(OUT, 'tagged_in', ['$execute in $(dimension) if data block $(a_x) $(a_y) $(a_z) Items[{components:{"minecraft:custom_data":{wtest:1b}}}] run scoreboard players add #left htest 1',
                     '$execute in $(dimension) if data block $(b_x) $(b_y) $(b_z) Items[{components:{"minecraft:custom_data":{wtest:1b}}}] run scoreboard players add #left htest 1'])
fl_all = []
for c in CODES:
    fl_all += [f'data modify storage wtest:arg q set from storage warehouse:chests c{c}',
               f'execute if data storage wtest:arg q{{registered:1b,valid:1b}} run function wtest:forceload_one with storage wtest:arg q']
x(OUT, 'forceload_all', fl_all)
x(OUT, 'forceload_one', ['scoreboard players set #q htest 0',
                         '$execute in $(dimension) store success score #q htest run forceload query $(a_x) $(a_z)',
                         'execute if score #q htest matches 0 run scoreboard players add #nofl htest 1'])
x(OUT, 'clear_n', ['$clear @s minecraft:cobblestone $(n)'])
(OUT / 'suite.json').write_text(json.dumps({'ns': NS, 'prefix': 'WTEST', 'players': PLAYERS, 'timeout_s': 480},
                                           ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Built {n} Warehouse live-test steps at {OUT}')
