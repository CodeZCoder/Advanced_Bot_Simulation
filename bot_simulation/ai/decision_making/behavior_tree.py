"""
Behavior tree system for bot decision making.
"""

import random
import math
import config

class BehaviorNode:
    """Base class for all behavior tree nodes."""
    
    def __init__(self, name):
        """
        Initialize a behavior node.
        
        Args:
            name (str): Node name
        """
        self.name = name
        self.parent = None
        self.blackboard = None
    
    def set_blackboard(self, blackboard):
        """
        Set the blackboard for this node.
        
        Args:
            blackboard (dict): Blackboard data
        """
        self.blackboard = blackboard
    
    def tick(self, entity, entity_manager, world_map):
        """
        Execute the node logic.
        
        Args:
            entity: The entity this node is controlling
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            str: "success", "failure", or "running"
        """
        raise NotImplementedError("Subclasses must implement tick method")


class Selector(BehaviorNode):
    """Selector node that succeeds if any child succeeds."""
    
    def __init__(self, name, children=None):
        """
        Initialize a selector node.
        
        Args:
            name (str): Node name
            children (list, optional): Child nodes
        """
        super().__init__(name)
        self.children = children or []
        for child in self.children:
            child.parent = self
    
    def add_child(self, child):
        """
        Add a child node.
        
        Args:
            child (BehaviorNode): Child node to add
        """
        self.children.append(child)
        child.parent = self
    
    def tick(self, entity, entity_manager, world_map):
        """
        Execute the selector logic.
        
        Args:
            entity: The entity this node is controlling
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            str: "success" if any child succeeds, "failure" if all fail, or "running"
        """
        for child in self.children:
            child.set_blackboard(self.blackboard)
            status = child.tick(entity, entity_manager, world_map)
            
            if status == "running":
                return "running"
            
            if status == "success":
                return "success"
        
        return "failure"


class Sequence(BehaviorNode):
    """Sequence node that succeeds if all children succeed."""
    
    def __init__(self, name, children=None):
        """
        Initialize a sequence node.
        
        Args:
            name (str): Node name
            children (list, optional): Child nodes
        """
        super().__init__(name)
        self.children = children or []
        self.current_child = 0
        for child in self.children:
            child.parent = self
    
    def add_child(self, child):
        """
        Add a child node.
        
        Args:
            child (BehaviorNode): Child node to add
        """
        self.children.append(child)
        child.parent = self
    
    def tick(self, entity, entity_manager, world_map):
        """
        Execute the sequence logic.
        
        Args:
            entity: The entity this node is controlling
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            str: "success" if all children succeed, "failure" if any fail, or "running"
        """
        if not self.children:
            return "success"
        
        # Start from the beginning if we're starting a new execution
        if "running_sequence" not in self.blackboard or self.blackboard["running_sequence"] != self.name:
            self.current_child = 0
            self.blackboard["running_sequence"] = self.name
        
        # Execute children in sequence
        while self.current_child < len(self.children):
            child = self.children[self.current_child]
            child.set_blackboard(self.blackboard)
            status = child.tick(entity, entity_manager, world_map)
            
            if status == "running":
                return "running"
            
            if status == "failure":
                self.current_child = 0
                self.blackboard["running_sequence"] = None
                return "failure"
            
            # Child succeeded, move to next
            self.current_child += 1
        
        # All children succeeded
        self.current_child = 0
        self.blackboard["running_sequence"] = None
        return "success"


class Condition(BehaviorNode):
    """Condition node that checks a condition."""
    
    def __init__(self, name, condition_func):
        """
        Initialize a condition node.
        
        Args:
            name (str): Node name
            condition_func (callable): Function that returns True/False
        """
        super().__init__(name)
        self.condition_func = condition_func
    
    def tick(self, entity, entity_manager, world_map):
        """
        Check the condition.
        
        Args:
            entity: The entity this node is controlling
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            str: "success" if condition is True, "failure" otherwise
        """
        if self.condition_func(entity, entity_manager, world_map, self.blackboard):
            return "success"
        else:
            return "failure"


class Action(BehaviorNode):
    """Action node that performs an action."""
    
    def __init__(self, name, action_func):
        """
        Initialize an action node.
        
        Args:
            name (str): Node name
            action_func (callable): Function that performs the action
        """
        super().__init__(name)
        self.action_func = action_func
    
    def tick(self, entity, entity_manager, world_map):
        """
        Perform the action.
        
        Args:
            entity: The entity this node is controlling
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            str: Result of the action ("success", "failure", or "running")
        """
        return self.action_func(entity, entity_manager, world_map, self.blackboard)


class Inverter(BehaviorNode):
    """Inverter node that inverts the result of its child."""
    
    def __init__(self, name, child=None):
        """
        Initialize an inverter node.
        
        Args:
            name (str): Node name
            child (BehaviorNode, optional): Child node
        """
        super().__init__(name)
        self.child = child
        if child:
            child.parent = self
    
    def set_child(self, child):
        """
        Set the child node.
        
        Args:
            child (BehaviorNode): Child node
        """
        self.child = child
        child.parent = self
    
    def tick(self, entity, entity_manager, world_map):
        """
        Invert the result of the child.
        
        Args:
            entity: The entity this node is controlling
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            str: Inverted result of child
        """
        if not self.child:
            return "failure"
        
        self.child.set_blackboard(self.blackboard)
        status = self.child.tick(entity, entity_manager, world_map)
        
        if status == "running":
            return "running"
        
        if status == "success":
            return "failure"
        
        return "success"


class Repeater(BehaviorNode):
    """Repeater node that repeats its child a specified number of times."""
    
    def __init__(self, name, child=None, repeat_count=None):
        """
        Initialize a repeater node.
        
        Args:
            name (str): Node name
            child (BehaviorNode, optional): Child node
            repeat_count (int, optional): Number of times to repeat, None for infinite
        """
        super().__init__(name)
        self.child = child
        if child:
            child.parent = self
        self.repeat_count = repeat_count
        self.current_count = 0
    
    def set_child(self, child):
        """
        Set the child node.
        
        Args:
            child (BehaviorNode): Child node
        """
        self.child = child
        child.parent = self
    
    def tick(self, entity, entity_manager, world_map):
        """
        Repeat the child node.
        
        Args:
            entity: The entity this node is controlling
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            str: Result of repeating the child
        """
        if not self.child:
            return "failure"
        
        # Reset counter if we're starting a new execution
        if "running_repeater" not in self.blackboard or self.blackboard["running_repeater"] != self.name:
            self.current_count = 0
            self.blackboard["running_repeater"] = self.name
        
        # Check if we've reached the repeat count
        if self.repeat_count is not None and self.current_count >= self.repeat_count:
            self.current_count = 0
            self.blackboard["running_repeater"] = None
            return "success"
        
        # Execute the child
        self.child.set_blackboard(self.blackboard)
        status = self.child.tick(entity, entity_manager, world_map)
        
        if status == "running":
            return "running"
        
        # Increment counter if child completed (success or failure)
        self.current_count += 1
        
        # If infinite repeating or not done yet, return running
        if self.repeat_count is None or self.current_count < self.repeat_count:
            return "running"
        
        # Done repeating
        self.current_count = 0
        self.blackboard["running_repeater"] = None
        return "success"


class RandomSelector(BehaviorNode):
    """Selector that chooses a random child to execute."""
    
    def __init__(self, name, children=None):
        """
        Initialize a random selector node.
        
        Args:
            name (str): Node name
            children (list, optional): Child nodes
        """
        super().__init__(name)
        self.children = children or []
        for child in self.children:
            child.parent = self
    
    def add_child(self, child):
        """
        Add a child node.
        
        Args:
            child (BehaviorNode): Child node to add
        """
        self.children.append(child)
        child.parent = self
    
    def tick(self, entity, entity_manager, world_map):
        """
        Execute a random child.
        
        Args:
            entity: The entity this node is controlling
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            str: Result of the chosen child
        """
        if not self.children:
            return "failure"
        
        # Choose a random child if we're starting a new execution
        if "random_selector_child" not in self.blackboard or self.blackboard["random_selector_parent"] != self.name:
            self.blackboard["random_selector_child"] = random.randint(0, len(self.children) - 1)
            self.blackboard["random_selector_parent"] = self.name
        
        # Execute the chosen child
        child_index = self.blackboard["random_selector_child"]
        child = self.children[child_index]
        child.set_blackboard(self.blackboard)
        status = child.tick(entity, entity_manager, world_map)
        
        if status == "running":
            return "running"
        
        # Child completed, clear the selection
        self.blackboard["random_selector_child"] = None
        self.blackboard["random_selector_parent"] = None
        
        return status


class BehaviorTree:
    """Behavior tree for bot decision making."""
    
    def __init__(self, root_node=None):
        """
        Initialize a behavior tree.
        
        Args:
            root_node (BehaviorNode, optional): Root node of the tree
        """
        self.root = root_node
        self.blackboard = {}
    
    def set_root(self, root_node):
        """
        Set the root node.
        
        Args:
            root_node (BehaviorNode): Root node
        """
        self.root = root_node
    
    def tick(self, entity, entity_manager, world_map):
        """
        Execute the behavior tree.
        
        Args:
            entity: The entity this tree is controlling
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            str: Result of the tree execution
        """
        if not self.root:
            return "failure"
        
        # Update blackboard with entity state
        self._update_blackboard(entity)
        
        # Execute the tree
        self.root.set_blackboard(self.blackboard)
        return self.root.tick(entity, entity_manager, world_map)
    
    def _update_blackboard(self, entity):
        """
        Update the blackboard with entity state.
        
        Args:
            entity: The entity this tree is controlling
        """
        # Get components
        energy_component = entity.get_energy_component()
        sensor_component = entity.get_sensor_suite_component()
        position_component = entity.get_position_component()
        
        # Update blackboard with entity state
        self.blackboard["entity_id"] = entity.get_id()
        self.blackboard["position"] = position_component.get_position()
        self.blackboard["energy"] = energy_component.get_energy()
        self.blackboard["energy_percentage"] = energy_component.get_energy_percentage()
        self.blackboard["age"] = entity.get_age()
        self.blackboard["is_mature"] = entity.is_mature()
        
        # Update with sensor data
        self.blackboard["perceived_entities"] = sensor_component.get_perceived_entities()
        self.blackboard["perceived_resources"] = sensor_component.get_perceived_resources()
        self.blackboard["perceived_signals"] = sensor_component.get_perceived_signals()
        self.blackboard["perceived_obstacles"] = sensor_component.get_perceived_obstacles()


# Common condition functions
def is_hungry(entity, entity_manager, world_map, blackboard):
    """Check if entity is hungry."""
    return blackboard["energy_percentage"] < 50

def is_starving(entity, entity_manager, world_map, blackboard):
    """Check if entity is starving."""
    return blackboard["energy_percentage"] < 20

def is_full(entity, entity_manager, world_map, blackboard):
    """Check if entity is full."""
    return blackboard["energy_percentage"] > 80

def is_mature(entity, entity_manager, world_map, blackboard):
    """Check if entity is mature."""
    return blackboard["is_mature"]

def has_nearby_resource(entity, entity_manager, world_map, blackboard):
    """Check if there's a resource nearby."""
    resources = blackboard["perceived_resources"]
    return len(resources) > 0 and min([r["distance"] for r in resources]) < 50

def has_nearby_bot(entity, entity_manager, world_map, blackboard):
    """Check if there's another bot nearby."""
    entities = blackboard["perceived_entities"]
    bots = [e for e in entities if e["type"] == "Bot"]
    return len(bots) > 0 and min([b["distance"] for b in bots]) < 100

def has_nearby_danger(entity, entity_manager, world_map, blackboard):
    """Check if the<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>