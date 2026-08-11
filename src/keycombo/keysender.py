"""
keysender.py
Gère la détection des fenêtres Windows et l'envoi de combinaisons de touches
à une application cible précise.
"""

import time
import win32gui
import win32con
import win32process
import win32api
import win32com.client
import psutil


MODIFIER_KEYS = {
    "ctrl": win32con.VK_CONTROL,
    "shift": win32con.VK_SHIFT,
    "alt": win32con.VK_MENU,
    "win": win32con.VK_LWIN,
}

SPECIAL_KEYS = {
    "enter": win32con.VK_RETURN,
    "tab": win32con.VK_TAB,
    "esc": win32con.VK_ESCAPE,
    "escape": win32con.VK_ESCAPE,
    "space": win32con.VK_SPACE,
    "backspace": win32con.VK_BACK,
    "delete": win32con.VK_DELETE,
    "up": win32con.VK_UP,
    "down": win32con.VK_DOWN,
    "left": win32con.VK_LEFT,
    "right": win32con.VK_RIGHT,
    "home": win32con.VK_HOME,
    "end": win32con.VK_END,
    "pageup": win32con.VK_PRIOR,
    "pagedown": win32con.VK_NEXT,
}
for i in range(1, 13):
    SPECIAL_KEYS[f"f{i}"] = getattr(win32con, f"VK_F{i}")


def key_to_vk(key: str) -> int:
    """Convertit un nom de touche ('ctrl', 'a', 'f5', ...) en code virtuel Windows."""
    key = key.strip().lower()
    if key in MODIFIER_KEYS:
        return MODIFIER_KEYS[key]
    if key in SPECIAL_KEYS:
        return SPECIAL_KEYS[key]
    if len(key) == 1:
        vk = win32api.VkKeyScan(key) & 0xFF
        if vk == 0xFF:
            raise ValueError(f"Touche inconnue : {key}")
        return vk
    raise ValueError(f"Touche inconnue : {key}")


def list_windows():
    """Retourne la liste des fenêtres visibles : [(hwnd, titre, nom_exe), ...]"""
    windows = []

    def enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            title = win32gui.GetWindowText(hwnd)
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                exe = psutil.Process(pid).name()
            except Exception:
                exe = "?"
            windows.append((hwnd, title, exe))

    win32gui.EnumWindows(enum_handler, None)
    return windows


def find_hwnd_by_exe(exe_name: str):
    """Retrouve le handle de fenêtre actuel d'une application via son .exe."""
    for hwnd, title, exe in list_windows():
        if exe.lower() == exe_name.lower():
            return hwnd
    return None


def send_combo_via_focus(hwnd, keys, restore_focus=True):
    """
    Active la fenêtre cible, envoie la combinaison de touches (touches réelles),
    puis restaure la fenêtre précédemment active.
    C'est le mode le plus fiable : il fonctionne avec quasiment toutes les applications.
    """
    previous_hwnd = win32gui.GetForegroundWindow()

    # Astuce requise par Windows pour autoriser un changement de focus
    # déclenché par une autre application.
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        pass
    time.sleep(0.05)

    vk_codes = [key_to_vk(k) for k in keys]

    for vk in vk_codes:
        win32api.keybd_event(vk, 0, 0, 0)
        time.sleep(0.01)
    for vk in reversed(vk_codes):
        win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.01)

    if restore_focus and previous_hwnd:
        time.sleep(0.05)
        try:
            win32gui.SetForegroundWindow(previous_hwnd)
        except Exception:
            pass


def send_combo_via_postmessage(hwnd, keys):
    """
    Envoie la combinaison directement à la fenêtre cible SANS changer le focus.
    Ne fonctionne que sur certaines applications Win32 classiques
    (pas les jeux, pas les apps DirectX/UWP en général).
    """
    vk_codes = [key_to_vk(k) for k in keys]
    for vk in vk_codes:
        win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, vk, 0)
        time.sleep(0.01)
    for vk in reversed(vk_codes):
        win32gui.PostMessage(hwnd, win32con.WM_KEYUP, vk, 0)
        time.sleep(0.01)
