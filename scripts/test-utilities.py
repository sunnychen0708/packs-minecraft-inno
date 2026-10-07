#!/usr/bin/env python3
"""Static checks plus optional isolated vanilla 26.3 server regression tests.

python scripts/test-utilities.py
python scripts/test-utilities.py --java PATH --server-jar PATH --accept-eula
The integration run uses console commands and an armor stand, not a player client.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import uuid
import threading
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'datapacks/utilities'
DATA = PACK / 'data'
# Vanilla experience dropped by each ore group (min, max); the others drop none.
VEIN_XP = {'coal': (0, 2), 'lapis': (2, 5), 'redstone': (1, 5), 'diamond': (3, 7), 'emerald': (3, 7), 'quartz': (2, 5), 'nether_gold': (0, 1)}
NO_VEIN_XP = ('iron', 'copper', 'gold', 'ancient')
# (ore block, vein group, pickaxe one tier too low): the vanilla incorrect_for_*_tool tags forbid these drops.
WRONG_TIER = [
    ('diamond_ore', 'diamond', 'stone_pickaxe'), ('deepslate_diamond_ore', 'diamond', 'copper_pickaxe'),
    ('diamond_ore', 'diamond', 'golden_pickaxe'), ('diamond_ore', 'diamond', 'wooden_pickaxe'),
    ('ancient_debris', 'ancient', 'iron_pickaxe'), ('ancient_debris', 'ancient', 'stone_pickaxe'),
    ('emerald_ore', 'emerald', 'stone_pickaxe'), ('gold_ore', 'gold', 'copper_pickaxe'),
    ('redstone_ore', 'redstone', 'stone_pickaxe'), ('iron_ore', 'iron', 'wooden_pickaxe'),
    ('lapis_ore', 'lapis', 'golden_pickaxe'), ('copper_ore', 'copper', 'wooden_pickaxe'),
]
# The lowest tier that may harvest each group still chains.
RIGHT_TIER = [
    ('diamond_ore', 'diamond', 'iron_pickaxe'), ('ancient_debris', 'ancient', 'diamond_pickaxe'),
    ('ancient_debris', 'ancient', 'netherite_pickaxe'), ('iron_ore', 'iron', 'stone_pickaxe'),
    ('iron_ore', 'iron', 'copper_pickaxe'), ('coal_ore', 'coal', 'wooden_pickaxe'),
    ('nether_quartz_ore', 'quartz', 'golden_pickaxe'),
]


def static_checks():
    for path in PACK.rglob('*.json'):
        json.loads(path.read_text(encoding='utf-8-sig'))
    meta = json.loads((PACK / 'pack.mcmeta').read_text(encoding='utf-8-sig'))
    assert meta['pack']['min_format'] == meta['pack']['max_format'] == [121, 0]
    version = re.search(r'v(\d+\.\d+)', meta['pack']['description'])[1]
    for doc in ('README.md', 'COMPATIBILITY-26.3.md'):
        assert f'v{version}' in (PACK / doc).read_text(encoding='utf-8').splitlines()[0], f'{doc} not synced to v{version}'
    assert f'version set value "26.3-{version}"' in (DATA / 'sunny_nav/function/load.mcfunction').read_text(encoding='utf-8'), f'sunny_nav:meta not synced to v{version}'
    assert f'v{version} 功能總覽' in (DATA / 'allinone/function/help.mcfunction').read_text(encoding='utf-8'), f'help not synced to v{version}'
    logs = json.loads((DATA / 'survival_utils/tags/block/natural_logs.json').read_text())['values']
    stats = (DATA / 'survival_utils/function/load/stats.mcfunction').read_text()
    tick = (DATA / 'survival_utils/function/tick.mcfunction').read_text()
    for log in logs:
        criterion = log.replace(':', '.', 1)
        match = re.search(r'scoreboard objectives add (\w+) minecraft.mined:' + re.escape(criterion) + r'\n', stats)
        assert match, f'Missing mining event for {log}'
        objective = match[1]
        dispatch = f'execute as @a[scores={{{objective}=1..}}] at @s run function survival_utils:tree/trigger'
        reset = f'scoreboard players set @a[scores={{{objective}=1..}}] {objective} 0'
        assert dispatch in tick and reset in tick and tick.index(dispatch) < tick.index(reset), log
    for path in DATA.rglob('*.mcfunction'):
        for namespace, function in re.findall(r'\bfunction ([a-z_]+):([a-z0-9_/]+)', path.read_text(encoding='utf-8')):
            assert (DATA / namespace / 'function' / (function + '.mcfunction')).is_file(), (path, function)
    modifier = DATA / 'survival_utils/item_modifier/damage_one.json'
    assert json.loads(modifier.read_text()) == {'type': 'minecraft:set_damage', 'damage': 1, 'add': True}
    for folder in ('predicate', 'item_modifier'):
        for path in DATA.glob(f'*/{folder}/*.json'):
            obj = json.loads(path.read_text())
            assert isinstance(obj, dict) and 'type' in obj, path
            assert 'function' not in obj, path
    # Chain-mined ores drop the vanilla experience range unless mined with Silk Touch.
    silk = 'execute unless items entity @s weapon.mainhand *[minecraft:enchantments~[{enchantments:"minecraft:silk_touch"}]] run function survival_utils:vein/xp '
    loot = 'loot spawn ~0.5 ~0.5 ~0.5 mine ~ ~ ~ mainhand\n'
    for ore, (low, high) in VEIN_XP.items():
        body = (DATA / f'survival_utils/function/vein/{ore}/break.mcfunction').read_text(encoding='utf-8')
        assert loot + silk + f'{{min:{low},max:{high}}}\nsetblock ~ ~ ~ minecraft:air\n' in body, ore
    for ore in NO_VEIN_XP:
        body = (DATA / f'survival_utils/function/vein/{ore}/break.mcfunction').read_text(encoding='utf-8')
        assert 'vein/xp' not in body, ore
    # Every ore group checks the pickaxe tier before it counts, loots or removes a block.
    gate = 'execute unless function survival_utils:vein/tool_ok run return 0\n'
    ores = sorted(p.parent.name for p in DATA.glob('survival_utils/function/vein/*/break.mcfunction'))
    assert ores == sorted([*VEIN_XP, *NO_VEIN_XP]), ores
    for ore in ores:
        body = (DATA / f'survival_utils/function/vein/{ore}/break.mcfunction').read_text(encoding='utf-8')
        assert gate in body and body.index(gate) < body.index('scoreboard players add #count') < body.index(loot), ore
    print(f'PASS static: JSON, format 121.0, {len(logs)} log events, dispatch/reset, function references, {len(VEIN_XP)} ore XP ranges', flush=True)


TP_DIMS = ('overworld', 'the_nether', 'the_end')


def integration(java, server):
    work = ROOT / 'dist' / ('utilities-test-' + uuid.uuid4().hex[:8])
    work.mkdir()
    packs = work / 'world/datapacks'
    packs.mkdir(parents=True)
    with zipfile.ZipFile(packs / 'utilities.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in PACK.rglob('*'):
            if path.is_file():
                archive.write(path, path.relative_to(PACK).as_posix())
    harness = packs / 'regression'
    funcs = harness / 'data/regression/function'
    funcs.mkdir(parents=True)
    (harness / 'pack.mcmeta').write_text(json.dumps({'pack': {'min_format': [121, 0], 'max_format': [121, 0], 'description': 'Isolated regression harness'}}))
    lines = ['scoreboard objectives add test dummy', 'scoreboard players set #passed test 0', 'kill @e[type=minecraft:armor_stand,tag=regression]', 'summon minecraft:armor_stand 0 80 0 {Tags:["regression"],NoGravity:1b}']
    actor = '@e[type=minecraft:armor_stand,tag=regression,limit=1]'
    assertions = []

    def check(condition, label):
        assertions.append(label)
        lines.append(f'execute {condition} run scoreboard players add #passed test 1')
        lines.append(f'execute {condition} run say PASS {label}')

    def equip(item='diamond_axe', components=''):
        lines.append(f'item replace entity {actor} weapon.mainhand with minecraft:{item}{components}')

    def wear():
        lines.append(f'item modify entity {actor} weapon.mainhand survival_utils:damage_one')

    def clear():
        lines.extend(['fill 0 80 0 10 110 10 minecraft:air', 'scoreboard players set #count su_tmp 0', 'scoreboard players set #found su_tmp 0'])

    # Real block traversal, loot and durability, with all three new leaves.
    for color in ('red', 'orange', 'yellow'):
        clear()
        equip()
        lines += ['fill 3 80 3 3 83 3 minecraft:poplar_log', f'setblock 3 84 3 minecraft:{color}_poplar_leaves[persistent=true]', f'execute as {actor} positioned 3 80 3 run function survival_utils:tree/start']
        check('if score #count su_tmp matches 4 if block 3 83 3 minecraft:air', f'{color}_poplar_chain')
        check(f'if items entity {actor} weapon.mainhand *[minecraft:damage=0]', f'{color}_poplar_legacy_durability')
        check('if entity @e[type=minecraft:item,nbt={Item:{id:"minecraft:poplar_log"}}]', f'{color}_poplar_drops')
    for wood, leaf in [('oak_log', 'oak_leaves'), ('pale_oak_log', 'pale_oak_leaves'), ('crimson_stem', 'nether_wart_block'), ('warped_stem', 'warped_wart_block')]:
        clear()
        equip()
        lines += [f'fill 3 80 3 3 82 3 minecraft:{wood}', f'setblock 3 83 3 minecraft:{leaf}', f'execute as {actor} positioned 3 80 3 run function survival_utils:tree/start']
        check('if score #count su_tmp matches 3', f'existing_{wood}')
    clear()
    equip()
    lines += ['fill 3 80 3 3 82 3 minecraft:poplar_log', f'execute as {actor} positioned 3 80 3 run function survival_utils:tree/start']
    check('if score #count su_tmp matches 0 if block 3 80 3 minecraft:poplar_log', 'leafless_logs_protected')
    lines += ['setblock 3 83 3 minecraft:red_poplar_leaves', 'scoreboard players set #count su_tmp 0']
    equip('stick')
    lines.append(f'execute as {actor} positioned 3 80 3 run function survival_utils:tree/start')
    check('if score #count su_tmp matches 0', 'non_axe_protected')
    clear()
    equip()
    lines += ['fill 1 80 1 9 80 9 minecraft:poplar_log', 'setblock 1 81 1 minecraft:yellow_poplar_leaves', f'execute as {actor} positioned 1 80 1 run function survival_utils:tree/start']
    check('if score #count su_tmp matches 64', '64_log_limit')
    # Restore v3.2 behavior even when the tool starts with one durability point.
    clear()
    equip('wooden_axe', '[minecraft:damage=58]')
    lines += ['fill 3 80 3 3 83 3 minecraft:poplar_log', 'setblock 3 84 3 minecraft:orange_poplar_leaves', f'execute as {actor} positioned 3 80 3 run function survival_utils:tree/start']
    check(f'if score #count su_tmp matches 4 if items entity {actor} weapon.mainhand minecraft:wooden_axe[minecraft:damage=0]', 'legacy_nearly_broken_axe_continues')
    for item in ('wooden_axe', 'stone_axe', 'copper_axe', 'iron_axe', 'golden_axe', 'diamond_axe', 'netherite_axe', 'diamond_pickaxe'):
        equip(item, '[minecraft:damage=10,minecraft:custom_name="Keep me"]')
        wear()
        check(f'if items entity {actor} weapon.mainhand *[minecraft:damage=0,minecraft:custom_name="Keep me"]', f'legacy_durability_{item}')
    equip('diamond_axe', '[minecraft:damage=10,minecraft:unbreakable={}]')
    wear()
    check(f'if items entity {actor} weapon.mainhand *[minecraft:damage=10,minecraft:unbreakable]', 'legacy_unbreakable_behavior')
    equip('diamond_axe', '[minecraft:damage=10,minecraft:enchantments={"minecraft:unbreaking":3}]')
    wear()
    check(f'if items entity {actor} weapon.mainhand *[minecraft:damage=0,minecraft:enchantments={{"minecraft:unbreaking":3}}]', 'legacy_enchantment_preserved')
    # Mining shares the restored v3.2 modifier; use a two-ore fixture.
    clear()
    equip('diamond_pickaxe', '[minecraft:damage=10]')
    lines += ['fill 3 80 3 3 81 3 minecraft:diamond_ore', f'execute as {actor} positioned 3 80 3 run function survival_utils:vein/diamond/break']
    check('if score #count su_tmp matches 2 if block 3 81 3 minecraft:air', 'vein_chain')
    check(f'if items entity {actor} weapon.mainhand *[minecraft:damage=0]', 'vein_legacy_durability')
    # Chain-mined ores spawn one orb each, within the vanilla range; Silk Touch and raw-ore groups spawn none.
    orbs = '@e[type=minecraft:experience_orb]'

    def mine(ore_block, ore, count, item='diamond_pickaxe', components=''):
        clear()
        equip(item, components)
        lines.extend([f'kill {orbs}', f'fill 3 80 3 3 {79 + count} 3 minecraft:{ore_block}', f'execute as {actor} positioned 3 80 3 run function survival_utils:vein/{ore}/break',
                      f'execute as {orbs} store result score @s test run data get entity @s Value', f'execute store result score #orbs test if entity {orbs}'])

    mine('diamond_ore', 'diamond', 2)
    check(f'if score #count su_tmp matches 2 if score #orbs test matches 2 unless entity @e[type=minecraft:experience_orb,scores={{test=..2}}] unless entity @e[type=minecraft:experience_orb,scores={{test=8..}}]', 'vein_xp_diamond_range')
    mine('coal_ore', 'coal', 10)
    check(f'if score #count su_tmp matches 10 if score #orbs test matches ..10 unless entity @e[type=minecraft:experience_orb,scores={{test=..0}}] unless entity @e[type=minecraft:experience_orb,scores={{test=3..}}]', 'vein_xp_coal_skips_zero')
    mine('diamond_ore', 'diamond', 2, components='[minecraft:enchantments={"minecraft:silk_touch":1}]')
    check(f'if score #count su_tmp matches 2 if score #orbs test matches 0', 'vein_xp_silk_touch_none')
    mine('iron_ore', 'iron', 2)
    check(f'if score #count su_tmp matches 2 if score #orbs test matches 0', 'vein_xp_iron_none')
    # A pickaxe below the ore's vanilla tier must leave the whole vein intact: no drops, no XP, no wear.
    items = '@e[type=minecraft:item]'
    for ore_block, ore, tool in WRONG_TIER:
        clear()
        equip(tool, '[minecraft:damage=10]')
        lines.extend([f'kill {orbs}', f'kill {items}', f'fill 3 80 3 3 81 3 minecraft:{ore_block}', f'execute as {actor} positioned 3 80 3 run function survival_utils:vein/{ore}/break'])
        check(f'if score #count su_tmp matches 0 if block 3 80 3 minecraft:{ore_block} if block 3 81 3 minecraft:{ore_block} unless entity {items} unless entity {orbs} if items entity {actor} weapon.mainhand *[minecraft:damage=10]', f'wrong_tier_{ore_block}_{tool}')
    for ore_block, ore, tool in RIGHT_TIER:
        clear()
        equip(tool)
        lines.extend([f'kill {items}', f'fill 3 80 3 3 81 3 minecraft:{ore_block}', f'execute as {actor} positioned 3 80 3 run function survival_utils:vein/{ore}/break'])
        check(f'if score #count su_tmp matches 2 if block 3 80 3 minecraft:air if block 3 81 3 minecraft:air if entity {items}', f'min_tier_{ore_block}_{tool}')
    lines.extend([f'kill {orbs}', f'kill {items}'])
    lines += [f'item replace entity {actor} weapon.mainhand with minecraft:wheat_seeds 5', f'item modify entity {actor} weapon.mainhand survival_utils:consume_one']
    check(f'if items entity {actor} weapon.mainhand minecraft:wheat_seeds[minecraft:count=4]', 'consume_one')
    # Exercise the real dispatch/reset lines using a non-player selector and spy.
    tick = (DATA / 'survival_utils/function/tick.mcfunction').read_text()
    event = '\n'.join(line for line in tick.splitlines() if 'ml_poplar' in line)
    event = event.replace('@a[', '@e[tag=regression,').replace('survival_utils:tree/trigger', 'regression:spy')
    (funcs / 'event.mcfunction').write_text(event + '\n')
    (funcs / 'spy.mcfunction').write_text('scoreboard players add #events test 1\n')
    lines += ['scoreboard players set #events test 0', f'scoreboard players set {actor} ml_poplar 1', 'function regression:event', 'function regression:event']
    check(f'if score #events test matches 1 if score {actor} ml_poplar matches 0', 'poplar_dispatch_once_and_reset')
    # An upgrade reload must preserve the existing waypoint namespaces and data.
    lines += ['data modify storage sunny_nav:players p999 set value {custom:{s1:{set:1b,name:{text:"Preserved"},x:12,y:80,z:34,dim:"minecraft:overworld"}}}', 'data modify storage sunny_nav:shared s1 set value {set:1b,name:{text:"Shared"},x:5,y:80,z:9,dim:"minecraft:overworld"}', 'function allinone:load']
    check('if data storage sunny_nav:players p999.custom.s1{x:12,z:34,name:{text:"Preserved"}}', 'personal_waypoint_preserved')
    check('if data storage sunny_nav:shared s1{x:5,z:9,name:{text:"Shared"}}', 'shared_waypoint_preserved')
    # Saved waypoints are block coordinates; every teleport must land in the middle of that block
    # (not on the corner of four blocks), on both sides of zero and in every dimension.
    tp_stand = '@e[type=minecraft:armor_stand,tag=tpcheck]'
    for dim in TP_DIMS:
        # A stand already in the target dimension: cross-dimension entity moves finish after the tick.
        lines += [f'kill {tp_stand}', f'execute in minecraft:{dim} run summon minecraft:armor_stand 0 80 0 {{Tags:["tpcheck"],NoGravity:1b}}']
        for x, z in ((5, 7), (-6, -9)):
            lines.append(f'execute as {tp_stand} run function sunny_nav:macro/tp_{dim.removeprefix("the_")} {{x:{x},y:80,z:{z}}}')
            check(f'in minecraft:{dim} positioned {x + 0.5} 80 {z + 0.5} if entity @e[type=minecraft:armor_stand,tag=tpcheck,distance=..0.01]', f'teleport_centered_{dim}_{x}_{z}')
        lines.append(f'kill {tp_stand}')
    # Instantiate every macro against harmless test arguments to catch lazy parser errors.
    args = '{id:999,slot:1,name:"Regression",x:1,y:80,z:1,dim:"minecraft:overworld",yaw:0,pitch:0,min:1,max:1,v:1}'
    for path in DATA.rglob('*.mcfunction'):
        if any(line.startswith('$') for line in path.read_text(encoding='utf-8').splitlines()):
            rel = path.relative_to(DATA)
            function = rel.parts[0] + ':' + '/'.join(rel.parts[2:]).removesuffix('.mcfunction')
            lines.append(f'execute as {actor} at @s run function {function} {args}')
    lines += [f'execute if score #passed test matches {len(assertions)} run say REGRESSION_SUCCESS', 'say REGRESSION_DONE']
    (funcs / 'run.mcfunction').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    # Fixtures are in chunk (0, 0) plus the teleport-check chunks of each dimension; wait until they
    # are loaded instead of sleeping a fixed time.
    (funcs / 'chunks_ready.mcfunction').write_text(
        'execute unless loaded 0 0 0 run return run say CHUNKS_PENDING\n'
        + ''.join(f'execute in minecraft:{dim} unless loaded -16 0 -16 run return run say CHUNKS_PENDING\n'
                  f'execute in minecraft:{dim} unless loaded 15 0 15 run return run say CHUNKS_PENDING\n' for dim in TP_DIMS)
        + 'say CHUNKS_READY\n')
    (work / 'eula.txt').write_text('eula=true\n')
    (work / 'server.properties').write_text('server-ip=127.0.0.1\nserver-port=0\nonline-mode=false\nwhite-list=true\nview-distance=2\nsimulation-distance=2\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\n')
    ready, chunks_ready, done = threading.Event(), threading.Event(), threading.Event()
    output = []
    proc = subprocess.Popen([str(java), '-Xms256M', '-Xmx1024M', '-jar', str(server), '--nogui'], cwd=work, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')

    def read():
        for line in proc.stdout:
            output.append(line)
            if 'Done (' in line:
                ready.set()
            if 'CHUNKS_READY' in line:
                chunks_ready.set()
            if 'REGRESSION_DONE' in line:
                done.set()

    reader = threading.Thread(target=read, daemon=True)
    reader.start()
    try:
        assert ready.wait(60), 'Server did not become ready'
        proc.stdin.write('forceload add 0 0\n')
        for dim in TP_DIMS:
            proc.stdin.write(f'execute in minecraft:{dim} run forceload add -16 -16 15 15\n')
        proc.stdin.flush()
        deadline = time.monotonic() + 60
        while not chunks_ready.is_set():
            assert time.monotonic() < deadline, 'Forceloaded fixture chunk did not load'
            proc.stdin.write('function regression:chunks_ready\n')
            proc.stdin.flush()
            chunks_ready.wait(1)
        proc.stdin.write('function regression:run\n')
        proc.stdin.flush()
        assert done.wait(45), 'Regression function did not complete'
    finally:
        if proc.poll() is None:
            proc.stdin.write('stop\n')
            proc.stdin.flush()
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                proc.terminate()
        reader.join(timeout=5)
        (work / 'console.log').write_text(''.join(output), encoding='utf-8')
        print(f'Integration evidence: {work}', flush=True)
    report = ''.join(output)
    failures = [label for label in assertions if f'PASS {label}' not in report]
    parse_errors = [line for line in output if any(s in line.lower() for s in ('failed to load', 'failed to parse', 'whilst instantiating', 'invalid macro', 'missing argument', 'unknown function'))]
    assert not failures, failures
    assert not parse_errors, parse_errors
    assert 'REGRESSION_SUCCESS' in report
    print(f'PASS vanilla 26.3: {len(assertions)} runtime assertions and all function macros', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java', type=Path)
    parser.add_argument('--server-jar', type=Path)
    parser.add_argument('--accept-eula', action='store_true')
    options = parser.parse_args()
    static_checks()
    if options.java or options.server_jar:
        assert options.java and options.server_jar and options.accept_eula, 'Provide Java, official server JAR and --accept-eula'
        (ROOT / 'dist').mkdir(exist_ok=True)
        integration(options.java.resolve(), options.server_jar.resolve())
