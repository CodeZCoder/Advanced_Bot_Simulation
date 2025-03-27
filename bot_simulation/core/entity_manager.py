"""
Entity manager module for managing all entities in the simulation.
"""

import pygame
from world.world_map import Quadtree
import config

class EntityManager:
    """
    Manages all entities (bots, resources, obstacles) in the simulation.
    Provides methods to add, remove, and query entities.
    """
    
    def __init__(self, world_bounds):
        """
        Initialize the entity manager.
        
        Args:
            world_bounds (pygame.Rect): Boundaries of the world
        """
        self.bots = []
        self.resources = []
        self.obstacles = []
        self.signals = []
        self.world_bounds = world_bounds
        
        # Create a quadtree for spatial partitioning
        self.quadtree = Quadtree(0, pygame.Rect(
            world_bounds.x, 
            world_bounds.y, 
            world_bounds.width, 
            world_bounds.height
        ))
        
        # Statistics tracking
        self.bot_count_history = []
        self.resource_count_history = []
        self.avg_energy_history = []
        self.avg_age_history = []
        self.generation_count = 0
        
    def add_bot(self, bot):
        """
        Add a bot to the simulation.
        
        Args:
            bot: Bot entity
        """
        self.bots.append(bot)
        
    def add_resource(self, resource):
        """
        Add a resource to the simulation.
        
        Args:
            resource: Resource entity
        """
        self.resources.append(resource)
        
    def add_obstacle(self, obstacle):
        """
        Add an obstacle to the simulation.
        
        Args:
            obstacle: Obstacle entity
        """
        self.obstacles.append(obstacle)
        
    def add_signal(self, signal):
        """
        Add a communication signal to the simulation.
        
        Args:
            signal: Signal entity
        """
        self.signals.append(signal)
        
    def remove_bot(self, bot):
        """
        Remove a bot from the simulation.
        
        Args:
            bot: Bot entity
        """
        if bot in self.bots:
            self.bots.remove(bot)
            
    def remove_resource(self, resource):
        """
        Remove a resource from the simulation.
        
        Args:
            resource: Resource entity
        """
        if resource in self.resources:
            self.resources.remove(resource)
            
    def remove_obstacle(self, obstacle):
        """
        Remove an obstacle from the simulation.
        
        Args:
            obstacle: Obstacle entity
        """
        if obstacle in self.obstacles:
            self.obstacles.remove(obstacle)
            
    def remove_signal(self, signal):
        """
        Remove a communication signal from the simulation.
        
        Args:
            signal: Signal entity
        """
        if signal in self.signals:
            self.signals.remove(signal)
            
    def get_all_bots(self):
        """
        Get all bots in the simulation.
        
        Returns:
            list: All bot entities
        """
        return self.bots
    
    def get_all_resources(self):
        """
        Get all resources in the simulation.
        
        Returns:
            list: All resource entities
        """
        return self.resources
    
    def get_all_obstacles(self):
        """
        Get all obstacles in the simulation.
        
        Returns:
            list: All obstacle entities
        """
        return self.obstacles
    
    def get_all_signals(self):
        """
        Get all communication signals in the simulation.
        
        Returns:
            list: All signal entities
        """
        return self.signals
    
    def get_entity_count(self):
        """
        Get the count of all entities in the simulation.
        
        Returns:
            tuple: (bot_count, resource_count, obstacle_count, signal_count)
        """
        return (len(self.bots), len(self.resources), len(self.obstacles), len(self.signals))
    
    def update_quadtree(self):
        """
        Update the quadtree with current entity positions.
        """
        # Clear the quadtree
        self.quadtree.clear()
        
        # Insert all entities into the quadtree
        for bot in self.bots:
            pos = bot.get_position_component()
            rect = pygame.Rect(
                pos.x - bot.get_radius(), 
                pos.y - bot.get_radius(),
                bot.get_radius() * 2, 
                bot.get_radius() * 2
            )
            self.quadtree.insert({"entity": bot, "rect": rect})
            
        for resource in self.resources:
            pos = resource.get_position()
            rect = pygame.Rect(
                pos[0] - config.RESOURCE_RADIUS, 
                pos[1] - config.RESOURCE_RADIUS,
                config.RESOURCE_RADIUS * 2, 
                config.RESOURCE_RADIUS * 2
            )
            self.quadtree.insert({"entity": resource, "rect": rect})
            
        for obstacle in self.obstacles:
            rect = obstacle.get_rect()
            self.quadtree.insert({"entity": obstacle, "rect": rect})
    
    def get_entities_in_range(self, position, radius):
        """
        Get all entities within a certain range of a position.
        
        Args:
            position (tuple): (x, y) position
            radius (float): Search radius
            
        Returns:
            list: Entities within range
        """
        # Create a search rectangle
        search_rect = pygame.Rect(
            position[0] - radius,
            position[1] - radius,
            radius * 2,
            radius * 2
        )
        
        # Query the quadtree
        found_entities = []
        self.quadtree.retrieve(found_entities, search_rect)
        
        # Filter by actual distance (quadtree returns entities in the rectangle)
        result = []
        for entity_data in found_entities:
            entity = entity_data["entity"]
            entity_pos = entity.get_position() if hasattr(entity, "get_position") else entity.get_position_component().get_position()
            
            # Calculate distance
            dx = entity_pos[0] - position[0]
            dy = entity_pos[1] - position[1]
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance <= radius:
                result.append(entity)
                
        return result
    
    def get_entities_in_cone(self, position, direction, angle, radius):
        """
        Get all entities within a cone of vision.
        
        Args:
            position (tuple): (x, y) position
            direction (tuple): (dx, dy) direction vector
            angle (float): Cone angle in degrees
            radius (float): Cone radius
            
        Returns:
            list: Entities within the cone
        """
        # First get all entities in range
        entities_in_range = self.get_entities_in_range(position, radius)
        
        # Filter by angle
        result = []
        for entity in entities_in_range:
            entity_pos = entity.get_position() if hasattr(entity, "get_position") else entity.get_position_component().get_position()
            
            # Calculate vector to entity
            to_entity = (entity_pos[0] - position[0], entity_pos[1] - position[1])
            
            # Skip if entity is at the same position
            if to_entity[0] == 0 and to_entity[1] == 0:
                continue
                
            # Calculate dot product
            dot_product = direction[0] * to_entity[0] + direction[1] * to_entity[1]
            
            # Calculate magnitudes
            dir_mag = (direction[0] ** 2 + direction[1] ** 2) ** 0.5
            to_entity_mag = (to_entity[0] ** 2 + to_entity[1] ** 2) ** 0.5
            
            # Calculate angle between vectors
            angle_between = pygame.math.acos(dot_product / (dir_mag * to_entity_mag))
            angle_between = pygame.math.degrees(angle_between)
            
            # Check if entity is within the cone
            if angle_between <= angle / 2:
                result.append(entity)
                
        return result
    
    def update_statistics(self):
        """
        Update simulation statistics.
        """
        # Update bot count history
        self.bot_count_history.append(len(self.bots))
        if len(self.bot_count_history) > config.GRAPH_HISTORY_LENGTH:
            self.bot_count_history.pop(0)
            
        # Update resource count history
        self.resource_count_history.append(len(self.resources))
        if len(self.resource_count_history) > config.GRAPH_HISTORY_LENGTH:
            self.resource_count_history.pop(0)
            
        # Calculate average energy
        if self.bots:
            avg_energy = sum(bot.get_energy_component().get_energy() for bot in self.bots) / len(self.bots)
            self.avg_energy_history.append(avg_energy)
            if len(self.avg_energy_history) > config.GRAPH_HISTORY_LENGTH:
                self.avg_energy_history.pop(0)
                
        # Calculate average age
        if self.bots:
            avg_age = sum(bot.get_age() for bot in self.bots) / len(self.bots)
            self.avg_age_history.append(avg_age)
            if len(self.avg_age_history) > config.GRAPH_HISTORY_LENGTH:
                self.avg_age_history.pop(0)
                
    def get_statistics(self):
        """
        Get simulation statistics.
        
        Returns:
            dict: Simulation statistics
        """
        return {
            "bot_count": len(self.bots),
            "resource_count": len(self.resources),
            "obstacle_count": len(self.obstacles),
            "signal_count": len(self.signals),
            "bot_count_history": self.bot_count_history,
            "resource_count_history": self.resource_count_history,
            "avg_energy_history": self.avg_energy_history,
            "avg_age_history": self.avg_age_history,
            "generation_count": self.generation_count
        }
        
    def increment_generation(self):
        """
        Increment the generation counter.
        """
        self.generation_count += 1
