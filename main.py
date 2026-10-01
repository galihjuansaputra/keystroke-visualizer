"""
main.py - Modern Windows Keystroke Visualizer Entry Point
"""

import sys
import os
import signal
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from config import ConfigManager
from overlay import OverlayWindow
from hook import InputHookThread
from sound import SoundManager
from tray import TrayManager

# Keep global reference to mutex to prevent garbage collection
_MUTEX_HANDLE = None


def ensure_single_instance():
    """
    Prevents running multiple instances of Keystroke Visualizer.
    If an instance is already running, alerts user and exits cleanly.
    """
    global _MUTEX_HANDLE
    mutex_name = "Local\\KeystrokeVisualizer_SingleInstance_Mutex_98a72b"
    _MUTEX_HANDLE = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    last_error = ctypes.windll.kernel32.GetLastError()
    
    ERROR_ALREADY_EXISTS = 183
    if last_error == ERROR_ALREADY_EXISTS:
        # Native Windows top-most info message box
        ctypes.windll.user32.MessageBoxW(
            0,
            "Keystroke Visualizer is already running in the background!\n\n"
            "Please check your system tray (bottom-right taskbar near the clock) "
            "to access Settings, test visualizers, or exit.",
            "Keystroke Visualizer - Already Running",
            0x00000040 | 0x00010000 | 0x00040000
        )
        sys.exit(0)


def main():
    ensure_single_instance()

    # Enable high-DPI scaling
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running in system tray

    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # 1. Config Manager
    cfg = ConfigManager()

    # 2. Sound Effects Manager
    sound_mgr = SoundManager(cfg)

    # 3. Overlay Window
    overlay = OverlayWindow(cfg)

    # 4. Input Hook Thread (Keyboard + Mouse)
    hook_thread = InputHookThread(
        capture_keyboard=cfg.get("capture_keyboard", True),
        only_combinations=cfg.get("only_combinations", False),
        capture_mouse=cfg.get("capture_mouse", True)
    )
    hook_thread.input_received.connect(overlay.display_event)
    hook_thread.audio_event.connect(sound_mgr.handle_audio_event)
    hook_thread.start()

    # 5. System Tray Manager
    tray_mgr = TrayManager(app, overlay, hook_thread, cfg, sound_mgr)

    # Clean shutdown on application exit
    def on_exit():
        hook_thread.stop()

    app.aboutToQuit.connect(on_exit)

    # Show initial welcome visual for 2.5s so user immediately sees the visualizer
    print("[Keystroke Visualizer] Starting visualizer...")
    overlay.display_event(["⌨️ Keystroke Visualizer", "Ready! Press Any Key"], "keyboard", 1)
    overlay.hide_timer.start(2500)

    print("[Keystroke Visualizer] Application running. Check system tray for settings.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

