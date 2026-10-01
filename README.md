# ⌨️ Keystroke Visualizer

A fast, lightweight, and modern Windows 11 Fluent on-screen visualizer for keystrokes, key combinations, and mouse events.

[![Download Latest Release](https://img.shields.io/github/v/release/galihjuansaputra/keystroke-visualizer?label=Download%20.exe&color=0078d4&style=for-the-badge)](https://github.com/galihjuansaputra/keystroke-visualizer/releases/latest)

---

## ⚡ Quick Start

1. Download **[`KeystrokeVisualizer.exe`](https://github.com/galihjuansaputra/keystroke-visualizer/releases/latest)**.
2. Run the executable — no installation required!
3. Look for the ⌨️ keyboard icon in your **Windows System Tray** to configure settings.

---

## ✨ Features

- **⚡ Zero Latency**: Low-level Windows hooks (`WH_KEYBOARD_LL`, `WH_MOUSE_LL`) running on a dedicated thread.
- **🎨 Windows 11 Fluent Acrylic**: Frosted glass effect with balanced padding, clean borders, and smooth rounded corners.
- **🔊 Authentic Mechanical Sound Effects**: High-fidelity zero-latency audio feedback for typing (with heavier acoustic response for Space/Enter/modifiers), mechanical mouse clicks (down & up micro-switch clicks), and rotary scroll wheel notch ticks.
- **🎚️ Independent Audio Controls**: 3 discrete toggles (Keyboard, Mouse Clicks, Mouse Scroll) and independent volume sliders for keyboard and mouse audio.
- **⚡ Combination-Only Mode**: Option to display only shortcuts and key combinations (ignoring everyday typing).
- **⌨️ / 🖱️ Independent Toggles**: Freely enable/disable keyboard capture, combination filtering, mouse tracking, and sound effects.
- **🔒 Non-Intrusive & Click-Through**: Always on top of games and fullscreen apps without stealing focus or blocking clicks.
- **📍 Free Repositioning**: Choose from 5 screen presets or drag the visualizer anywhere.
- **⚙️ Unified Settings Window**: Convenient, all-in-one modern settings window to configure display styles, key capture, and audio feedback in one place.

---

## ⚙️ Settings & System Tray Controls

- **Left-Click or Double-Click** the ⌨️ tray icon (or right-click and select **⚙️ Settings...**) to open the unified settings window:
  - **🎨 Appearance & Display**: Theme style, size scaling, screen position presets, manual drag repositioning, display duration, and repeat multiplier badge.
  - **⌨️ Input Detection**: Toggle keyboard capture, combination/shortcut-only filter, and mouse tracking.
  - **🔊 Audio Sound Effects**: Toggle typing & click audio, choose switch profiles (*Mechanical Switch*, *Typewriter*, *Deep Thock*, *Crisp Modern*, *Bubble Pop*), and adjust volume slider.

- **Right-Click Menu**:
  - **⚙️ Settings...**: Opens the all-in-one settings window.
  - **✨ Preview Test Keystroke**: Displays a live preview on screen.
  - **☩ Adjust Manual Position...**: Draggable overlay card to place anywhere on screen.
  - **💡 How to Reposition...**: Helpful repositioning instructions.
  - **❌ Exit**: Cleanly shuts down the visualizer.

---

## 🛠️ Development

```powershell
# 1. Clone & setup virtual environment
git clone https://github.com/galihjuansaputra/keystroke-visualizer.git
cd keystroke-visualizer
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt

# 2. Run
.\run.bat

# 3. Build standalone .exe
.\build_exe.bat
```
