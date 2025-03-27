"""
Main entry point for Bot Simulation.
Initializes the simulation and starts the main loop.
"""

import pygame
import sys
from core.simulation import Simulation
from core.event_handler import EventHandler
from core.clock import Clock
import config

def main():
    """
    Main function to initialize and run the simulation.
    """
    # Initialize Pygame
    pygame.init()
    
    # Create the display
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(config.TITLE)
    
    # Initialize core components
    clock = Clock(config.FPS)
    event_handler = EventHandler()
    simulation = Simulation(screen, clock, event_handler)
    
    # Start the simulation
    simulation.run()
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
