# Terminal and Text

Import the general helpers from `toolify.tools`.

## Styled output

`pct` prints optional foreground color, background color, and emojis:

```python
from toolify.tools import pct

pct("Completed", color="green", emoji="success")
pct(
    "Warning",
    color="black",
    bcolor="yellow",
    emoji="warning",
    end_emoji="fire",
)
```

Use `ec=False` to disable ANSI escape codes and `end=""` to avoid adding a
newline.

## Arabic display

`pat` reshapes Arabic characters and applies bidirectional display:

```python
from toolify.tools import pat

pat("مرحبا بالعالم", color="blue", emoji="heart")
```

Remove Arabic diacritics with `strip_tashkeel`:

```python
from toolify.tools import strip_tashkeel

strip_tashkeel("مُحَمَّدٌ")  # "محمد"
strip_tashkeel("ا^ل>س<لام؞")  # "السلام"
```

Set `remove_special_symbols=False` to preserve `>`, `<`, `^`, and `؞`.

## Tables

```python
from toolify.tools import print_table

print_table(
    headers=["Name", "Score"],
    rows=[["Ali", 95], ["Sara", 88]],
    style=2,
    separator=True,
)
```

Short rows are padded with empty cells. A row with more values than the header
raises `ValueError`.

## Logging

```python
from toolify.tools import setup_logger

logger = setup_logger(
    base_name="training",
    log_file="logs/training.log",
    to_console=True,
    log_format="full",
)
logger.info("Training started")
```

Toolify adds the current date to the filename and creates the parent directory.
Use `unique=True` when independent loggers need the same base name.

## Confirmation

```python
from toolify.tools import confirm

confirm(data={"files": 10}, message="Start processing? ")
```

The function returns for `y` or `yes`. Other responses raise `SystemExit(0)`.
