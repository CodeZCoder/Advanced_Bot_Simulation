"""
Main simulation module containing the simulation loop and core logic.
"""

import pygame
import sys
import random
import time
import config
from core.entity_manager import EntityManager
from world.world_map import WorldMap
from world.resource_manager import ResourceManager
from world.environment_effects import EnvironmentEffects
from systems.movement_system import MovementSystem
from systems.rendering_system import RenderingSystem
from systems.ai_system import AISystem
from systems.energy_system import EnergySystem
from systems.communication_system import CommunicationSystem
from systems.collision_system import CollisionSystem
from systems.evolution_system import EvolutionSystem
from entities.bot import Bot
from entities.obstacle import Obstacle
from ui.stats_display import StatsDisplay
from ui.controls import Controls
import csv
import os
from datetime import datetime

class Simulation:
    """
    Main simulation class that manages the simulation loop and core logic.
    """
    
    def __init__(self, screen, clock, event_handler):
        """
        Initialize the simulation.
        
        Args:
            screen (pygame.Surface): Main display surface
            clock (Clock): Clock instance for time management
            event_handler (EventHandler): Event handler instance
        """
        self.screen = screen
        self.clock = clock
        self.event_handler = event_handler
        
        # Create world map
        self.world_map = WorldMap(config.WORLD_WIDTH, config.WORLD_HEIGHT)
        
        # Create entity manager
        self.entity_manager = EntityManager(self.world_map.get_bounds())
        
        # Create resource manager
        self.resource_manager = ResourceManager(self.world_map, self.entity_manager)
        
        # Create environment effects
        self.environment_effects = EnvironmentEffects(self.world_map)
        
        # Create systems
        self.movement_system = MovementSystem(self.world_map, self.entity_manager)
        self.rendering_system = RenderingSystem(self.screen, self.entity_manager)
        self.ai_system = AISystem(self.entity_manager, self.world_map)
        self.energy_system = EnergySystem(self.entity_manager)
        self.communication_system = CommunicationSystem(self.entity_manager)
        self.collision_system = CollisionSystem(self.entity_manager, self.world_map)
        self.evolution_system = EvolutionSystem(self.entity_manager, self.world_map)
        
        # Create UI components
        self.stats_display = StatsDisplay(self.screen, self.entity_manager, self.clock)
        self.controls = Controls(self.screen, self.event_handler, self.clock)
        
        # Camera settings
        self.camera_rect = pygame.Rect(0, 0, config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self.camera_speed = 500  # Pixels per second
        self.camera_zoom = 1.0
        self.camera_zoom_speed = 0.1
        
        # Simulation settings
        self.simulation_speed = config.DEFAULT_SIMULATION_SPEED
        self.running = True
        self.paused = False
        self.debug_mode = False
        self.selected_bot = None
        
        # Data logging
        self.data_log_file = None
        self.data_log_writer = None
        self.last_log_time = 0
        self.log_interval = 5.0  # Log every 5 seconds
        
        # Initialize the simulation
        self._initialize()
        
    def _initialize(self):
        """
        Initialize the simulation with starting entities and settings.
        """
        # Add obstacles
        self._add_obstacles()
        
        # Add initial resources
        self.resource_manager.initialize_resources(config.RESOURCE_MAX_COUNT // 2)
        
        # Add initial bots
        self._add_initial_bots()
        
    def _add_obstacles(self):
        """
        Add obstacles to the world.
        """
        # Add boundary obstacles
        boundary_thickness = config.BOUNDARY_THICKNESS
        
        # Top boundary
        top_boundary = Obstacle(
            pygame.Rect(-boundary_thickness, -boundary_thickness, 
                       config.WORLD_WIDTH + boundary_thickness * 2, boundary_thickness)
        )
        self.world_map.add_obstacle(top_boundary)
        self.entity_manager.add_obstacle(top_boundary)
        
        # Bottom boundary
        bottom_boundary = Obstacle(
            pygame.Rect(-boundary_thickness, config.WORLD_HEIGHT, 
                       config.WORLD_WIDTH + boundary_thickness * 2, boundary_thickness)
        )
        self.world_map.add_obstacle(bottom_boundary)
        self.entity_manager.add_obstacle(bottom_boundary)
        
        # Left boundary
        left_boundary = Obstacle(
            pygame.Rect(-boundary_thickness, 0, 
                       boundary_thickness, config.WORLD_HEIGHT)
        )
        self.world_map.add_obstacle(left_boundary)
        self.entity_manager.add_obstacle(left_boundary)
        
        # Right boundary
        right_boundary = Obstacle(
            pygame.Rect(config.WORLD_WIDTH, 0, 
                       boundary_thickness, config.WORLD_HEIGHT)
        )
        self.world_map.add_obstacle(right_boundary)
        self.entity_manager.add_obstacle(right_boundary)
        
        # Add some random obstacles
        for _ in range(10):
            width = random.randint(50, 200)
            height = random.randint(50, 200)
            x = random.randint(0, config.WORLD_WIDTH - width)
            y = random.randint(0, config.WORLD_HEIGHT - height)
            
            obstacle = Obstacle(pygame.Rect(x, y, width, height))
            self.world_map.add_obstacle(obstacle)
            self.entity_manager.add_obstacle(obstacle)
            
    def _add_initial_bots(self):
        """
        Add initial bots to the simulation.
        """
        for _ in range(config.INITIAL_POPULATION):
            # Get a valid position
            position = self.world_map.get_random_valid_position(config.BOT_RADIUS_MAX)
            
            # Create a bot with random genetics
            bot = Bot(position)
            self.entity_manager.add_bot(bot)
            
    def run(self):
        """
        Run the main simulation loop.
        """
        while self.running:
            # Process events
            if not self.event_handler.process_events():
                self.running = False
                break
                
            # Update clock
            delta_time = self.clock.tick()
            
            # Handle simulation controls
            self._handle_controls()
            
            # Update camera
            self._update_camera(delta_time)
            
            # Update simulation if started and not paused
            if self.event_handler.is_simulation_started() and not self.event_handler.is_paused():
                self._update(delta_time)
                
            # Render
            self._render()
            
            # Handle data logging
            if self.event_handler.is_data_logging_requested():
                self._toggle_data_logging()
                
            if self.data_log_file and time.time() - self.last_log_time >= self.log_interval:
                self._log_data()
                self.last_log_time = time.time()
                
        # Clean up
        if self.data_log_file:
            self.data_log_file.close()
            
    def _handle_controls(self):
        """
        Handle simulation controls.
        """
        # Check for simulation speed change
        speed_change = self.event_handler.get_simulation_speed_change()
        if speed_change != 0:
            self.simulation_speed = max(
                config.SIMULATION_SPEED_MIN,
                min(config.SIMULATION_SPEED_MAX, 
                    self.simulation_speed + speed_change * config.SIMULATION_SPEED_STEP)
            )
            self.clock.set_simulation_speed(self.simulation_speed)
            
        # Check for bot selection
        if self.event_handler.is_mouse_clicked():
            self._handle_bot_selection()
            
        # Check for screenshot
        if self.event_handler.is_screenshot_requested():
            self._take_screenshot()
            
    def _update_camera(self, delta_time):
        """
        Update the camera position and zoom.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Handle camera movement
        camera_move = self.event_handler.get_camera_move()
        if camera_move[0] != 0 or camera_move[1] != 0:
            # Calculate movement
            move_x = camera_move[0] * self.camera_speed * delta_time
            move_y = camera_move[1] * self.camera_speed * delta_time
            
            # Update camera position
            self.camera_rect.x = max(0, min(config.WORLD_WIDTH - self.camera_rect.width, 
                                          self.camera_rect.x + move_x))
            self.camera_rect.y = max(0, min(config.WORLD_HEIGHT - self.camera_rect.height, 
                                          self.camera_rect.y + move_y))
                                          
        # Handle camera zoom
        camera_zoom = self.event_handler.get_camera_zoom()
        if camera_zoom != 0:
            # Calculate new zoom
            new_zoom = max(0.5, min(2.0, self.camera_zoom + camera_zoom * self.camera_zoom_speed))
            
            # Calculate zoom center (mouse position)
            mouse_pos = self.event_handler.get_mouse_position()
            center_x = mouse_pos[0] / self.camera_zoom
            center_y = mouse_pos[1] / self.camera_zoom
            
            # Update zoom
            zoom_factor = new_zoom / self.camera_zoom
            self.camera_zoom = new_zoom
            
            # Adjust camera position to zoom around mouse
            self.camera_rect.width = config.SCREEN_WIDTH / self.camera_zoom
            self.camera_rect.height = config.SCREEN_HEIGHT / self.camera_zoom
            self.camera_rect.x = max(0, min(config.WORLD_WIDTH - self.camera_rect.width,
                                          self.camera_rect.x + center_x * (1 - zoom_factor)))
            self.camera_rect.y = max(0, min(config.WORLD_HEIGHT - self.camera_rect.height,
                                          self.camera_rect.y + center_y * (1 - zoom_factor)))
                                          
    def _update(self, delta_time):
        """
        Update the simulation.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Perform fixed updates
        while self.clock.should_update_fixed():
            fixed_delta = self.clock.consume_fixed_update()
            
            # Update environment effects
            self.environment_effects.update(fixed_delta)
            is_daytime = self.environment_effects.is_daytime()
            
            # Update resource manager
            self.resource_manager.update(fixed_delta, is_daytime)
            
            # Update entity manager quadtree
            self.entity_manager.update_quadtree()
            
            # Update AI
            self.ai_system.update(fixed_delta)
            
            # Execute actions
            self.ai_system.execute_actions(fixed_delta)
            
            # Update physics and movement
            self.movement_system.update(fixed_delta)
            
            # Update collisions
            self.collision_system.update(fixed_delta)
            
            # Update energy
            self.energy_system.update(fixed_delta)
            
            # Update communication
            self.communication_system.update(fixed_delta)
            
            # Update evolution and reproduction
            self.evolution_system.update(fixed_delta)
            
            # Update statistics
            self.entity_manager.update_statistics()
            
    def _render(self):
        """
        Render the simulation.
        """
        # Clear the screen
        self.screen.fill(config.BLACK)
        
        # Render the world
        self.rendering_system.render_world(self.world_map, self.camera_rect, self.camera_zoom)
        
        # Render environment effects
        self.environment_effects.draw(self.screen, self.camera_rect)
        
        # Render entities
        self.rendering_system.render_entities(self.camera_rect, self.camera_zoom)
        
        # Render UI
        self.stats_display.render(self.simulation_speed, self.selected_bot)
        self.controls.render(self.simulation_speed)
        
        # Render debug info if enabled
        if self.debug_mode:
            self._render_debug_info()
            
        # Update the display
        pygame.display.flip()
        
    def _render_debug_info(self):
        """
        Render debug information.
        """
        # Render quadtree
        self.world_map.get_quadtree().draw(self.screen, self.camera_rect)
        
        # Render FPS
        font = pygame.font.SysFont(None, config.FONT_SIZE_SMALL)
        fps_text = font.render(f"FPS: {self.clock.get_fps():.1f}", True, config.WHITE)
        self.screen.blit(fps_text, (10, 10))
        
    def _handle_bot_selection(self):
        """
        Handle bot selection when clicking.
        """
        # Get mouse position in world coordinates
        mouse_pos = self.event_handler.get_mouse_position()
        world_x = self.camera_rect.x + mouse_pos[0] / self.camera_zoom
        world_y = self.camera_rect.y + mouse_pos[1] / self.camera_zoom
        world_pos = (world_x, world_y)
        
        # Find bots near the click
        nearby_entities = self.entity_manager.get_entities_in_range(world_pos, config.BOT_RADIUS_MAX * 2)
        
        # Filter for bots
        nearby_bots = [entity for entity in nearby_entities if isinstance(entity, Bot)]
        
        # Select the closest bot
        if nearby_bots:
            closest_bot = min(nearby_bots, key=lambda bot: 
                             ((bot.get_position_component().get_position()[0] - world_pos[0]) ** 2 + 
                              (bot.get_position_component().get_position()[1] - world_pos[1]) ** 2) ** 0.5)
            self.selected_bot = closest_bot
            self.event_handler.set_selected_bot(closest_bot)
        else:
            self.selected_bot = None
            self.event_handler.set_selected_bot(None)
            
    def _take_screenshot(self):
        """
        Take a screenshot of the current simulation.
        """
        # Create screenshots directory if it doesn't exist
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
            
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/simulation_{timestamp}.png"
        
        # Save screenshot
        pygame.image.save(self.screen, filename)
        print(f"Screenshot saved: {filename}")
        
    def _toggle_data_logging(self):
        """
        Toggle data logging on/off.
        """
        if self.data_log_file:
            # Close existing log file
            self.data_log_file.close()
            self.data_log_file = None
            self.data_log_writer = None
            print("Data logging stopped")
        else:
            # Create logs directory if it doesn't exist
            if not os.path.exists("logs"):
                os.makedirs("logs")
                
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs/simulation_{timestamp}.csv"
            
            # Create log file
            self.data_log_file = open(filename, 'w', newline='')
            self.data_log_writer = csv.writer(self.data_log_file)
            
            # Write header
            self.data_log_writer.writerow([
                "Time", "Day", "Bot Count", "Reso<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>