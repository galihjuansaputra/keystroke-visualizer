"""
sound.py - Native Ultra-Low-Latency Windows Memory Audio Engine
Uses in-memory PCM wave synthesis and Windows winmm.PlaySoundW for instant, zero-latency playback.
Completely eliminates multi-stream buffer bleeding, residual overlap, and audio lag.
"""

import sys
import os
import wave
import struct
import io
import ctypes
from PyQt6.QtCore import QObject

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    SOUNDS_DIR = os.path.join(sys._MEIPASS, "sounds")
else:
    SOUNDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")

SOUND_PROFILES = ["Mechanical Switch"]

HEAVY_KEYS = {
    "Space", "Enter", "Return", "Backspace", "Tab", "CapsLock", "Shift",
    "Ctrl", "Alt", "Win", "Delete", "Insert", "PageUp", "PageDown",
    "Home", "End", "Esc", "Menu", "NumLock", "ScrollLock", "Pause", "PrtScn"
}

# Windows Multimedia PlaySound flags
SND_ASYNC = 0x0001
SND_NODEFAULT = 0x0002
SND_MEMORY = 0x0004
SND_PURGE = 0x0040
PLAY_FLAGS = SND_MEMORY | SND_ASYNC | SND_NODEFAULT

winmm = ctypes.windll.winmm


class SoundManager(QObject):
    """
    High-performance, zero-latency sound engine using in-memory PCM audio and winmm.PlaySoundW.
    Plays instantly from RAM with exact digital volume scaling and atomic sound switching.
    """
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.cfg = config_manager

        # Raw audio buffers (unscaled)
        self._raw_kb_normal = self._read_wav_data("kb_mechanical_1.wav")
        self._raw_kb_heavy = self._read_wav_data("kb_mechanical_2.wav")
        self._raw_mouse_down = self._read_wav_data("mouse_down_1.wav")
        self._raw_mouse_up = self._read_wav_data("mouse_up_1.wav")
        self._raw_mouse_scroll = self._read_wav_data("mouse_scroll.wav")

        # Rendered memory buffers (volume scaled)
        self._buf_kb_normal = None
        self._buf_kb_heavy = None
        self._buf_mouse_down = None
        self._buf_mouse_up = None
        self._buf_mouse_scroll = None

        self._rebuild_volume_buffers()

    def _read_wav_data(self, filename: str):
        fpath = os.path.join(SOUNDS_DIR, filename)
        if not os.path.exists(fpath):
            return None
        try:
            with wave.open(fpath, "rb") as w:
                return {
                    "channels": w.getnchannels(),
                    "sampwidth": w.getsampwidth(),
                    "framerate": w.getframerate(),
                    "frames": w.readframes(w.getnframes())
                }
        except Exception as e:
            print(f"[SoundManager] Error reading {filename}: {e}")
            return None

    def _scale_and_encode_wav(self, raw_data, volume: float) -> bytes:
        if not raw_data:
            return b""

        vol = max(0.0, min(1.0, float(volume)))
        sampwidth = raw_data["sampwidth"]
        data = raw_data["frames"]

        if sampwidth == 2:
            n_samples = len(data) // 2
            samples = struct.unpack(f"<{n_samples}h", data)
            scaled = [int(max(-32767, min(32767, s * vol))) for s in samples]
            encoded_frames = struct.pack(f"<{len(scaled)}h", *scaled)
        else:
            encoded_frames = data

        bio = io.BytesIO()
        with wave.open(bio, "wb") as w:
            w.setnchannels(raw_data["channels"])
            w.setsampwidth(sampwidth)
            w.setframerate(raw_data["framerate"])
            w.writeframes(encoded_frames)
        return bio.getvalue()

    def _rebuild_volume_buffers(self):
        kb_vol = float(self.cfg.get("sound_volume_keyboard", self.cfg.get("sound_volume", 0.75)))
        mouse_vol = float(self.cfg.get("sound_volume_mouse", 0.45))

        self._buf_kb_normal = self._scale_and_encode_wav(self._raw_kb_normal, kb_vol)
        self._buf_kb_heavy = self._scale_and_encode_wav(self._raw_kb_heavy, kb_vol)
        self._buf_mouse_down = self._scale_and_encode_wav(self._raw_mouse_down, mouse_vol)
        self._buf_mouse_up = self._scale_and_encode_wav(self._raw_mouse_up, mouse_vol * 0.90)
        self._buf_mouse_scroll = self._scale_and_encode_wav(self._raw_mouse_scroll, mouse_vol * 0.85)

    def set_keyboard_volume(self, volume: float):
        """Updates keyboard audio volume (0.0 to 1.0)."""
        vol = max(0.0, min(1.0, float(volume)))
        self.cfg.set("sound_volume_keyboard", vol)
        self._buf_kb_normal = self._scale_and_encode_wav(self._raw_kb_normal, vol)
        self._buf_kb_heavy = self._scale_and_encode_wav(self._raw_kb_heavy, vol)

    def set_mouse_volume(self, volume: float):
        """Updates mouse audio volume (0.0 to 1.0)."""
        vol = max(0.0, min(1.0, float(volume)))
        self.cfg.set("sound_volume_mouse", vol)
        self._buf_mouse_down = self._scale_and_encode_wav(self._raw_mouse_down, vol)
        self._buf_mouse_up = self._scale_and_encode_wav(self._raw_mouse_up, vol * 0.90)
        self._buf_mouse_scroll = self._scale_and_encode_wav(self._raw_mouse_scroll, vol * 0.85)

    def play_keyboard_sound(self, key_name: str = ""):
        """Plays a mechanical keyboard sound directly from memory."""
        if not self.cfg.get("sound_keyboard", True):
            return

        is_heavy = False
        if key_name:
            kn_clean = key_name.strip().lower()
            is_heavy = any(h.lower() == kn_clean or h.lower() in kn_clean for h in HEAVY_KEYS)

        target_buf = self._buf_kb_heavy if (is_heavy and self._buf_kb_heavy) else self._buf_kb_normal
        if target_buf:
            winmm.PlaySoundW(target_buf, 0, PLAY_FLAGS)

    def play_mouse_sound(self):
        """Plays a crisp mouse down click directly from memory."""
        if not self.cfg.get("sound_mouse_click", self.cfg.get("sound_mouse", True)) or not self._buf_mouse_down:
            return
        winmm.PlaySoundW(self._buf_mouse_down, 0, PLAY_FLAGS)

    def play_mouse_release_sound(self):
        """Plays a crisp mouse up release click directly from memory."""
        if not self.cfg.get("sound_mouse_click", self.cfg.get("sound_mouse", True)) or not self._buf_mouse_up:
            return
        winmm.PlaySoundW(self._buf_mouse_up, 0, PLAY_FLAGS)

    def play_mouse_scroll_sound(self):
        """Plays a rotary scroll wheel tick directly from memory."""
        if not self.cfg.get("sound_mouse_scroll", self.cfg.get("sound_mouse", True)) or not self._buf_mouse_scroll:
            return
        winmm.PlaySoundW(self._buf_mouse_scroll, 0, PLAY_FLAGS)

    def handle_audio_event(self, category: str, action_name: str = ""):
        """Dedicated slot for InputHookThread.audio_event signal."""
        if category == "keyboard":
            self.play_keyboard_sound(key_name=action_name)
        elif category == "mouse_down":
            self.play_mouse_sound()
        elif category == "mouse_up":
            self.play_mouse_release_sound()
        elif category == "mouse_scroll":
            self.play_mouse_scroll_sound()
