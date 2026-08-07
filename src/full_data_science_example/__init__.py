"""Top-level package for Full Data Science Example."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("full-data-science-example")
except PackageNotFoundError:
    __version__ = "0+unknown"

__all__ = ["__version__"]
