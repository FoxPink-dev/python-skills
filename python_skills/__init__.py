"""Python Skills - Python engineering skills for AI coding agents."""

from importlib.metadata import version as _metadata_version

try:
    __version__ = _metadata_version("python-skills")
except Exception:
    __version__ = "0.0.0"

__all__ = ["__version__"]