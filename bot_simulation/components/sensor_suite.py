"""
Sensor suite component module for defining entity perception.
"""

import math
import pygame
import config
from components.position import PositionComponent

class SensorSuiteComponent:
    """
    Defines an entity's perception capabilities.
    """
    
    def __init__(self, visual_range=150, visual_angle=120, resource_detection_range=100, signal_detection_range=200):
        """
        Initialize the sensor suite component.
        
        Args:
            visual_range (float): Maximum visual detection range
            visual_angle (float): Field of view angle in degrees
            resource_detection_range (float): Range for detecting resources
            signal_detection_range (float): Range for detecting communication signals
        """
        self.visual_range = visual_range
        self.visual_angle = visual_angle
        self.resource_detection_range = resource_detection_range
        self.signal_detection_range = signal_detection_range
        
        # Sensor accuracy (1.0 = perfect, 0.0 = completely inaccurate)
        self.visual_accuracy = 0.9
        self.resource_accuracy = 0.8
        self.signal_accuracy = 0.7
        
        # Sensor resolution (higher = more detailed perception)
        self.visual_resolution = 0.8
        
        # Perception data
        self.perceived_entities = []
        self.perceived_resources = []
        self.perceived_signals = []
        self.perceived_obstacles = []
        
        # Internal sensors
        self.energy_level = 0
        self.age = 0
        
    def update(self, position_component, direction, entity_manager, world_map):
        """
        Update sensor data based on current position and surroundings.
        
        Args:
            position_component (PositionComponent): Entity's position component
            direction (tuple): Direction vector (dx, dy)
            entity_manager (EntityManager): Entity manager instance
            world_map (WorldMap): World map instance
        """
        # Clear previous perception data
        self.perceived_entities.clear()
        self.perceived_resources.clear()
        self.perceived_signals.clear()
        self.perceived_obstacles.clear()
        
        # Get position
        position = position_component.get_position()
        
        # Update visual perception
        self._update_visual_perception(position, direction, entity_manager)
        
        # Update resource detection
        self._update_resource_detection(position, entity_manager)
        
        # Update signal detection
        self._update_signal_detection(position, entity_manager)
        
        # Update obstacle detection
        self._update_obstacle_detection(position, world_map)
        
    def _update_visual_perception(self, position, direction, entity_manager):
        """
        Update visual perception of other entities.
        
        Args:
            position (tuple): (x, y) position
            direction (tuple): Direction vector (dx, dy)
            entity_manager (EntityManager): Entity manager instance
        """
        # Normalize direction vector
        dir_mag = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
        if dir_mag > 0:
            norm_dir = (direction[0] / dir_mag, direction[1] / dir_mag)
        else:
            norm_dir = (1, 0)  # Default direction if no movement
            
        # Get entities in cone of vision
        entities = entity_manager.get_entities_in_cone(
            position, norm_dir, self.visual_angle, self.visual_range
        )
        
        # Process perceived entities with accuracy and resolution factors
        for entity in entities:
            # Skip self
            if hasattr(entity, 'id') and hasattr(self, 'owner') and entity.id == self.owner.id:
                continue
                
            # Get entity position
            if hasattr(entity, 'get_position'):
                entity_pos = entity.get_position()
            elif hasattr(entity, 'get_position_component'):
                entity_pos = entity.get_position_component().get_position()
            else:
                continue
                
            # Calculate distance
            dx = entity_pos[0] - position[0]
            dy = entity_pos[1] - position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Apply accuracy (chance to miss based on distance)
            detection_chance = self.visual_accuracy * (1 - (distance / self.visual_range) ** 0.5)
            if detection_chance < 0.1:
                detection_chance = 0.1  # Minimum chance to detect
                
            import random
            if random.random() < detection_chance:
                # Apply resolution (uncertainty in position based on distance)
                position_error = distance * (1 - self.visual_resolution)
                perceived_pos = (
                    entity_pos[0] + random.uniform(-position_error, position_error),
                    entity_pos[1] + random.uniform(-position_error, position_error)
                )
                
                # Add to perceived entities
                self.perceived_entities.append({
                    "entity": entity,
                    "position": perceived_pos,
                    "distance": distance,
                    "type": type(entity).__name__,
                    "certainty": detection_chance
                })
                
    def _update_resource_detection(self, position, entity_manager):
        """
        Update resource detection.
        
        Args:
            position (tuple): (x, y) position
            entity_manager (EntityManager): Entity manager instance
        """
        # Get resources in range
        resources = entity_manager.get_entities_in_range(position, self.resource_detection_range)
        
        # Filter for resources
        resources = [entity for entity in resources if hasattr(entity, 'is_resource') and entity.is_resource()]
        
        # Process perceived resources with accuracy factor
        for resource in resources:
            # Get resource position
            resource_pos = resource.get_position()
            
            # Calculate distance
            dx = resource_pos[0] - position[0]
            dy = resource_pos[1] - position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Apply accuracy (chance to miss based on distance)
            detection_chance = self.resource_accuracy * (1 - (distance / self.resource_detection_range) ** 0.5)
            if detection_chance < 0.1:
                detection_chance = 0.1  # Minimum chance to detect
                
            import random
            if random.random() < detection_chance:
                # Apply position uncertainty
                position_error = distance * (1 - self.resource_accuracy)
                perceived_pos = (
                    resource_pos[0] + random.uniform(-position_error, position_error),
                    resource_pos[1] + random.uniform(-position_error, position_error)
                )
                
                # Add to perceived resources
                self.perceived_resources.append({
                    "resource": resource,
                    "position": perceived_pos,
                    "distance": distance,
                    "energy": resource.get_energy() if hasattr(resource, 'get_energy') else 0,
                    "certainty": detection_chance
                })
                
    def _update_signal_detection(self, position, entity_manager):
        """
        Update signal detection.
        
        Args:
            position (tuple): (x, y) position
            entity_manager (EntityManager): Entity manager instance
        """
        # Get signals in range
        signals = entity_manager.get_entities_in_range(position, self.signal_detection_range)
        
        # Filter for signals
        signals = [entity for entity in signals if hasattr(entity, 'is_signal') and entity.is_signal()]
        
        # Process perceived signals with accuracy factor
        for signal in signals:
            # Get signal position
            signal_pos = signal.get_position()
            
            # Calculate distance
            dx = signal_pos[0] - position[0]
            dy = signal_pos[1] - position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Apply accuracy (chance to miss based on distance)
            detection_chance = self.signal_accuracy * (1 - (distance / self.signal_detection_range) ** 0.5)
            if detection_chance < 0.1:
                detection_chance = 0.1  # Minimum chance to detect
                
            import random
            if random.random() < detection_chance:
                # Add to perceived signals
                self.perceived_signals.append({
                    "signal": signal,
                    "position": signal_pos,
                    "distance": distance,
                    "type": signal.get_type() if hasattr(signal, 'get_type') else 0,
                    "data": signal.get_data() if hasattr(signal, 'get_data') else None,
                    "sender": signal.get_sender() if hasattr(signal, 'get_sender') else None,
                    "certainty": detection_chance
                })
                
    def _update_obstacle_detection(self, position, world_map):
        """
        Update obstacle detection.
        
        Args:
            position (tuple): (x, y) position
            world_map (WorldMap): World map instance
        """
        # Get obstacles
        obstacles = world_map.get_obstacles()
        
        # Process obstacles in visual range
        for obstacle in obstacles:
            # Get obstacle rect
            rect = obstacle.get_rect()
            
            # Calculate distance to closest point on rectangle
            closest_x = max(rect.left, min(position[0], rect.right))
            closest_y = max(rect.top, min(position[1], rect.bottom))
            
            dx = closest_x - position[0]
            dy = closest_y - position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Check if in range
            if distance <= self.visual_range:
                # Add to perceived obstacles
                self.perceived_obstacles.append({
                    "obstacle": obstacle,
                    "rect": rect,
                    "distance": distance
                })
                
    def set_internal_sensors(self, energy_level, age):
        """
        Update internal sensor readings.
        
        Args:
            energy_level (float): Current energy level
            age (int): Current age
        """
        self.energy_level = energy_level
        self.age = age
        
    def get_perceived_entities(self):
        """
        Get all perceived entities.
        
        Returns:
            list: Perceived entities
        """
        return self.perceived_entities
    
    def get_perceived_resources(self):
        """
        Get perceived resources.
        
        Returns:
            list: Perceived resources
        """
        return self.perceived_resources
    
    def get_perceived_signals(self):
        """
        Get perceived communication signals.
        
        Returns:
            list: Perceived signals
        """
        return self.perceived_signals
    
    def get_perceived_obstacles(self):
        """
        Get perceived obstacles.
        
        Returns:
            list: Perceived obstacles
        """
        return self.perceived_obstacles
    
    def get_closest_resource(self):
        """
        Get the closest perceived resource.
        
        Returns:
            dict: Closest resource data or None
        """
        if not self.perceived_resources:
            return None
            
        return min(self.perceived_resources, key=lambda r: r["distance"])
    
    def get_closest_entity(self, entity_type=None):
        """
        Get the closest perceived entity, optionally filtered by type.
        
        Args:
            entity_type (str, optional): Entity type to filter by
            
        Returns:
            dict: Closest entity data or None
        """
        if not self.perceived_entities:
            return None
            
        if entity_type:
            filtered = [e for e in self.perceived_entities if e["type"] == entity_type]
            if not filtered:
                return None
            return min(filtered, key=lambda e: e["distance"])
        else:
            return min(self.perceived_entities, key=lambda e: e["distance"])
    
    def get_energy_level(self):
        """
        Get internal energy level reading.
        
        Returns:
            float: Energy level
        """
        return self.energy_level
    
    def get_age(self):
        """
        Get internal age reading.
        
        Returns:
            int: Age
        """
        return self.age
    
    def set_visual_range(self, range_value):
        """
        Set visual detection range.
        
        Args:
            range_value (float): New range
        """
        self.visual_range = range_value
        
    def set_visual_angle(self, angle):
        """
        Set visual detection angle.
        
        Args:
            angle (float): New angle in degrees
        """
        self.visual_angle = angle
        
    def set_resource_detection_range(self, range_value):
        """
        Set resource detection range.
        
        Args:
            range_value (float): New range
        """
        self.resource_detection_range = range_value
        
    def set_signal_detection_range(self, range_value):
        """
        Set signal detection range.
        
        Args:
            range_value (float): New range
        """
        self.signal_detection_range = range_value
        
    def set_accuracies(self, visual, resource, signal):
        """
        Set sensor accuracies.
        
        Args:
            visual (float): Visual accuracy (0-1)
            resource (float): Resource detection accuracy (0-1)
            signal (float): Signal detection accuracy (0-1)
        """
        self.visual_accuracy = max(0, min(1, visual))
        self.resource_accuracy = max(0, min(1, resource))
        self.signal_accuracy = max(0, min(1, signal))
        
    def draw_perception(self, surface, position, direction, camera_rect, zoom=1.0):
        """
        Draw visual representation of perception for debugging.
        
        Args:
            surface (pygame.Surface): Surface to draw on
            position (tuple): Entity position
            direction (tuple): Direction vector
            camera_rect (pygame.Rect): Camera view rectangle
            zoom (float): Zoom factor
        """
        # Calculate screen position
        screen_x = (position[0] - camera_rect.x) * zoom
        screen_y = (position[1] - camera_rect.y) * zoom
        
        # Normalize direction
        dir_mag = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
        if dir_mag > 0:
            norm_dir = (direction[0] / dir_mag, direction[1] / dir_mag)
        else:
            norm_dir = (1, 0)
            
        # Draw visual cone
        angle_rad = math.radians(self.visual_angle / 2)
        start_angle = math.atan2(norm_dir[1], norm_dir[0]) - angle_rad
        end_angle = math.atan2(norm_dir[1], norm_dir[0]) + angle_rad
        
        # Draw arc for visual cone
        points = [(screen_x, screen_y)]
        steps = 20
        for i in range(steps + 1):
            angle = start_angle + (end_angle - start_angle) * (i / steps)
            x = screen_x + math.cos(angle) * self.visual_range * zoom
            y = screen_y + math.sin(angle) * self.visual_range * zoom
            points.append((x, y))
        points.append((screen_x, <response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>