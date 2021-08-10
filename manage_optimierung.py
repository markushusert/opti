import sys
import os
import settings
import shutil
import glob
import subprocess
import auxiliary as aux
import numpy as np
import algorithmus as algo

def create_new_path_in_project(new_path):
    #adds new dir to the project by creating all needed directories and adding entries to all jobfiles
    base_dir=settings.g_workspace_dir

    #check if desired path lies in workspacedir
    common_path_to_ws=os.path.commonpath([base_dir,os.path.abspath(new_path)])
    if common_path_to_ws!=settings.g_workspace_dir:
        print("ERROR, can only create new path inside of project")
        raise ValueError

    relpath_from_ws=os.path.normpath(os.path.relpath(new_path,base_dir))
    path_accum=base_dir
    #loop over all dirs between target and base
    for dir in relpath_from_ws.split(os.sep):
        path_accum=os.path.join(path_accum,dir)
        #if a dir does not exist, create it and add to superior joblist
        if not os.path.isdir(path_accum):
            create_new_dir(path_accum)

def create_new_dir(newdir):
    #creates new directory (max depth of 1) creates an empty joblist and adds empty joblist to superior joblist
    if not(os.path.isdir(newdir)):
        os.mkdir(newdir)
        #create empty joblist
        new_joblist=os.path.join(newdir,settings.g_joblistfilename)
        open(new_joblist,"a").close()
        mother_joblist=os.path.join(newdir,"..",settings.g_joblistfilename)
        add_childjob_to_motherjob(new_joblist,mother_joblist)

def create_empty_generation(generation_name):
    #creates a new empty generation named <generation_name> and adds it to joblist
    abspath_to_generation=os.path.join(settings.get_run_dir(),settings.g_generation_dir,generation_name)
    create_new_path_in_project(abspath_to_generation)
    if False:
        os.makedirs(abspath_to_generation,exist_ok=True)
        generation_joblist=os.path.join(abspath_to_generation,settings.g_joblistfilename)
        #create empty joblist file
        open(generation_joblist,"a").close()
        #add generation joblist to main joblist
        add_childjob_to_motherjob(generation_joblist,settings.get_main_joblist_file())
        #add_generation_to_main_joblist(generation_joblist)

def get_parameters_to_set(coordinates):
    parameter_value_dict={}
    parameter_textfile=settings.get_param_file()
    with open(parameter_textfile,"r") as fil:
        for line in fil:
            if not line.startswith("#"):
                key,value=tuple(str.strip() for str in line.split("=",1))
                try:
                    parameter_value_dict[key]=float(eval(value))
                except:
                    raise Exception(f"could not evaluate to float expression: {value}")
    return parameter_value_dict
def get_latest_gen():
    #return tuple (name,nr) of last generation that has been created
    data_dir=settings.get_run_data_dir()
    generation_list_file=os.path.join(data_dir,settings.g_generation_list)
    if not os.path.isfile(generation_list_file):
        return None,-1
    else:
        with open(generation_list_file,"r") as fil:
            generation_list=[line.strip() for line in fil.readlines()]
        return generation_list,len(generation_list)-1#-1 because gen_nr starts at 0
def eval_generation(generation_name):
    print("todo, eval generation")
    return
def create_new_generation(population,gen_numbers,errors,new_gen_nr):
    new_pop_size=settings.g_pop_size[new_gen_nr]
    if population.shape[0]:
        new_population=algo.create_population_via_evolution(new_pop_size)
    else:
        #no savefile found, create starting population from scratch
        new_population=algo.create_starting_population(new_pop_size)

    new_generation_name=settings.get_generation_dirname(new_gen_nr)
    new_generation_path=os.path.join(settings.get_run_dir(),settings.g_generation_dir,new_generation_name)
    create_new_path_in_project(new_generation_path)

    for specimen_nr,specimen_coords in enumerate(new_population):
        create_calulation_dir(new_generation_path,specimen_nr,specimen_coords)
        

def create_calulation_dir(new_generation_path,specimen_nr,specimen_coords):
    calculation_dir=os.path.join(new_generation_path,settings.get_calculation_dirname(specimen_nr))
    create_new_path_in_project(calculation_dir)
    prepare_inputdir(calculation_dir,specimen_coords)
def read_current_state():
    current_savefile=get_current_savefile()
    population,gen_nr,errors=read_savefile(current_savefile)
    return population,gen_nr,errors
def read_savefile(current_savefile):
    #return old population, gen_nr and error read from savefile
    if current_savefile is None:
        #no savefile exists, arrays are empty
        population=np.zeros(shape=(0,settings.g_dimension))
        gen_nrs=np.zeros(shape=(0),dtype=np.uint)
        errors=np.zeros(shape=(0))
    else:
        #len=get_length_of_arrays(current_savefile)
        data=np.loadtxt(current_savefile)
        gen_nrs=np.uint(data[:,0])#first column
        errors=data[:,1]#second column
        population=data[:,2:]
        if population.shape[1] != settings.g_dimension:
            raise Exception(f"population data read from {os.path.abspath(current_savefile)} has wrong shape; expected {settings.g_dimension}; actual {population.shape[1]}")
    return population,gen_nrs,errors
def get_length_of_arrays(current_savefile):
    keys=("population","gen_nrs","errors")
    lengths_recorded=set()
    first_found=True
    with open(current_savefile,"r") as fil:
        total_line_nr=len(fil.readlines())
        for nr,line in enumerate(fil):
            if line.startswith(keys) or nr==total_line_nr-1:
                if first_found:
                    first_found=False
                else:
                    lengths_recorded.add(nr-start_nr-1)
                start_nr=nr
    if len(lengths_recorded) !=1:
        raise Exception(f"recorded several different arraylengths: {lengths_recorded}")
    else:
        return lengths_recorded.pop()


def get_current_savefile():
    dir_of_savefiles=os.path.join(settings.get_run_dir(),settings.g_run_data_dir,settings.g_save_dir)
    if not os.path.isdir(dir_of_savefiles):
        os.makedirs(dir_of_savefiles)
        return None
    else:
        list_of_savefiles=glob.glob(os.path.join(dir_of_savefiles,"*"))
        if not len(list_of_savefiles):
            return None
        basename_of_savefiles=[os.path.basename(file) for file in list_of_savefiles]
        basename_of_newest_savefile=basename_of_savefiles.sort(key=settings.get_savefile_number,reverse=True)[0]
        return os.path.join(dir_of_savefiles,basename_of_newest_savefile)

def add_childjob_to_motherjob(childfile,motherfile):
    child_dir=os.path.dirname(childfile)
    mother_dir=os.path.dirname(motherfile)
    mother_to_child=os.path.relpath(child_dir,mother_dir)
    child_to_mother=os.path.relpath(mother_dir,child_dir)
    with open(motherfile,"a") as fil:
        fil.write(f"cd {mother_to_child};")
        fil.write(f"serverJob --job {os.path.basename(childfile)};")
        fil.write(f"cd {child_to_mother}")
        fil.write("\n")

def add_generation_to_main_joblist(abspath_to_generation):
    with open(settings.get_main_joblist_file(),"r") as fil:
        linenumber=len(fil.readlines())

    with open(settings.get_main_joblist_file(),"a") as fil:
        if linenumber==0:
            pass
            #fil.write("start=$(pwd);")
        else:
            pass
            #fil.write("cd ${start}")
        fil.write(f"cd {abspath_to_generation};")
        fil.write("serverjob  --job")

def prepare_inputdir(input_dir,coordinates):
    parameter_values=get_parameters_to_set(coordinates)
    write_parameter_values(input_dir,parameter_values)
    copied_files=get_files(input_dir)
    set_values(input_dir,copied_files)
def write_parameter_values(input_dir,parameter_values):
    local_param_file=os.path.join(input_dir,settings.get_local_param_file())
    with open(local_param_file,"w") as fil:
        for key,value in parameter_values.items():
            fil.write(f"<{key}> {value}\n")

def set_values(input_dir,copied_files):
    local_param_file=os.path.join(input_dir,settings.get_local_param_file())
    with open(local_param_file) as fil:
        lines=fil.readlines()
    for line in lines:
        key=line.split()[0]
        value=float(line.split()[1])
        cmd=f"sed -i \"s/{key}/{value}/g\" "+" ".join(copied_files)
        #print(cmd)
        subprocess.run(cmd,shell=True)

def get_files(input_dir):
    start_dir=os.getcwd()
    os.chdir(input_dir)
    files_to_copy=glob.glob(os.path.join(settings.get_to_copy_dir(),"*"))
    for file in files_to_copy:
        try:
            shutil.copy(file,".")
        except FileExistsError:
            pass
        
    for file in glob.glob(os.path.join(settings.get_to_link_dir(),"*")):
        try:
            os.remove(os.path.basename(file))
        except FileExistsError:
            pass
        except OSError:
            pass
        os.symlink(file,os.path.basename(file))
    os.chdir(start_dir)
    #print(files_to_copy)
    return [os.path.basename(file) for file in files_to_copy]
