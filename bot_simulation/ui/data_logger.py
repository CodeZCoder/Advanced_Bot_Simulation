"""
Data logging module for recording simulation data.
"""

import os
import time
import csv
import json
import pygame
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

class DataLogger:
    """Logger for recording and analyzing simulation data."""
    
    def __init__(self, entity_manager, evolution_system, energy_system):
        """
        Initialize the data logger.
        
        Args:
            entity_manager: Entity manager instance
            evolution_system: Evolution system instance
            energy_system: Energy system instance
        """
        self.entity_manager = entity_manager
        self.evolution_system = evolution_system
        self.energy_system = energy_system
        
        # Create logs directory if it doesn't exist
        self.log_dir = "logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        # Generate timestamp for this session
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Data storage
        self.time_points = []
        self.population_data = []
        self.energy_data = []
        self.birth_data = []
        self.death_data = []
        self.generation_data = []
        
        # Detailed snapshots (less frequent)
        self.snapshots = []
        self.snapshot_interval = 60  # seconds
        self.last_snapshot_time = 0
        
        # CSV file handles
        self.csv_files = {}
        self.csv_writers = {}
        
        # Initialize CSV files
        self._init_csv_files()
        
    def _init_csv_files(self):
        """Initialize CSV log files."""
        # Main statistics log
        stats_file = os.path.join(self.log_dir, f"stats_{self.timestamp}.csv")
        self.csv_files["stats"] = open(stats_file, "w", newline="")
        self.csv_writers["stats"] = csv.writer(self.csv_files["stats"])
        
        # Write headers
        self.csv_writers["stats"].writerow([
            "Time", "Population", "Avg_Energy", "Total_Energy", 
            "Births", "Deaths", "Resources", "Highest_Generation"
        ])
        
        # Genetic data log
        genetics_file = os.path.join(self.log_dir, f"genetics_{self.timestamp}.csv")
        self.csv_files["genetics"] = open(genetics_file, "w", newline="")
        self.csv_writers["genetics"] = csv.writer(self.csv_files["genetics"])
        
        # Write headers (will add gene names dynamically on first update)
        self.genetics_headers_written = False
        
    def update(self, simulation_time):
        """
        Update the data logger.
        
        Args:
            simulation_time (float): Current simulation time
        """
        # Record basic statistics
        self._record_basic_stats(simulation_time)
        
        # Check if it's time for a detailed snapshot
        if simulation_time - self.last_snapshot_time >= self.snapshot_interval:
            self._take_snapshot(simulation_time)
            self.last_snapshot_time = simulation_time
            
    def _record_basic_stats(self, simulation_time):
        """
        Record basic simulation statistics.
        
        Args:
            simulation_time (float): Current simulation time
        """
        # Get statistics
        bots = self.entity_manager.get_all_bots()
        population = len(bots)
        avg_energy = self.energy_system.get_average_bot_energy()
        total_energy = self.energy_system.get_total_energy()
        births = self.evolution_system.get_birth_count()
        deaths = self.evolution_system.get_death_count()
        resources = len(self.entity_manager.get_all_resources())
        highest_gen = self.evolution_system.get_highest_generation()
        
        # Store in memory
        self.time_points.append(simulation_time)
        self.population_data.append(population)
        self.energy_data.append(avg_energy)
        self.birth_data.append(births)
        self.death_data.append(deaths)
        self.generation_data.append(highest_gen)
        
        # Write to CSV
        self.csv_writers["stats"].writerow([
            simulation_time, population, avg_energy, total_energy,
            births, deaths, resources, highest_gen
        ])
        self.csv_files["stats"].flush()
        
        # Record genetic data if there are bots
        if bots:
            self._record_genetic_stats(simulation_time, bots)
            
    def _record_genetic_stats(self, simulation_time, bots):
        """
        Record genetic statistics.
        
        Args:
            simulation_time (float): Current simulation time
            bots (list): List of bot entities
        """
        # Get genetic data from all bots
        gene_data = {}
        
        # First, collect all gene names if headers not written yet
        if not self.genetics_headers_written and bots:
            sample_genes = bots[0].get_genetic_component().get_all_genes()
            gene_names = list(sample_genes.keys())
            
            # Write headers
            headers = ["Time", "Bot_Count"]
            for gene in gene_names:
                headers.extend([f"{gene}_avg", f"{gene}_min", f"{gene}_max", f"{gene}_std"])
                
            self.csv_writers["genetics"].writerow(headers)
            self.genetics_headers_written = True
            
        # Collect gene values
        for bot in bots:
            genes = bot.get_genetic_component().get_all_genes()
            
            for gene_name, value in genes.items():
                if gene_name not in gene_data:
                    gene_data[gene_name] = []
                    
                gene_data[gene_name].append(value)
                
        # Calculate statistics
        row = [simulation_time, len(bots)]
        
        for gene_name, values in gene_data.items():
            values_array = np.array(values)
            avg = np.mean(values_array)
            min_val = np.min(values_array)
            max_val = np.max(values_array)
            std = np.std(values_array)
            
            row.extend([avg, min_val, max_val, std])
            
        # Write to CSV
        self.csv_writers["genetics"].writerow(row)
        self.csv_files["genetics"].flush()
        
    def _take_snapshot(self, simulation_time):
        """
        Take a detailed snapshot of the simulation state.
        
        Args:
            simulation_time (float): Current simulation time
        """
        snapshot = {
            "time": simulation_time,
            "bots": [],
            "resources": [],
            "statistics": {
                "population": len(self.entity_manager.get_all_bots()),
                "resources": len(self.entity_manager.get_all_resources()),
                "signals": len(self.entity_manager.get_all_signals()),
                "births": self.evolution_system.get_birth_count(),
                "deaths": self.evolution_system.get_death_count(),
                "avg_energy": self.energy_system.get_average_bot_energy(),
                "total_energy": self.energy_system.get_total_energy(),
                "highest_generation": self.evolution_system.get_highest_generation(),
                "generation_distribution": self.evolution_system.get_generation_stats()
            }
        }
        
        # Record bot data
        for bot in self.entity_manager.get_all_bots():
            bot_data = {
                "id": bot.get_id(),
                "position": bot.get_position(),
                "energy": bot.get_energy_component().get_energy(),
                "age": bot.get_age(),
                "generation": bot.generation,
                "mature": bot.is_mature(),
                "reproductions": bot.reproduction_count,
                "genes": bot.get_genetic_component().get_all_genes()
            }
            
            snapshot["bots"].append(bot_data)
            
        # Record resource data
        for resource in self.entity_manager.get_all_resources():
            resource_data = {
                "position": resource.get_position(),
                "energy": resource.get_energy()
            }
            
            snapshot["resources"].append(resource_data)
            
        # Add to snapshots list
        self.snapshots.append(snapshot)
        
        # Save snapshot to file
        snapshot_file = os.path.join(self.log_dir, f"snapshot_{self.timestamp}_{int(simulation_time)}.json")
        with open(snapshot_file, "w") as f:
            json.dump(snapshot, f, indent=2)
            
    def save_data(self):
        """Save all recorded data to files."""
        # Make sure all CSV data is written
        for file in self.csv_files.values():
            file.flush()
            
        # Generate plots
        self._generate_plots()
        
        # Save final snapshot
        simulation_time = pygame.time.get_ticks() / 1000
        self._take_snapshot(simulation_time)
        
        return os.path.abspath(self.log_dir)
        
    def _generate_plots(self):
        """Generate plots from recorded data."""
        # Create plots directory
        plots_dir = os.path.join(self.log_dir, "plots")
        if not os.path.exists(plots_dir):
            os.makedirs(plots_dir)
            
        # Population plot
        plt.figure(figsize=(10, 6))
        plt.plot(self.time_points, self.population_data)
        plt.title("Bot Population Over Time")
        plt.xlabel("Simulation Time (s)")
        plt.ylabel("Population")
        plt.grid(True)
        plt.savefig(os.path.join(plots_dir, f"population_{self.timestamp}.png"))
        plt.close()
        
        # Energy plot
        plt.figure(figsize=(10, 6))
        plt.plot(self.time_points, self.energy_data)
        plt.title("Average Bot Energy Over Time")
        plt.xlabel("Simulation Time (s)")
        plt.ylabel("Energy")
        plt.grid(True)
        plt.savefig(os.path.join(plots_dir, f"energy_{self.timestamp}.png"))
        plt.close()
        
        # Births and deaths plot
        plt.figure(figsize=(10, 6))
        plt.plot(self.time_points, self.birth_data, label="Births")
        plt.plot(self.time_points, self.death_data, label="Deaths")
        plt.title("Births and Deaths Over Time")
        plt.xlabel("Simulation Time (s)")
        plt.ylabel("Count")
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(plots_dir, f"births_deaths_{self.timestamp}.png"))
        plt.close()
        
        # Generation plot
        plt.figure(figsize=(10, 6))
        plt.plot(self.time_points, self.generation_data)
        plt.title("Highest Generation Over Time")
        plt.xlabel("Simulation Time (s)")
        plt.ylabel("Generation")
        plt.grid(True)
        plt.savefig(os.path.join(plots_dir, f"generation_{self.timestamp}.png"))
        plt.close()
        
        # If we have snapshots, generate genetic distribution plots
        if self.snapshots:
            self._generate_genetic_plots(plots_dir)
            
    def _generate_genetic_plots(self, plots_dir):
        """
        Generate plots of genetic distributions.
        
        Args:
            plots_dir (str): Directory to save plots
        """
        # Get the latest snapshot
        latest_snapshot = self.snapshots[-1]
        
        # Extract gene data
        if not latest_snapshot["bots"]:
            return
            
        # Get gene names from first bot
        gene_names = list(latest_snapshot["bots"][0]["genes"].keys())
        
        # For each gene, create a histogram
        for gene_name in gene_names:
            values = [bot["genes"][gene_name] for bot in latest_snapshot["bots"]]
            
            plt.figure(figsize=(8, 5))
            plt.hist(values, bins=20)
            plt.title(f"Distribution of {gene_name}")
            plt.xlabel("Value")
            plt.ylabel("Count")
            plt.grid(True)
            plt.savefig(os.path.join(plots_dir, f"gene_{gene_name}_{self.timestamp}.png"))
            plt.close()
            
    def close(self):
        """Close all open files."""
        for file in self.csv_files.values():
            file.close()
            
    def __del__(self):
        """Destructor to ensure files are closed."""
        self.close()
