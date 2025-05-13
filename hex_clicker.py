import sys, math, random
import pygame
import pygame_gui

# ─── DEFAULT SETTINGS ─────────────────────────────────────────────────────────
DEFAULT_COLS   = 10
DEFAULT_ROWS   =  8
DEFAULT_RADIUS = 40
DEFAULT_BORDER =  4
DEFAULT_ORIENTATION = "Flat"  # "Flat" or "Pointy"

# ─── HEX CELL ─────────────────────────────────────────────────────────────
class Hex:
    def __init__(self, col, row, size, color, border=0, orientation="Flat"):
        self.col = col
        self.row = row
        self.size = size
        self.color = color
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
        """Get the vertices of a hexagon with given size."""
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
    
    def draw(self, surface):
        """Draw the hexagon."""
        # Get outer and inner vertices
        outer_vertices = self.get_vertices(self.size)
        
        # Draw filled hex
        if self.border > 0:
            inner_size = max(0, self.size - self.border)
            inner_vertices = self.get_vertices(inner_size)
            pygame.draw.polygon(surface, self.color, inner_vertices)
            pygame.draw.polygon(surface, (0, 0, 0), outer_vertices, width=1)
        else:
            pygame.draw.polygon(surface, self.color, outer_vertices)
            pygame.draw.polygon(surface, (0, 0, 0), outer_vertices, width=1)

# ─── GRID BUILDER ────────────────────────────────────────────────────────────
def create_hex_grid(cols, rows, size, border, orientation):
    """Create a grid of hexagons using simple offset coordinates."""
    grid = []
    
    for col in range(cols):
        for row in range(rows):
            # Random color
            color = (
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255)
            )
            
            # Create hex
            hex = Hex(col, row, size, color, border, orientation)
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

        self._recalc_window_size()
        self.window = pygame.display.set_mode(
            (self.win_w, self.win_h), pygame.RESIZABLE
        )
        self.ui_mgr = pygame_gui.UIManager((self.win_w, self.win_h))

        # Single settings panel
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
        
        self.clock = pygame.time.Clock()
        self.hexes = create_hex_grid(
            self.cols, self.rows, self.radius, self.border, self.orientation
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

                # UI event processing
                self.ui_mgr.process_events(ev)

                # Handle slider movement
                if ev.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    for key,slider in self.sliders.items():
                        if ev.ui_element == slider:
                            setattr(self, key, int(ev.value))
                            # rebuild grid and window on any param change
                            self._recalc_window_size()
                            self.hexes = create_hex_grid(
                                self.cols, self.rows, self.radius, 
                                self.border, self.orientation
                            )
                            break
                
                # Handle orientation dropdown change
                if ev.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if ev.ui_element == self.orientation_dropdown:
                        self.orientation = ev.text
                        # rebuild grid with new orientation
                        self._recalc_window_size()
                        self.hexes = create_hex_grid(
                            self.cols, self.rows, self.radius,
                            self.border, self.orientation
                        )

            self.ui_mgr.update(dt)
            self._draw()
            pygame.display.flip()

    def _draw(self):
        self.window.fill((30,30,30))
        # Draw all hexes
        for hex in self.hexes:
            hex.draw(self.window)
        # Draw UI over top
        self.ui_mgr.draw_ui(self.window)

if __name__ == "__main__":
    HexMVP().run()
