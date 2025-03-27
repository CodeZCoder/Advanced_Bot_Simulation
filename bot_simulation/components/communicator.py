"""
Communicator component module for handling entity communication.
"""

import math
import random
import time
import config

class CommunicatorComponent:
    """
    Handles entity communication capabilities and signal processing.
    """
    
    def __init__(self, range_multiplier=1.0):
        """
        Initialize the communicator component.
        
        Args:
            range_multiplier (float): Multiplier for signal range
        """
        self.range_multiplier = range_multiplier
        self.signal_types = config.SIGNAL_TYPES
        self.signal_cooldowns = {
            1: 0,  # Danger signal cooldown
            2: 0,  # Food signal cooldown
            3: 0   # Mate signal cooldown
        }
        self.cooldown_duration = 50  # Updates before signal can be sent again
        self.signal_history = []
        self.received_signals = []
        self.signal_count = 0
        
    def update(self, delta_time):
        """
        Update communication state and cooldowns.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Update cooldowns
        for signal_type in self.signal_cooldowns:
            if self.signal_cooldowns[signal_type] > 0:
                self.signal_cooldowns[signal_type] -= delta_time * config.FPS
                if self.signal_cooldowns[signal_type] < 0:
                    self.signal_cooldowns[signal_type] = 0
                    
        # Update received signals (remove old ones)
        current_time = time.time()
        self.received_signals = [s for s in self.received_signals 
                               if current_time - s["time_received"] < 10]
                               
    def emit_signal(self, signal_type, data, sender, range_override=None, entity_manager=None):
        """
        Emit a communication signal.
        
        Args:
            signal_type (int): Type of signal
            data: Signal data
            sender: Entity sending the signal
            range_override (float, optional): Override for signal range
            entity_manager (EntityManager): Entity manager instance
            
        Returns:
            bool: True if signal was emitted successfully
        """
        # Check if signal type is valid
        if signal_type not in self.signal_types:
            return False
            
        # Check cooldown
        if self.signal_cooldowns[signal_type] > 0:
            return False
            
        # Set cooldown
        self.signal_cooldowns[signal_type] = self.cooldown_duration
        
        # Get sender position
        if hasattr(sender, 'get_position_component'):
            position = sender.get_position_component().get_position()
        else:
            return False
            
        # Determine signal range
        signal_range = range_override if range_override is not None else (
            config.SIGNAL_DETECTION_RANGE * self.range_multiplier
        )
        
        # Create signal entity
        from entities.signal import Signal
        signal = Signal(position, signal_type, data, sender, signal_range)
        
        # Add to entity manager
        if entity_manager:
            entity_manager.add_signal(signal)
            
        # Add to history
        self.signal_history.append({
            "type": signal_type,
            "data": data,
            "position": position,
            "range": signal_range,
            "time_sent": time.time()
        })
        
        # Limit history size
        if len(self.signal_history) > 20:
            self.signal_history.pop(0)
            
        self.signal_count += 1
        return True
    
    def receive_signal(self, signal):
        """
        Process a received signal.
        
        Args:
            signal: Signal entity or data
            
        Returns:
            bool: True if signal was processed successfully
        """
        # Extract signal data
        if hasattr(signal, 'get_type'):
            # Signal entity
            signal_type = signal.get_type()
            signal_data = signal.get_data()
            signal_sender = signal.get_sender()
            signal_position = signal.get_position()
        else:
            # Signal data
            signal_type = signal.get("type", 0)
            signal_data = signal.get("data")
            signal_sender = signal.get("sender")
            signal_position = signal.get("position")
            
        # Check if signal type is valid
        if signal_type not in self.signal_types:
            return False
            
        # Add to received signals
        self.received_signals.append({
            "type": signal_type,
            "data": signal_data,
            "sender": signal_sender,
            "position": signal_position,
            "time_received": time.time()
        })
        
        # Limit received signals size
        if len(self.received_signals) > 30:
            self.received_signals.pop(0)
            
        return True
    
    def get_signal_range(self):
        """
        Get the current signal range.
        
        Returns:
            float: Signal range
        """
        return config.SIGNAL_DETECTION_RANGE * self.range_multiplier
    
    def set_range_multiplier(self, multiplier):
        """
        Set the range multiplier.
        
        Args:
            multiplier (float): New range multiplier
        """
        self.range_multiplier = max(0.1, multiplier)
        
    def get_signal_cooldown(self, signal_type):
        """
        Get the current cooldown for a signal type.
        
        Args:
            signal_type (int): Signal type
            
        Returns:
            float: Cooldown time remaining
        """
        return self.signal_cooldowns.get(signal_type, 0)
    
    def can_emit_signal(self, signal_type):
        """
        Check if a signal type can be emitted.
        
        Args:
            signal_type (int): Signal type
            
        Returns:
            bool: True if signal can be emitted
        """
        return self.signal_cooldowns.get(signal_type, 0) <= 0
    
    def get_signal_history(self):
        """
        Get signal emission history.
        
        Returns:
            list: Signal history
        """
        return self.signal_history
    
    def get_received_signals(self):
        """
        Get received signals.
        
        Returns:
            list: Received signals
        """
        return self.received_signals
    
    def get_recent_signals_of_type(self, signal_type):
        """
        Get recent received signals of a specific type.
        
        Args:
            signal_type (int): Signal type
            
        Returns:
            list: Recent signals of the specified type
        """
        current_time = time.time()
        return [s for s in self.received_signals 
               if s["type"] == signal_type and current_time - s["time_received"] < 5]
    
    def get_signal_count(self):
        """
        Get the total number of signals emitted.
        
        Returns:
            int: Signal count
        """
        return self.signal_count
