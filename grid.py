"""
Module for managing the hex grid as a whole.
"""
import random
from typing import List, Dict, Tuple, Optional

from hex import Hex


def create_hex_grid(cols: int, rows: int, size: int, border: int, 
                   orientation: str, num_terrain_types: int, 
                   existing_hexes: Optional[List[Hex]] = None) -> List[Hex]:
    """
    Create a grid of hexagons using simple offset coordinates.
    
    If existing_hexes is provided, it will try to preserve the terrain of hexes
    that already exist at the same positions.
    """
    grid = []
    
    # Create a lookup of existing hex terrains by position (col, row)
    existing_terrains = {}
    if existing_hexes:
        for hex_obj in existing_hexes:
            existing_terrains[(hex_obj.col, hex_obj.row)] = hex_obj.terrain_index
    
    for col in range(cols):
        for row in range(rows):
            # Check if this position already had a hex
            if (col, row) in existing_terrains:
                # Preserve the terrain from the existing hex
                terrain_index = existing_terrains[(col, row)]
            else:
                # Only new hexes get random terrain
                terrain_index = random.randint(0, num_terrain_types - 1)
            
            # Create hex
            hex_obj = Hex(col, row, size, terrain_index, border, orientation)
            grid.append(hex_obj)
    
    return grid


class HexGrid:
    """Manager class for a collection of hexes forming a grid."""
    
    def __init__(self, cols: int, rows: int, size: int, border: int,
                orientation: str, terrain_types: List[Dict]):
        """Initialize a new hex grid with the given parameters."""
        self.cols = cols
        self.rows = rows
        self.size = size
        self.border = border
        self.orientation = orientation
        self.terrain_types = terrain_types
        self.selected_hex = None
        
        # Create initial grid
        self.hexes = create_hex_grid(
            self.cols, self.rows, self.size, self.border,
            self.orientation, len(self.terrain_types)
        )
    
    def rebuild_grid(self, new_cols: int = None, new_rows: int = None, 
                    new_size: int = None, new_border: int = None, 
                    new_orientation: str = None) -> None:
        """
        Rebuild the grid with new parameters while preserving terrain types.
        Only parameters that are provided will be updated.
        """
        # Update parameters with new values if provided
        if new_cols is not None:
            self.cols = new_cols
        if new_rows is not None:
            self.rows = new_rows
        if new_size is not None:
            self.size = new_size
        if new_border is not None:
            self.border = new_border
        if new_orientation is not None:
            self.orientation = new_orientation
            
        # Rebuild grid with updated parameters
        self.hexes = create_hex_grid(
            self.cols, self.rows, self.size, self.border,
            self.orientation, len(self.terrain_types), existing_hexes=self.hexes
        )

    def find_hex_at_position(self, pos: Tuple[int, int]) -> Optional[Hex]:
        """Find the hex at the given screen position."""
        for hex_obj in self.hexes:
            if hex_obj.contains_point(pos):
                return hex_obj
        return None
    
    def randomize_all_terrains(self) -> None:
        """Randomize the terrain of all hexes in the grid."""
        for hex_obj in self.hexes:
            hex_obj.randomize_terrain(len(self.terrain_types))
    
    def draw(self, surface) -> None:
        """Draw all hexes in the grid."""
        for hex_obj in self.hexes:
            hex_obj.draw(surface, self.terrain_types)
            
            # Highlight selected hex
            if hex_obj == self.selected_hex:
                # Draw a highlight around the selected hex
                highlight_vertices = hex_obj.get_vertices(hex_obj.size + 2)
                pygame.draw.polygon(surface, (255, 255, 255), highlight_vertices, width=2)


# Add import at the end to avoid circular import
import pygame