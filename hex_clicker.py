"""
Hex Grid Tool - Main application module
A tool for creating and manipulating hex grids for game prototyping.
"""
import sys
import math
import pygame
import pygame_gui

from constants import (
    DEFAULT_COLS, DEFAULT_ROWS, DEFAULT_RADIUS, DEFAULT_BORDER,
    DEFAULT_ORIENTATION, DEFAULT_TERRAIN_TYPES, PANEL_WIDTH, 
    MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT, BACKGROUND_COLOR
)
from hex import Hex
from grid import HexGrid
from ui import UIManager


class HexApp:
    """Main application class for the Hex Grid Tool."""
    
    def __init__(self):
        """Initialize the hex grid application."""
        pygame.init()
        pygame.display.set_caption("Hex Grid Tool")
        
        # Initialize grid parameters
        self.cols = DEFAULT_COLS
        self.rows = DEFAULT_ROWS
        self.radius = DEFAULT_RADIUS
        self.border = DEFAULT_BORDER
        self.orientation = DEFAULT_ORIENTATION
        
        # Initialize terrain types
        self.terrain_types = DEFAULT_TERRAIN_TYPES.copy()
        
        # Initialize UI state
        self.selected_hex = None
        
        # Calculate window dimensions and create display
        self._recalc_window_size()
        self.window = pygame.display.set_mode(
            (self.win_w, self.win_h), pygame.RESIZABLE
        )
        self.ui_mgr = pygame_gui.UIManager((self.win_w, self.win_h))
        
        # Create UI manager
        self.ui_manager = UIManager((self.win_w, self.win_h), self.ui_mgr)
        
        # Create hex grid
        self.grid = HexGrid(
            self.cols, self.rows, self.radius, self.border, 
            self.orientation, self.terrain_types
        )
        
        # Set up UI panels
        self._create_panels()
        
        # Initialize clock for frame timing
        self.clock = pygame.time.Clock()

    def _recalc_window_size(self):
        """Calculate the window size based on grid dimensions."""
        sqrt3 = math.sqrt(3)
        margin = 50
        
        if self.orientation == "Flat":
            width = self.radius * 3/2 * self.cols + self.radius/2
            height = self.radius * sqrt3 * (self.rows + 0.5)
        else:  # Pointy
            width = self.radius * sqrt3 * (self.cols + 0.5)
            height = self.radius * 3/2 * self.rows + self.radius/2
        
        # Add space for panels on the right - minimum width for panel area
        grid_width = int(width + margin)
        panel_width = PANEL_WIDTH + 20  # Add some margin
        
        # Total window width includes both grid and panel areas
        self.win_w = max(grid_width + panel_width, MIN_WINDOW_WIDTH)
        self.win_h = int(max(height + margin, MIN_WINDOW_HEIGHT))
        
        # Calculate panel position (right side of window)
        self.panel_x = self.win_w - PANEL_WIDTH - 10

    def _create_panels(self):
        """Create all UI panels and controls."""
        # Pack current settings into a dict for UI creation
        settings = {
            'cols': self.cols,
            'rows': self.rows,
            'radius': self.radius,
            'border': self.border,
            'orientation': self.orientation
        }
        
        # Create settings panel
        self.ui_manager.create_settings_panel(
            settings, 
            self.panel_x,
            self._on_slider_changed,
            self._on_orientation_changed
        )
        
        # Create terrain panel
        self.ui_manager.create_terrain_panel(
            self.panel_x, 
            self.terrain_types,
            self._on_color_button,
            self._on_randomize_all
        )

    def _on_slider_changed(self, key, value):
        """Handle slider value changes."""
        setattr(self, key, int(value))
        self._update_grid()
    
    def _on_orientation_changed(self, new_orientation):
        """Handle orientation dropdown changes."""
        self.orientation = new_orientation
        self._update_grid()
    
    def _on_color_button(self, terrain_index):
        """Handle color button clicks."""
        terrain_color = self.terrain_types[terrain_index]["color"]
        self.ui_manager.open_color_picker(terrain_index, terrain_color)
    
    def _on_randomize_all(self):
        """Handle randomize all button click."""
        self.grid.randomize_all_terrains()
    
    def _update_grid(self):
        """Update the grid with new parameters."""
        # Recalculate window dimensions
        self._recalc_window_size()
        
        # Resize the window
        self.window = pygame.display.set_mode(
            (self.win_w, self.win_h), pygame.RESIZABLE
        )
        self.ui_mgr.set_window_resolution((self.win_w, self.win_h))
        
        # Update panel positions
        self.ui_manager.update_panel_positions(self.panel_x)
        
        # Update the grid
        self.grid.rebuild_grid(
            self.cols, self.rows, self.radius, 
            self.border, self.orientation
        )

    def find_hex_by_coords(self, col, row):
        """Find a hex by its column and row coordinates."""
        for hex_obj in self.grid.hexes:
            if hex_obj.col == col and hex_obj.row == row:
                return hex_obj
        return None
    
    def handle_hex_click(self, pos, right_click=False):
        """Handle mouse click on a hex."""
        # Ignore if UI is active
        if (self.ui_manager.color_picker_active or 
            self.ui_manager.terrain_menu_active):
            return
            
        hex_obj = self.grid.find_hex_at_position(pos)
        if hex_obj:
            if right_click:
                # Right click - open terrain type dropdown
                self.ui_manager.open_terrain_menu(
                    hex_obj, pos, self.terrain_types
                )
                # Store reference to selected hex coordinates
                self.ui_manager.selected_hex_coords = (hex_obj.col, hex_obj.row)
            else:
                # Left click - randomize terrain
                hex_obj.randomize_terrain(len(self.terrain_types))
                # Store reference to selected hex
                self.grid.selected_hex = hex_obj
    
    def run(self):
        """Main application loop."""
        while True:
            dt = self.clock.tick(60)/1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.VIDEORESIZE:
                    self.window = pygame.display.set_mode(
                        (event.w, event.h), pygame.RESIZABLE
                    )
                    self.ui_mgr.set_window_resolution((event.w, event.h))
                    
                    # Recalculate panel positions
                    self.panel_x = event.w - PANEL_WIDTH - 10
                    self.ui_manager.update_panel_positions(self.panel_x)
                
                # Handle mouse clicks for hex interaction
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Process mouse clicks only if no menus are active
                    if not self.ui_manager.color_picker_active and not self.ui_manager.terrain_menu_active:
                        if event.button == 1:  # Left click
                            self.handle_hex_click(event.pos)
                        elif event.button == 3:  # Right click
                            self.handle_hex_click(event.pos, right_click=True)

                # UI event processing
                self.ui_mgr.process_events(event)

                # Handle slider movement
                if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    for key, slider in self.ui_manager.sliders.items():
                        if event.ui_element == slider:
                            self._on_slider_changed(key, event.value)
                            break
                
                # Handle orientation dropdown change
                if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if (self.ui_manager.orientation_dropdown and 
                        event.ui_element == self.ui_manager.orientation_dropdown):
                        self._on_orientation_changed(event.text)
                    elif (self.ui_manager.terrain_menu_active and 
                          hasattr(self.ui_manager, 'terrain_menu') and 
                          event.ui_element == self.ui_manager.terrain_menu):
                        # Terrain type selection for a hex
                        new_terrain_name = event.text
                        
                        # Find the hex by stored coordinates
                        selected_hex = None
                        if hasattr(self.ui_manager, 'selected_hex_coords'):
                            col, row = self.ui_manager.selected_hex_coords
                            selected_hex = self.find_hex_by_coords(col, row)
                        
                        # Find the terrain index by name
                        for i, terrain in enumerate(self.terrain_types):
                            if terrain["name"] == new_terrain_name:
                                # Update the hex's terrain_index
                                if selected_hex:
                                    selected_hex.terrain_index = i
                                    # Also update the selected hex in the grid
                                    self.grid.selected_hex = selected_hex
                                break
                                
                        # Close and destroy the menu
                        if hasattr(self.ui_manager, 'terrain_menu') and self.ui_manager.terrain_menu:
                            self.ui_manager.terrain_menu.kill()
                            self.ui_manager.terrain_menu = None
                        self.ui_manager.terrain_menu_active = False
                
                # Handle button clicks
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    action, data = self.ui_manager.process_button_event(event)
                    
                    if action == 'toggle_settings':
                        self.ui_manager.toggle_settings_visibility()
                    elif action == 'toggle_terrain':
                        self.ui_manager.toggle_terrain_panel_visibility()
                    elif action == 'hide_settings':
                        self.ui_manager.panel.hide()
                        self.ui_manager.settings_visible = False
                    elif action == 'hide_terrain':
                        self.ui_manager.terrain_panel.hide()
                        self.ui_manager.terrain_panel_visible = False
                    elif action == 'color_button':
                        self._on_color_button(data)
                    elif action == 'randomize_all':
                        self._on_randomize_all()
                
                # Handle color picker confirmation
                if (event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED and 
                    self.ui_manager.color_picker_active):
                    if self.ui_manager.color_picker_terrain_index is not None:
                        # Update terrain type color
                        r, g, b = event.colour.r, event.colour.g, event.colour.b
                        self.terrain_types[self.ui_manager.color_picker_terrain_index]["color"] = (r, g, b)
                    self.ui_manager.color_picker_active = False
                    self.ui_manager.color_picker_terrain_index = None
                
                # Handle window/dialog close events
                if event.type == pygame_gui.UI_WINDOW_CLOSE:
                    if (self.ui_manager.color_picker_active and 
                        hasattr(self.ui_manager, 'color_picker') and 
                        event.ui_element == self.ui_manager.color_picker):
                        self.ui_manager.color_picker_active = False
                        self.ui_manager.color_picker_terrain_index = None
                
                # If terrain menu is active and we clicked elsewhere, close it
                if event.type == pygame.MOUSEBUTTONDOWN and self.ui_manager.terrain_menu_active:
                    # Check if click is outside the menu
                    if hasattr(self.ui_manager, 'terrain_menu') and self.ui_manager.terrain_menu:
                        # Check if mouse is outside the menu
                        menu_rect = self.ui_manager.terrain_menu.get_relative_rect()
                        mouse_x, mouse_y = event.pos
                        if not menu_rect.collidepoint(mouse_x, mouse_y):
                            self.ui_manager.terrain_menu.kill()
                            self.ui_manager.terrain_menu = None
                            self.ui_manager.terrain_menu_active = False

            # Update UI
            self.ui_mgr.update(dt)
            
            # Draw everything
            self._draw()
            pygame.display.flip()

    def _draw(self):
        """Draw the application."""
        # Clear the screen
        self.window.fill(BACKGROUND_COLOR)
        
        # Draw the hex grid
        self.grid.draw(self.window)
        
        # Draw UI on top
        self.ui_mgr.draw_ui(self.window)


if __name__ == "__main__":
    HexApp().run()
