__all__ = [
    "pct",
    "pat",
    "print_table",
    "setup_logger",
    "strip_tashkeel",
    "confirm",
]


import sys
import logging
from typing import Union, Optional, Sequence, Any
from pathlib import Path
from uuid import uuid4
from datetime import datetime

try:
    from .constants import (
        COLORS,
        BCOLOR,
        EMOS,
        RESET_COLOR,
        DEFAULT_COLOR,
        TABLE_STYLES,
        ARABIC_DIACRITICS_RE,
        SPECIAL_TASHKEEL_TRANSLATION,
    )
except ImportError:
    # Allows running tools.py directly during local debugging.
    from constants import (
        COLORS,
        BCOLOR,
        EMOS,
        RESET_COLOR,
        DEFAULT_COLOR,
        TABLE_STYLES,
        ARABIC_DIACRITICS_RE,
        SPECIAL_TASHKEEL_TRANSLATION,
    )


def _resolve_color(color: Union[str, int], default=DEFAULT_COLOR) -> str:
    return COLORS.get(color, default)


def _resolve_bcolor(bcolor: Optional[Union[str, int]]) -> str:
    if bcolor is None:
        return ""
    return BCOLOR.get(bcolor, "")


def _resolve_emoji(emoji: str) -> str:
    return EMOS.get(emoji, "")


def pct(
    text: Any,
    color: Union[str, int] = 1,
    bcolor: Optional[Union[str, int]] = None,
    emoji: str = "",
    end_emoji: str = "",
    end: str = "\n",
    ec: bool = True,
) -> None:
    """Prints text with optional color, background color, and emojis.

    Args:
        text: Text to print.
        ec: If True, apply ANSI colors.
        color: Foreground color key.
        bcolor: Background color key.
        emoji: Emoji key printed before the text.
        end_emoji: Emoji key printed after the text.
        end: String appended after the printed text.
    """
    if ec:
        color_code = _resolve_color(color)
        bcolor_code = _resolve_bcolor(bcolor)
        reset_code = RESET_COLOR
    else:
        color_code = ""
        bcolor_code = ""
        reset_code = ""

    emoji_char = _resolve_emoji(emoji)
    end_emoji_char = _resolve_emoji(end_emoji)

    formatted_text = f"{color_code}{bcolor_code}{text}{reset_code}"

    if emoji_char:
        formatted_text = f"{emoji_char} {formatted_text}"

    if end_emoji_char:
        formatted_text = f"{formatted_text} {end_emoji_char}"

    print(formatted_text, end=end)


_ARABIC_RESHAPER = None


def _get_arabic_reshaper():
    """Lazily initializes and returns an ArabicReshaper instance."""
    global _ARABIC_RESHAPER

    if _ARABIC_RESHAPER is not None:
        return _ARABIC_RESHAPER

    try:
        from arabic_reshaper import ArabicReshaper
    except ImportError as exc:
        raise ImportError(
            "pat() requires 'arabic-reshaper'. "
            "Install it with: pip install arabic-reshaper"
        ) from exc

    configuration = {
        "delete_harakat": False,
        "shift_harakat_position": False,
        "use_unshaped_instead_of_isolated": True,
    }

    _ARABIC_RESHAPER = ArabicReshaper(configuration=configuration)
    return _ARABIC_RESHAPER


def pat(
    text: str,
    color: Union[str, int] = 1,
    bcolor: Optional[Union[str, int]] = None,
    emoji: str = "",
    end_emoji: str = "",
    end: str = "\n",
    ec: bool = True,
) -> None:
    """Prints Arabic text with proper reshaping and bidirectional display.

    Args:
        text: Arabic text to print.
        color: Foreground color key.
        bcolor: Background color key.
        emoji: Emoji key printed before the text.
        end_emoji: Emoji key printed after the text.
        end: String appended after the printed text.
        ec: If True, apply ANSI colors.
    """
    try:
        from bidi.algorithm import get_display
    except ImportError as exc:
        raise ImportError(
            "pat() requires 'python-bidi'. " "Install it with: pip install python-bidi"
        ) from exc

    reshaper = _get_arabic_reshaper()
    reshaped_text = reshaper.reshape(str(text))
    displayed_text = get_display(reshaped_text)

    pct(
        displayed_text,
        ec=ec,
        color=color,
        bcolor=bcolor,
        emoji=emoji,
        end_emoji=end_emoji,
        end=end,
    )


def print_table(
    headers: Sequence[Any],
    rows: Sequence[Sequence[Any]],
    style: int = 1,
    separator: bool | None = None,
) -> None:
    """Prints a simple formatted table.

    Short rows are automatically padded with empty strings.
    Rows with more columns than headers raise a ValueError.

    Args:
        headers: Table column headers.
        rows: Table rows.
        style: Table style ID from TABLE_STYLES.
        separator: If True, prints a separator line between rows.
    """
    if not headers or not rows:
        print("Empty data")
        return

    if style not in TABLE_STYLES:
        raise ValueError(
            f"Invalid table style: {style}. "
            f"Available styles are: {list(TABLE_STYLES.keys())}"
        )

    # Normalize rows:
    # - Short rows are padded with empty strings.
    # - Long rows raise an error.
    normalized_rows = []
    for idx, row in enumerate(rows):
        row = list(row)

        if len(row) > len(headers):
            raise ValueError(
                f"Row {idx} has {len(row)} columns, but expected at most {len(headers)}"
            )

        if len(row) < len(headers):
            row = row + [""] * (len(headers) - len(row))

        normalized_rows.append(row)

    # Calculate maximum width for each column.
    col_widths = [len(str(header)) for header in headers]

    for row in normalized_rows:
        for i, item in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(item)))

    style_chars = TABLE_STYLES[style]

    # Build table components.
    line_const = [style_chars[1] * (width + 2) for width in col_widths]

    top_border = style_chars[0] + style_chars[9].join(line_const) + style_chars[2]
    separator_line = style_chars[6] + style_chars[7].join(line_const) + style_chars[8]
    bottom_border = style_chars[4] + style_chars[10].join(line_const) + style_chars[5]

    # Print top border.
    print(top_border)

    # Print header row.
    header_row = style_chars[3] + " "
    for i, header in enumerate(headers):
        header_row += f"{str(header):<{col_widths[i]}} {style_chars[3]} "
    print(header_row.rstrip())

    print(separator_line)

    # Print data rows.
    for idx, row in enumerate(normalized_rows):
        row_str = style_chars[3] + " "

        for i, item in enumerate(row):
            row_str += f"{str(item):<{col_widths[i]}} {style_chars[3]} "

        print(row_str.rstrip())

        if separator and idx < len(normalized_rows) - 1:
            print(separator_line)

    print(bottom_border)


def setup_logger(
    base_name: str,
    log_file: str | Path,
    level: int = logging.INFO,
    to_console: bool = False,
    unique: bool = False,
    log_format: str = "simple",
) -> logging.Logger:
    """
    Create an isolated logger instance.
    """
    date_str = datetime.now().strftime("%Y_%m_%d")
    log_file = Path(log_file)

    if log_file.suffix == ".log":
        log_file = log_file.with_name(f"{log_file.stem}__{date_str}{log_file.suffix}")
    else:
        log_file = log_file.with_name(f"{log_file.name}__{date_str}.log")

    if len(log_file.parts) == 1:
        log_file = Path("logs") / log_file

    # uniqueness
    logger_name = (
        f"{base_name}_{uuid4().hex}_{date_str}" if unique else f"{base_name}_{date_str}"
    )

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.propagate = False  # prevent root duplication

    # Clean handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Formatter
    if log_format == "simple":
        formatter = logging.Formatter("%(message)s")
    elif log_format == "full":
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    elif "%" in log_format:
        formatter = logging.Formatter(
            log_format,
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    else:
        raise ValueError(
            "log_format must be 'simple', 'full', or a valid logging format string."
        )

    # File handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8", mode="a")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def strip_tashkeel(text: str, remove_special_symbols: bool = True) -> str:
    """Removes Arabic diacritics and optionally special diacritization symbols.

    Args:
        text: Input text.
        remove_special_symbols: If True, removes >, <, ^, and ؞.

    Returns:
        Text with Arabic diacritics removed.
    """
    text = str(text)

    if remove_special_symbols:
        text = text.translate(SPECIAL_TASHKEEL_TRANSLATION)

    return ARABIC_DIACRITICS_RE.sub("", text).strip()


def confirm(
    data=None,
    message="Do you want to continue? [y/yes to continue, any other key to exit]: ",
):
    """
    Prints data and asks the user to confirm continuation.

    Args:
        data: Data to display.
        message: Custom prompt message.

    Returns:
        None: Exits the program if the user doesn't confirm with 'y' or 'yes'.
    """
    if data is not None:
        pct("\n=== Data ===", color="cyan")
        pct(text=data, color="cyan")
        pct("============\n", color="cyan")

    response = input(message).strip().lower()

    if response not in ["y", "yes"]:
        pct("Exiting program.", color="red", emoji="bye")
        sys.exit(0)
