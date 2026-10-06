"""Stage 6: the player-relative turn/flip commands. Expected results are built from what the
player asked for, one world-frame step at a time (turn right = clockwise from above; flip
left-right = mirror across the player's own left-right), never from the pack's internal
rot/mirror scores. Verdicts come from the saved world."""
import sys; sys.argv = sys.argv[:1] + ['none']  # import helpers only; do not rerun stage 3
from stage3_house import *

YAW = {'south': 0, 'west': 90, 'north': 180, 'east': -90}
LR_AXIS = {'north': 'x', 'south': 'x', 'east': 'z', 'west': 'z'}  # left-right as the player sees it
FB_AXIS = {'north': 'z', 'south': 'z', 'east': 'x', 'west': 'x'}

def face(direction):
    cmd(f'tp @s ~ ~ ~ {YAW[direction]} 30', 0.6)

def apply_steps(src, pivot, target, steps):
    """steps: ('turn', k) quarter turns clockwise, or ('mirror', 'x'|'z'), in the order given."""
    out = {}
    for (x, y, z), s in src.items():
        dx, dz, st = x - pivot[0], z - pivot[2], s
        for kind, v in steps:
            if kind == 'turn':
                dx, dz = xform.rot_off(dx, dz, v); st = xform.rotate_state(st, v)
            else:
                if v == 'x': dx = -dx
                else: dz = -dz
                st = xform.mirror_state(st, v)
        out[(target[0] + dx, target[1] + (y - pivot[1]), target[2] + dz)] = st
    return out

def displays_match(w, exp, label):
    xs = [p[0] for p in exp]; zs = [p[2] for p in exp]
    disp = [e for e in w.entities_in(min(xs) - 2, Y0 - 1, min(zs) - 2, max(xs) + 2, Y0 + 6, max(zs) + 2) if e.get('id') == 'minecraft:block_display']
    def cell(e):
        p = e.get('Pos'); return tuple(int(v) for v in p) if all(float(v).is_integer() for v in p) else tuple(p)
    nonair = {p for p, s in exp.items() if s != 'minecraft:air'}
    bad = [(cell(e), mcworld.fmt(e.get('block_state'))) for e in disp if cell(e) not in exp or mcworld.fmt(e.get('block_state')) != exp[cell(e)]]
    return record(label, not bad and {cell(e) for e in disp} == nonair and len(disp) == len(nonair), f'{len(disp)}/{len(nonair)} bad={bad[:3]}')

def blueprint_case(name, target, ops):
    """ops: list of (facing, trigger, step) run after V; step is the world-frame step expected."""
    log(f'=== Blueprint: {name}')
    _, SRC = snapshot()
    trig('bpreset'); select_house(); trig('c')
    aim_target(target[0], target[2]); trig('v', 3.0)
    steps = []
    for facing, trigger, step in ops:
        face(facing); trig(trigger, 3.0)
        steps.append(step)
    d.screenshot(str(OUT / f'orient_{name}.png'))
    save_world(); w = world()
    exp = apply_steps(SRC, MARK1, target, steps)
    displays_match(w, exp, f'{name}: preview matches what was asked')
    trig('build', 1.0); time.sleep(8)
    save_world(); w = world()
    compare(w, exp, f'{name}: build matches the preview', extra_air=box_around(exp))
    no_drops(w, f'{name}: no drops')
    trig('undo', 1.0); time.sleep(18)

d.close_screens()
reload_packs()  # the new triggers must exist before anything runs
cmd('time set day'); cmd('weather clear'); cmd('difficulty peaceful'); cmd('kill @e[type=minecraft:item]')
T = (1045, Y0, 1060)
blueprint_case('north_turnright_then_flip', T, [
    ('north', 'bpturnright', ('turn', 1)),
    ('north', 'bpflip', ('mirror', LR_AXIS['north'])),
])
blueprint_case('east_flip_turnleft_flipfb', T, [
    ('east', 'bpflip', ('mirror', LR_AXIS['east'])),
    ('east', 'bpturnleft', ('turn', 3)),
    ('east', 'bpflipfb', ('mirror', FB_AXIS['east'])),
])
blueprint_case('west_turnright_x2_flipfb_turnleft', T, [
    ('west', 'bpturnright', ('turn', 1)),
    ('west', 'bpturnright', ('turn', 1)),
    ('west', 'bpflipfb', ('mirror', FB_AXIS['west'])),
    ('west', 'bpturnleft', ('turn', 3)),
])
log('=== bpreset returns the preview to the original direction')
_, SRC = snapshot()
select_house(); trig('c'); aim_target(T[0], T[2]); trig('v', 3.0)
face('north'); trig('bpturnright', 3.0); trig('bpflip', 3.0); trig('bpreset', 3.0)
save_world(); w = world()
displays_match(w, apply_steps(SRC, MARK1, T, []), 'bpreset: preview back to original')
trig('previewclear', 1.0)

log('=== direct edits on the real house, relative to facing')
select_house()
cx = SX1 + SX2; cz = SZ1 + SZ2
def direct_rel(label, facing, trigger, fn):
    cmd(f'tp @s 1002.5 {Y0} 1030.5 {YAW[facing]} 0', 0.8)
    direct(label, trigger, fn)
flipped = lambda axis: (lambda S: {((cx - x) if axis == 'x' else x, y, (cz - z) if axis == 'z' else z): xform.mirror_state(s, axis) for (x, y, z), s in S.items()})
direct_rel('turnright', 'north', 'turnright', lambda S: expect_placed(S, MARK1, k=1))
direct_rel('turnleft', 'north', 'turnleft', lambda S: expect_placed(S, MARK1, k=3))
direct_rel('flip facing north (left-right)', 'north', 'flip', flipped(LR_AXIS['north']))
direct_rel('flip facing east (left-right)', 'east', 'flip', flipped(LR_AXIS['east']))
direct_rel('flipfb facing north (front-back)', 'north', 'flipfb', flipped(FB_AXIS['north']))

log('=== screenshots: tutorial, main Dialog, direct-edit Dialog')
d.close_screens()
cmd('tp @s 1010.5 -55 1030.5 0 20')
trig('cphelp', 1.5); d.tap(0x54); time.sleep(0.8)
d.screenshot(str(OUT / 'tutorial.png')); d.esc(1); time.sleep(0.5)
trig('copypaste', 1.5); d.screenshot(str(OUT / 'dialog_main.png')); d.close_screens()
cmd('dialog show @s mcc:edit', 1.5); d.screenshot(str(OUT / 'dialog_edit.png')); d.close_screens()
