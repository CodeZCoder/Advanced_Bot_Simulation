"""
Communication system for bot simulation.
"""

import math
import time
import config
from entities.signal import Signal

class CommunicationSystem:
    """System for handling entity communication and signal propagation."""
    
    def __init__(self, entity_manager, world_map):
        """
        Initialize the communication system.
        
        Args:
            entity_manager: Entity manager instance
            world_map: World map instance
        """
        self.entity_manager = entity_manager
        self.world_map = world_map
        
        # Active signals
        self.active_signals = []
        
    def update(self, delta_time):
        """
        Update all signals and handle communication.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Update existing signals
        signals_to_remove = []
        
        for signal in self.active_signals:
            # Update signal
            if not signal.update(delta_time):
                signals_to_remove.append(signal)
                
        # Remove expired signals
        for signal in signals_to_remove:
            self.active_signals.remove(signal)
            
        # Process communication for all entities with communicator components
        entities = self.entity_manager.get_all_entities()
        
        for entity in entities:
            if hasattr(entity, 'get_communicator_component'):
                self._process_entity_communication(entity, delta_time)
                
    def _process_entity_communication(self, entity, delta_time):
        """
        Process communication for a single entity.
        
        Args:
            entity: Entity to process
            delta_time (float): Time delta in seconds
        """
        communicator_component = entity.get_communicator_component()
        
        # Update cooldowns
        communicator_component.update(delta_time)
        
        # Process signal reception
        if hasattr(entity, 'get_sensor_suite_component'):
            sensor_component = entity.get_sensor_suite_component()
            
            # Get entity position
            position = entity.get_position()
            
            # Check for signals in range
            perceived_signals = []
            
            for signal in self.active_signals:
                # Skip signals from this entity
                if signal.get_sender() == entity:
                    continue
                    
                # Calculate distance to signal
                signal_pos = signal.get_position()
                dx = position[0] - signal_pos[0]
                dy = position[1] - signal_pos[1]
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Check if in range
                if distance <= sensor_component.signal_detection_range:
                    # Check if signal is in current radius
                    if signal.is_in_range(position):
                        # Add to perceived signals
                        perceived_signals.append({
                            "signal": signal,
                            "type": signal.get_type(),
                            "data": signal.get_data(),
                            "position": signal_pos,
                            "distance": distance,
                            "sender": signal.get_sender()
                        })
                        
            # Update sensor with perceived signals
            sensor_component.set_perceived_signals(perceived_signals)
            
    def emit_signal(self, entity, signal_type, data=None):
        """
        Emit a signal from an entity.
        
        Args:
            entity: Entity emitting the signal
            signal_type (int): Type of signal
            data: Signal data
            
        Returns:
            bool: True if signal was emitted
        """
        # Check if entity has communicator component
        if not hasattr(entity, 'get_communicator_component'):
            return False
            
        communicator_component = entity.get_communicator_component()
        
        # Check if signal type is enabled
        if not communicator_component.is_signal_type_enabled(signal_type):
            return False
            
        # Check if on cooldown
        if not communicator_component.can_emit_signal(signal_type):
            return False
            
        # Get signal range
        signal_range = communicator_component.get_signal_range()
        
        # Create signal
        position = entity.get_position()
        signal = Signal(position, signal_type, data, entity, signal_range)
        
        # Add to active signals
        self.active_signals.append(signal)
        
        # Set cooldown
        communicator_component.set_signal_cooldown(signal_type)
        
        return True
        
    def get_active_signal_count(self):
        """
        Get the number of active signals.
        
        Returns:
            int: Number of active signals
        """
        return len(self.active_signals)
        
    def get_signals_by_type(self, signal_type):
        """
        Get active signals of a specific type.
        
        Args:
            signal_type (int): Type of signal
            
        Returns:
            list: List of signals of the specified type
        """
        return [s for s in self.active_signals if s.get_type() == signal_type]
