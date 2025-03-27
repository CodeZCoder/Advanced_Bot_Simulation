"""
Movement system for bot simulation.
"""

import math
import random
import config

class MovementSystem:
    """System for handling entity movement and physics."""
    
    def __init__(self, entity_manager, world_map):
        """
        Initialize the movement system.
        
        Args:
            entity_manager: Entity manager instance
            world_map: World map instance
        """
        self.entity_manager = entity_manager
        self.world_map = world_map
        
    def update(self, delta_time):
        """
        Update all entity positions and handle collisions.
        
        Args:
            delta_time (float): Time delta in seconds
        """
        # Get all entities with position and velocity components
        entities = self.entity_manager.get_all_entities()
        movable_entities = []
        
        for entity in entities:
            if hasattr(entity, 'get_position_component') and hasattr(entity, 'get_velocity_component'):
                movable_entities.append(entity)
                
        # Update positions
        for entity in movable_entities:
            self._update_entity_position(entity, delta_time)
            
        # Handle collisions
        self._handle_collisions(movable_entities)
        
    def _update_entity_position(self, entity, delta_time):
        """
        Update an entity's position based on velocity.
        
        Args:
            entity: Entity to update
            delta_time (float): Time delta in seconds
        """
        position_component = entity.get_position_component()
        velocity_component = entity.get_velocity_component()
        
        # Apply velocity to position
        new_x = position_component.x + velocity_component.dx * delta_time
        new_y = position_component.y + velocity_component.dy * delta_time
        
        # Ensure position is within world bounds
        world_bounds = self.world_map.get_bounds()
        new_x = max(0, min(world_bounds.width, new_x))
        new_y = max(0, min(world_bounds.height, new_y))
        
        # Check for collision with obstacles
        if hasattr(entity, 'get_radius'):
            radius = entity.get_radius()
            obstacles = self.world_map.get_nearby_obstacles((new_x, new_y), radius * 2)
            
            for obstacle in obstacles:
                if obstacle.collides_with_circle((new_x, new_y), radius):
                    # Collision detected, adjust position
                    self._handle_obstacle_collision(entity, obstacle, new_x, new_y)
                    
                    # Get updated position
                    new_x = position_component.x
                    new_y = position_component.y
                    break
        
        # Update position
        position_component.set_position(new_x, new_y)
        
        # Apply friction/drag
        if hasattr(entity, 'is_bot') and entity.is_bot():
            # Bots have more complex movement with acceleration and friction
            friction = config.BOT_FRICTION
            velocity_component.dx *= (1 - friction * delta_time)
            velocity_component.dy *= (1 - friction * delta_time)
            
            # Stop if velocity is very small
            if abs(velocity_component.dx) < 0.1 and abs(velocity_component.dy) < 0.1:
                velocity_component.dx = 0
                velocity_component.dy = 0
        
    def _handle_obstacle_collision(self, entity, obstacle, new_x, new_y):
        """
        Handle collision between entity and obstacle.
        
        Args:
            entity: Entity colliding with obstacle
            obstacle: Obstacle entity
            new_x (float): New x position
            new_y (float): New y position
        """
        position_component = entity.get_position_component()
        velocity_component = entity.get_velocity_component()
        
        # Get obstacle rectangle
        obstacle_rect = obstacle.get_rect()
        
        # Calculate closest point on rectangle to entity
        closest_x = max(obstacle_rect.left, min(new_x, obstacle_rect.right))
        closest_y = max(obstacle_rect.top, min(new_y, obstacle_rect.bottom))
        
        # Calculate direction from closest point to entity
        dx = new_x - closest_x
        dy = new_y - closest_y
        
        # Normalize direction
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            dx /= distance
            dy /= distance
            
        # Calculate minimum separation distance
        min_distance = entity.get_radius()
        
        # Calculate new position
        if distance < min_distance:
            # Move entity away from obstacle
            separation = min_distance - distance
            new_x = closest_x + dx * min_distance
            new_y = closest_y + dy * min_distance
            
            # Update position
            position_component.set_position(new_x, new_y)
            
            # Reflect velocity (bounce)
            if dx * velocity_component.dx + dy * velocity_component.dy < 0:
                # Dot product is negative, velocity is towards obstacle
                dot_product = velocity_component.dx * dx + velocity_component.dy * dy
                velocity_component.dx -= 2 * dot_product * dx
                velocity_component.dy -= 2 * dot_product * dy
                
                # Apply bounce damping
                velocity_component.dx *= config.BOUNCE_DAMPING
                velocity_component.dy *= config.BOUNCE_DAMPING
        
    def _handle_collisions(self, entities):
        """
        Handle collisions between entities.
        
        Args:
            entities (list): List of entities to check for collisions
        """
        # Use quadtree for efficient collision detection
        for i, entity1 in enumerate(entities):
            if not hasattr(entity1, 'get_radius'):
                continue
                
            position1 = entity1.get_position()
            radius1 = entity1.get_radius()
            
            # Get nearby entities from quadtree
            nearby_entities = self.world_map.get_nearby_entities(position1, radius1 * 2)
            
            for entity2 in nearby_entities:
                # Skip self
                if entity1 == entity2:
                    continue
                    
                # Skip if entity2 doesn't have radius
                if not hasattr(entity2, 'get_radius'):
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
                    self._resolve_entity_collision(entity1, entity2)
    
    def _resolve_entity_collision(self, entity1, entity2):
        """
        Resolve collision between two entities.
        
        Args:
            entity1: First entity
            entity2: Second entity
        """
        # Get components
        position1 = entity1.get_position_component()
        position2 = entity2.get_position_component()
        
        # Calculate collision vector
        dx = position1.x - position2.x
        dy = position1.y - position2.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Avoid division by zero
        if distance == 0:
            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
            distance = math.sqrt(dx * dx + dy * dy)
            
        # Normalize collision vector
        dx /= distance
        dy /= distance
        
        # Calculate overlap
        radius1 = entity1.get_radius()
        radius2 = entity2.get_radius()
        overlap = radius1 + radius2 - distance
        
        # Only resolve if there's an overlap
        if overlap <= 0:
            return
            
        # Calculate mass (if available)
        mass1 = getattr(entity1, 'mass', 1.0)
        mass2 = getattr(entity2, 'mass', 1.0)
        total_mass = mass1 + mass2
        
        # Calculate separation based on mass
        separation1 = overlap * (mass2 / total_mass)
        separation2 = overlap * (mass1 / total_mass)
        
        # Separate entities
        position1.x += dx * separation1
        position1.y += dy * separation1
        position2.x -= dx * separation2
        position2.y -= dy * separation2
        
        # Handle velocity changes if both entities have velocity components
        if (hasattr(entity1, 'get_velocity_component') and 
            hasattr(entity2, 'get_velocity_component')):
            
            velocity1 = entity1.get_velocity_component()
            velocity2 = entity2.get_velocity_component()
            
            # Calculate velocity along collision vector
            v1 = velocity1.dx * dx + velocity1.dy * dy
            v2 = velocity2.dx * dx + velocity2.dy * dy
            
            # Skip if entities are moving away from each other
            if v1 - v2 > 0:
                return
                
            # Calculate new velocities (elastic collision)
            new_v1 = ((mass1 - mass2) * v1 + 2 * mass2 * v2) / total_mass
            new_v2 = ((mass2 - mass1) * v2 + 2 * mass1 * v1) / total_mass
            
            # Apply new velocities
            velocity1.dx += (new_v1 - v1) * dx
            velocity1.dy += (new_v1 - v1) * dy
            velocity2.dx += (new_v2 - v2) * dx
            velocity2.dy += (new_v2 - v2) * dy
            
            # Apply collision damping
            velocity1.dx *= config.COLLISION_DAMPING
            velocity1.dy *= config.COLLISION_DAMPING
            velocity2.dx *= config.COLLISION_DAMPING
            velocity2.dy *= config.COLLISION_DAMPING
