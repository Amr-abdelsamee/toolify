"""Top-level package for Toolify."""

from importlib import import_module
from importlib.metadata import PackageNotFoundError, version
from types import ModuleType

__all__ = [
    "__version__",
    "tools",
    "plots",
    "ai",
    "audio",
    "youtube",
]

_SUBMODULES = {"tools", "plots", "ai", "audio", "youtube"}

try:
    __version__ = version("toolify")
except PackageNotFoundError:
    __version__ = "0.0.0"


def __getattr__(name: str) -> ModuleType:
    """Load Toolify submodules only when they are first accessed."""
    if name in _SUBMODULES:
        module = import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    """Return attributes available on the package."""
    return sorted(set(globals()) | _SUBMODULES)
