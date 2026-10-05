from realplay import *
log('=== stage 1: prep + real large chests')
cmd('difficulty peaceful'); cmd('time set day'); cmd('weather clear'); cmd('gamemode creative')
cmd('clear @s'); cmd('kill @e[type=minecraft:item]')
look_down_at(1040, GY, 1040, 6)
time.sleep(3)
fill_air(995, Y0, 995, 1100, Y0 + 10, 1100)
for c, (x, z) in BOX.items():
    cmd(f'setblock {x} {Y0} {z} chest[facing=south,type=right]', 0.15)
    cmd(f'setblock {x+1} {Y0} {z} chest[facing=south,type=left]', 0.15)
time.sleep(1)
save_world()
w = world()
bad = []
for c, (x, z) in BOX.items():
    r, l = w.block(x, Y0, z), w.block(x + 1, Y0, z)
    if 'type=right' not in r or 'type=left' not in l or 'facing=south' not in r: bad.append((c, r, l))
record('layout: 61 real large chests (right+left halves joined, facing south)', not bad, f'bad={bad[:3]}')
