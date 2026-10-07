"""Build an opt-in two-player v1.7 Copy/Paste regression datapack that works on the 3D test house.

Player A: /function mcc_mp_test:join_a
Player B: /function mcc_mp_test:join_b
Then either player: /function mcc_mp_test:start
Afterwards (pass, fail or timeout): /function mcc_mp_test:cleanup

Both players work at the same time, each on their own copy of the house from
scripts/mcc_house.py (doors, slabs, stairs, log axes, panes, torch, lanterns,
chest). Every step that changes the world compares all 100 cells of the house
box block-state-exact, and prints MCCMP_DIFF for every wrong cell. The players
select with real /trigger pos1/pos2 rays, Copy -> V -> Build with materials
from their own inventory, Move/Undo/Redo, Rotate, Flip and Cut/Paste.

Materials: the test gives each player exactly one house BOM, the build and the
undo refund are checked against the player's own baseline count, and the extra
items are cleared again, so the player inventories end where they started.

The generated test never runs on load and is intended only for innotest.
"""
from pathlib import Path
import json
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT/'scripts/real-client'))
import mcc_house as house
import xform

OUT=ROOT/'dist/mcc-multiplayer-test'
if OUT.exists(): shutil.rmtree(OUT)
F=OUT/'data/mcc_mp_test/function'
F.mkdir(parents=True,exist_ok=True)
(OUT/'pack.mcmeta').write_text(json.dumps({
    'pack':{'description':'Opt-in CopyPaste v1.7 two-player 3D house regression','min_format':121,'max_format':121}
},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

OW='in minecraft:overworld'
SX,SY,SZ=house.SIZE
Y=250
# Test area. Everything the test places stays inside it; cleanup clears it.
AREA=(-306,245,84,-266,259,126)
# Per player: source house S (with an air gap below for the pos1 ray), target T on a stone floor.
P={
    'a':{'tag':'mcc_mp_a','S':(-300,Y,88),'T':(-288,Y,88)},
    'b':{'tag':'mcc_mp_b','S':(-300,Y,113),'T':(-288,Y,113)},
}
REF=(-276,Y,100)      # untouched reference house
AIRREF=(-270,Y,120)   # untouched air box of the same size

def sel(p): return f'@a[tag={P[p]["tag"]},limit=1]'
def box(o): return f'{o[0]} {o[1]} {o[2]} {o[0]+SX-1} {o[1]+SY-1} {o[2]+SZ-1}'
def at(o): return f'{o[0]} {o[1]} {o[2]}'

steps=[]
def step(*commands): steps.append(('cmd',list(commands)))
def wait(label,conditions,tries=80):
    """Poll every 5 ticks until all conditions hold; count a FAIL after `tries` polls."""
    steps.append(('wait',label,list(conditions),tries))
def both_trigger(a):
    step(*[f'execute as {sel(p)} run trigger {a}' for p in P])
def aim(p,x,y,z,pitch):
    return f'execute {OW} run tp {sel(p)} {x+.5} {y} {z+.5} 0 {pitch}'
# Facing south (yaw 0). The ray starts at the eyes, 1.62 above the feet.
def aim_down(p,x,y,z): return aim(p,x,y+5,z,90)     # look straight down at cell (x,y,z) from above
def aim_up(p,x,y,z): return aim(p,x,y-4,z,-90)      # look straight up at cell (x,y,z) from below

def chained(cond):
    """Execute-chain conditions ("in ... if ...") are used as is; bare ones ("score ...") get "if"."""
    return cond if cond.startswith(('in ','positioned ')) else 'if '+cond

def negate(cond):
    if not cond.startswith(('in ','positioned ')): return 'unless '+cond
    for a,b in ((' if ',' unless '),(' unless ',' if ')):
        if a in cond:
            return cond.replace(a,b,1)
    raise ValueError(f'cannot negate execute condition: {cond}')

def check(label,*conditions):
    """Each condition is an execute-subcommand string, or (condition, diff text) to report a failing cell."""
    cmds=['scoreboard players set #ok mccmp 1']
    for c in conditions:
        cond,diff=(c if isinstance(c,tuple) else (c,None))
        cmds.append(f'execute {negate(cond)} run scoreboard players set #ok mccmp 0')
        if diff:
            cmds.append(f'execute {negate(cond)} run say MCCMP_DIFF {label.replace(" ","_")} {diff}')
    tag=label.replace(' ','_')
    cmds += [
        *[f'execute if score #ok mccmp matches 1 run tellraw @a[tag={P[p]["tag"]}] "MCCMP PASS {label}"' for p in P],
        *[f'execute unless score #ok mccmp matches 1 run tellraw @a[tag={P[p]["tag"]}] "MCCMP FAIL {label}"' for p in P],
        f'execute if score #ok mccmp matches 1 run say MCCMP_CHECK PASS {tag}',
        f'execute unless score #ok mccmp matches 1 run say MCCMP_CHECK FAIL {tag}',
        'execute if score #ok mccmp matches 1 run scoreboard players add #pass mccmp 1',
        'execute unless score #ok mccmp matches 1 run scoreboard players add #fail mccmp 1',
    ]
    step(*cmds)

# ---- expected house states -------------------------------------------------
BLOCK_AT={(x,y,z):b for x,y,z,b in house.BLOCKS}
CELLS=[(x,y,z) for y in range(SY) for x in range(SX) for z in range(SZ)]

def house_cells(origin,transform=None):
    """(world cell, expected state) for every cell of the house box after a transform.

    transform: None, 'r90' (clockwise around the origin cell, like Rotate with Pos1 as pivot)
    or 'mx' (mirror X inside the box, like Flip left/right while facing south)."""
    out=[]
    for x,y,z in CELLS:
        state=BLOCK_AT.get((x,y,z),'minecraft:air')
        if transform=='r90':
            dx,dz=xform.rot_off(x,z,1)
            state=xform.rotate_state(state,1)
        elif transform=='mx':
            dx,dz=SX-1-x,z
            state=xform.mirror_state(state,'x')
        else:
            dx,dz=x,z
        out.append(((origin[0]+dx,origin[1]+y,origin[2]+dz),(x,y,z),state))
    return out

def house_conds(origin,transform=None):
    conds=[]
    for (wx,wy,wz),rel,state in house_cells(origin,transform):
        conds.append((f'{OW} if block {wx} {wy} {wz} {state}',
                       f'{wx} {wy} {wz} (house {rel[0]} {rel[1]} {rel[2]}) expected {state}'))
    return conds

def exact_house(o):
    """Block-state-exact per cell (with diff report) plus a whole-box compare against the reference house."""
    return [*house_conds(o),f'{OW} if blocks {box(REF)} {at(o)} all']

def air_box(o,dx=SX,dy=SY,dz=SZ):
    return f'{OW} if blocks {AIRREF[0]} {AIRREF[1]} {AIRREF[2]} {AIRREF[0]+dx-1} {AIRREF[1]+dy-1} {AIRREF[2]+dz-1} {at(o)} all'

def no_items():
    x1,y1,z1,x2,y2,z2=AREA
    return f'{OW} unless entity @e[type=minecraft:item,x={x1},y={y1},z={z1},dx={x2-x1},dy={y2-y1},dz={z2-z1}]'

def lane_differs(label,obj):
    step('scoreboard players set #ok mccmp 1',
         f'execute if score {sel("a")} {obj} = {sel("b")} {obj} run scoreboard players set #ok mccmp 0',
         'execute if score #ok mccmp matches 1 run scoreboard players add #pass mccmp 1',
         'execute unless score #ok mccmp matches 1 run scoreboard players add #fail mccmp 1',
         f'execute if score #ok mccmp matches 1 run say MCCMP_CHECK PASS {label}',
         f'execute unless score #ok mccmp matches 1 run say MCCMP_CHECK FAIL {label}')

ITEMS=list(house.BOM.items())
def count_cmds(prefix):
    """Store each player's inventory count of every BOM item in #<p><prefix><i>."""
    return [f'execute store result score #{p}{prefix}{i} mccmp run clear {sel(p)} {item} 0'
            for p in P for i,(item,_) in enumerate(ITEMS)]
def counts_equal(extra):
    """Current count == baseline + extra*BOM for both players."""
    conds=[]
    cmds=count_cmds('n')
    for p in P:
        for i,(item,n) in enumerate(ITEMS):
            cmds.append(f'scoreboard players operation #{p}e{i} mccmp = #{p}base{i} mccmp')
            cmds.append(f'scoreboard players add #{p}e{i} mccmp {extra*n}')
            conds.append((f'score #{p}n{i} mccmp = #{p}e{i} mccmp',
                          f'player {p.upper()} {item} count wrong (expected baseline+{extra*n})'))
    step(*cmds)
    return conds

# ---- fixture ---------------------------------------------------------------
x1,y1,z1,x2,y2,z2=AREA
setup=[f'execute {OW} run fill {x1} {y1} {z1} {x2} {y2} {z2} air',
       f'execute {OW} run kill @e[type=minecraft:item,x={x1},y={y1},z={z1},dx={x2-x1},dy={y2-y1},dz={z2-z1}]']
setup+=house.place_commands(*REF,'overworld')
for p in P:
    setup+=house.place_commands(*P[p]['S'],'overworld')
    t=P[p]['T']
    setup.append(f'execute {OW} run fill {t[0]} {t[1]-1} {t[2]} {t[0]+SX-1} {t[1]-1} {t[2]+SZ-1} minecraft:stone')
for p in P:
    setup+=[f'execute as {sel(p)} run trigger previewclear',
            f'scoreboard players set {sel(p)} mcc_rot 0',
            f'scoreboard players set {sel(p)} mcc_mir 0',
            f'scoreboard players set {sel(p)} mcc_mask 0',
            f'scoreboard players set {sel(p)} mcc_hasa 0',
            f'scoreboard players set {sel(p)} mcc_buildconfirm 0']
setup+=['scoreboard players set #pass mccmp 0','scoreboard players set #fail mccmp 0']
# Nothing in this test waits for a bot reply: the runner runs it at the fastest tick rate.
# The bots' own inventories are parked in chests outside the test area for the whole run, so the
# given house materials always fit and are counted exactly; they are put back by cleanup (or by
# the next run's first step when a player was offline at cleanup).
NAMES={'a':'penguin0531','b':'geena0701'}   # the runner joins these two as A and B
STASH={'a':[(-310,250,86),(-310,250,88)],'b':[(-310,250,90),(-310,250,92)]}
step('scoreboard players set #fl mccmp 0',
     f'execute {OW} store success score #fl mccmp run forceload query -310 86',
     'execute if score #fl mccmp matches 0 run data modify storage mcc_mp_test:stash fl set value 1b',
     f'execute if score #fl mccmp matches 0 {OW} run forceload add -310 86 -310 92')
wait('inventory stash chunk loaded',['in minecraft:overworld if loaded -310 250 86','in minecraft:overworld if loaded -310 250 92'],tries=200)
step(*[f'function mcc_mp_test:unstash_{p}' for p in P], *[f'function mcc_mp_test:stash_{p}' for p in P])
check('both inventories parked',*[f'data storage mcc_mp_test:stash {{{p}:1b}}' for p in P],
      *[f'entity @a[name={NAMES[p]},nbt=!{{Inventory:[{{}}]}}]' for p in P])
step(*setup)
check('house fixtures ready',
      *[f'{OW} if blocks {box(REF)} {at(P[p]["S"])} all' for p in P],
      *[air_box(P[p]['T']) for p in P],
      f'{OW} if block {REF[0]+2} {REF[1]+2} {REF[2]} minecraft:oak_door[half=upper]',
      f'{OW} if block {REF[0]+2} {REF[1]+2} {REF[2]+2} minecraft:lantern[hanging=true]',
      no_items())

# ---- real pos1/pos2 rays: Pos1 = floor corner (from below), Pos2 = roof corner (from above) ----
step(*[aim_up(p,*P[p]['S']) for p in P])
both_trigger('pos1')
step(*[aim_down(p,P[p]['S'][0]+SX-1,Y+SY-1,P[p]['S'][2]+SZ-1) for p in P])
both_trigger('pos2')
conds=[]
for p in P:
    s=P[p]['S']
    for k,v in (('p1x',s[0]),('p1y',s[1]),('p1z',s[2]),('p2x',s[0]+SX-1),('p2y',s[1]+SY-1),('p2z',s[2]+SZ-1)):
        conds.append(f'score {sel(p)} mcc_{k} matches {v}')
check('independent 3d selections',*conds)

# ---- same-tick Copy -> V Blueprint -> Build from inventory ---------------------
both_trigger('c')
check('independent copy clipboards',
      *[f'score {sel(p)} mcc_cliptype matches 1' for p in P])
step('scoreboard players set #ok mccmp 0',
     f'execute unless score {sel("a")} mcc_id = {sel("b")} mcc_id run scoreboard players set #ok mccmp 1',
     'execute if score #ok mccmp matches 1 run scoreboard players add #pass mccmp 1',
     'execute unless score #ok mccmp matches 1 run scoreboard players add #fail mccmp 1',
     'execute if score #ok mccmp matches 1 run say MCCMP_CHECK PASS unique_mcc_id',
     'execute unless score #ok mccmp matches 1 run say MCCMP_CHECK FAIL unique_mcc_id')

step(*[aim_down(p,P[p]['T'][0],Y-1,P[p]['T'][2]) for p in P])
both_trigger('v')
wait('blueprints ready',[c for p in P for c in (
    f'score {sel(p)} mcc_bpready matches 1',
    f'score {sel(p)} mcc_bpscan matches 0',
    f'score {sel(p)} mcc_bpover_scan matches 0')])
bp=[]
for p in P:
    t=P[p]['T']
    bp+=[f'score {sel(p)} mcc_bpactive matches 1',f'score {sel(p)} mcc_bpbad matches 0',
         f'score {sel(p)} mcc_bpover matches 0',air_box(t)]
    for x,y,z,b in house.BLOCKS:
        wx,wy,wz=t[0]+x,t[1]+y,t[2]+z
        bp.append((f'{OW} positioned {wx}.0 {wy}.0 {wz}.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.01]',
                   f'player {p.upper()} blueprint missing at {wx} {wy} {wz} ({b.split("[")[0]})'))
step(*[f'execute store result score #{p}bp mccmp {OW} if entity @e[type=minecraft:block_display,tag=mcc_blueprint,x={P[p]["T"][0]},y={Y},z={P[p]["T"][2]},dx={SX-1},dy={SY-1},dz={SZ-1}]' for p in P])
check('both house blueprints complete, world untouched',*bp,
      *[(f'score #{p}bp mccmp matches {len(house.BLOCKS)}..',f'player {p.upper()} blueprint has fewer displays than the {len(house.BLOCKS)} house blocks') for p in P])

# Blueprint Flip (facing south: left/right = mirror X) inside the same bounds, then flip back.
def display_state(label,x,y,z,name,prop=None):
    """The Blueprint display at x,y,z shows block `name` (and property k=v when given)."""
    pk,pv=(prop.split('=') if prop else (None,None))
    want=[f'{{state:{{Name:"minecraft:{name}"{(",Properties:{"+pk+":\""+pv+"\"}") if prop else ""}}}}}',
          f'{{state:{{id:"minecraft:{name}"{(",properties:{"+pk+":\""+pv+"\"}") if prop else ""}}}}}']
    step('data remove storage mcc_mp_test:diag state',
         f'execute {OW} positioned {x}.0 {y}.0 {z}.0 as @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.01,limit=1] run data modify storage mcc_mp_test:diag state set from entity @s block_state')
    step('scoreboard players set #ds mccmp 0',
         *[f'execute if data storage mcc_mp_test:diag {w} run scoreboard players set #ds mccmp 1' for w in want])
    check(label,(f'score #ds mccmp matches 1',f'display at {x} {y} {z} is not {name} {prop or ""}'))

both_trigger('bpflip')
wait('flipped blueprints ready',[c for p in P for c in (f'score {sel(p)} mcc_bpready matches 1',f'score {sel(p)} mcc_bpscan matches 0')])
flip_cells=[]
for p in P:
    t=P[p]['T']
    for x,y,z,b in house.BLOCKS:
        wx,wy,wz=t[0]+SX-1-x,t[1]+y,t[2]+z
        flip_cells.append((f'{OW} positioned {wx}.0 {wy}.0 {wz}.0 if entity @e[type=minecraft:block_display,tag=mcc_blueprint,distance=..0.01]',
                           f'player {p.upper()} flipped blueprint missing at {wx} {wy} {wz}'))
check('blueprint flip keeps the house bounds',*flip_cells,*[f'score {sel(p)} mcc_bptx0 matches {P[p]["T"][0]}' for p in P])
ta=P['a']['T']
display_state('blueprint flip turns the wall torch',ta[0]+3,Y+2,ta[2]+1,'wall_torch','facing=west')
display_state('blueprint flip turns the chest',ta[0]+1,Y+1,ta[2]+3,'chest','facing=east')
display_state('blueprint flip changes the door hinge',ta[0]+2,Y+1,ta[2],'oak_door','hinge=right')
display_state('blueprint flip turns the roof stair',ta[0]+4,Y+3,ta[2]+2,'oak_stairs','facing=west')
both_trigger('bpflip')
wait('blueprints flipped back',[c for p in P for c in (f'score {sel(p)} mcc_bpready matches 1',f'score {sel(p)} mcc_bpscan matches 0')])
display_state('blueprint flip twice restores the torch',ta[0]+1,Y+2,ta[2]+1,'wall_torch','facing=east')
display_state('blueprint flip twice restores the chest',ta[0]+3,Y+1,ta[2]+3,'chest','facing=west')

# Exactly one BOM into each player's inventory, measured against the player's own baseline.
step(*count_cmds('base'),
     *[f'give {sel(p)} {item} {n}' for p in P for item,n in ITEMS])
step(f'execute {OW} run kill @e[type=minecraft:item,x={x1},y={y1},z={z1},dx={x2-x1},dy={y2-y1},dz={z2-z1}]')
check('one house BOM in each inventory',*counts_equal(1))
# Never build if the BOM did not fully fit: the build would fall back to the server's Warehouse.
step('scoreboard players operation #matok mccmp = #ok mccmp',
     *[f'execute if score #matok mccmp matches 1 as {sel(p)} run trigger build' for p in P])
wait('both builds finished',[c for p in P for c in (
    f'score {sel(p)} mcc_matphase matches 0',f'score {sel(p)} mcc_bpactive matches 0')],tries=120)
check('both builds exact 3d house',*[c for p in P for c in exact_house(P[p]['T'])],no_items())
check('builds took exactly one BOM from each inventory',*counts_equal(0))

both_trigger('undo')
wait('build undo settled',[f'score {sel(p)} mcc_matphase matches 0' for p in P])
check('build undo clears both targets',*[air_box(P[p]['T']) for p in P],
      *[c for p in P for c in exact_house(P[p]['S'])],no_items())
check('build undo refunds one BOM to each inventory',*counts_equal(1))
# Take back exactly what the test gave: only the count above each player's own baseline.
step('function mcc_mp_test:restore_inventory')
check('inventories back to baseline',*counts_equal(0))

# ---- same-tick real Move + Undo + Redo, per-player Work/Undo/Redo lanes ----
both_trigger('up set 1')
check('simultaneous move up keeps exact house',
      *[c for p in P for c in exact_house((P[p]['S'][0],Y+1,P[p]['S'][2]))],
      *[air_box(P[p]['S'],dy=1) for p in P],no_items())
lane_differs('separate_work_lanes','mcc_wbx')
lane_differs('separate_undo_lanes','mcc_ubx')
both_trigger('undo')
check('simultaneous move undo exact',
      *[c for p in P for c in exact_house(P[p]['S'])],
      *[air_box((P[p]['S'][0],Y+SY,P[p]['S'][2]),dy=1) for p in P],
      *[f'score {sel(p)} mcc_redo matches 1' for p in P],no_items())
lane_differs('separate_redo_lanes','mcc_rbx')
both_trigger('redo')
check('simultaneous move redo exact',*[c for p in P for c in exact_house((P[p]['S'][0],Y+1,P[p]['S'][2]))],no_items())
both_trigger('undo')
check('move restored before rotate',*[c for p in P for c in exact_house(P[p]['S'])])

# ---- same-tick real Rotate around Pos1, full state check, Undo ----
# Two cells of the turned footprint are occupied: the turned house must replace them, Undo must bring them back.
OCC=[(-2,1,2),(-4,0,0)]   # relative to Pos1: lantern / floor plank land here after the turn
step(*[f'execute {OW} run setblock {P[p]["S"][0]+dx} {Y+dy} {P[p]["S"][2]+dz} minecraft:stone' for p in P for dx,dy,dz in OCC])
both_trigger('turnright')
rot=[]
for p in P:
    s=P[p]['S']
    rot+=house_conds(s,'r90')
    rot.append(air_box((s[0]+1,Y,s[2]),dx=SX-1))   # the part of the old footprint the turned house left
check('simultaneous rotate 90 exact states',*rot,no_items())
both_trigger('undo')
left=[]
for p in P:
    s0=P[p]['S']
    for dx in range(-SX+1,0):
        for dy in range(SY):
            for dz in range(SZ):
                want='minecraft:stone' if (dx,dy,dz) in OCC else 'minecraft:air'
                left.append((f'{OW} if block {s0[0]+dx} {Y+dy} {s0[2]+dz} {want}',f'{s0[0]+dx} {Y+dy} {s0[2]+dz} expected {want} after undo'))
check('rotate undo exact and restores the occupied cells',*[c for p in P for c in exact_house(P[p]['S'])],*left,no_items())
step(*[f'execute {OW} run setblock {P[p]["S"][0]+dx} {Y+dy} {P[p]["S"][2]+dz} minecraft:air' for p in P for dx,dy,dz in OCC])

# ---- same-tick Flip (facing south: left/right = mirror X), full state check, Undo ----
step(*[aim_down(p,P[p]['S'][0]+2,Y+SY-1,P[p]['S'][2]+2) for p in P])
both_trigger('flip')
check('simultaneous flip exact states',*[c for p in P for c in house_conds(P[p]['S'],'mx')],no_items())
both_trigger('undo')
check('flip undo exact',*[c for p in P for c in exact_house(P[p]['S'])],no_items())

# ---- Undo guard: block-state changes are ignored, block-ID / block-entity changes block Undo ----
both_trigger('up set 1')
sa,sb=P['a']['S'],P['b']['S']
step(f'execute {OW} run setblock {sa[0]} {Y+4} {sa[2]+2} minecraft:oak_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]')
both_trigger('undo')
check('undo ignores a changed block state',*[c for p in P for c in exact_house(P[p]['S'])],
      *[f'score {sel(p)} mcc_redo matches 1' for p in P])
both_trigger('redo')
step(f'execute {OW} run setblock {sa[0]+1} {Y+1} {sa[2]+2} minecraft:stone')
step(f'execute as {sel("a")} run trigger undo')
check('undo rejects a changed block id and reports it',
      f'{OW} if block {sa[0]+1} {Y+1} {sa[2]+2} minecraft:stone',*exact_house((sb[0],Y+1,sb[2])),
      f'score {sel("a")} mcc_undo matches 1',f'score {sel("a")} mcc_diagcount matches 1',f'score {sel("a")} mcc_diagmissing matches 1',
      (f'data storage mcc:temp diag.coords[{{x:{sa[0]+1},y:{Y+1},z:{sa[2]+2},expected:"minecraft:oak_planks",current:"minecraft:stone",kind:1}}]','diagnostic does not name the changed plank'))
step(f'execute {OW} run item replace block {sb[0]+3} {Y+2} {sb[2]+3} container.0 with minecraft:diamond 1')
step(f'execute as {sel("b")} run trigger undo')
check('undo rejects a changed chest content and reports it',
      f'{OW} if block {sb[0]+3} {Y+2} {sb[2]+3} minecraft:chest',f'score {sel("b")} mcc_undo matches 1',
      f'score {sel("b")} mcc_diagcount matches 1',f'score {sel("b")} mcc_diagcontent matches 1',
      (f'data storage mcc:temp diag.coords[{{x:{sb[0]+3},y:{Y+2},z:{sb[2]+3},expected:"minecraft:chest",current:"minecraft:chest",kind:3}}]','diagnostic does not name the chest'))
step(f'execute {OW} run setblock {sa[0]+1} {Y+1} {sa[2]+2} minecraft:oak_planks',
     f'execute {OW} run item replace block {sb[0]+3} {Y+2} {sb[2]+3} container.0 with minecraft:air')
both_trigger('undo')
check('undo works again once the changes are put back',*[c for p in P for c in exact_house(P[p]['S'])],no_items())

# ---- X (Cut) and V paste of real blocks; per-player isolated Undo/Redo ----
both_trigger('x')
check('simultaneous cut clears both sources',
      *[air_box(P[p]['S']) for p in P],
      *[f'score {sel(p)} mcc_cliptype matches 2' for p in P],no_items())
step(*[aim_down(p,P[p]['T'][0],Y-1,P[p]['T'][2]) for p in P])
both_trigger('v')
check('simultaneous cut paste exact',*[c for p in P for c in exact_house(P[p]['T'])],
      *[f'score {sel(p)} mcc_clip matches 0' for p in P],no_items())

step(f'execute as {sel("a")} run trigger undo')
check('A undo does not touch B',air_box(P['a']['T']),*exact_house(P['b']['T']),
      f'score {sel("a")} mcc_redo matches 1',f'score {sel("b")} mcc_undo matches 1')
step(f'execute as {sel("a")} run trigger redo')
check('A redo does not touch B',*exact_house(P['a']['T']),*exact_house(P['b']['T']))
step(f'execute as {sel("b")} run trigger undo')
check('B independent undo',*exact_house(P['a']['T']),air_box(P['b']['T']))
step(f'execute as {sel("b")} run trigger undo')
check('B second undo restores cut source',*exact_house(P['b']['S']),air_box(P['b']['T']),
      *exact_house(P['a']['T']),air_box(P['a']['S']),no_items())

step(
    *[f'tellraw @a[tag={P[p]["tag"]}] [{{"text":"MCCMP DONE pass="}},{{"score":{{"name":"#pass","objective":"mccmp"}}}},{{"text":" fail="}},{{"score":{{"name":"#fail","objective":"mccmp"}}}}]' for p in P],
    'execute if score #fail mccmp matches 0 run say MCCMP_RESULT PASS',
    'execute unless score #fail mccmp matches 0 run say MCCMP_RESULT FAIL'
)

# ---- write functions ---------------------------------------------------------
for i,s in enumerate(steps):
    nxt=f'mcc_mp_test:step_{i+1}' if i+1<len(steps) else None
    if s[0]=='cmd':
        commands=list(s[1])
        if nxt: commands.append(f'schedule function {nxt} 4t replace')
    else:
        _,label,conds,tries=s
        tag=label.replace(' ','_')
        ready='execute '+' '.join(chained(c) for c in conds)
        commands=['scoreboard players add #wait mccmp 1',
                  f'{ready} run scoreboard players set #wait mccmp 0',
                  f'{ready} run return run schedule function {nxt} 4t replace',
                  f'execute if score #wait mccmp matches {tries}.. run say MCCMP_CHECK FAIL wait_{tag}',
                  f'execute if score #wait mccmp matches {tries}.. run scoreboard players add #fail mccmp 1',
                  f'execute if score #wait mccmp matches {tries}.. run scoreboard players set #wait mccmp 0',
                  f'execute if score #wait mccmp matches 0 run return run schedule function {nxt} 4t replace',
                  f'schedule function mcc_mp_test:step_{i} 5t replace']
    (F/f'step_{i}.mcfunction').write_text('\n'.join(commands)+'\n',encoding='utf-8')

(F/'join_a.mcfunction').write_text('tag @s remove mcc_mp_b\ntag @s add mcc_mp_a\ntellraw @s "MCCMP: registered as player A"\n',encoding='utf-8')
(F/'join_b.mcfunction').write_text('tag @s remove mcc_mp_a\ntag @s add mcc_mp_b\ntellraw @s "MCCMP: registered as player B"\n',encoding='utf-8')
(F/'start.mcfunction').write_text(
    'execute unless entity @a[tag=mcc_mp_a,limit=1] run tellraw @s "MCCMP: player A missing"\n'
    'execute unless entity @a[tag=mcc_mp_a,limit=1] run return fail\n'
    'execute unless entity @a[tag=mcc_mp_b,limit=1] run tellraw @s "MCCMP: player B missing"\n'
    'execute unless entity @a[tag=mcc_mp_b,limit=1] run return fail\n'
    'scoreboard objectives remove mccmp\n'
    'scoreboard objectives add mccmp dummy\n'
    'scoreboard players set #pass mccmp 0\n'
    'scoreboard players set #fail mccmp 0\n'
    'scoreboard players set #wait mccmp 0\n'
    'function mcc_mp_test:step_0\n',
    encoding='utf-8'
)
# Cleanup: stop the chain, take back anything the test gave (count above the
# player's own baseline), clear the area and the test state.
cleanup=[f'schedule clear mcc_mp_test:step_{i}' for i in range(len(steps))]
cleanup+=[f'execute as {sel(p)} run trigger previewclear' for p in P]
cleanup.append('function mcc_mp_test:restore_inventory')
cleanup+=[f'function mcc_mp_test:unstash_{p}' for p in P]
restore=[]
for p in P:
    for i,(item,_) in enumerate(ITEMS):
        guard=f'execute if score #{p}base{i} mccmp matches 0..'
        restore+=[f'{guard} store result score #{p}n{i} mccmp run clear {sel(p)} {item} 0',
                  f'{guard} run scoreboard players operation #{p}n{i} mccmp -= #{p}base{i} mccmp',
                  f'{guard} if score #{p}n{i} mccmp matches 1.. store result storage mcc_mp_test:tmp n int 1 run scoreboard players get #{p}n{i} mccmp',
                  f'{guard} if score #{p}n{i} mccmp matches 1.. run data modify storage mcc_mp_test:tmp item set value "{item}"',
                  f'{guard} if score #{p}n{i} mccmp matches 1.. as {sel(p)} run function mcc_mp_test:clear_n with storage mcc_mp_test:tmp']
(F/'restore_inventory.mcfunction').write_text('\n'.join(restore)+'\n',encoding='utf-8')
cleanup+=[f'execute {OW} run fill {x1} {y1} {z1} {x2} {y2} {z2} air',
          f'execute {OW} run kill @e[type=minecraft:item,x={x1},y={y1},z={z1},dx={x2-x1},dy={y2-y1},dz={z2-z1}]',
          'data remove storage mcc_mp_test:tmp n','data remove storage mcc_mp_test:tmp item',
          'tag @a remove mcc_mp_a','tag @a remove mcc_mp_b',
          'scoreboard objectives remove mccmp',
          'say MCCMP_CLEANUP DONE']
(F/'cleanup.mcfunction').write_text('\n'.join(cleanup)+'\n',encoding='utf-8')
(F/'clear_n.mcfunction').write_text('$clear @s $(item) $(n)\n',encoding='utf-8')
for p in P:
    n=NAMES[p]; who=f'@a[name={n},limit=1]'; (c1,c2)=STASH[p]
    b1=f'{c1[0]} {c1[1]} {c1[2]}'; b2=f'{c2[0]} {c2[1]} {c2[2]}'
    st=[f'execute if data storage mcc_mp_test:stash {{{p}:1b}} run return run say MCCMP_STASH {n} already parked',
        f'execute unless entity {who} run return run say MCCMP_STASH {n} offline, nothing parked',
        f'execute {OW} run setblock {b1} minecraft:chest', f'execute {OW} run setblock {b2} minecraft:chest']
    st+=[f'execute {OW} run item replace block {b1} container.{i} from entity {who} container.{i}' for i in range(27)]
    st+=[f'execute {OW} run item replace block {b2} container.{i-27} from entity {who} container.{i}' for i in range(27,36)]
    st+=[f'execute {OW} run item replace block {b2} container.9 from entity {who} weapon.offhand']
    st+=[f'item replace entity {who} container.{i} with minecraft:air' for i in range(36)]
    st+=[f'item replace entity {who} weapon.offhand with minecraft:air', f'data modify storage mcc_mp_test:stash {p} set value 1b']
    (F/f'stash_{p}.mcfunction').write_text('\n'.join(st)+'\n',encoding='utf-8')
    un=[f'execute unless data storage mcc_mp_test:stash {{{p}:1b}} run return 0',
        f'execute unless entity {who} run return run say MCCMP_STASH {n} offline: run function mcc_mp_test:unstash_{p} when {n} is back',
        f'execute {OW} unless block {b1} minecraft:chest run return run say MCCMP_STASH stash chest for {n} not loaded, inventory still parked']
    un+=[f'execute {OW} run item replace entity {who} container.{i} from block {b1} container.{i}' for i in range(27)]
    un+=[f'execute {OW} run item replace entity {who} container.{i} from block {b2} container.{i-27}' for i in range(27,36)]
    un+=[f'execute {OW} run item replace entity {who} weapon.offhand from block {b2} container.9',
         f'execute {OW} run data remove block {b1} Items', f'execute {OW} run data remove block {b2} Items',
         f'execute {OW} run setblock {b1} minecraft:air', f'execute {OW} run setblock {b2} minecraft:air',
         f'data remove storage mcc_mp_test:stash {p}', f'say MCCMP_STASH {n} inventory restored',
         'execute unless data storage mcc_mp_test:stash a unless data storage mcc_mp_test:stash b if data storage mcc_mp_test:stash {fl:1b} in minecraft:overworld run forceload remove -310 86 -310 92',
         'execute unless data storage mcc_mp_test:stash a unless data storage mcc_mp_test:stash b run data remove storage mcc_mp_test:stash fl']
    (F/f'unstash_{p}.mcfunction').write_text('\n'.join(un)+'\n',encoding='utf-8')
print(f'Built {len(steps)} v1.7 two-player 3D house steps at {OUT}')
