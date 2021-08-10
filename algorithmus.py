import py_evo_rosenbrock as evo
import numpy as np
import settings
def create_starting_population(new_pop_size):
    return evo.load_population(new_pop_size,settings.g_dimension,np.random,[0,1])
    

def create_population_via_evolution():
    print("using evolution")
    return