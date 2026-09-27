"""
main.py - Modern Windows Keystroke Visualizer Entry Point
"""

import sys
import os
import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from config import ConfigManager
from overlay import OverlayWindow
from hook import InputHookThread
from tray import TrayManager


def main():
    # Enable high-DPI scaling
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running in system tray

    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # 1. Config Manager
    cfg = ConfigManager()

    # 2. Overlay Window
    overlay = OverlayWindow(cfg)

    # 3. Input Hook Thread (Keyboard + Mouse)
    hook_thread = InputHookThread(
        capture_keyboard=cfg.get("capture_keyboard", True),
        only_combinations=cfg.get("only_combinations", False),
        capture_mouse=cfg.get("capture_mouse", True)
    )
    hook_thread.input_received.connect(overlay.display_event)
    hook_thread.start()

    # 4. System Tray Manager
    tray_mgr = TrayManager(app, overlay, hook_thread, cfg)

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

