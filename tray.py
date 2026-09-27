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
    def __init__(self, app, overlay, hook_thread, config_manager):
        self.app = app
        self.overlay = overlay
        self.hook_thread = hook_thread
        self.cfg = config_manager

        self.tray = QSystemTrayIcon(create_tray_icon(), self.app)
        self.tray.setToolTip("Keystroke Visualizer - Modern Windows OSD")

        self._build_menu()
        self.tray.show()

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
                padding: 6px 24px;
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

        # Test Keystroke Action
        test_action = menu.addAction("✨ Preview Test Keystroke")
        test_action.triggered.connect(self._preview_test)

        menu.addSeparator()

        # Position Submenu
        pos_menu = menu.addMenu("📍 Position Presets")
        presets = ["Bottom-Center", "Bottom-Right", "Bottom-Left", "Top-Center", "Top-Right"]
        current_preset = self.cfg.get("preset", "Bottom-Center")

        for p in presets:
            action = pos_menu.addAction(p)
            action.setCheckable(True)
            action.setChecked(p == current_preset)
            action.triggered.connect(lambda checked, preset=p: self._set_preset(preset))

        # Explicit Drag to Reposition Action (the only way to drag the visualizer)
        drag_action = menu.addAction("☩ Adjust Manual Position (Drag to Move)...")
        drag_action.triggered.connect(self._start_reposition)


        # Theme Submenu
        theme_menu = menu.addMenu("🎨 Themes")
        themes = ["Dark Modern Fluent", "Light Modern Fluent", "Cyberpunk Neon", "Minimal Monochrome"]
        current_theme = self.cfg.get("theme", "Dark Modern Fluent")

        for th in themes:
            action = theme_menu.addAction(th)
            action.setCheckable(True)
            action.setChecked(th == current_theme)
            action.triggered.connect(lambda checked, theme=th: self._set_theme(theme))

        # Size Submenu
        size_menu = menu.addMenu("📏 Size")
        sizes = ["Small", "Medium", "Large"]
        current_size = self.cfg.get("size", "Medium")

        for sz in sizes:
            action = size_menu.addAction(sz)
            action.setCheckable(True)
            action.setChecked(sz == current_size)
            action.triggered.connect(lambda checked, s=sz: self._set_size(s))


        # Duration Submenu
        dur_menu = menu.addMenu("⏱️ Display Duration")
        durations = [
            ("Fast (0.8s)", 800),
            ("Normal (1.2s)", 1200),
            ("Relaxed (2.0s)", 2000),
            ("Long (3.0s)", 3000)
        ]
        current_dur = self.cfg.get("display_duration_ms", 1200)

        for label, ms in durations:
            action = dur_menu.addAction(label)
            action.setCheckable(True)
            action.setChecked(ms == current_dur)
            action.triggered.connect(lambda checked, d=ms: self._set_duration(d))

        menu.addSeparator()

        # Mouse Events Toggle
        mouse_action = menu.addAction("🖱️ Visualize Mouse (Clicks & Scroll)")
        mouse_action.setCheckable(True)
        mouse_action.setChecked(self.cfg.get("capture_mouse", True))
        mouse_action.triggered.connect(self._toggle_mouse_capture)

        # Repeat Count Toggle
        repeat_action = menu.addAction("🔢 Show Multiplier (e.g. ×2)")
        repeat_action.setCheckable(True)
        repeat_action.setChecked(self.cfg.get("show_repeat_count", True))
        repeat_action.triggered.connect(self._toggle_repeat_count)

        menu.addSeparator()

        # Help / Drag Tip
        help_action = menu.addAction("💡 How to reposition...")
        help_action.triggered.connect(self._show_help)

        # Exit
        exit_action = menu.addAction("❌ Exit")
        exit_action.triggered.connect(self._exit_app)

        self.tray.setContextMenu(menu)

    def _preview_test(self):
        self.overlay.display_event(["Ctrl", "Shift", "A"], "keyboard", 1)

    def _start_reposition(self):
        self.overlay.set_reposition_mode(True)

    def _set_preset(self, preset):
        if getattr(self.overlay, "_reposition_mode", False):
            self.overlay.set_reposition_mode(False)
        self.cfg.set("preset", preset)
        self.cfg.set("custom_x", None)
        self.cfg.set("custom_y", None)
        self.overlay.update_position()
        self._build_menu()
        self.overlay.display_event(["Position", preset], "keyboard", 1)

    def _set_theme(self, theme):
        self.cfg.set("theme", theme)
        self.overlay._apply_theme()
        self._build_menu()
        self.overlay.display_event(["Theme", theme.split()[0]], "keyboard", 1)

    def _set_size(self, size_name):
        self.cfg.set("size", size_name)
        self._build_menu()
        self.overlay.display_event(["Size", size_name], "keyboard", 1)

    def _set_duration(self, ms):
        self.cfg.set("display_duration_ms", ms)
        self._build_menu()

    def _toggle_mouse_capture(self, checked):
        self.cfg.set("capture_mouse", checked)
        self.hook_thread.capture_mouse = checked
        self._build_menu()

    def _toggle_repeat_count(self, checked):
        self.cfg.set("show_repeat_count", checked)
        self._build_menu()

    def _show_help(self):
        QMessageBox.information(
            None,
            "Keystroke Visualizer - How to Reposition",
            "The visualizer is completely unclickable and undraggable by default so it will never interfere with your clicks in other applications.\n\n"
            "To adjust manual position:\n"
            "1. Click '☩ Adjust Manual Position (Drag to Move)...' in this tray menu.\n"
            "2. A draggable card will appear on your screen.\n"
            "3. Click and drag it to your desired spot, then release the mouse.\n"
            "4. Your new position is saved automatically, and the visualizer immediately returns to unclickable click-through mode!"
        )

    def _exit_app(self):
        self.hook_thread.stop()
        self.app.quit()
