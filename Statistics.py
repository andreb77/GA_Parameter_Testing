from Object_Defs import chromosome
from Processes import Operator
import matplotlib.pyplot as plt

class Stats:
    __red = "#e41a1c"
    __blue = "#377eb8"
    __gray = "#dadada"
    def chromosome(self, chrom):
        if not isinstance(chrom, chromosome):
            raise ValueError('Invalid input into chromosome_stats')
        print('')
        print(f'Solution cost: {round(chrom.get_cost(),2)}')
        print(f'Solution has {len(chrom.get_collection())} substations')
        print(f'Over-capacity?: {chrom.over_capacity()}')
        for gene1 in chrom.get_collection():
            max_cap = gene1.get_substation().get_max_cap()
            cap_remaining = gene1.get_substation().get_remaining_cap()
            line_cost_penalty = gene1.get_collection_of_lines().get_cost()
            line_cost_no_penalty = 0
            line_costs = []
            for line1 in gene1.get_collection_of_lines().get_collection():
                line_cost_no_penalty += line1.get_cost()
                line_costs.append(int(line1.get_cost()))
            line_costs.sort()
            print(f'Gene has cost: {round(gene1.get_cost(),2)}')
            print(f'    Substation Capacity: {round(cap_remaining,1)} remaining of {max_cap}')
            print(f'Substation cost: {gene1.get_substation().get_cost()}')
            print(f'    Total Lines cost: {round(line_cost_no_penalty,2)} Penalty cost: {round(line_cost_penalty - line_cost_no_penalty,2)}')
            print(f'    {line_costs}')
            print('')
        self.plot_chromosome(chrom)
        
    def generation(self, pop, operator, generation_nr):
        best_chrom = pop.get_elitist(100)[0]
        lowest_cost = best_chrom.get_cost()
        print(f'{str(int(lowest_cost)).zfill(5)}', end='')
        print(f' Generation: {str(generation_nr).zfill(3)}')
        oper_prob_lst = [operator.get_operator_prob(Operator.crossover), operator.get_operator_prob(Operator.mutate_substation_location), operator.get_operator_prob(Operator.mutate_substation_size)]
        oper_prob_lst = [ '%.2f' % elem for elem in oper_prob_lst ]
        print(oper_prob_lst)
    
    def plot_chromosome(self, chrom):
#        self.__ax.cla()
        plt.close('Chromosome')
        plt.figure('Chromosome')
        if not isinstance(chrom, chromosome):
            raise ValueError('Invalid input into plot_chromosome_for_animation')
        for gene1 in chrom.get_collection():
            for line1 in gene1.get_collection_of_lines().get_collection():
                x_values = [line1.get_substation_coordinates()[0], line1.get_centroid_coordinates()[0]]
                y_values = [line1.get_substation_coordinates()[1], line1.get_centroid_coordinates()[1]]
                plt.plot(x_values, y_values, linewidth=2, color=self.__gray)
                
            for centroid1 in gene1.get_collection_of_centroids().get_collection():
                x_value_c = centroid1.get_coordinates()[0]
                y_value_c = centroid1.get_coordinates()[1]
                plt.plot(x_value_c, y_value_c, marker='.', markersize=3, linewidth=0, color=self.__blue)
            
            
            plt.plot(gene1.get_substation_coordinates()[0], gene1.get_substation_coordinates()[1], 
                        marker='.', markersize=15, linewidth=0, color=self.__red)

        plt.axis('off')
        plt.title('Solution Cost: {:.0f}'.format(chrom.get_cost()))
