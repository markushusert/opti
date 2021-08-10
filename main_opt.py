#!/usr/bin/python3
import genericpath
import manage_optimierung as manage
import settings
import os
import sys

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
    generation_list,most_recent_gen=manage.get_latest_gen()
    population,gen_numbers,errors=manage.read_current_state()

    if generation_list is not None:
        latest_evaluated_generation=gen_numbers[-1]
        while most_recent_gen>latest_evaluated_generation:
            manage.eval_generation(generation_list[latest_evaluated_generation+1])
            latest_evaluated_generation+=1

    manage.create_new_generation(population,gen_numbers,errors,most_recent_gen+1)
    #manage_optimierung.create_empty_generation("dummy_generation")

if __name__=="__main__":
    main()