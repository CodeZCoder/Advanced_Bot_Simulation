"""
Energy component module for managing entity energy levels.
"""

import config

class EnergyComponent:
    """
    Manages entity energy levels, metabolism, and related functionality.
    """
    
    def __init__(self, initial_energy=100, max_energy=200, metabolism_rate=0.05):
        """
        Initialize the energy component.
        
        Args:
            initial_energy (float): Initial energy level
            max_energy (float): Maximum energy capacity
            metabolism_rate (float): Base energy consumption rate per update
        """
        self.energy = float(initial_energy)
        self.max_energy = float(max_energy)
        self.metabolism_rate = float(metabolism_rate)
        self.movement_cost_factor = config.BOT_MOVEMENT_COST
        self.action_costs = {
            "move": 0.02,
            "eat": 0.5,
            "reproduce": config.BOT_REPRODUCTION_COST,
            "communicate": config.SIGNAL_COST,
            "idle": 0.01
        }
        self.energy_history = []  # Track energy over time
        self.energy_gained = 0  # Total energy gained
        self.energy_spent = 0  # Total energy spent
        
    def update(self, delta_time):
        """
        Update energy based on metabolism.
        
        Args:
            delta_time (float): Time delta in seconds
            
        Returns:
            bool: True if entity is still alive, False if energy depleted
        """
        # Apply base metabolism cost
        energy_consumed = self.metabolism_rate * delta_time
        self.consume_energy(energy_consumed)
        
        # Track energy history (keep last 100 values)
        self.energy_history.append(self.energy)
        if len(self.energy_history) > 100:
            self.energy_history.pop(0)
            
        # Check if entity is still alive
        return self.energy > 0
    
    def consume_energy(self, amount):
        """
        Consume energy for an action.
        
        Args:
            amount (float): Amount of energy to consume
            
        Returns:
            bool: True if enough energy was available, False otherwise
        """
        if amount <= 0:
            return True
            
        if self.energy >= amount:
            self.energy -= amount
            self.energy_spent += amount
            return True
        else:
            # Not enough energy
            self.energy_spent += self.energy
            self.energy = 0
            return False
    
    def add_energy(self, amount):
        """
        Add energy (e.g., from consuming food).
        
        Args:
            amount (float): Amount of energy to add
            
        Returns:
            float: Amount of energy actually added (may be less if at max capacity)
        """
        if amount <= 0:
            return 0
            
        old_energy = self.energy
        self.energy = min(self.energy + amount, self.max_energy)
        added = self.energy - old_energy
        self.energy_gained += added
        return added
    
    def get_energy(self):
        """
        Get current energy level.
        
        Returns:
            float: Current energy
        """
        return self.energy
    
    def get_energy_percentage(self):
        """
        Get energy level as a percentage of maximum.
        
        Returns:
            float: Energy percentage (0-100)
        """
        return (self.energy / self.max_energy) * 100
    
    def get_max_energy(self):
        """
        Get maximum energy capacity.
        
        Returns:
            float: Maximum energy
        """
        return self.max_energy
    
    def set_max_energy(self, max_energy):
        """
        Set maximum energy capacity.
        
        Args:
            max_energy (float): New maximum energy
        """
        self.max_energy = float(max_energy)
        self.energy = min(self.energy, self.max_energy)
        
    def set_metabolism_rate(self, rate):
        """
        Set metabolism rate.
        
        Args:
            rate (float): New metabolism rate
        """
        self.metabolism_rate = float(rate)
        
    def get_metabolism_rate(self):
        """
        Get current metabolism rate.
        
        Returns:
            float: Metabolism rate
        """
        return self.metabolism_rate
    
    def get_action_cost(self, action_type):
        """
        Get energy cost for a specific action.
        
        Args:
            action_type (str): Action type
            
        Returns:
            float: Energy cost
        """
        return self.action_costs.get(action_type, 0)
    
    def set_action_cost(self, action_type, cost):
        """
        Set energy cost for a specific action.
        
        Args:
            action_type (str): Action type
            cost (float): Energy cost
        """
        self.action_costs[action_type] = float(cost)
        
    def calculate_movement_cost(self, distance):
        """
        Calculate energy cost for movement.
        
        Args:
            distance (float): Movement distance
            
        Returns:
            float: Energy cost
        """
        return distance * self.movement_cost_factor
    
    def can_afford_action(self, action_type, additional_cost=0):
        """
        Check if entity has enough energy for an action.
        
        Args:
            action_type (str): Action type
            additional_cost (float): Additional cost beyond base action cost
            
        Returns:
            bool: True if enough energy is available
        """
        total_cost = self.get_action_cost(action_type) + additional_cost
        return self.energy >= total_cost
    
    def get_energy_history(self):
        """
        Get energy history.
        
        Returns:
            list: Energy history
        """
        return self.energy_history
    
    def get_energy_stats(self):
        """
        Get energy statistics.
        
        Returns:
            dict: Energy statistics
        """
        return {
            "current": self.energy,
            "max": self.max_energy,
            "percentage": self.get_energy_percentage(),
            "gained": self.energy_gained,
            "spent": self.energy_spent,
            "metabolism_rate": self.metabolism_rate
        }
