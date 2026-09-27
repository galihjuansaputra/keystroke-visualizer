"""
overlay.py - Ultra-fast, Pure QPainter Modern Windows 11 Fluent Keystroke Visualizer
"""

import sys
import ctypes
from ctypes import wintypes
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QPoint, QRectF
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import (
    QColor, QFont, QFontMetrics, QCursor, QPainter, QPainterPath, QPen, QBrush
)

user32 = ctypes.windll.user32

# Win32 Constants for Window Management
GWL_EXSTYLE = -20
WS_EX_TOPMOST = 0x00000008
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_LAYERED = 0x00080000
WS_EX_NOACTIVATE = 0x08000000

HWND_TOPMOST = -1
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040

SIZES = {
    "Small": {
        "font_pt": 9.5,
        "plus_pt": 8.5,
        "key_h": 26,
        "pad": 8,
        "spacing": 7,
        "corner_radius": 10.0,
        "key_radius": 6.0,
        "chiclet_pad_h": 16,
    },
    "Medium": {
        "font_pt": 11.0,
        "plus_pt": 10.0,
        "key_h": 32,
        "pad": 10,
        "spacing": 8,
        "corner_radius": 13.0,
        "key_radius": 8.0,
        "chiclet_pad_h": 20,
    },
    "Large": {
        "font_pt": 13.5,
        "plus_pt": 12.0,
        "key_h": 40,
        "pad": 12,
        "spacing": 10,
        "corner_radius": 15.0,
        "key_radius": 9.0,
        "chiclet_pad_h": 26,
    }
}

THEMES = {
    "Dark Modern Fluent": {
        "container_bg": QColor(20, 24, 34, 235),
        "container_border": QColor(255, 255, 255, 180),
        "border_width": 2.2,
        "key_bg": QColor(42, 48, 64, 245),
        "key_border": QColor(255, 255, 255, 120),
        "key_text": QColor(255, 255, 255),
        "plus_color": QColor(255, 255, 255, 140),
        "repeat_bg": QColor(0, 120, 212, 235),
        "repeat_border": QColor(96, 205, 255, 240),
        "repeat_text": QColor(255, 255, 255),
        "mouse_bg": QColor(16, 124, 65, 235),
        "mouse_text": QColor(255, 255, 255),
    },
    "Light Modern Fluent": {
        "container_bg": QColor(246, 248, 250, 240),
        "container_border": QColor(0, 120, 212, 220),
        "border_width": 2.0,
        "key_bg": QColor(255, 255, 255, 250),
        "key_border": QColor(0, 0, 0, 60),
        "key_text": QColor(25, 25, 25),
        "plus_color": QColor(0, 0, 0, 140),
        "repeat_bg": QColor(0, 103, 192, 235),
        "repeat_border": QColor(0, 80, 160, 240),
        "repeat_text": QColor(255, 255, 255),
        "mouse_bg": QColor(16, 124, 65, 225),
        "mouse_text": QColor(255, 255, 255),
    },
    "Cyberpunk Neon": {
        "container_bg": QColor(10, 12, 22, 240),
        "container_border": QColor(0, 240, 255, 255),
        "border_width": 2.2,
        "key_bg": QColor(20, 26, 48, 245),
        "key_border": QColor(255, 0, 85, 240),
        "key_text": QColor(0, 240, 255),
        "plus_color": QColor(255, 0, 85, 220),
        "repeat_bg": QColor(255, 0, 85, 240),
        "repeat_border": QColor(0, 240, 255, 255),
        "repeat_text": QColor(255, 255, 255),
        "mouse_bg": QColor(0, 240, 255, 235),
        "mouse_text": QColor(10, 12, 22),
    },
    "Minimal Monochrome": {
        "container_bg": QColor(10, 10, 10, 240),
        "container_border": QColor(255, 255, 255, 220),
        "border_width": 2.0,
        "key_bg": QColor(32, 32, 32, 245),
        "key_border": QColor(255, 255, 255, 140),
        "key_text": QColor(255, 255, 255),
        "plus_color": QColor(255, 255, 255, 150),
        "repeat_bg": QColor(255, 255, 255, 240),
        "repeat_border": QColor(255, 255, 255, 255),
        "repeat_text": QColor(0, 0, 0),
        "mouse_bg": QColor(65, 65, 65, 235),
        "mouse_text": QColor(255, 255, 255),
    }
}


class OverlayWindow(QWidget):
    """
    High-performance, pure QPainter keystroke visualizer.
    Features:
    - 4-way balanced margins: top == bottom == left == right.
    - Size presets: Small, Medium, Large.
    - Duplicate key multiplier (×3) formatted consistently as a chiclet button.
    - Bold 2.2px Fluent borders with rounded joins.
    - Pure canvas rendering: impossible for buttons to overlap.
    """
    def __init__(self, config_manager):
        super().__init__()
        self.cfg = config_manager
        self._opacity = 1.0
        self._dragging = False
        self._drag_start_pos = QPoint()
        self._reposition_mode = False

        # Current event payload
        self._items = []
        self._content_width = 120
        self._content_height = 52
        self._cur_size_cfg = SIZES["Medium"]

        # Window Flags: Frameless, Always on Top, Tool Window (no taskbar button)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        # Fade Timer and Animation
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self._start_fade_out)

        self.fade_anim = QPropertyAnimation(self, b"window_opacity")
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_anim.finished.connect(self._on_fade_finished)

        # Win32 OS-level styles
        self._init_win32_styles()

        # Start hidden
        self.hide()

    def _init_win32_styles(self):
        hwnd = int(self.winId())
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style |= WS_EX_TOPMOST | WS_EX_TOOLWINDOW | WS_EX_LAYERED | WS_EX_NOACTIVATE | WS_EX_TRANSPARENT
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

    # Opacity property for smooth Qt property animation
    def get_window_opacity(self) -> float:
        return self._opacity

    def set_window_opacity(self, val: float):
        self._opacity = val
        self.setWindowOpacity(val)

    window_opacity = pyqtProperty(float, get_window_opacity, set_window_opacity)

    def _apply_theme(self):
        self.update()

    def _apply_click_through(self):
        hwnd = int(self.winId())
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        if not self._reposition_mode:
            style |= WS_EX_TRANSPARENT
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            style &= ~WS_EX_TRANSPARENT
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

    def display_event(self, tokens: list, category: str, count: int = 1):
        """
        Receives key/mouse event and computes exact geometry with zero overlap.
        """
        self.fade_anim.stop()
        self.set_window_opacity(1.0)

        # Get size preset config
        size_name = self.cfg.get("size", "Medium")
        s_cfg = SIZES.get(size_name, SIZES["Medium"])
        self._cur_size_cfg = s_cfg

        key_font = QFont("Segoe UI Variable Display", int(s_cfg["font_pt"]))
        key_font.setWeight(QFont.Weight.DemiBold)
        plus_font = QFont("Segoe UI Variable Display", int(s_cfg["plus_pt"]))
        plus_font.setBold(True)

        fm_key = QFontMetrics(key_font)
        fm_plus = QFontMetrics(plus_font)

        outer_pad = s_cfg["pad"]
        key_h = s_cfg["key_h"]
        spacing = s_cfg["spacing"]

        items = []
        cur_w = float(outer_pad)

        total_tokens = len(tokens)
        for i, token in enumerate(tokens):
            is_mouse_item = (category == "mouse" and i == total_tokens - 1)
            
            # Clean key text
            display_text = token
            if display_text in ("Win", "LWin", "RWin"):
                display_text = "Win"
            elif display_text in ("Shift", "LShift", "RShift"):
                display_text = "Shift"
            elif is_mouse_item:
                if "Left" in token:
                    display_text = "🖱️ Left"
                elif "Right" in token:
                    display_text = "🖱️ Right"
                elif "Middle" in token:
                    display_text = "🖱️ Middle"
                elif "Up" in token:
                    display_text = "⬆ Scroll Up"
                elif "Down" in token:
                    display_text = "⬇ Scroll Down"
                elif "Back" in token:
                    display_text = "🖱️ Back"
                elif "Forward" in token:
                    display_text = "🖱️ Forward"

            # Measure width
            text_advance = fm_key.horizontalAdvance(display_text)
            pad_h = s_cfg["chiclet_pad_h"]
            chiclet_w = max(key_h, text_advance + pad_h)

            items.append({
                "type": "key",
                "text": display_text,
                "is_mouse": is_mouse_item,
                "w": chiclet_w,
                "h": key_h
            })

            # Plus separator between combo keys
            if i < total_tokens - 1:
                plus_w = fm_plus.horizontalAdvance("+")
                items.append({
                    "type": "plus",
                    "text": "+",
                    "w": plus_w,
                    "h": key_h
                })

        # Repeat count badge: Formatted consistently as a chiclet button with same height!
        if count > 1 and self.cfg.get("show_repeat_count", True):
            repeat_text = f"×{count}"
            rep_w = max(key_h, fm_key.horizontalAdvance(repeat_text) + (s_cfg["chiclet_pad_h"] - 2))
            items.append({
                "type": "repeat",
                "text": repeat_text,
                "w": rep_w,
                "h": key_h
            })

        # Calculate exact item positions (x, y) with spacing
        total_h = key_h + 2 * outer_pad
        center_y = float(total_h) / 2.0

        cur_x = float(outer_pad)
        for i, item in enumerate(items):
            item["x"] = cur_x
            item["y"] = center_y - (item["h"] / 2.0)
            cur_x += item["w"]
            if i < len(items) - 1:
                cur_x += float(spacing)

        total_w = cur_x + float(outer_pad)

        # 1:1 Box for single key press
        if len(tokens) == 1 and count <= 1:
            total_w = max(total_w, float(total_h))
            # Center the keycap exactly inside the 1:1 box
            items[0]["x"] = (total_w - items[0]["w"]) / 2.0

        self._content_width = int(total_w)
        self._content_height = int(total_h)
        self._items = items

        # Exact pixel position and OS topmost display
        self._position_and_show()

        # Reset hide timer
        if not self._reposition_mode:
            duration_ms = self.cfg.get("display_duration_ms", 1200)
            self.hide_timer.start(duration_ms)

    def _position_and_show(self):
        screen = QApplication.primaryScreen()
        if not screen:
            return
        geo = screen.availableGeometry()

        w = self._content_width
        h = self._content_height

        preset = self.cfg.get("preset", "Bottom-Center")
        custom_x = self.cfg.get("custom_x")
        custom_y = self.cfg.get("custom_y")

        # Compute whole box alignment based on preset
        if preset == "Custom" and custom_x is not None and custom_y is not None:
            target_x = max(geo.left(), min(custom_x, geo.right() - w))
            target_y = max(geo.top(), min(custom_y, geo.bottom() - h))
        elif preset == "Bottom-Left":
            target_x = geo.left() + 40
            target_y = geo.bottom() - h - 50
        elif preset == "Top-Left":
            target_x = geo.left() + 40
            target_y = geo.top() + 50
        elif preset == "Bottom-Right":
            target_x = geo.right() - w - 40
            target_y = geo.bottom() - h - 50
        elif preset == "Top-Right":
            target_x = geo.right() - w - 40
            target_y = geo.top() + 50
        elif preset == "Top-Center":
            target_x = geo.left() + (geo.width() - w) // 2
            target_y = geo.top() + 50
        else:  # Bottom-Center (Default) - Mathematically exact center
            target_x = geo.left() + (geo.width() - w) // 2
            target_y = geo.bottom() - h - 60

        hwnd = int(self.winId())
        # Enforce exact size, position, and OS topmost z-order in a single atomic call
        user32.SetWindowPos(
            hwnd, HWND_TOPMOST,
            int(target_x), int(target_y), int(w), int(h),
            SWP_NOACTIVATE | SWP_SHOWWINDOW
        )
        user32.BringWindowToTop(hwnd)

        # Enforce unclickable click-through at all times unless explicitly in reposition mode
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        if self._reposition_mode:
            style &= ~WS_EX_TRANSPARENT
        else:
            style |= WS_EX_TRANSPARENT
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

        self.setGeometry(int(target_x), int(target_y), int(w), int(h))
        self.update()
        self.show()

    def update_position(self):
        self._position_and_show()

    def paintEvent(self, event):
        """Paints perfectly balanced container, chiclet keycaps, plus signs, and repeat buttons"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        theme_name = self.cfg.get("theme", "Dark Modern Fluent")
        theme = THEMES.get(theme_name, THEMES["Dark Modern Fluent"])
        s_cfg = getattr(self, "_cur_size_cfg", SIZES["Medium"])

        key_font = QFont("Segoe UI Variable Display", int(s_cfg["font_pt"]))
        key_font.setWeight(QFont.Weight.DemiBold)
        plus_font = QFont("Segoe UI Variable Display", int(s_cfg["plus_pt"]))
        plus_font.setBold(True)

        # 1. Container Rounded Rect & Border with bold, crisp stroke
        bw = theme.get("border_width", 2.2)
        half_bw = bw / 2.0
        rect = QRectF(half_bw, half_bw, float(self.width()) - bw, float(self.height()) - bw)
        path = QPainterPath()
        path.addRoundedRect(rect, s_cfg["corner_radius"], s_cfg["corner_radius"])

        painter.fillPath(path, QBrush(theme["container_bg"]))
        container_pen = QPen(theme["container_border"], bw)
        container_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.strokePath(path, container_pen)

        # 2. Draw Items using exact precomputed (x, y) coordinates
        key_radius = s_cfg["key_radius"]

        for item in self._items:
            itype = item["type"]
            ix = float(item["x"])
            iy = float(item["y"])
            iw = float(item["w"])
            ih = float(item["h"])

            if itype == "key":
                # Key chiclet
                krect = QRectF(ix, iy, iw, ih)
                kpath = QPainterPath()
                kpath.addRoundedRect(krect, key_radius, key_radius)

                bg_color = theme["mouse_bg"] if item.get("is_mouse") else theme["key_bg"]
                border_color = theme["mouse_bg"] if item.get("is_mouse") else theme["key_border"]
                text_color = theme["mouse_text"] if item.get("is_mouse") else theme["key_text"]

                painter.fillPath(kpath, QBrush(bg_color))
                key_pen = QPen(border_color, 1.4)
                key_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.strokePath(kpath, key_pen)

                # Text
                painter.setFont(key_font)
                painter.setPen(text_color)
                painter.drawText(krect, Qt.AlignmentFlag.AlignCenter, item["text"])

            elif itype == "plus":
                # Plus separator
                prect = QRectF(ix, iy, iw, ih)
                painter.setFont(plus_font)
                painter.setPen(theme["plus_color"])
                painter.drawText(prect, Qt.AlignmentFlag.AlignCenter, "+")

            elif itype == "repeat":
                # Multiplier button: Styled consistently as a chiclet button with distinct accent!
                rrect = QRectF(ix, iy, iw, ih)
                rpath = QPainterPath()
                rpath.addRoundedRect(rrect, key_radius, key_radius)

                painter.fillPath(rpath, QBrush(theme["repeat_bg"]))
                rep_pen = QPen(theme["repeat_border"], 1.4)
                rep_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.strokePath(rpath, rep_pen)

                painter.setFont(key_font)
                painter.setPen(theme["repeat_text"])
                painter.drawText(rrect, Qt.AlignmentFlag.AlignCenter, item["text"])


    def set_reposition_mode(self, enabled: bool):
        """Toggles reposition mode with a persistent draggable card"""
        self._reposition_mode = enabled
        self.hide_timer.stop()
        self.fade_anim.stop()
        self.set_window_opacity(1.0)

        hwnd = int(self.winId())
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)

        if enabled:
            # Temporarily allow mouse interaction to drag to position
            style &= ~WS_EX_TRANSPARENT
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            self.setCursor(Qt.CursorShape.SizeAllCursor)
            self.display_event(["☩ Drag to Reposition"], "keyboard", 1)
        else:
            # Immediately restore completely unclickable click-through
            self._apply_click_through()
            self._start_fade_out()

    def _start_fade_out(self):
        if self._reposition_mode:
            return
        fade_duration = self.cfg.get("fade_duration_ms", 250)
        self.fade_anim.setDuration(fade_duration)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.start()

    def _on_fade_finished(self):
        if self._opacity <= 0.05 and not self._reposition_mode:
            self.hide()

    # Mouse drag repositioning ONLY when explicitly opened via settings (reposition mode)
    def mousePressEvent(self, event):
        if self._reposition_mode and event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if self._reposition_mode and self._dragging:
            new_pos = event.globalPosition().toPoint() - self._drag_start_pos
            self.move(new_pos)
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        if self._reposition_mode and self._dragging:
            self._dragging = False
            # Save new custom coordinates
            self.cfg.set("preset", "Custom")
            self.cfg.set("custom_x", self.x())
            self.cfg.set("custom_y", self.y())

            # Return immediately to unclickable and undraggable state
            self.set_reposition_mode(False)
            self.display_event(["✓ Position Saved"], "keyboard", 1)
            event.accept()
        else:
            event.ignore()
