"""
Stats display module for rendering simulation statistics.
"""

import pygame
import math
import time
import config

class StatsDisplay:
    """Display for simulation statistics and information."""
    
    def __init__(self, screen, entity_manager, world_map, evolution_system, energy_system):
        """
        Initialize the stats display.
        
        Args:
            screen (pygame.Surface): Screen surface to draw on
            entity_manager: Entity manager instance
            world_map: World map instance
            evolution_system: Evolution system instance
            energy_system: Energy system instance
        """
        self.screen = screen
        self.entity_manager = entity_manager
        self.world_map = world_map
        self.evolution_system = evolution_system
        self.energy_system = energy_system
        
        # Initialize fonts
        pygame.font.init()
        self.title_font = pygame.font.SysFont('Arial', 20, bold=True)
        self.stats_font = pygame.font.SysFont('Arial', 16)
        self.small_font = pygame.font.SysFont('Arial', 12)
        
        # Colors
        self.text_color = (255, 255, 255)
        self.title_color = (255, 220, 100)
        self.panel_color = (30, 30, 30, 180)
        self.graph_color = (100, 200, 100)
        self.grid_color = (70, 70, 70)
        
        # Stats panel position and size
        self.panel_rect = pygame.Rect(10, 10, 250, 200)
        
        # Selected entity
        self.selected_entity = None
        self.selection_time = 0
        
        # Historical data for graphs
        self.history_length = 300  # Number of data points to store
        self.population_history = [0] * self.history_length
        self.energy_history = [0] * self.history_length
        self.birth_history = [0] * self.history_length
        self.death_history = [0] * self.history_length
        self.last_update_time = time.time()
        self.update_interval = 1.0  # Update history every second
        
        # Graph panel
        self.graph_rect = pygame.Rect(10, 220, 250, 150)
        self.current_graph = "population"  # Default graph to show
        
    def update(self):
        """Update the stats display."""
        # Update historical data
        current_time = time.time()
        if current_time - self.last_update_time >= self.update_interval:
            # Shift histories
            self.population_history.pop(0)
            self.energy_history.pop(0)
            self.birth_history.pop(0)
            self.death_history.pop(0)
            
            # Add new data points
            self.population_history.append(len(self.entity_manager.get_all_bots()))
            self.energy_history.append(self.energy_system.get_average_bot_energy())
            self.birth_history.append(self.evolution_system.get_birth_count())
            self.death_history.append(self.evolution_system.get_death_count())
            
            self.last_update_time = current_time
            
    def draw(self):
        """Draw the stats display."""
        # Draw stats panel
        self._draw_stats_panel()
        
        # Draw graph panel
        self._draw_graph_panel()
        
        # Draw selected entity info if any
        if self.selected_entity:
            self._draw_selected_entity_info()
            
    def _draw_stats_panel(self):
        """Draw the main statistics panel."""
        # Draw panel background
        panel_surface = pygame.Surface((self.panel_rect.width, self.panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill(self.panel_color)
        self.screen.blit(panel_surface, self.panel_rect)
        
        # Draw title
        title = self.title_font.render("Simulation Statistics", True, self.title_color)
        self.screen.blit(title, (self.panel_rect.x + 10, self.panel_rect.y + 10))
        
        # Get statistics
        bot_count = len(self.entity_manager.get_all_bots())
        resource_count = len(self.entity_manager.get_all_resources())
        signal_count = len(self.entity_manager.get_all_signals())
        avg_energy = self.energy_system.get_average_bot_energy()
        birth_count = self.evolution_system.get_birth_count()
        death_count = self.evolution_system.get_death_count()
        highest_gen = self.evolution_system.get_highest_generation()
        
        # Format statistics
        stats = [
            f"Population: {bot_count}",
            f"Resources: {resource_count}",
            f"Active Signals: {signal_count}",
            f"Avg. Energy: {avg_energy:.1f}",
            f"Births: {birth_count}",
            f"Deaths: {death_count}",
            f"Highest Generation: {highest_gen}"
        ]
        
        # Draw statistics
        y_offset = 40
        for stat in stats:
            text = self.stats_font.render(stat, True, self.text_color)
            self.screen.blit(text, (self.panel_rect.x + 15, self.panel_rect.y + y_offset))
            y_offset += 20
            
        # Draw simulation time
        sim_time = pygame.time.get_ticks() / 1000
        hours = int(sim_time / 3600)
        minutes = int((sim_time % 3600) / 60)
        seconds = int(sim_time % 60)
        
        time_text = f"Time: {hours:02d}:{minutes:02d}:{seconds:02d}"
        text = self.stats_font.render(time_text, True, self.text_color)
        self.screen.blit(text, (self.panel_rect.x + 15, self.panel_rect.y + y_offset))
        
    def _draw_graph_panel(self):
        """Draw the graph panel."""
        # Draw panel background
        panel_surface = pygame.Surface((self.graph_rect.width, self.graph_rect.height), pygame.SRCALPHA)
        panel_surface.fill(self.panel_color)
        self.screen.blit(panel_surface, self.graph_rect)
        
        # Draw title based on current graph
        if self.current_graph == "population":
            title = self.title_font.render("Population History", True, self.title_color)
        elif self.current_graph == "energy":
            title = self.title_font.render("Energy History", True, self.title_color)
        elif self.current_graph == "births":
            title = self.title_font.render("Birth History", True, self.title_color)
        elif self.current_graph == "deaths":
            title = self.title_font.render("Death History", True, self.title_color)
            
        self.screen.blit(title, (self.graph_rect.x + 10, self.graph_rect.y + 5))
        
        # Draw graph
        graph_area = pygame.Rect(
            self.graph_rect.x + 30,
            self.graph_rect.y + 30,
            self.graph_rect.width - 40,
            self.graph_rect.height - 40
        )
        
        # Draw grid
        for i in range(5):
            y = graph_area.y + i * graph_area.height // 4
            pygame.draw.line(
                self.screen,
                self.grid_color,
                (graph_area.x, y),
                (graph_area.x + graph_area.width, y),
                1
            )
            
        for i in range(6):
            x = graph_area.x + i * graph_area.width // 5
            pygame.draw.line(
                self.screen,
                self.grid_color,
                (x, graph_area.y),
                (x, graph_area.y + graph_area.height),
                1
            )
            
        # Get data based on current graph
        if self.current_graph == "population":
            data = self.population_history
            max_value = max(data) if max(data) > 0 else 1
        elif self.current_graph == "energy":
            data = self.energy_history
            max_value = max(data) if max(data) > 0 else 1
        elif self.current_graph == "births":
            data = self.birth_history
            max_value = max(data) if max(data) > 0 else 1
        elif self.current_graph == "deaths":
            data = self.death_history
            max_value = max(data) if max(data) > 0 else 1
            
        # Draw graph line
        points = []
        for i, value in enumerate(data):
            x = graph_area.x + i * graph_area.width // (len(data) - 1)
            y = graph_area.y + graph_area.height - (value / max_value) * graph_area.height
            points.append((x, y))
            
        if len(points) > 1:
            pygame.draw.lines(self.screen, self.graph_color, False, points, 2)
            
        # Draw current value
        current_value = data[-1]
        value_text = self.stats_font.render(f"Current: {current_value}", True, self.text_color)
        self.screen.blit(value_text, (self.graph_rect.x + 10, self.graph_rect.y + self.graph_rect.height - 25))
        
    def _draw_selected_entity_info(self):
        """Draw information about the selected entity."""
        if not self.selected_entity:
            return
            
        # Check if entity still exists
        if self.selected_entity not in self.entity_manager.get_all_entities():
            self.selected_entity = None
            return
            
        # Create panel
        panel_rect = pygame.Rect(
            self.screen.get_width() - 260,
            10,
            250,
            300
        )
        
        # Draw panel background
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill(self.panel_color)
        self.screen.blit(panel_surface, panel_rect)
        
        # Draw title
        if hasattr(self.selected_entity, 'is_bot') and self.selected_entity.is_bot():
            title = self.title_font.render("Bot Information", True, self.title_color)
        elif hasattr(self.selected_entity, 'is_resource') and self.selected_entity.is_resource():
            title = self.title_font.render("Resource Information", True, self.title_color)
        else:
            title = self.title_font.render("Entity Information", True, self.title_color)
            
        self.screen.blit(title, (panel_rect.x + 10, panel_rect.y + 10))
        
        # Draw entity information
        y_offset = 40
        
        # Common information
        entity_id = getattr(self.selected_entity, 'id', 'Unknown')
        position = self.selected_entity.get_position()
        
        info = [
            f"ID: {entity_id}",
            f"Position: ({position[0]:.1f}, {position[1]:.1f})"
        ]
        
        # Bot-specific information
        if hasattr(self.selected_entity, 'is_bot') and self.selected_entity.is_bot():
            # Get components
            energy_component = self.selected_entity.get_energy_component()
            genetic_component = self.selected_entity.get_genetic_component()
            
            # Add bot info
            info.extend([
                f"Age: {self.selected_entity.get_age():.1f}s",
                f"Generation: {self.selected_entity.generation}",
                f"Mature: {'Yes' if self.selected_entity.is_mature() else 'No'}",
                f"Energy: {energy_component.get_energy():.1f}/{energy_component.get_max_energy():.1f}",
                f"Reproductions: {self.selected_entity.reproduction_count}"
            ])
            
            # Add genetic info
            genes = genetic_component.get_all_genes()
            info.append("")
            info.append("Genetics:")
            
            for gene, value in genes.items():
                info.append(f"  {gene}: {value:.2f}")
                
            # Add AI state if available
            if hasattr(self.selected_entity, 'get_ai_state_component'):
                ai_state_component = self.selected_entity.get_ai_state_component()
                current_state = ai_state_component.get_current_state()
                
                info.append("")
                info.append(f"AI State: {current_state}")
                
        # Resource-specific information
        elif hasattr(self.selected_entity, 'is_resource') and self.selected_entity.is_resource():
            info.extend([
                f"Energy: {self.selected_entity.get_energy():.1f}",
                f"Radius: {self.selected_entity.get_radius():.1f}"
            ])
            
        # Draw information
        for line in info:
            text = self.stats_font.render(line, True, self.text_color)
            self.screen.blit(text, (panel_rect.x + 15, panel_rect.y + y_offset))
            y_offset += 20
            
    def handle_click(self, position):
        """
        Handle mouse click to select entities or change graph.
        
        Args:
            position (tuple): Mouse position (x, y)
            
        Returns:
            bool: True if click was handled
        """
        # Check if click is in graph panel
        if self.graph_rect.collidepoint(position):
            # Cycle through graph types
            if self.current_graph == "population":
                self.current_graph = "energy"
            elif self.current_graph == "energy":
                self.current_graph = "births"
            elif self.current_graph == "births":
                self.current_graph = "deaths"
            elif self.current_graph == "deaths":
                self.current_graph = "population"
                
            return True
            
        # Check if click is in the world view
        if (position[0] > self.panel_rect.right and 
            position[1] > self.panel_rect.bottom and
            position[0] < self.screen.get_width() and
            position[1] < self.screen.get_height()):
            
            # Convert screen position to world position
            camera_rect = self.world_map.get_camera_rect()
            zoom = self.world_map.get_zoom()
            
            world_x = position[0] / zoom + camera_rect.x
            world_y = position[1] / zoom + camera_rect.y
            
            # Find closest entity
            closest_entity = None
            closest_distance = float('inf')
            
            for entity in self.entity_manager.get_all_entities():
                if hasattr(entity, 'get_position'):
                    entity_pos = entity.get_position()
                    dx = entity_pos[0] - world_x
                    dy = entity_pos[1] - world_y
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    # Check if within selection radius
                    selection_radius = getattr(entity, 'get_radius', lambda: 10)()
                    if distance <= selection_radius and distance < closest_distance:
                        closest_entity = entity
                        closest_distance = distance
                        
            # Select the entity
            self.selected_entity = closest_entity
            self.selection_time = time.time()
            
            return True
            
        return False
        
    def toggle_graph(self):
        """Toggle between different graph types."""
        if self.current_graph == "population":
            self.current_graph = "energy"
        elif self.current_graph == "energy":
            self.current_graph = "births"
        elif self.current_graph == "births":
            self.current_graph = "deaths"
        elif self.current_graph == "deaths":
            self.current_graph = "population"
