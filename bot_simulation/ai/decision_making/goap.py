"""
Goal-Oriented Action Planning (GOAP) system for bot decision making.
"""

import heapq
import math
import random
import config

class GOAPAction:
    """Action that can be performed by an entity in GOAP."""
    
    def __init__(self, name, cost=1.0):
        """
        Initialize a GOAP action.
        
        Args:
            name (str): Action name
            cost (float): Action cost
        """
        self.name = name
        self.cost = cost
        self.preconditions = {}
        self.effects = {}
        
    def add_precondition(self, key, value):
        """
        Add a precondition for this action.
        
        Args:
            key (str): Precondition key
            value: Precondition value
        """
        self.preconditions[key] = value
        
    def add_effect(self, key, value):
        """
        Add an effect for this action.
        
        Args:
            key (str): Effect key
            value: Effect value
        """
        self.effects[key] = value
        
    def check_procedural_precondition(self, entity, entity_manager, world_map):
        """
        Check if procedural preconditions are met.
        
        Args:
            entity: The entity performing the action
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            bool: True if procedural preconditions are met
        """
        return True
    
    def get_cost(self, entity, entity_manager, world_map):
        """
        Get the cost of this action.
        
        Args:
            entity: The entity performing the action
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            float: Action cost
        """
        return self.cost
    
    def perform(self, entity, entity_manager, world_map):
        """
        Perform the action.
        
        Args:
            entity: The entity performing the action
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            bool: True if action was performed successfully
        """
        return True
    
    def is_done(self, entity, entity_manager, world_map):
        """
        Check if the action is done.
        
        Args:
            entity: The entity performing the action
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            bool: True if action is done
        """
        return True
    
    def requires_in_range(self):
        """
        Check if this action requires the entity to be in range of a target.
        
        Returns:
            bool: True if action requires being in range
        """
        return False
    
    def set_target(self, target):
        """
        Set the target for this action.
        
        Args:
            target: Target entity or position
        """
        pass
    
    def get_target(self):
        """
        Get the target for this action.
        
        Returns:
            Target entity or position
        """
        return None
    
    def reset(self):
        """Reset the action state."""
        pass


class GOAPPlanner:
    """Goal-Oriented Action Planning system."""
    
    def __init__(self):
        """Initialize the GOAP planner."""
        self.actions = []
        
    def add_action(self, action):
        """
        Add an action to the planner.
        
        Args:
            action (GOAPAction): Action to add
        """
        self.actions.append(action)
        
    def plan(self, entity, entity_manager, world_map, world_state, goal):
        """
        Create a plan to achieve the goal.
        
        Args:
            entity: The entity this planner is planning for
            entity_manager: Entity manager instance
            world_map: World map instance
            world_state (dict): Current world state
            goal (dict): Goal state
            
        Returns:
            list: Sequence of actions to achieve the goal, or None if no plan found
        """
        # Check if goal is already satisfied
        if self._is_goal_satisfied(world_state, goal):
            return []
            
        # Get usable actions (procedural preconditions met)
        usable_actions = []
        for action in self.actions:
            if action.check_procedural_precondition(entity, entity_manager, world_map):
                usable_actions.append(action)
                
        # A* search for plan
        open_list = []
        closed_list = set()
        
        # Start node
        start_node = PlanNode(None, 0, world_state, None)
        start_node.calculate_f(goal)
        
        # Add start node to open list
        heapq.heappush(open_list, start_node)
        
        # Search for plan
        while open_list:
            # Get node with lowest f value
            current_node = heapq.heappop(open_list)
            
            # Check if goal is satisfied
            if self._is_goal_satisfied(current_node.state, goal):
                # Goal found, build plan
                plan = []
                while current_node.parent:
                    plan.append(current_node.action)
                    current_node = current_node.parent
                plan.reverse()
                return plan
                
            # Add to closed list
            closed_list.add(current_node)
            
            # Try each action
            for action in usable_actions:
                # Check if action's preconditions are met
                if not self._are_preconditions_met(current_node.state, action.preconditions):
                    continue
                    
                # Apply action effects to get new state
                new_state = self._apply_effects(current_node.state.copy(), action.effects)
                
                # Create new node
                new_node = PlanNode(
                    current_node,
                    current_node.g + action.get_cost(entity, entity_manager, world_map),
                    new_state,
                    action
                )
                new_node.calculate_f(goal)
                
                # Check if node is in closed list
                if new_node in closed_list:
                    continue
                    
                # Check if node is in open list
                in_open = False
                for node in open_list:
                    if new_node == node:
                        in_open = True
                        if new_node.g < node.g:
                            # Replace with better path
                            node.g = new_node.g
                            node.f = new_node.f
                            node.parent = new_node.parent
                            node.action = new_node.action
                        break
                        
                if not in_open:
                    heapq.heappush(open_list, new_node)
                    
        # No plan found
        return None
    
    def _is_goal_satisfied(self, state, goal):
        """
        Check if the goal is satisfied by the state.
        
        Args:
            state (dict): Current state
            goal (dict): Goal state
            
        Returns:
            bool: True if goal is satisfied
        """
        for key, value in goal.items():
            if key not in state or state[key] != value:
                return False
        return True
    
    def _are_preconditions_met(self, state, preconditions):
        """
        Check if preconditions are met by the state.
        
        Args:
            state (dict): Current state
            preconditions (dict): Preconditions
            
        Returns:
            bool: True if preconditions are met
        """
        for key, value in preconditions.items():
            if key not in state or state[key] != value:
                return False
        return True
    
    def _apply_effects(self, state, effects):
        """
        Apply effects to the state.
        
        Args:
            state (dict): Current state
            effects (dict): Effects to apply
            
        Returns:
            dict: New state
        """
        for key, value in effects.items():
            state[key] = value
        return state


class PlanNode:
    """Node in the A* search for GOAP planning."""
    
    def __init__(self, parent, g, state, action):
        """
        Initialize a plan node.
        
        Args:
            parent (PlanNode): Parent node
            g (float): Cost from start to this node
            state (dict): World state at this node
            action (GOAPAction): Action that led to this node
        """
        self.parent = parent
        self.g = g
        self.h = 0
        self.f = 0
        self.state = state
        self.action = action
        
    def calculate_f(self, goal):
        """
        Calculate f value (f = g + h).
        
        Args:
            goal (dict): Goal state
        """
        self.h = self._calculate_heuristic(goal)
        self.f = self.g + self.h
        
    def _calculate_heuristic(self, goal):
        """
        Calculate heuristic value (distance to goal).
        
        Args:
            goal (dict): Goal state
            
        Returns:
            float: Heuristic value
        """
        # Count number of unsatisfied goal conditions
        h = 0
        for key, value in goal.items():
            if key not in self.state or self.state[key] != value:
                h += 1
        return h
    
    def __eq__(self, other):
        """
        Check if two nodes are equal.
        
        Args:
            other (PlanNode): Other node
            
        Returns:
            bool: True if nodes are equal
        """
        if not isinstance(other, PlanNode):
            return False
        return self.state == other.state
    
    def __lt__(self, other):
        """
        Compare nodes by f value.
        
        Args:
            other (PlanNode): Other node
            
        Returns:
            bool: True if this node has lower f value
        """
        return self.f < other.f


# Common GOAP actions
class MoveToResourceAction(GOAPAction):
    """Action to move to a resource."""
    
    def __init__(self):
        """Initialize the action."""
        super().__init__("MoveToResource", 1.0)
        self.add_precondition("has_target_resource", True)
        self.add_effect("near_resource", True)
        self.target = None
        self.in_range = False
        
    def check_procedural_precondition(self, entity, entity_manager, world_map):
        """
        Check if procedural preconditions are met.
        
        Args:
            entity: The entity performing the action
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            bool: True if procedural preconditions are met
        """
        # Check if there are resources
        sensor_component = entity.get_sensor_suite_component()
        resources = sensor_component.get_perceived_resources()
        
        if not resources:
            return False
            
        # Find closest resource
        closest = min(resources, key=lambda r: r["distance"])
        
        # Set target
        self.target = closest["resource"]
        
        return True
    
    def get_cost(self, entity, entity_manager, world_map):
        """
        Get the cost of this action.
        
        Args:
            entity: The entity performing the action
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            float: Action cost
        """
        # Cost based on distance
        if not self.target:
            return self.cost
            
        position = entity.get_position()
        target_position = self.target.get_position()
        
        dx = position[0] - target_position[0]
        dy = position[1] - target_position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        return self.cost * (1.0 + distance / 500.0)
    
    def perform(self, entity, entity_manager, world_map):
        """
        Perform the action.
        
        Args:
            entity: The entity performing the action
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            bool: True if action was performed successfully
        """
        if not self.target:
            return False
            
        # Check if already in range
        position = entity.get_position()
        target_position = self.target.get_position()
        
        dx = position[0] - target_position[0]
        dy = position[1] - target_position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance <= entity.get_radius() + 5:
            self.in_range = True
            return True
            
        # Move toward target
        action_component = entity.get_action_component()
        if action_component.queue_action("move", target_position):
            return True
        else:
            return False
    
    def is_done(self, entity, entity_manager, world_map):
        """
        Check if the action is done.
        
        Args:
            entity: The entity performing the action
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            bool: True if action is done
        """
        return self.in_range
    
    def requires_in_range(self):
        """
        Check if this action requires the entity to be in range of a target.
        
        Returns:
            bool: True if action requires being in range
        """
        return True
    
    def set_target(self, target):
        """
        Set the target for this action.
        
        Args:
            target: Target entity or position
        """
        self.target = target
    
    def get_target(self):
        """
        Get the target for this action.
        
        Returns:
            Target entity or position
        """
        return self.target
    
    def reset(self):
        """Reset the action state."""
        self.target = None
        self.in_range = False


class EatResourceAction(GOAPAction):
    """Action to eat a resource."""
    
    def __init__(self):
        """Initialize the action."""
        super().__init__("EatResource", 0.5)
        self.add_precondition("near_resource", True)
        self.add_effect("has_energy", True)
        self.target = None
        
    def check_procedural_precondition(self, entity, entity_manager, world_map):
        """
        Check if procedural preconditions are met.
        
        Args:
            entity: The entity performing the action
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            bool: True if procedural preconditions are met
        """
        # Check if there are resources nearby
        sensor_component = entity.get_sensor_suite_component()
        resources = sensor_component.get_perceived_resources()
        
        if not resources:
            return False
            
        # Find closest resource
        closest = min(resources, key=lambda r: r["distance"])
        
        # Check if close enough
        if closest["distance"] > entity.get_radius() + 5:
            return False
            
        # Set target
        self.target = closest["resource"]
        
        return True
    
    def perform(self, entity, entity_manager, world_map):
        """
        Perform the actio<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>