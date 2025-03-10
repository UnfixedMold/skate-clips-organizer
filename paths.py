import os
import sys

def resource_path(relative_path):
    """Return absolute path to resource, works for development & PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

if hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


ICON_DIR = resource_path("icons")
ICON_PNG = resource_path(os.path.join("icons", "hvx.png"))
ICON_ICO = resource_path(os.path.join("icons", "hvx.ico"))
SORT_VALUES = resource_path("sort_config.json")
