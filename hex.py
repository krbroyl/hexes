"""
Module for hex grid functionality and geometric calculations.
"""
import math
from typing import Tuple, List

import pygame


def point_in_polygon(point: Tuple[int, int], vertices: List[Tuple[int, int]]) -> bool:
    """Check if a point is inside a polygon using ray casting algorithm."""
    x, y = point
    n = len(vertices)
    inside = False
    
    p1x, p1y = vertices[0]
    for i in range(1, n + 1):
        p2x, p2y = vertices[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside


class Hex:
    """A single hexagonal cell in the grid."""
    
    def __init__(self, col: int, row: int, size: int, terrain_index: int, 
                 border: int = 0, orientation: str = "Flat"):
        """Initialize a hex cell with position and visual properties."""
        self.col = col
        self.row = row
        self.size = size
        self.terrain_index = terrain_index  # Index into the terrain types list
        self.border = border
        self.orientation = orientation
        
        # Calculate center coordinates
        self._calculate_center()
    
    def _calculate_center(self) -> None:
        """Calculate the center coordinates of the hex based on grid position."""
        if self.orientation == "Flat":
            # For flat-top hexes
            self.center_x = self.size * 3/2 * self.col + self.size + 10
            self.center_y = (self.size * math.sqrt(3) * 
                           (self.row + 0.5 * (self.col % 2)) + self.size + 10)
        else:
            # For pointy-top hexes
            self.center_x = (self.size * math.sqrt(3) * 
                           (self.col + 0.5 * (self.row % 2)) + self.size + 10)
            self.center_y = self.size * 3/2 * self.row + self.size + 10
    
    def get_vertices(self, size: int) -> List[Tuple[int, int]]:
        """Get the vertex coordinates of a hexagon with given size."""
        vertices = []
        for i in range(6):
            if self.orientation == "Flat":
                angle = math.pi / 3 * i
                # Starting at 0 degrees for flat-top
                x = self.center_x + size * math.cos(angle)
                y = self.center_y + size * math.sin(angle)
            else:
                angle = math.pi / 3 * i + math.pi / 6
                # Starting at 30 degrees for pointy-top
                x = self.center_x + size * math.cos(angle)
                y = self.center_y + size * math.sin(angle)
            vertices.append((int(x), int(y)))
        return vertices
    
    def draw(self, surface: pygame.Surface, terrain_types: List[dict]) -> None:
        """Draw the hexagon with the terrain color."""
        # Get outer and inner vertices
        outer_vertices = self.get_vertices(self.size)
        
        # Get terrain color
        terrain_color = terrain_types[self.terrain_index]["color"]
        
        # Draw filled hex
        if self.border > 0:
            inner_size = max(0, self.size - self.border)
            inner_vertices = self.get_vertices(inner_size)
            pygame.draw.polygon(surface, terrain_color, inner_vertices)
            pygame.draw.polygon(surface, (0, 0, 0), outer_vertices, width=1)
        else:
            pygame.draw.polygon(surface, terrain_color, outer_vertices)
            pygame.draw.polygon(surface, (0, 0, 0), outer_vertices, width=1)
    
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if the point is inside the hexagon."""
        # Use the vertices and collision detection
        vertices = self.get_vertices(self.size)
        return (pygame.Rect(
            self.center_x - self.size, 
            self.center_y - self.size,
            self.size * 2, 
            self.size * 2
        ).collidepoint(point) and point_in_polygon(point, vertices))
    
    def randomize_terrain(self, num_terrain_types: int) -> None:
        """Randomize the terrain index of this hex."""
        import random  # Import here to avoid circular import
        self.terrain_index = random.randint(0, num_terrain_types - 1)