"""Stage 12: Utilities + Warehouse + Copy/Paste installed together in the real client.

Leaves the world, installs the three ZIPs given on the command line (replacing older copies of
the same packs), re-enters, and checks: all three load without errors, G opens the Warehouse main
page, Utilities sethome / home / back move the player (read from the saved player data), and
/trigger help answers. The Copy/Paste + Warehouse stages are run separately afterwards.

    python stage12_all_packs.py <dir with utilities-*.zip warehouse-*.zip copy-paste-*.zip>
"""
import gzip, re, shutil, sys
from pathlib import Path
from realplay import *

SRC = Path(sys.argv[1])
VK_G = 0x47

def player_pos():
    files = sorted((WORLD / 'players' / 'data').glob('*.dat'), key=lambda p: p.stat().st_mtime)
    return mcworld.parse_nbt(gzip.decompress(files[-1].read_bytes())).get('Pos')

def near(pos, x, z, tol=1.5):
    return pos and abs(pos[0] - x) <= tol and abs(pos[2] - z) <= tol

RESUME = len(sys.argv) > 2 and sys.argv[2] == 'resume'   # world already loaded with the new packs
log('=== leave the world and install all three packs')
if not RESUME: leave_world()
packs = WORLD / 'datapacks'
if not RESUME:
    backup = Path(os.environ['APPDATA']) / '.minecraft' / 'backups' / f'MCC-Test-before-allpacks-{time.strftime("%Y%m%d-%H%M")}'
    shutil.copytree(WORLD, backup, ignore=shutil.ignore_patterns('session.lock'))
    log(f'    backup: {backup}')
    for z in SRC.glob('*.zip'):
        stem = re.sub(r'-v[0-9.]+$', '', z.stem)            # utilities / warehouse / copy-paste
        for old in packs.glob(f'{stem}-v*.zip'):
            old.unlink()
        shutil.copy2(z, packs / z.name)
    log(f'    datapacks now: {sorted(p.name for p in packs.iterdir())}')

log('=== re-enter the world')
if RESUME:
    d.click_rel(*EXPERIMENTAL_OK); pos = d.log_len() - 200000
    d.wait_log(max(pos, 0), r'\[Copy/Paste\] v[0-9.]+ 已載入', 90); time.sleep(4)
else:
    pos = join_world()
chat = [l.split('[CHAT] ', 1)[1] for l in d.log_since(pos).splitlines() if '[System] [CHAT] ' in l]
errors = [l for l in d.log_since(pos).splitlines() if re.search(r'Failed to load|Couldn\'t load|Failed to parse|Unknown function|Errors in currently selected', l)]
record('all packs: Utilities load message', any('[屁眼派對]' in l and '已載入' in l for l in chat), ' | '.join(l for l in chat if '已載入' in l))
record('all packs: Copy/Paste load message tells players to press G', any('[Copy/Paste]' in l and '按 G' in l for l in chat), '')
record('all packs: no datapack load errors', not errors, ' | '.join(errors[:3]))
d.screenshot(str(OUT / 'allpacks_joined.png'))

log('=== G opens the Warehouse main page')
d.close_screens()
cmd('tp @s ~ ~ ~ 0 -90', 0.6)
d.tap(VK_G); time.sleep(1.5)
d.screenshot(str(OUT / 'allpacks_G.png'))
record('all packs: G opened a Dialog', not d.in_game(), 'see allpacks_G.png')
d.close_screens()

log('=== Utilities: sethome -> walk away -> home -> back')
cmd(f'tp @s 1010.5 {Y0} 1020.5 0 0', 0.8)
trig('sethome', 1.5)
cmd(f'tp @s 1060.5 {Y0} 1060.5 0 0', 0.8)
trig('home', 2.0)
save_world(); p1 = player_pos()
record('utilities: home teleports to the saved spot', near(p1, 1010.5, 1020.5), str(p1))
trig('back', 2.0)
save_world(); p2 = player_pos()
record('utilities: back returns to where home was used', near(p2, 1060.5, 1060.5), str(p2))
pos = d.log_len(); trig('help', 1.5)
helpl = [l for l in d.log_since(pos).splitlines() if '[System] [CHAT] ' in l]
record('utilities: /trigger help answers', len(helpl) > 3, f'{len(helpl)} chat lines')
d.tap(0x54); time.sleep(0.8); d.screenshot(str(OUT / 'allpacks_help.png')); d.esc(1)
d.close_screens()
