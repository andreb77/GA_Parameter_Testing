from Functions import scalar_dist

class centroid:
    def __init__(self, x, y, peak):
        if not (isinstance(x, float) or isinstance(x, int)):
            raise ValueError('Invalid input into centroid')
        if not (isinstance(y, float) or isinstance(y, int)):
            raise ValueError('Invalid input into centroid')
        if not (isinstance(peak, float) or isinstance(peak, int)):
            raise ValueError('Invalid input into centroid')
        self.__coordinates = (x, y)
        self.__peak = peak
    def get_coordinates(self): 
        return self.__coordinates
    def get_peak(self):
        return self.__peak
    
class collection_of_centroids:
    def __init__(self):
        self.__collection = set()
    def add_centroid(self, cent):
        if not isinstance(cent, centroid):
            raise ValueError('Invalid input into collection_of_centroids')
        self.__collection.add(cent)
    def get_collection(self): 
        return self.__collection
    def get_number_of_centroids(self):
        self.__number_of_centroids = len(self.get_collection())
        return self.__number_of_centroids
    def get_x_bounds(self):
        self.__x_bounds = [min([cent.get_coordinates()[0] for cent in self.get_collection()]), max([cent.get_coordinates()[0] for cent in self.get_collection()])]
        return self.__x_bounds
    def get_y_bounds(self):
        self.__y_bounds = [min([cent.get_coordinates()[1] for cent in self.get_collection()]), max([cent.get_coordinates()[1] for cent in self.get_collection()])]
        return self.__y_bounds
    
class line:
    __cost_per_distance = 0.01
    def __init__(self, substation_coordinates, centroid_coordinates, line_capacity):
        if not (isinstance(substation_coordinates, list) and len(substation_coordinates) == 2):
            raise ValueError('Invalid input into line: substation_coordinate')
        if not (isinstance(centroid_coordinates, tuple) and len(centroid_coordinates) == 2):
            raise ValueError('Invalid input into line: centroid_coordinate')
        if not (isinstance(line_capacity, int) or isinstance(line_capacity, float)):
            raise ValueError('Invalid input into line: line_capacity')
        self.__substation_coordinates = substation_coordinates
        self.__centroid_coordinates = centroid_coordinates
        self.__line_capacity = line_capacity
        self.__cost = self.__cost_per_distance * scalar_dist(self.get_substation_coordinates(), self.get_centroid_coordinates())
    def get_substation_coordinates(self):
        return self.__substation_coordinates
    def get_centroid_coordinates(self):
        return self.__centroid_coordinates
    def get_line_capacity(self):
        return self.__line_capacity
    def get_cost(self):
        return self.__cost
    def get_length(self):
        return scalar_dist(self.get_centroid_coordinates(), self.get_substation_coordinates())

class collection_of_lines:
    def __init__(self):
        self.__collection = set()
        self.__cost = 0
    def add_line(self, line_instance):
        if not isinstance(line_instance, line):
            raise ValueError('Invalid input into collection_of_lines')
        self.__collection.add(line_instance)
    def get_collection(self): 
        return self.__collection
    def get_cost(self):
        return self.__cost
    def add_cost(self, cost):
        self.__cost += cost

class substation: #transmission zone substation
    __max_cap_to_cost_index = {1:360, 2:400, 3:440, 4:560, 5:720, 10:1200}
#    __max_cap_to_cost_index = {4000:1000000, 10000:2000000, 20000:5000000, 30000:10000000, 40000:15000000, 50000:20000000, 60000:25000000}
#    {10:1, 20:2, 50:5, 100:10, 150:15, 200:20, 250:25}
    def __init__(self, coordinates, sub_cap):
        if not (isinstance(coordinates, list) and len(coordinates) == 2):
            raise ValueError('Invalid coordinate input into substation')
        if not sub_cap in list(self.__max_cap_to_cost_index.keys()):
            raise ValueError('Invalid capacity input into substation')
        self.__coordinates = coordinates
        self.__max_cap = sub_cap
        self.__cap_remaining = sub_cap
        self.__cost = self.__max_cap_to_cost_index[sub_cap]
    def get_coordinates(self):
        return self.__coordinates
    def get_max_cap(self): 
        return self.__max_cap
    def get_remaining_cap(self): 
        return self.__cap_remaining
    def deduct_cap(self, line_capacity):
        if not (isinstance(line_capacity, float) or isinstance(line_capacity, int)): 
            raise ValueError('Invalid input into substation loading')
        self.__cap_remaining -= line_capacity
#    def reset_cap(self):
#        self.__cap_remaining = self.__max_cap
    def get_cost(self):
        return self.__cost
    def get_max_cap_to_cost_index(self):
        return self.__max_cap_to_cost_index
    def update_substation_location(self, new_coordinates):
        if not (isinstance(new_coordinates, list) and len(new_coordinates) == 2):
            raise ValueError('Invalid input into line: substation_coordinate')
        self.__coordinates = new_coordinates
    def update_substation_capacity(self, new_cap):
        if not new_cap in list(self.__max_cap_to_cost_index.keys()):
            raise ValueError('Invalid capacity input into mutate_substation_size')
        self.__max_cap = new_cap
        self.reset_sub()
    def reset_sub(self):
        '''Reset capacity remaining and cost
        '''
        self.__cap_remaining = self.__max_cap
        self.__cost = self.__max_cap_to_cost_index[self.__max_cap]

class collection_of_substations:
    ''' Class to ensure there are no duplicate substations introduced into the 
    same chromosome
    '''
    def __init__(self):
        self.__collection = set()
    def add_substation(self, sub):
        if not isinstance(sub, substation):
            raise ValueError('Invalid substation input into collection_of_substations')
        self.__collection.add(sub)
    def add_collection(self, col_of_subs):
        if not isinstance(col_of_subs, (collection_of_substations, list, set)):
            raise ValueError('Invalid substation input into collection_of_substations')
        if isinstance(col_of_subs, collection_of_substations):
            for sub in col_of_subs.get_collection:
                self.add_substation(sub)
        elif isinstance(col_of_subs, (list, set)):
            self.__collection = self.__collection.union(set(col_of_subs))
    def get_collection(self):
        return self.__collection

class gene:
    def __init__(self, sub):
        if not isinstance(sub, substation):
            raise ValueError('Invalid substation input into gene')
        self.__substation = sub
        self.__cost = 0
        self.__collection_of_lines = collection_of_lines()
        self.__collection_of_centroids = collection_of_centroids()
    def get_substation(self):
        return self.__substation
    def get_collection_of_lines(self): 
        return self.__collection_of_lines
    def get_collection_of_centroids(self): 
        return self.__collection_of_centroids
    def get_substation_coordinates(self):
        return self.get_substation().get_coordinates()
    def add_line(self, lin):
        if not isinstance(lin, line):
            raise ValueError('Invalid line input into gene')
        self.__collection_of_lines.add_line(lin)
        self.get_substation().deduct_cap(lin.get_line_capacity())
    def add_centroid(self, cent):
        if not isinstance(cent, centroid):
            raise ValueError('Invalid line input into gene')
        self.__collection_of_centroids.add_centroid(cent)
    def get_cost(self):
        return self.__cost
    def add_cost(self, cost):
        self.__cost += cost

class chromosome:
    """A collection of genes, termed a chromosome. Represents one potential solution
    to the defined problem.
    """
    def __init__(self, collection_of_genes):
        if not (isinstance(collection_of_genes, list) or isinstance(collection_of_genes[0], gene)):
            raise ValueError('Invalid input into chromosome')
        self.__collection_of_genes = collection_of_genes
        self.__cost = 0
    def get_collection(self):
        return self.__collection_of_genes
    def get_cost(self):
        return self.__cost
    def add_cost(self, cost):
        self.__cost += cost
    def get_nr_subs(self):
        return len(self.__collection_of_genes)
    def over_capacity(self):
        for gene in self.get_collection():
            if gene.get_substation().get_remaining_cap() < 0:
                return 1
        return 0

class population:
    def __init__(self, max_pop_size):
        if not isinstance(max_pop_size, int):
            raise ValueError('Maximum population size input is not correct datatype')
        self.__maximum_population_size = max_pop_size
        self.__collection_of_chromosomes = set()
    def add_chromosome(self, chromosome_instance):
        if not isinstance(chromosome_instance, chromosome): 
            raise ValueError('Invalid input into population')
        if not chromosome_instance in set(self.__collection_of_chromosomes): #checks if the chromosome's memory location is already in the population
            self.__collection_of_chromosomes.add(chromosome_instance)
    def add_collection_of_chromosomes(self, collection_of_chromosomes):
        if not isinstance(collection_of_chromosomes, set): 
            raise ValueError('Invalid input into population')
        self.__collection_of_chromosomes.update(collection_of_chromosomes)
    def get_collection(self): 
        return self.__collection_of_chromosomes
    def get_elitist(self, elitist_percentage):
        if not isinstance(elitist_percentage, (float, int)):
            raise ValueError('Invalid input into get_elitist')
        population_list = list(self.get_collection())
        population_list.sort(key=lambda x: x.get_cost())
        number_elitist_chromosomes = int(self.current_population_size() * elitist_percentage / 100)
        return population_list[:number_elitist_chromosomes]
    def get_best_cost(self):
        population_list = list(self.get_collection())
        population_list.sort(key=lambda x: x.get_cost())
        return population_list[0].get_cost()
    def get_best_chromosome(self):
        population_list = list(self.get_collection())
        population_list.sort(key=lambda x: x.get_cost())
        return population_list[0]
    def get_all_costs(self):
        cost_list = []
        for chrom in self.get_collection():
            cost_list.append(chrom.get_cost())
        return cost_list
    def current_population_size(self): 
        return len(self.get_collection())
#    def set_maximum_population_size(self, max_pop_size):
#        if not isinstance(max_pop_size, int):
#            raise ValueError('Maximum population size getter input is not correct datatype')
#        self.__maximum_population_size = max_pop_size
    def get_max_population_size(self):
        return self.__maximum_population_size
    

#if __name__ == "__main__":
#    cent = centroid([0, 0], 5)
#    coll_of_cents = collection_of_centroids()
#    coll_of_cents.add_centroid(cent)
#    
#    lin = line([0,0],[1,1],5)
#    coll_of_lines = collection_of_lines()
#    coll_of_lines.add_line(lin)
#    
#    sub = substation([1,1], 10)
#    sub.get_max_cap()
#    sub.get_remaining_cap()
#    
#    gene1 = gene(sub, coll_of_lines, coll_of_cents)
#    gene1.get_cost()
#    
#    chrom = chromosome()
#    chrom.add_gene(gene1)
#    chrom.get_cost()
#    
#    pop = population()
#    pop.add_chromosome(chrom)
#    pop.get_collection()
#    
#    sub2 = generator.substation_generator(0,0,10,10)
    
    