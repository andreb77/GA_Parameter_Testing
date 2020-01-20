import pickle
import pandas as pd
import matplotlib.pyplot as plt
import copy
import matplotlib.animation as animation
from matplotlib import rcParams
from Object_Defs import chromosome, collection_of_centroids, population
from Processes import Operator

class CollectionOfPopulations:
    '''This stores all the generations of one program run
    '''
    __red = "#e41a1c"
    __blue = "#377eb8"
    __gray = "#dadada"
    def __init__(self, all_centroids):
        if not isinstance(all_centroids, collection_of_centroids):
            raise ValueError('Invalid centroid input into Recorder')
        self.__collection = []
        self.__col_of_centroids = all_centroids
    
    def add_population(self, pop):
        if not isinstance(pop, population):
            raise ValueError('Invalid input into add_population')
        self.__collection.append(copy.deepcopy(pop))
        
    def get_collection(self):
        return self.__collection

    def get_best_cost(self):
        return self.__collection[-1].get_best_cost()
    
    def get_best_chromosome(self):
        return self.__collection[-1].get_best_chromosome()
    
    def get_best_chromosome_for_each_generation(self):
        chrom_list = []
        for pop in self.get_collection():
            chrom_list.append(pop.get_best_chromosome())
        return chrom_list
    
    def get_best_cost_progression(self):
        '''Returns a list of the lowest cost for each generation
        '''
        hist_cost_list = []
        for pop in self.get_collection():
            hist_cost_list.append(pop.get_best_cost())
        return hist_cost_list
    
    def animate_best_chromosome(self):
        '''Animates the best chromosome of each generation
        '''
        self.__generation_nr = 0
        rcParams['mathtext.fontset'] = 'cm'
        rcParams['font.size'] = 14
        nvec = self.get_best_chromosome_for_each_generation()
        fig = plt.figure(figsize=(6, 6))
        self.__ax = fig.add_subplot(111)
        ani = animation.FuncAnimation(fig, self.plot_chromosome_for_animation, frames=nvec, blit=False)
        ani.save("Chromosome Evolution.gif", writer='imagemagick', savefig_kwargs={'delay': 12})
        
    def plot_chromosome_for_animation(self, chrom):
        self.__ax.cla()
        if not isinstance(chrom, chromosome):
            raise ValueError('Invalid input into plot_chromosome_for_animation')
        for gene1 in chrom.get_collection():
            for line1 in gene1.get_collection_of_lines().get_collection():
                x_values = [line1.get_substation_coordinates()[0], line1.get_centroid_coordinates()[0]]
                y_values = [line1.get_substation_coordinates()[1], line1.get_centroid_coordinates()[1]]
                plt.plot(x_values, y_values, linewidth=2, color=self.__gray)
            plt.plot(gene1.get_substation_coordinates()[0], gene1.get_substation_coordinates()[1], 
                        marker='.', markersize=15, linewidth=0, color=self.__red)
#        for cent in all_centroids.get_collection():
#            plt.plot(cent.get_coordinates()[0], cent.get_coordinates()[1], 
#                     marker='.', markersize=10, linewidth=0, color=self.__blue)
        plt.axis('off')
        plt.title(f'Generation: {str(self.__generation_nr).zfill(2)} Cost: {int(chrom.get_cost())}')
        plt.xlim(self.__col_of_centroids.get_x_bounds())
        plt.ylim(self.__col_of_centroids.get_y_bounds())
        self.__generation_nr += 1
        
    def animate_cost_distribution(self):
        '''Successively plots all costs of a generation iterating over all 
        generations of one program run
        '''
        self.__generation_nr = 0
        rcParams['mathtext.fontset'] = 'cm'
        rcParams['font.size'] = 14
        nvec = [pop.get_all_costs() for pop in self.get_collection()]
        fig = plt.figure(figsize=(8, 6))
        self.__ax = fig.add_subplot(111)
        ani = animation.FuncAnimation(fig, self.plot_cost_list_for_animation, frames=nvec, blit=False)
        ani.save("Cost Distribution.gif", writer='imagemagick', savefig_kwargs={'delay': 6})
        
    def plot_cost_list_for_animation(self, cost_list):
        self.__ax.cla()
        if not isinstance(cost_list, list):
            raise ValueError('Invalid input into plot_cost_list_for_animation')
        cost_list.sort(reverse=False)
        plt.plot(cost_list)
#        plt.title('Cost: {:.4f}'.format(min(cost_list)))
        plt.title(f'Generation: {str(self.__generation_nr).zfill(2)} Cost: {int(min(cost_list))}')
        plt.xlabel('Chromosome number')
        plt.ylabel('Cost')
        plt.xlim(0, len(cost_list))
        plt.ylim(3000, 30000)
        self.__generation_nr += 1
        
class CollectionOfProgramRuns:
    '''Stores CollectionsOfPopulations
    '''
    __red = "#e41a1c"
    __blue = "#377eb8"
    __gray = "#dadada"
    def __init__(self, all_centroids):
        if not isinstance(all_centroids, collection_of_centroids):
            raise ValueError('Invalid centroid input into Recorder')
        self.__collection = []
        self.__col_of_centroids = all_centroids
        
    def add_collection_of_pops(self, col_of_pops):
        if not isinstance(col_of_pops, CollectionOfPopulations):
            raise ValueError('Invalid input into add_collection_of_pops')
        self.__collection.append(col_of_pops)
        
    def get_collection(self):
        return self.__collection
    
    def save_best_costs(self):
        best_cost_list = []
        for col_of_pops in self.get_collection():
            best_cost_list.append(col_of_pops.get_best_cost())
        cost_result_df = pd.DataFrame(best_cost_list)
        cost_result_df.to_csv('cost_results.csv')

    def plot_all_run_costs(self):
        plt.figure("All Run Costs")
        for col_of_pops in self.get_collection():
            one_run_costs = col_of_pops.get_best_cost_progression()
            plt.plot(one_run_costs)
        plt.show()
    
    def pickle_out(self, instance):
        if not isinstance(instance, CollectionOfProgramRuns):
            raise ValueError('Invalid input into pickle_out')
        pickle_out = open('CollectionOfProgramRuns.pickle', 'wb')
        pickle.dump(instance, pickle_out)
        pickle_out.close()
    
    def pickle_in(self):
        pickle_in = open('CollectionOfProgramRuns.pickle', 'rb')
        return pickle.load(pickle_in)
        
class MinimalistRecorder:
    '''Saves the best chromosome from each program run, each
    chromosome in the final population of the last program run and the operator
    probability progression in the final program run.
    Also used for terminate conditions.
    '''
    __red = "#e41a1c"
    __blue = "#377eb8"
    __gray = "#dadada"
    def __init__(self):
        self.__colection_of_hist_best_costs = []  # list of HistoricCost classes
        self.__best_program_run_chromosomes = []
        self.__hist_operator_success_percentage = []
        self.__final_pop = []
        self.__terminate_condition = 0

#    def new_cost_list(self):
        

    def add_generation_best_cost(self, chrom_cost, generation_nr):
        '''The best cost of each generation of every program run
        '''
        if not isinstance(chrom_cost, (float, int)):
            raise ValueError('Invalid input into add_generation_best_cost')
        if generation_nr == 0:
            self.__colection_of_hist_best_costs.append(HistoricCost())
        latest_historic_cost_instance = self.__colection_of_hist_best_costs[-1]
        latest_historic_cost_instance.add_best_cost(chrom_cost)
    
    def get_collection_of_historic_costs(self):
        return self.__colection_of_hist_best_costs
    
    def termination_condition(self, threshold_percentage):  # This is not dynamically programmed
        if len(self.get_collection_of_historic_costs()) == 0:
            return 0
        hist_cost = self.get_collection_of_historic_costs()[-1].get_costs()
        if len(hist_cost) < 50:
            self.__terminate_condition = 0
            return 0
        elif ((hist_cost[-50] - hist_cost[-1]) / hist_cost[-1])*100 < threshold_percentage and self.__terminate_condition == 0:
                self.__terminate_condition = 1
                return 1
        self.__terminate_condition = 0
        return 0
        
    def add_best_program_run_chromosome(self, chrom):
        if not isinstance(chrom, chromosome):
            raise ValueError('Invalid input into add_best_program_run_chromosome')
        self.__best_program_run_chromosomes.append(chrom)
        
    def get_best_program_run_chromosomes(self):
        return self.__best_program_run_chromosomes
    
    def add_final_pop_chrom_info(self, pop):
        '''Add one cost at a time. Input chromosomes must be pre-sorted
        '''
        if not isinstance(pop, population):
            raise ValueError('Invalid input into add_final_pop_cost_distribution')
        self.__final_pop = pop
        
    def get_final_pop(self):
        return self.__final_pop
        
    def add_operator_success_percentage(self, operator_succcess_list, operator_class):
        '''Adds operator success count for each generation.
        '''
        if not isinstance(operator_succcess_list, list):
            raise ValueError('Invalid input into add_operator_success_count')
        if not isinstance(operator_class, Operator):
            raise ValueError('Invalid input into add_operator_success_count')
        self.__operator_class = operator_class
        self.__hist_operator_success_percentage.append(operator_succcess_list)
    
    def get_operator_class(self):
        return self.__operator_class
    
    def get_operator_success_percentage(self):
        return self.__hist_operator_success_percentage

    def plot_historic_cost_nr(self, program_run_nr):
        '''Plot historic costs from one program run.
        '''
        plt.close('One Run Costs')
        plt.figure('One Run Costs')
        if not isinstance(program_run_nr, int):
            raise ValueError('Invalid input into plot_historic_cost_nr')
        plt.close(f'Historic Cost From Program Run Number {program_run_nr}')
        plt.close(f'Historic Cost From Program Run Number {program_run_nr}')
        plt.plot(self.get_collection_of_historic_costs()[program_run_nr].get_costs())
        plt.title('One Run Costs')
        plt.xlabel('Generation Number')
        plt.ylabel('Cost')
        plt.show()

    def plot_all_run_costs(self):
        plt.close('All Run Costs')
        plt.figure('All Run Costs')
        for cost_instance in self.get_collection_of_historic_costs():
            one_run_costs = cost_instance.get_costs()
            plt.plot(one_run_costs)
        plt.show()

    def save_best_program_run_costs(self):
        best_cost_list = []
        for chrom in self.get_best_program_run_chromosomes():
            best_cost_list.append(chrom.get_cost())
        cost_result_df = pd.DataFrame(best_cost_list)
        cost_result_df.to_csv('Results/Cost Results.csv')
        
    def save_final_population(self):
        arr = []
        population_list = self.get_final_pop().get_elitist(100)
        population_list = list(sorted(population_list, key=lambda x: x.get_cost()))        
        for chrom in population_list:  # Transpose data manually
            arr.append([chrom.get_cost(), chrom.get_nr_subs(), chrom.over_capacity()])
        cost_df = pd.DataFrame(columns=['Costs', 'Nr Substations', 'over_capacity'], data=arr)
        cost_df.to_csv('Results/Final Population Costs.csv')
        
    def save_operator_success_count(self):
        operator_list = []
        for op in self.get_operator_class().get_operators():
            operator_list.append(op.__name__)
        df = pd.DataFrame(columns=operator_list, data=self.get_operator_success_percentage())
        df.to_csv('Results/Operator Success Count.csv')
        
    def pickle_out(self, instance):
        if not isinstance(instance, MinimalistRecorder):
            raise ValueError('Invalid input into pickle_out')
        pickle_out = open('Results/MinimalistRecorder.pickle', 'wb')
        pickle.dump(instance, pickle_out)
        pickle_out.close()
    
    def pickle_in(self):
        pickle_in = open('Results/MinimalistRecorder.pickle', 'rb')
        return pickle.load(pickle_in)   
    
class HistoricCost:
    def __init__(self):
        self.__cost_list = []
    def add_best_cost(self, cost):
        if not isinstance(cost, (float, int)):
            raise ValueError('Invalid input into HistoricCost')
        self.__cost_list.append(cost)
    def get_costs(self):
        return self.__cost_list
        
