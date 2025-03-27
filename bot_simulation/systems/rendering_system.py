"""
Rendering system for bot simulation.
"""

import pygame
import math
import config

class RenderingSystem:
    """System for rendering entities and world elements."""
    
    def __init__(self, screen, entity_manager, world_map):
        """
        Initialize the rendering system.
        
        Args:
            screen (pygame.Surface): Screen surface to draw on
            entity_manager: Entity manager instance
            world_map: World map instance
        """
        self.screen = screen
        self.entity_manager = entity_manager
        self.world_map = world_map
        
        # Colors
        self.background_color = (10, 10, 20)
        self.grid_color = (30, 30, 40)
        
        # Debug rendering flags
        self.show_quadtree = False
        self.show_sensors = False
        self.show_ids = False
        
        # Font for debug text
        pygame.font.init()
        self.debug_font = pygame.font.SysFont('Arial', 10)
        
    def render(self):
        """Render the simulation."""
        # Clear screen
        self.screen.fill(self.background_color)
        
        # Get camera information
        camera_rect = self.world_map.get_camera_rect()
        zoom = self.world_map.get_zoom()
        
        # Draw grid
        self._draw_grid(camera_rect, zoom)
        
        # Draw entities
        self._draw_entities(camera_rect, zoom)
        
        # Draw debug information if enabled
        if self.show_quadtree:
            self._draw_quadtree(camera_rect, zoom)
            
    def _draw_grid(self, camera_rect, zoom):
        """
        Draw background grid.
        
        Args:
            camera_rect (pygame.Rect): Camera view rectangle
            zoom (float): Zoom factor
        """
        # Calculate grid size based on zoom
        grid_size = 100 * zoom
        
        # Calculate grid offset
        offset_x = -camera_rect.x * zoom % grid_size
        offset_y = -camera_rect.y * zoom % grid_size
        
        # Draw vertical grid lines
        for x in range(int(offset_x), int(self.screen.get_width() + grid_size), int(grid_size)):
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.screen.get_height()))
            
        # Draw horizontal grid lines
        for y in range(int(offset_y), int(self.screen.get_height() + grid_size), int(grid_size)):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (self.screen.get_width(), y))
            
    def _draw_entities(self, camera_rect, zoom):
        """
        Draw all entities.
        
        Args:
            camera_rect (pygame.Rect): Camera view rectangle
            zoom (float): Zoom factor
        """
        # Get all entities
        entities = self.entity_manager.get_all_entities()
        
        # Sort entities by type for layered rendering
        # Draw in order: obstacles, resources, signals, bots
        obstacles = []
        resources = []
        signals = []
        bots = []
        
        for entity in entities:
            if hasattr(entity, 'is_obstacle') and entity.is_obstacle():
                obstacles.append(entity)
            elif hasattr(entity, 'is_resource') and entity.is_resource():
                resources.append(entity)
            elif hasattr(entity, 'is_signal') and entity.is_signal():
                signals.append(entity)
            elif hasattr(entity, 'is_bot') and entity.is_bot():
                bots.append(entity)
                
        # Draw each type of entity
        for entity in obstacles:
            if hasattr(entity, 'draw'):
                entity.draw(self.screen, camera_rect, zoom)
                
        for entity in resources:
            if hasattr(entity, 'draw'):
                entity.draw(self.screen, camera_rect, zoom)
                
        for entity in signals:
            if hasattr(entity, 'draw'):
                entity.draw(self.screen, camera_rect, zoom)
                
        for entity in bots:
            if hasattr(entity, 'draw'):
                entity.draw(self.screen, camera_rect, zoom)
                
                # Draw sensor visualization if enabled
                if self.show_sensors and hasattr(entity, 'get_sensor_suite_component'):
                    self._draw_bot_sensors(entity, camera_rect, zoom)
                    
                # Draw entity ID if enabled
                if self.show_ids:
                    self._draw_entity_id(entity, camera_rect, zoom)
                    
    def _draw_bot_sensors(self, bot, camera_rect, zoom):
        """
        Draw bot sensor visualization.
        
        Args:
            bot: Bot entity
            camera_rect (pygame.Rect): Camera view rectangle
            zoom (float): Zoom factor
        """
        sensor_component = bot.get_sensor_suite_component()
        position = bot.get_position()
        
        # Calculate screen position
        screen_x = (position[0] - camera_rect.x) * zoom
        screen_y = (position[1] - camera_rect.y) * zoom
        
        # Draw visual range
        visual_range = sensor_component.visual_range * zoom
        pygame.draw.circle(self.screen, (50, 50, 150, 30), (screen_x, screen_y), visual_range, 1)
        
        # Draw visual cone
        fov = sensor_component.visual_fov
        direction = bot.get_direction()
        
        if direction[0] == 0 and direction[1] == 0:
            # If no direction, use default
            direction = (1, 0)
            
        # Calculate cone points
        angle = math.atan2(direction[1], direction[0])
        half_fov = fov / 2
        
        start_angle = angle - half_fov
        end_angle = angle + half_fov
        
        # Draw cone
        points = [(screen_x, screen_y)]
        
        for i in range(20):
            cone_angle = start_angle + (end_angle - start_angle) * i / 19
            cone_x = screen_x + math.cos(cone_angle) * visual_range
            cone_y = screen_y + math.sin(cone_angle) * visual_range
            points.append((cone_x, cone_y))
            
        points.append((screen_x, screen_y))
        
        # Draw filled cone with transparency
        cone_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        pygame.draw.polygon(cone_surface, (50, 50, 150, 30), points)
        self.screen.blit(cone_surface, (0, 0))
        
        # Draw resource detection range
        resource_range = sensor_component.resource_detection_range * zoom
        pygame.draw.circle(self.screen, (50, 150, 50, 30), (screen_x, screen_y), resource_range, 1)
        
        # Draw signal detection range
        signal_range = sensor_component.signal_detection_range * zoom
        pygame.draw.circle(self.screen, (150, 50, 50, 30), (screen_x, screen_y), signal_range, 1)
        
    def _draw_entity_id(self, entity, camera_rect, zoom):
        """
        Draw entity ID.
        
        Args:
            entity: Entity to draw ID for
            camera_rect (pygame.Rect): Camera view rectangle
            zoom (float): Zoom factor
        """
        position = entity.get_position()
        
        # Calculate screen position
        screen_x = (position[0] - camera_rect.x) * zoom
        screen_y = (position[1] - camera_rect.y) * zoom
        
        # Get entity ID
        entity_id = getattr(entity, 'id', str(id(entity)))
        
        # Render ID text
        text = self.debug_font.render(str(entity_id), True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen_x, screen_y - 20))
        
        self.screen.blit(text, text_rect)
        
    def _draw_quadtree(self, camera_rect, zoom):
        """
        Draw quadtree visualization.
        
        Args:
            camera_rect (pygame.Rect): Camera view rectangle
            zoom (float): Zoom factor
        """
        # Get quadtree
        quadtree = self.world_map.get_quadtree()
        
        # Draw quadtree nodes
        self._draw_quadtree_node(quadtree.root, camera_rect, zoom)
        
    def _draw_quadtree_node(self, node, camera_rect, zoom):
        """
        Draw a quadtree node.
        
        Args:
            node: Quadtree node
            camera_rect (pygame.Rect): Camera view rectangle
            zoom (float): Zoom factor
        """
        # Calculate screen rectangle
        screen_rect = pygame.Rect(
            (node.boundary.x - camera_rect.x) * zoom,
            (node.boundary.y - camera_rect.y) * zoom,
            node.boundary.width * zoom,
            node.boundary.height * zoom
        )
        
        # Draw rectangle
        pygame.draw.rect(self.screen, (100, 100, 100, 50), screen_rect, 1)
        
        # Draw children if divided
        if node.divided:
            self._draw_quadtree_node(node.northwest, camera_rect, zoom)
            self._draw_quadtree_node(node.northeast, camera_rect, zoom)
            self._draw_quadtree_node(node.southwest, camera_rect, zoom)
            self._draw_quadtree_node(node.southeast, camera_rect, zoom)
            
    def toggle_quadtree_visualization(self):
        """Toggle quadtree visualization."""
        self.show_quadtree = not self.show_quadtree
        
    def toggle_sensor_visualization(self):
        """Toggle sensor visualization."""
        self.show_sensors = not self.show_sensors
        
    def toggle_id_visualization(self):
        """Toggle entity ID visualization."""
        self.show_ids = not self.show_ids
