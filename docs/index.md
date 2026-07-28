# Toolify

Toolify is a collection of practical Python utilities for terminal output,
Arabic text, plotting, audio inspection, Hugging Face repositories, and
YouTube media.

## Modules

| Module | What it provides |
| --- | --- |
| `toolify.tools` | Colored output, Arabic display, tables, logging, and confirmation |
| `toolify.plots` | Line-plot generation |
| `toolify.audio` | Silence detection, spectrograms, and duration helpers |
| `toolify.ai` | Hugging Face size inspection and repository downloads |
| `toolify.youtube` | Video downloads, transcripts, and playlist inspection |

## Install

```bash
pip install toolify
```

Toolify requires Python 3.11 or newer. YouTube downloads that combine separate
video and audio streams also require FFmpeg.

## First example

```python
from toolify.tools import pct, strip_tashkeel

pct("Toolify is ready", color="green", emoji="success")
print(strip_tashkeel("مُحَمَّدٌ"))
```

Continue with the [installation guide](getting-started/installation.md) or the
[quick start](getting-started/quickstart.md).
