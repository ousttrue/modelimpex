__all__ = [
    "register",
    "unregister",
]
from .humanoidio import register, unregister

bl_info = {
    "name": "humanoidio",
    "blender": (4, 1, 0),
    "category": "Import-Export",
    "support": "COMMUNITY",
}

if "humanoidio" in locals():
    import importlib
    import sys

    tmp = {k: v for k, v in sys.modules.items()}
    for k, m in tmp.items():
        if k.startswith("humanoidio."):
            # print(f"reimport: {k}")
            importlib.reload(m)
