"""
Constants used by toolify.tools.
"""

import re

__all__ = [
    "COLORS",
    "BCOLOR",
    "EMOS",
    "RESET_COLOR",
    "DEFAULT_COLOR",
    "TABLE_STYLES",
    "ARABIC_DIACRITICS_RE",
    "SPECIAL_TASHKEEL_TRANSLATION",
]


# Raw ANSI foreground color codes
_COLOR_VALUES = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_black": "\033[90m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
}


# Raw ANSI background color codes
_BACKGROUND_VALUES = {
    "black": "\033[40m",
    "red": "\033[41m",
    "green": "\033[42m",
    "yellow": "\033[43m",
    "blue": "\033[44m",
    "magenta": "\033[45m",
    "cyan": "\033[46m",
    "white": "\033[47m",
    "bright_black": "\033[100m",
    "bright_red": "\033[101m",
    "bright_green": "\033[102m",
    "bright_yellow": "\033[103m",
    "bright_blue": "\033[104m",
    "bright_magenta": "\033[105m",
    "bright_cyan": "\033[106m",
    "bright_white": "\033[107m",
}


_COLOR_ALIASES = {
    "black": "black",
    "red": "red",
    "green": "green",
    "blue": "blue",
    "yellow": "yellow",
    "cyan": "cyan",
    "magenta": "magenta",
    "white": "white",
    "bblack": "bright_black",
    "bred": "bright_red",
    "bgreen": "bright_green",
    "bblue": "bright_blue",
    "byellow": "bright_yellow",
    "bcyan": "bright_cyan",
    "bmagenta": "bright_magenta",
    "bwhite": "bright_white",
}


# Public foreground color aliases
COLORS = {
    alias: _COLOR_VALUES[color_name] for alias, color_name in _COLOR_ALIASES.items()
}

COLORS.update(
    {
        1: _COLOR_VALUES["white"],
        2: _COLOR_VALUES["red"],
        3: _COLOR_VALUES["green"],
        4: _COLOR_VALUES["blue"],
        5: _COLOR_VALUES["yellow"],
        6: _COLOR_VALUES["cyan"],
        7: _COLOR_VALUES["magenta"],
        8: _COLOR_VALUES["bright_red"],
        9: _COLOR_VALUES["bright_green"],
        10: _COLOR_VALUES["bright_blue"],
        11: _COLOR_VALUES["bright_yellow"],
        12: _COLOR_VALUES["bright_cyan"],
        13: _COLOR_VALUES["bright_magenta"],
        14: _COLOR_VALUES["bright_white"],
        15: _COLOR_VALUES["bright_black"],
    }
)


# Public background color aliases
BCOLOR = {
    alias: _BACKGROUND_VALUES[color_name]
    for alias, color_name in _COLOR_ALIASES.items()
}

BCOLOR.update(
    {
        1: _BACKGROUND_VALUES["black"],
        2: _BACKGROUND_VALUES["red"],
        3: _BACKGROUND_VALUES["green"],
        4: _BACKGROUND_VALUES["yellow"],
        5: _BACKGROUND_VALUES["blue"],
        6: _BACKGROUND_VALUES["magenta"],
        7: _BACKGROUND_VALUES["cyan"],
        8: _BACKGROUND_VALUES["white"],
        9: _BACKGROUND_VALUES["bright_black"],
        10: _BACKGROUND_VALUES["bright_red"],
        11: _BACKGROUND_VALUES["bright_green"],
        12: _BACKGROUND_VALUES["bright_yellow"],
        13: _BACKGROUND_VALUES["bright_blue"],
        14: _BACKGROUND_VALUES["bright_magenta"],
        15: _BACKGROUND_VALUES["bright_cyan"],
        16: _BACKGROUND_VALUES["bright_white"],
    }
)


EMOS = {
    "success": "✅",
    "done": "✔️",
    "error": "❌",
    "fail": "💥",
    "warning": "⚠️",
    "stop": "🛑",
    "blocked": "⛔️",
    "ok": "🆗",
    "lock": "🔒",
    "unlock": "🔓",
    "key": "🔑",
    "info": "ℹ️",
    "note": "📝",
    "star": "⭐️",
    "fire": "🔥",
    "heart": "❤️",
    "bye": "👋🏻",
}


RESET_COLOR = "\033[0m"
DEFAULT_COLOR = _COLOR_VALUES["white"]


TABLE_STYLES = {
    1: ["╔", "═", "╗", "║", "╚", "╝", "╠", "╬", "╣", "╦", "╩"],
    2: ["┌", "─", "┐", "│", "└", "┘", "├", "┼", "┤", "┬", "┴"],
    3: ["╭", "─", "╮", "│", "╰", "╯", "├", "┼", "┤", "┬", "┴"],
    4: ["┏", "━", "┓", "┃", "┗", "┛", "┣", "╋", "┫", "┳", "┻"],
    5: ["┌", "╌", "┐", "│", "└", "┘", "├", "┼", "┤", "┬", "┴"],
    6: ["+", "-", "+", "|", "+", "+", "+", "+", "+", "+", "+"],
    7: [" ", "-", " ", " ", " ", " ", " ", "-", " ", "-", "-"],
    8: ["|", "-", "|", "|", "|", "|", "|", "|", "|", "|", "|"],
    9: ["╔", "─", "╗", "│", "╚", "╝", "├", "┼", "┤", "╦", "╩"],
}


# More complete Arabic diacritics/Quranic marks range
ARABIC_DIACRITICS_RE = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")


# Special symbols used in your Egyptian Arabic diacritization work
SPECIAL_TASHKEEL_TRANSLATION = str.maketrans("", "", "><^؞")
