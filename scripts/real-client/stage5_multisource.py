"""Stage 5: every material is spread over several Warehouse chests (its sort box, overflow
boxes, and boxes a player stuffed it into by hand), so Build must charge across chests.
Undo must refund through the entry chest and the real sorter must put each refund back in
that material's own sort box. Verdicts come from the saved world, chest by chest."""
import sys; sys.argv = sys.argv[:1] + ['none']  # import helpers only; do not rerun stage 3
from stage3_house import *
from collections import Counter

# (item, box, half, count); no single box holds a full BOM of stone bricks or planks,
# so Build has to take from several chests whatever order it uses.
PLAN = [
    ('minecraft:stone_bricks', '39', 'R', 8), ('minecraft:stone_bricks', '39', 'L', 6), ('minecraft:stone_bricks', '30', 'R', 7),
    ('minecraft:stone_bricks', '12', 'R', 5), ('minecraft:stone_bricks', '60', 'L', 7), ('minecraft:stone_bricks', '22', 'R', 7),
    ('minecraft:oak_planks', '11', 'R', 9), ('minecraft:oak_planks', '11', 'L', 9), ('minecraft:oak_planks', '10', 'R', 9),
    ('minecraft:oak_planks', '25', 'L', 9), ('minecraft:oak_planks', '40', 'R', 8), ('minecraft:oak_planks', '33', 'R', 8),
    ('minecraft:oak_log', '36', 'R', 5), ('minecraft:oak_log', '30', 'L', 6), ('minecraft:oak_log', '44', 'R', 7),
    ('minecraft:oak_slab', '37', 'R', 7), ('minecraft:oak_slab', '50', 'R', 9), ('minecraft:oak_slab', '15', 'L', 8),
    ('minecraft:oak_stairs', '37', 'L', 8), ('minecraft:oak_stairs', '20', 'R', 8), ('minecraft:oak_stairs', '59', 'R', 8),
    ('minecraft:oak_door', '37', 'R', 1), ('minecraft:oak_door', '50', 'L', 1),
    ('minecraft:glass_pane', '51', 'R', 1), ('minecraft:glass_pane', '56', 'R', 3),
    ('minecraft:chest', '49', 'R', 1), ('minecraft:chest', '31', 'L', 1),
    ('minecraft:torch', '13', 'R', 1), ('minecraft:torch', '20', 'L', 1),
    ('minecraft:lantern', '27', 'R', 2), ('minecraft:lantern', '14', 'R', 2),
]
T = (1019, Y0, 1039)

def per_box(w):
    _, per = warehouse_stock(w)
    return {c: Counter({k: v for k, v in cc.items() if k in house.BOM}) for c, cc in per.items()}

def item_boxes(per, item):
    return {c: cc[item] for c, cc in per.items() if cc.get(item)}

def charged_across(before, after, label, expect):
    """Every chest may only lose items; per item the total loss must equal `expect`."""
    ok = True; notes = []
    for item, need in expect.items():
        gained = {c: after[c][item] - before[c][item] for c in before if after[c][item] > before[c][item]}
        lost = {c: before[c][item] - after[c][item] for c in before if after[c][item] < before[c][item]}
        if gained or sum(lost.values()) != need: ok = False
        notes.append(f'{item.split(":")[1]}:{"+".join(f"{c}x{n}" for c, n in sorted(lost.items()))}' + (f' GAINED{gained}' if gained else ''))
    return record(label, ok, '; '.join(notes))

log('=== stage 5: materials spread over several chests; Build charges across them; Undo refunds sort home')
d.close_screens()
save_world(); w = world()
per0 = per_box(w)
# Home = the box the real sorter put the material in; a player override wins if present.
overrides = storage('warehouse')['rules'].get('overrides', {})
home = {}
for item in house.BOM:
    boxes = item_boxes(per0, item)
    if item in overrides: home[item] = f'{overrides[item]:02d}'
    elif len(boxes) == 1: home[item] = next(iter(boxes))
    else: home[item] = next(b for i, b, _, _ in PLAN if i == item)  # rerun: PLAN lists the home box first
record('setup: every material has a known sort box', all(home.values()), f'home={home}')
# The selection must hold only the house: anything else becomes a material Warehouse lacks.
stray = [(p, w.block(*p)) for p in sel_cells() if w.block(*p) != 'minecraft:air'
         and (p[0] - HOUSE_O[0], p[1] - HOUSE_O[1], p[2] - HOUSE_O[2]) not in {(x, y, z) for x, y, z, _ in house.BLOCKS}]
for (x, y, z), b in stray:
    log(f'    removing stray {b} at {(x, y, z)} from the selection'); cmd(f'setblock {x} {y} {z} air')
assert sum(n for i, _, _, n in PLAN if i == 'minecraft:stone_bricks') == BOM2['minecraft:stone_bricks']
for item in house.BOM:
    assert sum(n for i, _, _, n in PLAN if i == item) == BOM2[item], item

log('--- redistribute: empty the involved chests, then place the plan')
touched = sorted({b for _, b, _, _ in PLAN} | set(home.values()))
for b in touched:
    x, z = BOX[b]
    cmd(f'data modify block {x} {Y0} {z} Items set value []', 0.2)
    cmd(f'data modify block {x + 1} {Y0} {z} Items set value []', 0.2)
slot = Counter()
for item, b, half, n in PLAN:
    x, z = BOX[b]
    hx = x if half == 'R' else x + 1
    cmd(f'item replace block {hx} {Y0} {z} container.{slot[(b, half)]} with {item} {n}', 0.25)
    slot[(b, half)] += 1
time.sleep(3)
save_world(); w = world()
per1 = per_box(w)
want1 = {c: Counter() for c in BOX}
for item, b, _, n in PLAN: want1[b][item] += n
bad = {c: (dict(per1[c]), dict(want1[c])) for c in BOX if per1[c] != want1[c]}
record('setup: plan placed chest by chest (totals still 2x BOM)', not bad, f'bad={bad}')
for item in ('minecraft:stone_bricks', 'minecraft:oak_planks'):
    log(f'    {item}: {item_boxes(per1, item)}')

log('--- Copy -> V -> Build')
_, SRC = snapshot()
reset_xform(); select_house(); trig('c')
aim_target(T[0], T[2]); trig('v', 3.0)
trig('build', 1.0); time.sleep(8)
save_world(); w = world()
exp = expect_placed(SRC, T)
compare(w, exp, 'multi-chest build: 3D copy exact', extra_air=box_around(exp))
no_drops(w, 'multi-chest build: no drops')
per2 = per_box(w)
charged_across(per1, per2, 'multi-chest build: charged exactly one BOM, only by removing from chests', house.BOM)
for item in ('minecraft:stone_bricks', 'minecraft:oak_planks'):
    n = sum(1 for c in BOX if per2[c][item] < per1[c][item])
    record(f'multi-chest build: {item.split(":")[1]} taken from several chests', n >= 2, f'{n} chests')
record('multi-chest build: entry chest empty', not +per2['00'], str(dict(per2['00'])))

log('--- Undo: refund goes through the entry chest and is sorted back home')
trig('undo', 1.0); time.sleep(25)
save_world(); w = world()
compare(w, {p: 'minecraft:air' for p in exp}, 'multi-chest undo: target back to air')
no_drops(w, 'multi-chest undo: no drops')
per3 = per_box(w)
record('multi-chest undo: entry chest empty (everything sorted)', not +per3['00'], str(dict(per3['00'])))
for item, need in house.BOM.items():
    h = home[item]
    others = {c: (per2[c][item], per3[c][item]) for c in BOX if c != h and per3[c][item] != per2[c][item]}
    record(f'refund sorted home: {item.split(":")[1]} +{need} in box {h}, no other chest changed',
           per3[h][item] == per2[h][item] + need and not others,
           f'box {h}: {per2[h][item]} -> {per3[h][item]}; other changes={others}')
tot3 = Counter(); [tot3.update(cc) for cc in per3.values()]
record('multi-chest undo: Warehouse total back to 2x BOM', {k: tot3[k] for k in house.BOM} == BOM2, str(dict(tot3)))

log('--- Redo charges across chests again, Undo refunds again')
trig('redo', 1.0); time.sleep(8)
save_world(); w = world()
compare(w, exp, 'multi-chest redo: 3D copy exact again')
per4 = per_box(w)
charged_across(per3, per4, 'multi-chest redo: charged exactly one BOM again', house.BOM)
trig('undo', 1.0); time.sleep(25)
save_world(); w = world()
per5 = per_box(w)
tot5 = Counter(); [tot5.update(cc) for cc in per5.values()]
record('final: Warehouse total back to 2x BOM, entry empty', {k: tot5[k] for k in house.BOM} == BOM2 and not +per5['00'], str(dict(per5['00'])))
d.close_screens()
