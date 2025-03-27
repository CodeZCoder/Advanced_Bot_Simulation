"""
Resource entity module for defining resource entities.
"""

import pygame
import random
import math
import config

class Resource:
    """
    Resource entity that can be consumed by bots for energy.
    """
    
    def __init__(self, position, energy=None):
        """
        Initialize a resource entity.
        
        Args:
            position (tuple): (x, y) position
            energy (float, optional): Energy value, random if None
        """
        self.position = position
        self.energy = energy if energy is not None else random.uniform(
            config.RESOURCE_ENERGY_MIN, 
            config.RESOURCE_ENERGY_MAX
        )
        self.radius = config.RESOURCE_RADIUS
        self.color = self._calculate_color()
        self.creation_time = pygame.time.get_ticks()
        self.pulse_rate = random.uniform(0.5, 2.0)  # Visual effect rate
        self.pulse_offset = random.uniform(0, math.pi * 2)  # Random phase
        
    def _calculate_color(self):
        """
        Calculate color based on energy value.
        
        Returns:
            tuple: RGB color
        """
        # Higher energy = more vibrant green
        energy_ratio = (self.energy - config.RESOURCE_ENERGY_MIN) / (
            config.RESOURCE_ENERGY_MAX - config.RESOURCE_ENERGY_MIN
        )
        
        # Green with varying intensity
        green = 100 + int(155 * energy_ratio)
        
        return (30, green, 30)
    
    def update(self, delta_time):
        """
        Update resource state.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Resources are mostly static, but could have visual effects
        pass
    
    def get_position(self):
        """
        Get the resource position.
        
        Returns:
            tuple: (x, y) position
        """
        return self.position
    
    def get_energy(self):
        """
        Get the resource energy value.
        
        Returns:
            float: Energy value
        """
        return self.energy
    
    def get_radius(self):
        """
        Get the resource radius.
        
        Returns:
            float: Radius
        """
        return self.radius
    
    def is_resource(self):
        """
        Check if this entity is a resource.
        
        Returns:
            bool: Always True for resources
        """
        return True
    
    def draw(self, surface, camera_rect, zoom=1.0):
        """
        Draw the resource.
        
        Args:
            surface (pygame.Surface): Surface to draw on
            camera_rect (pygame.Rect): Camera view rectangle
            zoom (float): Zoom factor
        """
        # Calculate screen position
        screen_x = (self.position[0] - camera_rect.x) * zoom
        screen_y = (self.position[1] - camera_rect.y) * zoom
        
        # Apply zoom to radius
        scaled_radius = self.radius * zoom
        
        # Calculate pulse effect (subtle size variation)
        current_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
        pulse = math.sin(current_time * self.pulse_rate + self.pulse_offset) * 0.2 + 1.0
        pulse_radius = scaled_radius * pulse
        
        # Draw resource
        pygame.draw.circle(surface, self.color, (screen_x, screen_y), pulse_radius)
        
        # Draw outline
        pygame.draw.circle(surface, (255, 255, 255, 100), (screen_x, screen_y), pulse_radius, 1)
        
    def collides_with_circle(self, center, radius):
        """
        Check if this resource collides with a circle.
        
        Args:
            center (tuple): Circle center (x, y)
            radius (float): Circle radius
            
        Returns:
            bool: True if collision detected
        """
        dx = self.position[0] - center[0]
        dy = self.position[1] - center[1]
        distance_squared = dx * dx + dy * dy
        
        return distance_squared <= (self.radius + radius) ** 2
