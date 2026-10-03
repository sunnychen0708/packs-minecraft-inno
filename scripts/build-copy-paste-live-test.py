"""Build an opt-in real-player v1.2.1 integration test datapack; never runs on load.

Run /function mcc_test:start in a BACKED UP disposable creative world.
Uses the real player's triggers and Minecraft tick dispatch, with delayed assertions.
The test owns x=-210..-160, y=248..260, z=80..120 in each vanilla dimension.
"""
import argparse
import json
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'dist/mcc-live-test')
OUT=parser.parse_args().output.resolve()
F=OUT/'data/mcc_test/function'
F.mkdir(parents=True,exist_ok=True)
(OUT/'pack.mcmeta').write_text(json.dumps({'pack':{'description':'Opt-in CopyPaste v1.2.1 live regression','min_format':121,'max_format':121}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

steps=[]
def step(*commands): steps.append(list(commands))
def trigger(name): step('trigger '+name)
def aim(x,z,y=250,dim='overworld'): step(f'execute in minecraft:{dim} run tp @s {x+.5} {y+4} {z+.5} 0 90')
def check(label,conditions):
    step('scoreboard players set #ok mcct 0',
         f'execute {conditions} run scoreboard players set #ok mcct 1',
         f'execute if score #ok mcct matches 1 run tellraw @s "MCCT PASS {label}"',
         f'execute unless score #ok mcct matches 1 run tellraw @s "MCCT FAIL {label}"',
         'execute if score #ok mcct matches 1 run scoreboard players add #pass mcct 1',
         'execute unless score #ok mcct matches 1 run scoreboard players add #fail mcct 1')
def fixture(dim='overworld'):
    step(f'execute in minecraft:{dim} run fill -205 249 85 -160 255 120 air',
         f'execute in minecraft:{dim} run setblock -200 250 90 gold_block',
         f'execute in minecraft:{dim} run setblock -198 250 90 diamond_block',
         f'execute in minecraft:{dim} run setblock -200 250 91 emerald_block',
         f'execute in minecraft:{dim} run setblock -198 250 91 iron_block',
         f'execute in minecraft:{dim} run setblock -200 250 105 copper_block',
         f'execute in minecraft:{dim} run setblock -198 250 105 lapis_block',
         f'execute in minecraft:{dim} run setblock -200 250 106 redstone_block',
         f'execute in minecraft:{dim} run setblock -198 250 106 coal_block',
         f'execute in minecraft:{dim} run setblock -180 249 90 stone',
         f'execute in minecraft:{dim} run setblock -170 249 105 stone',
         f'execute in minecraft:{dim} run setblock -165 249 105 stone',
         'scoreboard players set @s mcc_hasa 0')
def selection(dim='overworld'):
    aim(-200,90,250,dim); trigger('pos1')
    aim(-198,91,250,dim); trigger('pos2')
def selection2(dim='overworld'):
    aim(-200,105,250,dim); trigger('pos1')
    aim(-198,106,250,dim); trigger('pos2')
def target(x=-180,z=90,dim='overworld'): aim(x,z,249,dim)
def reset_transform():
    step('scoreboard players set @s mcc_rot 0',
         'scoreboard players set @s mcc_mir 0',
         'scoreboard players set @s mcc_mask 0')

reset_transform()
fixture(); selection()
check('raycast selection','if score @s mcc_p1x matches -200 if score @s mcc_p1y matches 250 if score @s mcc_p1z matches 90 if score @s mcc_p2x matches -198 if score @s mcc_p2z matches 91')

# v1.2.1 selection contract: reselecting Pos1/Pos2 changes the next Copy, while
# doing another Copy without new Pos keeps using the current selection.
selection2(); trigger('c')
target(-170,105); trigger('v')
check('reselected copy uses new region','in minecraft:overworld positioned -170 250 105 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:copper_block"},limit=1]')
trigger('previewclear')
trigger('c')
target(-165,105); trigger('v')
check('selection persists without new pos','in minecraft:overworld positioned -165 250 105 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:copper_block"},limit=1]')
trigger('previewclear')
selection()

# v1.2.1 Anchor lifecycle: external pivots are valid, Clear Anchor works through the
# real trigger/tick path, and reselecting either endpoint drops a stale custom Anchor.
step('execute in minecraft:overworld run setblock -190 250 100 stone')
aim(-190,100); trigger('anchor')
check('external anchor selected','if score @s mcc_hasa matches 1 if score @s mcc_anx matches -190 if score @s mcc_any matches 250 if score @s mcc_anz matches 100')
trigger('anchor set 2')
check('clear anchor trigger','if score @s mcc_hasa matches 0')
aim(-190,100); trigger('anchor')
aim(-200,90); trigger('pos1')
check('pos1 reselection clears stale anchor','if score @s mcc_hasa matches 0 if score @s mcc_p1x matches -200 if score @s mcc_p1z matches 90')
aim(-190,100); trigger('anchor')
trigger('rotate90')
check('external anchor rotate real','in minecraft:overworld if block -180 250 90 gold_block if block -180 250 92 diamond_block if block -181 250 90 emerald_block if block -181 250 92 iron_block if score @s mcc_anx matches -190 if score @s mcc_anz matches 100')
trigger('undo')
check('external anchor rotate undo','in minecraft:overworld if block -200 250 90 gold_block if block -198 250 91 iron_block')
trigger('anchor set 2')

# Default Anchor must be Pos1 even when Pos1 is not the selected cuboid minimum.
aim(-198,91); trigger('pos1')
aim(-200,90); trigger('pos2')
trigger('c')
target(); trigger('v')
check('default pos1 anchor exact','in minecraft:overworld positioned -180 250 90 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:iron_block"},limit=1]')
check('default pos1 anchor offset','in minecraft:overworld positioned -182 250 89 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.1,nbt={block_state:"minecraft:gold_block"},limit=1]')
trigger('previewclear')

# Restore the ordinary selection used by the rest of the live suite.
fixture(); selection()

# Copy creates only a shared visual Blueprint; target world stays untouched.
trigger('c')
check('copy type','if score @s mcc_clip matches 1 if score @s mcc_cliptype matches 1')
target(); trigger('v')
check('copy V does not create blocks','in minecraft:overworld if block -180 250 90 air if block -178 250 91 air')
check('copy V creates blueprint','in minecraft:overworld positioned -180 250 90 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..5,limit=1]')
trigger('previewclear')
check('preview clear','in minecraft:overworld unless entity @e[type=minecraft:block_display,tag=mcc_blueprint]')

# Copy/Blueprint is not a real world edit and must not consume its Clipboard.
check('copy clipboard persists','if score @s mcc_clip matches 1 if score @s mcc_cliptype matches 1')

# v1.2.1 material-backed Build through the real player trigger path.
# The harness expects the Warehouse datapack to be installed alongside Copy/Paste.
target(); trigger('v')
step(
    'execute in minecraft:overworld run setblock -170 250 110 chest',
    'execute in minecraft:overworld run setblock -169 250 110 chest',
    'execute in minecraft:overworld run data modify block -170 250 110 Items set value [{Slot:0b,id:"minecraft:gold_block",count:1},{Slot:1b,id:"minecraft:diamond_block",count:1},{Slot:2b,id:"minecraft:emerald_block",count:1},{Slot:3b,id:"minecraft:iron_block",count:1}]',
    'data modify storage warehouse:chests c11 set value {registered:1b,valid:1b,dimension:"minecraft:overworld",a_x:-170,a_y:250,a_z:110,b_x:-169,b_y:250,b_z:110}'
)
trigger('build')
check('material build real','in minecraft:overworld if block -180 250 90 gold_block if block -178 250 90 diamond_block if block -180 250 91 emerald_block if block -178 250 91 iron_block if score @s mcc_bpactive matches 0')
check('material build consumed warehouse stock','in minecraft:overworld unless data block -170 250 110 Items[0]')

# Reset owned test area before the Cut sequence.
fixture(); selection()

# Cut is now X. It edits real blocks and supports Undo/Redo toggling.
trigger('x')
check('x cuts real source','in minecraft:overworld if block -200 250 90 air if block -198 250 91 air if score @s mcc_cliptype matches 2')
trigger('undo')
check('x undo','in minecraft:overworld if block -200 250 90 gold_block if block -198 250 91 iron_block if score @s mcc_redo matches 1')
trigger('redo')
check('x redo','in minecraft:overworld if block -200 250 90 air if block -198 250 91 air if score @s mcc_undo matches 1')
trigger('undo')
check('x undo again','in minecraft:overworld if block -200 250 90 gold_block if block -198 250 91 iron_block')

# Cut + V is a real move and consumes the Cut clipboard after one successful paste.
trigger('x'); target(); trigger('v')
check('x V real paste','in minecraft:overworld if block -180 250 90 gold_block if block -178 250 90 diamond_block if block -180 250 91 emerald_block if block -178 250 91 iron_block')
check('x V consumes clipboard','if score @s mcc_clip matches 0 if score @s mcc_cliptype matches 0')
target(-170,90); trigger('v')
check('consumed x cannot duplicate','in minecraft:overworld if block -170 250 90 air if block -168 250 91 air')

# Undo/Redo of the most recent real paste toggles destination state.
trigger('undo')
check('paste undo','in minecraft:overworld if block -180 250 90 air if block -178 250 91 air')
trigger('redo')
check('paste redo','in minecraft:overworld if block -180 250 90 gold_block if block -178 250 91 iron_block')

# Restore fixture and verify Move + Z/Y behavior.
fixture(); selection()
step('tp @s -199 254 88 0 70')
trigger('up set 1')
check('move real blocks','in minecraft:overworld if block -200 251 90 gold_block if block -198 251 91 iron_block if score @s mcc_p1y matches 251')
trigger('undo')
check('move undo','in minecraft:overworld if block -200 250 90 gold_block if score @s mcc_p1y matches 250')
trigger('redo')
check('move redo','in minecraft:overworld if block -200 251 90 gold_block if score @s mcc_p1y matches 251')
trigger('undo')

# New real edit after Undo invalidates Redo.
trigger('up set 1'); trigger('undo')
check('redo exists after undo','if score @s mcc_redo matches 1')
trigger('flipx')
check('new real edit invalidates redo','if score @s mcc_redo matches 0')
trigger('undo')

# Copy/Blueprint must NOT invalidate Redo because it does not change world blocks.
trigger('up set 1'); trigger('undo')
trigger('c'); target(-170,90); trigger('v')
check('blueprint preserves redo','if score @s mcc_redo matches 1')
trigger('previewclear'); trigger('redo'); trigger('undo')

# Flip remains a direct real edit and is Redo-able.
trigger('flipx')
check('flipx real','in minecraft:overworld if block -198 250 90 gold_block if block -200 250 90 diamond_block')
trigger('undo')
check('flip undo','in minecraft:overworld if block -200 250 90 gold_block if block -198 250 90 diamond_block')
trigger('redo')
check('flip redo','in minecraft:overworld if block -198 250 90 gold_block if block -200 250 90 diamond_block')
trigger('undo')

# Direct real Rotate about Pos1.
trigger('rotate90')
check('rotate90 real','in minecraft:overworld if block -200 250 90 gold_block if block -200 250 92 diamond_block if block -201 250 90 emerald_block if block -201 250 92 iron_block')
trigger('undo')
check('rotate90 undo','in minecraft:overworld if block -200 250 90 gold_block if block -198 250 90 diamond_block if block -200 250 91 emerald_block')
trigger('redo')
check('rotate90 redo','in minecraft:overworld if block -200 250 92 diamond_block if block -201 250 90 emerald_block')
trigger('undo')

trigger('rotate180')
check('rotate180 real','in minecraft:overworld if block -200 250 90 gold_block if block -202 250 90 diamond_block if block -200 250 89 emerald_block if block -202 250 89 iron_block')
trigger('undo')
trigger('rotate270')
check('rotate270 real','in minecraft:overworld if block -200 250 90 gold_block if block -200 250 88 diamond_block if block -199 250 90 emerald_block if block -199 250 88 iron_block')
trigger('undo')

# Rotated Copy Blueprint: still visual only.
trigger('c')
trigger('rotate set 20')
target(); trigger('v')
check('rotated blueprint no real blocks','in minecraft:overworld if block -180 250 90 air if block -180 250 92 air if block -181 250 90 air')
check('rotated blueprint display','in minecraft:overworld positioned -180 250 90 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..6,limit=1]')
trigger('previewclear')
trigger('rotate set 10')

# Cross-dimension Copy Blueprint: no real blocks in target dimension, display exists there.
fixture('overworld'); selection('overworld'); trigger('c')
step('execute in minecraft:the_nether run fill -185 249 85 -170 255 100 air',
     'execute in minecraft:the_nether run setblock -180 249 90 stone')
target(-180,90,'the_nether'); trigger('v')
check('nether blueprint no real blocks','in minecraft:the_nether if block -180 250 90 air if block -178 250 91 air')
check('nether blueprint display','in minecraft:the_nether positioned -180 250 90 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..5,limit=1]')
trigger('previewclear')

# Cross-dimension Cut paste still moves real blocks and consumes the clipboard.
step('execute in minecraft:overworld run tp @s -199.5 254 88.5 0 70')
selection('overworld'); trigger('x')
target(-180,90,'the_nether'); trigger('v')
check('cross-dimension x paste','in minecraft:the_nether if block -180 250 90 gold_block if block -178 250 91 iron_block if score @s mcc_clip matches 0')
trigger('undo')
check('cross-dimension paste undo','in minecraft:the_nether if block -180 250 90 air if block -178 250 91 air')
trigger('redo')
check('cross-dimension paste redo','in minecraft:the_nether if block -180 250 90 gold_block if block -178 250 91 iron_block')

step('tellraw @s [{"text":"MCCT DONE pass="},{"score":{"name":"#pass","objective":"mcct"}},{"text":" fail="},{"score":{"name":"#fail","objective":"mcct"}}]')
for i,cmds in enumerate(steps):
    if i+1<len(steps):
        cmds.append(f'schedule function mcc_test:step_{i+1} 10t replace')
    (F/f'body_{i}.mcfunction').write_text('\n'.join(cmds)+'\n',encoding='utf-8')
    (F/f'step_{i}.mcfunction').write_text(f'execute as @a[tag=mcct_actor,limit=1] at @s run function mcc_test:body_{i}\n',encoding='utf-8')
(F/'start.mcfunction').write_text(
    'scoreboard objectives add mcct dummy\n'
    'scoreboard players set #pass mcct 0\n'
    'scoreboard players set #fail mcct 0\n'
    'tag @s add mcct_actor\n'
    'function mcc_test:step_0\n',
    encoding='utf-8'
)
print(f'Built {len(steps)} v1.2.1 live steps at {OUT}')
