import re
import sys
import logging
from itertools import cycle
import arabic_reshaper
from bidi.algorithm import get_display
from typing import Union, List, Tuple

# ANSI color codes
COLORS_STR = {
    # Foreground
    "white": "\033[37m",
    "red": "\033[31m",
    "green": "\033[32m",
    "blue": "\033[34m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "magenta": "\033[35m",
    "bred": "\033[91m",
    "bgreen": "\033[92m",
    "bblue": "\033[94m",
    "byellow": "\033[93m",
    "bcyan": "\033[96m",
    "bmagenta": "\033[95m",
    "bwhite": "\033[97m",
    "bblack": "\033[90m",
    # Background
    "bg_red": "\033[41m",
    "bg_green": "\033[42m",
    "bg_blue": "\033[44m",
    "bg_yellow": "\033[43m",
    "bg_cyan": "\033[46m",
    "bg_magenta": "\033[45m",
    "bg_white": "\033[47m",
    "bg_black": "\033[40m",
    "bg_bred": "\033[101m",
    "bg_bgreen": "\033[102m",
    "bg_bblue": "\033[104m",
    "bg_byellow": "\033[103m",
    "bg_bcyan": "\033[106m",
    "bg_bmagenta": "\033[105m",
    "bg_bwhite": "\033[107m",
    "bg_bblack": "\033[100m",
}

COLORS = {
    1: "\033[37m",  # white
    2: "\033[31m",  # red
    3: "\033[32m",  # green
    4: "\033[34m",  # blue
    5: "\033[33m",  # yellow
    6: "\033[36m",  # cyan
    7: "\033[35m",  # magenta
    8: "\033[91m",  # bright red
    9: "\033[92m",  # bright green
    10: "\033[94m",  # bright blue
    11: "\033[93m",  # bright yellow
    12: "\033[96m",  # bright cyan
    13: "\033[95m",  # bright magenta
    14: "\033[97m",  # bright white
    15: "\033[90m",  # bright black
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


def pct(text: str, color: Union[str, int] = 1, emoji: str = "") -> None:
    """Prints text in the specified color with an optional emoji.

    Args:
        text: The text to print.
        color: Color code (int from COLORS or str from COLORS_STR). Defaults to 1 (white).
        emoji: Emoji key from EMOS dictionary. Defaults to empty string.
    """
    color_code = COLORS.get(color) or COLORS_STR.get(color, DEFAULT_COLOR)
    emoji_char = EMOS.get(emoji, "")
    if emoji_char:
        print(f"{emoji_char} {color_code}{text}{RESET_COLOR}")
    else:
        print(f"{color_code}{text}{RESET_COLOR}")


def pat(text: str, color: Union[str, int] = 1, emoji: str = "") -> None:
    """Prints Arabic text with proper reshaping and bidirectional display.

    Args:
        text: The Arabic text to print.
        color: Color code (int from COLORS or str from COLORS_STR). Defaults to 1 (white).
        emoji: Emoji key from EMOS dictionary. Defaults to empty string.
    """
    reshaped_text = arabic_reshaper.reshape(text)
    displayed_text = get_display(reshaped_text)
    pct(displayed_text, color, emoji)


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




def line_plotter(
    data_list: List[List[float]],
    save_name: str,
    legend_list: List[str] = [],
    x_values: List[float] = [],
    x_label: str = "",
    y_label: str = "",
    title: str = "",
    size: Tuple[int, int] = (10, 6),
) -> None:
    """Saves a line plot for each list in data_list.

    Args:
        data_list: List of data lists to plot.
        save_name: File path to save the plot.
        legend_list: List of legend labels for each data list. If empty, no legend is shown.
        x_values: Values for the x-axis. If empty, uses range(len(data_list[0])).
        x_label: Label for the x-axis. Defaults to empty string.
        y_label: Label for the y-axis. Defaults to empty string.
        title: Title of the plot. Defaults to empty string.
        size: Figure size as (width, height). Defaults to (10, 6).

    Raises:
        ValueError: If data_list is empty, legend_list length mismatches, or data lists have different sizes.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed.")
        return

    if not data_list:
        raise ValueError("data_list cannot be empty")
    if legend_list and len(data_list) != len(legend_list):
        raise ValueError("Length of data_list must match length of legend_list")

    data_lengths = {len(data) for data in data_list}
    if len(data_lengths) > 1:
        raise ValueError("All lists in data_list must have the same size")

    plt.figure(figsize=size)
    if not x_values:
        x_values = list(range(len(data_list[0])))

    colors = cycle(["blue", "red", "green", "purple", "orange", "cyan", "magenta"])
    markers = cycle(["o", "s", "^", "D", "v", "<", ">"])
    linestyles = cycle(["-", "--", ":", "-."])

    for data, color, marker, linestyle in zip(data_list, colors, markers, linestyles):
        if legend_list:
            plt.plot(
                x_values,
                data,
                marker=marker,
                linestyle=linestyle,
                color=color,
                label=legend_list[0],
            )
            legend_list = legend_list[1:]  # Avoid mutating original list
        else:
            plt.plot(x_values, data, marker=marker, linestyle=linestyle, color=color)

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    if legend_list:
        plt.legend()

    plt.grid(True, linestyle="--", alpha=0.7)
    plt.savefig(save_name, dpi=300, bbox_inches="tight")
    plt.close()


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


def print_package_info() -> None:
    """Prints information about the Toolify package and its functions."""
    package_info = [
        ("pct", "Prints text in a specified color with an optional emoji."),
        (
            "print_arabic_text",
            "Prints Arabic text with proper reshaping and bidirectional display.",
        ),
        ("setup_logger", "Configures a logger for logging messages to a file."),
        ("line_plotter", "Saves a line plot for multiple data lists."),
        (
            "sheel_tashkeel",
            "Removes Arabic diacritics and specific characters from text.",
        ),
        ("get_available_gpus", "Prints information about available CUDA GPUs."),
        ("confirm", "Prints data and asks the user to confirm continuation."),
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
    print_package_info()
