"""
AI system for bot simulation.
"""

import random
import math
import config
from ai.decision_making.behavior_tree import BehaviorTree, Selector, Sequence, Condition, Action
from ai.decision_making.utility_ai import UtilityAI
from ai.decision_making.goap import GOAPPlanner
from ai.learning.reinforcement_learning import QLearning
from ai.pathfinding.astar import AStar

class AISystem:
    """System for handling entity AI and decision making."""
    
    def __init__(self, entity_manager, world_map, communication_system, energy_system, evolution_system):
        """
        Initialize the AI system.
        
        Args:
            entity_manager: Entity manager instance
            world_map: World map instance
            communication_system: Communication system instance
            energy_system: Energy system instance
            evolution_system: Evolution system instance
        """
        self.entity_manager = entity_manager
        self.world_map = world_map
        self.communication_system = communication_system
        self.energy_system = energy_system
        self.evolution_system = evolution_system
        
        # Pathfinding
        self.pathfinder = AStar(world_map)
        
        # AI type distribution
        self.ai_types = {
            "behavior_tree": 0.4,  # 40% of bots use behavior trees
            "utility_ai": 0.3,     # 30% of bots use utility AI
            "goap": 0.3            # 30% of bots use GOAP
        }
        
        # Learning system instances (one per bot)
        self.learning_systems = {}
        
    def update(self, delta_time):
        """
        Update AI for all entities.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Get all entities with AI components
        entities = self.entity_manager.get_all_entities()
        ai_entities = []
        
        for entity in entities:
            if hasattr(entity, 'get_ai_state_component'):
                ai_entities.append(entity)
                
        # Update AI for each entity
        for entity in ai_entities:
            self._update_entity_ai(entity, delta_time)
            
    def _update_entity_ai(self, entity, delta_time):
        """
        Update AI for a single entity.
        
        Args:
            entity: Entity to update
            delta_time (float): Time delta in seconds
        """
        # Get components
        ai_state_component = entity.get_ai_state_component()
        
        # Check if entity has an AI type assigned
        if not hasattr(entity, 'ai_type'):
            # Assign AI type based on distribution
            rand = random.random()
            if rand < self.ai_types["behavior_tree"]:
                entity.ai_type = "behavior_tree"
                self._setup_behavior_tree(entity)
            elif rand < self.ai_types["behavior_tree"] + self.ai_types["utility_ai"]:
                entity.ai_type = "utility_ai"
                self._setup_utility_ai(entity)
            else:
                entity.ai_type = "goap"
                self._setup_goap(entity)
                
        # Update based on AI type
        if entity.ai_type == "behavior_tree":
            self._update_behavior_tree(entity, delta_time)
        elif entity.ai_type == "utility_ai":
            self._update_utility_ai(entity, delta_time)
        elif entity.ai_type == "goap":
            self._update_goap(entity, delta_time)
            
        # Update learning system if entity has one
        if entity.get_id() in self.learning_systems:
            self._update_learning(entity, delta_time)
            
    def _setup_behavior_tree(self, entity):
        """
        Set up behavior tree for an entity.
        
        Args:
            entity: Entity to set up behavior tree for
        """
        # Create behavior tree
        tree = BehaviorTree()
        
        # Create root selector
        root = Selector("Root")
        
        # Create main branches
        survive_branch = Sequence("Survive")
        reproduce_branch = Sequence("Reproduce")
        explore_branch = Sequence("Explore")
        
        # Survive branch
        is_low_energy = Condition("IsLowEnergy", lambda: self._check_low_energy(entity))
        find_food = Sequence("FindFood")
        is_food_visible = Condition("IsFoodVisible", lambda: self._check_food_visible(entity))
        move_to_food = Action("MoveToFood", lambda: self._move_to_food(entity))
        eat_food = Action("EatFood", lambda: self._eat_food(entity))
        
        find_food.add_child(is_food_visible)
        find_food.add_child(move_to_food)
        find_food.add_child(eat_food)
        
        wander_for_food = Action("WanderForFood", lambda: self._wander_for_food(entity))
        
        survive_branch.add_child(is_low_energy)
        survive_branch.add_child(Selector("FindFoodStrategy").add_child(find_food).add_child(wander_for_food))
        
        # Reproduce branch
        is_mature = Condition("IsMature", lambda: entity.is_mature())
        has_enough_energy = Condition("HasEnoughEnergy", lambda: self._check_reproduction_energy(entity))
        find_mate = Sequence("FindMate")
        is_mate_visible = Condition("IsMateVisible", lambda: self._check_mate_visible(entity))
        move_to_mate = Action("MoveToMate", lambda: self._move_to_mate(entity))
        reproduce = Action("Reproduce", lambda: self._reproduce(entity))
        
        find_mate.add_child(is_mate_visible)
        find_mate.add_child(move_to_mate)
        find_mate.add_child(reproduce)
        
        signal_for_mate = Action("SignalForMate", lambda: self._signal_for_mate(entity))
        
        reproduce_branch.add_child(is_mature)
        reproduce_branch.add_child(has_enough_energy)
        reproduce_branch.add_child(Selector("FindMateStrategy").add_child(find_mate).add_child(signal_for_mate))
        
        # Explore branch
        wander = Action("Wander", lambda: self._wander(entity))
        explore_branch.add_child(wander)
        
        # Add branches to root
        root.add_child(survive_branch)
        root.add_child(reproduce_branch)
        root.add_child(explore_branch)
        
        # Set root
        tree.set_root(root)
        
        # Store tree in entity
        entity.behavior_tree = tree
        
    def _update_behavior_tree(self, entity, delta_time):
        """
        Update behavior tree for an entity.
        
        Args:
            entity: Entity to update behavior tree for
            delta_time (float): Time delta in seconds
        """
        # Get behavior tree
        tree = entity.behavior_tree
        
        # Update tree
        tree.update()
        
    def _setup_utility_ai(self, entity):
        """
        Set up utility AI for an entity.
        
        Args:
            entity: Entity to set up utility AI for
        """
        # Create utility AI
        utility_ai = UtilityAI()
        
        # Add actions
        utility_ai.add_action("eat", self._eat_food, [
            ("hunger", lambda: self._get_hunger_score(entity), 0.8),
            ("food_proximity", lambda: self._get_food_proximity_score(entity), 0.6)
        ])
        
        utility_ai.add_action("wander_for_food", self._wander_for_food, [
            ("hunger", lambda: self._get_hunger_score(entity), 0.7),
            ("no_food_visible", lambda: 1.0 if not self._check_food_visible(entity) else 0.0, 0.5)
        ])
        
        utility_ai.add_action("reproduce", self._reproduce, [
            ("maturity", lambda: 1.0 if entity.is_mature() else 0.0, 1.0),
            ("energy_surplus", lambda: self._get_energy_surplus_score(entity), 0.7),
            ("mate_proximity", lambda: self._get_mate_proximity_score(entity), 0.8)
        ])
        
        utility_ai.add_action("move_to_mate", self._move_to_mate, [
            ("maturity", lambda: 1.0 if entity.is_mature() else 0.0, 1.0),
            ("energy_surplus", lambda: self._get_energy_surplus_score(entity), 0.6),
            ("mate_visible", lambda: 1.0 if self._check_mate_visible(entity) else 0.0, 0.9),
            ("not_at_mate", lambda: 1.0 if not self._check_at_mate(entity) else 0.0, 0.9)
        ])
        
        utility_ai.add_action("signal_for_mate", self._signal_for_mate, [
            ("maturity", lambda: 1.0 if entity.is_mature() else 0.0, 1.0),
            ("energy_surplus", lambda: self._get_energy_surplus_score(entity), 0.6),
            ("no_mate_visible", lambda: 1.0 if not self._check_mate_visible(entity) else 0.0, 0.7)
        ])
        
        utility_ai.add_action("wander", self._wander, [
            ("boredom", lambda: 0.3, 0.3),
            ("energy_ok", lambda: 1.0 - self._get_hunger_score(entity), 0.4)
        ])
        
        # Store utility AI in entity
        entity.utility_ai = utility_ai
        
    def _update_utility_ai(self, entity, delta_time):
        """
        Update utility AI for an entity.
        
        Args:
            entity: Entity to update utility AI for
            delta_time (float): Time delta in seconds
        """
        # Get utility AI
        utility_ai = entity.utility_ai
        
        # Update AI
        utility_ai.update()
        
    def _setup_goap(self, entity):
        """
        Set up GOAP for an entity.
        
        Args:
            entity: Entity to set up GOAP for
        """
        # Create GOAP planner
        planner = GOAPPlanner()
        
        # Define world state predicates
        planner.add_predicate("has_energy", lambda: not self._check_low_energy(entity))
        planner.add_predicate("food_visible", self._check_food_visible)
        planner.add_predicate("at_food", self._check_at_food)
        planner.add_predicate("is_mature", entity.is_mature)
        planner.add_predicate("has_reproduction_energy", self._check_reproduction_energy)
        planner.add_predicate("mate_visible", self._check_mate_visible)
        planner.add_predicate("at_mate", self._check_at_mate)
        
        # Define actions
        planner.add_action("move_to_food", 
            preconditions={"food_visible": True, "at_food": False},
            effects={"at_food": True},
            cost=5,
            action=lambda: self._move_to_food(entity)
        )
        
        planner.add_action("eat_food",
            preconditions={"at_food": True},
            effects={"has_energy": True},
            cost=1,
            action=lambda: self._eat_food(entity)
        )
        
        planner.add_action("wander_for_food",
            preconditions={"food_visible": False, "has_energy": False},
            effects={"food_visible": True},
            cost=10,
            action=lambda: self._wander_for_food(entity)
        )
        
        planner.add_action("move_to_mate",
            preconditions={"is_mature": True, "has_reproduction_energy": True, "mate_visible": True, "at_mate": False},
            effects={"at_mate": True},
            cost=5,
            action=lambda: self._move_to_mate(entity)
        )
        
        planner.add_action("reproduce",
            preconditions={"is_mature": True, "has_reproduction_energy": True, "at_mate": True},
            effects={},  # No specific effects, but high priority goal
            cost=1,
            action=lambda: self._reproduce(entity)
        )
        
        planner.add_action("signal_for_mate",
            preconditions={"is_mature": True, "has_reproduction_energy": True, "mate_visible": False},
            effects={"mate_visible": True},
            cost=3,
            action=lambda: self._signal_for_mate(entity)
        )
        
        planner.add_action("wander",
            preconditions={"has_energy": True},
            effects={},  # No specific effects, just a fallback
            cost=1,
            action=lambda: self._wander(entity)
        )
        
        # Define goals
        planner.add_goal("survive", {"has_energy": True}, priority=10)
        planner.add_goal("reproduce", {"is_mature": True, "has_reproduction_energy": True, "at_mate": True}, priority=5)
        planner.add_goal("explore", {}, priority=1)  # Empty goal, lowest priority
        
        # Store planner in entity
        entity.goap_planner = planner
        entity.current_plan = None
        entity.current_action_index = 0
        
    def _update_goap(self, entity, delta_time):
        """
        Update GOAP for an entity.
        
        Args:
            entity: Entity to update GOAP for
            delta_time (float): Time delta in seconds
        """
        # Get GOAP planner
        planner = entity.goap_planner
        
        # Check if we need a new plan
        if entity.current_plan is None or entity.current_action_index >= len(entity.current_plan):
            # Generate new plan
            entity.current_plan = planner.plan()
            entity.current_action_index = 0
            
        # Execute current action if we have a plan
        if entity.current_plan and entity.current_action_index < len(entity.current_plan):
            action = entity.current_plan[entity.current_action_index]
            result = action()
            
            # Move to next action if current one succeeded
            if result:
                entity.current_action_index += 1
                
    def _setup_learning(self, entity):
        """
        Set up learning system for an entity.
        
        Args:
            entity: Entity to set up learning for
        """
        # Get genetic component to extract learning parameters
        genetic_component = entity.get_genetic_component()
        genes = genetic_component.get_all_genes()
        
        # Extract learning parameters
        learning_rate = genes.get('learning_rate', 0.1)
        discount_factor = genes.get('discount_factor', 0.9)
        exploration_rate = genes.get('exploration_rate', 0.2)
        
        # Create Q-learning system
        q_learning = QLearning(
            learning_rate=learning_rate,
            discount_factor=discount_factor,
            exploration_rate=exploration_rate
        )
        
        # Define states
        # State is a tuple of (energy_level, food_visible, mate_visible)
        # energy_level: 0 = low, 1 = medium, 2 = high
        # food_visible: 0 = no, 1 = yes
        # mate_visible: 0 = no, 1 = yes
        
        # Define actions
        # 0 = move_to_food, 1 = eat_food, 2 = wander_for_food
        # 3 = move_to_mate, 4 = reproduce, 5 = signal_for_mate, 6 = wander
        
        # Store learning system in dictionary
        self.learning_systems[entity.get_id()] = q_learning
        
        # Initialize entity's learning state
        entity.learning_state = self._get_learning_state(entity)
        entity.learning_action = None
        entity.learning_reward = 0
        
    def _update_learning(self, entity, delta_time):
        """
        Update learning system for an entity.
        
        Args:
            entity: Entity to update learning for
            delta_time (float): Time delta in seconds
        """
        # Get learning system
        q_learning = self.learning_systems[entity.get_id()]
        
        # Get current state
        current_state = self._get_learning_state(entity)
        
        # If we have a previous state and action, update Q-values
        if hasattr(entity, 'learning_state') and hasattr(entity, 'learning_action') and entity.learning_action is not None:
            # Calculate reward
            reward = self._calculate_reward(entity)
            
            # Update Q-value
            q_learning.update(entity.learning_state, entity.learning_action, reward, current_state)
            
        # Choose new action
        action = q_learning.choose_action(current_state)
        
        # Execute action
        self._execute_learning_action(entity, action)
        
        # Update entity's learning state
        entity.learning_st<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>