"""
Fake Plugin for testing plugin discovery

This is a minimal plugin that implements the Plugin interface
to test if Broca2 can discover and load plugins automatically.
"""

from .plugin import FakePlugin

__all__ = ["FakePlugin"]
