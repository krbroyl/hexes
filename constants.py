"""
Constants used throughout the hex grid application.
"""

# Default settings for the grid
DEFAULT_COLS = 10
DEFAULT_ROWS = 8
DEFAULT_RADIUS = 40
DEFAULT_BORDER = 4
DEFAULT_ORIENTATION = "Flat"  # "Flat" or "Pointy"

# Default terrain types with names and colors
DEFAULT_TERRAIN_TYPES = [
    {"name": "Plains", "color": (210, 230, 115)},
    {"name": "Desert", "color": (237, 201, 175)},
    {"name": "Forest", "color": (76, 166, 107)},
    {"name": "Water", "color": (118, 182, 237)},
    {"name": "Mountains", "color": (166, 162, 140)},
    {"name": "Hills", "color": (148, 196, 139)},
    {"name": "Swamp", "color": (76, 128, 107)}
]

# UI settings
PANEL_WIDTH = 300
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 620
BACKGROUND_COLOR = (30, 30, 30)