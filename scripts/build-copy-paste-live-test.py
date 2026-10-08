"""Build an opt-in real-player v1.3 integration test datapack; never runs on load.

Run /function mcc_test:start in a BACKED UP disposable creative world.
Uses the real player's triggers and Minecraft tick dispatch, with delayed assertions.
The test owns x=-210..-160, y=248..260, z=80..120 in each vanilla dimension.
"""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import mcc_house as house

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'dist/mcc-live-test')
OUT=parser.parse_args().output.resolve()
F=OUT/'data/mcc_test/function'
F.mkdir(parents=True,exist_ok=True)
(OUT/'pack.mcmeta').write_text(json.dumps({'pack':{'description':'Opt-in CopyPaste v1.3 live regression','min_format':121,'max_format':121}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

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

# The fixtures write blocks before the player is necessarily nearby (and the
# Nether section prepares its target before teleporting there). Force-load the
# owned areas first and let them load, otherwise setblock/fill silently fail and
# a raycast can hit unrelated terrain such as the Nether roof.
step('execute in minecraft:overworld run forceload add -210 80 -160 120',
     'execute in minecraft:the_nether run forceload add -210 80 -160 120',
     'execute in minecraft:overworld run tp @s -179.5 254 90.5 0 90')
for _ in range(6): step()
reset_transform()
fixture(); selection()
check('overworld fixture ready','in minecraft:overworld if block -200 250 90 gold_block if block -180 249 90 stone')
check('raycast selection','if score @s mcc_p1x matches -200 if score @s mcc_p1y matches 250 if score @s mcc_p1z matches 90 if score @s mcc_p2x matches -198 if score @s mcc_p2z matches 91')

# v1.3 selection contract: reselecting Pos1/Pos2 changes the next Copy, while
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

# v1.3 Anchor lifecycle: external pivots are valid, Clear Anchor works through the
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

# v1.3 material-backed Build through the real player trigger path.
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

# Cut is X. It edits real blocks; Undo invalidates the live Cut clipboard and
# Redo rebuilds the original one (v1.3).
trigger('x')
check('x cuts real source','in minecraft:overworld if block -200 250 90 air if block -198 250 91 air if score @s mcc_cliptype matches 2')
trigger('undo')
check('x undo invalidates cut clipboard','in minecraft:overworld if block -200 250 90 gold_block if block -198 250 91 iron_block if score @s mcc_redo matches 1 if score @s mcc_clip matches 0')
trigger('redo')
check('x redo rebuilds cut clipboard','in minecraft:overworld if block -200 250 90 air if block -198 250 91 air if score @s mcc_undo matches 1 if score @s mcc_clip matches 1 if score @s mcc_cliptype matches 2')
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
check('nether target ready','in minecraft:the_nether if block -180 249 90 stone if block -180 250 90 air')
target(-180,90,'the_nether'); trigger('v')
check('nether raycast hits target','if score @s mcc_dstd matches 2 if score @s mcc_dstx matches -180 if score @s mcc_dsty matches 250 if score @s mcc_dstz matches 90')
check('nether blueprint no real blocks','in minecraft:the_nether if block -180 250 90 air if block -178 250 91 air')
check('nether blueprint display','in minecraft:the_nether positioned -180 250 90 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..5,limit=1]')
trigger('previewclear')

# Cross-dimension Cut paste still moves real blocks and consumes the clipboard.
step('execute in minecraft:overworld run tp @s -199.5 254 88.5 0 70')
selection('overworld'); trigger('x')
check('nether target still ready','in minecraft:the_nether if block -180 249 90 stone if block -180 250 90 air')
target(-180,90,'the_nether'); trigger('v')
check('cross-dimension x paste','in minecraft:the_nether if block -180 250 90 gold_block if block -178 250 91 iron_block if score @s mcc_clip matches 0')
trigger('undo')
check('cross-dimension paste undo','in minecraft:the_nether if block -180 250 90 air if block -178 250 91 air')
trigger('redo')
check('cross-dimension paste redo','in minecraft:the_nether if block -180 250 90 gold_block if block -178 250 91 iron_block')

# ---- Real Warehouse + 3D house through the player's triggers and real ticks ----
# Does not assume default classification: every Warehouse code gets a box, one
# custom player rule is applied, and stock is always counted through the
# Warehouse API across all boxes. The world's own registrations and rules are
# backed up first and restored at the end.
OW='in minecraft:overworld'
CODES=['00']+[f'{r}{s}' for r in range(1,7) for s in range(10)]
BOX={}
for i,code in enumerate(CODES):
    BOX[code]=(-209+2*(i%25), 111+3*(i//25))
def box_cmds():
    out=[]
    for code,(x,z) in BOX.items():
        out += [f'execute in minecraft:overworld run setblock {x} 249 {z} chest',
                f'execute in minecraft:overworld run setblock {x} 249 {z+1} chest',
                f'data modify storage warehouse:chests c{code} set value {{registered:1b,valid:1b,dimension:"minecraft:overworld",a_x:{x},a_y:249,a_z:{z},b_x:{x},b_y:249,b_z:{z+1}}}']
    return out
def all_boxes_empty_of(item):
    return ' '.join(f'unless data block {x} 249 {z} Items[{{id:"{item}"}}] unless data block {x} 249 {z+1} Items[{{id:"{item}"}}]' for x,z in BOX.values())
def stock_is(label_prefix, expect):
    for item,count in house.BOM.items():
        n=expect if expect is not None else count
        step(f'function warehouse:api/count_item {{item_id:"{item}"}}')
        check(f'{label_prefix} {item.split(":")[1]} = {n}',f'if data storage warehouse:api result{{ok:1b,complete:1b,available:{n}}}')
step('kill @e[type=minecraft:item]',
     'data modify storage mcc_test:backup chests set from storage warehouse:chests',
     'data modify storage mcc_test:backup overrides set from storage warehouse:rules overrides',
     'execute in minecraft:overworld run fill -210 249 80 -160 255 120 air',
     'execute in minecraft:overworld run fill -210 248 80 -160 248 120 stone',
     'scoreboard players set #enabled wh_sys 1',
     # Custom player rule: planks go to box 11 instead of the default box.
     'data modify storage warehouse:rules overrides."minecraft:oak_planks" set value 11')
step(*box_cmds())
x00,z00=BOX['00']
step(f'execute in minecraft:overworld run data modify block {x00} 249 {z00} Items set value [{",".join(house.stock_items())}]')
for _ in range(12): step()  # real Warehouse ticks sort the entry chest
check('warehouse sorted all house materials out of entry',f'{OW} unless data block {x00} 249 {z00} Items[0] unless data block {x00} 249 {z00+1} Items[0]')
x11,z11=BOX['11']
check('custom rule: planks sorted into box 11',f'{OW} if data block {x11} 249 {z11} Items[{{id:"minecraft:oak_planks",count:{house.BOM["minecraft:oak_planks"]}}}]')
stock_is('warehouse stock',None)

# House plus two temporary corner markers visible from above (selection -206..-200, 250..253, 99..105).
step(*house.place_commands(-205,250,100,'overworld'),
     'execute in minecraft:overworld run setblock -206 250 99 minecraft:white_wool',
     'execute in minecraft:overworld run setblock -200 253 105 minecraft:white_wool',
     'execute in minecraft:overworld run setblock -185 249 99 stone',
     'scoreboard players set @s mcc_rot 0','scoreboard players set @s mcc_mir 0','scoreboard players set @s mcc_mask 0')
check('3d house fixture ready',f'{OW} if block -203 252 100 minecraft:oak_door[half=upper] if block -203 252 102 minecraft:lantern[hanging=true] if block -204 252 101 minecraft:wall_torch')
aim(-206,99,250); trigger('pos1')
aim(-200,105,253); trigger('pos2')
check('3d selection by raycast','if score @s mcc_p1x matches -206 if score @s mcc_p1y matches 250 if score @s mcc_p1z matches 99 if score @s mcc_p2x matches -200 if score @s mcc_p2y matches 253 if score @s mcc_p2z matches 105')
step('execute in minecraft:overworld run setblock -206 250 99 air',
     'execute in minecraft:overworld run setblock -200 253 105 air')
trigger('c')
target(-185,99); trigger('v')
for _ in range(4): step()
check('3d blueprint ready, no real blocks',f'{OW} if score @s mcc_bpactive matches 1 if score @s mcc_bpready matches 1 if score @s mcc_bpbad matches 0 if block -184 250 100 air if block -182 253 100 air')
trigger('build')
for _ in range(6): step()
check('3d build exact copy',f'{OW} if blocks -206 250 99 -200 253 105 -185 250 99 all')
check('3d build no item drops','unless entity @e[type=minecraft:item]')
stock_is('after build',0)
trigger('undo')
check('3d build undo world',f'{OW} if block -184 250 100 air if block -183 251 99 air if block -182 253 100 air')
for _ in range(12): step()
check('undo refunds sorted back out of entry',f'{OW} unless data block {x00} 249 {z00} Items[0] unless data block {x00} 249 {z00+1} Items[0]')
stock_is('after undo',None)
trigger('redo')
for _ in range(6): step()
check('3d redo exact copy',f'{OW} if blocks -206 250 99 -200 253 105 -185 250 99 all')
stock_is('after redo',0)
trigger('undo')
for _ in range(12): step()

# Pick: look at a stone brick block and take one stack from the Warehouse.
step('clear @s minecraft:stone_bricks','execute in minecraft:overworld run setblock -195 249 108 minecraft:stone_bricks')
aim(-195,108,249)
trigger('pick')
check('pick gives warehouse stone bricks',f'if items entity @s container.* minecraft:stone_bricks {OW} {all_boxes_empty_of("minecraft:stone_bricks")}')
step('clear @s minecraft:stone_bricks',
     *[f'data modify storage warehouse:chests c{code} set from storage mcc_test:backup chests.c{code}' for code in CODES],
     'data remove storage warehouse:rules overrides',
     'data modify storage warehouse:rules overrides set from storage mcc_test:backup overrides')
step('execute in minecraft:overworld run forceload remove -210 80 -160 120',
     'execute in minecraft:the_nether run forceload remove -210 80 -160 120')
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
print(f'Built {len(steps)} v1.3 live steps at {OUT}')
