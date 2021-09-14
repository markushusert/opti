import os
from auxiliary import tryint
import sys
import auxiliary as aux
import numpy as np
import re

g_workspace_dir=os.getcwd()
g_run_dir="dummy_calc"
g_generation_dir="generations"
g_generaton_basename="generation_"
g_generation_list="generation_list"
g_run_data_dir="data"
g_settings_file="settings.txt"
g_calculation_basename="calc_"
g_param_file="params.txt"
g_save_dir="saves"
g_savebasename="save_"
g_local_pop_file="local_pop.txt"
g_start_var_to_export="g_serverjob_start"
g_jobdir_var="jobdir"
name_of_jobdir_to_pass="jobdir_to_pass"

g_debug=True#flag to indicate that script is still in developpement, and no calculations should be started or evaluated

g_settings_dir=".opti"
if not os.path.isdir(g_settings_dir):
    print(f"current directory needs to contain a {g_settings_dir}-directory")
    print("make sure you are starting script in correct directory")
g_joblistfilename="job.list"

g_settings_to_read=["g_dimension","g_pop_size","g_submit_cmd","g_post_cmd","g_mutation_width","g_alpha","g_alpha2"]
g_dimension=None
g_pop_size=None
g_submit_cmd=None
g_post_cmd=None
g_mutation_width=None
g_alpha=None
g_alpha2=None



def get_param_file():
    possible_settings_dirs=get_settings_dirs()
    possible_param_files=[os.path.join(dir,g_param_file) for dir in possible_settings_dirs]
    possible_param_files=[file for file in possible_param_files if os.path.isfile(file)]
    if len(possible_param_files):
        return possible_param_files[-1]
    else:
        raise Exception(f"could not find any param-files named {g_param_file} in {possible_settings_dirs}")
def get_generation_listfile():
    return os.path.join(get_run_data_dir(),g_generation_list)
def get_generation_path(generation_nr):
    new_generation_name=get_generation_dirname(int(generation_nr))
    return os.path.join(get_run_dir(),g_generation_dir,new_generation_name)

def get_jobfile_name(dir):
    if True:
        return g_joblistfilename
    else:
        #old
        return os.path.basename(dir)+".list"#serverjobfiles have the names of the directories they lie in
def get_calculation_dirname(calc_nr):
    return g_calculation_basename+str(calc_nr)
def get_generation_dirname(new_gen_nr):
    return g_generaton_basename+str(new_gen_nr)
def get_settings_dirs():
    #return paths to look for for settings files
    #in order of relevance: last dir will overwrite previous dirs
    return [os.path.join(g_workspace_dir,g_settings_dir),os.path.join(get_run_dir(),g_settings_dir)]
    pass
def get_savefile_dir():
    return os.path.join(get_run_dir(),g_run_data_dir,g_save_dir)
def get_savefile_name(number):
    return f"{g_savebasename}{number}.txt"
def get_savefile_number(savefile_name):
    return get_only_number_of_string(savefile_name)
def get_only_number_of_string(string):
    tokens=re.split('([0-9]+)', string)#split filename in numreic and alphabetical chunks
    numeric_tokens=[aux.tryint(token) for token in tokens if type(aux.tryint(token)) is int]
    if len(numeric_tokens) !=1:
        raise Exception(f"only one number is supposed to be in string: {string}")
    else:
        return numeric_tokens[0]
def get_run_data_dir():
    return os.path.join(get_run_dir(),g_run_data_dir)

def get_dir_of_savefiles():
    return os.path.join(get_run_dir(),g_run_data_dir,g_save_dir)
def get_local_param_file():
    return g_param_file
def get_run_dir():
    if g_run_dir.startswith("/"):
        return g_run_dir
    else:
        return os.path.join(g_workspace_dir,g_run_dir)
def get_main_joblist_file():
    return os.path.join(g_workspace_dir,g_joblistfilename)
def get_to_link_dir():
    return os.path.join(g_workspace_dir,"param_files","to_link")
def get_to_copy_dir():
    return os.path.join(g_workspace_dir,"param_files","to_copy")
def read_settings():
    found_setting={key:False for key in g_settings_to_read}
    for settings_dir in get_settings_dirs():
        if os.path.isdir(settings_dir):
            modell_file=os.path.join(settings_dir,"settings.txt")
            if not os.path.isfile(modell_file):
                print(f"ERROR: trying to read {modell_file} to read settings, could not find file")
                print("make sure you started script in right dir")
                raise Exception
            else:
                with open(modell_file,"r") as fil:
                    for line in fil:
                        for key in g_settings_to_read:
                            if line.startswith(key+"="):
                                found_setting[key]=True
                                try:
                                    value=line.split("=",1)[1].strip()
                                    globals()[key]=eval(value)
                                except:
                                    print(f"error evaluating \"{value}\"")
                                    raise Exception

                                if key.endswith("dir"):
                                    #interpret paths in settings.txt relative to given textfile
                                    globals()[key]=os.path.abspath(os.path.join(modell_file,globals()[key]))
                                
                    
    unset_settings=[key for key,value in found_setting.items() if not value]
    if len(unset_settings):
        raise Exception(f"could not find settings: {unset_settings}")
read_settings()

