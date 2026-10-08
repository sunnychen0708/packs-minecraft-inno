"""Stage 13: Utilities vein mining gives vanilla experience for every chain-mined ore.

The player really mines (survival, sneaking, attack = RIGHT mouse on this machine) the first ore
of a small vein; the gained experience is read from the saved player data.
"""
import ctypes, gzip
from realplay import *

# Read the player's own key bindings instead of guessing (this machine: sneak = left Ctrl, hold).
_OPTS = dict(l.split(':', 1) for l in (Path(os.environ['APPDATA']) / '.minecraft' / 'options.txt').read_text(encoding='utf-8').splitlines() if ':' in l)
_VK = {'key.keyboard.left.control': 0xA2, 'key.keyboard.right.control': 0xA3, 'key.keyboard.left.shift': 0xA0, 'key.keyboard.right.shift': 0xA1}
VK_SNEAK = _VK[_OPTS['key_key.sneak']]
assert _OPTS.get('toggleCrouch') == 'false', 'sneak must be hold-to-sneak for this test'
ATTACK_BUTTON = _OPTS['key_key.attack']        # key.mouse.right on this machine
ORE_X, ORE_Z = 1100, 1100            # vein along +Z at the ground layer
PLAYER = (ORE_X + 0.5, Y0, ORE_Z - 2.5)

def player():
    files = sorted((WORLD / 'players' / 'data').glob('*.dat'), key=lambda p: p.stat().st_mtime)
    return mcworld.parse_nbt(gzip.decompress(files[-1].read_bytes()))

def xp_total():
    return player().get('XpTotal', 0)

def hold_attack(sec):
    """Attack is bound to the RIGHT mouse button on this machine."""
    d.focus()
    flags = (0x0008, 0x0010) if ATTACK_BUTTON == 'key.mouse.right' else (0x0002, 0x0004)
    down = d.INPUT(type=0); down.u.mi = d.MOUSEINPUT(0, 0, 0, flags[0], 0, 0)
    up = d.INPUT(type=0); up.u.mi = d.MOUSEINPUT(0, 0, 0, flags[1], 0, 0)
    d._send(down); time.sleep(sec); d._send(up)

def mine_vein(label, ore, n, pickaxe, expect_lo, expect_hi):
    log(f'=== {label}: {n} {ore} in a row, sneak + mine the first one')
    d.close_screens()
    cmd('gamemode survival'); cmd('kill @e[type=minecraft:experience_orb]'); cmd('kill @e[type=minecraft:item]')
    cmd(f'fill {ORE_X} {Y0} {ORE_Z} {ORE_X} {Y0 + 1} {ORE_Z + 6} minecraft:air')
    cmd(f'fill {ORE_X} {Y0} {ORE_Z} {ORE_X} {Y0} {ORE_Z + n - 1} minecraft:{ore}')
    cmd('clear @s'); cmd(f'item replace entity @s weapon.mainhand with {pickaxe}')
    cmd('xp set @s 0 levels'); cmd('xp set @s 0 points')
    look_at_from(*PLAYER, ORE_X + 0.5, Y0 + 0.5, ORE_Z + 0.02)
    time.sleep(1.0)
    save_world(); before = xp_total()
    d._send(d._key(VK_SNEAK)); time.sleep(0.4)
    hold_attack(0.9)                                 # just long enough to break the first ore by hand
    time.sleep(0.6); d._send(d._key(VK_SNEAK, True))
    time.sleep(4.0)                                  # let the orbs fly to the player
    d.screenshot(str(OUT / f'vein_{label}.png'))
    save_world(); w = world()
    left = [z for z in range(ORE_Z, ORE_Z + n) if w.block(ORE_X, Y0, z) != 'minecraft:air']
    gained = xp_total() - before
    orbs = [e for e in w.entities_in(ORE_X - 3, Y0 - 1, ORE_Z - 4, ORE_X + 3, Y0 + 3, ORE_Z + 8) if e.get('id') == 'minecraft:experience_orb']
    gained += sum(e.get('Value', 0) * e.get('Count', 1) for e in orbs)   # anything not picked up yet
    record(f'{label}: whole vein mined', not left, f'left={left}')
    record(f'{label}: experience {expect_lo}..{expect_hi}', expect_lo <= gained <= expect_hi, f'gained {gained} (orbs left {len(orbs)})')
    cmd('gamemode creative'); cmd('clear @s')

d.close_screens()
mine_vein('diamond', 'diamond_ore', 4, 'minecraft:diamond_pickaxe', 4 * 3, 4 * 7)
mine_vein('diamond_silk_touch', 'diamond_ore', 4, 'minecraft:diamond_pickaxe[minecraft:enchantments={"minecraft:silk_touch":1}]', 0, 0)
mine_vein('iron', 'iron_ore', 4, 'minecraft:diamond_pickaxe', 0, 0)
cmd(f'fill {ORE_X} {Y0} {ORE_Z} {ORE_X} {Y0 + 1} {ORE_Z + 6} minecraft:air')
d.close_screens()
