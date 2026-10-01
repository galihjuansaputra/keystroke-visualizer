"""
tray.py - System Tray Icon and Context Settings Menu
"""

from PyQt6.QtWidgets import (
    QSystemTrayIcon, QMenu, QMessageBox
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPen, QBrush
from PyQt6.QtCore import Qt


def create_tray_icon() -> QIcon:
    """Generates a clean modern keyboard icon pixmap for the Windows system tray"""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Rounded base keyboard body
    painter.setBrush(QBrush(QColor(0, 120, 212)))
    painter.setPen(QPen(QColor(255, 255, 255, 200), 2))
    painter.drawRoundedRect(6, 12, 52, 40, 10, 10)

    # Key chiclets
    painter.setBrush(QBrush(QColor(255, 255, 255)))
    painter.setPen(Qt.PenStyle.NoPen)
    
    # Row 1 keys
    painter.drawRoundedRect(12, 18, 8, 8, 2, 2)
    painter.drawRoundedRect(24, 18, 8, 8, 2, 2)
    painter.drawRoundedRect(36, 18, 8, 8, 2, 2)
    painter.drawRoundedRect(48, 18, 4, 8, 2, 2)

    # Row 2 keys
    painter.drawRoundedRect(12, 30, 10, 8, 2, 2)
    painter.drawRoundedRect(26, 30, 8, 8, 2, 2)
    painter.drawRoundedRect(38, 30, 14, 8, 2, 2)

    # Spacebar
    painter.drawRoundedRect(18, 42, 28, 5, 2, 2)

    painter.end()
    return QIcon(pixmap)


class TrayManager:
    def __init__(self, app, overlay, hook_thread, config_manager, sound_manager=None):
        self.app = app
        self.overlay = overlay
        self.hook_thread = hook_thread
        self.cfg = config_manager
        self.sound_mgr = sound_manager
        self.settings_window = None

        self.tray = QSystemTrayIcon(create_tray_icon(), self.app)
        self.tray.setToolTip("Keystroke Visualizer - Click for Settings")

        self.tray.activated.connect(self._on_tray_activated)
        self._build_menu()
        self.tray.show()

    def _on_tray_activated(self, reason):
        # Open Settings on left-click or double-click
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick
        ):
            self.open_settings()

    def open_settings(self):
        if self.settings_window is None:
            from settings_window import SettingsWindow
            self.settings_window = SettingsWindow(
                self.cfg, self.overlay, self.hook_thread, self.sound_mgr
            )
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def _build_menu(self):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #20242F;
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                padding: 6px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QMenu::item {
                padding: 7px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #0078D4;
                color: #FFFFFF;
            }
            QMenu::separator {
                height: 1px;
                background-color: rgba(255, 255, 255, 0.15);
                margin: 4px 10px;
            }
        """)

        # Title
        title_action = menu.addAction("⌨️ Keystroke Visualizer")
        title_action.setEnabled(False)
        menu.addSeparator()

        # Open Unified Settings Window
        settings_action = menu.addAction("⚙️ Settings...")
        settings_action.triggered.connect(self.open_settings)

        # Test Keystroke Action
        test_action = menu.addAction("✨ Preview Test Keystroke")
        test_action.triggered.connect(self._preview_test)

        # Explicit Drag to Reposition Action
        drag_action = menu.addAction("☩ Adjust Manual Position (Drag to Move)...")
        drag_action.triggered.connect(self._start_reposition)

        menu.addSeparator()

        # Help / Drag Tip
        help_action = menu.addAction("💡 How to reposition...")
        help_action.triggered.connect(self._show_help)

        # Exit
        exit_action = menu.addAction("❌ Exit")
        exit_action.triggered.connect(self._exit_app)

        self.tray.setContextMenu(menu)

    def _preview_test(self):
        if self.sound_mgr and self.cfg.get("sound_keyboard", True):
            self.sound_mgr.play_keyboard_sound()
        self.overlay.display_event(["Ctrl", "Shift", "P"], "keyboard", 1)

    def _start_reposition(self):
        self.overlay.set_reposition_mode(True)

    def _show_help(self):
        QMessageBox.information(
            None,
            "Keystroke Visualizer - How to Reposition",
            "The visualizer is completely unclickable and undraggable by default so it will never interfere with your clicks in other applications.\n\n"
            "To adjust manual position:\n"
            "1. Click '☩ Adjust Manual Position (Drag to Move)...' or open '⚙️ Settings'.\n"
            "2. A draggable card will appear on your screen.\n"
            "3. Click and drag it to your desired spot, then release the mouse.\n"
            "4. Your new position is saved automatically, and the visualizer immediately returns to unclickable click-through mode!"
        )

    def _exit_app(self):
        self.hook_thread.stop()
        self.app.quit()
