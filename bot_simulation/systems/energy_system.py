"""
Energy system for bot simulation.
"""

import math
import config

class EnergySystem:
    """System for handling entity energy metabolism and consumption."""
    
    def __init__(self, entity_manager, evolution_system):
        """
        Initialize the energy system.
        
        Args:
            entity_manager: Entity manager instance
            evolution_system: Evolution system instance
        """
        self.entity_manager = entity_manager
        self.evolution_system = evolution_system
        
    def update(self, delta_time):
        """
        Update energy levels for all entities.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Get all entities with energy components
        entities = self.entity_manager.get_all_entities()
        energy_entities = []
        
        for entity in entities:
            if hasattr(entity, 'get_energy_component'):
                energy_entities.append(entity)
                
        # Update energy for each entity
        for entity in energy_entities:
            self._update_entity_energy(entity, delta_time)
            
            # Check for death
            if self.evolution_system.check_entity_death(entity):
                self.evolution_system.handle_death(entity)
                
    def _update_entity_energy(self, entity, delta_time):
        """
        Update energy for a single entity.
        
        Args:
            entity: Entity to update
            delta_time (float): Time delta in seconds
        """
        energy_component = entity.get_energy_component()
        
        # Apply base metabolism cost
        if hasattr(entity, 'is_bot') and entity.is_bot():
            # Bots have more complex metabolism
            genetic_component = entity.get_genetic_component()
            genes = genetic_component.get_all_genes()
            
            # Base metabolic rate from genes
            base_rate = genes['metabolic_rate']
            
            # Scale with size/mass if applicable
            if hasattr(entity, 'mass'):
                base_rate *= math.pow(entity.mass, 0.75)  # Kleiber's law
                
            # Adjust based on activity
            velocity_component = entity.get_velocity_component()
            speed_squared = velocity_component.dx * velocity_component.dx + velocity_component.dy * velocity_component.dy
            activity_multiplier = 1.0 + speed_squared * 0.01
            
            # Calculate energy consumption
            energy_consumption = base_rate * activity_multiplier * delta_time
            
            # Apply energy change
            energy_component.change_energy(-energy_consumption)
        else:
            # Simple metabolism for other entities
            metabolism = getattr(entity, 'metabolism', 0.0)
            energy_component.change_energy(-metabolism * delta_time)
            
    def handle_eating(self, entity, resource):
        """
        Handle an entity eating a resource.
        
        Args:
            entity: Entity eating the resource
            resource: Resource being eaten
            
        Returns:
            float: Amount of energy gained
        """
        if not hasattr(entity, 'get_energy_component'):
            return 0.0
            
        # Get energy from resource
        resource_energy = resource.get_energy()
        
        # Apply energy gain to entity
        energy_component = entity.get_energy_component()
        
        # Apply efficiency factor if entity is a bot
        if hasattr(entity, 'is_bot') and entity.is_bot():
            genetic_component = entity.get_genetic_component()
            genes = genetic_component.get_all_genes()
            efficiency = genes['energy_efficiency']
            
            # Apply efficiency
            gained_energy = resource_energy * efficiency
        else:
            gained_energy = resource_energy
            
        # Add energy to entity
        energy_component.change_energy(gained_energy)
        
        return gained_energy
        
    def get_total_energy(self):
        """
        Get the total energy of all entities.
        
        Returns:
            float: Total energy
        """
        total = 0.0
        entities = self.entity_manager.get_all_entities()
        
        for entity in entities:
            if hasattr(entity, 'get_energy_component'):
                energy_component = entity.get_energy_component()
                total += energy_component.get_energy()
                
        return total
        
    def get_average_bot_energy(self):
        """
        Get the average energy of all bots.
        
        Returns:
            float: Average bot energy, or 0 if no bots
        """
        total = 0.0
        count = 0
        
        bots = self.entity_manager.get_all_bots()
        
        for bot in bots:
            energy_component = bot.get_energy_component()
            total += energy_component.get_energy()
            count += 1
            
        if count == 0:
            return 0.0
            
        return total / count
