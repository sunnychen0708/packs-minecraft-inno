"""Build an opt-in real-player integration test datapack; never runs on load.

Run /function mcc_test:start in a BACKED UP disposable creative world.
Uses the real player's triggers and Minecraft tick dispatch, with delayed assertions.
The test owns x=-210..-170, y=248..260, z=80..110 in the overworld.
"""
import argparse
import json
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'dist/mcc-live-test')
OUT=parser.parse_args().output.resolve()
F = OUT / 'data/mcc_test/function'
F.mkdir(parents=True, exist_ok=True)
(OUT/'pack.mcmeta').write_text(json.dumps({'pack': {'description': 'Opt-in CopyPaste live regression', 'min_format':121,'max_format':121}}))
steps=[]
def step(*commands): steps.append(list(commands))
def check(label, conditions):
    step('scoreboard players set #ok mcct 0',
         f'execute {conditions} run scoreboard players set #ok mcct 1',
         f'execute if score #ok mcct matches 1 run tellraw @s "MCCT PASS {label}"',
         f'execute unless score #ok mcct matches 1 run tellraw @s "MCCT FAIL {label}"',
         'execute if score #ok mcct matches 1 run scoreboard players add #pass mcct 1',
         'execute unless score #ok mcct matches 1 run scoreboard players add #fail mcct 1')
def trigger(name): step('trigger '+name)
def aim(x,z,y=250): step(f'tp @s {x+.5} {y+4} {z+.5} 0 90')
def fixture():
    step('fill -205 249 85 -175 255 105 air',
         'setblock -200 250 90 gold_block',
         'setblock -198 250 90 diamond_block',
         'setblock -200 250 91 emerald_block',
         'setblock -198 250 91 iron_block',
         'setblock -180 249 90 stone',
         'scoreboard players set @s mcc_hasa 0')
def selection():
    aim(-200,90); trigger('pos1')
    aim(-198,91); trigger('pos2')
def target(): aim(-180,90,249)

check('upgrade defaults', 'if score @s mcc_rot matches 0..3 if score @s mcc_mir matches 0..2')
step('scoreboard players set @s mcc_rot 0','scoreboard players set @s mcc_mir 0','scoreboard players set @s mcc_mask 0')
fixture(); selection()
check('raycast pos1/pos2', 'if score @s mcc_p1x matches -200 if score @s mcc_p1y matches 250 if score @s mcc_p1z matches 90 if score @s mcc_p2x matches -198 if score @s mcc_p2z matches 91')
aim(-198,91); trigger('anchor')
check('anchor', 'if score @s mcc_hasa matches 1 if score @s mcc_anx matches -198 if score @s mcc_anz matches 91')
trigger('anchor set 2'); check('clear anchor','if score @s mcc_hasa matches 0')
trigger('c'); check('copy','if score @s mcc_ok matches 1 if score @s mcc_clip matches 1')
target(); trigger('v')
check('replace paste','if block -180 250 90 gold_block if block -178 250 90 diamond_block if block -180 250 91 emerald_block if block -179 250 90 air')
trigger('undo'); check('paste undo','if block -180 250 90 air if block -178 250 90 air')
step('fill -179 250 90 -178 250 91 stone')
trigger('mode'); target(); trigger('v')
check('masked paste','if block -180 250 90 gold_block if block -179 250 90 stone')
trigger('undo'); check('masked undo','if block -180 250 90 air if block -178 250 90 stone')
trigger('mode')
trigger('cut'); check('cut','if block -200 250 90 air if block -198 250 91 air')
trigger('undo'); check('cut undo','if block -200 250 90 gold_block if block -198 250 91 iron_block')
for name,delta in [('right',(-1,0,0)),('left',(1,0,0)),('up',(0,1,0)),('down',(0,-1,0)),('forward',(0,0,1)),('backward',(0,0,-1))]:
    step('tp @s -199 254 88 0 70')
    trigger(name+' set 1')
    dx,dy,dz=delta
    check('move '+name, f'if block {-200+dx} {250+dy} {90+dz} gold_block if block {-198+dx} {250+dy} {91+dz} iron_block if score @s mcc_p1x matches {-200+dx} if score @s mcc_p1y matches {250+dy} if score @s mcc_p1z matches {90+dz}')
    trigger('undo'); check('undo '+name,'if block -200 250 90 gold_block if block -198 250 91 iron_block if score @s mcc_p1x matches -200 if score @s mcc_p1y matches 250 if score @s mcc_p1z matches 90')
for name,cond in [('flipx','if block -198 250 90 gold_block if block -200 250 90 diamond_block'),('flipz','if block -200 250 91 gold_block if block -200 250 90 emerald_block')]:
    trigger(name); check(name,cond)
    trigger('undo'); check(name+' undo','if block -200 250 90 gold_block if block -198 250 91 iron_block')
# Independent oracle: mirror source axes first, then clockwise rotation.
for r in range(4):
    for m in range(3):
        step('fill -183 250 87 -177 250 93 air')
        trigger(f'rotate set {(r+1)*10}'); trigger(f'mirror set {(m+1)*10}')
        target(); trigger('v')
        cond=[]
        for x,z,block in [(0,0,'gold_block'),(2,0,'diamond_block'),(0,1,'emerald_block'),(2,1,'iron_block')]:
            if m==1:x=-x
            if m==2:z=-z
            for _ in range(r):x,z=-z,x
            cond.append(f'if block {-180+x} 250 {90+z} {block}')
        check(f'paste r{r} m{m}',' '.join(cond))
        trigger('undo'); check(f'undo r{r} m{m}','if block -180 250 90 air')
trigger('rotate set 10'); trigger('mirror set 10')
for value in (1,2,3,0):
    trigger('rotate'); check(f'rotate cycle {value}',f'if score @s mcc_rot matches {value}')
for value in (1,2,0):
    trigger('mirror'); check(f'mirror cycle {value}',f'if score @s mcc_mir matches {value}')
# Custom anchor and clipboard isolation: edit a different selection after Copy.
fixture(); selection(); aim(-198,91); trigger('anchor'); trigger('c')
target(); trigger('v')
check('custom anchor paste','if block -182 250 89 gold_block if block -180 250 90 iron_block')
trigger('undo')
trigger('up set 1')
check('move anchor','if score @s mcc_any matches 251')
trigger('undo'); check('undo anchor','if score @s mcc_any matches 250')
trigger('flipx'); check('flip anchor','if score @s mcc_anx matches -200')
trigger('undo'); check('undo flip anchor','if score @s mcc_anx matches -198')
trigger('anchor set 2'); trigger('c')
step('setblock -195 250 95 lapis_block')
aim(-195,95); trigger('pos1'); trigger('pos2')
trigger('up set 1'); trigger('undo'); trigger('flipx'); trigger('undo')
step('fill -183 250 87 -177 250 93 air'); target(); trigger('v')
check('clipboard survives other Move/Flip','if block -180 250 90 gold_block if block -178 250 91 iron_block')
trigger('undo'); selection()
trigger('right set 129')
check('reject move 129','if block -200 250 90 gold_block if score @s mcc_p1x matches -200')
# Test every source/destination dimension through the actual player's raycast.
for dimension in ('the_nether','the_end','overworld'):
    step(f'execute in minecraft:{dimension} run tp @s -180.5 254 90.5 0 90')
    step('setblock -180 249 90 stone','fill -183 250 87 -177 251 93 air')
    target(); trigger('v')
    check('cross dimension paste '+dimension,'if block -180 250 90 gold_block if block -178 250 91 iron_block')
    trigger('undo'); check('cross dimension undo '+dimension,'if block -180 250 90 air')
    fixture(); selection(); trigger('c')
    check('copy from '+dimension,'if score @s mcc_ok matches 1')
    trigger('up set 1'); check('move in '+dimension,'if block -200 251 90 gold_block')
    trigger('undo'); trigger('flipz')
    check('flip in '+dimension,'if block -200 250 91 gold_block')
    trigger('undo')
step('tellraw @s [{"text":"MCCT DONE pass="},{"score":{"name":"#pass","objective":"mcct"}},{"text":" fail="},{"score":{"name":"#fail","objective":"mcct"}}]')
for i,cmds in enumerate(steps):
    if i+1<len(steps):cmds.append(f'schedule function mcc_test:step_{i+1} 10t replace')
    (F/f'body_{i}.mcfunction').write_text('\n'.join(cmds)+'\n',encoding='utf-8')
    (F/f'step_{i}.mcfunction').write_text(f'execute as @a[tag=mcct_actor,limit=1] at @s run function mcc_test:body_{i}\n',encoding='utf-8')
(F/'start.mcfunction').write_text('scoreboard objectives add mcct dummy\nscoreboard players set #pass mcct 0\nscoreboard players set #fail mcct 0\ntag @s add mcct_actor\nfunction mcc_test:step_0\n',encoding='utf-8')
print(f'Built {len(steps)} live steps at {OUT}')

# A separate upgrade probe removes only the fields absent in v0.2, then lets a
# real game tick migrate them. Existing ID, clipboard and selection must survive.
(F/'upgrade.mcfunction').write_text('''scoreboard players operation #saved_id mcct = @s mcc_id
scoreboard players operation #saved_clip mcct = @s mcc_clip
scoreboard players operation #saved_x mcct = @s mcc_p1x
scoreboard players reset @s mcc_rot
scoreboard players reset @s mcc_mir
scoreboard players reset @s mcc_usel
schedule function mcc_test:upgrade_check 10t replace
''',encoding='utf-8')
(F/'upgrade_check.mcfunction').write_text('execute as @a[tag=mcct_actor,limit=1] at @s run function mcc_test:upgrade_body\n',encoding='utf-8')
(F/'upgrade_body.mcfunction').write_text('''scoreboard players set #upgrade mcct 0
execute if score @s mcc_rot matches 0 if score @s mcc_mir matches 0 if score @s mcc_usel matches 0 if score @s mcc_id = #saved_id mcct if score @s mcc_clip = #saved_clip mcct if score @s mcc_p1x = #saved_x mcct run scoreboard players set #upgrade mcct 1
execute if score #upgrade mcct matches 1 run tellraw @s "MCCT PASS missing-state migration preserves player data"
execute unless score #upgrade mcct matches 1 run tellraw @s "MCCT FAIL missing-state migration preserves player data"
function mcc:panel
''',encoding='utf-8')

