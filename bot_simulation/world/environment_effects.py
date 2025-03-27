"""
Environment effects module for managing global effects like day/night cycles and weather.
"""

import pygame
import random
import math
import config

class EnvironmentEffects:
    """
    Manages global environmental effects like day/night cycles and weather.
    """
    
    def __init__(self, world_map):
        """
        Initialize the environment effects manager.
        
        Args:
            world_map (WorldMap): World map instance
        """
        self.world_map = world_map
        self.time_of_day = 0  # 0 to DAY_NIGHT_CYCLE_LENGTH
        self.current_weather = "clear"
        self.weather_transition = 0
        self.weather_duration = 0
        self.weather_intensity = 0
        self.weather_particles = []
        self.weather_types = ["clear", "rain", "fog", "wind"]
        self.weather_probabilities = {
            "clear": 0.7,
            "rain": 0.1,
            "fog": 0.1,
            "wind": 0.1
        }
        self.weather_effects = {
            "clear": {},
            "rain": {"visibility_reduction": 0.3, "movement_penalty": 0.1},
            "fog": {"visibility_reduction": 0.5},
            "wind": {"movement_bonus_direction": (0, 0), "movement_factor": 0.2}
        }
        
    def update(self, delta_time):
        """
        Update environmental effects.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Update time of day
        self.time_of_day = (self.time_of_day + delta_time * config.FPS) % config.DAY_NIGHT_CYCLE_LENGTH
        
        # Update weather
        self._update_weather(delta_time)
        
    def _update_weather(self, delta_time):
        """
        Update weather conditions.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Update weather duration
        self.weather_duration -= delta_time
        
        # Check if it's time to change weather
        if self.weather_duration <= 0:
            self._change_weather()
            
        # Update weather transition
        if self.weather_transition > 0:
            self.weather_transition -= delta_time
            
        # Update weather particles
        self._update_weather_particles(delta_time)
        
    def _change_weather(self):
        """
        Change the current weather condition.
        """
        # Determine new weather type
        new_weather = self._get_random_weather()
        
        # Set transition time
        self.weather_transition = 5.0  # 5 seconds transition
        
        # Set weather duration (between 30 and 120 seconds)
        self.weather_duration = random.uniform(30, 120)
        
        # Set weather intensity
        self.weather_intensity = random.uniform(0.3, 1.0)
        
        # Set current weather
        self.current_weather = new_weather
        
        # If it's wind, set a random direction
        if new_weather == "wind":
            angle = random.uniform(0, 2 * math.pi)
            self.weather_effects["wind"]["movement_bonus_direction"] = (
                math.cos(angle),
                math.sin(angle)
            )
            
        # Clear weather particles
        self.weather_particles.clear()
        
    def _get_random_weather(self):
        """
        Get a random weather type based on probabilities.
        
        Returns:
            str: Weather type
        """
        # Get a random value
        value = random.random()
        
        # Determine weather type
        cumulative = 0
        for weather_type, probability in self.weather_probabilities.items():
            cumulative += probability
            if value <= cumulative:
                return weather_type
                
        # Default to clear
        return "clear"
    
    def _update_weather_particles(self, delta_time):
        """
        Update weather particles (rain, snow, etc.).
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Update existing particles
        i = 0
        while i < len(self.weather_particles):
            particle = self.weather_particles[i]
            
            # Update position
            particle["position"] = (
                particle["position"][0] + particle["velocity"][0] * delta_time,
                particle["position"][1] + particle["velocity"][1] * delta_time
            )
            
            # Check if particle is out of bounds
            if not self.world_map.get_bounds().collidepoint(particle["position"]):
                self.weather_particles.pop(i)
            else:
                i += 1
                
        # Add new particles based on weather type
        if self.current_weather == "rain" and self.weather_intensity > 0:
            # Add rain particles
            particle_count = int(20 * self.weather_intensity)
            for _ in range(particle_count):
                # Random position at the top of the screen
                x = random.uniform(0, self.world_map.get_bounds().width)
                y = random.uniform(-10, 0)
                
                # Add particle
                self.weather_particles.append({
                    "type": "rain",
                    "position": (x, y),
                    "velocity": (random.uniform(-20, 20), random.uniform(100, 200)),
                    "size": random.uniform(2, 5),
                    "color": (100, 100, 255, int(128 * self.weather_intensity))
                })
                
    def is_daytime(self):
        """
        Check if it's currently daytime.
        
        Returns:
            bool: True if it's daytime
        """
        return self.time_of_day < (config.DAY_NIGHT_CYCLE_LENGTH / 2)
    
    def get_daylight_factor(self):
        """
        Get the current daylight factor (0 to 1).
        
        Returns:
            float: Daylight factor
        """
        # Calculate position in day/night cycle (0 to 1)
        cycle_position = self.time_of_day / config.DAY_NIGHT_CYCLE_LENGTH
        
        # Convert to daylight factor
        if cycle_position < 0.25:  # Dawn
            return cycle_position * 4
        elif cycle_position < 0.75:  # Day to dusk
            return 1.0 - (cycle_position - 0.25) * 2
        else:  # Night
            return 0.0
            
    def get_weather_effect(self, effect_name):
        """
        Get the current value of a weather effect.
        
        Args:
            effect_name (str): Name of the effect
            
        Returns:
            float or tuple: Effect value
        """
        if self.current_weather in self.weather_effects:
            weather_data = self.weather_effects[self.current_weather]
            if effect_name in weather_data:
                # Scale by intensity
                value = weather_data[effect_name]
                if isinstance(value, (int, float)):
                    return value * self.weather_intensity
                elif isinstance(value, tuple):
                    return value  # Direction vectors aren't scaled
                    
        return 0.0
    
    def get_current_weather(self):
        """
        Get the current weather type.
        
        Returns:
            str: Current weather type
        """
        return self.current_weather
    
    def get_weather_intensity(self):
        """
        Get the current weather intensity.
        
        Returns:
            float: Weather intensity (0 to 1)
        """
        return self.weather_intensity
    
    def get_weather_particles(self):
        """
        Get the current weather particles.
        
        Returns:
            list: Weather particles
        """
        return self.weather_particles
    
    def draw(self, surface, camera_rect):
        """
        Draw environmental effects.
        
        Args:
            surface (pygame.Surface): Surface to draw on
            camera_rect (pygame.Rect): Camera view rectangle
        """
        # Apply daylight tint
        self._apply_daylight_tint(surface)
        
        # Draw weather particles
        self._draw_weather_particles(surface, camera_rect)
        
    def _apply_daylight_tint(self, surface):
        """
        Apply a daylight tint to the surface.
        
        Args:
            surface (pygame.Surface): Surface to tint
        """
        daylight = self.get_daylight_factor()
        
        # Create a tint overlay
        if daylight < 1.0:
            # Create a dark overlay for night
            darkness = 1.0 - daylight
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 50, int(128 * darkness)))  # Blue-ish night tint
            surface.blit(overlay, (0, 0))
            
    def _draw_weather_particles(self, surface, camera_rect):
        """
        Draw weather particles.
        
        Args:
            surface (pygame.Surface): Surface to draw on
            camera_rect (pygame.Rect): Camera view rectangle
        """
        # Draw particles
        for particle in self.weather_particles:
            # Check if particle is visible
            screen_pos = (
                particle["position"][0] - camera_rect.x,
                particle["position"][1] - camera_rect.y
            )
            
            if (0 <= screen_pos[0] <= surface.get_width() and
                0 <= screen_pos[1] <= surface.get_height()):
                
                # Draw based on particle type
                if particle["type"] == "rain":
                    # Draw a line for rain
                    end_pos = (
                        screen_pos[0] + particle["velocity"][0] * 0.05,
                        screen_pos[1] + particle["velocity"][1] * 0.05
                    )
                    pygame.draw.line(
                        surface,
                        particle["color"],
                        screen_pos,
                        end_pos,
                        1
                    )
