from Functions import scalar_dist
from random import choice, random, randint, gauss
from math import pi
import random as rndm
import copy
import sys
from Functions import polar_move
from Object_Defs import centroid, collection_of_centroids, line, \
    substation, collection_of_substations, gene, chromosome, population

    
class generator:
    def substation(x_bounds, y_bounds):
        '''Creates a substation within bounds with capacity under substation class
        '''
        if not (len(x_bounds) == 2 or x_bounds[0] < x_bounds[1]):
            raise ValueError('Invalid input into substation_generator')
        if not (len(y_bounds) == 2 or y_bounds[0] < y_bounds[1]):
            raise ValueError('Invalid input into substation_generator')
        x = (x_bounds[1] - x_bounds[0]) * random() + x_bounds[0]
        y = (y_bounds[1] - y_bounds[0]) * random() + y_bounds[0]
        substation_capacity = choice(list(substation.get_max_cap_to_cost_index(substation).keys()))
        return substation([x,y], substation_capacity)
    
    def gene(all_centroids, col_of_substations):
        '''Creates all the collections of genes within a sinlge chromosome
        '''
        if not isinstance(all_centroids, collection_of_centroids):
            raise ValueError('Invalid input into gene generator')
        if not isinstance(col_of_substations, collection_of_substations):
            raise ValueError('Invalid input into gene generator')
        collection_of_genes = []
        for sub in col_of_substations.get_collection():
            collection_of_genes.append(gene(sub))
        process.generate_lines(all_centroids, collection_of_genes)
        return collection_of_genes
    
    def create_chromosome(all_centroids, col_of_subs):
        '''Substations must have their capacities reset before applying this 
        operator
        '''
        if not isinstance(col_of_subs, collection_of_substations):
            raise ValueError('Invalid input into create_chromosome')
        new_chrom = chromosome(generator.gene(all_centroids, col_of_subs))
        process.update_chrom_cost(new_chrom)
        return new_chrom

class process:
    def closest_substation(coll_of_genes, cent):
        """returns memory location of closest gene to a given centroid
        """
        if not isinstance(cent, centroid):
            raise ValueError('Invalid input into closest_coord')
        if not isinstance(coll_of_genes, list): 
            raise ValueError('Invalid input into closest_coord')
        min_len = sys.float_info.max
        for i in coll_of_genes: #i is of type gene
            potential_min_len = scalar_dist(i.get_substation().get_coordinates(), cent.get_coordinates())
            if potential_min_len < min_len:
                min_len = potential_min_len
                closest_gene = i
        if min_len == sys.float_info.max:
            raise ValueError('Couldn\'t find closest_coord')
        return closest_gene
    
    def generate_lines(all_centroids, coll_of_genes):
        if not isinstance(all_centroids, collection_of_centroids):
            raise ValueError('Invalid input into generate_lines')
        if not isinstance(coll_of_genes, list):
            raise ValueError('Invalid input into generate_lines')
        for cent in all_centroids.get_collection():
            #Find gene the centroid belongs in
            closest_gene = process.closest_substation(coll_of_genes, cent)
            #Add centroid to gene
            closest_gene.add_centroid(cent)
            #Create line and add it to the gene
            lin = line(closest_gene.get_substation_coordinates(), cent.get_coordinates(), cent.get_peak())
            closest_gene.add_line(lin)
        
    def update_chrom_cost(chrom):
        '''
        '''
        if not isinstance(chrom, chromosome):
            raise ValueError('Invalid input into update_chrom_cost')
        if not(chrom.get_cost() == 0): #the cost of each chromosome is only calculated once
            return
        for gene1 in chrom.get_collection():
            coll_of_lines = gene1.get_collection_of_lines() #gets the collection_of_lines class within gene
            for line1 in coll_of_lines.get_collection(): #adds each line cost to collection of lines
                coll_of_lines.add_cost(line1.get_cost())
                if line1.get_length() > 2000:
                    coll_of_lines.add_cost(line1.get_cost())  # Long lines cost twice as much
            gene1.add_cost(coll_of_lines.get_cost()) #lines cost
            
            gene1.add_cost(gene1.get_substation().get_cost()) #substation cost
            if gene1.get_substation().get_remaining_cap() < 0:
                penalty_cost = 4 * list(gene1.get_substation().get_max_cap_to_cost_index().values())[-1]
                gene1.add_cost(penalty_cost)
                
            chrom.add_cost(gene1.get_cost())

    def substation_location_mutator(sub, mutation_dist_percentage, x_bounds, y_bounds):
        '''Mutates one substation's location in memory. mutation_dist_percentage is a percentage 
        of the x bounds.
        '''
        if not isinstance(sub, substation):
            raise ValueError('Invalid input into substation_location_mutator')
        if (not isinstance(mutation_dist_percentage, (float, int))) or mutation_dist_percentage < 0 or mutation_dist_percentage > 100:
            raise ValueError('Invalid input into substation_location_mutator')
        mutation_dist = mutation_dist_percentage /100
        dist = ((x_bounds[1] - x_bounds[0]) + (y_bounds[1] - y_bounds[0])) / 2
        r = gauss(0, mutation_dist * dist) #One standard deviation is in x percent of x_bounds
        theta = 2 * pi * random()
        new_coords = polar_move(sub.get_coordinates(), r, theta)
        if new_coords[0] < x_bounds[0]: #Ensure new coordinates are within operating region
            new_coords[0] = x_bounds[0]
        if new_coords[0] > x_bounds[1]:
            new_coords[0] = x_bounds[1]
        if new_coords[1] < y_bounds[0]:
            new_coords[1] = y_bounds[0]
        if new_coords[1] > y_bounds[1]:
            new_coords[1] = y_bounds[1]
        sub.update_substation_location(new_coords)
        
    def substation_size_mutator(sub):
        '''Randomly mutates one substation's size.
        '''
        if not isinstance(sub, substation):
            raise ValueError('Invalid input into substation_size_mutator')
        sub_index = list(sub.get_max_cap_to_cost_index().keys()).index(sub.get_max_cap())
        sub_index += choice([-1, 1])
        
        if sub_index < 0:
            sub_index += 1
        elif sub_index > len(sub.get_max_cap_to_cost_index().keys()) - 1:
            sub_index -= 1
            
        new_cap = list(sub.get_max_cap_to_cost_index().keys())[sub_index]
        sub.update_substation_capacity(new_cap)
        
    
    def substation_crossover(coll_of_subs1, coll_of_subs2):
        '''Joins two collections of substations in a set to ensure no duplicates.
        '''
        if not isinstance(coll_of_subs1, collection_of_substations):
            raise ValueError('Invalid input into random_chromosome_selector')
        if not isinstance(coll_of_subs2, collection_of_substations):
            raise ValueError('Invalid input into random_chromosome_selector')
        for sub1 in coll_of_subs2.get_collection():
            coll_of_subs1.add_substation(sub1)
        return coll_of_subs1

    def evolve(old_population, new_population, all_centroids, operator, generation_nr, old_pop_preservation_rate):
        '''new_pop is added to until new_pop has same number of chromosomes as
        old_population
        '''
        if not isinstance(old_population, population):
            raise ValueError('Invalid population input into evolve')
        if not isinstance(new_population, population):
            raise ValueError('Invalid population input into evolve')
        if not isinstance(all_centroids, collection_of_centroids):
            raise ValueError('Invalid centroid input into evolve')
        if not isinstance(operator, Operator):
            raise ValueError('Invalid operator input into evolve')
        if not isinstance(generation_nr, int):
            raise ValueError('Invalid operator input into evolve')
        
        while old_population.get_max_population_size() > new_population.current_population_size():    
            if random() < old_pop_preservation_rate:
                new_chrom = selector.tournament(old_population, 3)
            else:
                selected_operator = operator.oper_select()  # Operator selection step
                selected_chrom1 = selector.tournament(old_population, 3)
                selected_chrom2 = selector.tournament(old_population, 3)
                new_chrom = selected_operator(selected_chrom1, selected_chrom2, all_centroids)
                operator.record_operator_performance(selected_operator, new_chrom, selected_chrom1, selected_chrom2)
    #            if Checker.no_duplicate_cost(new_population, new_chrom): ###########################################################
            new_population.add_chromosome(new_chrom)
        return new_population

class selector:
    def random_chromosome(pop):
        '''Returns a random single chromosome from a population
        '''
        if not isinstance(pop, population):
            raise ValueError('Invalid input into random_chromosome_selector')
        return choice(list(pop.get_collection()))
    
    def tournament(pop, tournament_size):
        if not isinstance(pop, population):
            raise ValueError('Invalid input into tournament')
        if not isinstance(tournament_size, int):
            raise ValueError('Invalid input into tournament')
        best_chromosome = selector.random_chromosome(pop)
        for i in range(tournament_size - 1):
            contender_chromosome = selector.random_chromosome(pop)
            if contender_chromosome.get_cost() < best_chromosome.get_cost():
                best_chromosome = contender_chromosome
        return best_chromosome
    
    def substations(col_of_subs, one_substation):
        '''Randomly selects a specified number (or random number) of
        substations from a chromosome and returns their memory locations in a 
        colection_of_substations class. One_substation is a boolean
        '''
        if not isinstance(col_of_subs, collection_of_substations):
            raise ValueError('Invalid chromosome input into substation_selector')
        if not isinstance(one_substation, int):
            raise ValueError('Invalid max_nr_subs_to_select input into substation_selector')
        if one_substation == 1:  # returns 1 substation of class substation instead of a collection of substations
            selected_substation = choice(list(col_of_subs.get_collection()))
            return selected_substation
        else:
            if len(col_of_subs.get_collection()) == 1:
                k1 = 1
                return col_of_subs,col_of_subs
            
        k1 = randint(1, len(col_of_subs.get_collection()) - 1)
        selected_substations = rndm.sample(population=col_of_subs.get_collection(), k=k1)
        
        new_col_of_subs1 = collection_of_substations()
        new_col_of_subs1.add_collection(selected_substations)
        
        new_col_of_subs2 = collection_of_substations()
        set_of_subs = col_of_subs.get_collection().difference(set(selected_substations))
        new_col_of_subs2.add_collection(set_of_subs)
        
        return new_col_of_subs1, new_col_of_subs2

class Operator:
    
    ## ------------------ Handling apative operator probabilities -------------
    
    def __init__(self, operator_dict, adaptive):
        oper_success_list = []
        oper_nr_usage = []
        for oper in operator_dict:
            oper_success_list.append((oper, 0))
            oper_nr_usage.append((oper, 0))
        self.__operator_nr_success_dict = dict(oper_success_list)
        self.__operator_nr_usage_dict = dict(oper_nr_usage)
        self.__operator_prob_dict = operator_dict
        self.__adaptive = adaptive
    
    def is_adaptive(self):
        return self.__adaptive
    
    def get_operators(self):
        return list(self.__operator_nr_success_dict.keys())

    def get_nr_successes(self, oper):
        if not callable(oper):
            raise ValueError('Invalid input into get_nr_successes')
        return self.__operator_nr_success_dict[oper]
    
    def reset_nr_successes(self, oper):
        if not callable(oper):
            raise ValueError('Invalid input into get_nr_successes')
        self.__operator_nr_success_dict[oper] = 0
    
    def get_nr_usages(self, oper):
        if not callable(oper):
            raise ValueError('Invalid input into get_nr_usages')
        return self.__operator_nr_usage_dict[oper]
    
    def reset_nr_usages(self, oper):
        if not callable(oper):
            raise ValueError('Invalid input into get_nr_successes')
        self.__operator_nr_usage_dict[oper] = 0
    
    def get_operator_prob(self, oper):
        if not callable(oper):
            print(oper)
            raise ValueError('Invalid input into get_operator_prob')
        return self.__operator_prob_dict[oper]
    
    def record_operator_performance(self, oper, new_chrom, old_chrom1, old_chrom2):
        if not callable(oper):
            raise ValueError('Invalid input into record_operator_success')
        if not isinstance(new_chrom, chromosome):
            raise ValueError('Invalid input into record_operator_success')
        if not isinstance(old_chrom1, chromosome):
            raise ValueError('Invalid input into record_operator_success')
        if not isinstance(old_chrom2, chromosome):
            raise ValueError('Invalid input into record_operator_success')
        self.__operator_nr_usage_dict[oper] += 1
        if oper is Operator.crossover:
            if new_chrom.get_cost() < old_chrom1.get_cost() and new_chrom.get_cost() < old_chrom2.get_cost():
                self.__operator_nr_success_dict[oper] += 1
        else:
            if new_chrom.get_cost() < old_chrom1.get_cost():
                self.__operator_nr_success_dict[oper] += 1

    def set_new_prob(self, prob, oper):
        if not callable(oper):
            raise ValueError('Invalid input into set_new_prob')
        if not (isinstance(prob, (int, float))) and not (prob <= 1.001 and prob >= 0):
            raise ValueError('Invalid prob input into set_new_prob')
        self.__operator_prob_dict[oper] = prob
    
    def update_weights(self):
        adjustment_const = 0.002
        total_nr_successes = 0
        for op in self.get_operators():
            total_nr_successes += self.get_nr_successes(op)
        for op in self.get_operators():
            if total_nr_successes > 0:  # Check some successes have been achieved
                success_ratio = self.get_nr_successes(op) / total_nr_successes
                new_prob = self.get_operator_prob(op) + adjustment_const * success_ratio
                self.set_new_prob(new_prob, op)
            if self.get_operator_prob(op) < 0.01:
                self.set_new_prob(0.01, op)
        total_prob = 0  # normalize values
        for op in self.get_operators():
            total_prob += self.get_operator_prob(op)
        for op in self.get_operators():
            new_prob = self.get_operator_prob(op) / total_prob
            self.set_new_prob(new_prob, op)
    
    def get_success_percentage(self):
        success_percentage_list = []
        for op in self.get_operators():
            if self.get_nr_usages(op) == 0:
                success_percentage = 0
            else:
                success_percentage = self.get_nr_successes(op) / self.get_nr_usages(op) * 100
            success_percentage_list.append(success_percentage)
        return success_percentage_list
    
    def reset(self):
        for op in self.get_operators():
            self.reset_nr_successes(op)
            self.reset_nr_usages(op)
    
    def update(self):
        success_percentage_list = self.get_success_percentage()
        if self.is_adaptive():
            self.update_weights()
        self.reset()
        return success_percentage_list
        
    ## ------------------- Operator functions ---------------------------------

    def mutate_substation_location(chrom1, chrom2, all_centroids):
        '''Returns a mutated collection of substations in a new memory location.
        Calculated from the given population.
        '''
        if not isinstance(chrom1, chromosome):
            raise ValueError('Invalid input into mutate_location')
        if not isinstance(all_centroids, collection_of_centroids):
            raise ValueError('Invalid input into mutate_substation_location')
        col_of_subs = collection_of_substations()
        for gene1 in chrom1.get_collection():
            sub = copy.deepcopy(gene1.get_substation())
            sub.reset_sub()
            col_of_subs.add_substation(sub)
        selected_substation = selector.substations(col_of_subs, 1)
        process.substation_location_mutator(selected_substation, 0.1, all_centroids.get_x_bounds(), all_centroids.get_y_bounds())
        return generator.create_chromosome(all_centroids, col_of_subs)
    
    def mutate_substation_size(chrom1, chrom2, all_centroids):
        '''Returns a mutated collection of substations in a new memory location.
        Calculated from the given population.
        '''
        if not isinstance(chrom1, chromosome):
            raise ValueError('Invalid input into mutate_location')
        if not isinstance(all_centroids, collection_of_centroids):
            raise ValueError('Invalid input into mutate_substation_size')
        col_of_subs = collection_of_substations()
        for gene1 in chrom1.get_collection():
            sub = copy.deepcopy(gene1.get_substation())
            sub.reset_sub()
            col_of_subs.add_substation(sub)
        selected_substation = selector.substations(col_of_subs, 1)
        process.substation_size_mutator(selected_substation)
        return generator.create_chromosome(all_centroids, col_of_subs)
    
    def crossover(chrom1, chrom2, all_centroids):
        '''To keep the operators on similar compute times only one offspring is
        created.
        '''
        if not isinstance(chrom1, chromosome):
            raise ValueError('Invalid chromosome1 input into mutate_location')
        if not isinstance(chrom2, chromosome):
            raise ValueError('Invalid chromosome2 input into mutate_location')
        if not isinstance(all_centroids, collection_of_centroids):
            raise ValueError('Invalid input into crossover')       
        col_of_subs1 = collection_of_substations()
        for gene1 in chrom1.get_collection():
            col_of_subs1.add_substation(gene1.get_substation())
       
        col_of_subs2 = collection_of_substations()
        for gene1 in chrom2.get_collection():
            col_of_subs2.add_substation(gene1.get_substation())
            
        col_of_subs11, col_of_subs12 = selector.substations(col_of_subs1, 0)
        col_of_subs21, col_of_subs22 = selector.substations(col_of_subs2, 0)
        
        col_of_subs3 = process.substation_crossover(col_of_subs11, col_of_subs22)
        col_of_subs4 = process.substation_crossover(col_of_subs12, col_of_subs21)
        
        col_of_subs5 = collection_of_substations()
        col_of_subs6 = collection_of_substations()
        
        for sub in col_of_subs3.get_collection():
            sub1 = copy.deepcopy(sub)
            sub1.reset_sub()
            col_of_subs5.add_substation(sub1)
        
        for sub in col_of_subs4.get_collection():
            sub1 = copy.deepcopy(sub)
            sub1.reset_sub()
            col_of_subs6.add_substation(sub1)
        
        offspring1 = generator.create_chromosome(all_centroids, col_of_subs5)
        offspring2 = generator.create_chromosome(all_centroids, col_of_subs6)
        
        if offspring1.get_cost() < offspring2.get_cost():
            return offspring1
        return offspring2

    def oper_select(self):
        counter = 0
        while 1:
            for op in self.get_operators():
                if random() < self.get_operator_prob(op):
                    return op
            counter += 1
            if counter > 1000:
                raise ValueError('Large search depth in oper_select')

## ----------------- Class to Check for duplicates ----------------------------

class Checker:
    def no_duplicate_cost(pop, chrom):
        '''Simple duplicate checker to check if a chromosome already exists in 
        a population with equal fitness.
        '''
        if not isinstance(pop, population):
            raise ValueError('Invalid input into np_duplicate')
        if not isinstance(chrom, chromosome):
            raise ValueError('Invalid input into np_duplicate')
        for chrom1 in pop.get_collection():
            if chrom1.get_cost() == chrom.get_cost():
                return 0
        return 1
    
    