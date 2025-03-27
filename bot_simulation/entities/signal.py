"""
Signal entity module for defining communication signal entities.
"""

import pygame
import math
import time
import config

class Signal:
    """
    Signal entity that represents communication between bots.
    """
    
    def __init__(self, position, signal_type, data, sender, range_value):
        """
        Initialize a signal entity.
        
        Args:
            position (tuple): (x, y) position
            signal_type (int): Type of signal
            data: Signal data
            sender: Entity sending the signal
            range_value (float): Signal range
        """
        self.position = position
        self.signal_type = signal_type
        self.data = data
        self.sender = sender
        self.range = range_value
        self.creation_time = time.time()
        self.lifetime = config.SIGNAL_LIFETIME
        self.current_radius = 0
        self.expansion_speed = range_value / (config.SIGNAL_LIFETIME * 0.5)  # Expand to full range in half lifetime
        self.alpha = 255  # Transparency
        
        # Set color based on signal type
        self.color = self._get_color_for_type()
        
    def _get_color_for_type(self):
        """
        Get color based on signal type.
        
        Returns:
            tuple: RGBA color
        """
        if self.signal_type == 1:  # Danger
            return (255, 50, 50, self.alpha)
        elif self.signal_type == 2:  # Food
            return (50, 255, 50, self.alpha)
        elif self.signal_type == 3:  # Mate
            return (50, 50, 255, self.alpha)
        else:
            return (200, 200, 200, self.alpha)
            
    def update(self, delta_time):
        """
        Update signal state.
        
        Args:
            delta_time (float): Time delta in seconds
            
        Returns:
            bool: True if signal is still active
        """
        # Update age
        age = time.time() - self.creation_time
        
        # Check if expired
        if age >= self.lifetime:
            return False
            
        # Update radius (expand outward)
        if age < self.lifetime * 0.5:
            # Expanding phase
            self.current_radius = min(self.range, age * self.expansion_speed)
        else:
            # Keep at max radius
            self.current_radius = self.range
            
        # Update transparency (fade out)
        fade_start = self.lifetime * 0.5
        if age > fade_start:
            fade_progress = (age - fade_start) / (self.lifetime - fade_start)
            self.alpha = int(255 * (1 - fade_progress))
            
        # Update color with new alpha
        self.color = self.color[:3] + (self.alpha,)
        
        return True
    
    def get_position(self):
        """
        Get the signal position.
        
        Returns:
            tuple: (x, y) position
        """
        return self.position
    
    def get_type(self):
        """
        Get the signal type.
        
        Returns:
            int: Signal type
        """
        return self.signal_type
    
    def get_data(self):
        """
        Get the signal data.
        
        Returns:
            Signal data
        """
        return self.data
    
    def get_sender(self):
        """
        Get the signal sender.
        
        Returns:
            Entity that sent the signal
        """
        return self.sender
    
    def get_range(self):
        """
        Get the signal range.
        
        Returns:
            float: Signal range
        """
        return self.range
    
    def get_current_radius(self):
        """
        Get the current signal radius.
        
        Returns:
            float: Current radius
        """
        return self.current_radius
    
    def is_signal(self):
        """
        Check if this entity is a signal.
        
        Returns:
            bool: Always True for signals
        """
        return True
    
    def draw(self, surface, camera_rect, zoom=1.0):
        """
        Draw the signal.
        
        Args:
            surface (pygame.Surface): Surface to draw on
            camera_rect (pygame.Rect): Camera view rectangle
            zoom (float): Zoom factor
        """
        # Calculate screen position
        screen_x = (self.position[0] - camera_rect.x) * zoom
        screen_y = (self.position[1] - camera_rect.y) * zoom
        
        # Apply zoom to radius
        scaled_radius = self.current_radius * zoom
        
        # Create a surface for the signal with transparency
        signal_surface = pygame.Surface((scaled_radius * 2, scaled_radius * 2), pygame.SRCALPHA)
        
        # Draw expanding circle with transparency
        pygame.draw.circle(signal_surface, self.color, (scaled_radius, scaled_radius), scaled_radius)
        
        # Draw a thin border
        border_color = self.color[:3] + (min(255, self.alpha + 50),)
        pygame.draw.circle(signal_surface, border_color, (scaled_radius, scaled_radius), scaled_radius, 2)
        
        # Draw a small dot at the center
        center_color = self.color[:3] + (min(255, self.alpha + 100),)
        pygame.draw.circle(signal_surface, center_color, (scaled_radius, scaled_radius), 3)
        
        # Blit the signal surface onto the main surface
        surface.blit(signal_surface, (screen_x - scaled_radius, screen_y - scaled_radius))
        
    def is_in_range(self, position):
        """
        Check if a position is within the signal's current radius.
        
        Args:
            position (tuple): (x, y) position to check
            
        Returns:
            bool: True if position is in range
        """
        dx = self.position[0] - position[0]
        dy = self.position[1] - position[1]
        distance_squared = dx * dx + dy * dy
        
        return distance_squared <= self.current_radius * self.current_radius
