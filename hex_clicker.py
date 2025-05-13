import sys, math, random
import pygame
import pygame_gui

# ─── DEFAULT SETTINGS ─────────────────────────────────────────────────────────
DEFAULT_COLS   = 10
DEFAULT_ROWS   =  8
DEFAULT_RADIUS = 40
DEFAULT_BORDER =  4
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

# ─── HEX CELL ─────────────────────────────────────────────────────────────
class Hex:
    def __init__(self, col, row, size, terrain_index, border=0, orientation="Flat"):
        self.col = col
        self.row = row
        self.size = size
        self.terrain_index = terrain_index  # Index into the terrain types list
        self.border = border
        self.orientation = orientation
        
        # Calculate center coordinates
        if orientation == "Flat":
            # For flat-top hexes
            self.center_x = size * 3/2 * col + size + 10
            self.center_y = size * math.sqrt(3) * (row + 0.5 * (col % 2)) + size + 10
        else:
            # For pointy-top hexes
            self.center_x = size * math.sqrt(3) * (col + 0.5 * (row % 2)) + size + 10
            self.center_y = size * 3/2 * row + size + 10
    
    def get_vertices(self, size):
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
    
    def draw(self, surface, terrain_types):
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
    
    def contains_point(self, point):
        """Check if the point is inside the hexagon."""
        # Use the vertices and pygame's collision detection
        vertices = self.get_vertices(self.size)
        return pygame.Rect(
            self.center_x - self.size, 
            self.center_y - self.size,
            self.size * 2, 
            self.size * 2
        ).collidepoint(point) and point_in_polygon(point, vertices)
    
    def randomize_terrain(self, num_terrain_types):
        """Randomize the terrain index of this hex."""
        self.terrain_index = random.randint(0, num_terrain_types - 1)

# ─── UTILITY FUNCTIONS ─────────────────────────────────────────────────────────
def point_in_polygon(point, vertices):
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

# ─── GRID BUILDER ────────────────────────────────────────────────────────────
def create_hex_grid(cols, rows, size, border, orientation, num_terrain_types, existing_hexes=None):
    """Create a grid of hexagons using simple offset coordinates.
    
    If existing_hexes is provided, it will try to preserve the terrain of hexes
    that already exist at the same positions.
    """
    grid = []
    
    # Create a lookup of existing hex terrains by position (col, row)
    existing_terrains = {}
    if existing_hexes:
        for hex in existing_hexes:
            existing_terrains[(hex.col, hex.row)] = hex.terrain_index
    
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
            hex = Hex(col, row, size, terrain_index, border, orientation)
            grid.append(hex)
    
    return grid

# ─── MAIN MVP APP ─────────────────────────────────────────────────────────────
class HexMVP:
    PANEL_WIDTH = 300

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Hex Grid Tool")
        self.cols = DEFAULT_COLS
        self.rows = DEFAULT_ROWS
        self.radius = DEFAULT_RADIUS
        self.border = DEFAULT_BORDER
        self.orientation = DEFAULT_ORIENTATION
        
        # Initialize terrain types
        self.terrain_types = DEFAULT_TERRAIN_TYPES.copy()
        
        # For handling hex interaction
        self.selected_hex = None
        self.terrain_menu_active = False
        self.terrain_menu_pos = (0, 0)
        self.color_picker_active = False
        self.color_picker_terrain_index = None

        self._recalc_window_size()
        self.window = pygame.display.set_mode(
            (self.win_w, self.win_h), pygame.RESIZABLE
        )
        self.ui_mgr = pygame_gui.UIManager((self.win_w, self.win_h))

        # Main settings panel
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((10,10),(self.PANEL_WIDTH,240)),
            manager=self.ui_mgr
        )

        # Sliders for cols, rows, radius, border
        self.sliders = {}
        specs = [
            ('cols',   'Columns',      (1,50)),
            ('rows',   'Rows',         (1,50)),
            ('radius','Hex Radius',    (5,150)),
            ('border','Border Thick',  (0,50))
        ]
        y = 20
        for key,label,vr in specs:
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((20,y),(100,25)),
                text=label,
                manager=self.ui_mgr,
                container=self.panel
            )
            slider = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect((130,y),(150,25)),
                start_value=getattr(self, key),
                value_range=vr,
                manager=self.ui_mgr,
                container=self.panel
            )
            self.sliders[key] = slider
            y += 40
        
        # Orientation dropdown
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20,y),(100,25)),
            text='Orientation',
            manager=self.ui_mgr,
            container=self.panel
        )
        self.orientation_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=["Flat", "Pointy"],
            starting_option=self.orientation,
            relative_rect=pygame.Rect((130,y),(150,25)),
            manager=self.ui_mgr,
            container=self.panel
        )
        
        # Terrain Settings Panel
        self.terrain_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((10,260),(self.PANEL_WIDTH,350)),
            manager=self.ui_mgr
        )
        
        # Terrain settings title
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10,10),(280,25)),
            text='Terrain Settings',
            manager=self.ui_mgr,
            container=self.terrain_panel
        )
        
        # Terrain color buttons
        self.terrain_buttons = []
        y_pos = 40
        for i, terrain in enumerate(self.terrain_types):
            # Label with terrain name
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((20,y_pos),(120,25)),
                text=terrain["name"],
                manager=self.ui_mgr,
                container=self.terrain_panel
            )
            
            # Color button
            color_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((150,y_pos),(120,25)),
                text='Change Color',
                manager=self.ui_mgr,
                container=self.terrain_panel,
                object_id=f'terrain_color_{i}'
            )
            self.terrain_buttons.append(color_button)
            y_pos += 40
        
        # Button to randomize all terrains
        self.randomize_all_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20,y_pos),(260,30)),
            text='Randomize All Terrains',
            manager=self.ui_mgr,
            container=self.terrain_panel
        )
        
        self.clock = pygame.time.Clock()
        
        # Initial grid creation - this is the only time we do full random terrains
        self.hexes = create_hex_grid(
            self.cols, self.rows, self.radius, self.border, 
            self.orientation, len(self.terrain_types)
        )

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
            
        self.win_w = int(width + self.PANEL_WIDTH + margin)
        self.win_h = int(height + margin)
        self.win_h = max(self.win_h, 300)  # Minimum height

    def find_hex_at_position(self, pos):
        """Find the hex at the given screen position."""
        for hex in self.hexes:
            if hex.contains_point(pos):
                return hex
        return None
    
    def handle_hex_click(self, pos, right_click=False):
        """Handle mouse click on a hex."""
        # If color picker or terrain menu is active, don't process clicks on hexes
        if self.color_picker_active or self.terrain_menu_active:
            return
            
        hex = self.find_hex_at_position(pos)
        if hex:
            if right_click:
                # Right click - open terrain type dropdown
                self.open_terrain_menu(hex, pos)
            else:
                # Left click - randomize terrain
                hex.randomize_terrain(len(self.terrain_types))
            
            # Set as selected hex
            self.selected_hex = hex
    
    def open_terrain_menu(self, hex, pos):
        """Open a terrain type selection menu for the given hex."""
        if self.terrain_menu_active:
            return  # Prevent opening multiple menus
        
        # Store the hex and position
        self.selected_hex = hex
        self.terrain_menu_active = True
        self.terrain_menu_pos = pos
        
        # Get terrain type names
        options = [terrain["name"] for terrain in self.terrain_types]
        
        # Create dropdown menu
        terrain_menu_width = 150
        terrain_menu_height = 30
        
        # Position menu near the mouse but ensure it's on screen
        menu_x = min(pos[0], self.win_w - terrain_menu_width - 10)
        menu_y = min(pos[1], self.win_h - len(options) * 30 - 10)
        
        self.terrain_menu = pygame_gui.elements.UIDropDownMenu(
            options_list=options,
            starting_option=self.terrain_types[hex.terrain_index]["name"],
            relative_rect=pygame.Rect(menu_x, menu_y, terrain_menu_width, terrain_menu_height),
            manager=self.ui_mgr
        )
    
    def open_color_picker(self, terrain_index):
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
        terrain_color = self.terrain_types[terrain_index]["color"]
        color_obj = pygame.Color(terrain_color[0], terrain_color[1], terrain_color[2])
        
        self.color_picker = pygame_gui.windows.UIColourPickerDialog(
            rect=rect,
            manager=self.ui_mgr,
            initial_colour=color_obj
        )
    
    def randomize_all_terrains(self):
        """Randomize the terrain of all hexes."""
        for hex in self.hexes:
            hex.randomize_terrain(len(self.terrain_types))

    def run(self):
        while True:
            dt = self.clock.tick(60)/1000.0
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if ev.type == pygame.VIDEORESIZE:
                    self.window = pygame.display.set_mode(
                        (ev.w, ev.h), pygame.RESIZABLE
                    )
                    self.ui_mgr.set_window_resolution((ev.w, ev.h))
                
                # Handle mouse clicks for hex interaction
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    # Process mouse clicks only if no menus are active
                    if not self.color_picker_active and not self.terrain_menu_active:
                        if ev.button == 1:  # Left click
                            self.handle_hex_click(ev.pos)
                        elif ev.button == 3:  # Right click
                            self.handle_hex_click(ev.pos, right_click=True)

                # UI event processing
                self.ui_mgr.process_events(ev)

                # Handle slider movement
                if ev.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    for key,slider in self.sliders.items():
                        if ev.ui_element == slider:
                            setattr(self, key, int(ev.value))
                            # rebuild grid and window on any param change
                            # but preserve existing hex terrains
                            self._recalc_window_size()
                            self.hexes = create_hex_grid(
                                self.cols, self.rows, self.radius, 
                                self.border, self.orientation,
                                len(self.terrain_types),
                                existing_hexes=self.hexes  # Pass existing hexes to preserve terrains
                            )
                            break
                
                # Handle orientation dropdown change
                if ev.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if ev.ui_element == self.orientation_dropdown:
                        self.orientation = ev.text
                        # rebuild grid with new orientation
                        # but preserve existing hex terrains
                        self._recalc_window_size()
                        self.hexes = create_hex_grid(
                            self.cols, self.rows, self.radius,
                            self.border, self.orientation,
                            len(self.terrain_types),
                            existing_hexes=self.hexes  # Pass existing hexes to preserve terrains
                        )
                    elif ev.ui_element == self.terrain_menu and self.selected_hex:
                        # Terrain type selection for a hex
                        new_terrain_name = ev.text
                        # Find the terrain index by name
                        for i, terrain in enumerate(self.terrain_types):
                            if terrain["name"] == new_terrain_name:
                                self.selected_hex.terrain_index = i
                                break
                        # Close the menu
                        self.terrain_menu_active = False
                
                # Handle button clicks
                if ev.type == pygame_gui.UI_BUTTON_PRESSED:
                    # Check if it's a terrain color button
                    for i, button in enumerate(self.terrain_buttons):
                        if ev.ui_element == button:
                            self.open_color_picker(i)
                            break
                    
                    # Check if it's the randomize all button
                    if ev.ui_element == self.randomize_all_button:
                        self.randomize_all_terrains()
                
                # Handle color picker confirmation
                if ev.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED and self.color_picker_active:
                    if self.color_picker_terrain_index is not None:
                        # Update terrain type color
                        r, g, b = ev.colour.r, ev.colour.g, ev.colour.b
                        self.terrain_types[self.color_picker_terrain_index]["color"] = (r, g, b)
                    self.color_picker_active = False
                    self.color_picker_terrain_index = None
                
                # Handle window/dialog close events
                if ev.type == pygame_gui.UI_WINDOW_CLOSE:
                    if self.color_picker_active and hasattr(self, 'color_picker') and ev.ui_element == self.color_picker:
                        self.color_picker_active = False
                        self.color_picker_terrain_index = None
                
                # If terrain menu is active and we clicked elsewhere, close it
                if ev.type == pygame.MOUSEBUTTONDOWN and self.terrain_menu_active:
                    # Check if click is outside the menu
                    if hasattr(self, 'terrain_menu') and not self.terrain_menu.hover_point(ev.pos):
                        # If menu is far from click, close it
                        menu_rect = self.terrain_menu.get_relative_rect()
                        if (abs(menu_rect.x - ev.pos[0]) > 50 or 
                            abs(menu_rect.y - ev.pos[1]) > 50):
                            self.terrain_menu_active = False

            self.ui_mgr.update(dt)
            self._draw()
            pygame.display.flip()

    def _draw(self):
        self.window.fill((30,30,30))
        # Draw all hexes
        for hex in self.hexes:
            hex.draw(self.window, self.terrain_types)
            
            # Highlight selected hex
            if hex == self.selected_hex:
                # Draw a highlight around the selected hex
                highlight_vertices = hex.get_vertices(hex.size + 2)
                pygame.draw.polygon(self.window, (255, 255, 255), highlight_vertices, width=2)
        
        # Draw UI over top
        self.ui_mgr.draw_ui(self.window)

if __name__ == "__main__":
    HexMVP().run()
