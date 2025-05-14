"""
Module for managing UI components of the hex grid application.
"""
import pygame
import pygame_gui
from typing import Dict, List, Tuple, Callable, Optional

from constants import PANEL_WIDTH


class UIManager:
    """Manager for all UI components in the application."""
    
    def __init__(self, window_size: Tuple[int, int], ui_manager: pygame_gui.UIManager):
        """Initialize UI manager with window dimensions and pygame_gui manager."""
        self.win_w, self.win_h = window_size
        self.ui_mgr = ui_manager
        
        # Panel visibility state
        self.settings_visible = True
        self.terrain_panel_visible = True
        
        # UI element references
        self.panel = None
        self.terrain_panel = None
        self.toggle_settings_button = None
        self.toggle_terrain_button = None
        self.hide_settings_button = None
        self.hide_terrain_button = None
        self.orientation_dropdown = None
        self.sliders = {}
        self.terrain_buttons = []
        self.randomize_all_button = None
        
        # UI state for interaction
        self.terrain_menu_active = False
        self.terrain_menu = None
        self.color_picker_active = False
        self.color_picker = None
        self.color_picker_terrain_index = None
        
        # Create UI components
        self._create_control_buttons()
    
    def _create_control_buttons(self):
        """Create the main control buttons for toggling panels."""
        # Button to toggle settings visibility
        self.toggle_settings_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 10), (30, 30)),
            text="☰",  # Hamburger menu icon
            manager=self.ui_mgr
        )
        
        # Button to toggle terrain panel visibility
        self.toggle_terrain_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 50), (30, 30)),
            text="🎨",  # Palette icon
            manager=self.ui_mgr
        )
    
    def create_settings_panel(self, settings: Dict, panel_x: int, 
                             slider_changed_callback: Callable,
                             orientation_changed_callback: Callable):
        """Create the settings panel with all controls."""
        # Main settings panel
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((panel_x, 10), (PANEL_WIDTH, 240)),
            manager=self.ui_mgr
        )

        # Add "Hide" button to main panel
        self.hide_settings_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((PANEL_WIDTH - 50, 5), (40, 20)),
            text="Hide",
            manager=self.ui_mgr,
            container=self.panel
        )

        # Sliders for cols, rows, radius, border
        self.sliders = {}
        specs = [
            ('cols', 'Columns', (1, 50)),
            ('rows', 'Rows', (1, 50)),
            ('radius', 'Hex Radius', (5, 150)),
            ('border', 'Border Thick', (0, 50))
        ]
        y = 35  # Start a bit lower to make room for hide button
        for key, label, vr in specs:
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((20, y), (100, 25)),
                text=label,
                manager=self.ui_mgr,
                container=self.panel
            )
            slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect((130, y), (150, 25)),
                start_value=settings[key],
                value_range=vr,
                manager=self.ui_mgr,
                container=self.panel
            )
            self.sliders[key] = slider
            y += 40
        
        # Orientation dropdown
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, y), (100, 25)),
            text='Orientation',
            manager=self.ui_mgr,
            container=self.panel
        )
        self.orientation_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=["Flat", "Pointy"],
            starting_option=settings['orientation'],
            relative_rect=pygame.Rect((130, y), (150, 25)),
            manager=self.ui_mgr,
            container=self.panel
        )
    
    def create_terrain_panel(self, panel_x: int, terrain_types: List[Dict], 
                            color_button_callback: Callable,
                            randomize_callback: Callable):
        """Create the terrain settings panel."""
        # Terrain Settings Panel - position below the main panel
        self.terrain_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((panel_x, 260), (PANEL_WIDTH, 350)),
            manager=self.ui_mgr
        )
        
        # Add "Hide" button to terrain panel
        self.hide_terrain_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((PANEL_WIDTH - 50, 5), (40, 20)),
            text="Hide",
            manager=self.ui_mgr,
            container=self.terrain_panel
        )
        
        # Terrain settings title
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (220, 25)),
            text='Terrain Settings',
            manager=self.ui_mgr,
            container=self.terrain_panel
        )
        
        # Terrain color buttons
        self.terrain_buttons = []
        y_pos = 40
        for i, terrain in enumerate(terrain_types):
            # Label with terrain name
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((20, y_pos), (120, 25)),
                text=terrain["name"],
                manager=self.ui_mgr,
                container=self.terrain_panel
            )
            
            # Color button
            color_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((150, y_pos), (120, 25)),
                text='Change Color',
                manager=self.ui_mgr,
                container=self.terrain_panel,
                object_id=f'terrain_color_{i}'
            )
            self.terrain_buttons.append(color_button)
            y_pos += 40
        
        # Button to randomize all terrains
        self.randomize_all_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, y_pos), (260, 30)),
            text='Randomize All Terrains',
            manager=self.ui_mgr,
            container=self.terrain_panel
        )
    
    def toggle_settings_visibility(self):
        """Toggle the visibility of just the settings panel."""
        if hasattr(self, 'panel') and self.panel:
            self.settings_visible = not self.settings_visible
            
            if self.settings_visible:
                self.panel.show()
            else:
                self.panel.hide()
    
    def toggle_terrain_panel_visibility(self):
        """Toggle the visibility of just the terrain panel."""
        if hasattr(self, 'terrain_panel') and self.terrain_panel:
            self.terrain_panel_visible = not self.terrain_panel_visible
            
            if self.terrain_panel_visible:
                self.terrain_panel.show()
            else:
                self.terrain_panel.hide()
    
    def update_panel_positions(self, panel_x: int):
        """Update the positions of all panels."""
        if self.panel:
            self.panel.set_position((panel_x, 10))
        
        if self.terrain_panel:
            self.terrain_panel.set_position((panel_x, 260))
    
    def open_color_picker(self, terrain_index: int, terrain_color: Tuple[int, int, int]):
        """Open a color picker for the specified terrain type."""
        if self.color_picker_active:
            return  # Prevent opening multiple color pickers
        
        # Store the terrain index
        self.color_picker_terrain_index = terrain_index
        self.color_picker_active = True
        
        # Create color picker dialog
        rect = pygame.Rect(0, 0, 400, 400)  # Size to avoid warning
        rect.center = (self.win_w // 2, self.win_h // 2)
        
        # Convert terrain color to pygame.Color object
        color_obj = pygame.Color(terrain_color[0], terrain_color[1], terrain_color[2])
        
        self.color_picker = pygame_gui.windows.UIColourPickerDialog(
            rect=rect,
            manager=self.ui_mgr,
            initial_colour=color_obj
        )
    
    def open_terrain_menu(self, hex_obj, pos: Tuple[int, int], terrain_types: List[Dict]):
        """Open a terrain type selection menu for the given hex."""
        if self.terrain_menu_active:
            # If there's an active menu, destroy it first
            if hasattr(self, 'terrain_menu') and self.terrain_menu:
                self.terrain_menu.kill()
            self.terrain_menu = None
        
        # Store active state and hexagon coordinates (not the reference)
        self.terrain_menu_active = True
        self.selected_hex_coords = (hex_obj.col, hex_obj.row)  # Store coordinates instead of reference
        
        # Get terrain type names
        options = [terrain["name"] for terrain in terrain_types]
        
        # Create dropdown menu
        terrain_menu_width = 150
        terrain_menu_height = 30
        
        # Position menu near the mouse but ensure it's on screen
        menu_x = min(pos[0], self.win_w - terrain_menu_width - 10)
        menu_y = min(pos[1], self.win_h - len(options) * 30 - 10)
        
        try:
            self.terrain_menu = pygame_gui.elements.UIDropDownMenu(
                options_list=options,
                starting_option=terrain_types[hex_obj.terrain_index]["name"],
                relative_rect=pygame.Rect(menu_x, menu_y, terrain_menu_width, terrain_menu_height),
                manager=self.ui_mgr
            )
        except Exception as e:
            print(f"Error creating terrain menu: {e}")
            self.terrain_menu_active = False
    
    def process_button_event(self, event: pygame.event.Event) -> Tuple[str, Optional[int]]:
        """
        Process a UI button event and return the action to take.
        
        Returns:
            A tuple of (action_type, optional_data) where action_type is one of:
            'toggle_settings', 'toggle_terrain', 'hide_settings', 'hide_terrain',
            'color_button', 'randomize_all', or None if no recognized action.
            
            optional_data contains the terrain index for color_button actions.
        """
        if event.ui_element == self.toggle_settings_button:
            return 'toggle_settings', None
        elif event.ui_element == self.toggle_terrain_button:
            return 'toggle_terrain', None
        elif self.hide_settings_button and event.ui_element == self.hide_settings_button:
            return 'hide_settings', None
        elif self.hide_terrain_button and event.ui_element == self.hide_terrain_button:
            return 'hide_terrain', None
        elif self.randomize_all_button and event.ui_element == self.randomize_all_button:
            return 'randomize_all', None
            
        # Check if it's a terrain color button
        for i, button in enumerate(self.terrain_buttons):
            if event.ui_element == button:
                return 'color_button', i
        
        return None, None