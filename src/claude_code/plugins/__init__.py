"""
Plugins module for Claude Code plugin system.

Provides plugin lifecycle management, registry, and hook system.
"""

from .base import (
    BasePlugin,
    LoadedPlugin,
    PluginAuthor,
    PluginManifest,
    PluginScope,
    PluginSource,
)
from .registry import (
    HookHandler,
    PluginRegistry,
    get_plugin_registry,
    reset_plugin_registry,
)

__all__ = [
    "BasePlugin",
    "HookHandler",
    "LoadedPlugin",
    "PluginAuthor",
    "PluginManifest",
    "PluginRegistry",
    "PluginScope",
    "PluginSource",
    "get_plugin_registry",
    "reset_plugin_registry",
]
