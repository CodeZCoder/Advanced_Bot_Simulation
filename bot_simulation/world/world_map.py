"""
World map module for defining the structure and properties of the world space.
Implements a Quadtree for efficient spatial partitioning.
"""

import pygame
import config

class Quadtree:
    """
    Quadtree implementation for efficient spatial partitioning.
    """
    
    def __init__(self, level, bounds):
        """
        Initialize a quadtree node.
        
        Args:
            level (int): Current level of the quadtree
            bounds (pygame.Rect): Boundaries of this quadtree node
        """
        self.level = level
        self.bounds = bounds
        self.objects = []
        self.nodes = []
        self.is_divided = False
        
    def clear(self):
        """
        Clear the quadtree.
        """
        self.objects.clear()
        
        for i in range(len(self.nodes)):
            if self.nodes[i]:
                self.nodes[i].clear()
                
        self.is_divided = False
        self.nodes.clear()
        
    def split(self):
        """
        Split the quadtree into four quadrants.
        """
        x = self.bounds.x
        y = self.bounds.y
        subWidth = self.bounds.width / 2
        subHeight = self.bounds.height / 2
        
        # Create four children
        self.nodes.append(Quadtree(self.level + 1, pygame.Rect(x, y, subWidth, subHeight)))
        self.nodes.append(Quadtree(self.level + 1, pygame.Rect(x + subWidth, y, subWidth, subHeight)))
        self.nodes.append(Quadtree(self.level + 1, pygame.Rect(x, y + subHeight, subWidth, subHeight)))
        self.nodes.append(Quadtree(self.level + 1, pygame.Rect(x + subWidth, y + subHeight, subWidth, subHeight)))
        
        self.is_divided = True
        
    def get_index(self, rect):
        """
        Determine which quadrant an object belongs to.
        
        Args:
            rect (pygame.Rect): Rectangle to check
            
        Returns:
            int: Index of the quadrant (-1 if it can't fit in a single quadrant)
        """
        index = -1
        center_x = self.bounds.x + self.bounds.width / 2
        center_y = self.bounds.y + self.bounds.height / 2
        
        # Object can completely fit within the top quadrants
        top = rect.y < center_y and rect.y + rect.height < center_y
        # Object can completely fit within the bottom quadrants
        bottom = rect.y > center_y
        
        # Object can completely fit within the left quadrants
        if rect.x < center_x and rect.x + rect.width < center_x:
            if top:
                index = 0
            elif bottom:
                index = 2
        # Object can completely fit within the right quadrants
        elif rect.x > center_x:
            if top:
                index = 1
            elif bottom:
                index = 3
                
        return index
    
    def insert(self, obj):
        """
        Insert an object into the quadtree.
        
        Args:
            obj (dict): Object with 'entity' and 'rect' keys
        """
        # If this node is divided, insert into appropriate child
        if self.is_divided:
            index = self.get_index(obj["rect"])
            
            if index != -1:
                self.nodes[index].insert(obj)
                return
                
        # Add object to this node
        self.objects.append(obj)
        
        # Check if we need to split
        if len(self.objects) > config.QUADTREE_MAX_OBJECTS and self.level < config.QUADTREE_MAX_LEVELS:
            # Split if this is the first time
            if not self.is_divided:
                self.split()
                
            # Redistribute objects
            i = 0
            while i < len(self.objects):
                index = self.get_index(self.objects[i]["rect"])
                
                if index != -1:
                    self.nodes[index].insert(self.objects.pop(i))
                else:
                    i += 1
                    
    def retrieve(self, return_objects, rect):
        """
        Retrieve all objects that could collide with the given rectangle.
        
        Args:
            return_objects (list): List to fill with found objects
            rect (pygame.Rect): Rectangle to check
            
        Returns:
            list: List of objects that could collide
        """
        index = self.get_index(rect)
        
        if index != -1 and self.is_divided:
            self.nodes[index].retrieve(return_objects, rect)
            
        # Add all objects at this level
        return_objects.extend(self.objects)
        
        return return_objects
    
    def draw(self, surface, camera_rect, color=(200, 200, 200), width=1):
        """
        Draw the quadtree for debugging purposes.
        
        Args:
            surface (pygame.Surface): Surface to draw on
            camera_rect (pygame.Rect): Camera view rectangle
            color (tuple): RGB color
            width (int): Line width
        """
        # Only draw if this node is visible in the camera
        if self.bounds.colliderect(camera_rect):
            # Draw this node's bounds
            draw_rect = pygame.Rect(
                self.bounds.x - camera_rect.x,
                self.bounds.y - camera_rect.y,
                self.bounds.width,
                self.bounds.height
            )
            pygame.draw.rect(surface, color, draw_rect, width)
            
            # Draw children
            if self.is_divided:
                for node in self.nodes:
                    node.draw(surface, camera_rect, color, width)


class WorldMap:
    """
    Defines the structure, boundaries, and properties of the world space.
    """
    
    def __init__(self, width, height):
        """
        Initialize the world map.
        
        Args:
            width (int): Width of the world
            height (int): Height of the world
        """
        self.width = width
        self.height = height
        self.bounds = pygame.Rect(0, 0, width, height)
        self.quadtree = Quadtree(0, self.bounds)
        self.obstacles = []
        self.regions = []  # For different environmental regions
        
    def get_bounds(self):
        """
        Get the world boundaries.
        
        Returns:
            pygame.Rect: World boundaries
        """
        return self.bounds
    
    def get_quadtree(self):
        """
        Get the world quadtree.
        
        Returns:
            Quadtree: World quadtree
        """
        return self.quadtree
    
    def add_obstacle(self, obstacle):
        """
        Add an obstacle to the world.
        
        Args:
            obstacle: Obstacle entity
        """
        self.obstacles.append(obstacle)
        
    def get_obstacles(self):
        """
        Get all obstacles in the world.
        
        Returns:
            list: All obstacle entities
        """
        return self.obstacles
    
    def is_position_valid(self, position, radius=0):
        """
        Check if a position is valid (within bounds and not inside obstacles).
        
        Args:
            position (tuple): (x, y) position
            radius (float): Entity radius
            
        Returns:
            bool: True if the position is valid
        """
        x, y = position
        
        # Check world boundaries
        if (x - radius < 0 or x + radius > self.width or
            y - radius < 0 or y + radius > self.height):
            return False
            
        # Check obstacles
        for obstacle in self.obstacles:
            if obstacle.collides_with_circle(position, radius):
                return False
                
        return True
    
    def get_random_valid_position(self, radius=0):
        """
        Get a random valid position in the world.
        
        Args:
            radius (float): Entity radius
            
        Returns:
            tuple: (x, y) position
        """
        import random
        
        # Try to find a valid position
        for _ in range(100):  # Limit attempts to avoid infinite loop
            x = random.uniform(radius, self.width - radius)
            y = random.uniform(radius, self.height - radius)
            position = (x, y)
            
            if self.is_position_valid(position, radius):
                return position
                
        # Fallback to a position in the center
        return (self.width / 2, self.height / 2)
    
    def add_region(self, region):
        """
        Add an environmental region to the world.
        
        Args:
            region: Region definition (rect, type, properties)
        """
        self.regions.append(region)
        
    def get_region_at_position(self, position):
        """
        Get the environmental region at a position.
        
        Args:
            position (tuple): (x, y) position
            
        Returns:
            dict: Region definition or None
        """
        for region in self.regions:
            if region["rect"].collidepoint(position):
                return region
                
        return None
    
    def draw(self, surface, camera_rect):
        """
        Draw the world map.
        
        Args:
            surface (pygame.Surface): Surface to draw on
            camera_rect (pygame.Rect): Camera view rectangle
        """
        # Draw world boundaries
        boundary_rect = pygame.Rect(
            -camera_rect.x,
            -camera_rect.y,
            self.width,
            self.height
        )
        pygame.draw.rect(surface, config.DARK_GRAY, boundary_rect, config.BOUNDARY_THICKNESS)
        
        # Draw regions
        for region in self.regions:
            region_rect = pygame.Rect(
                region["rect"].x - camera_rect.x,
                region["rect"].y - camera_rect.y,
                region["rect"].width,
                region["rect"].height
            )
            pygame.draw.rect(surface, region["color"], region_rect)
            
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(surface, camera_rect)
            
        # Draw quadtree for debugging (uncomment if needed)
        # self.quadtree.draw(surface, camera_rect)
