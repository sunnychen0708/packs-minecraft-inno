"""Stage 10: Build takes materials from the player's own inventory and off hand first, then
Warehouse; Undo gives the player's part back to the player as far as it fits and sends the
rest to Warehouse. Renamed stacks are never used. Verdicts come from the saved player data
and chests."""
import sys; sys.argv = sys.argv[:1] + ['none']  # import helpers only; do not rerun stage 3
from stage3_house import *
import gzip
from collections import Counter

BRICK, PLANK = 'minecraft:stone_bricks', 'minecraft:oak_planks'

def player():
    files = sorted((WORLD / 'players' / 'data').glob('*.dat'), key=lambda p: p.stat().st_mtime)
    return mcworld.parse_nbt(gzip.decompress(files[-1].read_bytes()))

def inv_state():
    """(plain counts in slots 0-35 by id, off hand item, renamed brick count, used slots)."""
    pl = player(); plain = Counter(); renamed = 0
    for it in pl.get('Inventory', []):
        if it.get('components'):
            if it['id'] == BRICK: renamed += it.get('count', 1)
        else: plain[it['id']] += it.get('count', 1)
    off = pl.get('equipment', {}).get('offhand')
    return plain, off, renamed, len(pl.get('Inventory', []))

def stock():
    tot, per = warehouse_stock(world())
    return {k: tot.get(k, 0) for k in house.BOM}, dict(per['00'])

d.close_screens()
reload_packs()
cmd('time set day'); cmd('kill @e[type=minecraft:item]')
T = (1045, Y0, 1060)

log('=== 1. player carries 10 bricks + a renamed brick stack, 5 planks in the off hand')
cmd('clear @s')
cmd(f'item replace entity @s hotbar.0 with {BRICK} 10')
cmd(f'item replace entity @s hotbar.1 with {BRICK}[custom_name="Keep me"] 64')
cmd(f'item replace entity @s weapon.offhand with {PLANK} 5')
time.sleep(1)
save_world()
wh0, entry0 = stock()
record('setup: Warehouse holds a full BOM', all(wh0[k] >= v for k, v in house.BOM.items()) and not entry0, str(wh0))
_, SRC = snapshot()
reset_xform(); select_house(); trig('c')
aim_target(T[0], T[2]); trig('v', 4.0)
pos = d.log_len()
trig('materials', 1.0); time.sleep(6)
rows = [l.split('[CHAT] ', 1)[1] for l in d.log_since(pos).splitlines() if '[System] [CHAT] ' in l and '背包' in l]
record('materials check shows the backpack part', any('背包 10' in r for r in rows) and any('背包 5' in r for r in rows), ' | '.join(rows[:3]))
trig('build', 1.0); time.sleep(8)
save_world(); w = world()
exp = expect_placed(SRC, T)
compare(w, exp, 'build: house exact', extra_air=box_around(exp))
plain, off, renamed, _ = inv_state()
record('build: took the 10 plain bricks and the 5 off-hand planks first', plain.get(BRICK, 0) == 0 and not off, f'plain={dict(plain)} offhand={off}')
record('build: renamed brick stack untouched', renamed == 64, f'renamed={renamed}')
wh1, _ = stock()
want = dict(wh0); want[BRICK] -= house.BOM[BRICK] - 10; want[PLANK] -= house.BOM[PLANK] - 5
for k in house.BOM:
    if k not in (BRICK, PLANK): want[k] -= house.BOM[k]
record('build: Warehouse charged only the rest of the BOM', wh1 == want, f'want={want} got={wh1}')
no_drops(w, 'build: no drops')

log('=== 2. Undo gives the player part back to the player, the rest to Warehouse')
trig('undo', 1.0); time.sleep(22)
save_world(); w = world()
compare(w, {p: 'minecraft:air' for p in exp}, 'undo: target back to air')
plain, off, renamed, _ = inv_state()
record('undo: player got back 10 bricks and 5 planks', plain.get(BRICK, 0) == 10 and plain.get(PLANK, 0) == 5, f'plain={dict(plain)} offhand={off}')
wh2, entry2 = stock()
record('undo: Warehouse back to its starting stock, entry sorted', wh2 == wh0 and not entry2, f'want={wh0} got={wh2} entry={entry2}')
no_drops(w, 'undo: no drops')

log('=== 2b. Redo charges the player first again, Undo returns it again')
trig('redo', 1.0); time.sleep(8)
save_world(); w = world()
compare(w, exp, 'redo: house exact again')
plain, off, renamed, _ = inv_state()
record('redo: took the 10 bricks and 5 planks from the player again', plain.get(BRICK, 0) == 0 and plain.get(PLANK, 0) == 0 and renamed == 64, f'plain={dict(plain)} renamed={renamed}')
wh3, _ = stock()
record('redo: Warehouse charged only the rest again', wh3 == wh1, f'want={wh1} got={wh3}')
trig('undo', 1.0); time.sleep(22)
save_world(); w = world()
plain, off, renamed, _ = inv_state()
wh4, entry4 = stock()
record('redo undo: player and Warehouse back exactly', plain.get(BRICK, 0) == 10 and plain.get(PLANK, 0) == 5 and wh4 == wh0 and not entry4, f'plain={dict(plain)} wh={wh4}')
no_drops(w, 'redo undo: no drops')

log('=== 3. nearly full inventory: only what fits goes back, the rest to Warehouse, nothing dropped')
cmd('clear @s')
cmd(f'item replace entity @s hotbar.0 with {BRICK} 64')
time.sleep(1)
save_world(); wh0, _ = stock()
trig('c'); aim_target(T[0], T[2]); trig('v', 4.0)
trig('build', 1.0); time.sleep(8)
save_world()
plain, _, _, _ = inv_state()
record('full-inv build: 20 bricks taken from the 64-stack', plain.get(BRICK, 0) == 44, f'plain={dict(plain)}')
# The player then picks more bricks up (60 in the slot) and fills every other slot with dirt.
cmd(f'item replace entity @s hotbar.0 with {BRICK} 60')
for s in range(1, 36):
    slot = f'hotbar.{s}' if s < 9 else f'inventory.{s - 9}'
    cmd(f'item replace entity @s {slot} with minecraft:dirt 64', 0.12)
time.sleep(1)
trig('undo', 1.0); time.sleep(22)
save_world(); w = world()
plain, _, _, used = inv_state()
record('full-inv undo: only 4 bricks fit and went to the player', plain.get(BRICK, 0) == 64 and used == 36, f'plain bricks={plain.get(BRICK, 0)} slots used={used}')
wh2, entry2 = stock()
want = dict(wh0); want[BRICK] += 16  # Build took all 20 bricks from the player; 4 fit back, 16 go to Warehouse
record('full-inv undo: the 16 that did not fit went to Warehouse', wh2 == want and not entry2, f'want={want} got={wh2}')
no_drops(w, 'full-inv undo: nothing dropped on the ground')
cmd('clear @s')
d.close_screens()
