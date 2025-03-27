"""
Renderable component module for storing entity rendering data.
"""

import pygame
import math
import config

class RenderableComponent:
    """
    Stores data for rendering an entity.
    """
    
    def __init__(self, color=None, radius=10, shape="circle"):
        """
        Initialize the renderable component.
        
        Args:
            color (tuple): RGB color tuple, or None for random color
            radius (float): Radius for circular entities or half-width for rectangular ones
            shape (str): Shape type ("circle", "rectangle", "triangle")
        """
        # Set default color if none provided
        if color is None:
            import random
            self.color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )
        else:
            self.color = color
            
        self.radius = radius
        self.shape = shape
        self.outline_color = None
        self.outline_thickness = 0
        self.alpha = 255  # Transparency (255 = opaque, 0 = transparent)
        self.visible = True
        self.z_index = 0  # For layering (higher = drawn on top)
        self.rotation = 0  # Rotation in radians
        self.scale = 1.0  # Scale multiplier
        self.flash_timer = 0  # For temporary visual effects
        self.flash_color = None
        
    def set_color(self, color):
        """
        Set the color.
        
        Args:
            color (tuple): RGB color tuple
        """
        self.color = color
        
    def get_color(self):
        """
        Get the current color.
        
        Returns:
            tuple: RGB color tuple
        """
        return self.color
    
    def set_radius(self, radius):
        """
        Set the radius.
        
        Args:
            radius (float): New radius
        """
        self.radius = radius
        
    def get_radius(self):
        """
        Get the current radius.
        
        Returns:
            float: Current radius
        """
        return self.radius
    
    def set_shape(self, shape):
        """
        Set the shape.
        
        Args:
            shape (str): Shape type ("circle", "rectangle", "triangle")
        """
        self.shape = shape
        
    def set_outline(self, color, thickness=1):
        """
        Set outline properties.
        
        Args:
            color (tuple): RGB color tuple
            thickness (int): Outline thickness
        """
        self.outline_color = color
        self.outline_thickness = thickness
        
    def set_alpha(self, alpha):
        """
        Set transparency.
        
        Args:
            alpha (int): Alpha value (0-255)
        """
        self.alpha = max(0, min(255, alpha))
        
    def set_visible(self, visible):
        """
        Set visibility.
        
        Args:
            visible (bool): Whether the entity is visible
        """
        self.visible = visible
        
    def set_z_index(self, z_index):
        """
        Set z-index for layering.
        
        Args:
            z_index (int): Z-index value
        """
        self.z_index = z_index
        
    def set_rotation(self, rotation):
        """
        Set rotation.
        
        Args:
            rotation (float): Rotation in radians
        """
        self.rotation = rotation
        
    def set_scale(self, scale):
        """
        Set scale.
        
        Args:
            scale (float): Scale multiplier
        """
        self.scale = max(0.1, scale)  # Prevent negative or zero scale
        
    def flash(self, color, duration=0.5):
        """
        Make the entity flash a color temporarily.
        
        Args:
            color (tuple): RGB color tuple
            duration (float): Flash duration in seconds
        """
        self.flash_color = color
        self.flash_timer = duration
        
    def update(self, delta_time):
        """
        Update visual effects.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Update flash effect
        if self.flash_timer > 0:
            self.flash_timer -= delta_time
            if self.flash_timer <= 0:
                self.flash_color = None
                
    def draw(self, surface, position, camera_rect=None, zoom=1.0):
        """
        Draw the entity.
        
        Args:
            surface (pygame.Surface): Surface to draw on
            position (tuple): (x, y) position
            camera_rect (pygame.Rect, optional): Camera view rectangle
            zoom (float, optional): Zoom factor
        """
        if not self.visible:
            return
            
        # Calculate screen position if camera is provided
        if camera_rect:
            screen_x = (position[0] - camera_rect.x) * zoom
            screen_y = (position[1] - camera_rect.y) * zoom
        else:
            screen_x, screen_y = position
            
        # Apply scale to radius
        scaled_radius = self.radius * self.scale * zoom
        
        # Determine color (use flash color if flashing)
        color = self.flash_color if self.flash_color else self.color
        
        # Create a surface with alpha if needed
        if self.alpha < 255:
            # Create a temporary surface for alpha blending
            temp_surface = pygame.Surface((scaled_radius * 2, scaled_radius * 2), pygame.SRCALPHA)
            temp_surface.fill((0, 0, 0, 0))  # Transparent background
            
            # Draw on the temporary surface
            if self.shape == "circle":
                pygame.draw.circle(temp_surface, (*color, self.alpha), 
                                  (scaled_radius, scaled_radius), scaled_radius)
                if self.outline_color:
                    pygame.draw.circle(temp_surface, (*self.outline_color, self.alpha), 
                                      (scaled_radius, scaled_radius), scaled_radius, 
                                      self.outline_thickness)
            elif self.shape == "rectangle":
                rect = pygame.Rect(0, 0, scaled_radius * 2, scaled_radius * 2)
                pygame.draw.rect(temp_surface, (*color, self.alpha), rect)
                if self.outline_color:
                    pygame.draw.rect(temp_surface, (*self.outline_color, self.alpha), 
                                    rect, self.outline_thickness)
            elif self.shape == "triangle":
                points = [
                    (scaled_radius, 0),
                    (0, scaled_radius * 2),
                    (scaled_radius * 2, scaled_radius * 2)
                ]
                pygame.draw.polygon(temp_surface, (*color, self.alpha), points)
                if self.outline_color:
                    pygame.draw.polygon(temp_surface, (*self.outline_color, self.alpha), 
                                       points, self.outline_thickness)
                                       
            # Rotate if needed
            if self.rotation != 0:
                temp_surface = pygame.transform.rotate(temp_surface, -math.degrees(self.rotation))
                
            # Blit the temporary surface
            surface.blit(temp_surface, (screen_x - temp_surface.get_width() // 2, 
                                      screen_y - temp_surface.get_height() // 2))
        else:
            # Draw directly on the surface
            if self.shape == "circle":
                pygame.draw.circle(surface, color, (screen_x, screen_y), scaled_radius)
                if self.outline_color:
                    pygame.draw.circle(surface, self.outline_color, (screen_x, screen_y), 
                                      scaled_radius, self.outline_thickness)
            elif self.shape == "rectangle":
                rect = pygame.Rect(screen_x - scaled_radius, screen_y - scaled_radius, 
                                  scaled_radius * 2, scaled_radius * 2)
                pygame.draw.rect(surface, color, rect)
                if self.outline_color:
                    pygame.draw.rect(surface, self.outline_color, rect, self.outline_thickness)
            elif self.shape == "triangle":
                # Calculate points based on rotation
                if self.rotation != 0:
                    # Triangle pointing in direction of rotation
                    points = [
                        (screen_x + math.cos(self.rotation) * scaled_radius, 
                         screen_y + math.sin(self.rotation) * scaled_radius),
                        (screen_x + math.cos(self.rotation + 2.3) * scaled_radius, 
                         screen_y + math.sin(self.rotation + 2.3) * scaled_radius),
                        (screen_x + math.cos(self.rotation - 2.3) * scaled_radius, 
                         screen_y + math.sin(self.rotation - 2.3) * scaled_radius)
                    ]
                else:
                    # Default upward-pointing triangle
                    points = [
                        (screen_x, screen_y - scaled_radius),
                        (screen_x - scaled_radius, screen_y + scaled_radius),
                        (screen_x + scaled_radius, screen_y + scaled_radius)
                    ]
                pygame.draw.polygon(surface, color, points)
                if self.outline_color:
                    pygame.draw.polygon(surface, self.outline_color, points, self.outline_thickness)
