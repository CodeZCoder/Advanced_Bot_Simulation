"""
Reinforcement learning system for bot decision making.
"""

import random
import math
import numpy as np
import config

class QLearning:
    """Q-Learning reinforcement learning algorithm."""
    
    def __init__(self, state_size, action_size, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.3):
        """
        Initialize the Q-Learning algorithm.
        
        Args:
            state_size (int): Number of possible states
            action_size (int): Number of possible actions
            learning_rate (float): Learning rate (alpha)
            discount_factor (float): Discount factor (gamma)
            exploration_rate (float): Exploration rate (epsilon)
        """
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = 0.995
        self.min_exploration_rate = 0.01
        
        # Initialize Q-table with small random values
        self.q_table = np.random.uniform(low=0, high=0.1, size=(state_size, action_size))
        
        # Track learning progress
        self.total_rewards = 0
        self.episode_count = 0
        self.update_count = 0
        
    def select_action(self, state):
        """
        Select an action using epsilon-greedy policy.
        
        Args:
            state (int): Current state
            
        Returns:
            int: Selected action
        """
        # Exploration: choose random action
        if random.random() < self.exploration_rate:
            return random.randint(0, self.action_size - 1)
            
        # Exploitation: choose best action
        return np.argmax(self.q_table[state])
    
    def update(self, state, action, reward, next_state):
        """
        Update Q-value using the Q-learning update rule.
        
        Args:
            state (int): Current state
            action (int): Action taken
            reward (float): Reward received
            next_state (int): Next state
        """
        # Q-learning update rule:
        # Q(s,a) = Q(s,a) + alpha * (reward + gamma * max(Q(s',a')) - Q(s,a))
        
        # Calculate target Q-value
        best_next_action = np.argmax(self.q_table[next_state])
        target_q = reward + self.discount_factor * self.q_table[next_state, best_next_action]
        
        # Update Q-value
        self.q_table[state, action] += self.learning_rate * (target_q - self.q_table[state, action])
        
        # Update tracking variables
        self.total_rewards += reward
        self.update_count += 1
        
    def end_episode(self):
        """End the current episode and update exploration rate."""
        self.episode_count += 1
        
        # Decay exploration rate
        self.exploration_rate = max(self.min_exploration_rate, 
                                   self.exploration_rate * self.exploration_decay)
        
    def get_best_action(self, state):
        """
        Get the best action for a state (no exploration).
        
        Args:
            state (int): Current state
            
        Returns:
            int: Best action
        """
        return np.argmax(self.q_table[state])
    
    def get_q_value(self, state, action):
        """
        Get the Q-value for a state-action pair.
        
        Args:
            state (int): State
            action (int): Action
            
        Returns:
            float: Q-value
        """
        return self.q_table[state, action]
    
    def set_learning_rate(self, learning_rate):
        """
        Set the learning rate.
        
        Args:
            learning_rate (float): New learning rate
        """
        self.learning_rate = max(0.01, min(1.0, learning_rate))
        
    def set_exploration_rate(self, exploration_rate):
        """
        Set the exploration rate.
        
        Args:
            exploration_rate (float): New exploration rate
        """
        self.exploration_rate = max(self.min_exploration_rate, min(1.0, exploration_rate))
        
    def get_stats(self):
        """
        Get learning statistics.
        
        Returns:
            dict: Learning statistics
        """
        return {
            "episodes": self.episode_count,
            "updates": self.update_count,
            "total_rewards": self.total_rewards,
            "average_reward": self.total_rewards / max(1, self.update_count),
            "exploration_rate": self.exploration_rate
        }


class StateDiscretizer:
    """Discretizes continuous state variables into discrete states."""
    
    def __init__(self, num_energy_levels=5, num_distance_levels=5, num_density_levels=3):
        """
        Initialize the state discretizer.
        
        Args:
            num_energy_levels (int): Number of energy level buckets
            num_distance_levels (int): Number of distance level buckets
            num_density_levels (int): Number of density level buckets
        """
        self.num_energy_levels = num_energy_levels
        self.num_distance_levels = num_distance_levels
        self.num_density_levels = num_density_levels
        
        # Calculate total number of possible states
        self.state_size = num_energy_levels * num_distance_levels * num_density_levels
        
    def get_state(self, entity, entity_manager, world_map):
        """
        Get the discrete state for an entity.
        
        Args:
            entity: The entity to get state for
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            int: Discrete state index
        """
        # Get entity components
        energy_component = entity.get_energy_component()
        sensor_component = entity.get_sensor_suite_component()
        
        # Get energy level (0 to num_energy_levels-1)
        energy_percentage = energy_component.get_energy_percentage()
        energy_level = min(self.num_energy_levels - 1, 
                          int(energy_percentage / 100 * self.num_energy_levels))
        
        # Get distance to nearest resource (0 to num_distance_levels-1)
        resources = sensor_component.get_perceived_resources()
        if resources:
            closest_resource = min(resources, key=lambda r: r["distance"])
            max_distance = sensor_component.resource_detection_range
            distance_ratio = min(1.0, closest_resource["distance"] / max_distance)
            distance_level = min(self.num_distance_levels - 1, 
                               int(distance_ratio * self.num_distance_levels))
        else:
            distance_level = self.num_distance_levels - 1  # Furthest level if no resources
            
        # Get entity density around bot (0 to num_density_levels-1)
        entities = sensor_component.get_perceived_entities()
        entity_count = len(entities)
        
        if entity_count == 0:
            density_level = 0  # No entities
        elif entity_count < 3:
            density_level = 1  # Few entities
        else:
            density_level = 2  # Many entities
            
        # Combine into single state index
        state = (energy_level * self.num_distance_levels * self.num_density_levels +
                distance_level * self.num_density_levels +
                density_level)
                
        return state


class RewardFunction:
    """Calculates rewards for reinforcement learning."""
    
    def __init__(self):
        """Initialize the reward function."""
        # Reward weights
        self.energy_gain_weight = 1.0
        self.energy_loss_weight = -0.5
        self.reproduction_weight = 5.0
        self.exploration_weight = 0.2
        self.communication_weight = 0.3
        self.idle_weight = -0.1
        
        # Previous state tracking
        self.previous_energy = {}
        self.previous_position = {}
        self.previous_reproduction_count = {}
        self.previous_explored_cells = {}
        
    def calculate_reward(self, entity, entity_manager, world_map, action_type):
        """
        Calculate reward for an entity's action.
        
        Args:
            entity: The entity to calculate reward for
            entity_manager: Entity manager instance
            world_map: World map instance
            action_type (str): Type of action performed
            
        Returns:
            float: Reward value
        """
        entity_id = entity.get_id()
        reward = 0.0
        
        # Get current state
        energy_component = entity.get_energy_component()
        current_energy = energy_component.get_energy()
        current_position = entity.get_position()
        current_reproduction_count = entity.get_reproduction_count()
        
        # Get memory component for exploration tracking
        memory_component = entity.get_memory_component()
        current_explored_cells = len(memory_component.location_familiarity)
        
        # Initialize previous state if not exists
        if entity_id not in self.previous_energy:
            self.previous_energy[entity_id] = current_energy
            self.previous_position[entity_id] = current_position
            self.previous_reproduction_count[entity_id] = current_reproduction_count
            self.previous_explored_cells[entity_id] = current_explored_cells
            return 0.0  # No reward for first update
            
        # Calculate energy change reward
        energy_change = current_energy - self.previous_energy[entity_id]
        if energy_change > 0:
            reward += energy_change * self.energy_gain_weight
        else:
            reward += energy_change * self.energy_loss_weight
            
        # Calculate reproduction reward
        reproduction_change = current_reproduction_count - self.previous_reproduction_count[entity_id]
        if reproduction_change > 0:
            reward += reproduction_change * self.reproduction_weight
            
        # Calculate exploration reward
        exploration_change = current_explored_cells - self.previous_explored_cells[entity_id]
        if exploration_change > 0:
            reward += exploration_change * self.exploration_weight
            
        # Action-specific rewards
        if action_type == "eat":
            # Additional reward for successful eating
            if energy_change > 0:
                reward += 1.0
        elif action_type == "reproduce":
            # Additional reward for successful reproduction
            if reproduction_change > 0:
                reward += 2.0
        elif action_type == "communicate":
            # Small reward for communication
            reward += self.communication_weight
        elif action_type == "idle":
            # Small penalty for idling
            reward += self.idle_weight
            
        # Update previous state
        self.previous_energy[entity_id] = current_energy
        self.previous_position[entity_id] = current_position
        self.previous_reproduction_count[entity_id] = current_reproduction_count
        self.previous_explored_cells[entity_id] = current_explored_cells
        
        return reward
    
    def reset_entity(self, entity_id):
        """
        Reset tracking for an entity.
        
        Args:
            entity_id: Entity ID to reset
        """
        if entity_id in self.previous_energy:
            del self.previous_energy[entity_id]
        if entity_id in self.previous_position:
            del self.previous_position[entity_id]
        if entity_id in self.previous_reproduction_count:
            del self.previous_reproduction_count[entity_id]
        if entity_id in self.previous_explored_cells:
            del self.previous_explored_cells[entity_id]


class ReinforcementLearningSystem:
    """Reinforcement learning system for bot decision making."""
    
    def __init__(self):
        """Initialize the reinforcement learning system."""
        # Define actions
        self.actions = [
            "move_to_resource",
            "eat_resource",
            "move_to_bot",
            "reproduce",
            "flee_danger",
            "emit_signal",
            "explore",
            "idle"
        ]
        self.action_size = len(self.actions)
        
        # Create state discretizer
        self.state_discretizer = StateDiscretizer()
        self.state_size = self.state_discretizer.state_size
        
        # Create reward function
        self.reward_function = RewardFunction()
        
        # Create Q-learning algorithm
        self.q_learning = QLearning(
            self.state_size,
            self.action_size,
            learning_rate=config.LEARNING_RATE,
            discount_factor=0.9,
            exploration_rate=config.EXPLORATION_RATE
        )
        
        # Track entity states
        self.entity_states = {}
        self.entity_actions = {}
        
    def select_action(self, entity, entity_manager, world_map):
        """
        Select an action for an entity.
        
        Args:
            entity: The entity to select action for
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            str: Selected action
        """
        entity_id = entity.get_id()
        
        # Get current state
        state = self.state_discretizer.get_state(entity, entity_manager, world_map)
        
        # Store current state
        self.entity_states[entity_id] = state
        
        # Select action using Q-learning
        action_index = self.q_learning.select_action(state)
        action = self.actions[action_index]
        
        # Store selected action
        self.entity_actions[entity_id] = action_index
        
        return action
    
    def update(self, entity, entity_manager, world_map, action_result):
        """
        Update the learning system based on action result.
        
        Args:
            entity: The entity that performed the action
            entity_manager: Entity manager instance
            world_map: World map instance
            action_result (dict): Result of the action
        """
        entity_id = entity.get_id()
        
        # Check if we have previous state and action
        if entity_id not in self.entity_states or entity_id not in self.entity_actions:
            return
            
        # Get previous state and action
        prev_state = self.entity_states[entity_id]
        action_index = self.entity_actions[entity_id]
        
        # Get current state
        current_state = self.state_discretizer.get_state(entity, entity_manager, world_map)
        
        # Calculate reward
        action_type = action_result.get("action", "unknown")
        reward = self.reward_function.calculate_reward(entity, entity_manager, world_map, action_type)
        
        # Update Q-learning
        self.q_learning.update(prev_state, action_index, reward, current_state)
        
        # Update entity state
        self.entity_states[entity_id] = current_state
        
    def end_episode(self, entity_id):
        """
        End an episode for an entity.
        
        Args:
            entity_id: Entity ID
        """
        # Reset entity tracking
        if entity_id in self.entity_states:
            del self.entity_states[entity_id]
        if entity_id in self.entity_actions:
            del self.entity_actions[entity_id]
            
        # Reset reward tracking
        self.reward_function.reset_entity(entity_id)
        
        # Update Q-learning
        self.q_learning.end_episode()
        
    def get_q_values(self, entity, entity_manager, world_map):
        """
        Get Q-values for current state.
        
        Args:
            entity: The entity to get Q-values for
            entity_manager: Entity<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>