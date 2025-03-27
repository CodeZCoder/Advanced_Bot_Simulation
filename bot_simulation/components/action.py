"""
Action component module for defining entity capabilities and actions.
"""

import math
import random
import config

class ActionComponent:
    """
    Defines an entity's action capabilities and manages action execution.
    """
    
    def __init__(self):
        """
        Initialize the action component.
        """
        # Available actions
        self.available_actions = {
            "move": True,
            "eat": True,
            "communicate": False,  # Unlocked with maturity
            "reproduce": False,    # Unlocked with maturity
            "attack": False,       # Unlocked with maturity
            "idle": True
        }
        
        # Action cooldowns (in updates)
        self.action_cooldowns = {
            "move": 0,
            "eat": 10,
            "communicate": 50,
            "reproduce": 200,
            "attack": 30,
            "idle": 0
        }
        
        # Current cooldown timers
        self.cooldown_timers = {
            "move": 0,
            "eat": 0,
            "communicate": 0,
            "reproduce": 0,
            "attack": 0,
            "idle": 0
        }
        
        # Action parameters
        self.action_params = {
            "move_speed_multiplier": 1.0,
            "eat_efficiency": 0.8,
            "communication_range_multiplier": 1.0,
            "reproduction_success_rate": 0.7,
            "attack_strength": 0.5
        }
        
        # Current action
        self.current_action = None
        self.current_action_target = None
        self.current_action_data = None
        self.current_action_progress = 0
        self.current_action_duration = 0
        
        # Action history
        self.action_history = []
        self.action_counts = {
            "move": 0,
            "eat": 0,
            "communicate": 0,
            "reproduce": 0,
            "attack": 0,
            "idle": 0
        }
        
    def update(self, delta_time):
        """
        Update action state and cooldowns.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Update cooldown timers
        for action in self.cooldown_timers:
            if self.cooldown_timers[action] > 0:
                self.cooldown_timers[action] -= delta_time
                if self.cooldown_timers[action] < 0:
                    self.cooldown_timers[action] = 0
                    
        # Update current action progress
        if self.current_action:
            self.current_action_progress += delta_time
            
            # Check if action is complete
            if self.current_action_progress >= self.current_action_duration:
                self.current_action = None
                self.current_action_target = None
                self.current_action_data = None
                self.current_action_progress = 0
                self.current_action_duration = 0
                
    def queue_action(self, action_type, target=None, data=None, duration=1.0):
        """
        Queue an action for execution.
        
        Args:
            action_type (str): Type of action
            target: Target entity or position
            data: Additional action data
            duration (float): Action duration in seconds
            
        Returns:
            bool: True if action was queued successfully
        """
        # Check if action is available
        if not self.is_action_available(action_type):
            return False
            
        # Check if action is on cooldown
        if self.is_action_on_cooldown(action_type):
            return False
            
        # Set current action
        self.current_action = action_type
        self.current_action_target = target
        self.current_action_data = data
        self.current_action_progress = 0
        self.current_action_duration = duration
        
        # Start cooldown
        self.cooldown_timers[action_type] = self.action_cooldowns[action_type]
        
        # Update action count
        self.action_counts[action_type] += 1
        
        # Add to history (keep last 10 actions)
        self.action_history.append({
            "type": action_type,
            "target": target,
            "data": data
        })
        if len(self.action_history) > 10:
            self.action_history.pop(0)
            
        return True
    
    def execute_current_action(self, entity, entity_manager, world_map):
        """
        Execute the current action.
        
        Args:
            entity: The entity performing the action
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            dict: Action result data
        """
        if not self.current_action:
            return {"success": False, "reason": "No action queued"}
            
        # Execute based on action type
        if self.current_action == "move":
            return self._execute_move(entity)
        elif self.current_action == "eat":
            return self._execute_eat(entity, entity_manager)
        elif self.current_action == "communicate":
            return self._execute_communicate(entity, entity_manager)
        elif self.current_action == "reproduce":
            return self._execute_reproduce(entity, entity_manager, world_map)
        elif self.current_action == "attack":
            return self._execute_attack(entity, entity_manager)
        elif self.current_action == "idle":
            return self._execute_idle(entity)
        else:
            return {"success": False, "reason": "Unknown action type"}
            
    def _execute_move(self, entity):
        """
        Execute move action.
        
        Args:
            entity: The entity performing the action
            
        Returns:
            dict: Action result data
        """
        # Get target position
        target = self.current_action_target
        if not target:
            return {"success": False, "reason": "No target position"}
            
        # Get entity components
        position_component = entity.get_position_component()
        velocity_component = entity.get_velocity_component()
        energy_component = entity.get_energy_component()
        
        # Calculate direction to target
        if isinstance(target, tuple):
            target_position = target
        else:
            # Assume target is an entity with position
            target_position = target.get_position_component().get_position()
            
        # Calculate direction
        direction = position_component.direction_to(target_position)
        
        # Apply movement
        speed = velocity_component.get_speed()
        if speed == 0:
            # If not moving, start moving
            acceleration = self.action_params["move_speed_multiplier"] * config.BOT_ACCELERATION
            velocity_component.accelerate_towards(target_position, acceleration, position_component)
        else:
            # Already moving, adjust direction
            velocity_component.accelerate_towards(target_position, 
                                                config.BOT_ACCELERATION * 0.5, 
                                                position_component)
            
        # Calculate energy cost based on acceleration
        energy_cost = energy_component.calculate_movement_cost(velocity_component.get_speed() * 0.1)
        energy_component.consume_energy(energy_cost)
        
        return {
            "success": True,
            "target": target_position,
            "direction": direction,
            "energy_cost": energy_cost
        }
        
    def _execute_eat(self, entity, entity_manager):
        """
        Execute eat action.
        
        Args:
            entity: The entity performing the action
            entity_manager: Entity manager instance
            
        Returns:
            dict: Action result data
        """
        # Get target resource
        target = self.current_action_target
        if not target:
            return {"success": False, "reason": "No target resource"}
            
        # Get entity components
        position_component = entity.get_position_component()
        energy_component = entity.get_energy_component()
        
        # Check if resource still exists
        resources = entity_manager.get_all_resources()
        if target not in resources:
            return {"success": False, "reason": "Resource no longer exists"}
            
        # Check if close enough to eat
        resource_position = target.get_position()
        distance = position_component.distance_to(resource_position)
        
        if distance > entity.get_radius() + config.RESOURCE_RADIUS:
            return {"success": False, "reason": "Too far from resource"}
            
        # Consume the resource
        resource_energy = target.get_energy()
        gained_energy = resource_energy * self.action_params["eat_efficiency"]
        
        # Add energy to entity
        actual_gained = energy_component.add_energy(gained_energy)
        
        # Remove resource
        entity_manager.remove_resource(target)
        
        # Apply eating cost
        energy_cost = energy_component.get_action_cost("eat")
        energy_component.consume_energy(energy_cost)
        
        return {
            "success": True,
            "resource": target,
            "energy_gained": actual_gained,
            "energy_cost": energy_cost
        }
        
    def _execute_communicate(self, entity, entity_manager):
        """
        Execute communicate action.
        
        Args:
            entity: The entity performing the action
            entity_manager: Entity manager instance
            
        Returns:
            dict: Action result data
        """
        # Get communication data
        signal_type = self.current_action_data.get("type") if self.current_action_data else 1
        signal_data = self.current_action_data.get("data") if self.current_action_data else None
        
        # Get entity components
        position_component = entity.get_position_component()
        energy_component = entity.get_energy_component()
        communicator_component = entity.get_communicator_component()
        
        # Check if entity has communicator component
        if not communicator_component:
            return {"success": False, "reason": "No communicator component"}
            
        # Apply communication cost
        energy_cost = energy_component.get_action_cost("communicate")
        if not energy_component.consume_energy(energy_cost):
            return {"success": False, "reason": "Not enough energy"}
            
        # Create and emit signal
        signal_range = config.SIGNAL_DETECTION_RANGE * self.action_params["communication_range_multiplier"]
        success = communicator_component.emit_signal(signal_type, signal_data, entity, signal_range, entity_manager)
        
        return {
            "success": success,
            "signal_type": signal_type,
            "signal_data": signal_data,
            "energy_cost": energy_cost
        }
        
    def _execute_reproduce(self, entity, entity_manager, world_map):
        """
        Execute reproduce action.
        
        Args:
            entity: The entity performing the action
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            dict: Action result data
        """
        # Get target mate
        target = self.current_action_target
        
        # Get entity components
        position_component = entity.get_position_component()
        energy_component = entity.get_energy_component()
        genetic_component = entity.get_genetic_component()
        
        # Check if entity has genetic component
        if not genetic_component:
            return {"success": False, "reason": "No genetic component"}
            
        # Check if entity has enough energy
        reproduction_cost = energy_component.get_action_cost("reproduce")
        if not energy_component.consume_energy(reproduction_cost):
            return {"success": False, "reason": "Not enough energy"}
            
        # Check reproduction success rate
        if random.random() > self.action_params["reproduction_success_rate"]:
            return {"success": False, "reason": "Reproduction failed", "energy_cost": reproduction_cost}
            
        # Determine reproduction type (sexual or asexual)
        if target:
            # Sexual reproduction
            # Check if target is a bot
            bots = entity_manager.get_all_bots()
            if target not in bots:
                return {"success": False, "reason": "Target is not a valid mate", "energy_cost": reproduction_cost}
                
            # Check if close enough to mate
            target_position = target.get_position_component().get_position()
            distance = position_component.distance_to(target_position)
            
            if distance > entity.get_radius() + target.get_radius() + 5:
                return {"success": False, "reason": "Too far from mate", "energy_cost": reproduction_cost}
                
            # Check if target has enough energy
            target_energy = target.get_energy_component()
            if not target_energy.consume_energy(reproduction_cost * 0.5):
                return {"success": False, "reason": "Mate doesn't have enough energy", "energy_cost": reproduction_cost}
                
            # Create offspring with combined genetics
            target_genetic = target.get_genetic_component()
            offspring_genetics = genetic_component.combine_with(target_genetic)
            
            # Get position for offspring (between parents)
            parent_pos = position_component.get_position()
            target_pos = target_position
            offspring_pos = (
                (parent_pos[0] + target_pos[0]) / 2 + random.uniform(-10, 10),
                (parent_pos[1] + target_pos[1]) / 2 + random.uniform(-10, 10)
            )
            
            # Ensure position is valid
            if not world_map.is_position_valid(offspring_pos, config.BOT_RADIUS_MIN):
                # Try to find a nearby valid position
                for _ in range(10):
                    test_pos = (
                        parent_pos[0] + random.uniform(-20, 20),
                        parent_pos[1] + random.uniform(-20, 20)
                    )
                    if world_map.is_position_valid(test_pos, config.BOT_RADIUS_MIN):
                        offspring_pos = test_pos
                        break
                else:
                    # Couldn't find valid position
                    return {"success": False, "reason": "No valid position for offspring", "energy_cost": reproduction_cost}
                    
            # Create offspring
            from entities.bot import Bot
            offspring = Bot(offspring_pos, offspring_genetics)
            entity_manager.add_bot(offspring)
            
            # Increment generation counter
            entity_manager.increment_generation()
            
            return {
                "success": True,
                "reproduction_type": "sexual",
                "mate": target,
                "offspring": offspring,
                "energy_cost": reproduction_cost
            }
        else:
            # Asexual reproduction
            # Create offspring with mutated genetics
            offspring_genetics = genetic_component.clone_with_mutation()
            
            # Get position for offspring (near parent)
            parent_pos = position_component.get_position()
            offspring_pos = (
                parent_pos[0] + random.uniform(-20, 20),
                parent_pos[1] + random.uniform(-20, 20)
            )
       <response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>