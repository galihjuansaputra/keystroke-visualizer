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
- **🎯 Clean Keystrokes & Shortcuts**: Discrete key chiclets (1:1 square single keys) with combo support (`Ctrl + C`, `Win + D`, etc.) and repeat counters (`×2`, `×3`).
- **⚡ Combination-Only Mode**: Option to display only shortcuts and key combinations (ignoring everyday typing).
- **⌨️ / 🖱️ Independent Toggles**: Freely enable/disable keyboard capture, combination filtering, and mouse event tracking.
- **🔒 Non-Intrusive & Click-Through**: Always on top of games and fullscreen apps without stealing focus or blocking clicks.
- **📍 Free Repositioning**: Choose from 5 screen presets or drag the visualizer anywhere.
- **🎨 Themes & Sizes**: Built-in themes (*Dark Modern*, *Light Modern*, *Cyberpunk*, *Minimal*) with Small, Medium, and Large scaling.

---

## ⚙️ System Tray Controls

Right-click the ⌨️ icon in the system tray to adjust settings:

| Option | Description |
| :--- | :--- |
| **✨ Preview Test** | Test the overlay appearance immediately |
| **📍 Presets** | Bottom-Center, Bottom-Left, Bottom-Right, Top-Center, Top-Right |
| **☩ Move / Drag** | Unlock overlay to drag it anywhere across multiple monitors |
| **🎨 Themes & Size** | Switch theme styles and scale (Small / Medium / Large) |
| **⏱️ Display Duration** | Fast (0.8s), Normal (1.2s), Relaxed (2.0s), or Long (3.0s) |
| **⌨️ Visualize Keyboard** | Enable or disable keyboard visualization |
| **⚡ Only Shortcuts / Combos** | Filter display to only show key combinations (e.g. `Ctrl+C`, `Alt+Tab`) |
| **🖱️ Visualize Mouse** | Toggle mouse button tracking (clicks and scroll directions) |
| **🔢 Show Multiplier** | Toggle repeat badges (e.g. `×2`, `×3`) |

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
