"""
Bot entity module for defining the bot entity blueprint.
"""

import pygame
import random
import math
import uuid
import config
from components.position import PositionComponent
from components.velocity import VelocityComponent
from components.renderable import RenderableComponent
from components.energy import EnergyComponent
from components.sensor_suite import SensorSuiteComponent
from components.action import ActionComponent
from components.ai_state import AIStateComponent
from components.memory import MemoryComponent
from components.communicator import CommunicatorComponent
from components.genetics import GeneticComponent

class Bot:
    """
    Bot entity that combines multiple components to create an autonomous agent.
    """
    
    def __init__(self, position, genetics=None):
        """
        Initialize a bot entity.
        
        Args:
            position (tuple): Initial (x, y) position
            genetics (GeneticComponent, optional): Genetic component or None for random genetics
        """
        # Generate unique ID
        self.id = str(uuid.uuid4())[:8]
        
        # Create or use provided genetics
        self.genetic_component = genetics if genetics else GeneticComponent()
        self.genetic_component.set_entity_id(self.id)
        
        # Extract genetic traits
        genes = self.genetic_component.get_all_genes()
        traits = self.genetic_component.get_all_traits()
        
        # Create components
        self.position_component = PositionComponent(position[0], position[1])
        
        self.velocity_component = VelocityComponent(0, 0, genes["max_speed"])
        self.velocity_component.acceleration = genes["acceleration"]
        
        self.renderable_component = RenderableComponent(
            color=traits["color"],
            radius=traits["radius"],
            shape="circle"
        )
        
        self.energy_component = EnergyComponent(
            initial_energy=config.BOT_INITIAL_ENERGY,
            max_energy=genes["max_energy"],
            metabolism_rate=genes["metabolism_rate"]
        )
        self.energy_component.movement_cost_factor = traits["movement_cost_factor"]
        
        self.sensor_suite_component = SensorSuiteComponent(
            visual_range=genes["visual_range"],
            visual_angle=genes["visual_angle"],
            resource_detection_range=genes["resource_detection_range"],
            signal_detection_range=genes["signal_detection_range"]
        )
        self.sensor_suite_component.set_accuracies(
            genes["visual_accuracy"],
            genes["resource_accuracy"],
            genes["signal_accuracy"]
        )
        self.sensor_suite_component.owner = self
        
        self.action_component = ActionComponent()
        self.action_component.set_action_param("eat_efficiency", genes["eat_efficiency"])
        self.action_component.set_action_param("communication_range_multiplier", genes["communication_range"])
        self.action_component.set_action_param("reproduction_success_rate", genes["reproduction_rate"])
        self.action_component.set_action_param("attack_strength", genes["attack_strength"])
        
        self.ai_state_component = AIStateComponent()
        self.ai_state_component.set_personality({
            "aggression": genes["aggression"],
            "sociability": genes["sociability"],
            "curiosity": genes["curiosity"],
            "caution": genes["caution"]
        })
        self.ai_state_component.learning_rate = genes["learning_rate"]
        self.ai_state_component.exploration_rate = genes["exploration_rate"]
        
        self.memory_component = MemoryComponent(
            capacity=int(100 * genes["memory_capacity"])
        )
        
        self.communicator_component = CommunicatorComponent(
            range_multiplier=genes["communication_range"]
        )
        
        # Entity state
        self.age = 0
        self.alive = True
        self.maturity_age = config.BOT_MATURITY_AGE
        self.max_age = config.BOT_MAX_AGE * random.uniform(0.8, 1.2)
        self.reproduction_count = 0
        self.last_action_result = None
        
        # Unlock actions based on maturity
        self._update_available_actions()
        
    def update(self, delta_time, entity_manager, world_map):
        """
        Update the bot entity.
        
        Args:
            delta_time (float): Time delta in seconds
            entity_manager (EntityManager): Entity manager instance
            world_map (WorldMap): World map instance
            
        Returns:
            bool: True if entity is still alive
        """
        if not self.alive:
            return False
            
        # Increment age
        self.age += delta_time * config.FPS
        
        # Check for death by old age
        if self.age >= self.max_age:
            self.alive = False
            return False
            
        # Update energy (metabolism)
        if not self.energy_component.update(delta_time):
            # Death by starvation
            self.alive = False
            return False
            
        # Update components
        self.velocity_component.apply_friction()
        self.renderable_component.update(delta_time)
        self.communicator_component.update(delta_time)
        
        # Update sensor data
        direction = (
            math.cos(self.velocity_component.get_direction()),
            math.sin(self.velocity_component.get_direction())
        )
        self.sensor_suite_component.update(
            self.position_component,
            direction,
            entity_manager,
            world_map
        )
        
        # Update internal sensor readings
        self.sensor_suite_component.set_internal_sensors(
            self.energy_component.get_energy(),
            self.age
        )
        
        # Update memory
        self.memory_component.update(delta_time, self)
        
        # Update AI state
        self.ai_state_component.update(delta_time, self)
        
        # Update action component
        self.action_component.update(delta_time)
        
        # Check if actions need to be unlocked based on maturity
        self._update_available_actions()
        
        return True
    
    def make_decision(self, entity_manager, world_map):
        """
        Make a decision about what action to take.
        
        Args:
            entity_manager (EntityManager): Entity manager instance
            world_map (WorldMap): World map instance
            
        Returns:
            dict: Decision data
        """
        # Let AI component make decision
        decision = self.ai_state_component.make_decision(self, entity_manager, world_map)
        self.last_action_result = decision
        return decision
    
    def execute_action(self, entity_manager, world_map):
        """
        Execute the current action.
        
        Args:
            entity_manager (EntityManager): Entity manager instance
            world_map (WorldMap): World map instance
            
        Returns:
            dict: Action result
        """
        result = self.action_component.execute_current_action(self, entity_manager, world_map)
        
        # Track reproduction
        if result.get("success", False) and self.action_component.current_action == "reproduce":
            self.reproduction_count += 1
            
        return result
    
    def move(self, delta_time):
        """
        Move the bot based on current velocity.
        
        Args:
            delta_time (float): Time delta in seconds
            
        Returns:
            tuple: New position
        """
        # Get velocity
        velocity = self.velocity_component.get_velocity()
        
        # Apply movement
        self.position_component.move(
            velocity[0] * delta_time,
            velocity[1] * delta_time
        )
        
        # Update renderable rotation to match movement direction
        if velocity[0] != 0 or velocity[1] != 0:
            direction = math.atan2(velocity[1], velocity[0])
            self.renderable_component.set_rotation(direction)
            
        return self.position_component.get_position()
    
    def receive_signal(self, signal):
        """
        Process a received signal.
        
        Args:
            signal: Signal entity or data
            
        Returns:
            bool: True if signal was processed
        """
        return self.communicator_component.receive_signal(signal)
    
    def collide_with(self, other_entity):
        """
        Handle collision with another entity.
        
        Args:
            other_entity: Entity collided with
            
        Returns:
            dict: Collision result
        """
        # Basic collision response
        return {"type": "collision", "entity": other_entity}
    
    def _update_available_actions(self):
        """
        Update available actions based on maturity.
        """
        # Check if mature
        is_mature = self.age >= self.maturity_age
        
        # Unlock reproduction and communication when mature
        if is_mature:
            self.action_component.unlock_action("reproduce")
            self.action_component.unlock_action("communicate")
            
        # Unlock attack based on aggression and maturity
        aggression = self.ai_state_component.get_personality()["aggression"]
        if is_mature and aggression > 0.3:
            self.action_component.unlock_action("attack")
            
    def get_position_component(self):
        """
        Get the position component.
        
        Returns:
            PositionComponent: Position component
        """
        return self.position_component
    
    def get_velocity_component(self):
        """
        Get the velocity component.
        
        Returns:
            VelocityComponent: Velocity component
        """
        return self.velocity_component
    
    def get_renderable_component(self):
        """
        Get the renderable component.
        
        Returns:
            RenderableComponent: Renderable component
        """
        return self.renderable_component
    
    def get_energy_component(self):
        """
        Get the energy component.
        
        Returns:
            EnergyComponent: Energy component
        """
        return self.energy_component
    
    def get_sensor_suite_component(self):
        """
        Get the sensor suite component.
        
        Returns:
            SensorSuiteComponent: Sensor suite component
        """
        return self.sensor_suite_component
    
    def get_action_component(self):
        """
        Get the action component.
        
        Returns:
            ActionComponent: Action component
        """
        return self.action_component
    
    def get_ai_state_component(self):
        """
        Get the AI state component.
        
        Returns:
            AIStateComponent: AI state component
        """
        return self.ai_state_component
    
    def get_memory_component(self):
        """
        Get the memory component.
        
        Returns:
            MemoryComponent: Memory component
        """
        return self.memory_component
    
    def get_communicator_component(self):
        """
        Get the communicator component.
        
        Returns:
            CommunicatorComponent: Communicator component
        """
        return self.communicator_component
    
    def get_genetic_component(self):
        """
        Get the genetic component.
        
        Returns:
            GeneticComponent: Genetic component
        """
        return self.genetic_component
    
    def get_position(self):
        """
        Get the current position.
        
        Returns:
            tuple: (x, y) position
        """
        return self.position_component.get_position()
    
    def get_velocity(self):
        """
        Get the current velocity.
        
        Returns:
            tuple: (dx, dy) velocity
        """
        return self.velocity_component.get_velocity()
    
    def get_energy(self):
        """
        Get the current energy level.
        
        Returns:
            float: Energy level
        """
        return self.energy_component.get_energy()
    
    def get_age(self):
        """
        Get the current age.
        
        Returns:
            float: Age in updates
        """
        return self.age
    
    def get_radius(self):
        """
        Get the bot radius.
        
        Returns:
            float: Radius
        """
        return self.renderable_component.get_radius()
    
    def is_alive(self):
        """
        Check if the bot is alive.
        
        Returns:
            bool: True if alive
        """
        return self.alive
    
    def is_mature(self):
        """
        Check if the bot is mature.
        
        Returns:
            bool: True if mature
        """
        return self.age >= self.maturity_age
    
    def get_id(self):
        """
        Get the bot ID.
        
        Returns:
            str: Bot ID
        """
        return self.id
    
    def get_generation(self):
        """
        Get the bot generation.
        
        Returns:
            int: Generation number
        """
        return self.genetic_component.get_generation()
    
    def get_lineage_id(self):
        """
        Get the bot lineage ID.
        
        Returns:
            int: Lineage ID
        """
        return self.genetic_component.get_lineage_id()
    
    def get_reproduction_count(self):
        """
        Get the number of successful reproductions.
        
        Returns:
            int: Reproduction count
        """
        return self.reproduction_count
    
    def get_last_action_result(self):
        """
        Get the result of the last action.
        
        Returns:
            dict: Last action result
        """
        return self.last_action_result
    
    def get_stats(self):
        """
        Get comprehensive bot statistics.
        
        Returns:
            dict: Bot statistics
        """
        return {
            "id": self.id,
            "position": self.get_position(),
            "velocity": self.get_velocity(),
            "energy": self.get_energy(),
            "max_energy": self.energy_component.get_max_energy(),
            "age": self.age,
            "maturity_age": self.maturity_age,
            "max_age": self.max_age,
            "alive": self.alive,
            "generation": self.get_generation(),
            "lineage": self.get_lineage_id(),
            "reproduction_count": self.reproduction_count,
            "current_state": self.ai_state_component.get_current_state(),
            "current_action": self.action_component.get_current_action(),
            "needs": self.ai_state_component.get_needs(),
            "personality": self.ai_state_component.get_personality(),
            "memory_stats": self.memory_component.get_memory_stats(),
            "genetic_fitness": self.genetic_component.get_fitness_estimate()
        }
