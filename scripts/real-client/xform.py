"""Vanilla-equivalent block-state rotate/mirror (reference for expected results)."""
DIRS = ['north', 'east', 'south', 'west']
CW = {d: DIRS[(i + 1) % 4] for i, d in enumerate(DIRS)}

def parse(s):
    if '[' not in s: return s, {}
    n, p = s[:-1].split('[', 1)
    return n, dict(kv.split('=', 1) for kv in p.split(','))

def fmt(n, p):
    return n + ('[' + ','.join(f'{k}={v}' for k, v in sorted(p.items())) + ']' if p else '')

def rot_dir(d, k):
    for _ in range(k % 4): d = CW[d]
    return d

def rotate_state(s, k):
    """k quarter turns clockwise (seen from above)."""
    n, p = parse(s); k %= 4
    if k == 0: return s
    q = dict(p)
    if p.get('facing') in CW: q['facing'] = rot_dir(p['facing'], k)
    if 'axis' in p and k % 2 == 1 and p['axis'] in ('x', 'z'): q['axis'] = 'z' if p['axis'] == 'x' else 'x'
    if all(d in p for d in DIRS):
        for d in DIRS: q[rot_dir(d, k)] = p[d]
    if 'rotation' in p: q['rotation'] = str((int(p['rotation']) + 4 * k) % 16)
    return fmt(n, q)

SWAP_LR = {'inner_left': 'inner_right', 'inner_right': 'inner_left', 'outer_left': 'outer_right', 'outer_right': 'outer_left', 'straight': 'straight'}

def mirror_state(s, axis):
    """axis='x': reflect x (vanilla FRONT_BACK, east<->west); axis='z': reflect z (LEFT_RIGHT, north<->south)."""
    n, p = parse(s); q = dict(p)
    flip = {'x': {'east': 'west', 'west': 'east'}, 'z': {'north': 'south', 'south': 'north'}}[axis]
    f = p.get('facing')
    along = f in flip
    base = n.split(':')[1]
    if base.endswith('_stairs'):
        if along: q['facing'] = flip[f]; q['shape'] = SWAP_LR[p['shape']]
    elif base.endswith('_door'):
        if along: q['facing'] = flip[f]
        q['hinge'] = 'right' if p['hinge'] == 'left' else 'left'
    elif base in ('chest', 'trapped_chest') or base.endswith('copper_chest'):
        if along: q['facing'] = flip[f]
        q['type'] = {'left': 'right', 'right': 'left'}.get(p.get('type'), p.get('type'))
    elif f in ('north', 'east', 'south', 'west'):
        if along: q['facing'] = flip[f]
    if all(d in p for d in DIRS):
        for a, b in flip.items(): q[b] = p[a]
    return fmt(n, q)

def rot_off(dx, dz, k):
    for _ in range(k % 4): dx, dz = -dz, dx
    return dx, dz
