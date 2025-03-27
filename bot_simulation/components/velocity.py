"""
Velocity component module for storing entity velocity data.
"""

import math

class VelocityComponent:
    """
    Stores and manages entity velocity data.
    """
    
    def __init__(self, dx=0, dy=0, max_speed=0):
        """
        Initialize the velocity component.
        
        Args:
            dx (float): Initial x velocity
            dy (float): Initial y velocity
            max_speed (float): Maximum speed
        """
        self.dx = float(dx)
        self.dy = float(dy)
        self.max_speed = float(max_speed)
        self.acceleration = 0.0
        self.friction = 0.1  # Slows down movement over time
        self.rotation = 0.0  # Direction in radians
        
    def get_velocity(self):
        """
        Get the current velocity vector.
        
        Returns:
            tuple: (dx, dy) velocity
        """
        return (self.dx, self.dy)
    
    def set_velocity(self, dx, dy):
        """
        Set the velocity vector, respecting max speed.
        
        Args:
            dx (float): New x velocity
            dy (float): New y velocity
        """
        self.dx = float(dx)
        self.dy = float(dy)
        self._clamp_to_max_speed()
        
    def accelerate(self, amount, direction=None):
        """
        Accelerate in the current direction or a specified direction.
        
        Args:
            amount (float): Acceleration amount
            direction (float, optional): Direction in radians, or None to use current rotation
        """
        if direction is not None:
            self.rotation = direction
            
        # Calculate acceleration vector
        accel_x = amount * math.cos(self.rotation)
        accel_y = amount * math.sin(self.rotation)
        
        # Apply acceleration
        self.dx += accel_x
        self.dy += accel_y
        
        # Clamp to max speed
        self._clamp_to_max_speed()
        
    def accelerate_towards(self, target_position, amount, position_component):
        """
        Accelerate towards a target position.
        
        Args:
            target_position: Target position (tuple or PositionComponent)
            amount (float): Acceleration amount
            position_component: This entity's position component
        """
        # Calculate direction to target
        if hasattr(target_position, 'get_position'):
            target_x, target_y = target_position.get_position()
        else:
            target_x, target_y = target_position
            
        current_x, current_y = position_component.get_position()
        
        dx = target_x - current_x
        dy = target_y - current_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Normalize direction
            dx /= distance
            dy /= distance
            
            # Update rotation
            self.rotation = math.atan2(dy, dx)
            
            # Apply acceleration
            self.dx += dx * amount
            self.dy += dy * amount
            
            # Clamp to max speed
            self._clamp_to_max_speed()
            
    def apply_friction(self):
        """
        Apply friction to slow down movement.
        """
        if abs(self.dx) > 0 or abs(self.dy) > 0:
            speed = math.sqrt(self.dx * self.dx + self.dy * self.dy)
            
            if speed > 0:
                friction_amount = min(speed, self.friction)
                friction_factor = 1.0 - (friction_amount / speed)
                
                self.dx *= friction_factor
                self.dy *= friction_factor
                
                # Stop completely if very slow
                if abs(self.dx) < 0.01:
                    self.dx = 0
                if abs(self.dy) < 0.01:
                    self.dy = 0
                    
    def get_speed(self):
        """
        Get the current speed (magnitude of velocity).
        
        Returns:
            float: Current speed
        """
        return math.sqrt(self.dx * self.dx + self.dy * self.dy)
    
    def set_max_speed(self, max_speed):
        """
        Set the maximum speed.
        
        Args:
            max_speed (float): New maximum speed
        """
        self.max_speed = float(max_speed)
        self._clamp_to_max_speed()
        
    def get_direction(self):
        """
        Get the current movement direction in radians.
        
        Returns:
            float: Direction in radians
        """
        if self.dx == 0 and self.dy == 0:
            return self.rotation
        else:
            return math.atan2(self.dy, self.dx)
        
    def set_direction(self, radians):
        """
        Set the rotation direction.
        
        Args:
            radians (float): Direction in radians
        """
        self.rotation = radians
        
    def _clamp_to_max_speed(self):
        """
        Clamp velocity to maximum speed.
        """
        if self.max_speed > 0:
            speed = math.sqrt(self.dx * self.dx + self.dy * self.dy)
            
            if speed > self.max_speed:
                factor = self.max_speed / speed
                self.dx *= factor
                self.dy *= factor
