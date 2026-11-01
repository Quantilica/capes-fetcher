"""Coletor e conversor Lake Hive de dados da pós-graduação e teses da CAPES."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("capes-fetcher")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["__version__"]
