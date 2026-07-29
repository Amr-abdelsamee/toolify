<h1>
  <img
    src="docs/assets/images/toolify-logo.png"
    alt="Toolify logo"
    width="84"
    align="absmiddle"
  >
  Toolify
</h1>

[![PyPI](https://img.shields.io/pypi/v/toolify)](https://pypi.org/project/toolify/)
[![Python](https://img.shields.io/pypi/pyversions/toolify)](https://pypi.org/project/toolify/)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://amr-abdelsamee.github.io/toolify/)
[![License](https://img.shields.io/pypi/l/toolify)](https://github.com/Amr-abdelsamee/toolify/blob/main/LICENSE)

Toolify is a Python utility library for terminal output, Arabic text handling,
logging, plotting, audio inspection, Hugging Face downloads, and YouTube media
downloads.

## Features

| Module | Purpose |
| --- | --- |
| `toolify.tools` | Colored output, Arabic text, tables, logging, and confirmation |
| `toolify.plots` | Line-plot generation |
| `toolify.audio` | Silence detection, spectrograms, and duration helpers |
| `toolify.ai` | Hugging Face repository inspection and downloads |
| `toolify.youtube` | YouTube video, transcript, and playlist utilities |

## Installation

Install the latest release from PyPI:

```bash
pip install toolify
```

Python 3.11 or newer is required. FFmpeg is also required when YouTube video
and audio streams need to be merged.

### Install FFmpeg

FFmpeg is a system application, not a Python package.

#### Windows

Install it from PowerShell with Windows Package Manager:

```powershell
winget install --exact --id Gyan.FFmpeg
```

Close and reopen the terminal after installation. If `winget` is unavailable,
download a Windows build from the
[official FFmpeg download page](https://ffmpeg.org/download.html), extract it,
and add its `bin` directory to the Windows `PATH`.

#### Linux

Ubuntu, Debian, and Linux Mint:

```bash
sudo apt update
sudo apt install ffmpeg
```


Verify the installation on either operating system:

```bash
ffmpeg -version
```


## Documentation

The complete guides and API reference are available in the
[Toolify documentation](https://amr-abdelsamee.github.io/toolify/).

- [Installation](https://amr-abdelsamee.github.io/toolify/getting-started/installation/)
- [Quick start](https://amr-abdelsamee.github.io/toolify/getting-started/quickstart/)
- [User guides](https://amr-abdelsamee.github.io/toolify/guides/tools/)
- [API reference](https://amr-abdelsamee.github.io/toolify/reference/tools/)
- [Changelog](https://github.com/Amr-abdelsamee/toolify/blob/main/CHANGELOG.md)

## Development

```bash
git clone https://github.com/Amr-abdelsamee/toolify.git
cd toolify
pip install -e ".[dev,docs]"
python -m pytest -m "not integration"
mkdocs serve
```

See the [contributing guide](https://amr-abdelsamee.github.io/toolify/development/contributing/)
and [release guide](https://amr-abdelsamee.github.io/toolify/development/releasing/).

## License

Toolify is licensed under the
[MIT License](https://github.com/Amr-abdelsamee/toolify/blob/main/LICENSE).
