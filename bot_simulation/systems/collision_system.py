"""
Collision system for bot simulation.
"""

import math
import config

class CollisionSystem:
    """System for handling entity collisions."""
    
    def __init__(self, entity_manager, world_map):
        """
        Initialize the collision system.
        
        Args:
            entity_manager: Entity manager instance
            world_map: World map instance
        """
        self.entity_manager = entity_manager
        self.world_map = world_map
        
    def update(self, delta_time):
        """
        Update all entity collisions.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Use quadtree for efficient collision detection
        entities = self.entity_manager.get_all_entities()
        
        # Check collisions between entities
        for entity1 in entities:
            if not hasattr(entity1, 'get_position') or not hasattr(entity1, 'get_radius'):
                continue
                
            position1 = entity1.get_position()
            radius1 = entity1.get_radius()
            
            # Get nearby entities from quadtree
            nearby_entities = self.world_map.get_nearby_entities(position1, radius1 * 2)
            
            for entity2 in nearby_entities:
                # Skip self
                if entity1 == entity2:
                    continue
                    
                # Skip if entity2 doesn't have position or radius
                if not hasattr(entity2, 'get_position') or not hasattr(entity2, 'get_radius'):
                    continue
                    
                position2 = entity2.get_position()
                radius2 = entity2.get_radius()
                
                # Check collision
                dx = position1[0] - position2[0]
                dy = position1[1] - position2[1]
                distance_squared = dx * dx + dy * dy
                min_distance = radius1 + radius2
                
                if distance_squared < min_distance * min_distance:
                    # Collision detected
                    self._handle_collision(entity1, entity2)
                    
        # Check collisions with obstacles
        for entity in entities:
            if not hasattr(entity, 'get_position') or not hasattr(entity, 'get_radius'):
                continue
                
            position = entity.get_position()
            radius = entity.get_radius()
            
            # Get nearby obstacles
            obstacles = self.world_map.get_nearby_obstacles(position, radius * 2)
            
            for obstacle in obstacles:
                if obstacle.collides_with_circle(position, radius):
                    # Collision detected
                    self._handle_obstacle_collision(entity, obstacle)
                    
    def _handle_collision(self, entity1, entity2):
        """
        Handle collision between two entities.
        
        Args:
            entity1: First entity
            entity2: Second entity
        """
        # Handle specific entity type collisions
        if hasattr(entity1, 'is_bot') and entity1.is_bot():
            if hasattr(entity2, 'is_bot') and entity2.is_bot():
                # Bot-bot collision
                self._handle_bot_bot_collision(entity1, entity2)
            elif hasattr(entity2, 'is_resource') and entity2.is_resource():
                # Bot-resource collision
                self._handle_bot_resource_collision(entity1, entity2)
        elif hasattr(entity1, 'is_resource') and entity1.is_resource():
            if hasattr(entity2, 'is_bot') and entity2.is_bot():
                # Resource-bot collision
                self._handle_bot_resource_collision(entity2, entity1)
                
    def _handle_bot_bot_collision(self, bot1, bot2):
        """
        Handle collision between two bots.
        
        Args:
            bot1: First bot
            bot2: Second bot
        """
        # Get positions
        pos1 = bot1.get_position()
        pos2 = bot2.get_position()
        
        # Calculate collision vector
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Avoid division by zero
        if distance == 0:
            dx = 1.0
            dy = 0.0
            distance = 1.0
            
        # Normalize collision vector
        dx /= distance
        dy /= distance
        
        # Calculate overlap
        overlap = bot1.get_radius() + bot2.get_radius() - distance
        
        if overlap <= 0:
            return
            
        # Calculate mass (if available)
        mass1 = getattr(bot1, 'mass', 1.0)
        mass2 = getattr(bot2, 'mass', 1.0)
        total_mass = mass1 + mass2
        
        # Calculate separation based on mass
        separation1 = overlap * (mass2 / total_mass)
        separation2 = overlap * (mass1 / total_mass)
        
        # Separate bots
        pos_component1 = bot1.get_position_component()
        pos_component2 = bot2.get_position_component()
        
        pos_component1.x += dx * separation1
        pos_component1.y += dy * separation1
        pos_component2.x -= dx * separation2
        pos_component2.y -= dy * separation2
        
        # Handle velocity changes
        vel_component1 = bot1.get_velocity_component()
        vel_component2 = bot2.get_velocity_component()
        
        # Calculate velocity along collision vector
        v1 = vel_component1.dx * dx + vel_component1.dy * dy
        v2 = vel_component2.dx * dx + vel_component2.dy * dy
        
        # Skip if bots are moving away from each other
        if v1 - v2 > 0:
            return
            
        # Calculate new velocities (elastic collision)
        new_v1 = ((mass1 - mass2) * v1 + 2 * mass2 * v2) / total_mass
        new_v2 = ((mass2 - mass1) * v2 + 2 * mass1 * v1) / total_mass
        
        # Apply new velocities
        vel_component1.dx += (new_v1 - v1) * dx
        vel_component1.dy += (new_v1 - v1) * dy
        vel_component2.dx += (new_v2 - v2) * dx
        vel_component2.dy += (new_v2 - v2) * dy
        
        # Apply collision damping
        vel_component1.dx *= config.COLLISION_DAMPING
        vel_component1.dy *= config.COLLISION_DAMPING
        vel_component2.dx *= config.COLLISION_DAMPING
        vel_component2.dy *= config.COLLISION_DAMPING
        
    def _handle_bot_resource_collision(self, bot, resource):
        """
        Handle collision between bot and resource.
        
        Args:
            bot: Bot entity
            resource: Resource entity
        """
        # Check if bot has an action component
        if not hasattr(bot, 'get_action_component'):
            return
            
        # Check if bot is trying to eat
        action_component = bot.get_action_component()
        if action_component.is_action_active("eat"):
            # Bot is trying to eat, handled by AI system
            pass
        else:
            # Just a collision, separate entities
            pos1 = bot.get_position()
            pos2 = resource.get_position()
            
            # Calculate collision vector
            dx = pos1[0] - pos2[0]
            dy = pos1[1] - pos2[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Avoid division by zero
            if distance == 0:
                dx = 1.0
                dy = 0.0
                distance = 1.0
                
            # Normalize collision vector
            dx /= distance
            dy /= distance
            
            # Calculate overlap
            overlap = bot.get_radius() + resource.get_radius() - distance
            
            if overlap <= 0:
                return
                
            # Separate entities (only move bot)
            pos_component = bot.get_position_component()
            pos_component.x += dx * overlap
            pos_component.y += dy * overlap
            
    def _handle_obstacle_collision(self, entity, obstacle):
        """
        Handle collision between entity and obstacle.
        
        Args:
            entity: Entity colliding with obstacle
            obstacle: Obstacle entity
        """
        # Get entity position
        position = entity.get_position()
        radius = entity.get_radius()
        
        # Get obstacle rectangle
        obstacle_rect = obstacle.get_rect()
        
        # Calculate closest point on rectangle to entity
        closest_x = max(obstacle_rect.left, min(position[0], obstacle_rect.right))
        closest_y = max(obstacle_rect.top, min(position[1], obstacle_rect.bottom))
        
        # Calculate direction from closest point to entity
        dx = position[0] - closest_x
        dy = position[1] - closest_y
        
        # Normalize direction
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            dx /= distance
            dy /= distance
            
        # Calculate minimum separation distance
        min_distance = radius
        
        # Calculate new position
        if distance < min_distance:
            # Move entity away from obstacle
            separation = min_distance - distance
            new_x = closest_x + dx * min_distance
            new_y = closest_y + dy * min_distance
            
            # Update position
            pos_component = entity.get_position_component()
            pos_component.set_position(new_x, new_y)
            
            # Reflect velocity (bounce)
            if hasattr(entity, 'get_velocity_component'):
                vel_component = entity.get_velocity_component()
                
                # Calculate dot product
                dot_product = vel_component.dx * dx + vel_component.dy * dy
                
                # Only reflect if moving towards obstacle
                if dot_product < 0:
                    # Reflect velocity
                    vel_component.dx -= 2 * dot_product * dx
                    vel_component.dy -= 2 * dot_product * dy
                    
                    # Apply bounce damping
                    vel_component.dx *= config.BOUNCE_DAMPING
                    vel_component.dy *= config.BOUNCE_DAMPING
