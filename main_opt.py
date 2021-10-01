#!/usr/bin/python3
import genericpath
import manage_optimierung as manage
import settings
import os
import sys
import numpy as np

def pass_cmd_line_args():
    if len(sys.argv)<2:
        print("provide run-directory at command line")
        exit()
    else:
        settings.g_run_dir=sys.argv[1]
        settings.g_joblistfilename=settings.g_run_dir+".list"
        try:
            #try to create run directory
            os.mkdir(settings.g_run_dir)
            #try to create dir for different gengerations
            manage.create_new_dir(settings.g_generation_dir)
        except:
            pass
        settings.read_settings()

def main():
    pass_cmd_line_args()
    generation_list=manage.get_all_gens()
    number_run_generations=len(generation_list)
    population,gen_numbers,errors=manage.read_current_state()
    latest_evaluated_generation=int(gen_numbers[-1] if gen_numbers.size else -1)
    if len(generation_list)!=0:#there exist some generation folders
        while number_run_generations>latest_evaluated_generation+1:#+1 because first generation starts at 0
            population_to_add,gen_nr_to_add,errors_to_add=manage.eval_generation(latest_evaluated_generation+1)
            population=np.append(population,population_to_add,axis=0)
            gen_numbers=np.append(gen_numbers,gen_nr_to_add,axis=0)
            errors=np.append(errors,errors_to_add,axis=0)
            
            latest_evaluated_generation+=1

    new_gen_dir=manage.create_new_generation(population,gen_numbers,errors,latest_evaluated_generation+1)
    manage.run_generation(new_gen_dir)
    #manage_optimierung.create_empty_generation("dummy_generation")

if __name__=="__main__":
    main()