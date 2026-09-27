# ⌨️ Keystroke Visualizer (Windows Fluent OSD)

A fast, lightweight, and modern Windows 11 Fluent style keystroke and mouse visualizer inspired by [KeyPress-OSD](https://github.com/marius-sucan/KeyPress-OSD).

---

## ✨ Features

- **⚡ Fast & Zero Latency**: Low-level Windows hooks (`WH_KEYBOARD_LL`, `WH_MOUSE_LL` via `ctypes`) running on an independent background thread.
- **🎨 Windows 11 Fluent Design**:
  - Dark frosted acrylic glass with bold, clean borders (`2.2px` stroke) and smooth rounded corners.
  - Symmetrical 4-way balanced margins: top, bottom, left, and right spacing are perfectly equalized.
  - Multiple built-in themes: **Dark Modern Fluent**, **Light Modern Fluent**, **Cyberpunk Neon**, and **Minimal Monochrome**.
- **🎯 Clean, Discrete Keystrokes (No Typing Spam)**:
  - Displays single key presses (e.g. `A`, `B`, `Enter`, `Tab`).
  - **1:1 Square Box**: Single keys render in an authentic 1:1 square box with rounded corners.
  - Updates immediately to the next key instead of accumulating long sentences.
  - Displays keyboard combinations cleanly (e.g., `Shift + A`, `Alt + Tab`, `Win + D`, `Ctrl + Shift + Esc`).
  - Consistent duplicate multiplier chiclet button (e.g. `×2`, `×3`) when pressing or holding the same key.
- **📏 Size Presets**:
  - **Small**: Compact (26px keys, 8px padding, 9.5pt font).
  - **Medium** *(Default)*: Standard balanced (32px keys, 10px padding, 11pt font).
  - **Large**: High-visibility / streaming (40px keys, 12px padding, 13.5pt font).
- **🖱️ Mouse Events & Combos**:
  - Visualizes `🖱️ Left`, `🖱️ Right`, `🖱️ Middle`, `🖱️ Back`, `🖱️ Forward`.
  - Visualizes scroll directions (`⬆ Scroll Up`, `⬇ Scroll Down`).
  - Supports modifier combos (e.g., `Ctrl + Left Click`, `Shift + Scroll Up`).
- **📌 Always On Top & Non-Intrusive**:
  - Stays in front of fullscreen games, IDEs, browsers, and applications without stealing focus (`SWP_NOACTIVATE`).
  - **Lock Position (Click-Through Mode)**: Mouse clicks pass through the overlay directly to your apps underneath.
- **📍 Free Repositioning & Presets**:
  - Presets: **Bottom-Center** (default, mathematically centered to 0.0px), **Bottom-Right**, **Bottom-Left**, **Top-Center**, **Top-Right**.
  - **Drag to Reposition**: Right-click the system tray icon, select **"☩ Move / Drag to Reposition..."**, and drag the overlay anywhere on your screen (even across multiple monitors!).
- **💾 Persistent Settings**: Remembers your preferred position, size, theme, display duration, and click-through mode in `config.json`.

---

## 🚀 Running from Source

1. **Clone the repository**:
   ```bash
   git clone https://github.com/galihjuansaputra/keystroke-visualizer.git
   cd keystroke-visualizer
   ```

2. **Set up virtual environment & dependencies**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\pip install -r requirements.txt
   ```

3. **Launch the visualizer**:
   - For interactive console testing:
     ```powershell
     .\run.bat
     ```
   - For silent background running:
     ```powershell
     .\run_background.bat
     ```

---

## 🛠️ Building the Standalone `.exe`
Run `build_exe.bat` or execute:
```powershell
.\.venv\Scripts\pyinstaller --noconsole --onefile --clean --icon=app_icon.ico --name="KeystrokeVisualizer" main.py
```
The compiled executable will be output to `dist/KeystrokeVisualizer.exe`.

---

## ⚙️ System Tray Controls
Look for the keyboard icon in your Windows Taskbar System Tray (notification area). Right-click to access:
1. **✨ Preview Test Keystroke**: Tests the overlay styling.
2. **📍 Position Presets**: Switch between Bottom-Center, Bottom-Right, Top-Center, etc.
3. **☩ Move / Drag to Reposition**: Keeps the card visible so you can drag it anywhere.
4. **🔒 Lock Position (Pass-Through Clicks)**: Makes clicks pass through so you can game/type without obstruction.
5. **🎨 Themes**: Dark Modern, Light, Cyberpunk Neon, Minimal.
6. **📏 Size**: Small, Medium, Large.
7. **⏱️ Display Duration**: Fast (0.8s), Normal (1.2s), Relaxed (2.0s), Long (3.0s).
8. **🖱️ Visualize Mouse**: Enable or disable mouse clicks/wheel.
9. **🔢 Show Multiplier**: Toggle repeat counts (`×2`).
10. **❌ Exit**: Safely unhooks and shuts down.
