import re
import sys

from gi.repository import Gdk

if sys.platform == "darwin":
    PRIMARY_MODIFIER_MASK = Gdk.ModifierType(0)
    for mask_name in ("META_MASK", "SUPER_MASK", "MOD2_MASK"):
        mask = getattr(Gdk.ModifierType, mask_name, None)
        if mask is not None:
            PRIMARY_MODIFIER_MASK |= mask
    if PRIMARY_MODIFIER_MASK == 0:
        PRIMARY_MODIFIER_MASK = Gdk.ModifierType.CONTROL_MASK
    PRIMARY_ACCEL = "<Meta>"
    PRIMARY_KEY_NAME = "Cmd"
else:
    PRIMARY_MODIFIER_MASK = Gdk.ModifierType.CONTROL_MASK
    PRIMARY_ACCEL = "<Primary>"
    PRIMARY_KEY_NAME = "Ctrl"


def is_primary_modifier(state: Gdk.ModifierType) -> bool:
    return bool(state & PRIMARY_MODIFIER_MASK)


def is_primary_keyval(keyval: int) -> bool:
    if sys.platform == "darwin":
        command_key = getattr(Gdk, "KEY_Command", None)
        primary_keys = [
            Gdk.KEY_Meta_L,
            Gdk.KEY_Meta_R,
            Gdk.KEY_Super_L,
            Gdk.KEY_Super_R,
        ]
        if command_key is not None:
            primary_keys.append(command_key)
        return keyval in primary_keys
    return keyval in (Gdk.KEY_Control_L, Gdk.KEY_Control_R)


_SHORTCUT_RE = re.compile(r"<([^>]+)>|([^<>]+)")


def format_shortcut_for_display(shortcut_str: str) -> str:
    """Format a GTK accelerator string for display in tooltips.

    On macOS, uses Unicode symbols (⌘, ⇧, ⌥, ⌃).
    On other platforms, uses text labels (Ctrl, Shift, Alt).
    """
    if not shortcut_str:
        return ""

    tokens = _SHORTCUT_RE.findall(shortcut_str)
    modifiers = []
    key = None

    for mod, k in tokens:
        if mod:
            modifiers.append(mod)
        if k:
            key = key or k

    if not key:
        return ""

    if key.isalpha() and len(key) == 1:
        key_display = key.upper()
    else:
        KEY_ALIASES = {
            "Page_Up": "PgUp",
            "Page_Down": "PgDn",
            "Delete": "Del",
            "less": "<",
            "comma": ",",
        }
        key_display = KEY_ALIASES.get(key, key)

    if sys.platform == "darwin":
        mod_symbols = {
            "Meta": "⌘",
            "Primary": "⌘",
            "Shift": "⇧",
            "Alt": "⌥",
            "Ctrl": "⌃",
        }
        parts = [mod_symbols[m] for m in modifiers if m in mod_symbols]
        parts.append(key_display)
        return "".join(parts)
    else:
        mod_names = {
            "Primary": "Ctrl",
            "Meta": "Super",
            "Shift": "Shift",
            "Alt": "Alt",
            "Ctrl": "Ctrl",
        }
        parts = [mod_names[m] for m in modifiers if m in mod_names]
        parts.append(key_display)
        sep = "+"
        return sep.join(parts)
