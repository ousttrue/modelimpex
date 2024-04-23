bl_info = {
    "name": "humanoidio",
    "blender": (4, 1, 0),
    "category": "Import-Export",
}

__all__ = [
    "bl_info",
    "register",
    "unregister",
]

if "humanoidio" in locals():
    import importlib
    import sys

    tmp = {k: v for k, v in sys.modules.items()}
    for k, m in tmp.items():
        if k.startswith("humanoidio."):
            importlib.reload(m)

from .humanoidio import register, unregister, bl_info as bl_info
