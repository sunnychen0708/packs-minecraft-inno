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


def static_checks():
    for path in PACK.rglob('*.json'):
        json.loads(path.read_text(encoding='utf-8-sig'))
    meta = json.loads((PACK / 'pack.mcmeta').read_text(encoding='utf-8-sig'))
    assert meta['pack']['min_format'] == meta['pack']['max_format'] == [121, 0]
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
    for folder in ('predicate', 'item_modifier'):
        for path in DATA.glob(f'*/{folder}/*.json'):
            obj = json.loads(path.read_text())
            assert isinstance(obj, dict) and 'type' in obj, path
            assert 'function' not in obj, path
    print(f'PASS static: JSON, format 121.0, {len(logs)} log events, dispatch/reset, function references', flush=True)


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
        lines.append(f'execute as {actor} run function survival_utils:tool/damage_one')

    def clear():
        lines.extend(['fill 0 80 0 10 110 10 minecraft:air', 'scoreboard players set #count su_tmp 0', 'scoreboard players set #found su_tmp 0'])

    # Real block traversal, loot and durability, with all three new leaves.
    for color in ('red', 'orange', 'yellow'):
        clear()
        equip()
        lines += ['fill 3 80 3 3 83 3 minecraft:poplar_log', f'setblock 3 84 3 minecraft:{color}_poplar_leaves[persistent=true]', f'execute as {actor} positioned 3 80 3 run function survival_utils:tree/start']
        check('if score #count su_tmp matches 4 if block 3 83 3 minecraft:air', f'{color}_poplar_chain')
        check(f'if items entity {actor} weapon.mainhand *[minecraft:damage=4]', f'{color}_poplar_wear')
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
    # Last durability point removes the tool and the next recursion returns.
    clear()
    equip('wooden_axe', '[minecraft:damage=58]')
    lines += ['fill 3 80 3 3 83 3 minecraft:poplar_log', 'setblock 3 84 3 minecraft:orange_poplar_leaves', f'execute as {actor} positioned 3 80 3 run function survival_utils:tree/start']
    check(f'if score #count su_tmp matches 1 unless items entity {actor} weapon.mainhand * if block 3 81 3 minecraft:poplar_log', 'broken_axe_stops_chain')
    for item in ('wooden_axe', 'stone_axe', 'copper_axe', 'iron_axe', 'golden_axe', 'diamond_axe', 'netherite_axe', 'diamond_pickaxe'):
        equip(item, '[minecraft:damage=10,minecraft:custom_name="Keep me"]')
        wear()
        check(f'if items entity {actor} weapon.mainhand *[minecraft:damage=11,minecraft:custom_name="Keep me"]', f'one_point_{item}')
    equip('diamond_axe', '[minecraft:damage=10,minecraft:unbreakable={}]')
    wear()
    check(f'if items entity {actor} weapon.mainhand *[minecraft:damage=10]', 'unbreakable_unchanged')
    equip('diamond_axe', '[minecraft:enchantments={"minecraft:unbreaking":3}]')
    wear()
    check('if data storage survival_utils:tool args{unbreaking:3} if score #wear su_tmp matches 0..3', 'unbreaking_level_and_roll')
    # Mining shares the durability helper; use a two-ore fixture.
    clear()
    equip('diamond_pickaxe')
    lines += ['fill 3 80 3 3 81 3 minecraft:diamond_ore', f'execute as {actor} positioned 3 80 3 run function survival_utils:vein/diamond/break']
    check('if score #count su_tmp matches 2 if block 3 81 3 minecraft:air', 'vein_chain')
    check(f'if items entity {actor} weapon.mainhand *[minecraft:damage=2]', 'vein_wear')
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
    # Instantiate every macro against harmless test arguments to catch lazy parser errors.
    args = '{id:999,slot:1,name:"Regression",x:1,y:80,z:1,dim:"minecraft:overworld",yaw:0,pitch:0,unbreaking:0,damage:1}'
    for path in DATA.rglob('*.mcfunction'):
        if any(line.startswith('$') for line in path.read_text(encoding='utf-8').splitlines()):
            rel = path.relative_to(DATA)
            function = rel.parts[0] + ':' + '/'.join(rel.parts[2:]).removesuffix('.mcfunction')
            lines.append(f'execute as {actor} at @s run function {function} {args}')
    lines += [f'execute if score #passed test matches {len(assertions)} run say REGRESSION_SUCCESS', 'say REGRESSION_DONE']
    (funcs / 'run.mcfunction').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    (work / 'eula.txt').write_text('eula=true\n')
    (work / 'server.properties').write_text('server-ip=127.0.0.1\nserver-port=0\nonline-mode=false\nwhite-list=true\nview-distance=2\nsimulation-distance=2\nlevel-type=minecraft:flat\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1}],"biome":"minecraft:plains"}\n')
    ready, done = threading.Event(), threading.Event()
    output = []
    proc = subprocess.Popen([str(java), '-Xms256M', '-Xmx1024M', '-jar', str(server), '--nogui'], cwd=work, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')

    def read():
        for line in proc.stdout:
            output.append(line)
            if 'Done (' in line:
                ready.set()
            if 'REGRESSION_DONE' in line:
                done.set()

    reader = threading.Thread(target=read, daemon=True)
    reader.start()
    try:
        assert ready.wait(60), 'Server did not become ready'
        proc.stdin.write('forceload add 0 0\n')
        proc.stdin.flush()
        time.sleep(2)
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
