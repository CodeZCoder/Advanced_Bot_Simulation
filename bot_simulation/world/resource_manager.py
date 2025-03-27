"""
Resource manager module for handling spawning, depletion, and regeneration of resources.
"""

import pygame
import random
import config
from entities.resource import Resource

class ResourceManager:
    """
    Handles spawning, depletion, and regeneration of resources in the world.
    """
    
    def __init__(self, world_map, entity_manager):
        """
        Initialize the resource manager.
        
        Args:
            world_map (WorldMap): World map instance
            entity_manager (EntityManager): Entity manager instance
        """
        self.world_map = world_map
        self.entity_manager = entity_manager
        self.resource_spawn_timer = 0
        self.depleted_resources = []  # Track depleted resources for respawning
        self.resource_distribution = {}  # Track resource distribution across regions
        
    def update(self, delta_time, is_daytime):
        """
        Update resource spawning and regeneration.
        
        Args:
            delta_time (float): Time delta in seconds
            is_daytime (bool): Whether it's currently daytime
        """
        # Update spawn timer
        self.resource_spawn_timer += delta_time
        
        # Attempt to spawn new resources
        self._spawn_resources(is_daytime)
        
        # Update depleted resources
        self._update_depleted_resources(delta_time)
        
    def _spawn_resources(self, is_daytime):
        """
        Attempt to spawn new resources based on probability.
        
        Args:
            is_daytime (bool): Whether it's currently daytime
        """
        # Get current resource count
        current_resources = len(self.entity_manager.get_all_resources())
        
        # Don't spawn if at max capacity
        if current_resources >= config.RESOURCE_MAX_COUNT:
            return
            
        # Calculate spawn probability (higher during daytime)
        spawn_probability = config.RESOURCE_SPAWN_RATE
        if is_daytime:
            spawn_probability *= config.DAY_RESOURCE_MULTIPLIER
            
        # Attempt to spawn resources
        if random.random() < spawn_probability:
            # Determine resource energy value
            energy = random.uniform(config.RESOURCE_ENERGY_MIN, config.RESOURCE_ENERGY_MAX)
            
            # Get a valid position
            position = self.world_map.get_random_valid_position(config.RESOURCE_RADIUS)
            
            # Create and add the resource
            resource = Resource(position, energy)
            self.entity_manager.add_resource(resource)
            
            # Update resource distribution
            region = self.world_map.get_region_at_position(position)
            if region:
                region_type = region.get("type", "default")
                if region_type not in self.resource_distribution:
                    self.resource_distribution[region_type] = 0
                self.resource_distribution[region_type] += 1
                
    def _update_depleted_resources(self, delta_time):
        """
        Update depleted resources and respawn them after a delay.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Update respawn timers for depleted resources
        i = 0
        while i < len(self.depleted_resources):
            resource_data = self.depleted_resources[i]
            resource_data["timer"] += delta_time
            
            # Check if it's time to respawn
            if resource_data["timer"] >= config.RESOURCE_RESPAWN_TIME / config.FPS:
                # Create a new resource at the original position or a new position
                if random.random() < 0.5:  # 50% chance to respawn at original position
                    position = resource_data["position"]
                else:
                    position = self.world_map.get_random_valid_position(config.RESOURCE_RADIUS)
                    
                # Determine resource energy value
                energy = random.uniform(config.RESOURCE_ENERGY_MIN, config.RESOURCE_ENERGY_MAX)
                
                # Create and add the resource
                resource = Resource(position, energy)
                self.entity_manager.add_resource(resource)
                
                # Remove from depleted list
                self.depleted_resources.pop(i)
            else:
                i += 1
                
    def deplete_resource(self, resource):
        """
        Mark a resource as depleted and remove it from the simulation.
        
        Args:
            resource (Resource): Resource to deplete
        """
        # Add to depleted resources list for respawning
        self.depleted_resources.append({
            "position": resource.get_position(),
            "timer": 0
        })
        
        # Remove from entity manager
        self.entity_manager.remove_resource(resource)
        
        # Update resource distribution
        region = self.world_map.get_region_at_position(resource.get_position())
        if region:
            region_type = region.get("type", "default")
            if region_type in self.resource_distribution and self.resource_distribution[region_type] > 0:
                self.resource_distribution[region_type] -= 1
                
    def get_resource_distribution(self):
        """
        Get the distribution of resources across regions.
        
        Returns:
            dict: Resource distribution by region type
        """
        return self.resource_distribution
    
    def initialize_resources(self, count):
        """
        Initialize the simulation with a starting number of resources.
        
        Args:
            count (int): Number of resources to create
        """
        for _ in range(count):
            # Determine resource energy value
            energy = random.uniform(config.RESOURCE_ENERGY_MIN, config.RESOURCE_ENERGY_MAX)
            
            # Get a valid position
            position = self.world_map.get_random_valid_position(config.RESOURCE_RADIUS)
            
            # Create and add the resource
            resource = Resource(position, energy)
            self.entity_manager.add_resource(resource)
            
            # Update resource distribution
            region = self.world_map.get_region_at_position(position)
            if region:
                region_type = region.get("type", "default")
                if region_type not in self.resource_distribution:
                    self.resource_distribution[region_type] = 0
                self.resource_distribution[region_type] += 1
