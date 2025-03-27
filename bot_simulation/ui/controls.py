"""
Controls module for handling user input and simulation controls.
"""

import pygame
import config

class Controls:
    """Controls for simulation interaction and user input."""
    
    def __init__(self, screen, entity_manager, world_map, simulation):
        """
        Initialize the controls.
        
        Args:
            screen (pygame.Surface): Screen surface to draw on
            entity_manager: Entity manager instance
            world_map: World map instance
            simulation: Simulation instance
        """
        self.screen = screen
        self.entity_manager = entity_manager
        self.world_map = world_map
        self.simulation = simulation
        
        # Initialize fonts
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 16)
        self.small_font = pygame.font.SysFont('Arial', 12)
        
        # Colors
        self.text_color = (255, 255, 255)
        self.button_color = (60, 60, 80)
        self.button_hover_color = (80, 80, 100)
        self.button_active_color = (100, 100, 120)
        self.panel_color = (30, 30, 30, 180)
        
        # Controls panel position and size
        self.panel_rect = pygame.Rect(
            self.screen.get_width() - 260,
            self.screen.get_height() - 200,
            250,
            190
        )
        
        # Buttons
        self.buttons = {
            'start': {
                'rect': pygame.Rect(self.panel_rect.x + 10, self.panel_rect.y + 40, 110, 30),
                'text': 'Start',
                'action': self.toggle_simulation,
                'state': 'normal'
            },
            'reset': {
                'rect': pygame.Rect(self.panel_rect.x + 130, self.panel_rect.y + 40, 110, 30),
                'text': 'Reset',
                'action': self.reset_simulation,
                'state': 'normal'
            },
            'speed_down': {
                'rect': pygame.Rect(self.panel_rect.x + 10, self.panel_rect.y + 80, 50, 30),
                'text': '-',
                'action': lambda: self.change_speed(-0.25),
                'state': 'normal'
            },
            'speed_up': {
                'rect': pygame.Rect(self.panel_rect.x + 190, self.panel_rect.y + 80, 50, 30),
                'text': '+',
                'action': lambda: self.change_speed(0.25),
                'state': 'normal'
            },
            'zoom_out': {
                'rect': pygame.Rect(self.panel_rect.x + 10, self.panel_rect.y + 120, 50, 30),
                'text': '-',
                'action': lambda: self.change_zoom(-0.1),
                'state': 'normal'
            },
            'zoom_in': {
                'rect': pygame.Rect(self.panel_rect.x + 190, self.panel_rect.y + 120, 50, 30),
                'text': '+',
                'action': lambda: self.change_zoom(0.1),
                'state': 'normal'
            },
            'save': {
                'rect': pygame.Rect(self.panel_rect.x + 10, self.panel_rect.y + 160, 110, 30),
                'text': 'Save Data',
                'action': self.save_data,
                'state': 'normal'
            },
            'screenshot': {
                'rect': pygame.Rect(self.panel_rect.x + 130, self.panel_rect.y + 160, 110, 30),
                'text': 'Screenshot',
                'action': self.take_screenshot,
                'state': 'normal'
            }
        }
        
        # Sliders
        self.sliders = {
            'speed': {
                'rect': pygame.Rect(self.panel_rect.x + 70, self.panel_rect.y + 80, 110, 30),
                'value': 1.0,
                'min': 0.25,
                'max': 3.0,
                'dragging': False
            },
            'zoom': {
                'rect': pygame.Rect(self.panel_rect.x + 70, self.panel_rect.y + 120, 110, 30),
                'value': 1.0,
                'min': 0.5,
                'max': 2.0,
                'dragging': False
            }
        }
        
        # Key bindings
        self.key_bindings = {
            pygame.K_SPACE: self.toggle_simulation,
            pygame.K_r: self.reset_simulation,
            pygame.K_EQUALS: lambda: self.change_speed(0.25),
            pygame.K_MINUS: lambda: self.change_speed(-0.25),
            pygame.K_z: lambda: self.change_zoom(0.1),
            pygame.K_x: lambda: self.change_zoom(-0.1),
            pygame.K_s: self.save_data,
            pygame.K_p: self.take_screenshot
        }
        
        # Camera movement
        self.camera_drag = False
        self.camera_drag_start = (0, 0)
        self.camera_drag_origin = (0, 0)
        
    def update(self):
        """Update the controls."""
        # Update button states
        mouse_pos = pygame.mouse.get_pos()
        
        for button_name, button in self.buttons.items():
            if button['rect'].collidepoint(mouse_pos):
                if pygame.mouse.get_pressed()[0]:
                    button['state'] = 'active'
                else:
                    button['state'] = 'hover'
            else:
                button['state'] = 'normal'
                
        # Update slider values based on simulation state
        self.sliders['speed']['value'] = self.simulation.time_scale
        self.sliders['zoom']['value'] = self.world_map.get_zoom()
        
        # Update start/pause button text
        if self.simulation.running:
            self.buttons['start']['text'] = 'Pause'
        else:
            self.buttons['start']['text'] = 'Start'
            
    def draw(self):
        """Draw the controls."""
        # Draw panel background
        panel_surface = pygame.Surface((self.panel_rect.width, self.panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill(self.panel_color)
        self.screen.blit(panel_surface, self.panel_rect)
        
        # Draw title
        title = self.font.render("Simulation Controls", True, self.text_color)
        self.screen.blit(title, (self.panel_rect.x + 10, self.panel_rect.y + 10))
        
        # Draw buttons
        for button_name, button in self.buttons.items():
            # Determine button color based on state
            if button['state'] == 'normal':
                color = self.button_color
            elif button['state'] == 'hover':
                color = self.button_hover_color
            else:  # active
                color = self.button_active_color
                
            # Draw button
            pygame.draw.rect(self.screen, color, button['rect'])
            pygame.draw.rect(self.screen, self.text_color, button['rect'], 1)
            
            # Draw button text
            text = self.font.render(button['text'], True, self.text_color)
            text_rect = text.get_rect(center=button['rect'].center)
            self.screen.blit(text, text_rect)
            
        # Draw sliders
        for slider_name, slider in self.sliders.items():
            # Draw slider track
            pygame.draw.rect(self.screen, self.button_color, slider['rect'])
            pygame.draw.rect(self.screen, self.text_color, slider['rect'], 1)
            
            # Calculate handle position
            value_ratio = (slider['value'] - slider['min']) / (slider['max'] - slider['min'])
            handle_x = slider['rect'].x + value_ratio * slider['rect'].width
            handle_rect = pygame.Rect(handle_x - 5, slider['rect'].y, 10, slider['rect'].height)
            
            # Draw handle
            pygame.draw.rect(self.screen, self.button_hover_color, handle_rect)
            pygame.draw.rect(self.screen, self.text_color, handle_rect, 1)
            
            # Draw value text
            if slider_name == 'speed':
                text = self.small_font.render(f"Speed: {slider['value']:.2f}x", True, self.text_color)
            elif slider_name == 'zoom':
                text = self.small_font.render(f"Zoom: {slider['value']:.2f}x", True, self.text_color)
                
            text_rect = text.get_rect(center=(slider['rect'].centerx, slider['rect'].y - 10))
            self.screen.blit(text, text_rect)
            
    def handle_event(self, event):
        """
        Handle user input events.
        
        Args:
            event (pygame.event.Event): Event to handle
            
        Returns:
            bool: True if event was handled
        """
        # Handle key presses
        if event.type == pygame.KEYDOWN:
            if event.key in self.key_bindings:
                self.key_bindings[event.key]()
                return True
                
        # Handle mouse clicks
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = event.pos
                
                # Check button clicks
                for button_name, button in self.buttons.items():
                    if button['rect'].collidepoint(mouse_pos):
                        button['action']()
                        return True
                        
                # Check slider clicks
                for slider_name, slider in self.sliders.items():
                    if slider['rect'].collidepoint(mouse_pos):
                        slider['dragging'] = True
                        self._update_slider_value(slider_name, mouse_pos[0])
                        return True
                        
                # Check for camera drag
                if (mouse_pos[0] > self.panel_rect.right or mouse_pos[1] < self.panel_rect.top) and \
                   (mouse_pos[0] > 270 or mouse_pos[1] > 380):  # Avoid stats panels
                    self.camera_drag = True
                    self.camera_drag_start = mouse_pos
                    self.camera_drag_origin = self.world_map.get_camera_position()
                    return True
                    
            elif event.button == 4:  # Mouse wheel up
                self.change_zoom(0.1)
                return True
                
            elif event.button == 5:  # Mouse wheel down
                self.change_zoom(-0.1)
                return True
                
        # Handle mouse button releases
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click
                # Stop slider dragging
                for slider_name, slider in self.sliders.items():
                    if slider['dragging']:
                        slider['dragging'] = False
                        return True
                        
                # Stop camera dragging
                if self.camera_drag:
                    self.camera_drag = False
                    return True
                    
        # Handle mouse motion
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            
            # Update sliders if dragging
            for slider_name, slider in self.sliders.items():
                if slider['dragging']:
                    self._update_slider_value(slider_name, mouse_pos[0])
                    return True
                    
            # Update camera if dragging
            if self.camera_drag:
                dx = (self.camera_drag_start[0] - mouse_pos[0]) / self.world_map.get_zoom()
                dy = (self.camera_drag_start[1] - mouse_pos[1]) / self.world_map.get_zoom()
                
                new_x = self.camera_drag_origin[0] + dx
                new_y = self.camera_drag_origin[1] + dy
                
                self.world_map.set_camera_position(new_x, new_y)
                return True
                
        return False
        
    def _update_slider_value(self, slider_name, x_pos):
        """
        Update a slider value based on mouse position.
        
        Args:
            slider_name (str): Name of the slider
            x_pos (int): Mouse x position
        """
        slider = self.sliders[slider_name]
        
        # Calculate value based on position
        value_ratio = (x_pos - slider['rect'].x) / slider['rect'].width
        value_ratio = max(0, min(1, value_ratio))
        
        value = slider['min'] + value_ratio * (slider['max'] - slider['min'])
        
        # Apply value
        if slider_name == 'speed':
            self.simulation.set_time_scale(value)
        elif slider_name == 'zoom':
            self.world_map.set_zoom(value)
            
        # Update slider value
        slider['value'] = value
        
    def toggle_simulation(self):
        """Toggle simulation running state."""
        if self.simulation.running:
            self.simulation.pause()
        else:
            self.simulation.start()
            
    def reset_simulation(self):
        """Reset the simulation."""
        self.simulation.reset()
        
    def change_speed(self, delta):
        """
        Change simulation speed.
        
        Args:
            delta (float): Speed change amount
        """
        current_speed = self.simulation.time_scale
        new_speed = max(self.sliders['speed']['min'], min(self.sliders['speed']['max'], current_speed + delta))
        self.simulation.set_time_scale(new_speed)
        
    def change_zoom(self, delta):
        """
        Change zoom level.
        
        Args:
            delta (float): Zoom change amount
        """
        current_zoom = self.world_map.get_zoom()
        new_zoom = max(self.sliders['zoom']['min'], min(self.sliders['zoom']['max'], current_zoom + delta))
        self.world_map.set_zoom(new_zoom)
        
    def save_data(self):
        """Save simulation data to file."""
        self.simulation.save_data()
        
    def take_screenshot(self):
        """Take a screenshot of the simulation."""
        timestamp = pygame.time.get_ticks()
        filename = f"screenshot_{timestamp}.png"
        pygame.image.save(self.screen, filename)
        print(f"Screenshot saved as {filename}")
        
    def get_panel_rect(self):
        """
        Get the controls panel rectangle.
        
        Returns:
            pygame.Rect: Panel rectangle
        """
        return self.panel_rect
