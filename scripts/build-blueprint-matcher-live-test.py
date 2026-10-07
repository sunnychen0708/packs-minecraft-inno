"""Build an opt-in Copy/Paste v1.7 Blueprint matcher live test datapack (issue #49).

Places every exact 26.3 block state (from scripts/data/blocks-26.3.json) at one reserved
block with `setblock ... strict`, runs mcc:blueprint/generated/root there as the server
(so summon creates nothing) and checks that mcc:temp state is exactly {id, properties}.
Air must still fail. Work is split into scheduled batches so one tick never runs the
whole 35720-state check.

Run: /function mcc_bp_live:start  ->  `MCCBP_RESULT PASS|FAIL` in the server log.
The generated test never runs on load and is intended only for innotest.
"""
from pathlib import Path
import itertools
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist/mcc-bp-matcher-live-test'
POS = (-440, 250, 120)
BATCH = 1000

if OUT.exists():
    shutil.rmtree(OUT)
F = OUT / 'data/mcc_bp_live/function'
F.mkdir(parents=True)
(OUT / 'pack.mcmeta').write_text(json.dumps({
    'pack': {'description': 'Opt-in CopyPaste v1.7 Blueprint matcher live test', 'min_format': 121, 'max_format': 121}
}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

blocks = json.loads((ROOT / 'scripts/data/blocks-26.3.json').read_text(encoding='utf-8'))
states = []
for block, spec in blocks.items():
    props = spec.get('properties', {})
    for combo in itertools.product(*props.values()):
        states.append((block, dict(zip(props, combo))))
# Repeats: a state that is already in storage must still be rewritten correctly.
states += [s for s in states if s[0] in ('minecraft:stone', 'minecraft:oak_planks')]
states += [('minecraft:oak_stairs', blocks['minecraft:oak_stairs']['default'])] * 2

x, y, z = POS
at = f'{x} {y} {z}'
here = f'in minecraft:overworld positioned {at}'

def write(name, lines):
    (F / f'{name}.mcfunction').write_text('\n'.join(lines) + '\n', encoding='utf-8')

write('start', [
    'scoreboard objectives add mccbp dummy',
    'scoreboard players set #states mccbp 0',
    'scoreboard players set #fail mccbp 0',
    'scoreboard players set #air mccbp -1',
    f'execute in minecraft:overworld run forceload add {x} {z}',
    # Refuse to overwrite anything: the reserved block must be air.
    f'execute {here} unless block ~ ~ ~ minecraft:air run return run say MCCBP_RESULT FAIL reserved block {at} is not air',
    'data merge storage mcc:temp {tx:0,ty:0,tz:0,id:0}',
    'say MCCBP_BEGIN',
    'schedule function mcc_bp_live:batch_0 1t',
])

batches = [states[i:i + BATCH] for i in range(0, len(states), BATCH)]
for n, chunk in enumerate(batches):
    lines = []
    for block, props in chunk:
        pred = block + ('[' + ','.join(f'{k}={v}' for k, v in props.items()) + ']' if props else '')
        snbt = '{id:"%s"%s}' % (block, (',properties:{' + ','.join(f'{k}:"{v}"' for k, v in props.items()) + '}') if props else '')
        lines += [f'execute in minecraft:overworld run setblock {at} {pred} strict',
                  f'data modify storage mcc_bp_live:t want set value {snbt}',
                  'function mcc_bp_live:check']
    lines.append(f'schedule function mcc_bp_live:{"batch_" + str(n + 1) if n + 1 < len(batches) else "finish"} 1t')
    write(f'batch_{n}', lines)

write('check', [
    'scoreboard players add #states mccbp 1',
    'data remove storage mcc:temp state',
    f'execute store result score #ret mccbp {here} run function mcc:blueprint/generated/root',
    'execute unless score #ret mccbp matches 1 run return run function mcc_bp_live:fail with storage mcc_bp_live:t',
    'execute unless data storage mcc:temp state run return run function mcc_bp_live:fail with storage mcc_bp_live:t',
    'data modify storage mcc_bp_live:t cmp set from storage mcc_bp_live:t want',
    'execute store success score #chg mccbp run data modify storage mcc_bp_live:t cmp set from storage mcc:temp state',
    'execute unless score #chg mccbp matches 0 run return run function mcc_bp_live:fail with storage mcc_bp_live:t',
])
write('fail', [
    'scoreboard players add #fail mccbp 1',
    '$execute if score #fail mccbp matches ..20 run say MCCBP_STATE_FAIL $(want)',
])
write('finish', [
    f'execute in minecraft:overworld run setblock {at} minecraft:air strict',
    'data remove storage mcc:temp state',
    f'execute store result score #air mccbp {here} run function mcc:blueprint/generated/root',
    f'execute in minecraft:overworld run setblock {at} minecraft:air strict',
    f'execute in minecraft:overworld run forceload remove {x} {z}',
    'execute store result storage mcc_bp_live:t n int 1 run scoreboard players get #states mccbp',
    'execute store result storage mcc_bp_live:t f int 1 run scoreboard players get #fail mccbp',
    'execute store result storage mcc_bp_live:t a int 1 run scoreboard players get #air mccbp',
    'function mcc_bp_live:report with storage mcc_bp_live:t',
    f'execute if score #states mccbp matches {len(states)} if score #fail mccbp matches 0 if score #air mccbp matches 0 unless data storage mcc:temp state run return run say MCCBP_RESULT PASS',
    'say MCCBP_RESULT FAIL',
])
write('report', ['$say MCCBP_COUNTS states=$(n) expected=%d fail=$(f) air_ret=$(a)' % len(states)])

print(f'built {OUT} ({len(states)} states, {len(batches)} batches)')
