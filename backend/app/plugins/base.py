"""
Base plugin interface and utilities for Semantic Kernel plugins.

This module defines the base plugin class and common utilities
for creating Semantic Kernel compatible plugins.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.functions.kernel_function_metadata import KernelFunctionMetadata


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    name: str
    description: str
    version: str = "1.0.0"
    author: Optional[str] = None
    functions: List[str] = None

    def __post_init__(self):
        if self.functions is None:
            self.functions = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "functions": self.functions
        }


class BasePlugin(ABC):
    """
    Base class for all Semantic Kernel plugins.

    Plugins inherit from this class and use the @kernel_function decorator
    to expose functions to the kernel.
    """

    @classmethod
    @abstractmethod
    def get_metadata(cls) -> PluginMetadata:
        """
        Get plugin metadata.

        Returns:
            PluginMetadata instance describing the plugin
        """
        pass

    @classmethod
    def get_functions(cls) -> List[KernelFunctionMetadata]:
        """
        Get all kernel functions from this plugin.

        Returns:
            List of KernelFunctionMetadata
        """
        functions = []
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if hasattr(attr, '__kernel_function__'):
                functions.append(attr.__kernel_function__)
        return functions


class PluginRegistry:
    """
    Registry for managing available plugins.

    Provides discovery and registration of plugins.
    """

    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._metadata: Dict[str, PluginMetadata] = {}

    def register(self, plugin: BasePlugin) -> None:
        """
        Register a plugin.

        Args:
            plugin: Plugin instance to register

        Raises:
            ValueError: If a plugin with the same name is already registered
        """
        metadata = plugin.get_metadata()
        if metadata.name in self._plugins:
            raise ValueError(f"Plugin '{metadata.name}' is already registered")

        self._plugins[metadata.name] = plugin
        self._metadata[metadata.name] = metadata

    def unregister(self, name: str) -> None:
        """
        Unregister a plugin.

        Args:
            name: Name of the plugin to unregister
        """
        self._plugins.pop(name, None)
        self._metadata.pop(name, None)

    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """
        Get a registered plugin by name.

        Args:
            name: Name of the plugin

        Returns:
            Plugin instance or None if not found
        """
        return self._plugins.get(name)

    def get_metadata(self, name: str) -> Optional[PluginMetadata]:
        """
        Get metadata for a registered plugin.

        Args:
            name: Name of the plugin

        Returns:
            PluginMetadata or None if not found
        """
        return self._metadata.get(name)

    def list_plugins(self) -> List[PluginMetadata]:
        """
        List all registered plugins.

        Returns:
            List of PluginMetadata for all registered plugins
        """
        return list(self._metadata.values())

    def get_all_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata for all registered plugins.

        Returns:
            Dictionary mapping plugin names to their metadata dictionaries
        """
        return {
            name: metadata.to_dict()
            for name, metadata in self._metadata.items()
        }


# Global plugin registry
_registry: Optional[PluginRegistry] = None


def get_plugin_registry() -> PluginRegistry:
    """
    Get the global plugin registry.

    Returns:
        PluginRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
    return _registry


def reset_plugin_registry() -> None:
    """Reset the global plugin registry (useful for testing)."""
    global _registry
    _registry = None
