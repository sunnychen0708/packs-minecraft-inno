"""Stage 3+: custom rule, stock, 3D house, Copy/Blueprint/Build, Undo/Redo, rotated/mirrored
builds, Cut, Move, Flip, direct Rotate, Pick. Every verdict comes from the saved world files."""
from realplay import *
import xform

ONLY = set(sys.argv[1:])  # optional: run selected sections
def want(s): return not ONLY or s in ONLY

AX, AY, AZ = MARK1
(SX1, SY1, SZ1), (SX2, SY2, SZ2) = MARK1, MARK2
BOM2 = {k: 2 * v for k, v in house.BOM.items()}
HOUSE_CHEST = (HOUSE_O[0] + 3, HOUSE_O[1] + 1, HOUSE_O[2] + 3)
CHEST_LOOT = {'minecraft:diamond': 5, 'minecraft:apple': 7}

def sel_cells():
    return [(x, y, z) for x in range(SX1, SX2 + 1) for y in range(SY1, SY2 + 1) for z in range(SZ1, SZ2 + 1)]

def snapshot():
    w = world()
    src = {p: w.block(*p) for p in sel_cells()}
    # The 3D house is the test fixture: if someone moved it, every check would compare air with air.
    solid = sum(1 for s in src.values() if s != 'minecraft:air')
    if solid < len(house.BLOCKS):
        raise RuntimeError(f'test house missing at {HOUSE_O}: only {solid}/{len(house.BLOCKS)} blocks in the selection')
    return w, src

def compare(w, expect, label, extra_air=()):
    bad = [(p, e, w.block(*p)) for p, e in expect.items() if w.block(*p) != e]
    bad += [(p, 'minecraft:air', w.block(*p)) for p in extra_air if p not in expect and w.block(*p) != 'minecraft:air']
    return record(label, not bad, f'{len(expect)} cells; mismatches={len(bad)} ' + '; '.join(f'{p}: want {e} got {g}' for p, e, g in bad[:6]))

def expect_placed(src, target, k=0, mirror=None, pivot=MARK1):
    """Expected blocks when the selection is re-placed with Pos1/pivot landing on `target`."""
    out = {}
    for (x, y, z), s in src.items():
        dx, dz = x - pivot[0], z - pivot[2]
        st = s
        if mirror == 'x': dx = -dx; st = xform.mirror_state(st, 'x')
        if mirror == 'z': dz = -dz; st = xform.mirror_state(st, 'z')
        dx, dz = xform.rot_off(dx, dz, k); st = xform.rotate_state(st, k)
        out[(target[0] + dx, target[1] + (y - pivot[1]), target[2] + dz)] = st
    return out

def box_around(cells, pad=1):
    xs = [p[0] for p in cells]; ys = [p[1] for p in cells]; zs = [p[2] for p in cells]
    return [(x, y, z) for x in range(min(xs) - pad, max(xs) + pad + 1) for y in range(max(Y0, min(ys)), max(ys) + pad + 1)
            for z in range(min(zs) - pad, max(zs) + pad + 1)]

def no_drops(w, label):
    # Only items this build could drop count; mobs burning at daybreak drop rotten flesh etc.
    relevant = set(house.BOM) | set(CHEST_LOOT) | {'minecraft:stone_bricks', 'minecraft:white_wool'}
    items = [e for e in item_entities(w) if e.get('Item', {}).get('id') in relevant]
    return record(label, not items, f'dropped={[(e.get("Item", {}).get("id"), e.get("Item", {}).get("count")) for e in items][:6]}')

def chest_items_at(w, p):
    return mcworld.items_of(w.block_entity(*p))

def stock_is(w, expect, label, entry_empty=True):
    tot, per = warehouse_stock(w)
    got = {k: tot.get(k, 0) for k in house.BOM}
    ok = got == expect
    entry = dict(per['00'])
    if entry_empty: ok = ok and not entry
    return record(label, ok, f'want={expect} got={got} entry={entry}')

def aim_target(tx, tz):
    """Look straight down at the ground block so the paste target is the air cell above it."""
    look_down_at(tx, GY, tz, 4)

def select_house():
    cmd(f'setblock {MARK1[0]} {MARK1[1]} {MARK1[2]} minecraft:white_wool')
    cmd(f'setblock {MARK2[0]} {MARK2[1]} {MARK2[2]} minecraft:white_wool')
    look_down_at(*MARK1, 4); trig('pos1')
    look_down_at(*MARK2, 4); trig('pos2')
    cmd(f'setblock {MARK1[0]} {MARK1[1]} {MARK1[2]} air')
    cmd(f'setblock {MARK2[0]} {MARK2[1]} {MARK2[2]} air')

def reset_xform():
    """Rotation/mirror are per-player Blueprint settings that outlive a Copy; start from identity."""
    trig('rotate set 10'); trig('mirror set 10')

def wait_sorted(sec=15):
    time.sleep(sec)

def place_house():
    for c in house.place_commands(*HOUSE_O):
        cmd(c, 0.12)
    items = ','.join(f'{{Slot:{i}b,id:"{k}",count:{v}}}' for i, (k, v) in enumerate(CHEST_LOOT.items()))
    cmd(f'data modify block {HOUSE_CHEST[0]} {HOUSE_CHEST[1]} {HOUSE_CHEST[2]} Items set value [{items}]')

def clear_dest(x1, z1, x2, z2):
    cmd(f'fill {x1} {Y0} {z1} {x2} {Y0 + 8} {z2} air')

d.close_screens()

if want('rule'):
    log('=== custom Warehouse rule by held item: oak_planks -> box 11')
    cmd('clear @s'); cmd('item replace entity @s hotbar.0 with minecraft:oak_planks 1')
    cmd(f'tp @s 1020.5 {Y0} 1020.5 180 -90')
    trig('wh_rule set 1', 1.0)
    d.screenshot(str(OUT / 'rule1.png'))
    d.close_screens()
    trig('wh_rule_dest set 11', 1.0)
    d.screenshot(str(OUT / 'rule2.png'))
    d.close_screens()
    cmd('clear @s')
    save_world()
    ov = storage('warehouse')['rules'].get('overrides', {})
    record('rule: oak_planks override saved as box 11', ov.get('minecraft:oak_planks') == 11, f'overrides={ov}')

if want('stock'):
    log('=== stock: 2x house BOM into the entry chest, real Warehouse ticks sort it')
    x0, z0 = BOX['00']
    cmd(f'tp @s {x0 + 1} {Y0} {z0 + 3} 180 0')
    for i, (k, v) in enumerate(BOM2.items()):
        cmd(f'item replace block {x0} {Y0} {z0} container.{i} with {k} {v}', 0.3)
    wait_sorted(20)
    save_world(); w = world()
    stock_is(w, BOM2, 'stock: entry chest emptied and every material counted in registered boxes')
    tot, per = warehouse_stock(w)
    record('stock: custom rule honoured (all oak_planks in box 11)', per['11'].get('minecraft:oak_planks', 0) == BOM2['minecraft:oak_planks'],
           f'box11={dict(per["11"])} planks elsewhere={[(c, v["minecraft:oak_planks"]) for c, v in per.items() if c != "11" and v.get("minecraft:oak_planks")]}')

if want('house'):
    log('=== 3D house fixture')
    clear_dest(990, 1030, 1100, 1100)
    cmd(f'tp @s 1002.5 {Y0 + 6} 1035.5 0 30'); time.sleep(2)
    place_house()
    save_world(); w = world()
    bad = [(x, y, z) for x, y, z, b in house.BLOCKS if w.block(HOUSE_O[0] + x, HOUSE_O[1] + y, HOUSE_O[2] + z).split('[')[0] != b.split('[')[0]]
    record('house: 86-block 3D house placed', not bad, f'bad={bad[:4]}')
    record('house: chest inside holds loot', chest_items_at(w, HOUSE_CHEST) == CHEST_LOOT, str(chest_items_at(w, HOUSE_CHEST)))
    d.screenshot(str(OUT / 'house.png'))

if want('build'):
    log('=== Copy -> V Blueprint -> Build from Warehouse, Undo (refund), Redo (charge)')
    w, SRC = snapshot()
    T1 = (1019, Y0, 1039)
    reset_xform()
    select_house()
    trig('c')
    aim_target(T1[0], T1[2]); trig('v', 3.0)
    d.screenshot(str(OUT / 'bp.png'))
    save_world(); w = world()
    exp = expect_placed(SRC, T1)
    real = [p for p, s in exp.items() if w.block(*p) != 'minecraft:air']
    record('blueprint: V creates no real blocks', not real, f'real={real[:4]}')
    disp = [e for e in w.entities_in(T1[0] - 1, Y0 - 1, T1[2] - 1, T1[0] + 8, Y0 + 5, T1[2] + 8) if e.get('id') == 'minecraft:block_display']
    record('blueprint: block_display preview exists at target', len(disp) > 0, f'{len(disp)} displays')
    # A block_display renders from its origin corner: it must sit exactly on the block corner of
    # the cell it previews (an integer-coordinate summon is centred +0.5 X/Z and looks skewed).
    def _cell(e):
        p = e.get('Pos', [0.5, 0, 0.5])
        return tuple(int(v) for v in p) if all(float(v).is_integer() for v in p) else None
    # 26.3 saves block_state as a string without default properties; mcworld.fmt fills them in.
    misplaced = [(e.get('Pos'), mcworld.fmt(e.get('block_state'))) for e in disp
                 if _cell(e) not in exp or mcworld.fmt(e.get('block_state')) != exp[_cell(e)]]
    nonair = {p for p, s in exp.items() if s != 'minecraft:air'}
    covered = {_cell(e) for e in disp}
    record('blueprint: every display sits exactly on its target block with the exact state',
           disp and not misplaced and covered == nonair and len(disp) == len(nonair),
           f'{len(disp)} displays for {len(nonair)} blocks; misplaced={misplaced[:4]} missing={sorted(nonair - covered)[:4]}')
    compare(w, SRC, 'blueprint: source untouched')
    trig('build', 1.0); time.sleep(6)
    d.screenshot(str(OUT / 'build.png'))
    save_world(); w = world()
    exp_built = dict(exp)
    rel_chest = (T1[0] + HOUSE_CHEST[0] - AX, T1[1] + HOUSE_CHEST[1] - AY, T1[2] + HOUSE_CHEST[2] - AZ)
    compare(w, exp_built, 'build: 3D copy exact (every block + state)', extra_air=box_around(exp_built))
    record('build: copied chest is empty (Copy never duplicates contents)', chest_items_at(w, rel_chest) == {}, str(chest_items_at(w, rel_chest)))
    record('build: source chest keeps its loot', chest_items_at(w, HOUSE_CHEST) == CHEST_LOOT, str(chest_items_at(w, HOUSE_CHEST)))
    stock_is(w, dict(house.BOM), 'build: Warehouse charged exactly one house BOM')
    no_drops(w, 'build: no item entities dropped')
    trig('undo', 1.0); wait_sorted(18)
    save_world(); w = world()
    compare(w, {p: 'minecraft:air' for p in exp_built}, 'build undo: target back to air')
    stock_is(w, BOM2, 'build undo: materials refunded and re-sorted out of entry')
    no_drops(w, 'build undo: no item entities')
    trig('redo', 1.0); time.sleep(6)
    save_world(); w = world()
    compare(w, exp_built, 'build redo: 3D copy exact again')
    stock_is(w, dict(house.BOM), 'build redo: charged one BOM again')
    trig('undo', 1.0); wait_sorted(18)

if want('rotbuild'):
    for k, val, tx in ((1, 20, 1045), (2, 30, 1065), (3, 40, 1075)):
        log(f'=== Blueprint rotate {90 * k} -> Build')
        w, SRC = snapshot()
        T = (tx, Y0, 1060)
        trig('c'); trig(f'rotate set {val}')
        aim_target(T[0], T[2]); trig('v', 3.0)
        trig('build', 1.0); time.sleep(6)
        save_world(); w = world()
        exp = expect_placed(SRC, T, k=k)
        compare(w, exp, f'rotated build {90 * k}: exact blocks + rotated states', extra_air=box_around(exp))
        no_drops(w, f'rotated build {90 * k}: no drops')
        trig('undo', 1.0); wait_sorted(15)
        trig('rotate set 10')
    save_world(); stock_is(world(), BOM2, 'rotated builds: all refunds back in Warehouse')

if want('mirbuild'):
    for val, axis, tx in ((20, 'x', 1045), (30, 'z', 1065)):
        log(f'=== Blueprint mirror {axis} -> Build')
        w, SRC = snapshot()
        T = (tx, Y0, 1080)
        trig('c'); trig('rotate set 10'); trig(f'mirror set {val}')
        aim_target(T[0], T[2]); trig('v', 3.0)
        trig('build', 1.0); time.sleep(6)
        save_world(); w = world()
        exp = expect_placed(SRC, T, mirror=axis)
        ok = compare(w, exp, f'mirrored build {axis}: exact blocks + mirrored states', extra_air=box_around(exp))
        if not ok:
            other = expect_placed(SRC, T, mirror='z' if axis == 'x' else 'x')
            compare(w, other, f'(diagnostic) mirrored build {axis} matches the OTHER axis instead?')
        no_drops(w, f'mirrored build {axis}: no drops')
        trig('undo', 1.0); wait_sorted(15)
        trig('mirror set 10')
    save_world(); stock_is(world(), BOM2, 'mirrored builds: all refunds back in Warehouse')

if want('cut'):
    log('=== Cut -> V real move (with chest contents), Undo/Redo')
    w, SRC = snapshot()
    T = (1019, Y0, 1080)
    select_house()
    trig('x', 2.0)
    save_world(); w = world()
    compare(w, {p: 'minecraft:air' for p in SRC}, 'cut: source fully removed')
    no_drops(w, 'cut: no drops (door, lanterns, wall torch)')
    aim_target(T[0], T[2]); trig('v', 3.0)
    save_world(); w = world()
    exp = expect_placed(SRC, T)
    compare(w, exp, 'cut paste: exact 3D move', extra_air=box_around(exp))
    moved_chest = (T[0] + HOUSE_CHEST[0] - AX, T[1] + HOUSE_CHEST[1] - AY, T[2] + HOUSE_CHEST[2] - AZ)
    record('cut paste: chest contents moved with it', chest_items_at(w, moved_chest) == CHEST_LOOT, str(chest_items_at(w, moved_chest)))
    no_drops(w, 'cut paste: no drops')
    aim_target(T[0] + 20, T[2]); trig('v', 2.0)
    save_world(); w = world()
    again = expect_placed(SRC, (T[0] + 20, T[1], T[2]))
    record('cut clipboard consumed: second V places nothing', all(w.block(*p) == 'minecraft:air' for p in again), '')
    trig('undo', 1.5)
    save_world(); w = world()
    compare(w, {p: 'minecraft:air' for p in exp}, 'cut paste undo: target cleared')
    trig('undo', 1.5)
    save_world(); w = world()
    compare(w, SRC, 'cut undo: source restored exactly')
    record('cut undo: source chest loot restored once', chest_items_at(w, HOUSE_CHEST) == CHEST_LOOT, str(chest_items_at(w, HOUSE_CHEST)))
    no_drops(w, 'cut undo: no drops')

def direct(label, trigger, expect_fn, settle=2.5):
    save_world()
    w, SRC = snapshot()
    trig(trigger, settle)
    save_world(); w = world()
    exp = expect_fn(SRC)
    compare(w, exp, f'{label}: exact result', extra_air=[p for p in SRC if p not in exp])
    loot_at = [p for p, s in exp.items() if s.startswith('minecraft:chest')]
    record(f'{label}: chest contents preserved', any(chest_items_at(w, p) == CHEST_LOOT for p in loot_at), str([chest_items_at(w, p) for p in loot_at]))
    no_drops(w, f'{label}: no drops')
    trig('undo', settle)
    save_world(); w = world()
    compare(w, SRC, f'{label} undo: exact original')
    no_drops(w, f'{label} undo: no drops')

if want('direct'):
    log('=== Move / Flip / direct Rotate on the real house')
    select_house()
    cmd(f'tp @s 1002.5 {Y0} 1030.5 180 0')   # facing north: right = +x
    def shifted(dx, dy=0, dz=0):
        return lambda S: {(x + dx, y + dy, z + dz): s for (x, y, z), s in S.items()}
    direct('move right 3', 'right set 3', shifted(3))
    if 'moveonly' in ONLY: raise SystemExit
    direct('move up 2', 'up set 2', shifted(0, 2))
    cx = SX1 + SX2; cz = SZ1 + SZ2
    direct('flipx', 'flipx', lambda S: {(cx - x, y, z): xform.mirror_state(s, 'x') for (x, y, z), s in S.items()})
    direct('flipz', 'flipz', lambda S: {(x, y, cz - z): xform.mirror_state(s, 'z') for (x, y, z), s in S.items()})
    for k in (1, 2, 3):
        direct(f'rotate{90 * k}', f'rotate{90 * k}', lambda S, k=k: expect_placed(S, MARK1, k=k))

if want('pick'):
    log('=== Pick from Warehouse')
    cmd('clear @s')
    cmd(f'setblock 1030 {Y0} 1030 minecraft:stone_bricks')
    look_at_from(1030.5, Y0, 1033.5, 1030.5, Y0 + 0.5, 1030.5)
    time.sleep(1.0)  # let the client settle on the new view before the server raycasts it
    trig('pick', 2.0)
    save_world(); w = world()
    tot, _ = warehouse_stock(w)
    import glob
    pdat = sorted((WORLD / 'players' / 'data').glob('*.dat'), key=lambda p: p.stat().st_mtime)[-1] if (WORLD / 'players' / 'data').exists() else None
    inv = {}
    if pdat:
        import gzip
        pl = mcworld.parse_nbt(gzip.decompress(pdat.read_bytes()))
        for it in pl.get('Inventory', []): inv[it['id']] = inv.get(it['id'], 0) + it.get('count', 1)
    got = inv.get('minecraft:stone_bricks', 0)
    record('pick: player received stone bricks from Warehouse', got > 0 and tot.get('minecraft:stone_bricks', 0) == BOM2['minecraft:stone_bricks'] - got,
           f'player has {got}; warehouse now {tot.get("minecraft:stone_bricks", 0)} (was {BOM2["minecraft:stone_bricks"]})')
    cmd(f'setblock 1030 {Y0} 1030 air')

d.close_screens()
log('=== done: ' + ', '.join(f'{sum(1 for v in results.values() if v["ok"])} ok', ) + f' / {sum(1 for v in results.values() if not v["ok"])} fail')
