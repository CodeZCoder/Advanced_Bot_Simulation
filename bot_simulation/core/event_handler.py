"""
Event handler module for processing user input and simulation events.
"""

import pygame
import sys
from pygame.locals import *

class EventHandler:
    """
    Processes user input and simulation events.
    """
    
    def __init__(self):
        """
        Initialize the event handler.
        """
        self.quit_requested = False
        self.paused = False
        self.simulation_started = False
        self.simulation_speed_change = 0
        self.selected_bot = None
        self.mouse_position = (0, 0)
        self.mouse_clicked = False
        self.mouse_right_clicked = False
        self.key_pressed = {}
        self.key_just_pressed = {}
        self.screenshot_requested = False
        self.data_logging_requested = False
        self.camera_move = [0, 0]  # [x, y] movement
        self.camera_zoom = 0  # Positive for zoom in, negative for zoom out
        
    def process_events(self):
        """
        Process all pending events.
        
        Returns:
            bool: False if quit was requested, True otherwise
        """
        # Reset one-time event flags
        self.mouse_clicked = False
        self.mouse_right_clicked = False
        self.key_just_pressed = {}
        self.screenshot_requested = False
        self.data_logging_requested = False
        self.simulation_speed_change = 0
        self.camera_move = [0, 0]
        self.camera_zoom = 0
        
        # Process all pending events
        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit_requested = True
                return False
                
            elif event.type == KEYDOWN:
                self.key_pressed[event.key] = True
                self.key_just_pressed[event.key] = True
                
                # Handle specific key presses
                if event.key == K_ESCAPE:
                    self.quit_requested = True
                    return False
                elif event.key == K_SPACE:
                    self.simulation_started = not self.simulation_started
                elif event.key == K_p:
                    self.paused = not self.paused
                elif event.key == K_EQUALS or event.key == K_PLUS:
                    self.simulation_speed_change = 1
                elif event.key == K_MINUS:
                    self.simulation_speed_change = -1
                elif event.key == K_s and (self.key_pressed.get(K_LCTRL, False) or self.key_pressed.get(K_RCTRL, False)):
                    self.screenshot_requested = True
                elif event.key == K_l:
                    self.data_logging_requested = True
                    
                # Camera controls
                elif event.key == K_w or event.key == K_UP:
                    self.camera_move[1] = -1
                elif event.key == K_s or event.key == K_DOWN:
                    self.camera_move[1] = 1
                elif event.key == K_a or event.key == K_LEFT:
                    self.camera_move[0] = -1
                elif event.key == K_d or event.key == K_RIGHT:
                    self.camera_move[0] = 1
                    
            elif event.type == KEYUP:
                self.key_pressed[event.key] = False
                
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.mouse_clicked = True
                    self.mouse_position = event.pos
                elif event.button == 3:  # Right click
                    self.mouse_right_clicked = True
                    self.mouse_position = event.pos
                elif event.button == 4:  # Scroll up
                    self.camera_zoom = 1
                elif event.button == 5:  # Scroll down
                    self.camera_zoom = -1
                    
            elif event.type == MOUSEMOTION:
                self.mouse_position = event.pos
                
        return True
    
    def is_simulation_started(self):
        """
        Check if the simulation has been started.
        
        Returns:
            bool: True if the simulation is started
        """
        return self.simulation_started
    
    def is_paused(self):
        """
        Check if the simulation is paused.
        
        Returns:
            bool: True if the simulation is paused
        """
        return self.paused
    
    def get_simulation_speed_change(self):
        """
        Get the requested simulation speed change.
        
        Returns:
            int: 1 for speed up, -1 for slow down, 0 for no change
        """
        return self.simulation_speed_change
    
    def get_mouse_position(self):
        """
        Get the current mouse position.
        
        Returns:
            tuple: (x, y) mouse position
        """
        return self.mouse_position
    
    def is_mouse_clicked(self):
        """
        Check if the mouse was clicked this frame.
        
        Returns:
            bool: True if the mouse was clicked
        """
        return self.mouse_clicked
    
    def is_mouse_right_clicked(self):
        """
        Check if the right mouse button was clicked this frame.
        
        Returns:
            bool: True if the right mouse button was clicked
        """
        return self.mouse_right_clicked
    
    def is_key_pressed(self, key):
        """
        Check if a key is currently pressed.
        
        Args:
            key: Pygame key constant
            
        Returns:
            bool: True if the key is pressed
        """
        return self.key_pressed.get(key, False)
    
    def is_key_just_pressed(self, key):
        """
        Check if a key was just pressed this frame.
        
        Args:
            key: Pygame key constant
            
        Returns:
            bool: True if the key was just pressed
        """
        return self.key_just_pressed.get(key, False)
    
    def is_screenshot_requested(self):
        """
        Check if a screenshot was requested.
        
        Returns:
            bool: True if a screenshot was requested
        """
        return self.screenshot_requested
    
    def is_data_logging_requested(self):
        """
        Check if data logging was requested.
        
        Returns:
            bool: True if data logging was requested
        """
        return self.data_logging_requested
    
    def get_camera_move(self):
        """
        Get the requested camera movement.
        
        Returns:
            list: [x, y] movement direction
        """
        return self.camera_move
    
    def get_camera_zoom(self):
        """
        Get the requested camera zoom.
        
        Returns:
            int: Zoom direction (1 for in, -1 for out, 0 for none)
        """
        return self.camera_zoom
    
    def set_selected_bot(self, bot):
        """
        Set the currently selected bot.
        
        Args:
            bot: Bot entity or None
        """
        self.selected_bot = bot
    
    def get_selected_bot(self):
        """
        Get the currently selected bot.
        
        Returns:
            Bot entity or None
        """
        return self.selected_bot
