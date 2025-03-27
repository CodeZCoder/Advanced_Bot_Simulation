"""
Position component module for storing entity position data.
"""

import pygame
import math

class PositionComponent:
    """
    Stores and manages entity position data.
    """
    
    def __init__(self, x, y):
        """
        Initialize the position component.
        
        Args:
            x (float): Initial x coordinate
            y (float): Initial y coordinate
        """
        self.x = float(x)
        self.y = float(y)
        self.previous_x = self.x  # For interpolation
        self.previous_y = self.y
        
    def get_position(self):
        """
        Get the current position.
        
        Returns:
            tuple: (x, y) position
        """
        return (self.x, self.y)
    
    def set_position(self, x, y):
        """
        Set the position.
        
        Args:
            x (float): New x coordinate
            y (float): New y coordinate
        """
        # Store previous position for interpolation
        self.previous_x = self.x
        self.previous_y = self.y
        
        # Update position
        self.x = float(x)
        self.y = float(y)
        
    def move(self, dx, dy):
        """
        Move the position by a delta.
        
        Args:
            dx (float): Change in x
            dy (float): Change in y
        """
        # Store previous position for interpolation
        self.previous_x = self.x
        self.previous_y = self.y
        
        # Update position
        self.x += float(dx)
        self.y += float(dy)
        
    def distance_to(self, other_position):
        """
        Calculate distance to another position.
        
        Args:
            other_position: Another position component or (x, y) tuple
            
        Returns:
            float: Distance
        """
        if isinstance(other_position, PositionComponent):
            other_x, other_y = other_position.get_position()
        else:
            other_x, other_y = other_position
            
        dx = self.x - other_x
        dy = self.y - other_y
        return math.sqrt(dx * dx + dy * dy)
    
    def direction_to(self, other_position):
        """
        Calculate direction vector to another position.
        
        Args:
            other_position: Another position component or (x, y) tuple
            
        Returns:
            tuple: Normalized direction vector (dx, dy)
        """
        if isinstance(other_position, PositionComponent):
            other_x, other_y = other_position.get_position()
        else:
            other_x, other_y = other_position
            
        dx = other_x - self.x
        dy = other_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            return (dx / distance, dy / distance)
        else:
            return (0, 0)
    
    def angle_to(self, other_position):
        """
        Calculate angle to another position in radians.
        
        Args:
            other_position: Another position component or (x, y) tuple
            
        Returns:
            float: Angle in radians
        """
        if isinstance(other_position, PositionComponent):
            other_x, other_y = other_position.get_position()
        else:
            other_x, other_y = other_position
            
        dx = other_x - self.x
        dy = other_y - self.y
        
        return math.atan2(dy, dx)
    
    def get_interpolated_position(self, alpha):
        """
        Get interpolated position between previous and current position.
        
        Args:
            alpha (float): Interpolation factor (0 to 1)
            
        Returns:
            tuple: Interpolated (x, y) position
        """
        return (
            self.previous_x + (self.x - self.previous_x) * alpha,
            self.previous_y + (self.y - self.previous_y) * alpha
        )
