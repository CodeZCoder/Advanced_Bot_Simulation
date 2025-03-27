"""
Pathfinding algorithms for bot navigation.
"""

import heapq
import math
import config

class AStar:
    """A* pathfinding algorithm."""
    
    def __init__(self, world_map):
        """
        Initialize the A* pathfinder.
        
        Args:
            world_map: World map instance
        """
        self.world_map = world_map
        self.grid_size = config.PATHFINDING_GRID_SIZE
        
    def find_path(self, start, goal, entity_radius=10):
        """
        Find a path from start to goal.
        
        Args:
            start (tuple): Start position (x, y)
            goal (tuple): Goal position (x, y)
            entity_radius (float): Radius of the entity
            
        Returns:
            list: List of positions forming a path, or None if no path found
        """
        # Convert positions to grid coordinates
        start_grid = self._to_grid(start)
        goal_grid = self._to_grid(goal)
        
        # Initialize open and closed sets
        open_set = []
        closed_set = set()
        
        # Create start node
        start_node = PathNode(None, start_grid)
        start_node.g = 0
        start_node.h = self._heuristic(start_grid, goal_grid)
        start_node.f = start_node.g + start_node.h
        
        # Add start node to open set
        heapq.heappush(open_set, (start_node.f, id(start_node), start_node))
        
        # Main loop
        while open_set:
            # Get node with lowest f value
            _, _, current = heapq.heappop(open_set)
            
            # Check if goal reached
            if current.position == goal_grid:
                # Reconstruct path
                path = []
                while current:
                    path.append(self._to_world(current.position))
                    current = current.parent
                return path[::-1]  # Reverse path
                
            # Add to closed set
            closed_set.add(current.position)
            
            # Generate neighbors
            for neighbor_pos in self._get_neighbors(current.position, entity_radius):
                # Skip if in closed set
                if neighbor_pos in closed_set:
                    continue
                    
                # Create neighbor node
                neighbor = PathNode(current, neighbor_pos)
                
                # Calculate g value
                neighbor.g = current.g + self._distance(current.position, neighbor_pos)
                
                # Check if better path exists
                skip = False
                for _, _, node in open_set:
                    if node.position == neighbor_pos and node.g <= neighbor.g:
                        skip = True
                        break
                        
                if skip:
                    continue
                    
                # Calculate f value
                neighbor.h = self._heuristic(neighbor_pos, goal_grid)
                neighbor.f = neighbor.g + neighbor.h
                
                # Add to open set
                heapq.heappush(open_set, (neighbor.f, id(neighbor), neighbor))
                
        # No path found
        return None
    
    def _to_grid(self, position):
        """
        Convert world position to grid position.
        
        Args:
            position (tuple): World position (x, y)
            
        Returns:
            tuple: Grid position (x, y)
        """
        return (int(position[0] / self.grid_size), int(position[1] / self.grid_size))
    
    def _to_world(self, grid_position):
        """
        Convert grid position to world position.
        
        Args:
            grid_position (tuple): Grid position (x, y)
            
        Returns:
            tuple: World position (x, y)
        """
        return ((grid_position[0] + 0.5) * self.grid_size, (grid_position[1] + 0.5) * self.grid_size)
    
    def _heuristic(self, a, b):
        """
        Calculate heuristic distance between two positions.
        
        Args:
            a (tuple): First position (x, y)
            b (tuple): Second position (x, y)
            
        Returns:
            float: Heuristic distance
        """
        # Euclidean distance
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def _distance(self, a, b):
        """
        Calculate actual distance between two positions.
        
        Args:
            a (tuple): First position (x, y)
            b (tuple): Second position (x, y)
            
        Returns:
            float: Actual distance
        """
        # Euclidean distance
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def _get_neighbors(self, position, entity_radius):
        """
        Get valid neighboring positions.
        
        Args:
            position (tuple): Current position (x, y)
            entity_radius (float): Radius of the entity
            
        Returns:
            list: List of valid neighboring positions
        """
        # Possible moves (8 directions)
        moves = [
            (0, 1),   # North
            (1, 1),   # Northeast
            (1, 0),   # East
            (1, -1),  # Southeast
            (0, -1),  # South
            (-1, -1), # Southwest
            (-1, 0),  # West
            (-1, 1)   # Northwest
        ]
        
        neighbors = []
        for dx, dy in moves:
            new_pos = (position[0] + dx, position[1] + dy)
            
            # Check if within world bounds
            world_bounds = self.world_map.get_bounds()
            world_pos = self._to_world(new_pos)
            if (world_pos[0] < 0 or world_pos[0] >= world_bounds.width or
                world_pos[1] < 0 or world_pos[1] >= world_bounds.height):
                continue
                
            # Check if collides with obstacles
            if self._collides_with_obstacles(world_pos, entity_radius):
                continue
                
            neighbors.append(new_pos)
            
        return neighbors
    
    def _collides_with_obstacles(self, position, entity_radius):
        """
        Check if position collides with obstacles.
        
        Args:
            position (tuple): Position to check (x, y)
            entity_radius (float): Radius of the entity
            
        Returns:
            bool: True if position collides with obstacles
        """
        # Get nearby obstacles
        obstacles = self.world_map.get_nearby_obstacles(position, entity_radius + self.grid_size)
        
        # Check collision with each obstacle
        for obstacle in obstacles:
            if obstacle.collides_with_circle(position, entity_radius):
                return True
                
        return False


class PathNode:
    """Node in the A* pathfinding algorithm."""
    
    def __init__(self, parent, position):
        """
        Initialize a path node.
        
        Args:
            parent (PathNode): Parent node
            position (tuple): Position (x, y)
        """
        self.parent = parent
        self.position = position
        
        self.g = 0  # Cost from start to this node
        self.h = 0  # Heuristic cost from this node to goal
        self.f = 0  # Total cost (g + h)
        
    def __eq__(self, other):
        """
        Check if two nodes are equal.
        
        Args:
            other (PathNode): Other node
            
        Returns:
            bool: True if nodes are equal
        """
        return self.position == other.position
        
    def __lt__(self, other):
        """
        Compare nodes by f value.
        
        Args:
            other (PathNode): Other node
            
        Returns:
            bool: True if this node has lower f value
        """
        return self.f < other.f
