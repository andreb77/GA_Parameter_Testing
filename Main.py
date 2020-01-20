import pandas as pd
from random import randint
from Functions import population_size_calculator, max_nr_substations_in_chromosome
from Object_Defs import centroid, collection_of_centroids, \
        substation, collection_of_substations, chromosome, population
from Processes import generator, process, Operator
from Recorders import CollectionOfProgramRuns, CollectionOfPopulations, MinimalistRecorder
import time
from Statistics import Stats

if __name__ == "__main__":
    start_time = time.localtime()
    ## -------------- Adding loads from csv to centroid class -----------------
    
    loads = pd.read_csv('loads normalized capacity.csv')
    load_transition = loads[['0', '1', '2']]
    all_centroids = collection_of_centroids()
    for x,y,peak in load_transition.values:
        one_centroid = centroid(x,y,peak)
        all_centroids.add_centroid(one_centroid)

    ## ----------- Important parameters ---------------------------------------

    nr_program_runs = 50
    pop_size = 500
    generations = 250
    
    elitist_percentage = 5
    operator_dict = {Operator.crossover:0.7, Operator.mutate_substation_location:0.25, Operator.mutate_substation_size:0.05}
    operator_adaptive = 0  # 0 or 1
    old_pop_preservation_rate = 0.3  # 0 < 1
    
    local_search = 1 # 0 or 1
    local_search_generations = 1000
    local_search_pop_size = 10
    local_search_operator_dict = {Operator.mutate_substation_location:1}

    recorder = MinimalistRecorder()
    stats = Stats()
#    col_of_prog_runs = CollectionOfProgramRuns(all_centroids)
    
    for run_nr in range(nr_program_runs):
        print(f'Program run nr {str(run_nr).zfill(2)}')
        
        ## ------------- Instantiate population -------------------------------
        
#        number_of_substation_options = len(substation.get_max_cap_to_cost_index(substation).keys())
#        pop_size = population_size_calculator(all_centroids.get_number_of_centroids(), number_of_substation_options)
        pop = population(pop_size)
#        print('Population size = ' + str(pop.get_max_population_size()))

        ## ------------- Fill initial population with chromosomes -------------
    
        for i in range(pop.get_max_population_size()):
            new_chromosome_len = randint(1, max_nr_substations_in_chromosome(all_centroids.get_number_of_centroids()))
            coll_of_substations = collection_of_substations()
            for i in range(new_chromosome_len): #adding substations to coll_of_substations
                new_substation = generator.substation(all_centroids.get_x_bounds(), all_centroids.get_y_bounds())
                coll_of_substations.add_substation(new_substation)
            new_chromosome = chromosome(generator.gene(all_centroids, coll_of_substations))
            process.update_chrom_cost(new_chromosome)
            pop.add_chromosome(new_chromosome)
        
        ## ------------------ Other Initialization ----------------------------
        
        operator = Operator(operator_dict, adaptive=operator_adaptive)  # Instantiates an operator class instance for every new prgram run
#        col_of_pops = CollectionOfPopulations(all_centroids)
        
        ## ------------------ Evolution process -------------------------------
        generation_nr = 0
        while not(recorder.termination_condition(2)) and generation_nr < generations:
            elite_pop = population(pop_size)
            collection_of_chromosomes = pop.get_elitist(elitist_percentage)
            for chrom in collection_of_chromosomes:
                elite_pop.add_chromosome(chrom)
            new_pop = process.evolve(pop, elite_pop, all_centroids, operator, generation_nr, old_pop_preservation_rate)
            success_percentage_list = operator.update()  # Update weights every program run
            ## --------------- Recording --------------------------------------
#            col_of_pops.add_population(new_pop)  # recorder that records every chromosome instance
            if run_nr == nr_program_runs-1:  # Is this the last program run?
                recorder.add_operator_success_percentage(success_percentage_list, operator)
            recorder.add_generation_best_cost(new_pop.get_elitist(100)[0].get_cost(), generation_nr)
            ## --------------- Ancillary --------------------------------------
#            stats.generation(new_pop, operator, generation_nr)
            ## ----------------------------------------------------------------
            pop = new_pop
            generation_nr += 1
        
        ## ------------------- Local Search -----------------------------------
        if local_search == 1:
            local_search_operator_list = [Operator.mutate_substation_location]
            local_search_operator = Operator(local_search_operator_dict, adaptive=0)
             
            generation_nr = 0
            while generation_nr < local_search_generations:
                elite_pop = population(local_search_pop_size)
                elite_pop.add_chromosome(pop.get_best_chromosome())
                best_chrom_in_pop = population(local_search_pop_size)
                best_chrom_in_pop.add_chromosome(pop.get_best_chromosome())
                # Only use the best chromosome from the last population to create mutations.
                new_pop = process.evolve(best_chrom_in_pop, elite_pop, all_centroids, local_search_operator, generation_nr, 0)
                if generation_nr % 100 == 0:    
                    recorder.add_generation_best_cost(new_pop.get_elitist(100)[0].get_cost(), generation_nr)
#                stats.generation(new_pop, operator, generation_nr)
                pop = new_pop
                generation_nr += 1
        ## --------------------------------------------------------------------
#        col_of_prog_runs.add_collection_of_pops(col_of_pops)
        recorder.add_best_program_run_chromosome(new_pop.get_elitist(100)[0])
        if run_nr == nr_program_runs-1:
            recorder.add_final_pop_chrom_info(new_pop)
    
    ## -------------- More Recording ------------------------------------------
    recorder.save_best_program_run_costs()
    recorder.save_final_population()
    recorder.save_operator_success_count()
    recorder.pickle_out(recorder)
    
#    stats.chromosome(pop.get_best_chromosome())
    
    ## -------------- Plotting ------------------------------------------------
#    recorder.plot_all_run_costs()

    print(f'Start Time: {start_time}')
    print(f'Finish Time: {time.localtime()}')
    
