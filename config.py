"""
config.py - Persistent configuration management
"""

import json
import os
import sys

DEFAULT_CONFIG = {
    "preset": "Bottom-Center",
    "custom_x": None,
    "custom_y": None,
    "display_duration_ms": 1200,
    "fade_duration_ms": 250,
    "theme": "Dark Modern Fluent",
    "size": "Medium",
    "capture_keyboard": True,
    "only_combinations": False,
    "capture_mouse": True,
    "show_repeat_count": True,
    "click_through": True,
    "scale": 1.0
}


CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


class ConfigManager:
    def __init__(self):
        self.data = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except Exception as e:
                print(f"Error loading config.json: {e}")

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving config.json: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()
