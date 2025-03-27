"""
Evolution system for bot simulation.
"""

import random
import math
import time
import config
from entities.bot import Bot

class EvolutionSystem:
    """System for handling bot evolution, reproduction, and death."""
    
    def __init__(self, entity_manager, world_map):
        """
        Initialize the evolution system.
        
        Args:
            entity_manager: Entity manager instance
            world_map: World map instance
        """
        self.entity_manager = entity_manager
        self.world_map = world_map
        
        # Reproduction tracking
        self.reproduction_cooldowns = {}
        
        # Death tracking
        self.dead_entities = []
        
        # Statistics
        self.birth_count = 0
        self.death_count = 0
        self.generation_stats = {}
        
    def update(self, delta_time):
        """
        Update the evolution system.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Update reproduction cooldowns
        current_time = time.time()
        cooldowns_to_remove = []
        
        for entity_id, cooldown_time in self.reproduction_cooldowns.items():
            if current_time >= cooldown_time:
                cooldowns_to_remove.append(entity_id)
                
        for entity_id in cooldowns_to_remove:
            del self.reproduction_cooldowns[entity_id]
            
        # Process dead entities
        for entity in self.dead_entities:
            self.entity_manager.remove_entity(entity)
            
        self.dead_entities = []
        
    def handle_reproduction(self, parent1, parent2=None):
        """
        Handle reproduction between bots.
        
        Args:
            parent1: First parent bot
            parent2: Second parent bot (optional, for sexual reproduction)
            
        Returns:
            Bot: Newly created bot, or None if reproduction failed
        """
        # Check if parent1 is on cooldown
        current_time = time.time()
        if parent1.get_id() in self.reproduction_cooldowns:
            return None
            
        # Check if parent1 is mature
        if not parent1.is_mature():
            return None
            
        # Check if parent1 has enough energy
        energy_component1 = parent1.get_energy_component()
        if energy_component1.get_energy_percentage() < config.REPRODUCTION_ENERGY_THRESHOLD:
            return None
            
        # Determine reproduction type
        if parent2 is None:
            # Asexual reproduction
            return self._asexual_reproduction(parent1)
        else:
            # Sexual reproduction
            
            # Check if parent2 is on cooldown
            if parent2.get_id() in self.reproduction_cooldowns:
                return None
                
            # Check if parent2 is mature
            if not parent2.is_mature():
                return None
                
            # Check if parent2 has enough energy
            energy_component2 = parent2.get_energy_component()
            if energy_component2.get_energy_percentage() < config.REPRODUCTION_ENERGY_THRESHOLD:
                return None
                
            # Check if parents are close enough
            pos1 = parent1.get_position()
            pos2 = parent2.get_position()
            
            dx = pos1[0] - pos2[0]
            dy = pos1[1] - pos2[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > parent1.get_radius() + parent2.get_radius() + 10:
                return None
                
            return self._sexual_reproduction(parent1, parent2)
            
    def _asexual_reproduction(self, parent):
        """
        Perform asexual reproduction.
        
        Args:
            parent: Parent bot
            
        Returns:
            Bot: Newly created bot
        """
        # Get parent components
        genetic_component = parent.get_genetic_component()
        position_component = parent.get_position_component()
        energy_component = parent.get_energy_component()
        
        # Create child genes (copy with mutations)
        child_genes = genetic_component.copy_with_mutations()
        
        # Calculate child position (near parent)
        angle = random.uniform(0, 2 * math.pi)
        distance = parent.get_radius() + config.BOT_RADIUS + 5
        
        child_pos = (
            position_component.x + math.cos(angle) * distance,
            position_component.y + math.sin(angle) * distance
        )
        
        # Ensure position is within world bounds
        world_bounds = self.world_map.get_bounds()
        child_pos = (
            max(0, min(world_bounds.width, child_pos[0])),
            max(0, min(world_bounds.height, child_pos[1]))
        )
        
        # Create child bot
        child = Bot(child_pos, child_genes)
        
        # Set child generation
        child.generation = parent.generation + 1
        
        # Deduct energy from parent
        reproduction_cost = config.REPRODUCTION_ENERGY_COST
        energy_component.change_energy(-reproduction_cost)
        
        # Set reproduction cooldown for parent
        self.reproduction_cooldowns[parent.get_id()] = time.time() + config.REPRODUCTION_COOLDOWN
        
        # Add child to entity manager
        self.entity_manager.add_entity(child)
        
        # Update statistics
        self.birth_count += 1
        parent.reproduction_count += 1
        
        # Update generation stats
        if child.generation not in self.generation_stats:
            self.generation_stats[child.generation] = 1
        else:
            self.generation_stats[child.generation] += 1
            
        return child
        
    def _sexual_reproduction(self, parent1, parent2):
        """
        Perform sexual reproduction.
        
        Args:
            parent1: First parent bot
            parent2: Second parent bot
            
        Returns:
            Bot: Newly created bot
        """
        # Get parent components
        genetic_component1 = parent1.get_genetic_component()
        genetic_component2 = parent2.get_genetic_component()
        position_component1 = parent1.get_position_component()
        position_component2 = parent2.get_position_component()
        energy_component1 = parent1.get_energy_component()
        energy_component2 = parent2.get_energy_component()
        
        # Create child genes (combine with mutations)
        child_genes = genetic_component1.combine_with(genetic_component2)
        
        # Calculate child position (between parents)
        midpoint = (
            (position_component1.x + position_component2.x) / 2,
            (position_component1.y + position_component2.y) / 2
        )
        
        # Add small random offset
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(5, 15)
        
        child_pos = (
            midpoint[0] + math.cos(angle) * distance,
            midpoint[1] + math.sin(angle) * distance
        )
        
        # Ensure position is within world bounds
        world_bounds = self.world_map.get_bounds()
        child_pos = (
            max(0, min(world_bounds.width, child_pos[0])),
            max(0, min(world_bounds.height, child_pos[1]))
        )
        
        # Create child bot
        child = Bot(child_pos, child_genes)
        
        # Set child generation (max of parents + 1)
        child.generation = max(parent1.generation, parent2.generation) + 1
        
        # Deduct energy from parents
        reproduction_cost = config.REPRODUCTION_ENERGY_COST / 2  # Split cost between parents
        energy_component1.change_energy(-reproduction_cost)
        energy_component2.change_energy(-reproduction_cost)
        
        # Set reproduction cooldown for parents
        self.reproduction_cooldowns[parent1.get_id()] = time.time() + config.REPRODUCTION_COOLDOWN
        self.reproduction_cooldowns[parent2.get_id()] = time.time() + config.REPRODUCTION_COOLDOWN
        
        # Add child to entity manager
        self.entity_manager.add_entity(child)
        
        # Update statistics
        self.birth_count += 1
        parent1.reproduction_count += 1
        parent2.reproduction_count += 1
        
        # Update generation stats
        if child.generation not in self.generation_stats:
            self.generation_stats[child.generation] = 1
        else:
            self.generation_stats[child.generation] += 1
            
        return child
        
    def handle_death(self, entity):
        """
        Handle entity death.
        
        Args:
            entity: Entity that died
        """
        # Add to dead entities list for removal
        self.dead_entities.append(entity)
        
        # Update statistics
        self.death_count += 1
        
    def check_entity_death(self, entity):
        """
        Check if an entity should die.
        
        Args:
            entity: Entity to check
            
        Returns:
            bool: True if entity should die
        """
        # Check if entity is a bot
        if not hasattr(entity, 'is_bot') or not entity.is_bot():
            return False
            
        # Check energy
        energy_component = entity.get_energy_component()
        if energy_component.get_energy() <= 0:
            return True
            
        # Check age (if max age is defined)
        if config.BOT_MAX_AGE > 0:
            if entity.get_age() >= config.BOT_MAX_AGE:
                return True
                
        return False
        
    def get_birth_count(self):
        """
        Get the total number of births.
        
        Returns:
            int: Birth count
        """
        return self.birth_count
        
    def get_death_count(self):
        """
        Get the total number of deaths.
        
        Returns:
            int: Death count
        """
        return self.death_count
        
    def get_generation_stats(self):
        """
        Get generation statistics.
        
        Returns:
            dict: Generation statistics
        """
        return self.generation_stats
        
    def get_highest_generation(self):
        """
        Get the highest generation number.
        
        Returns:
            int: Highest generation
        """
        if not self.generation_stats:
            return 0
        return max(self.generation_stats.keys())
