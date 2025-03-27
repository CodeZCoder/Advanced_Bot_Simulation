"""
AI state component module for managing entity AI state.
"""

import random
import math
import config

class AIStateComponent:
    """
    Manages entity AI state, decision making, and behavior.
    """
    
    def __init__(self):
        """
        Initialize the AI state component.
        """
        # Current state
        self.current_state = "idle"
        self.previous_state = None
        self.state_duration = 0
        
        # Behavior tree state
        self.current_node = None
        self.node_stack = []
        
        # Goal-oriented action planning state
        self.current_goal = None
        self.current_plan = []
        self.world_state = {}
        
        # Utility AI state
        self.action_scores = {}
        self.needs = {
            "hunger": 0.5,  # 0 = full, 1 = starving
            "safety": 0.0,  # 0 = safe, 1 = threatened
            "reproduction": 0.0,  # 0 = no urge, 1 = strong urge
            "curiosity": 0.5,  # 0 = bored, 1 = curious
            "social": 0.3   # 0 = solitary, 1 = social
        }
        
        # Learning state
        self.learning_enabled = False
        self.learning_rate = config.LEARNING_RATE
        self.exploration_rate = config.EXPLORATION_RATE
        
        # Decision history
        self.decision_history = []
        
        # Personality traits (influence decision making)
        self.personality = {
            "aggression": random.uniform(0.0, 0.3),  # Low to moderate aggression
            "sociability": random.uniform(0.2, 0.8),
            "curiosity": random.uniform(0.3, 0.9),
            "caution": random.uniform(0.2, 0.8)
        }
        
    def update(self, delta_time, entity):
        """
        Update AI state.
        
        Args:
            delta_time (float): Time delta in seconds
            entity: The entity this component belongs to
        """
        # Update state duration
        self.state_duration += delta_time
        
        # Update needs based on entity state
        self._update_needs(entity)
        
        # Update exploration rate (decay over time)
        if self.learning_enabled:
            self.exploration_rate *= config.EXPLORATION_DECAY
            if self.exploration_rate < 0.01:
                self.exploration_rate = 0.01
                
    def _update_needs(self, entity):
        """
        Update internal needs based on entity state.
        
        Args:
            entity: The entity this component belongs to
        """
        # Update hunger based on energy
        energy_component = entity.get_energy_component()
        if energy_component:
            energy_percentage = energy_component.get_energy_percentage()
            self.needs["hunger"] = max(0, 1 - (energy_percentage / 100))
            
        # Update safety based on nearby entities
        sensor_component = entity.get_sensor_suite_component()
        if sensor_component:
            # Check for nearby entities
            perceived_entities = sensor_component.get_perceived_entities()
            threat_level = 0
            
            for perceived in perceived_entities:
                if perceived["type"] == "Bot" and perceived["distance"] < 50:
                    # Consider other bots potential threats
                    threat_level += 0.1 * (1 - (perceived["distance"] / 50))
                    
            self.needs["safety"] = min(1, threat_level)
            
            # Update reproduction urge based on energy and age
            if energy_percentage > 70 and entity.get_age() > config.BOT_MATURITY_AGE:
                self.needs["reproduction"] += 0.01
            else:
                self.needs["reproduction"] = max(0, self.needs["reproduction"] - 0.005)
                
            # Update curiosity based on unexplored areas
            # This is simplified - would be more complex in a full implementation
            if len(perceived_entities) == 0:
                self.needs["curiosity"] += 0.01
            else:
                self.needs["curiosity"] = max(0, self.needs["curiosity"] - 0.005)
                
            # Update social need based on nearby bots
            bot_count = sum(1 for p in perceived_entities if p["type"] == "Bot")
            if bot_count == 0:
                self.needs["social"] += 0.005 * self.personality["sociability"]
            else:
                ideal_bots = 2 * self.personality["sociability"]
                if bot_count < ideal_bots:
                    self.needs["social"] += 0.005
                else:
                    self.needs["social"] = max(0, self.needs["social"] - 0.01)
                    
    def make_decision(self, entity, entity_manager, world_map):
        """
        Make a decision about what action to take.
        
        Args:
            entity: The entity this component belongs to
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            dict: Decision data
        """
        # Get components
        action_component = entity.get_action_component()
        sensor_component = entity.get_sensor_suite_component()
        energy_component = entity.get_energy_component()
        memory_component = entity.get_memory_component()
        
        # Check if current action is still in progress
        current_action = action_component.get_current_action()
        if current_action:
            return {"action": current_action["type"], "continue": True}
            
        # Use utility AI to score possible actions
        self._calculate_action_scores(entity)
        
        # Apply exploration for learning
        if self.learning_enabled and random.random() < self.exploration_rate:
            # Choose a random action for exploration
            available_actions = [a for a in action_component.available_actions 
                               if action_component.available_actions[a] and 
                               not action_component.is_action_on_cooldown(a)]
            
            if available_actions:
                chosen_action = random.choice(available_actions)
                return self._execute_action(chosen_action, entity, entity_manager, world_map)
                
        # Choose action with highest score
        best_action = max(self.action_scores.items(), key=lambda x: x[1])
        action_type = best_action[0]
        
        # Execute the chosen action
        result = self._execute_action(action_type, entity, entity_manager, world_map)
        
        # Record decision
        self.decision_history.append({
            "action": action_type,
            "scores": self.action_scores.copy(),
            "needs": self.needs.copy(),
            "result": result
        })
        if len(self.decision_history) > 20:
            self.decision_history.pop(0)
            
        # Update state
        self.previous_state = self.current_state
        self.current_state = action_type
        self.state_duration = 0
        
        return result
    
    def _calculate_action_scores(self, entity):
        """
        Calculate utility scores for all possible actions.
        
        Args:
            entity: The entity this component belongs to
        """
        # Get components
        action_component = entity.get_action_component()
        sensor_component = entity.get_sensor_suite_component()
        energy_component = entity.get_energy_component()
        
        # Reset scores
        self.action_scores = {
            "move": 0,
            "eat": 0,
            "communicate": 0,
            "reproduce": 0,
            "attack": 0,
            "idle": 0.1  # Small base score for idle
        }
        
        # Only consider available actions not on cooldown
        for action in self.action_scores:
            if not action_component.is_action_available(action) or action_component.is_action_on_cooldown(action):
                self.action_scores[action] = -1  # Not available
                
        # Calculate move score
        # Higher when curious or when resources/threats are detected
        move_score = self.needs["curiosity"] * 0.5
        
        # If hungry, prioritize moving toward food
        if self.needs["hunger"] > 0.5:
            closest_resource = sensor_component.get_closest_resource()
            if closest_resource:
                # Increase score based on hunger and proximity
                move_score += self.needs["hunger"] * (1 - min(1, closest_resource["distance"] / 200))
                
        # If threatened, move away from threats
        if self.needs["safety"] > 0.3:
            move_score += self.needs["safety"] * 0.7
            
        # If social need is high, move toward other bots
        if self.needs["social"] > 0.7:
            closest_bot = sensor_component.get_closest_entity("Bot")
            if closest_bot:
                move_score += self.needs["social"] * 0.3 * (1 - min(1, closest_bot["distance"] / 150))
                
        self.action_scores["move"] = move_score
        
        # Calculate eat score
        # Higher when hungry and food is nearby
        eat_score = 0
        if self.needs["hunger"] > 0.3:
            closest_resource = sensor_component.get_closest_resource()
            if closest_resource and closest_resource["distance"] < 50:
                # Higher score for closer food and higher hunger
                eat_score = self.needs["hunger"] * (1 - closest_resource["distance"] / 50)
                
        self.action_scores["eat"] = eat_score
        
        # Calculate communicate score
        # Higher when social need is high or threats detected
        communicate_score = 0
        if self.needs["social"] > 0.5:
            communicate_score = self.needs["social"] * 0.3
            
        # Increase if danger detected to warn others
        if self.needs["safety"] > 0.6:
            communicate_score += self.needs["safety"] * 0.4
            
        self.action_scores["communicate"] = communicate_score
        
        # Calculate reproduce score
        # Higher when reproduction need is high and energy is sufficient
        reproduce_score = 0
        if self.needs["reproduction"] > 0.7 and energy_component.get_energy_percentage() > 60:
            reproduce_score = self.needs["reproduction"] * 0.8
            
            # Check for potential mates
            closest_bot = sensor_component.get_closest_entity("Bot")
            if closest_bot and closest_bot["distance"] < 100:
                reproduce_score *= (1 - closest_bot["distance"] / 100)
            else:
                reproduce_score *= 0.3  # Reduce if no mates nearby
                
        self.action_scores["reproduce"] = reproduce_score
        
        # Calculate attack score
        # Higher with high aggression and when threatened
        attack_score = 0
        if self.personality["aggression"] > 0.5 and self.needs["safety"] > 0.7:
            attack_score = self.personality["aggression"] * self.needs["safety"] * 0.6
            
        self.action_scores["attack"] = attack_score
        
        # Calculate idle score
        # Higher when all needs are satisfied
        idle_score = 0.1  # Base score
        if (self.needs["hunger"] < 0.3 and 
            self.needs["safety"] < 0.2 and 
            self.needs["reproduction"] < 0.5 and
            self.needs["curiosity"] < 0.4):
            idle_score = 0.5  # Significant score when all needs low
            
        self.action_scores["idle"] = idle_score
        
    def _execute_action(self, action_type, entity, entity_manager, world_map):
        """
        Execute a chosen action.
        
        Args:
            action_type (str): Type of action
            entity: The entity this component belongs to
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            dict: Action result
        """
        # Get components
        action_component = entity.get_action_component()
        sensor_component = entity.get_sensor_suite_component()
        position_component = entity.get_position_component()
        
        if action_type == "move":
            # Determine move target
            target = None
            
            if self.needs["hunger"] > 0.6:
                # Move toward food if hungry
                closest_resource = sensor_component.get_closest_resource()
                if closest_resource:
                    target = closest_resource["position"]
            elif self.needs["safety"] > 0.6:
                # Move away from threats if threatened
                closest_threat = sensor_component.get_closest_entity("Bot")
                if closest_threat:
                    # Calculate position away from threat
                    threat_pos = closest_threat["position"]
                    current_pos = position_component.get_position()
                    away_vector = (
                        current_pos[0] - threat_pos[0],
                        current_pos[1] - threat_pos[1]
                    )
                    # Normalize and extend
                    mag = math.sqrt(away_vector[0]**2 + away_vector[1]**2)
                    if mag > 0:
                        away_vector = (
                            current_pos[0] + (away_vector[0] / mag) * 100,
                            current_pos[1] + (away_vector[1] / mag) * 100
                        )
                        target = away_vector
            elif self.needs["social"] > 0.7:
                # Move toward other bots if social
                closest_bot = sensor_component.get_closest_entity("Bot")
                if closest_bot:
                    target = closest_bot["position"]
            
            if not target:
                # Random exploration
                current_pos = position_component.get_position()
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(50, 200)
                target = (
                    current_pos[0] + math.cos(angle) * distance,
                    current_pos[1] + math.sin(angle) * distance
                )
                
                # Ensure target is within world bounds
                world_bounds = world_map.get_bounds()
                target = (
                    max(0, min(world_bounds.width, target[0])),
                    max(0, min(world_bounds.height, target[1]))
                )
                
            # Queue the move action
            action_component.queue_action("move", target, None, 1.0)
            return {"action": "move", "target": target}
            
        elif action_type == "eat":
            # Find closest resource
            closest_resource = sensor_component.get_closest_resource()
            if closest_resource:
                # Queue the eat action
                action_component.queue_action("eat", closest_resource["resource"], None, 0.5)
                return {"action": "eat", "target": closest_resource["resource"]}
            else:
                # Fallback to move if no resources found
                return self._execute_action("move", entity, entity_manager, world_map)
                
        elif action_type == "communicate":
            # Determine signal type based on needs
            signal_type = 1  # Default: general signal
            signal_data = None
            
            if self.needs["safety"] > 0.6:
                signal_type = 1  # Danger
                signal_data = {"position": position_component.get_position()}
            elif self.needs["hunger"] < 0.3:
                signal_type = 2  # Food
                # Include nearby resource positions if any
                resources = sensor_component.get_perceived_resources()
                if resources:
                    signal_data = {"position": resources[0]["position"]}
            eli<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>