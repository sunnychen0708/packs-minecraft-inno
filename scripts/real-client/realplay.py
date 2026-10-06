"""Real-player verification of Warehouse + Copy/Paste in the MCC-Test world.

Every action is typed/clicked into the real Minecraft client through OS input
(mcdrive). Every verdict is taken from the saved world files (mcworld), never
from chat/log PASS lines.
"""
from __future__ import annotations
import json, math, os, re, sys, time
from pathlib import Path
from collections import Counter
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))  # scripts/ (mcc_house)
import mcdrive as d
import mcworld
import mcc_house as house

WORLD = Path(os.environ['APPDATA']) / '.minecraft' / 'saves' / os.environ.get('MCC_WORLD', 'MCC-Test')
OUT = Path(os.environ.get('MCC_REALPLAY_OUT', HERE.parents[1] / 'dist' / 'real-client'))
OUT.mkdir(parents=True, exist_ok=True)
RESULTS = OUT / 'realplay-results.json'
GY = -61          # superflat grass top layer
Y0 = GY + 1       # first air layer

# ---------- layout ----------
CODES = ['00'] + [f'{r}{s}' for r in range(1, 7) for s in range(10)]
def chest_pos(i):          # right half at (x, Y0, z), left half at (x+1, Y0, z); both face south
    return 1000 + 3 * (i % 16), 1000 + 5 * (i // 16)
BOX = {c: chest_pos(i) for i, c in enumerate(CODES)}
HOUSE_O = (1000, Y0, 1040)           # house origin (min corner)
MARK1 = (999, Y0, 1039)              # selection corners (temporary wool markers)
MARK2 = (1005, Y0 + 3, 1045)
SEL = (MARK1, MARK2)

def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(OUT / 'realplay.log', 'a', encoding='utf-8') as f: f.write(line + '\n')

results = json.loads(RESULTS.read_text(encoding='utf-8')) if RESULTS.exists() else {}
def record(name, ok, detail=''):
    results[name] = {'ok': bool(ok), 'detail': detail, 'time': time.strftime('%H:%M:%S')}
    RESULTS.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding='utf-8')
    log(f'{"OK  " if ok else "FAIL"} {name} {detail}')
    return ok

# ---------- game actions ----------
def cmd(c, settle=0.5): d.chat('/' + c, settle)
def trig(t, settle=1.2):
    """Run a trigger and require the game's own confirmation in the log."""
    pos = d.log_len()
    cmd('trigger ' + t, settle)
    name = t.split()[0]
    if not d.wait_log(pos, r'\[CHAT\] 已觸發 \[' + re.escape(name) + r'\]', 5):
        raise RuntimeError(f'trigger {name} was not confirmed by the game')

def reload_packs():
    """/reload, then wait for Copy/Paste's own load message; never continue on an unloaded pack."""
    pos = d.log_len()
    cmd('reload', 1.0)
    if not d.wait_log(pos, r'\[Copy/Paste\] v[0-9.]+ 已載入', 30):
        raise RuntimeError('reload not confirmed (no Copy/Paste load message)')
    time.sleep(1.0)

def save_world():
    """Pause (Esc) makes the integrated server save every chunk; then resume."""
    p = d.log_len()
    d.esc(1)
    ok = d.wait_log(p, r'Saving chunks for level .*the_nether', 25)
    time.sleep(2.5)
    d.esc(1)
    time.sleep(0.5)
    if not ok: raise RuntimeError('world save not observed')

def world():
    return mcworld.World(WORLD)

def look_down_at(x, y, z, h=4):
    """Hover above a block and look straight down (creative flight)."""
    cmd(f'tp @s {x + .5} {y + 1 + h} {z + .5} 0 90', 0.6)

def look_at_from(px, py, pz, tx, ty, tz):
    """Stand at (px,py,pz) feet and look at world point (tx,ty,tz)."""
    ex, ey, ez = px, py + 1.62, pz
    dx, dy, dz = tx - ex, ty - ey, tz - ez
    yaw = math.degrees(math.atan2(-dx, dz))
    pitch = -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
    cmd(f'tp @s {px} {py} {pz} {yaw:.2f} {pitch:.2f}', 0.6)

def fill_air(x1, y1, z1, x2, y2, z2):
    step = 30
    for x in range(x1, x2 + 1, step):
        for z in range(z1, z2 + 1, step):
            cmd(f'fill {x} {y1} {z} {min(x + step - 1, x2)} {y2} {min(z + step - 1, z2)} air', 0.25)

# ---------- world reads ----------
def region_blocks(w, a, b):
    (x1, y1, z1), (x2, y2, z2) = a, b
    return {(x, y, z): w.block(x, y, z) for x in range(min(x1, x2), max(x1, x2) + 1)
            for y in range(min(y1, y2), max(y1, y2) + 1) for z in range(min(z1, z2), max(z1, z2) + 1)}

def warehouse_stock(w):
    tot = Counter(); per = {}
    for c, (x, z) in BOX.items():
        cc = Counter()
        for xx in (x, x + 1):
            be = w.block_entity(xx, Y0, z)
            for k, v in mcworld.items_of(be).items(): cc[k] += v
        per[c] = cc; tot.update(cc)
    return tot, per

def item_entities(w, a=(990, Y0 - 2, 990), b=(1110, Y0 + 12, 1110)):
    return [e for e in w.entities_in(*a, *b) if e.get('id') == 'minecraft:item']

def storage(ns):
    import gzip
    p = WORLD / 'data' / ns / 'command_storage.dat'
    return mcworld.parse_nbt(gzip.decompress(p.read_bytes()))['data']['contents']

# ---------- leaving / entering the world (Dialog JSON only loads when a world opens) ----------
# Window coordinates for an 870x519 client window; screenshot first if the window size differs.
PAUSE_SAVE_QUIT, TITLE_SINGLEPLAYER, WORLD_FIRST_ROW, WORLD_PLAY = (433, 379), (433, 267), (283, 147), (276, 427)

def leave_world():
    """Esc -> 儲存並回到標題畫面; returns once the integrated server has stopped."""
    d.close_screens()
    pos = d.log_len()
    d.esc(1); time.sleep(1.5)
    d.click_rel(*PAUSE_SAVE_QUIT)
    if not d.wait_log(pos, r'Stopping server|Saving worlds|關閉伺服器', 30):
        raise RuntimeError('world did not close')
    time.sleep(4)

def join_world():
    """Title -> 單人遊戲 -> top world (MCC-Test is the most recently played) -> play; waits for Copy/Paste to load."""
    d.click_rel(*TITLE_SINGLEPLAYER); time.sleep(3)
    d.click_rel(*WORLD_FIRST_ROW); time.sleep(1)
    d.screenshot(str(OUT / 'join_world_list.png'))
    pos = d.log_len()
    d.click_rel(*WORLD_PLAY)
    if not d.wait_log(pos, r'\[Copy/Paste\] v[0-9.]+ 已載入', 90):
        raise RuntimeError('world did not load')
    time.sleep(4)
    return pos
