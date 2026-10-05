from realplay import *
log('=== stage 2: register all 61 large chests through the real Warehouse UI + real use-click')
def register(code):
    x, z = BOX[code]
    for attempt in range(3):
        d.close_screens()
        cmd(f'tp @s {x+0.5} {Y0} {z+2.5} 180 -90')
        trig(f'wh_register set {100 if code == "00" else int(code)}', 1.0)
        if d.in_game(): log(f'{code}: armed dialog did not open'); continue
        d.click_dialog_button(281, 302)
        if not d.in_game(): log(f'{code}: dialog still open after 開始註冊'); continue
        look_at_from(x + 0.5, Y0, z + 2.5, x + 0.5, Y0 + 0.4, z + 0.5)
        time.sleep(0.4); d.use_click(); time.sleep(1.2)
        if d.in_game(): log(f'{code}: no result dialog after use-click'); continue
        d.screenshot(str(OUT / 'reg' / f'{code}.png'))
        d.close_screens()
        # the chest must still be whole
        return True
    return False
(OUT / 'reg').mkdir(exist_ok=True)
for code in CODES[1:]:
    ok = register(code)
    log(f'register {code}: {"done" if ok else "GAVE UP"}')
d.close_screens()
save_world()
st = storage('warehouse')['chests']
bad = []
for code, (x, z) in BOX.items():
    e = st.get(f'c{code}', {})
    halves = {(e.get('a_x'), e.get('a_y'), e.get('a_z')), (e.get('b_x'), e.get('b_y'), e.get('b_z'))}
    if not (e.get('registered') == 1 and e.get('valid') == 1 and halves == {(x, Y0, z), (x + 1, Y0, z)}): bad.append((code, e.get('registered'), e.get('valid'), halves))
record('warehouse: all 61 codes registered to the correct large chest via UI + click', not bad, f'bad={bad[:5]}')
w = world()
broken = [c for c, (x, z) in BOX.items() if 'chest' not in w.block(x, Y0, z) or 'chest' not in w.block(x + 1, Y0, z)]
record('warehouse: no chest half broken during registration', not broken, f'broken={broken}')
