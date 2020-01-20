from math import sqrt, sin, cos, radians

def scalar_dist(coord1, coord2):
    return sqrt( (coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2 )

def polar_move(coord, r, theta):
    '''takes [x,y] value and a scalar dist and angle (in radians), outputs new coordinate (as a list)
    '''
    x_dist = r * sin(radians(theta))
    y_dist = r * cos(radians(theta))
    return [(coord[0] + x_dist), (coord[1] + y_dist)]

def population_size_calculator(number_of_centroids, number_of_substation_capacities):
        maximum_search_space_size = 10**16 * 10**16 * number_of_substation_capacities * number_of_centroids/10 / 2
        # nr centroids / 10 gives maximum number of substations in a solution
        # Search space calculated to be 3.15*10^33
        k = 2 #make k smaller to reduce population size
        size = int(maximum_search_space_size * (1.36 * 10**-32) * k)
        if size > 5000: size = 5000
        elif size < 100: size = 100
        return size

def max_nr_substations_in_chromosome(number_of_centroids):
    return int(number_of_centroids / 10)


