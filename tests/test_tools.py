import os
import logging
import pytest
from datetime import datetime

from toolify.tools import (
    pct,
    print_table,
    setup_logger,
    strip_tashkeel,
    confirm,
)


def test_strip_tashkeel_removes_arabic_diacritics():
    text = "مُحَمَّدٌ"
    result = strip_tashkeel(text)

    assert result == "محمد"


def test_strip_tashkeel_removes_special_symbols_by_default():
    text = "ا^ل>س<لام؞"
    result = strip_tashkeel(text)

    assert result == "السلام"


def test_strip_tashkeel_can_keep_special_symbols():
    text = "ا^ل>س<لام؞"
    result = strip_tashkeel(text, remove_special_symbols=False)

    assert result == "ا^ل>س<لام؞"


def test_pct_prints_plain_text_when_ec_false(capsys):
    pct("Hello Toolify", ec=False)

    captured = capsys.readouterr()

    assert captured.out == "Hello Toolify\n"


def test_pct_prints_with_emoji_when_ec_false(capsys):
    pct("Done", ec=False, emoji="success", end_emoji="fire")

    captured = capsys.readouterr()

    assert captured.out == "✅ Done 🔥\n"


def test_pct_custom_end(capsys):
    pct("Hello", ec=False, end="")

    captured = capsys.readouterr()

    assert captured.out == "Hello"


def test_print_table_outputs_headers_and_rows(capsys):
    headers = ["Name", "Score"]
    rows = [
        ["Ali", 95],
        ["Sara", 88],
    ]

    print_table(headers, rows)

    captured = capsys.readouterr()

    assert "Name" in captured.out
    assert "Score" in captured.out
    assert "Ali" in captured.out
    assert "Sara" in captured.out


def test_setup_logger_creates_log_file(tmp_path):
    date_str = datetime.now().strftime("%Y_%m_%d")
    log_file = tmp_path /f"test.log"
    logger = setup_logger(__name__, str(log_file))
    log_file = tmp_path /f"test__{date_str}.log"
    logger.info("Hello logger")

    assert isinstance(logger, logging.Logger)
    assert log_file.exists()

    content = log_file.read_text(encoding="utf-8")
    assert "Hello logger" in content


def test_confirm_returns_none_when_user_confirms(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "yes")

    result = confirm(message="Continue? ")

    assert result is None


def test_confirm_exits_when_user_declines(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "no")

    with pytest.raises(SystemExit):
        confirm(message="Continue? ")
