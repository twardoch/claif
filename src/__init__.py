""""""

import sys
from importlib import metadata
from typing import Any

__version__ = metadata.version(__name__)

# Enable package-style imports for plugins
__path__ = []
__package__ = "claif"


class PluginFinder:
    """Finder for claif plugins to enable package-style imports."""

    @classmethod
    def find_spec(cls, fullname, path, target=None):
        if not fullname.startswith("claif."):
            return None

        plugin_name = fullname.split(".")[-1]
        try:
            eps = metadata.entry_points(group="claif.plugins")
            for ep in eps:
                if ep.name == plugin_name:
                    # Create a spec that will load the plugin module
                    from importlib.machinery import ModuleSpec

                    plugin_module = ep.load()

                    class Loader:
                        @staticmethod
                        def create_module(spec):
                            return plugin_module

                        @staticmethod
                        def exec_module(module):
                            pass

                    return ModuleSpec(fullname, Loader())
        except Exception:
            return None
        return None


# Register the finder
sys.meta_path.insert(0, PluginFinder())


def __getattr__(name: str) -> Any:
    """Dynamic attribute lookup for plugins.

    To register a plugin, add the following to your pyproject.toml:

    [project.entry-points."claif.plugins"]
    plugin_name = "plugin_module"  # Just point to the module

    Args:
        name: Name of plugin to load

    Returns:
        Loaded plugin module

    Raises:
        AttributeError: If plugin cannot be found or loaded
    """
    try:
        eps = metadata.entry_points(group="claif.plugins")
        for ep in eps:
            if ep.name == name:
                return ep.load()
    except Exception as e:
        msg = f"Failed to load plugin '{name}': {e}"
        raise AttributeError(msg) from e

    msg = f"module '{__name__}' has no attribute '{name}'"
    raise AttributeError(msg)
