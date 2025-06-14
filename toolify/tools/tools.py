import re
import sys
import logging
import psutil
import platform
import arabic_reshaper
from bidi.algorithm import get_display
from typing import Union, List, Tuple

# ANSI color codes

_COLOR_VALUES = {
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

# Foreground color aliases
COLORS = {
    # Primary names
    "white": _COLOR_VALUES["white"],
    "red": _COLOR_VALUES["red"],
    "green": _COLOR_VALUES["green"],
    "blue": _COLOR_VALUES["blue"],
    "yellow": _COLOR_VALUES["yellow"],
    "cyan": _COLOR_VALUES["cyan"],
    "magenta": _COLOR_VALUES["magenta"],
    "bred": _COLOR_VALUES["bright_red"],
    "bgreen": _COLOR_VALUES["bright_green"],
    "bblue": _COLOR_VALUES["bright_blue"],
    "byellow": _COLOR_VALUES["bright_yellow"],
    "bcyan": _COLOR_VALUES["bright_cyan"],
    "bmagenta": _COLOR_VALUES["bright_magenta"],
    "bwhite": _COLOR_VALUES["bright_white"],
    "bblack": _COLOR_VALUES["bright_black"],
    
    # Numeric aliases
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

# Background color aliases
BCOLOR = {
    # Primary names
    "black": _BACKGROUND_VALUES["black"],
    "red": _BACKGROUND_VALUES["red"],
    "green": _BACKGROUND_VALUES["green"],
    "yellow": _BACKGROUND_VALUES["yellow"],
    "blue": _BACKGROUND_VALUES["blue"],
    "magenta": _BACKGROUND_VALUES["magenta"],
    "cyan": _BACKGROUND_VALUES["cyan"],
    "white": _BACKGROUND_VALUES["white"],
    
    # Bright variants
    "bblack": _BACKGROUND_VALUES["bright_black"],
    "bred": _BACKGROUND_VALUES["bright_red"],
    "bgreen": _BACKGROUND_VALUES["bright_green"],
    "byellow": _BACKGROUND_VALUES["bright_yellow"],
    "bblue": _BACKGROUND_VALUES["bright_blue"],
    "bmagenta": _BACKGROUND_VALUES["bright_magenta"],
    "bcyan": _BACKGROUND_VALUES["bright_cyan"],
    "bwhite": _BACKGROUND_VALUES["bright_white"],
    
    # Numeric aliases
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


# Emoji mappings 
EMOS = {
    "launch": "🚀",
    "check": "✅",
    "cross": "❌",
    "warn1": "⚠️",
    "warn2": "⛔️",
    "warn3": "🛑",
    "ok": "🆗",
    "done": "✔️",
    "arrow": "⏩",
    "retry": "🔄",
    "fix": "🛠️",
    "lock": "🔒",
    "unlock": "🔓",
    "settings": "⚙️",
    "star": "⭐️",
    "heart": "❤️",
    "fire": "🔥",
    "error": "💥",
    "clock": "🕒",
    "bye": "👋🏻",
}

RESET_COLOR = "\033[0m"
DEFAULT_COLOR = "\033[37m"


def pct(text: str, color: Union[str, int] = 1, bcolor: Union[str, int] = None, emoji: str = "") -> None:
    """Prints text in the specified color with an optional emoji.

    Args:
        text: The text to print.
        color: Color code (int from COLORS or str from COLORS_STR). Defaults to 1 (white).
        emoji: Emoji key from EMOS dictionary. Defaults to empty string.
    """
    color_code = COLORS.get(color, DEFAULT_COLOR)
    bcode_code = BCOLOR.get(bcolor, "") if bcolor is not None else ""
    emoji_char = EMOS.get(emoji, "")

    formatted_text = f"{color_code}{bcode_code}{text}{RESET_COLOR}"
    if emoji_char:
        print(f"{emoji_char} {formatted_text}")
    else:
        print(formatted_text)


def pctm(text: str, tokens: list[int], colors: list, emoji: str = "") -> None:
    """Prints colored text with multiple color segments and an optional emoji prefix.

    The function splits the input text into segments based on the token counts and
    applies corresponding colors to each segment. An optional emoji can be prefixed
    to the final output.

    Args:
        text: The text to be colored and printed.
        tokens: A list of integers specifying how many words each color should apply to.
        colors: A list of color specifications for each token segment.
            Each element can be either:
            - A single color code (str or int from COLORS)
            - A tuple of (text_color, background_color)
        emoji: Optional emoji key from EMOS dictionary to prefix the output. Defaults to "".

    Example:
        pctm("Hello world this is colored", [2, 3], ["red", ("blue", "yellow")], "smile")
        # Prints: 😊 Hello world this is colored
        # Where "Hello world" is red and "this is colored" has blue text on yellow background
    """
    if len(tokens) != len(colors):
        print("Must provide a color for each token")
        return

    text_tokens = text.split()
    next_tokens = 0
    colored_text = ""
    for token, color in zip(tokens, colors):
        if token < 0:
            token *= -1
        selected_text = text_tokens[next_tokens : token + next_tokens]
        next_tokens += token
        color_code = (
            COLORS.get(color[0], DEFAULT_COLOR)
            if len(color) == 2
            else COLORS.get(color, DEFAULT_COLOR)
        )
        bcode_code = BCOLOR.get(color[1], "") if len(color) == 2 else ""
        selected_text = " ".join(selected_text)
        colored_text += f"{color_code}{bcode_code}{selected_text}{RESET_COLOR} "
    if next_tokens != len(text_tokens):
        colored_text = (f"{colored_text}{RESET_COLOR}{' '.join(text_tokens[next_tokens:])}")

    emoji_char = EMOS.get(emoji, "")
    formatted_text = f"{colored_text}{RESET_COLOR}"

    if emoji_char:
        print(f"{emoji_char} {formatted_text}")
    else:
        print(formatted_text)


def pat(text: str, color: Union[str, int] = 1, bcolor: Union[str, int] = None, emoji: str = "") -> None:
    """Prints Arabic text with proper reshaping and bidirectional display.

    Args:
        text: The Arabic text to print.
        color: Color code (int from COLORS or str from COLORS_STR). Defaults to 1 (white).
        emoji: Emoji key from EMOS dictionary. Defaults to empty string.
    """
    reshaped_text = arabic_reshaper.reshape(text)
    displayed_text = get_display(reshaped_text)
    pct(displayed_text, color, bcolor, emoji)


def setup_logger(log_file: str = "log.log", format_type: str = "") -> logging.Logger:
    """Configures and returns a logger for logging messages to a file.

    Args:
        log_file: Path to the log file. Defaults to "log.log".
        format_type: Format of the log messages ("simple" for message only, else timestamp and level).

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger

    file_handler = logging.FileHandler(log_file)

    if format_type == "simple":
        formatter = logging.Formatter("%(message)s")
    else:
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    file_handler.setFormatter(formatter)
    logger.handlers = []
    logger.addHandler(file_handler)
    return logger


def sheel_tashkeel(text: str) -> str:
    """Removes Arabic diacritics and specific characters from text.

    Args:
        text: Input text to process.

    Returns:
        Text with diacritics and specified characters removed.
    """
    arabic_diacritics = re.compile(r"[\u0617-\u061A\u064B-\u0652\u0670]")
    return re.sub(
        arabic_diacritics,
        "",
        text.replace(">", "").replace("<", "").replace("^", "").replace("؞", ""),
    )


def get_available_gpus() -> None:
    """Prints information about available CUDA GPUs.

    Requires torch to be installed and CUDA to be available.
    """
    try:
        import torch
    except ImportError:
        print("PyTorch is not installed.")
        return

    if torch.cuda.is_available():
        print(f"Available GPUs: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
    else:
        print("No GPUs detected (CUDA not available)")


def print_system_specs():
    """Prints detailed system specifications including CPU model, number of cores, number of threads, total RAM, and disk information."""
    
    print("---------------------")
    print("System Specifications:")
    print("---------------------")
    
    # CPU Information
    print(f"CPU Model: {platform.processor()}")
    print(f"Number of Cores: {psutil.cpu_count(logical=False)}")
    print(f"Number of Threads: {psutil.cpu_count(logical=True)}")
    
    # RAM Information
    ram = psutil.virtual_memory()
    ram_total = ram.total / (1024 ** 3)  # Convert bytes to GB
    print(f"Total RAM: {ram_total:.2f} GB")
    
    # Disk Information
    disk = psutil.disk_partitions()
    if disk:
        for partition in disk:
            try:
                disk_usage = psutil.disk_usage(partition.mountpoint)
                disk_total = disk_usage.total / (1024 ** 3)  # Convert bytes to GB
                print(f"Disk ({partition.mountpoint}):")
                print(f"  Type: {partition.fstype}")
                print(f"  Size: {disk_total:.2f} GB")
            except PermissionError:
                print(f"Disk ({partition.mountpoint}): Access denied")
    else:
        print("Disk Information: Not available")
    print("---------------------")


def confirm(
    data=None,
    message="Do you want to continue? [y/yes to continue, any other key to exit]: ",
):
    """
    Prints data and asks the user to confirm continuation.

    Args:
        data: The data to display (e.g., dict, list, string).
        message: Custom prompt message (default provided).

    Returns:
        None: Exits the program if the user doesn't confirm with 'y' or 'yes'.
    """
    if data:
        pct("\n=== Data ===", color="cyan")
        pct(data, color="cyan")
        pct("============\n", color="cyan")

    response = input(message).strip().lower()

    if response not in ["y", "yes"]:
        pct("Exiting program.", color="red", emoji="bye")
        sys.exit(0)


def print_available_functions() -> None:
    """Prints information about the Toolify.tools functions."""
    package_info = [
        (
            "pct", 
            "Prints text in a specified color with an optional emoji."
        ),
        (
            "pctm", 
            "Prints colored text with multiple color segments and an optional emoji prefix."
        ),
        (
            "pat",
            "Prints Arabic text with proper reshaping and bidirectional display.",
        ),
        (
            "setup_logger", 
            "Configures a logger for logging messages to a file."),
        (
            "sheel_tashkeel",
            "Removes Arabic diacritics and specific characters from text.",
        ),
        (
            "get_available_gpus", 
            "Prints information about available CUDA GPUs."),
        (
            "print_system_specs",
            "Prints detailed system specifications including CPU model, number of cores, number of threads, total RAM, and disk information."
        ),
        (
            "confirm", 
            "Prints data and asks the user to confirm continuation."),
        (
            "print_package_info",
            "Prints information about the package and its functions.",
        ),
    ]
    pct("Toolify Package Information", color="bcyan", emoji="star")
    for func_name, description in package_info:
        pct(f"{func_name}: {description}", color="white")


if __name__ == "__main__":
    text = "This is a file to help in testing and debugging"
    pct(text, color=5, emoji="star")
    pctm(text, [1,2], ["red", "green"])
    print_available_functions()
