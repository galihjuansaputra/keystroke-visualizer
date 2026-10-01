"""
hook.py - Global Low-Level Windows Keyboard and Mouse Hooks with PyQt6 QThread
"""

import ctypes
from ctypes import wintypes
import time
from PyQt6.QtCore import QThread, pyqtSignal
from keys import KeyFormatter, MODIFIER_KEYS

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Hook types
WH_KEYBOARD_LL = 13
WH_MOUSE_LL = 14

# Windows messages
# Windows messages
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105

WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP = 0x0208
WM_MOUSEWHEEL = 0x020A
WM_MOUSEHWHEEL = 0x020E
WM_XBUTTONDOWN = 0x020B
WM_XBUTTONUP = 0x020C

# Structures
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_ulonglong)
    ]

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", POINT),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_ulonglong)
    ]

# Hook Callback Prototype
HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_longlong, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

# Explicit 64-bit ABI types
kernel32.GetModuleHandleW.restype = wintypes.HMODULE
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]

user32.SetWindowsHookExW.restype = wintypes.HHOOK
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]

user32.CallNextHookEx.restype = ctypes.c_longlong
user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]

user32.UnhookWindowsHookEx.restype = wintypes.BOOL
user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]

user32.GetMessageW.restype = wintypes.BOOL
user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]

user32.PeekMessageW.restype = wintypes.BOOL
user32.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT, wintypes.UINT]

user32.PostThreadMessageW.restype = wintypes.BOOL
user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]

user32.AllowSetForegroundWindow.restype = wintypes.BOOL
user32.AllowSetForegroundWindow.argtypes = [wintypes.DWORD]
ASFW_ANY = 0xFFFFFFFF


class InputHookThread(QThread):
    # Emits (tokens_list, category, count) for on-screen visual overlay
    input_received = pyqtSignal(list, str, int)

    # Emits (category, action_name) for audio sound effects (independent of visual toggles)
    audio_event = pyqtSignal(str, str)

    def __init__(self, capture_keyboard: bool = True, only_combinations: bool = False, capture_mouse: bool = True):
        super().__init__()
        self.capture_keyboard = capture_keyboard
        self.only_combinations = only_combinations
        self.capture_mouse = capture_mouse
        self._is_running = True
        self._thread_id = None
        self._hook_kb = None
        self._hook_mouse = None
        
        # Keep references to ctypes callbacks to prevent garbage collection
        self._kb_proc = None
        self._mouse_proc = None

        # Tracking key repeats and held keys
        self._pressed_keys = set()
        self._last_combo_str = ""
        self._repeat_count = 1
        self._last_event_time = 0.0

    def _get_modifiers(self) -> dict:
        ctrl = bool(user32.GetAsyncKeyState(0x11) & 0x8000)
        shift = bool(user32.GetAsyncKeyState(0x10) & 0x8000)
        alt = bool(user32.GetAsyncKeyState(0x12) & 0x8000)
        win = bool((user32.GetAsyncKeyState(0x5B) & 0x8000) or (user32.GetAsyncKeyState(0x5C) & 0x8000))
        return {
            "ctrl": ctrl,
            "shift": shift,
            "alt": alt,
            "win": win
        }

    def _on_keyboard_event(self, nCode, wParam, lParam):
        if nCode >= 0:
            if wParam in (WM_KEYUP, WM_SYSKEYUP):
                kb_struct = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                self._pressed_keys.discard(kb_struct.vkCode)
                return user32.CallNextHookEx(self._hook_kb, nCode, wParam, lParam)

            if wParam in (WM_KEYDOWN, WM_SYSKEYDOWN):
                kb_struct = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                vk = kb_struct.vkCode
                scan = kb_struct.scanCode
                
                is_auto_repeat = (vk in self._pressed_keys)
                self._pressed_keys.add(vk)
                
                # Check modifiers
                mods = self._get_modifiers()
                
                # Unlock foreground permissions when Win or special system keys are used
                if mods.get("win") or vk in (0x5B, 0x5C, 0x09, 0x1B):
                    user32.AllowSetForegroundWindow(ASFW_ANY)
                
                key_name = KeyFormatter.get_key_name(vk, scan, is_shift=mods["shift"])
                tokens = KeyFormatter.format_event(mods, key_name)
                
                is_combo = KeyFormatter.is_combination(mods, vk, key_name, tokens)
                
                # Audio feedback: play for all keys, or only combinations if shortcut-only mode is active
                if not is_auto_repeat:
                    if not self.only_combinations or is_combo:
                        self.audio_event.emit("keyboard", key_name)

                # Visual overlay processing
                if tokens and self.capture_keyboard:
                    # Filter for shortcuts/combinations if only_combinations is active
                    if self.only_combinations and not is_combo:
                        return user32.CallNextHookEx(self._hook_kb, nCode, wParam, lParam)

                    combo_str = "+".join(tokens)
                    now = time.time()
                    
                    if not is_auto_repeat:
                        if combo_str == self._last_combo_str and (now - self._last_event_time) < 0.6:
                            self._repeat_count += 1
                        else:
                            self._last_combo_str = combo_str
                            self._repeat_count = 1
                        
                        self._last_event_time = now
                        self.input_received.emit(tokens, "keyboard", self._repeat_count)
                        
        return user32.CallNextHookEx(self._hook_kb, nCode, wParam, lParam)

    def _on_mouse_event(self, nCode, wParam, lParam):
        if nCode >= 0:
            if wParam in (WM_LBUTTONUP, WM_RBUTTONUP, WM_MBUTTONUP, WM_XBUTTONUP):
                self.audio_event.emit("mouse_up", "")
                return user32.CallNextHookEx(self._hook_mouse, nCode, wParam, lParam)

            mouse_struct = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
            mods = self._get_modifiers()
            action_name = None
            is_scroll = False

            if wParam == WM_LBUTTONDOWN:
                action_name = "Left Click"
            elif wParam == WM_RBUTTONDOWN:
                action_name = "Right Click"
            elif wParam == WM_MBUTTONDOWN:
                action_name = "Middle Click"
            elif wParam == WM_MOUSEWHEEL:
                is_scroll = True
                delta = ctypes.c_short(mouse_struct.mouseData >> 16).value
                action_name = "Scroll Up" if delta > 0 else "Scroll Down"
            elif wParam == WM_XBUTTONDOWN:
                btn = (mouse_struct.mouseData >> 16) & 0xFFFF
                action_name = "Mouse 4 (Back)" if btn == 1 else "Mouse 5 (Forward)"

            if action_name:
                # Audio feedback (independent of visual display filtering)
                if is_scroll:
                    self.audio_event.emit("mouse_scroll", action_name)
                else:
                    self.audio_event.emit("mouse_down", action_name)

                # Visual overlay processing
                if self.capture_mouse:
                    tokens = KeyFormatter.format_event(mods, action_name, is_mouse=True)
                    combo_str = "+".join(tokens)
                    now = time.time()
                    
                    if combo_str == self._last_combo_str and (now - self._last_event_time) < 0.4:
                        self._repeat_count += 1
                    else:
                        self._last_combo_str = combo_str
                        self._repeat_count = 1
                    
                    self._last_event_time = now
                    self.input_received.emit(tokens, "mouse", self._repeat_count)

        return user32.CallNextHookEx(self._hook_mouse, nCode, wParam, lParam)

    def run(self):
        self._thread_id = kernel32.GetCurrentThreadId()
        
        # Force Windows to create a message queue for this thread
        msg = wintypes.MSG()
        user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 0)

        hmod = kernel32.GetModuleHandleW(None)

        # Setup callbacks
        self._kb_proc = HOOKPROC(self._on_keyboard_event)
        self._hook_kb = user32.SetWindowsHookExW(
            WH_KEYBOARD_LL,
            self._kb_proc,
            hmod,
            0
        )
        if not self._hook_kb:
            self._hook_kb = user32.SetWindowsHookExW(
                WH_KEYBOARD_LL,
                self._kb_proc,
                None,
                0
            )
        if not self._hook_kb:
            err = kernel32.GetLastError()
            print(f"[ERROR] Failed to install keyboard hook. Error code: {err}")
        else:
            print(f"[OK] Keyboard hook installed successfully: {self._hook_kb}")

        self._mouse_proc = HOOKPROC(self._on_mouse_event)
        self._hook_mouse = user32.SetWindowsHookExW(
            WH_MOUSE_LL,
            self._mouse_proc,
            hmod,
            0
        )
        if not self._hook_mouse:
            self._hook_mouse = user32.SetWindowsHookExW(
                WH_MOUSE_LL,
                self._mouse_proc,
                None,
                0
            )
        if not self._hook_mouse:
            err = kernel32.GetLastError()
            print(f"[ERROR] Failed to install mouse hook. Error code: {err}")
        else:
            print(f"[OK] Mouse hook installed successfully: {self._hook_mouse}")

        # Standard Windows message loop
        msg = wintypes.MSG()
        while self._is_running:
            b_ret = user32.GetMessageW(ctypes.byref(msg), 0, 0, 0)
            if b_ret == 0 or b_ret == -1:
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        # Cleanup hooks
        self._cleanup_hooks()

    def _cleanup_hooks(self):
        if self._hook_kb:
            user32.UnhookWindowsHookEx(self._hook_kb)
            self._hook_kb = None
        if self._hook_mouse:
            user32.UnhookWindowsHookEx(self._hook_mouse)
            self._hook_mouse = None
        user32.AllowSetForegroundWindow(ASFW_ANY)

    def stop(self):
        self._is_running = False
        self._cleanup_hooks()
        if self._thread_id:
            user32.PostThreadMessageW(self._thread_id, 0x0012, 0, 0)  # WM_QUIT
        self.wait(1000)

