"""
Obstacle entity module for defining obstacle entities.
"""

import pygame
import random
import config

class Obstacle:
    """
    Obstacle entity that blocks movement and creates barriers in the world.
    """
    
    def __init__(self, rect, color=None):
        """
        Initialize an obstacle entity.
        
        Args:
            rect (pygame.Rect): Rectangle defining the obstacle bounds
            color (tuple, optional): RGB color, random if None
        """
        self.rect = rect
        self.color = color if color is not None else (
            random.randint(50, 100),
            random.randint(50, 100),
            random.randint(50, 100)
        )
        self.border_color = (
            min(255, self.color[0] + 30),
            min(255, self.color[1] + 30),
            min(255, self.color[2] + 30)
        )
        self.creation_time = pygame.time.get_ticks()
        
    def update(self, delta_time):
        """
        Update obstacle state.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Obstacles are static, no update needed
        pass
    
    def get_rect(self):
        """
        Get the obstacle rectangle.
        
        Returns:
            pygame.Rect: Obstacle rectangle
        """
        return self.rect
    
    def get_position(self):
        """
        Get the obstacle center position.
        
        Returns:
            tuple: (x, y) position
        """
        return (self.rect.centerx, self.rect.centery)
    
    def is_obstacle(self):
        """
        Check if this entity is an obstacle.
        
        Returns:
            bool: Always True for obstacles
        """
        return True
    
    def draw(self, surface, camera_rect, zoom=1.0):
        """
        Draw the obstacle.
        
        Args:
            surface (pygame.Surface): Surface to draw on
            camera_rect (pygame.Rect): Camera view rectangle
            zoom (float): Zoom factor
        """
        # Calculate screen rectangle
        screen_rect = pygame.Rect(
            (self.rect.x - camera_rect.x) * zoom,
            (self.rect.y - camera_rect.y) * zoom,
            self.rect.width * zoom,
            self.rect.height * zoom
        )
        
        # Draw obstacle
        pygame.draw.rect(surface, self.color, screen_rect)
        
        # Draw border
        pygame.draw.rect(surface, self.border_color, screen_rect, 2)
        
    def collides_with_circle(self, center, radius):
        """
        Check if this obstacle collides with a circle.
        
        Args:
            center (tuple): Circle center (x, y)
            radius (float): Circle radius
            
        Returns:
            bool: True if collision detected
        """
        # Find the closest point on the rectangle to the circle center
        closest_x = max(self.rect.left, min(center[0], self.rect.right))
        closest_y = max(self.rect.top, min(center[1], self.rect.bottom))
        
        # Calculate distance between the closest point and circle center
        dx = closest_x - center[0]
        dy = closest_y - center[1]
        distance_squared = dx * dx + dy * dy
        
        return distance_squared <= radius * radius
    
    def collides_with_rect(self, rect):
        """
        Check if this obstacle collides with a rectangle.
        
        Args:
            rect (pygame.Rect): Rectangle to check collision with
            
        Returns:
            bool: True if collision detected
        """
        return self.rect.colliderect(rect)
