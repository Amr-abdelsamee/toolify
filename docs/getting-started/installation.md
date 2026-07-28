# Installation

## From PyPI

Install the latest stable release:

```bash
pip install toolify
```

Toolify requires Python 3.11 or newer. The package dependencies are installed
automatically from its package metadata.

## FFmpeg

FFmpeg is required only when YouTube downloads need to merge separate video
and audio streams. Install it with your operating system's package manager and
ensure the `ffmpeg` command is available on `PATH`.

## From source

For development, clone the repository and install it in editable mode:

```bash
git clone https://github.com/Amr-abdelsamee/toolify.git
cd toolify
pip install -e ".[dev,docs]"
```

Run the offline tests:

```bash
python -m pytest -m "not integration"
```
