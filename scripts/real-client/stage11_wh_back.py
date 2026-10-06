"""Stage 11: Warehouse back buttons return to the page the player came from. Everything is
clicked with the real mouse; each step is screenshotted (titles are checked by eye) and the
navigation trigger the button sent is read from the client log."""
from realplay import *

SHOTS = OUT / 'wh_back'; SHOTS.mkdir(exist_ok=True)
EXIT = (433, 478)          # exit / notice button, bottom centre of an 870x519 window
SPECIAL = {}               # filled from screenshots of the entry/overflow pages

def sky():
    cmd('tp @s ~ ~ ~ 0 -90', 0.6)

def shot(name):
    time.sleep(0.8); d.screenshot(str(SHOTS / f'{name}.png'))

def click(name, x, y):
    pos = d.log_len()
    d.click_rel(x, y); time.sleep(1.5)
    shot(name)
    return [l.split('[CHAT] ', 1)[1] for l in d.log_since(pos).splitlines() if '[System] [CHAT] ' in l]

def cell(i):
    """Window position of box i (1-9) on a 3x3 region page."""
    return (189 + 244 * ((i - 1) % 3), 230 + 44 * ((i - 1) // 3))

def flow(name, nav, box_xy, back_xy=EXIT):
    d.close_screens(); sky()
    trig(f'wh_nav set {nav}', 1.5)
    shot(f'{name}_0_list')
    log(f'=== {name}: box click -> {click(f"{name}_1_open", *box_xy)}')
    log(f'    back click -> {click(f"{name}_2_back", *back_xy)}')

d.close_screens()
reload_packs()
def look_at_chest(code):
    x, z = BOX[code]
    cmd(f'tp @s {x + 0.5} {Y0} {z + 2.5} 180 -90', 0.6)

def register_via_ui(name, code, region_nav, idx):
    d.close_screens(); look_at_chest(code)
    trig(f'wh_nav set {region_nav}', 1.5)
    click(f'{name}_1_armed', *cell(idx))
    click(f'{name}_2_started', 281, 302)            # 開始註冊 closes the Dialog
    x, z = BOX[code]
    look_at_from(x + 0.5, Y0, z + 2.5, x + 0.5, Y0 + 0.4, z + 0.5)
    time.sleep(0.4); d.use_click(); time.sleep(1.5)
    shot(f'{name}_3_result')

log('=== 52 is unregistered now: unregister list -> 52 -> "not registered" notice -> 返回')
d.close_screens(); sky(); trig('wh_nav set 55', 1.5)
log(f'    box click -> {click("notreg_52_1_notice", *cell(2))}')
log(f'    back click -> {click("notreg_52_2_back", *EXIT)}')
log('=== register 52 through the UI -> success -> 回箱子註冊')
register_via_ui('register_52', '52', 15, 2)
log(f'    回箱子註冊 -> {click("register_52_4_back", 281, 230)}')
log('=== unregister 52 -> done -> 返回')
d.close_screens(); sky(); trig('wh_nav set 55', 1.5)
click('unregister_52_b_1_confirm', *cell(2))
click('unregister_52_b_2_done', 266, 478)
log(f'    返回 -> {click("unregister_52_b_3_back", *EXIT)}')
log('=== register 52 again (restore)')
register_via_ui('register_52_restore', '52', 15, 2)
d.close_screens()
save_world()
e = storage('warehouse')['chests'].get('c52', {})
x, z = BOX['52']
record('52 registered back to its own large chest', e.get('registered') == 1 and e.get('valid') == 1 and
       {(e.get('a_x'), e.get('a_z')), (e.get('b_x'), e.get('b_z'))} == {(x, z), (x + 1, z)}, str(e))
