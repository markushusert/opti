import py_evo_rosenbrock as evo
import numpy as np
import settings
g_range=[0,1]
def create_starting_population(new_pop_size):
    return evo.load_population(new_pop_size,settings.g_dimension,np.random,g_range)
    

def create_population_via_evolution(population,errors,new_pop_size,generation_nr):
    return evo.make_child_population(population,errors,settings.g_mutation_width[generation_nr-1],settings.g_alpha,settings.g_alpha2,new_pop_size,g_range)
    print("using evolution")
    return