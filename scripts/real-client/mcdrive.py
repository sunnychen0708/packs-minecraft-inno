"""Drive the real Minecraft client window with OS-level keyboard/mouse input (Windows SendInput)."""
from __future__ import annotations
import ctypes, ctypes.wintypes as wt, os, re, time
from pathlib import Path

user32 = ctypes.WinDLL('user32', use_last_error=True)
LOG = Path(os.environ['APPDATA']) / '.minecraft' / 'logs' / 'latest.log'

ULONG_PTR = ctypes.c_size_t
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [('dx', wt.LONG), ('dy', wt.LONG), ('mouseData', wt.DWORD), ('dwFlags', wt.DWORD), ('time', wt.DWORD), ('dwExtraInfo', ULONG_PTR)]
class KEYBDINPUT(ctypes.Structure):
    _fields_ = [('wVk', wt.WORD), ('wScan', wt.WORD), ('dwFlags', wt.DWORD), ('time', wt.DWORD), ('dwExtraInfo', ULONG_PTR)]
class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [('uMsg', wt.DWORD), ('wParamL', wt.WORD), ('wParamH', wt.WORD)]
class _U(ctypes.Union):
    _fields_ = [('mi', MOUSEINPUT), ('ki', KEYBDINPUT), ('hi', HARDWAREINPUT)]
class INPUT(ctypes.Structure):
    _fields_ = [('type', wt.DWORD), ('u', _U)]

KEYUP, UNICODE, SCANCODE = 0x2, 0x4, 0x8
def _send(*inputs):
    arr = (INPUT * len(inputs))(*inputs)
    n = user32.SendInput(len(inputs), arr, ctypes.sizeof(INPUT))
    if n != len(inputs): raise OSError(ctypes.get_last_error(), 'SendInput blocked')

def _key(vk, up=False):
    sc = user32.MapVirtualKeyW(vk, 0)
    i = INPUT(type=1); i.u.ki = KEYBDINPUT(vk, sc, KEYUP if up else 0, 0, 0); return i

def tap(vk, hold=0.05):
    _send(_key(vk)); time.sleep(hold); _send(_key(vk, True)); time.sleep(0.05)

def type_text(s):
    for ch in s:
        d = INPUT(type=1); d.u.ki = KEYBDINPUT(0, ord(ch), UNICODE, 0, 0)
        u = INPUT(type=1); u.u.ki = KEYBDINPUT(0, ord(ch), UNICODE | KEYUP, 0, 0)
        _send(d, u); time.sleep(0.012)

def right_click(hold=0.08):
    d = INPUT(type=0); d.u.mi = MOUSEINPUT(0, 0, 0, 0x0008, 0, 0)
    u = INPUT(type=0); u.u.mi = MOUSEINPUT(0, 0, 0, 0x0010, 0, 0)
    _send(d); time.sleep(hold); _send(u); time.sleep(0.1)

VK_RETURN, VK_ESCAPE, VK_MENU, VK_T, VK_OEM2 = 0x0D, 0x1B, 0x12, 0x54, 0xBF

def find_window():
    pids = set()
    import subprocess
    out = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq javaw.exe', '/FO', 'CSV', '/NH'], capture_output=True, text=True).stdout
    for line in out.splitlines():
        parts = line.strip('"').split('","')
        if len(parts) > 1 and parts[1].isdigit(): pids.add(int(parts[1]))
    found = []
    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(h, _):
        pid = wt.DWORD(); user32.GetWindowThreadProcessId(h, ctypes.byref(pid))
        if pid.value in pids and user32.IsWindowVisible(h):
            buf = ctypes.create_unicode_buffer(256); user32.GetWindowTextW(h, buf, 256)
            if 'Minecraft' in buf.value: found.append(h)
        return True
    user32.EnumWindows(cb, 0)
    if not found: raise RuntimeError('Minecraft window not found')
    return found[0]

HWND = None
def focus():
    global HWND
    HWND = HWND or find_window()
    if user32.IsIconic(HWND): user32.ShowWindow(HWND, 9)
    for _ in range(5):
        if user32.GetForegroundWindow() == HWND: return
        tap(VK_MENU, 0.01)
        user32.SetForegroundWindow(HWND)
        time.sleep(0.4)
    if user32.GetForegroundWindow() != HWND: raise RuntimeError('cannot focus Minecraft')

def log_len():
    return LOG.stat().st_size

def log_since(pos):
    with open(LOG, 'rb') as f:
        f.seek(pos); return f.read().decode('utf-8', 'replace')

def wait_log(pos, pattern, timeout=20.0):
    rx = re.compile(pattern); t = time.time() + timeout
    while time.time() < t:
        s = log_since(pos)
        m = rx.search(s)
        if m: return m
        time.sleep(0.25)
    return None

def chat(cmd, settle=0.6):
    """Open chat with T, type the command like a player, press Enter."""
    focus()
    tap(VK_T); time.sleep(0.35)
    type_text(cmd); time.sleep(0.15)
    tap(VK_RETURN); time.sleep(settle)

def esc(n=1):
    focus()
    for _ in range(n): tap(VK_ESCAPE); time.sleep(0.3)

def screenshot(path):
    from PIL import ImageGrab
    focus()
    r = wt.RECT(); user32.GetWindowRect(HWND, ctypes.byref(r))
    ImageGrab.grab(bbox=(r.left, r.top, r.right, r.bottom), all_screens=True).save(path)
    return path

def save_all(timeout=20):
    p = log_len()
    chat('/save-all flush', settle=0.3)
    m = wait_log(p, r'\[CHAT\] [^\n]*(Saved|已儲存|儲存完成|存檔)', timeout)
    time.sleep(1.0)
    return log_since(p)

def click_rel(rx, ry, button='left'):
    """Click at a point given in window-screenshot coordinates (as seen in screenshot())."""
    focus()
    r = wt.RECT(); user32.GetWindowRect(HWND, ctypes.byref(r))
    user32.SetCursorPos(int(r.left + rx), int(r.top + ry)); time.sleep(0.15)
    down, up = (0x0002, 0x0004) if button == 'left' else (0x0008, 0x0010)
    i = INPUT(type=0); i.u.mi = MOUSEINPUT(0, 0, 0, down, 0, 0); _send(i); time.sleep(0.06)
    i = INPUT(type=0); i.u.mi = MOUSEINPUT(0, 0, 0, up, 0, 0); _send(i); time.sleep(0.3)

def window_size():
    r = wt.RECT(); user32.GetWindowRect(HWND or find_window(), ctypes.byref(r))
    return r.right - r.left, r.bottom - r.top

def sharpness():
    from PIL import ImageGrab, ImageFilter, ImageStat
    focus()
    r = wt.RECT(); user32.GetWindowRect(HWND, ctypes.byref(r))
    w, h = r.right - r.left, r.bottom - r.top
    im = ImageGrab.grab(bbox=(r.left, r.top, r.right, r.bottom), all_screens=True).convert('L')
    box = (int(w * 0.29), int(h * 0.895), int(w * 0.707), int(h * 0.978))
    return ImageStat.Stat(im.crop(box).filter(ImageFilter.FIND_EDGES)).mean[0]

def in_game():
    return sharpness() > 38

def close_screens(max_esc=6):
    for _ in range(max_esc):
        time.sleep(0.35)
        if in_game(): return True
        tap(VK_ESCAPE); time.sleep(0.5)
    return in_game()

def left_click_here():
    i = INPUT(type=0); i.u.mi = MOUSEINPUT(0, 0, 0, 0x0002, 0, 0); _send(i); time.sleep(0.06)
    i = INPUT(type=0); i.u.mi = MOUSEINPUT(0, 0, 0, 0x0004, 0, 0); _send(i); time.sleep(0.2)

def click_dialog_button(rx, ry):
    """Click a Dialog button; the caller must be looking at the sky. A second
    left click while still looking at the sky releases the attack key that the
    game re-latches when the dialog closes on mouse-down."""
    click_rel(rx, ry); time.sleep(0.6)
    left_click_here(); time.sleep(0.3)

# This player's options.txt binds key.use to the LEFT mouse button and key.attack to RIGHT.
def use_click():
    left_click_here()

def click_dialog_button(rx, ry):
    click_rel(rx, ry); time.sleep(0.6)
