"""
Clock module for managing time and frame rate in the simulation.
"""

import pygame
import time

class Clock:
    """
    Manages time, frame rate, and provides utilities for frame rate independence.
    """
    
    def __init__(self, target_fps):
        """
        Initialize the clock.
        
        Args:
            target_fps (int): Target frames per second
        """
        self.pygame_clock = pygame.time.Clock()
        self.target_fps = target_fps
        self.current_fps = target_fps
        self.delta_time = 0.0
        self.fixed_time_step = 1.0 / target_fps
        self.accumulated_time = 0.0
        self.simulation_speed = 1.0
        self.real_time = 0.0
        self.simulation_time = 0.0
        self.frame_count = 0
        self.last_time = time.time()
        
    def tick(self):
        """
        Update the clock and return the time delta.
        
        Returns:
            float: Time delta in seconds
        """
        # Get the time delta from Pygame's clock
        self.delta_time = self.pygame_clock.tick(self.target_fps) / 1000.0
        
        # Update real time tracking
        current_time = time.time()
        self.real_time += current_time - self.last_time
        self.last_time = current_time
        
        # Update simulation time based on speed multiplier
        self.simulation_time += self.delta_time * self.simulation_speed
        
        # Update frame counter
        self.frame_count += 1
        
        # Calculate current FPS
        self.current_fps = self.pygame_clock.get_fps()
        
        # Accumulate time for fixed updates
        self.accumulated_time += self.delta_time * self.simulation_speed
        
        return self.delta_time
    
    def should_update_fixed(self):
        """
        Check if a fixed update step should be performed.
        
        Returns:
            bool: True if a fixed update should be performed
        """
        return self.accumulated_time >= self.fixed_time_step
    
    def consume_fixed_update(self):
        """
        Consume time for a fixed update step.
        
        Returns:
            float: Fixed time step
        """
        self.accumulated_time -= self.fixed_time_step
        return self.fixed_time_step
    
    def set_simulation_speed(self, speed):
        """
        Set the simulation speed multiplier.
        
        Args:
            speed (float): Speed multiplier (1.0 = normal speed)
        """
        self.simulation_speed = speed
    
    def get_fps(self):
        """
        Get the current frames per second.
        
        Returns:
            float: Current FPS
        """
        return self.current_fps
    
    def get_simulation_time(self):
        """
        Get the current simulation time.
        
        Returns:
            float: Simulation time in seconds
        """
        return self.simulation_time
    
    def get_simulation_day(self):
        """
        Get the current simulation day.
        
        Returns:
            int: Current simulation day
        """
        from config import DAY_NIGHT_CYCLE_LENGTH
        return int(self.simulation_time * self.target_fps / DAY_NIGHT_CYCLE_LENGTH)
    
    def is_daytime(self):
        """
        Check if it's currently daytime in the simulation.
        
        Returns:
            bool: True if it's daytime
        """
        from config import DAY_NIGHT_CYCLE_LENGTH
        cycle_position = (self.simulation_time * self.target_fps) % DAY_NIGHT_CYCLE_LENGTH
        return cycle_position < (DAY_NIGHT_CYCLE_LENGTH / 2)
