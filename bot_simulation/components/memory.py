"""
Memory component module for storing entity memory data.
"""

import math
import time
import random
import config

class MemoryComponent:
    """
    Stores and manages entity memory, including short-term and long-term memory.
    """
    
    def __init__(self, capacity=100):
        """
        Initialize the memory component.
        
        Args:
            capacity (int): Maximum number of memory items to store
        """
        # Short-term memory (recent perceptions, decays quickly)
        self.short_term_memory = []
        self.short_term_capacity = 20
        self.short_term_decay_rate = 0.1  # Items decay this much per update
        
        # Long-term memory (learned associations, locations, etc.)
        self.long_term_memory = []
        self.long_term_capacity = capacity
        self.long_term_decay_rate = 0.001  # Very slow decay
        
        # Memory categories
        self.resource_locations = []  # Remembered resource locations
        self.danger_locations = []    # Remembered danger locations
        self.bot_encounters = []      # Remembered encounters with other bots
        self.signal_memories = []     # Remembered communication signals
        
        # Memory maps
        self.location_familiarity = {}  # Grid-based familiarity map
        self.grid_size = 50  # Size of grid cells for location memory
        
        # Memory statistics
        self.total_memories_added = 0
        self.total_memories_forgotten = 0
        self.memory_access_count = 0
        
    def update(self, delta_time, entity):
        """
        Update memory, applying decay and processing.
        
        Args:
            delta_time (float): Time delta in seconds
            entity: The entity this component belongs to
        """
        # Update short-term memory decay
        self._update_short_term_memory(delta_time)
        
        # Update long-term memory decay
        self._update_long_term_memory(delta_time)
        
        # Process sensor data into memory
        self._process_sensor_data(entity)
        
        # Update location familiarity
        self._update_location_familiarity(entity)
        
    def _update_short_term_memory(self, delta_time):
        """
        Update short-term memory, applying decay.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Apply decay to all short-term memories
        for memory in self.short_term_memory:
            memory["strength"] -= self.short_term_decay_rate * delta_time
            
        # Remove decayed memories
        self.short_term_memory = [m for m in self.short_term_memory if m["strength"] > 0]
        
    def _update_long_term_memory(self, delta_time):
        """
        Update long-term memory, applying decay.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Apply decay to all long-term memories
        for memory in self.long_term_memory:
            memory["strength"] -= self.long_term_decay_rate * delta_time
            
        # Remove very weak memories if over capacity
        if len(self.long_term_memory) > self.long_term_capacity:
            # Sort by strength and remove weakest
            self.long_term_memory.sort(key=lambda m: m["strength"])
            forgotten = self.long_term_memory[:len(self.long_term_memory) - self.long_term_capacity]
            self.long_term_memory = self.long_term_memory[len(self.long_term_memory) - self.long_term_capacity:]
            
            # Update statistics
            self.total_memories_forgotten += len(forgotten)
            
    def _process_sensor_data(self, entity):
        """
        Process sensor data into memory.
        
        Args:
            entity: The entity this component belongs to
        """
        # Get sensor component
        sensor_component = entity.get_sensor_suite_component()
        if not sensor_component:
            return
            
        # Process perceived resources
        for resource in sensor_component.get_perceived_resources():
            self._remember_resource(resource)
            
        # Process perceived entities
        for perceived in sensor_component.get_perceived_entities():
            if perceived["type"] == "Bot":
                self._remember_bot_encounter(perceived)
                
        # Process perceived signals
        for signal in sensor_component.get_perceived_signals():
            self._remember_signal(signal)
            
    def _update_location_familiarity(self, entity):
        """
        Update location familiarity based on current position.
        
        Args:
            entity: The entity this component belongs to
        """
        # Get position
        position_component = entity.get_position_component()
        if not position_component:
            return
            
        position = position_component.get_position()
        
        # Convert to grid coordinates
        grid_x = int(position[0] / self.grid_size)
        grid_y = int(position[1] / self.grid_size)
        grid_key = f"{grid_x},{grid_y}"
        
        # Update familiarity
        if grid_key in self.location_familiarity:
            self.location_familiarity[grid_key] = min(1.0, self.location_familiarity[grid_key] + 0.01)
        else:
            self.location_familiarity[grid_key] = 0.1
            
    def _remember_resource(self, resource_data):
        """
        Remember a resource location.
        
        Args:
            resource_data (dict): Resource perception data
        """
        position = resource_data["position"]
        
        # Check if already in short-term memory
        for memory in self.short_term_memory:
            if (memory["type"] == "resource" and 
                self._positions_close(memory["position"], position, 20)):
                # Update existing memory
                memory["position"] = position  # Update position
                memory["energy"] = resource_data["energy"]
                memory["strength"] = min(1.0, memory["strength"] + 0.2)  # Reinforce
                memory["last_seen"] = time.time()
                return
                
        # Add to short-term memory
        self.short_term_memory.append({
            "type": "resource",
            "position": position,
            "energy": resource_data["energy"],
            "strength": resource_data["certainty"],
            "created": time.time(),
            "last_seen": time.time()
        })
        
        # Update resource locations list
        self._update_resource_locations(position, resource_data["energy"])
        
        # Potentially add to long-term memory if significant
        if resource_data["energy"] > 30 or resource_data["certainty"] > 0.8:
            self._add_to_long_term_memory({
                "type": "resource",
                "position": position,
                "energy": resource_data["energy"],
                "strength": resource_data["certainty"] * 0.5,  # Start weaker in long-term
                "created": time.time(),
                "last_seen": time.time()
            })
            
    def _remember_bot_encounter(self, bot_data):
        """
        Remember an encounter with another bot.
        
        Args:
            bot_data (dict): Bot perception data
        """
        position = bot_data["position"]
        
        # Add to short-term memory
        self.short_term_memory.append({
            "type": "bot",
            "position": position,
            "distance": bot_data["distance"],
            "strength": bot_data["certainty"],
            "created": time.time(),
            "last_seen": time.time()
        })
        
        # Update bot encounters list
        self._update_bot_encounters(position)
        
    def _remember_signal(self, signal_data):
        """
        Remember a communication signal.
        
        Args:
            signal_data (dict): Signal perception data
        """
        # Add to short-term memory
        self.short_term_memory.append({
            "type": "signal",
            "position": signal_data["position"],
            "signal_type": signal_data["type"],
            "data": signal_data["data"],
            "sender": signal_data["sender"],
            "strength": signal_data["certainty"],
            "created": time.time(),
            "last_seen": time.time()
        })
        
        # Update signal memories list
        self._update_signal_memories(signal_data)
        
        # Process signal based on type
        if signal_data["type"] == 1:  # Danger
            # Remember danger location
            if signal_data["data"] and "position" in signal_data["data"]:
                self._update_danger_locations(signal_data["data"]["position"])
        elif signal_data["type"] == 2:  # Food
            # Remember food location
            if signal_data["data"] and "position" in signal_data["data"]:
                self._update_resource_locations(signal_data["data"]["position"], 30)  # Assume medium energy
                
    def _update_resource_locations(self, position, energy):
        """
        Update remembered resource locations.
        
        Args:
            position (tuple): Resource position
            energy (float): Resource energy
        """
        # Check if already tracking this location
        for i, loc in enumerate(self.resource_locations):
            if self._positions_close(loc["position"], position, 20):
                # Update existing entry
                self.resource_locations[i] = {
                    "position": position,
                    "energy": energy,
                    "last_seen": time.time(),
                    "reliability": min(1.0, loc["reliability"] + 0.1)
                }
                return
                
        # Add new location
        self.resource_locations.append({
            "position": position,
            "energy": energy,
            "last_seen": time.time(),
            "reliability": 0.7
        })
        
        # Limit list size
        if len(self.resource_locations) > 20:
            # Remove oldest or least reliable
            self.resource_locations.sort(key=lambda x: x["reliability"] * (1 / (time.time() - x["last_seen"] + 1)))
            self.resource_locations = self.resource_locations[1:]
            
    def _update_danger_locations(self, position):
        """
        Update remembered danger locations.
        
        Args:
            position (tuple): Danger position
        """
        # Check if already tracking this location
        for i, loc in enumerate(self.danger_locations):
            if self._positions_close(loc["position"], position, 50):
                # Update existing entry
                self.danger_locations[i] = {
                    "position": position,
                    "last_seen": time.time(),
                    "reliability": min(1.0, loc["reliability"] + 0.1)
                }
                return
                
        # Add new location
        self.danger_locations.append({
            "position": position,
            "last_seen": time.time(),
            "reliability": 0.7
        })
        
        # Limit list size
        if len(self.danger_locations) > 10:
            # Remove oldest
            self.danger_locations.sort(key=lambda x: time.time() - x["last_seen"])
            self.danger_locations = self.danger_locations[1:]
            
    def _update_bot_encounters(self, position):
        """
        Update remembered bot encounters.
        
        Args:
            position (tuple): Bot position
        """
        # Add new encounter
        self.bot_encounters.append({
            "position": position,
            "time": time.time()
        })
        
        # Limit list size
        if len(self.bot_encounters) > 30:
            self.bot_encounters = self.bot_encounters[1:]
            
    def _update_signal_memories(self, signal_data):
        """
        Update remembered signals.
        
        Args:
            signal_data (dict): Signal data
        """
        # Add new signal memory
        self.signal_memories.append({
            "position": signal_data["position"],
            "type": signal_data["type"],
            "data": signal_data["data"],
            "sender": signal_data["sender"],
            "time": time.time()
        })
        
        # Limit list size
        if len(self.signal_memories) > 20:
            self.signal_memories = self.signal_memories[1:]
            
    def _add_to_long_term_memory(self, memory):
        """
        Add a memory to long-term memory.
        
        Args:
            memory (dict): Memory data
        """
        # Check if similar memory already exists
        for existing in self.long_term_memory:
            if (existing["type"] == memory["type"] and 
                (existing["type"] != "resource" or 
                 self._positions_close(existing["position"], memory["position"], 30))):
                # Update existing memory
                existing["strength"] = min(1.0, existing["strength"] + 0.2)
                existing["last_seen"] = memory["last_seen"]
                if "energy" in memory:
                    existing["energy"] = memory["energy"]
                return
                
        # Add new memory
        self.long_term_memory.append(memory)
        self.total_memories_added += 1
        
        # Check capacity
        if len(self.long_term_memory) > self.long_term_capacity:
            # Remove weakest memory
            self.long_term_memory.sort(key=lambda m: m["strength"])
            self.long_term_memory.pop(0)
            self.total_memories_forgotten += 1
            
    def _positions_close(self, pos1, pos2, threshold):
        """
        Check if two positions are close to each other.
        
        Args:
            pos1 (tuple): First position
            pos2 (tuple): Second position
            threshold (float): Distance threshold
            
        Returns:
            bool: True if positions are within threshold
        """
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return (dx * dx + dy * dy) <= threshold * threshold
    
    def get_nearest_remembered_resource(self, current_position):
        """
        Get the nearest remembered resource location.
        
        Args:
            current_position (tuple): Current position
            
        Returns:
            dict: Resource data or None
        """
        if not self.resource_locations:
            return None
            
        # Calculate distances
        for loc in self.resource_locations:
            dx = loc["position"][0] - current_position[0]
            dy = loc["position"][1] - current_position[1]
            loc["distance"] = math.sqrt(dx * dx + dy * dy)
            
        # Sort by distance and reliability
        self.resource_locations.sort(key=lambda x: x["distance"] / (x["reliability"] + 0.1))
        
        # Return nearest
        self.memory_access_count += 1
        return self.resource_locations[0]
    
    def get_nearest_danger(self, current_position):
        """
        Get the nearest remembered danger location.
        
        Args:
            current_position (tuple): Current position
            
        Returns:
            dict: Danger data or None
        """
        if not self.danger_locations:
            return None
            
        # Calculate distances
        for loc in self.danger_locations:
            dx = loc["position"][0] - current_position[0]
            dy = loc["position"][1] - current_position[1]
            loc["distance"] = math.sqrt(dx * dx + dy * dy)
            
        # Sort by distance and reliability
        self.danger_locations.sort(key=lambda x: x["distance"] / (x["reliability"] + 0.1))
        
        # Return nearest
        self.memory_access_co<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>