#!/usr/bin/python3
# evo.py


import numpy as np
from numpy.core.fromnumeric import argsort
import matplotlib.pyplot as plt
import os

def opti(pop_size, max_gen, alpha, alpha2, sigma,
  rng, dim, range_in, mut_width, n_child):

  N = pop_size
  ploti=1
  # create a population of possible solutions
  # population=np.array float32 (N,dom)
  population = load_population(N, dim, rng, range_in)
  errors = np.zeros(N, dtype=np.float32)
  best_over_gen = np.zeros(max_gen+1, dtype=np.float32)
  gen_number = np.zeros(N, dtype=np.uint)

  #evaluate starting population
  for i in range(N):
    errors[i] = error(population[i])   #adapt for simulations

  #find best solution and best error of starting population
  best_soln = population[0]  # 
  best_err = errors[0]
  for i in range(N):
    err = error(population[i])
    if err < best_err:
      best_err = err
      best_soln = np.copy(population[i])
  interval = (int)(max_gen // 10)
  best_over_gen[0]=best_err

  for gen in range(max_gen):
    mut_width_i=mut_width[0]- gen/max_gen*(mut_width[0]-mut_width[1]) #starts at maximum and decreases linearly
    new_pop=make_child_population(population,errors,mut_width_i,alpha,alpha2,n_child,range_in)
    
    for iter in range(n_child):
        child = new_pop[iter,:]
        #idx = select_bad(errors, sigma, rng)   # index of bad point --> overwritten with child # now changed to only adding childs to population, no death

        #evaluate child and and add results to arrays
        err_ch  =error(child)
        population = np.append(population,[child],axis=0)
        gen_number = np.append(gen_number,[gen+1],axis=0)
        errors     = np.append(errors,    [err_ch]  ,axis=0)
        if err_ch < best_err:
          best_err = err_ch
          best_soln = np.copy(child)
    best_over_gen[gen+1]=best_err
    gen_plus=gen+1
    if gen_plus % interval == 0:
      print("generation = " + str(gen_plus))
      print("best solution: ", end="")
      print(best_soln)
      print("best error = %0.6f " % best_err)
      print("==================")
      os.makedirs("Results",exist_ok=True)
      if ploti==1:
        plt.scatter(population[:,0], population[:,1],c=gen_number,cmap='viridis', vmin=0, vmax=max_gen)
        plt.colorbar()
        plt.savefig('Results/'+str(gen_plus)+'.png')
        plt.close()
      if gen_plus==max_gen:
        plt.plot(best_over_gen)
        plt.xlabel('Generation')
        plt.ylabel('Result')
        plt.savefig('Results/plot_Result-Generation.png')
        plt.close()


  return best_soln

#def make_solution(dim, rng):
#  return np.float32(rng.uniform(low=-2.0, high=2.0,
#    size=dim))

def error(soln):
  # f(x,y) = 100(y – x^2)^2 + (1 – x)^2
  # solution is x=1, y=1 giving f(x,y) = 0.0
  x = soln[0]; y = soln[1]
  a = np.float32(100 * (y - (x * x)) * (y - (x * x)))
  b = np.float32((1 - x) * (1 - x))
  computed = a + b
  return np.abs(0.0 - computed) 

def load_population(popsize, dim, rng, range_in):
  return np.float32(rng.uniform(low=range_in[0], high=range_in[1],
    size=(popsize,dim)))
def make_child_population(population,errors,mutation_width,alpha, alpha2,n_child,range_in):
  (p1, p2) = select_two_good(errors, alpha, alpha2, np.random)#selects 2 parents for the next generation, based 
  dimensions=population.shape[1]
  new_pop=np.zeros((0,dimensions))
  for iter in range(n_child):
      child = make_child(population, p1, p2, np.random)
      mutate(child, np.random, range_in, mutation_width)
      child_2d=np.reshape(child,(1,dimensions))
      new_pop=np.append(new_pop,child_2d,axis=0)
  return new_pop
def make_child(population, p1, p2, rng):
  parent1 = population[p1]
  parent2 = population[p2]
  dim = len(parent1)
  idx = rng.randint(1,dim)  # (0,dim) could make a clone
  child = np.zeros(dim, dtype=np.float32)
  #take first <idx> parameters from parent1 and remaining block from parent2
  for j in range(0, idx): child[j] = parent1[j]
  for j in range(idx, dim): child[j] = parent2[j]
  return child

def mutate(child, rng, range_in, mut_width):
  dim = len(child)
  range_tot=range_in[1]-range_in[0]
  for j in range(dim):
      child[j] += rng.uniform(-mut_width*range_tot, mut_width*range_tot)
      child[j] = max(child[j],range_in[0])
      child[j] = min(child[j],range_in[1])
  return

def select_good(errors, pct, rng):
  # select the index of a good solution
  N = len(errors)
  n = np.int(N * pct)  # number solns to examine
  all_indices = np.arange(N)  # [0, 1, 2, . . ]
  rng.shuffle(all_indices)
  selected_errors = errors[all_indices[0:n]]  #choose best value out of n
  idx = np.argmin(selected_errors)            # index of best of n
  return idx

def select_good2(errors, alpha2, rng,n):  # gives each individual a probability depending on sorted fitness: higher fitness-- better chance
  # select the index of a good solution
  n = len(errors)
  indis = argsort(errors)  #sorted indices of errors

  a=np.zeros(n, dtype=np.float32)
  probability=np.zeros(n, dtype=np.float32)
  prob2=a
  indis_inv=a       # 
  for i in range(n):
      a[i]=i
      i2=np.float32(i+1)
      probability[i]=1/i2 ** alpha2#probability= probability for each index in sorted error list to be chosen
      prob2[i]=sum(probability)#accumulated probability at each index

  testi=rng.uniform(0,1)
  testi=testi*prob2[-1]#random float from 0 to total accumulated probaiility

  indi=np.searchsorted(prob2,testi)  #index in sorted vector
  idx=indis[indi]  #index in errors
  if idx==indis.shape[0]:
    idx2=idx-1 #last and second to last if idx==last
  else:
    idx2=indis[indi+1]  #index parent 2
  return [idx, idx2]

def select_two_good(errors, pct, alpha2, rng):
  #result1 = select_good(errors, pct, rng)
  #result2 = select_good(errors, pct, rng)
  n=2 #give 2 parents
  [result1, result2] = select_good2(errors, alpha2, rng, n)
  return (result1, result2)  # tuple

#def select_bad(errors, pct, rng):
#  # select the index of a bad solution
#  N = len(errors)
#  n = np.int(N * pct)  # number solns to examine
#  all_indices = np.arange(N)  # [0, 1, 2, . . ]
#  rng.shuffle(all_indices)
#  selected_errors = errors[all_indices[0:n]]
#  idx = np.argmax(selected_errors)
#  return idx  

def main():
  print("\nBegin evolutionary optimization demo ")
  np.set_printoptions(precision=4, suppress=True)

  #rng = np.random.RandomState(0)
  rng = np.random
  pop_size = 100
  max_gen = 40
  n_child =10
  alpha = 0.80              # selection pressure good parents
  alpha2 = 1.4 #for function select_good2, alpha2 in [1,2], 1... higher chance for all, 2 ... higherchance for best individual
  sigma = 0.3            # removed, no death
  dim=2                     # number of dimensions
  range_in = [-5.0,5.0]        # Range of inputvalues
  mut_width = [0.1,0.02]    # width of mutation, for first and last generation, interpolation in between

  best_soln = opti(pop_size, max_gen, alpha, alpha2,
    sigma, rng, dim, range_in, mut_width, n_child)

  print("\nFinal best solution: ")
  print(best_soln)

  print("\nEnd demo ")

if __name__ == "__main__":
  main()
