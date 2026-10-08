"""Stage 8: material lists show item names in the player's language (translation keys),
not raw ids. Read from the client's own chat log and screenshots."""
import sys; sys.argv = sys.argv[:1] + ['none']  # import helpers only; do not rerun stage 3
from stage3_house import *

def chat_lines(pos):
    return [l.split('[CHAT] ', 1)[1] for l in d.log_since(pos).splitlines() if '[Render thread/INFO]: [System] [CHAT] ' in l]

d.close_screens()
reload_packs()
cmd('time set day'); cmd('weather clear')
T = (1045, Y0, 1060)
reset_xform(); select_house(); trig('c')
aim_target(T[0], T[2]); trig('v', 4.0)
log('=== material check list')
pos = d.log_len()
trig('materials', 1.0); time.sleep(6)
d.tap(0x54); time.sleep(0.8); d.screenshot(str(OUT / 'names_materials.png')); d.esc(1)
lines = chat_lines(pos)
rows = [l for l in lines if 'Warehouse' in l and '/' in l]
record('materials list: names, not ids', rows and not any('minecraft:' in l for l in rows), ' | '.join(rows[:4]))
record('materials list: zh_tw names shown', any('橡木門' in l for l in rows) and any('石磚' in l for l in rows), f'{len(rows)} rows')
log('=== shortage list (one diamond block the Warehouse does not have)')
trig('previewclear', 1.0)
cmd(f'setblock {MARK1[0]} {MARK1[1]} {MARK1[2]} minecraft:diamond_block')
trig('c')
aim_target(T[0], T[2]); trig('v', 4.0)
pos = d.log_len()
trig('build', 1.0); time.sleep(6)
d.tap(0x54); time.sleep(0.8); d.screenshot(str(OUT / 'names_shortage.png')); d.esc(1)
lines = chat_lines(pos)
miss = [l for l in lines if '×' in l]
record('shortage list: diamond block named in zh_tw', any('鑽石方塊' in l for l in miss) and not any('minecraft:' in l for l in miss), ' | '.join(miss))
trig('previewclear', 1.0)
cmd(f'setblock {MARK1[0]} {MARK1[1]} {MARK1[2]} air')
d.close_screens()
