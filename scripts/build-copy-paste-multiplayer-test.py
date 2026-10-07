"""Build an opt-in two-player v1.7 Copy/Paste concurrency test datapack.

Player A: /function mcc_mp_test:join_a
Player B: /function mcc_mp_test:join_b
Then either player: /function mcc_mp_test:start

The generated test never runs on load and is intended only for a backed-up test world.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist/mcc-multiplayer-test'
F=OUT/'data/mcc_mp_test/function'
F.mkdir(parents=True,exist_ok=True)
(OUT/'pack.mcmeta').write_text(json.dumps({
    'pack':{'description':'Opt-in CopyPaste v1.7 two-player concurrency regression','min_format':121,'max_format':121}
},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

steps=[]
def step(*commands): steps.append(list(commands))
def both_trigger(a,b=None):
    b=a if b is None else b
    step(f'execute as @a[tag=mcc_mp_a,limit=1] run trigger {a}',
         f'execute as @a[tag=mcc_mp_b,limit=1] run trigger {b}')
def aim(tag,x,z,y=250):
    step(f'execute in minecraft:overworld run tp @a[tag={tag},limit=1] {x+.5} {y+4} {z+.5} 0 90')
def check(label,*conditions):
    cmds=['scoreboard players set #ok mccmp 1']
    for cond in conditions:
        if cond.startswith('in '):
            if ' if ' in cond:
                negated = cond.replace(' if ', ' unless ', 1)
            elif ' unless ' in cond:
                negated = cond.replace(' unless ', ' if ', 1)
            else:
                raise ValueError(f'cannot negate execute condition: {cond}')
            cmds.append(f'execute {negated} run scoreboard players set #ok mccmp 0')
        else:
            cmds.append(f'execute unless {cond} run scoreboard players set #ok mccmp 0')
    cmds += [
        f'execute if score #ok mccmp matches 1 run tellraw @a[tag=mcc_mp_a] "MCCMP PASS {label}"',
        f'execute if score #ok mccmp matches 1 run tellraw @a[tag=mcc_mp_b] "MCCMP PASS {label}"',
        f'execute unless score #ok mccmp matches 1 run tellraw @a[tag=mcc_mp_a] "MCCMP FAIL {label}"',
        f'execute unless score #ok mccmp matches 1 run tellraw @a[tag=mcc_mp_b] "MCCMP FAIL {label}"',
        f'execute if score #ok mccmp matches 1 run say MCCMP_CHECK PASS {label}',
        f'execute unless score #ok mccmp matches 1 run say MCCMP_CHECK FAIL {label}',
        'execute if score #ok mccmp matches 1 run scoreboard players add #pass mccmp 1',
        'execute unless score #ok mccmp matches 1 run scoreboard players add #fail mccmp 1',
    ]
    step(*cmds)

# Two visually distinct source fixtures and two target areas.
step(
    'execute in minecraft:overworld run fill -305 248 85 -270 255 130 air',
    'execute in minecraft:overworld run setblock -300 250 90 gold_block',
    'execute in minecraft:overworld run setblock -298 250 90 diamond_block',
    'execute in minecraft:overworld run setblock -300 250 91 emerald_block',
    'execute in minecraft:overworld run setblock -298 250 91 iron_block',
    'execute in minecraft:overworld run setblock -300 250 120 copper_block',
    'execute in minecraft:overworld run setblock -298 250 120 lapis_block',
    'execute in minecraft:overworld run setblock -300 250 121 redstone_block',
    'execute in minecraft:overworld run setblock -298 250 121 coal_block',
    'execute in minecraft:overworld run setblock -280 249 90 stone',
    'execute in minecraft:overworld run setblock -280 249 120 stone',
    'scoreboard players set #pass mccmp 0',
    'scoreboard players set #fail mccmp 0',
    'scoreboard players set @a[tag=mcc_mp_a] mcc_rot 0',
    'scoreboard players set @a[tag=mcc_mp_b] mcc_rot 0',
    'scoreboard players set @a[tag=mcc_mp_a] mcc_mir 0',
    'scoreboard players set @a[tag=mcc_mp_b] mcc_mir 0'
)

aim('mcc_mp_a',-300,90); aim('mcc_mp_b',-300,120); both_trigger('pos1')
aim('mcc_mp_a',-298,91); aim('mcc_mp_b',-298,121); both_trigger('pos2')
check('independent selections',
      'score @a[tag=mcc_mp_a,limit=1] mcc_p1z matches 90',
      'score @a[tag=mcc_mp_b,limit=1] mcc_p1z matches 120',
      'score @a[tag=mcc_mp_a,limit=1] mcc_p2z matches 91',
      'score @a[tag=mcc_mp_b,limit=1] mcc_p2z matches 121')

# Same-tick Copy. Each player's private clipboard must stay distinct.
both_trigger('c')
check('independent copy clipboards',
      'score @a[tag=mcc_mp_a,limit=1] mcc_cliptype matches 1',
      'score @a[tag=mcc_mp_b,limit=1] mcc_cliptype matches 1')
step(
    'scoreboard players set #ok mccmp 0',
    'execute unless score @a[tag=mcc_mp_a,limit=1] mcc_id = @a[tag=mcc_mp_b,limit=1] mcc_id run scoreboard players set #ok mccmp 1',
    'execute if score #ok mccmp matches 1 run scoreboard players add #pass mccmp 1',
    'execute unless score #ok mccmp matches 1 run scoreboard players add #fail mccmp 1',
    'execute if score #ok mccmp matches 1 run tellraw @a[tag=mcc_mp_a] "MCCMP PASS unique mcc_id"',
    'execute if score #ok mccmp matches 1 run tellraw @a[tag=mcc_mp_b] "MCCMP PASS unique mcc_id"',
    'execute if score #ok mccmp matches 1 run say MCCMP_CHECK PASS unique_mcc_id',
    'execute unless score #ok mccmp matches 1 run say MCCMP_CHECK FAIL unique_mcc_id'
)

# Same-tick V now creates two shared-visible Blueprints, not real blocks.
aim('mcc_mp_a',-280,90,249); aim('mcc_mp_b',-280,120,249); both_trigger('v')
check('copy V keeps world untouched',
      'in minecraft:overworld if block -280 250 90 air',
      'in minecraft:overworld if block -278 250 91 air',
      'in minecraft:overworld if block -280 250 120 air',
      'in minecraft:overworld if block -278 250 121 air')
check('both blueprints visible',
      'in minecraft:overworld positioned -280 250 90 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..5,limit=1]',
      'in minecraft:overworld positioned -280 250 120 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..5,limit=1]')
both_trigger('previewclear')
check('both blueprints clear','in minecraft:overworld unless entity @e[type=minecraft:block_display,tag=mcc_blueprint]')

# Same-tick real Move + Undo + Redo, proving per-player Work/Undo/Redo separation.
both_trigger('up set 1')
check('simultaneous move',
      'in minecraft:overworld if block -300 251 90 gold_block',
      'in minecraft:overworld if block -300 251 120 copper_block')
step(
    'scoreboard players set #ok mccmp 1',
    'execute if score @a[tag=mcc_mp_a,limit=1] mcc_wbx = @a[tag=mcc_mp_b,limit=1] mcc_wbx run scoreboard players set #ok mccmp 0',
    'execute if score @a[tag=mcc_mp_a,limit=1] mcc_ubx = @a[tag=mcc_mp_b,limit=1] mcc_ubx run scoreboard players set #ok mccmp 0',
    'execute if score #ok mccmp matches 1 run scoreboard players add #pass mccmp 1',
    'execute unless score #ok mccmp matches 1 run scoreboard players add #fail mccmp 1',
    'execute if score #ok mccmp matches 1 run tellraw @a[tag=mcc_mp_a] "MCCMP PASS separate work/undo lanes"',
    'execute if score #ok mccmp matches 1 run tellraw @a[tag=mcc_mp_b] "MCCMP PASS separate work/undo lanes"',
    'execute if score #ok mccmp matches 1 run say MCCMP_CHECK PASS separate_work_undo_lanes',
    'execute unless score #ok mccmp matches 1 run say MCCMP_CHECK FAIL separate_work_undo_lanes'
)
both_trigger('undo')
check('simultaneous undo',
      'in minecraft:overworld if block -300 250 90 gold_block',
      'in minecraft:overworld if block -300 250 120 copper_block',
      'score @a[tag=mcc_mp_a,limit=1] mcc_redo matches 1',
      'score @a[tag=mcc_mp_b,limit=1] mcc_redo matches 1')
step(
    'scoreboard players set #ok mccmp 1',
    'execute if score @a[tag=mcc_mp_a,limit=1] mcc_rbx = @a[tag=mcc_mp_b,limit=1] mcc_rbx run scoreboard players set #ok mccmp 0',
    'execute if score #ok mccmp matches 1 run scoreboard players add #pass mccmp 1',
    'execute unless score #ok mccmp matches 1 run scoreboard players add #fail mccmp 1',
    'execute if score #ok mccmp matches 1 run tellraw @a[tag=mcc_mp_a] "MCCMP PASS separate redo lanes"',
    'execute if score #ok mccmp matches 1 run tellraw @a[tag=mcc_mp_b] "MCCMP PASS separate redo lanes"',
    'execute if score #ok mccmp matches 1 run say MCCMP_CHECK PASS separate_redo_lanes',
    'execute unless score #ok mccmp matches 1 run say MCCMP_CHECK FAIL separate_redo_lanes'
)
both_trigger('redo')
check('simultaneous redo',
      'in minecraft:overworld if block -300 251 90 gold_block',
      'in minecraft:overworld if block -300 251 120 copper_block')
both_trigger('undo')

# Same-tick direct real Rotate and independent Undo.
both_trigger('turnright')
check('simultaneous real rotate',
      'in minecraft:overworld if block -300 250 90 gold_block',
      'in minecraft:overworld if block -300 250 92 diamond_block',
      'in minecraft:overworld if block -300 250 120 copper_block',
      'in minecraft:overworld if block -300 250 122 lapis_block')
both_trigger('undo')
check('rotate undo isolated',
      'in minecraft:overworld if block -300 250 90 gold_block',
      'in minecraft:overworld if block -298 250 90 diamond_block',
      'in minecraft:overworld if block -300 250 120 copper_block',
      'in minecraft:overworld if block -298 250 120 lapis_block')

# X replaces Cut. Both players cut and paste their own material in the same ticks.
both_trigger('x')
check('simultaneous x',
      'in minecraft:overworld if block -300 250 90 air',
      'in minecraft:overworld if block -300 250 120 air',
      'score @a[tag=mcc_mp_a,limit=1] mcc_cliptype matches 2',
      'score @a[tag=mcc_mp_b,limit=1] mcc_cliptype matches 2')
aim('mcc_mp_a',-280,90,249); aim('mcc_mp_b',-280,120,249); both_trigger('v')
check('simultaneous x paste stays separate',
      'in minecraft:overworld if block -280 250 90 gold_block',
      'in minecraft:overworld if block -278 250 91 iron_block',
      'in minecraft:overworld if block -280 250 120 copper_block',
      'in minecraft:overworld if block -278 250 121 coal_block',
      'score @a[tag=mcc_mp_a,limit=1] mcc_clip matches 0',
      'score @a[tag=mcc_mp_b,limit=1] mcc_clip matches 0')

# Undo only A: B's world and history must remain untouched.
step('execute as @a[tag=mcc_mp_a,limit=1] run trigger undo')
check('A undo does not touch B',
      'in minecraft:overworld if block -280 250 90 air',
      'in minecraft:overworld if block -280 250 120 copper_block',
      'score @a[tag=mcc_mp_a,limit=1] mcc_redo matches 1',
      'score @a[tag=mcc_mp_b,limit=1] mcc_undo matches 1')
step('execute as @a[tag=mcc_mp_a,limit=1] run trigger redo')
check('A redo does not touch B',
      'in minecraft:overworld if block -280 250 90 gold_block',
      'in minecraft:overworld if block -280 250 120 copper_block')
step('execute as @a[tag=mcc_mp_b,limit=1] run trigger undo')
check('B independent undo',
      'in minecraft:overworld if block -280 250 90 gold_block',
      'in minecraft:overworld if block -280 250 120 air')

step(
    'tellraw @a[tag=mcc_mp_a] [{"text":"MCCMP DONE pass="},{"score":{"name":"#pass","objective":"mccmp"}},{"text":" fail="},{"score":{"name":"#fail","objective":"mccmp"}}]',
    'tellraw @a[tag=mcc_mp_b] [{"text":"MCCMP DONE pass="},{"score":{"name":"#pass","objective":"mccmp"}},{"text":" fail="},{"score":{"name":"#fail","objective":"mccmp"}}]',
    'execute if score #fail mccmp matches 0 run say MCCMP_RESULT PASS',
    'execute unless score #fail mccmp matches 0 run say MCCMP_RESULT FAIL'
)
for i,commands in enumerate(steps):
    if i+1<len(steps): commands.append(f'schedule function mcc_mp_test:step_{i+1} 10t replace')
    (F/f'step_{i}.mcfunction').write_text('\n'.join(commands)+'\n',encoding='utf-8')

(F/'join_a.mcfunction').write_text('tag @s remove mcc_mp_b\ntag @s add mcc_mp_a\ntellraw @s "MCCMP: registered as player A"\n',encoding='utf-8')
(F/'join_b.mcfunction').write_text('tag @s remove mcc_mp_a\ntag @s add mcc_mp_b\ntellraw @s "MCCMP: registered as player B"\n',encoding='utf-8')
(F/'start.mcfunction').write_text(
    'execute unless entity @a[tag=mcc_mp_a,limit=1] run tellraw @s "MCCMP: player A missing"\n'
    'execute unless entity @a[tag=mcc_mp_a,limit=1] run return fail\n'
    'execute unless entity @a[tag=mcc_mp_b,limit=1] run tellraw @s "MCCMP: player B missing"\n'
    'execute unless entity @a[tag=mcc_mp_b,limit=1] run return fail\n'
    'scoreboard objectives add mccmp dummy\n'
    'scoreboard players set #pass mccmp 0\n'
    'scoreboard players set #fail mccmp 0\n'
    'function mcc_mp_test:step_0\n',
    encoding='utf-8'
)
print(f'Built {len(steps)} v1.7 two-player steps at {OUT}')
