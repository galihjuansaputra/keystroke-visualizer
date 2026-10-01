"""
settings_window.py - Modern Windows 11 Fluent Unified Settings Window
All visualizer appearance, input detection, and audio sound effects configured in a single window.
Includes explicit Save & Apply, independent keyboard & mouse audio volume controls, and Fluent checkmarks.
"""

import os
import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox, QCheckBox,
    QSlider, QPushButton, QGroupBox, QScrollArea, QWidget, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from tray import create_tray_icon
from sound import SOUND_PROFILES

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    CHECKMARK_PATH = os.path.join(sys._MEIPASS, "checkmark.png").replace("\\", "/")
else:
    CHECKMARK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "checkmark.png").replace("\\", "/")


class SettingsWindow(QDialog):
    """
    Modern Fluent Settings Window providing full control over Keystroke Visualizer.
    """
    def __init__(self, config_manager, overlay_window, hook_thread, sound_manager=None, parent=None):
        super().__init__(parent)
        self.cfg = config_manager
        self.overlay = overlay_window
        self.hook_thread = hook_thread
        self.sound_mgr = sound_manager

        self.setWindowTitle("Keystroke Visualizer - Settings")
        self.setWindowIcon(create_tray_icon())
        self.setMinimumSize(680, 760)
        self.resize(720, 820)

        # Allow standard window minimizing/closing
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint
        )

        self._init_ui()
        self._load_values()
        self._apply_styles()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Scroll Area for clean scrolling on any screen resolution
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background-color: #1A1D24; border: none; }")

        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(18)

        # 1. Header Section
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        title_label = QLabel("⚙️ Visualizer & Audio Settings")
        title_label.setObjectName("pageTitle")
        
        subtitle_label = QLabel("Customize overlay display, input filters, and independent mechanical sound effects.")
        subtitle_label.setObjectName("pageSubtitle")
        subtitle_label.setWordWrap(True)

        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        content_layout.addLayout(header_layout)

        # 2. Section: Appearance & Display (Visual Overlay)
        display_group = QGroupBox("🎨 Visual Overlay Appearance")
        display_layout = QVBoxLayout(display_group)
        display_layout.setSpacing(12)

        # Theme Style
        theme_row = QHBoxLayout()
        theme_lbl = QLabel("Theme Style:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Modern Fluent", "Light Modern Fluent", "Cyberpunk Neon", "Minimal Monochrome"])
        theme_row.addWidget(theme_lbl)
        theme_row.addStretch()
        theme_row.addWidget(self.theme_combo)
        display_layout.addLayout(theme_row)

        # Visualizer Size
        size_row = QHBoxLayout()
        size_lbl = QLabel("Visualizer Size:")
        self.size_combo = QComboBox()
        self.size_combo.addItems(["Small", "Medium", "Large"])
        size_row.addWidget(size_lbl)
        size_row.addStretch()
        size_row.addWidget(self.size_combo)
        display_layout.addLayout(size_row)

        # Screen Position
        pos_row = QHBoxLayout()
        pos_lbl = QLabel("Screen Position:")
        self.pos_combo = QComboBox()
        self.pos_combo.addItems(["Bottom-Center", "Bottom-Left", "Bottom-Right", "Top-Center", "Top-Right", "Custom (Draggable)"])
        pos_row.addWidget(pos_lbl)
        pos_row.addStretch()
        pos_row.addWidget(self.pos_combo)
        display_layout.addLayout(pos_row)

        # Reposition Drag Button
        drag_btn = QPushButton("☩ Drag Visualizer to Custom Position...")
        drag_btn.setObjectName("secondaryBtn")
        drag_btn.clicked.connect(self._on_start_reposition)
        display_layout.addWidget(drag_btn)

        # Duration
        dur_row = QHBoxLayout()
        dur_lbl = QLabel("Display Duration:")
        self.dur_combo = QComboBox()
        self.dur_combo.addItem("Fast (0.8s)", 800)
        self.dur_combo.addItem("Normal (1.2s)", 1200)
        self.dur_combo.addItem("Relaxed (2.0s)", 2000)
        self.dur_combo.addItem("Long (3.0s)", 3000)
        dur_row.addWidget(dur_lbl)
        dur_row.addStretch()
        dur_row.addWidget(self.dur_combo)
        display_layout.addLayout(dur_row)

        # Multiplier checkbox
        self.repeat_chk = QCheckBox("Show repeat multiplier badge for repeated keys (e.g. ×2, ×3)")
        display_layout.addWidget(self.repeat_chk)

        content_layout.addWidget(display_group)

        # 3. Section: Input & Key Filtering (Visual Overlay)
        input_group = QGroupBox("⌨️ On-Screen Key Detection (Visual Display)")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(10)

        self.kb_chk = QCheckBox("Show Keyboard Strokes on screen")
        self.kb_chk.toggled.connect(self._on_kb_display_toggled)
        input_layout.addWidget(self.kb_chk)

        self.combo_chk = QCheckBox("Only show shortcuts && key combinations (e.g. Ctrl+C, Alt+Tab)")
        input_layout.addWidget(self.combo_chk)

        self.mouse_chk = QCheckBox("Show Mouse actions on screen (Clicks && Scroll wheel)")
        input_layout.addWidget(self.mouse_chk)

        content_layout.addWidget(input_group)

        # 4. Section: Audio Sound Effects (Independent Audio Engine)
        sound_group = QGroupBox("🔊 Audio Sound Effects (Independent from Visuals)")
        sound_layout = QVBoxLayout(sound_group)
        sound_layout.setSpacing(14)

        sound_hint = QLabel("Selectively enable or disable keyboard, mouse click, and scroll wheel audio effects.")
        sound_hint.setObjectName("groupHint")
        sound_hint.setWordWrap(True)
        sound_layout.addWidget(sound_hint)

        # 3 Individual Sound Toggles
        self.sound_kb_chk = QCheckBox("Enable Keyboard typing audio (Mechanical switch)")
        sound_layout.addWidget(self.sound_kb_chk)

        self.sound_mouse_click_chk = QCheckBox("Enable Mouse click audio (Mechanical micro-switch)")
        sound_layout.addWidget(self.sound_mouse_click_chk)

        self.sound_mouse_scroll_chk = QCheckBox("Enable Mouse scroll wheel audio (Rotary notch tick)")
        sound_layout.addWidget(self.sound_mouse_scroll_chk)

        # Sound Profile
        prof_row = QHBoxLayout()
        prof_lbl = QLabel("Sound Switch Profile:")
        self.prof_combo = QComboBox()
        self.prof_combo.addItems(SOUND_PROFILES)
        prof_row.addWidget(prof_lbl)
        prof_row.addStretch()
        prof_row.addWidget(self.prof_combo)
        sound_layout.addLayout(prof_row)

        # Keyboard Volume Slider
        kb_vol_vbox = QVBoxLayout()
        kb_vol_vbox.setSpacing(4)
        kb_vol_header = QHBoxLayout()
        kb_vol_lbl = QLabel("⌨️ Keyboard Sound Volume:")
        self.kb_vol_value_lbl = QLabel("75%")
        self.kb_vol_value_lbl.setObjectName("volVal")
        kb_vol_header.addWidget(kb_vol_lbl)
        kb_vol_header.addStretch()
        kb_vol_header.addWidget(self.kb_vol_value_lbl)
        kb_vol_vbox.addLayout(kb_vol_header)

        self.kb_vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.kb_vol_slider.setRange(0, 100)
        self.kb_vol_slider.setValue(75)
        self.kb_vol_slider.valueChanged.connect(lambda v: self.kb_vol_value_lbl.setText(f"{v}%"))
        kb_vol_vbox.addWidget(self.kb_vol_slider)
        sound_layout.addLayout(kb_vol_vbox)

        # Mouse Volume Slider
        mouse_vol_vbox = QVBoxLayout()
        mouse_vol_vbox.setSpacing(4)
        mouse_vol_header = QHBoxLayout()
        mouse_vol_lbl = QLabel("🖱️ Mouse Sound Volume (Clicks & Scroll):")
        self.mouse_vol_value_lbl = QLabel("50%")
        self.mouse_vol_value_lbl.setObjectName("volVal")
        mouse_vol_header.addWidget(mouse_vol_lbl)
        mouse_vol_header.addStretch()
        mouse_vol_header.addWidget(self.mouse_vol_value_lbl)
        mouse_vol_vbox.addLayout(mouse_vol_header)

        self.mouse_vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.mouse_vol_slider.setRange(0, 100)
        self.mouse_vol_slider.setValue(50)
        self.mouse_vol_slider.valueChanged.connect(lambda v: self.mouse_vol_value_lbl.setText(f"{v}%"))
        mouse_vol_vbox.addWidget(self.mouse_vol_slider)
        sound_layout.addLayout(mouse_vol_vbox)

        # Audio Test Buttons (Clean 2x2 Grid)
        test_grid = QGridLayout()
        test_grid.setSpacing(10)

        test_kb_snd_btn = QPushButton("⌨️ Normal Key (A-Z)")
        test_kb_snd_btn.setObjectName("secondaryBtn")
        test_kb_snd_btn.clicked.connect(self._on_test_kb_normal)

        test_kb_heavy_btn = QPushButton("⌨️ Heavy Key (Space/Enter)")
        test_kb_heavy_btn.setObjectName("secondaryBtn")
        test_kb_heavy_btn.clicked.connect(self._on_test_kb_heavy)

        test_mouse_snd_btn = QPushButton("🖱️ Mouse Click")
        test_mouse_snd_btn.setObjectName("secondaryBtn")
        test_mouse_snd_btn.clicked.connect(self._on_test_mouse_sound)

        test_scroll_snd_btn = QPushButton("📜 Scroll Wheel")
        test_scroll_snd_btn.setObjectName("secondaryBtn")
        test_scroll_snd_btn.clicked.connect(self._on_test_scroll_sound)

        test_grid.addWidget(test_kb_snd_btn, 0, 0)
        test_grid.addWidget(test_kb_heavy_btn, 0, 1)
        test_grid.addWidget(test_mouse_snd_btn, 1, 0)
        test_grid.addWidget(test_scroll_snd_btn, 1, 1)
        sound_layout.addLayout(test_grid)

        content_layout.addWidget(sound_group)

        scroll.setWidget(content_widget)
        root_layout.addWidget(scroll)

        # Bottom Bar with Test Overlay, Cancel, and Save & Apply
        bottom_bar = QFrame()
        bottom_bar.setObjectName("bottomBar")
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(24, 14, 24, 14)
        bottom_layout.setSpacing(12)

        test_overlay_btn = QPushButton("✨ Preview Visualizer")
        test_overlay_btn.setObjectName("secondaryBtn")
        test_overlay_btn.clicked.connect(self._on_test_overlay)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("secondaryBtn")
        close_btn.clicked.connect(self.close)

        self.save_apply_btn = QPushButton("💾 Save && Apply")
        self.save_apply_btn.setObjectName("primaryBtn")
        self.save_apply_btn.clicked.connect(self._on_save_and_apply)

        bottom_layout.addWidget(test_overlay_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(close_btn)
        bottom_layout.addWidget(self.save_apply_btn)

        root_layout.addWidget(bottom_bar)

    def _load_values(self):
        # Appearance
        current_theme = self.cfg.get("theme", "Dark Modern Fluent")
        idx_th = self.theme_combo.findText(current_theme)
        if idx_th >= 0:
            self.theme_combo.setCurrentIndex(idx_th)

        current_size = self.cfg.get("size", "Medium")
        idx_sz = self.size_combo.findText(current_size)
        if idx_sz >= 0:
            self.size_combo.setCurrentIndex(idx_sz)

        current_pos = self.cfg.get("preset", "Bottom-Center")
        if current_pos == "Custom":
            self.pos_combo.setCurrentText("Custom (Draggable)")
        else:
            idx_pos = self.pos_combo.findText(current_pos)
            if idx_pos >= 0:
                self.pos_combo.setCurrentIndex(idx_pos)

        dur_ms = self.cfg.get("display_duration_ms", 1200)
        idx_dur = self.dur_combo.findData(dur_ms)
        if idx_dur >= 0:
            self.dur_combo.setCurrentIndex(idx_dur)

        self.repeat_chk.setChecked(self.cfg.get("show_repeat_count", True))

        # Input
        kb_enabled = self.cfg.get("capture_keyboard", True)
        self.kb_chk.setChecked(kb_enabled)
        self.combo_chk.setChecked(self.cfg.get("only_combinations", False))
        self.combo_chk.setEnabled(kb_enabled)
        self.mouse_chk.setChecked(self.cfg.get("capture_mouse", True))

        # 3 Sound Toggles
        self.sound_kb_chk.setChecked(self.cfg.get("sound_keyboard", True))
        self.sound_mouse_click_chk.setChecked(self.cfg.get("sound_mouse_click", self.cfg.get("sound_mouse", True)))
        self.sound_mouse_scroll_chk.setChecked(self.cfg.get("sound_mouse_scroll", self.cfg.get("sound_mouse", True)))
        
        prof = self.cfg.get("sound_profile", "Mechanical Switch")
        idx_prof = self.prof_combo.findText(prof)
        if idx_prof >= 0:
            self.prof_combo.setCurrentIndex(idx_prof)

        # Independent Volumes
        kb_vol = float(self.cfg.get("sound_volume_keyboard", self.cfg.get("sound_volume", 0.75)))
        kb_vol_pct = int(round(kb_vol * 100))
        self.kb_vol_slider.setValue(kb_vol_pct)
        self.kb_vol_value_lbl.setText(f"{kb_vol_pct}%")

        mouse_vol = float(self.cfg.get("sound_volume_mouse", 0.50))
        mouse_vol_pct = int(round(mouse_vol * 100))
        self.mouse_vol_slider.setValue(mouse_vol_pct)
        self.mouse_vol_value_lbl.setText(f"{mouse_vol_pct}%")

    def _apply_styles(self):
        checkmark_url = CHECKMARK_PATH.replace("\\", "/")
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #1A1D24;
                color: #FFFFFF;
                font-family: 'Segoe UI Variable Text', 'Segoe UI', sans-serif;
                font-size: 13px;
            }}
            #contentWidget {{
                background-color: #1A1D24;
            }}
            #pageTitle {{
                font-size: 20px;
                font-weight: bold;
                color: #FFFFFF;
            }}
            #pageSubtitle {{
                font-size: 12px;
                color: rgba(255, 255, 255, 0.65);
            }}
            #groupHint {{
                font-size: 11.5px;
                color: rgba(255, 255, 255, 0.55);
                margin-bottom: 4px;
            }}
            QGroupBox {{
                background-color: #222631;
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 8px;
                margin-top: 24px;
                padding: 22px 18px 18px 18px;
                font-size: 13px;
                font-weight: 600;
                color: #58A6FF;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                left: 14px;
                top: 4px;
            }}
            QLabel {{
                color: #E2E8F0;
                font-size: 13px;
            }}
            #volVal {{
                font-weight: bold;
                color: #58A6FF;
                font-size: 13px;
            }}
            QComboBox {{
                background-color: #2D3342;
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 6px;
                padding: 6px 32px 6px 14px;
                min-width: 220px;
                max-width: 260px;
                font-size: 13px;
            }}
            QComboBox:hover {{
                border-color: #0078D4;
                background-color: #353C4D;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 28px;
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: #222631;
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.15);
                selection-background-color: #0078D4;
                padding: 4px;
            }}
            QCheckBox {{
                color: #E2E8F0;
                spacing: 10px;
                font-size: 13px;
            }}
            QCheckBox:hover {{
                color: #FFFFFF;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1.5px solid rgba(255, 255, 255, 0.35);
                background-color: #2D3342;
            }}
            QCheckBox::indicator:hover {{
                border-color: #0078D4;
                background-color: #363D4E;
            }}
            QCheckBox::indicator:checked {{
                background-color: #0078D4;
                border-color: #0078D4;
                image: url({checkmark_url});
            }}
            QCheckBox::indicator:checked:hover {{
                background-color: #1084D8;
                border-color: #1084D8;
                image: url({checkmark_url});
            }}
            QSlider::groove:horizontal {{
                height: 6px;
                background: #2D3342;
                border-radius: 3px;
            }}
            QSlider::sub-page:horizontal {{
                background: #0078D4;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: #FFFFFF;
                border: 2px solid #0078D4;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
            #primaryBtn {{
                background-color: #0078D4;
                color: #FFFFFF;
                font-weight: 600;
                border-radius: 6px;
                padding: 8px 24px;
                border: none;
                font-size: 13px;
            }}
            #primaryBtn:hover {{
                background-color: #1084D8;
            }}
            #primaryBtn:pressed {{
                background-color: #006CBE;
            }}
            #secondaryBtn {{
                background-color: #2D3342;
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 12.5px;
            }}
            #secondaryBtn:hover {{
                background-color: #384052;
                border-color: rgba(255, 255, 255, 0.30);
            }}
            #bottomBar {{
                background-color: #14171E;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
            }}
            QScrollBar:vertical {{
                background: #1A1D24;
                width: 8px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: #2D3342;
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #3D4559;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

    def _on_kb_display_toggled(self, checked):
        self.combo_chk.setEnabled(checked)

    def _on_start_reposition(self):
        self.overlay.set_reposition_mode(True)

    def _on_test_kb_normal(self):
        if self.sound_mgr:
            vol = self.kb_vol_slider.value() / 100.0
            self.sound_mgr.set_keyboard_volume(vol)
            self.sound_mgr.play_keyboard_sound(key_name="A")
        self.overlay.display_event(["⌨️ Normal Key", "A"], "keyboard", 1)

    def _on_test_kb_heavy(self):
        if self.sound_mgr:
            vol = self.kb_vol_slider.value() / 100.0
            self.sound_mgr.set_keyboard_volume(vol)
            self.sound_mgr.play_keyboard_sound(key_name="Space")
        self.overlay.display_event(["⌨️ Heavy Key", "Space"], "keyboard", 1)

    def _on_test_mouse_sound(self):
        if self.sound_mgr:
            vol = self.mouse_vol_slider.value() / 100.0
            self.sound_mgr.set_mouse_volume(vol)
            self.sound_mgr.play_mouse_sound()
        self.overlay.display_event(["🖱️ Sound Test", "Mouse Click"], "mouse", 1)

    def _on_test_scroll_sound(self):
        if self.sound_mgr:
            vol = self.mouse_vol_slider.value() / 100.0
            self.sound_mgr.set_mouse_volume(vol)
            self.sound_mgr.play_mouse_scroll_sound()
        self.overlay.display_event(["📜 Sound Test", "Scroll Wheel"], "mouse", 1)

    def _on_test_overlay(self):
        if self.sound_mgr and self.sound_kb_chk.isChecked():
            vol = self.kb_vol_slider.value() / 100.0
            self.sound_mgr.set_keyboard_volume(vol)
            self.sound_mgr.play_keyboard_sound(key_name="P")
        self.overlay.display_event(["Ctrl", "Shift", "P"], "keyboard", 1)

    def _on_save_and_apply(self):
        """
        Applies all settings to config, updates live components, persists to config.json, and closes dialog.
        """
        # 1. Appearance
        theme_text = self.theme_combo.currentText()
        self.cfg.data["theme"] = theme_text

        size_text = self.size_combo.currentText()
        self.cfg.data["size"] = size_text

        pos_text = self.pos_combo.currentText()
        if pos_text != "Custom (Draggable)":
            self.cfg.data["preset"] = pos_text
            self.cfg.data["custom_x"] = None
            self.cfg.data["custom_y"] = None

        dur_ms = self.dur_combo.currentData()
        if dur_ms:
            self.cfg.data["display_duration_ms"] = dur_ms

        self.cfg.data["show_repeat_count"] = self.repeat_chk.isChecked()

        # 2. Input detection (Visual overlay)
        kb_capture = self.kb_chk.isChecked()
        combo_only = self.combo_chk.isChecked()
        mouse_capture = self.mouse_chk.isChecked()

        self.cfg.data["capture_keyboard"] = kb_capture
        self.cfg.data["only_combinations"] = combo_only
        self.cfg.data["capture_mouse"] = mouse_capture

        self.hook_thread.capture_keyboard = kb_capture
        self.hook_thread.only_combinations = combo_only
        self.hook_thread.capture_mouse = mouse_capture

        # 3. Audio settings (3 individual toggles)
        sound_kb = self.sound_kb_chk.isChecked()
        sound_click = self.sound_mouse_click_chk.isChecked()
        sound_scroll = self.sound_mouse_scroll_chk.isChecked()
        sound_prof = self.prof_combo.currentText()
        kb_vol_float = self.kb_vol_slider.value() / 100.0
        mouse_vol_float = self.mouse_vol_slider.value() / 100.0

        self.cfg.data["sound_keyboard"] = sound_kb
        self.cfg.data["sound_mouse_click"] = sound_click
        self.cfg.data["sound_mouse_scroll"] = sound_scroll
        self.cfg.data["sound_mouse"] = (sound_click or sound_scroll)
        self.cfg.data["sound_profile"] = sound_prof
        self.cfg.data["sound_volume_keyboard"] = kb_vol_float
        self.cfg.data["sound_volume_mouse"] = mouse_vol_float
        self.cfg.data["sound_volume"] = kb_vol_float

        if self.sound_mgr:
            self.sound_mgr.set_keyboard_volume(kb_vol_float)
            self.sound_mgr.set_mouse_volume(mouse_vol_float)

        # 4. Save to disk
        self.cfg.save()

        # 5. Apply live updates to overlay
        self.overlay._apply_theme()
        if pos_text != "Custom (Draggable)":
            self.overlay.update_position()

        # Visual feedback on save
        self.overlay.display_event(["⚙️ Settings", "Saved & Applied!"], "keyboard", 1)

        # Update button text briefly for instant confirmation without closing
        self.save_apply_btn.setText("✅ Saved & Applied!")
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: self.save_apply_btn.setText("💾 Save && Apply"))
