"""
Configuration file for Bot Simulation.
Contains constants for screen dimensions, simulation parameters, colors, etc.
"""

# Screen and display settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
TITLE = "Bot Simulation"
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)

# World settings
WORLD_WIDTH = 3000  # Larger than screen for scrolling/zooming
WORLD_HEIGHT = 2000
BOUNDARY_THICKNESS = 5
QUADTREE_MAX_OBJECTS = 10
QUADTREE_MAX_LEVELS = 5

# Bot settings
BOT_RADIUS_MIN = 5
BOT_RADIUS_MAX = 15
BOT_SPEED_MIN = 0.5
BOT_SPEED_MAX = 3.0
BOT_ACCELERATION = 0.2
BOT_INITIAL_ENERGY = 100
BOT_MAX_ENERGY = 200
BOT_METABOLISM_RATE = 0.05  # Energy consumed per update
BOT_MOVEMENT_COST = 0.02    # Additional energy per unit of movement
BOT_REPRODUCTION_COST = 50  # Energy cost to reproduce
BOT_MATURITY_AGE = 500      # Updates before reproduction is possible
BOT_MAX_AGE = 10000         # Maximum lifespan in updates

# Sensor settings
VISUAL_RANGE = 150
VISUAL_ANGLE = 120  # Degrees
RESOURCE_DETECTION_RANGE = 100
SIGNAL_DETECTION_RANGE = 200

# Resource settings
RESOURCE_RADIUS = 8
RESOURCE_ENERGY_MIN = 20
RESOURCE_ENERGY_MAX = 50
RESOURCE_SPAWN_RATE = 0.01  # Probability per update
RESOURCE_MAX_COUNT = 100
RESOURCE_RESPAWN_TIME = 500  # Updates before respawning

# Communication settings
SIGNAL_TYPES = {
    1: "DANGER",
    2: "FOOD",
    3: "MATE"
}
SIGNAL_COST = 5  # Energy cost to emit a signal
SIGNAL_DURATION = 100  # Updates before signal dissipates

# Learning settings
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9
EXPLORATION_RATE = 0.2
EXPLORATION_DECAY = 0.9999

# Evolution settings
MUTATION_RATE = 0.1
MUTATION_AMOUNT = 0.2  # Maximum percentage change

# Environment effects
DAY_NIGHT_CYCLE_LENGTH = 2000  # Updates per full cycle
DAY_RESOURCE_MULTIPLIER = 1.5  # Resources spawn faster during day

# UI settings
FONT_SIZE_SMALL = 14
FONT_SIZE_MEDIUM = 18
FONT_SIZE_LARGE = 24
UI_PADDING = 10
GRAPH_WIDTH = 300
GRAPH_HEIGHT = 150
GRAPH_HISTORY_LENGTH = 100  # Number of data points to store

# Simulation control
INITIAL_POPULATION = 20
SIMULATION_SPEED_MIN = 0.5
SIMULATION_SPEED_MAX = 5.0
SIMULATION_SPEED_STEP = 0.5
DEFAULT_SIMULATION_SPEED = 1.0
