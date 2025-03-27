"""
Utility AI system for bot decision making.
"""

import math
import random
import config

class UtilityAI:
    """Utility AI system for bot decision making."""
    
    def __init__(self):
        """Initialize the utility AI system."""
        # Available actions
        self.actions = {}
        
        # Considerations for each action
        self.considerations = {}
        
        # Action weights (importance)
        self.weights = {}
        
        # Response curves for considerations
        self.curves = {}
        
    def add_action(self, action_name, weight=1.0):
        """
        Add an action to the utility AI.
        
        Args:
            action_name (str): Name of the action
            weight (float): Weight/importance of the action
        """
        self.actions[action_name] = action_name
        self.considerations[action_name] = []
        self.weights[action_name] = weight
        
    def add_consideration(self, action_name, consideration_name, evaluation_func, curve_func, weight=1.0):
        """
        Add a consideration for an action.
        
        Args:
            action_name (str): Name of the action
            consideration_name (str): Name of the consideration
            evaluation_func (callable): Function that evaluates the consideration (0-1)
            curve_func (callable): Response curve function
            weight (float): Weight/importance of the consideration
        """
        if action_name not in self.actions:
            self.add_action(action_name)
            
        self.considerations[action_name].append({
            "name": consideration_name,
            "evaluation_func": evaluation_func,
            "curve_func": curve_func,
            "weight": weight
        })
        
    def evaluate_action(self, action_name, entity, entity_manager, world_map):
        """
        Evaluate the utility of an action.
        
        Args:
            action_name (str): Name of the action
            entity: The entity this AI is controlling
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            float: Utility score (0-1)
        """
        if action_name not in self.actions:
            return 0.0
            
        # Get considerations for this action
        action_considerations = self.considerations[action_name]
        if not action_considerations:
            return 0.0
            
        # Evaluate each consideration
        consideration_scores = []
        for consideration in action_considerations:
            # Get raw value from evaluation function
            raw_value = consideration["evaluation_func"](entity, entity_manager, world_map)
            
            # Apply response curve
            curved_value = consideration["curve_func"](raw_value)
            
            # Apply weight
            weighted_value = curved_value * consideration["weight"]
            
            consideration_scores.append(weighted_value)
            
        # Combine scores (multiplicative)
        if not consideration_scores:
            return 0.0
            
        # Multiply all scores together
        final_score = 1.0
        for score in consideration_scores:
            final_score *= score
            
        # Apply action weight
        final_score *= self.weights[action_name]
        
        return final_score
    
    def select_action(self, entity, entity_manager, world_map):
        """
        Select the best action based on utility scores.
        
        Args:
            entity: The entity this AI is controlling
            entity_manager: Entity manager instance
            world_map: World map instance
            
        Returns:
            str: Name of the selected action
        """
        # Evaluate all actions
        action_scores = {}
        for action_name in self.actions:
            action_scores[action_name] = self.evaluate_action(action_name, entity, entity_manager, world_map)
            
        # Select action with highest score
        if not action_scores:
            return None
            
        best_action = max(action_scores.items(), key=lambda x: x[1])
        
        # Return action name and score
        return {
            "action": best_action[0],
            "score": best_action[1],
            "all_scores": action_scores
        }


# Response curve functions
def linear_curve(x):
    """
    Linear response curve.
    
    Args:
        x (float): Input value (0-1)
        
    Returns:
        float: Output value (0-1)
    """
    return max(0.0, min(1.0, x))

def exponential_curve(x):
    """
    Exponential response curve.
    
    Args:
        x (float): Input value (0-1)
        
    Returns:
        float: Output value (0-1)
    """
    return max(0.0, min(1.0, x * x))

def logarithmic_curve(x):
    """
    Logarithmic response curve.
    
    Args:
        x (float): Input value (0-1)
        
    Returns:
        float: Output value (0-1)
    """
    if x <= 0:
        return 0.0
    return max(0.0, min(1.0, math.sqrt(x)))

def sigmoid_curve(x, steepness=5.0, midpoint=0.5):
    """
    Sigmoid response curve.
    
    Args:
        x (float): Input value (0-1)
        steepness (float): Steepness of the curve
        midpoint (float): Midpoint of the curve
        
    Returns:
        float: Output value (0-1)
    """
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return 1.0 / (1.0 + math.exp(-steepness * (x - midpoint)))

def inverse_curve(x):
    """
    Inverse response curve.
    
    Args:
        x (float): Input value (0-1)
        
    Returns:
        float: Output value (0-1)
    """
    return max(0.0, min(1.0, 1.0 - x))

def sine_curve(x):
    """
    Sine response curve.
    
    Args:
        x (float): Input value (0-1)
        
    Returns:
        float: Output value (0-1)
    """
    return max(0.0, min(1.0, math.sin(x * math.pi / 2)))

def cosine_curve(x):
    """
    Cosine response curve.
    
    Args:
        x (float): Input value (0-1)
        
    Returns:
        float: Output value (0-1)
    """
    return max(0.0, min(1.0, 1.0 - math.cos(x * math.pi / 2)))

def step_curve(x, threshold=0.5):
    """
    Step response curve.
    
    Args:
        x (float): Input value (0-1)
        threshold (float): Threshold value
        
    Returns:
        float: Output value (0 or 1)
    """
    return 1.0 if x >= threshold else 0.0

def smoothstep_curve(x):
    """
    Smoothstep response curve.
    
    Args:
        x (float): Input value (0-1)
        
    Returns:
        float: Output value (0-1)
    """
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return x * x * (3 - 2 * x)


# Common evaluation functions
def evaluate_hunger(entity, entity_manager, world_map):
    """
    Evaluate hunger level.
    
    Args:
        entity: The entity this AI is controlling
        entity_manager: Entity manager instance
        world_map: World map instance
        
    Returns:
        float: Hunger level (0-1)
    """
    energy_component = entity.get_energy_component()
    energy_percentage = energy_component.get_energy_percentage()
    
    # Convert to hunger (0 = full, 1 = starving)
    return max(0.0, min(1.0, 1.0 - (energy_percentage / 100.0)))

def evaluate_resource_proximity(entity, entity_manager, world_map):
    """
    Evaluate proximity to resources.
    
    Args:
        entity: The entity this AI is controlling
        entity_manager: Entity manager instance
        world_map: World map instance
        
    Returns:
        float: Resource proximity (0-1)
    """
    sensor_component = entity.get_sensor_suite_component()
    resources = sensor_component.get_perceived_resources()
    
    if not resources:
        return 0.0
        
    # Find closest resource
    closest = min(resources, key=lambda r: r["distance"])
    
    # Convert distance to proximity (0 = far, 1 = close)
    max_distance = sensor_component.resource_detection_range
    proximity = 1.0 - (closest["distance"] / max_distance)
    
    return max(0.0, min(1.0, proximity))

def evaluate_bot_proximity(entity, entity_manager, world_map):
    """
    Evaluate proximity to other bots.
    
    Args:
        entity: The entity this AI is controlling
        entity_manager: Entity manager instance
        world_map: World map instance
        
    Returns:
        float: Bot proximity (0-1)
    """
    sensor_component = entity.get_sensor_suite_component()
    entities = sensor_component.get_perceived_entities()
    bots = [e for e in entities if e["type"] == "Bot"]
    
    if not bots:
        return 0.0
        
    # Find closest bot
    closest = min(bots, key=lambda b: b["distance"])
    
    # Convert distance to proximity (0 = far, 1 = close)
    max_distance = sensor_component.visual_range
    proximity = 1.0 - (closest["distance"] / max_distance)
    
    return max(0.0, min(1.0, proximity))

def evaluate_danger_proximity(entity, entity_manager, world_map):
    """
    Evaluate proximity to danger.
    
    Args:
        entity: The entity this AI is controlling
        entity_manager: Entity manager instance
        world_map: World map instance
        
    Returns:
        float: Danger proximity (0-1)
    """
    sensor_component = entity.get_sensor_suite_component()
    signals = sensor_component.get_perceived_signals()
    danger_signals = [s for s in signals if s["type"] == 1]  # Danger signal
    
    if not danger_signals:
        return 0.0
        
    # Find closest danger signal
    closest = min(danger_signals, key=lambda s: s["distance"])
    
    # Convert distance to proximity (0 = far, 1 = close)
    max_distance = sensor_component.signal_detection_range
    proximity = 1.0 - (closest["distance"] / max_distance)
    
    return max(0.0, min(1.0, proximity))

def evaluate_maturity(entity, entity_manager, world_map):
    """
    Evaluate maturity level.
    
    Args:
        entity: The entity this AI is controlling
        entity_manager: Entity manager instance
        world_map: World map instance
        
    Returns:
        float: Maturity level (0-1)
    """
    age = entity.get_age()
    maturity_age = config.BOT_MATURITY_AGE
    
    # Convert age to maturity (0 = young, 1 = mature)
    maturity = age / maturity_age
    
    return max(0.0, min(1.0, maturity))

def evaluate_energy_surplus(entity, entity_manager, world_map):
    """
    Evaluate energy surplus.
    
    Args:
        entity: The entity this AI is controlling
        entity_manager: Entity manager instance
        world_map: World map instance
        
    Returns:
        float: Energy surplus (0-1)
    """
    energy_component = entity.get_energy_component()
    energy_percentage = energy_component.get_energy_percentage()
    
    # Convert to surplus (0 = no surplus, 1 = full surplus)
    # Only consider surplus above 50%
    surplus = max(0.0, (energy_percentage - 50.0) / 50.0)
    
    return max(0.0, min(1.0, surplus))

def evaluate_exploration_need(entity, entity_manager, world_map):
    """
    Evaluate need for exploration.
    
    Args:
        entity: The entity this AI is controlling
        entity_manager: Entity manager instance
        world_map: World map instance
        
    Returns:
        float: Exploration need (0-1)
    """
    memory_component = entity.get_memory_component()
    position = entity.get_position()
    
    # Check familiarity with current location
    familiarity = memory_component.get_location_familiarity(position)
    
    # Convert to exploration need (0 = familiar, 1 = unfamiliar)
    exploration_need = 1.0 - familiarity
    
    return max(0.0, min(1.0, exploration_need))

def evaluate_social_need(entity, entity_manager, world_map):
    """
    Evaluate social need.
    
    Args:
        entity: The entity this AI is controlling
        entity_manager: Entity manager instance
        world_map: World map instance
        
    Returns:
        float: Social need (0-1)
    """
    ai_state_component = entity.get_ai_state_component()
    personality = ai_state_component.get_personality()
    
    # Base social need on sociability personality trait
    social_need = personality["sociability"]
    
    # Modify based on recent bot encounters
    memory_component = entity.get_memory_component()
    bot_encounters = memory_component.bot_encounters
    
    # If no recent encounters, increase social need
    if not bot_encounters:
        social_need *= 1.5
    else:
        # Check recency of encounters
        import time
        current_time = time.time()
        recent_encounters = [e for e in bot_encounters if current_time - e["time"] < 30]
        
        if not recent_encounters:
            social_need *= 1.2
            
    return max(0.0, min(1.0, social_need))

def evaluate_reproduction_need(entity, entity_manager, world_map):
    """
    Evaluate reproduction need.
    
    Args:
        entity: The entity this AI is controlling
        entity_manager: Entity manager instance
        world_map: World map instance
        
    Returns:
        float: Reproduction need (0-1)
    """
    # Check maturity
    if not entity.is_mature():
        return 0.0
        
    # Check energy
    energy_component = entity.get_energy_component()
    energy_percentage = energy_component.get_energy_percentage()
    
    if energy_percentage < 60:
        return 0.0
        
    # Base reproduction need on energy surplus
    reproduction_need = max(0.0, (energy_percentage - 60.0) / 40.0)
    
    # Modify based on genetic component
    genetic_component = entity.get_genetic_component()
    genes = genetic_component.get_all_genes()
    
    # Use reproduction rate gene to influence need
    reproduction_need *= genes["reproduction_rate"]
    
    return max(0.0, min(1.0, reproduction_need))


def create_default_utility_ai():
    """
    Create a default utility AI for bots.
    
    Returns:
        UtilityAI: Default utility AI
    """
    # Create the utility AI
    utility_ai = UtilityAI()
    
    # Add actions
    utility_ai.add_action("move_to_resource", 1.0)
    utility_ai.add_action("eat_resource", 1.2)
    utility_ai.add_action("move_to_bot", 0.7)
    utility_ai.add_action("reproduce", 0.8)
    utility_ai.add_action("flee_danger", 1.5)
    utility_ai.add_action("emit_danger_signal", 0.6)
    utility_ai.add_action("emit_food_signal", 0.5)
    utility_ai.add_action("emit_mate_signal", 0.4)
    utility_ai.add_action("explore", 0.3)
    utility_ai.add_action("idle", 0.1)
    
    # Add considerations for move_to_resource
    utility_ai.add_consideration(
        "move_to_resource",
        "hunger",
        evaluate_hunger,
        sigmoid_curve,
        1.2
    )
    utility_ai.add_consideration(
        "move_to_resource",
        "resource_proximity",
        evaluate_resource_proximity,
        logarithmic_curve,
        0.8
    )
    utility_ai.add_consideration(
        "move_to_resource",
        "danger_proximity",
        evaluate_danger_proximity,
        inverse_curve,
        1.0
    )
    
    # Add considerations for eat_resource
    utility_ai.add_consideration(
        "eat_resource",
        "hunger",
        evaluate_hunger,
        exponential_curve,
        1.5
    )
    utility_ai.add_consideration(
        "eat_resource",
        "resource_proximity",
        evaluate_resource_proximity,
        step_curve,
        2.0
    )
    
    # Add considerations for move_to_bot
    utility_ai.add_consideration(
        "move_to_bot",
        "social_need",
        evaluate_social_need,
        sigmoid_curve,
        1.0
    )
    utility_ai.add_consideration(
        "move_to_bot",
        "bot_proximity",
        evaluate_bot_proximity,
        logarithmic_curve,
        0.7
    )
    utility_ai.add_consideration(
        "move_to_bot",
        "hunger",
        evaluate_hunger,
<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>