"""Stage 7: the slimmed-down Copy/Paste Dialogs. Screenshots of every page, and the paste-mode
button must name the active mode and actually switch it (mcc_mask read from the saved world)."""
import gzip
from realplay import *

def mask():
    p = WORLD / 'data' / 'minecraft' / 'scoreboard.dat'
    d0 = mcworld.parse_nbt(gzip.decompress(p.read_bytes()))['data']
    return next((s.get('Score', 0) for s in d0['PlayerScores'] if s.get('Objective') == 'mcc_mask' and not s.get('Name', '').startswith('#')), 0)

d.close_screens()
reload_packs()
cmd('tp @s 1010.5 -55 1030.5 0 20')
for value, name in ((1, 'main'), (2, 'adjust'), (3, 'more'), (4, 'edit')):
    trig(f'copypaste set {value}', 1.5)
    d.screenshot(str(OUT / f'menu_{name}.png'))
    record(f'menu {name}: Dialog opened', not d.in_game(), '')
    d.close_screens()
save_world(); m0 = mask()
pos = d.log_len()
trig('mode set 2', 1.5)
d.screenshot(str(OUT / 'menu_more_after_toggle.png'))
record('paste mode button reopens the More page', not d.in_game(), '')
d.close_screens()
save_world(); m1 = mask()
record('paste mode actually switched', m1 == 1 - m0, f'mcc_mask {m0} -> {m1}; chat: {[l.split("[CHAT] ")[-1] for l in d.log_since(pos).splitlines() if "貼上模式" in l]}')
trig('mode set 2', 1.5); d.close_screens()
save_world(); record('paste mode switched back', mask() == m0, f'mcc_mask now {mask()}')
