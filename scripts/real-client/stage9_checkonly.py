"""Stage 9: with complete Warehouse stock, the material check only reports.
The target must stay air and every chest must be unchanged (read from the saved world)."""
import sys; sys.argv = sys.argv[:1] + ['none']  # import helpers only; do not rerun stage 3
from stage3_house import *

d.close_screens()
reload_packs()
log('=== top up Warehouse so one house BOM is complete')
save_world(); tot, _ = warehouse_stock(world())
x0, z0 = BOX['00']; slot = 0
for k, v in house.BOM.items():
    if tot.get(k, 0) < v:
        cmd(f'item replace block {x0} {Y0} {z0} container.{slot} with {k} {v - tot.get(k, 0)}', 0.3); slot += 1
time.sleep(20)
save_world(); w0 = world(); before, per0 = warehouse_stock(w0)
record('setup: Warehouse holds at least one full BOM', all(before.get(k, 0) >= v for k, v in house.BOM.items()) and not per0['00'], str({k: before.get(k, 0) for k in house.BOM}))
T = (1045, Y0, 1060)
_, SRC = snapshot()
reset_xform(); select_house(); trig('c')
aim_target(T[0], T[2]); trig('v', 4.0)
pos = d.log_len()
trig('materials', 1.0); time.sleep(10)
d.tap(0x54); time.sleep(0.8); d.screenshot(str(OUT / 'checkonly.png')); d.esc(1)
chat = [l.split('[CHAT] ', 1)[1] for l in d.log_since(pos).splitlines() if '[System] [CHAT] ' in l]
save_world(); w = world()
exp = expect_placed(SRC, T)
record('check only: nothing built', all(w.block(*p) == 'minecraft:air' for p in exp), '')
after, per1 = warehouse_stock(w)
record('check only: every chest unchanged', per1 == per0, '')
record('check only: no build / shortage message', not any('施工' in l and ('完成' in l or '未施工' in l) for l in chat), ' | '.join(chat[-4:]))
trig('previewclear', 1.0)
d.close_screens()
