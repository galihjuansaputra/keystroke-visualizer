"""
keys.py - Key and Mouse Event Translation & Formatting for Keystroke Visualizer
"""

# Windows Virtual Key Codes
VK_MAP = {
    # Modifiers
    0x10: "Shift",
    0x11: "Ctrl",
    0x12: "Alt",
    0x14: "CapsLock",
    0x5B: "Win",
    0x5C: "Win",
    0xA0: "LShift",
    0xA1: "RShift",
    0xA2: "LCtrl",
    0xA3: "RCtrl",
    0xA4: "LAlt",
    0xA5: "RAlt",

    # Navigation & Control
    0x08: "Backspace",
    0x09: "Tab",
    0x0D: "Enter",
    0x1B: "Esc",
    0x20: "Space",
    0x21: "PageUp",
    0x22: "PageDown",
    0x23: "End",
    0x24: "Home",
    0x25: "←",
    0x26: "↑",
    0x27: "→",
    0x28: "↓",
    0x2D: "Insert",
    0x2E: "Delete",
    0x5D: "Menu",
    0x2C: "PrtScn",
    0x13: "Pause",
    0x90: "NumLock",
    0x91: "ScrollLock",

    # Function Keys
    0x70: "F1", 0x71: "F2", 0x72: "F3", 0x73: "F4",
    0x74: "F5", 0x75: "F6", 0x76: "F7", 0x77: "F8",
    0x78: "F9", 0x79: "F10", 0x7A: "F11", 0x7B: "F12",
    0x7C: "F13", 0x7D: "F14", 0x7E: "F15", 0x7F: "F16",
    0x80: "F17", 0x81: "F18", 0x82: "F19", 0x83: "F20",
    0x84: "F21", 0x85: "F22", 0x86: "F23", 0x87: "F24",

    # Media / Audio Keys
    0xAD: "Mute",
    0xAE: "VolDown",
    0xAF: "VolUp",
    0xB0: "NextTrack",
    0xB1: "PrevTrack",
    0xB2: "StopMedia",
    0xB3: "Play/Pause",

    # Numpad Keys
    0x60: "Num 0", 0x61: "Num 1", 0x62: "Num 2", 0x63: "Num 3",
    0x64: "Num 4", 0x65: "Num 5", 0x66: "Num 6", 0x67: "Num 7",
    0x68: "Num 8", 0x69: "Num 9",
    0x6A: "Num *", 0x6B: "Num +", 0x6C: "Num Sep",
    0x6D: "Num -", 0x6E: "Num .", 0x6F: "Num /",

    # OEM punctuation keys
    0xBA: ";", 0xBB: "=", 0xBC: ",", 0xBD: "-", 0xBE: ".", 0xBF: "/",
    0xC0: "`", 0xDB: "[", 0xDC: "\\", 0xDD: "]", 0xDE: "'",
    0xDF: "OEM",
}

SHIFT_OEM_MAP = {
    "`": "~", "1": "!", "2": "@", "3": "#", "4": "$", "5": "%",
    "6": "^", "7": "&", "8": "*", "9": "(", "0": ")", "-": "_",
    "=": "+", "[": "{", "]": "}", "\\": "|", ";": ":", "'": "\"",
    ",": "<", ".": ">", "/": "?"
}

MODIFIER_KEYS = {
    0x10, 0xA0, 0xA1,  # Shift
    0x11, 0xA2, 0xA3,  # Ctrl
    0x12, 0xA4, 0xA5,  # Alt
    0x5B, 0x5C,        # Win
}

NAV_AND_SPECIAL_KEYS = {
    "Backspace", "Tab", "Enter", "Esc", "PageUp", "PageDown",
    "End", "Home", "←", "↑", "→", "↓", "Insert", "Delete",
    "Menu", "PrtScn", "Pause",
} | {f"F{i}" for i in range(1, 25)}


class KeyFormatter:
    @staticmethod
    def get_key_name(vk_code: int, scan_code: int, is_shift: bool = False) -> str:
        # Check standard alphanumeric keys (0-9)
        if 0x30 <= vk_code <= 0x39:
            return chr(vk_code)
        
        # Letter A-Z
        if 0x41 <= vk_code <= 0x5A:
            return chr(vk_code)
        
        # Check mapping table
        if vk_code in VK_MAP:
            return VK_MAP[vk_code]
        
        # Fallback to ASCII if printable
        if 32 <= vk_code <= 126:
            return chr(vk_code)
        
        return f"Key_{vk_code}"

    @staticmethod
    def format_event(modifiers: dict, main_key: str, is_mouse: bool = False) -> list[str]:
        """
        Returns a list of token strings representing the combo.
        e.g. ['Ctrl', 'Shift', 'A'] or ['Win', 'E'] or ['Alt', 'Tab'] or ['Ctrl', 'Left Click']
        """
        tokens = []
        if modifiers.get("ctrl"):
            tokens.append("Ctrl")
        if modifiers.get("shift"):
            tokens.append("Shift")
        if modifiers.get("alt"):
            tokens.append("Alt")
        if modifiers.get("win"):
            tokens.append("Win")
        
        # If main_key is already one of the active modifiers, don't duplicate
        # e.g. user just pressed or released a lone Shift/Ctrl/Alt/Win
        if main_key in ("Ctrl", "Shift", "Alt", "Win"):
            if not tokens:
                tokens.append(main_key)
        else:
            tokens.append(main_key)
            
        return tokens

    @staticmethod
    def is_combination(modifiers: dict, vk_code: int, main_key: str, tokens: list[str]) -> bool:
        """
        Determines whether a key event represents a key combination / shortcut.
        A combination involves:
        - Non-modifier key with Ctrl, Alt, or Win (e.g. Ctrl+C, Alt+Tab, Win+R, Ctrl+Shift+P)
        - Shift with navigation/function/control keys (e.g. Shift+Tab, Shift+Enter, Shift+F10)
        - Excludes lone modifier presses (e.g. pressing just Shift, Ctrl, Alt, Win)
        - Excludes regular single-key typing (e.g. 'A', '1', 'space')
        """
        # Lone modifiers are not combinations
        if vk_code in MODIFIER_KEYS:
            return False

        has_ctrl = modifiers.get("ctrl", False)
        has_alt = modifiers.get("alt", False)
        has_win = modifiers.get("win", False)
        has_shift = modifiers.get("shift", False)

        # Primary modifier combos: Ctrl + Key, Alt + Key, Win + Key
        if has_ctrl or has_alt or has_win:
            return True

        # Shift + Navigation / Function / Special keys (e.g. Shift+Tab, Shift+Delete, Shift+F5, Shift+Arrow)
        if has_shift and main_key in NAV_AND_SPECIAL_KEYS:
            return True

        return False


