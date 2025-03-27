"""
Growth system for bot simulation.
"""

import math
import config

class GrowthSystem:
    """System for handling entity growth, maturation, and development."""
    
    def __init__(self, entity_manager):
        """
        Initialize the growth system.
        
        Args:
            entity_manager: Entity manager instance
        """
        self.entity_manager = entity_manager
        
        # Track maturation events
        self.maturation_events = []
        
    def update(self, delta_time):
        """
        Update growth and maturation for all entities.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Clear previous maturation events
        self.maturation_events = []
        
        # Get all entities that can grow/mature
        entities = self.entity_manager.get_all_entities()
        growth_entities = []
        
        for entity in entities:
            if hasattr(entity, 'is_bot') and entity.is_bot():
                growth_entities.append(entity)
                
        # Update growth for each entity
        for entity in growth_entities:
            self._update_entity_growth(entity, delta_time)
            
    def _update_entity_growth(self, entity, delta_time):
        """
        Update growth for a single entity.
        
        Args:
            entity: Entity to update
            delta_time (float): Time delta in seconds
        """
        # Increment age
        entity.age += delta_time
        
        # Check for maturation
        if not entity.mature and entity.age >= config.BOT_MATURITY_AGE:
            self._handle_maturation(entity)
            
        # Update size based on age (if growing)
        if entity.age < config.BOT_GROWTH_DURATION:
            # Calculate growth progress (0 to 1)
            growth_progress = min(1.0, entity.age / config.BOT_GROWTH_DURATION)
            
            # Get genetic size factor
            genetic_component = entity.get_genetic_component()
            genes = genetic_component.get_all_genes()
            size_factor = genes['size_factor']
            
            # Calculate new size
            min_size = config.BOT_MIN_SIZE
            max_size = config.BOT_MAX_SIZE * size_factor
            new_size = min_size + (max_size - min_size) * growth_progress
            
            # Update entity size
            entity.set_radius(new_size)
            
            # Update mass (proportional to volume)
            entity.mass = math.pow(new_size / config.BOT_MIN_SIZE, 3)
            
        # Update capabilities based on age
        self._update_capabilities(entity)
        
    def _handle_maturation(self, entity):
        """
        Handle entity maturation.
        
        Args:
            entity: Entity that has matured
        """
        # Set mature flag
        entity.mature = True
        
        # Enable reproduction capability
        action_component = entity.get_action_component()
        action_component.enable_action("reproduce")
        
        # Adjust other capabilities
        communicator_component = entity.get_communicator_component()
        communicator_component.enable_signal_type(3)  # Enable mate signals
        
        # Add to maturation events
        self.maturation_events.append({
            "entity": entity,
            "position": entity.get_position(),
            "time": entity.age
        })
        
    def _update_capabilities(self, entity):
        """
        Update entity capabilities based on age.
        
        Args:
            entity: Entity to update
        """
        # Get components
        action_component = entity.get_action_component()
        sensor_component = entity.get_sensor_suite_component()
        communicator_component = entity.get_communicator_component()
        
        # Calculate development progress (0 to 1)
        development_progress = min(1.0, entity.age / config.BOT_MATURITY_AGE)
        
        # Get genetic development factor
        genetic_component = entity.get_genetic_component()
        genes = genetic_component.get_all_genes()
        development_factor = genes['development_rate']
        
        # Adjust progress based on genetics
        adjusted_progress = math.pow(development_progress, 1.0 / development_factor)
        
        # Update sensor capabilities
        base_visual_range = config.BOT_VISUAL_RANGE
        max_visual_range = base_visual_range * genes['visual_range']
        sensor_component.visual_range = base_visual_range + (max_visual_range - base_visual_range) * adjusted_progress
        
        base_fov = config.BOT_VISUAL_FOV
        max_fov = base_fov * genes['visual_fov']
        sensor_component.visual_fov = base_fov + (max_fov - base_fov) * adjusted_progress
        
        base_resource_range = config.BOT_RESOURCE_DETECTION_RANGE
        max_resource_range = base_resource_range * genes['resource_detection']
        sensor_component.resource_detection_range = base_resource_range + (max_resource_range - base_resource_range) * adjusted_progress
        
        # Update communication capabilities
        base_signal_range = config.BOT_SIGNAL_RANGE
        max_signal_range = base_signal_range * genes['signal_range']
        communicator_component.signal_range = base_signal_range + (max_signal_range - base_signal_range) * adjusted_progress
        
        # Enable actions based on development
        if adjusted_progress >= 0.25:
            action_component.enable_action("communicate")
            communicator_component.enable_signal_type(1)  # Danger signals
            
        if adjusted_progress >= 0.5:
            communicator_component.enable_signal_type(2)  # Food signals
            
        # Reproduction is enabled at maturation
        
    def get_maturation_events(self):
        """
        Get recent maturation events.
        
        Returns:
            list: List of maturation events
        """
        return self.maturation_events
        
    def get_average_maturation_age(self):
        """
        Get the average age at which entities mature.
        
        Returns:
            float: Average maturation age, or 0 if no data
        """
        total = 0.0
        count = 0
        
        for event in self.maturation_events:
            total += event["time"]
            count += 1
            
        if count == 0:
            return 0.0
            
        return total / count
