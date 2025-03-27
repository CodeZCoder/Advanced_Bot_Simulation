"""
Genetic component module for storing entity genetic data.
"""

import random
import math
import copy
import config

class GeneticComponent:
    """
    Stores and manages entity genetic data and traits.
    """
    
    def __init__(self, parent_genetics=None):
        """
        Initialize the genetic component.
        
        Args:
            parent_genetics (GeneticComponent, optional): Parent genetics to inherit from
        """
        # Genetic parameters
        if parent_genetics:
            # Inherit from parent with mutation
            self.genes = self._inherit_from_parent(parent_genetics)
        else:
            # Generate random genetics
            self.genes = self._generate_random_genes()
            
        # Derived traits (calculated from genes)
        self.traits = self._calculate_traits()
        
        # Genetic history
        self.generation = 1 if not parent_genetics else parent_genetics.generation + 1
        self.lineage_id = random.randint(1000, 9999) if not parent_genetics else parent_genetics.lineage_id
        self.mutation_count = 0
        self.parent_ids = []
        
        # Add parent ID if available
        if parent_genetics and hasattr(parent_genetics, 'entity_id'):
            self.parent_ids.append(parent_genetics.entity_id)
            
        # This will be set when the entity is created
        self.entity_id = None
        
    def _generate_random_genes(self):
        """
        Generate random genetic parameters.
        
        Returns:
            dict: Genetic parameters
        """
        return {
            # Physical attributes
            "size": random.uniform(0.7, 1.3),  # Size multiplier
            "max_speed": random.uniform(config.BOT_SPEED_MIN, config.BOT_SPEED_MAX),
            "acceleration": random.uniform(0.1, 0.3),
            "color_r": random.randint(50, 255),
            "color_g": random.randint(50, 255),
            "color_b": random.randint(50, 255),
            
            # Energy attributes
            "max_energy": random.uniform(config.BOT_MAX_ENERGY * 0.8, config.BOT_MAX_ENERGY * 1.2),
            "metabolism_rate": random.uniform(config.BOT_METABOLISM_RATE * 0.7, config.BOT_METABOLISM_RATE * 1.3),
            "movement_efficiency": random.uniform(0.8, 1.2),  # Lower is more efficient
            
            # Sensor attributes
            "visual_range": random.uniform(config.VISUAL_RANGE * 0.7, config.VISUAL_RANGE * 1.3),
            "visual_angle": random.uniform(config.VISUAL_ANGLE * 0.7, config.VISUAL_ANGLE * 1.3),
            "resource_detection_range": random.uniform(config.RESOURCE_DETECTION_RANGE * 0.7, config.RESOURCE_DETECTION_RANGE * 1.3),
            "signal_detection_range": random.uniform(config.SIGNAL_DETECTION_RANGE * 0.7, config.SIGNAL_DETECTION_RANGE * 1.3),
            "visual_accuracy": random.uniform(0.7, 1.0),
            "resource_accuracy": random.uniform(0.7, 1.0),
            "signal_accuracy": random.uniform(0.7, 1.0),
            
            # Action attributes
            "eat_efficiency": random.uniform(0.7, 1.0),
            "communication_range": random.uniform(0.8, 1.2),
            "reproduction_rate": random.uniform(0.6, 0.9),
            "attack_strength": random.uniform(0.3, 0.7),
            
            # AI attributes
            "aggression": random.uniform(0.1, 0.4),
            "sociability": random.uniform(0.3, 0.8),
            "curiosity": random.uniform(0.4, 0.9),
            "caution": random.uniform(0.3, 0.8),
            
            # Learning attributes
            "learning_rate": random.uniform(config.LEARNING_RATE * 0.7, config.LEARNING_RATE * 1.3),
            "memory_capacity": random.uniform(0.8, 1.2),
            "exploration_rate": random.uniform(config.EXPLORATION_RATE * 0.7, config.EXPLORATION_RATE * 1.3),
            
            # Evolution attributes
            "mutation_rate": random.uniform(config.MUTATION_RATE * 0.5, config.MUTATION_RATE * 1.5),
            "mutation_amount": random.uniform(config.MUTATION_AMOUNT * 0.5, config.MUTATION_AMOUNT * 1.5)
        }
        
    def _inherit_from_parent(self, parent_genetics):
        """
        Inherit genes from parent with mutation.
        
        Args:
            parent_genetics (GeneticComponent): Parent genetics
            
        Returns:
            dict: Inherited genetic parameters
        """
        # Copy parent genes
        genes = copy.deepcopy(parent_genetics.genes)
        
        # Apply mutations
        mutation_rate = genes["mutation_rate"]
        mutation_amount = genes["mutation_amount"]
        
        for gene in genes:
            # Determine if this gene mutates
            if random.random() < mutation_rate:
                # Apply mutation
                if isinstance(genes[gene], float):
                    # Mutate float value
                    mutation_factor = 1.0 + random.uniform(-mutation_amount, mutation_amount)
                    genes[gene] *= mutation_factor
                    self.mutation_count += 1
                elif isinstance(genes[gene], int):
                    # Mutate integer value
                    mutation_value = int(genes[gene] * random.uniform(-mutation_amount, mutation_amount))
                    genes[gene] += mutation_value
                    self.mutation_count += 1
                    
        return genes
    
    def _calculate_traits(self):
        """
        Calculate derived traits from genes.
        
        Returns:
            dict: Derived traits
        """
        return {
            # Physical traits
            "radius": config.BOT_RADIUS_MIN + (config.BOT_RADIUS_MAX - config.BOT_RADIUS_MIN) * self.genes["size"],
            "color": (
                self.genes["color_r"],
                self.genes["color_g"],
                self.genes["color_b"]
            ),
            
            # Performance traits
            "energy_efficiency": 1.0 / (self.genes["metabolism_rate"] / config.BOT_METABOLISM_RATE),
            "movement_cost_factor": config.BOT_MOVEMENT_COST * self.genes["movement_efficiency"],
            
            # Behavioral traits
            "foraging_preference": self.genes["resource_accuracy"] * (1.0 - self.genes["metabolism_rate"] / config.BOT_METABOLISM_RATE),
            "social_preference": self.genes["sociability"] * self.genes["communication_range"],
            "exploration_preference": self.genes["curiosity"] * (1.0 - self.genes["caution"]),
            "combat_ability": self.genes["attack_strength"] * self.genes["aggression"],
            
            # Evolutionary fitness (estimated)
            "estimated_fitness": (
                self.genes["max_energy"] / config.BOT_MAX_ENERGY +
                (1.0 - self.genes["metabolism_rate"] / config.BOT_METABOLISM_RATE) +
                self.genes["eat_efficiency"] +
                self.genes["reproduction_rate"] +
                self.genes["visual_range"] / config.VISUAL_RANGE
            ) / 5.0
        }
        
    def combine_with(self, other_genetics):
        """
        Combine genetics with another entity (sexual reproduction).
        
        Args:
            other_genetics (GeneticComponent): Other entity's genetics
            
        Returns:
            GeneticComponent: Combined genetics for offspring
        """
        # Create new genetics
        offspring_genetics = GeneticComponent()
        
        # Inherit genes from both parents
        for gene in self.genes:
            # Randomly select from which parent to inherit each gene
            if random.random() < 0.5:
                offspring_genetics.genes[gene] = self.genes[gene]
            else:
                offspring_genetics.genes[gene] = other_genetics.genes[gene]
                
        # Set mutation parameters (average of parents)
        offspring_genetics.genes["mutation_rate"] = (self.genes["mutation_rate"] + other_genetics.genes["mutation_rate"]) / 2
        offspring_genetics.genes["mutation_amount"] = (self.genes["mutation_amount"] + other_genetics.genes["mutation_amount"]) / 2
        
        # Apply mutations
        for gene in offspring_genetics.genes:
            # Determine if this gene mutates
            if random.random() < offspring_genetics.genes["mutation_rate"]:
                # Apply mutation
                if isinstance(offspring_genetics.genes[gene], float):
                    # Mutate float value
                    mutation_factor = 1.0 + random.uniform(
                        -offspring_genetics.genes["mutation_amount"], 
                        offspring_genetics.genes["mutation_amount"]
                    )
                    offspring_genetics.genes[gene] *= mutation_factor
                    offspring_genetics.mutation_count += 1
                elif isinstance(offspring_genetics.genes[gene], int):
                    # Mutate integer value
                    mutation_value = int(offspring_genetics.genes[gene] * random.uniform(
                        -offspring_genetics.genes["mutation_amount"], 
                        offspring_genetics.genes["mutation_amount"]
                    ))
                    offspring_genetics.genes[gene] += mutation_value
                    offspring_genetics.mutation_count += 1
                    
        # Recalculate traits
        offspring_genetics.traits = offspring_genetics._calculate_traits()
        
        # Set generation and lineage
        offspring_genetics.generation = max(self.generation, other_genetics.generation) + 1
        
        # Determine lineage (50% chance to inherit from either parent)
        if random.random() < 0.5:
            offspring_genetics.lineage_id = self.lineage_id
        else:
            offspring_genetics.lineage_id = other_genetics.lineage_id
            
        # Add parent IDs
        if hasattr(self, 'entity_id'):
            offspring_genetics.parent_ids.append(self.entity_id)
        if hasattr(other_genetics, 'entity_id'):
            offspring_genetics.parent_ids.append(other_genetics.entity_id)
            
        return offspring_genetics
    
    def clone_with_mutation(self):
        """
        Create a clone with mutations (asexual reproduction).
        
        Returns:
            GeneticComponent: Mutated clone genetics
        """
        # Create new genetics based on self
        clone_genetics = GeneticComponent(self)
        
        # Recalculate traits
        clone_genetics.traits = clone_genetics._calculate_traits()
        
        return clone_genetics
    
    def get_gene(self, gene_name):
        """
        Get a specific gene value.
        
        Args:
            gene_name (str): Name of the gene
            
        Returns:
            Gene value or None if not found
        """
        return self.genes.get(gene_name)
    
    def get_trait(self, trait_name):
        """
        Get a specific trait value.
        
        Args:
            trait_name (str): Name of the trait
            
        Returns:
            Trait value or None if not found
        """
        return self.traits.get(trait_name)
    
    def get_all_genes(self):
        """
        Get all genes.
        
        Returns:
            dict: All genetic parameters
        """
        return self.genes
    
    def get_all_traits(self):
        """
        Get all traits.
        
        Returns:
            dict: All derived traits
        """
        return self.traits
    
    def get_generation(self):
        """
        Get the generation number.
        
        Returns:
            int: Generation number
        """
        return self.generation
    
    def get_lineage_id(self):
        """
        Get the lineage ID.
        
        Returns:
            int: Lineage ID
        """
        return self.lineage_id
    
    def get_mutation_count(self):
        """
        Get the number of mutations.
        
        Returns:
            int: Mutation count
        """
        return self.mutation_count
    
    def get_parent_ids(self):
        """
        Get the parent IDs.
        
        Returns:
            list: Parent IDs
        """
        return self.parent_ids
    
    def set_entity_id(self, entity_id):
        """
        Set the entity ID.
        
        Args:
            entity_id: Entity ID
        """
        self.entity_id = entity_id
    
    def get_genetic_distance(self, other_genetics):
        """
        Calculate genetic distance to another entity.
        
        Args:
            other_genetics (GeneticComponent): Other entity's genetics
            
        Returns:
            float: Genetic distance (0-1, where 0 is identical)
        """
        if not other_genetics:
            return 1.0
            
        # Calculate average difference across all genes
        total_diff = 0
        gene_count = 0
        
        for gene in self.genes:
            if gene in other_genetics.genes:
                if isinstance(self.genes[gene], (int, float)):
                    # Normalize the difference
                    max_val = max(abs(self.genes[gene]), abs(other_genetics.genes[gene]))
                    if max_val > 0:
                        diff = abs(self.genes[gene] - other_genetics.genes[gene]) / max_val
                    else:
                        diff = 0
                    total_diff += diff
                    gene_count += 1
                    
        if gene_count == 0:
            return 1.0
            
        return total_diff / gene_count
    
    def get_color_for_lineage(self):
        """
        Get a consistent color based on lineage ID.
        
        Returns:
            tuple: RGB color
        """
        # Use lineage ID to generate a consistent color
        random.seed(self.lineage_id)
        color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )
        random.seed()  # Reset random seed
        
        return color
    
    def get_fitness_estimate(self):
        """
        Get an estimate of genetic fitness.
        
        Returns:
            float: Estimated fitness (0-1)
        """
        return self.traits["estimated_fitness"]
