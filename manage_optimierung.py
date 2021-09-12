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
def get_all_gens():
    dir_of_generations=os.path.join(settings.get_run_dir(),settings.g_generation_dir)
    generation_dirs=glob.glob(os.path.join(dir_of_generations,settings.g_generaton_basename+"*"))
    generation_dir_names=[os.path.basename(dir) for dir in generation_dirs]
    generation_dir_names.sort(key=settings.get_only_number_of_string)
    return generation_dir_names

    #return tuple (name,nr) of last generation that has been created
    generation_list_file=settings.get_generation_listfile()
    if not os.path.isfile(generation_list_file):
        return None,0
    else:
        with open(generation_list_file,"r") as fil:
            generation_list=[line.strip() for line in fil.readlines()]
        return generation_list,len(generation_list)

def create_new_generation(population,gen_numbers,errors,new_gen_nr):
    new_pop_size=settings.g_pop_size[new_gen_nr]
    if population.shape[0]:
        new_population=algo.create_population_via_evolution(population,errors,new_pop_size,new_gen_nr)
    else:
        #no savefile found, create starting population from scratch
        new_population=algo.create_starting_population(new_pop_size)

    new_generation_path=settings.get_generation_path(new_gen_nr)
    create_new_path_in_project(new_generation_path)
    add_generation_to_list(new_generation_path)
    write_population(new_generation_path,new_population)

    for specimen_nr,specimen_coords in enumerate(new_population):
        print(f"creating specimen {specimen_nr} of generation {new_gen_nr}")
        create_calulation_dir(new_generation_path,specimen_nr,specimen_coords)

    save_current_state(population,errors,gen_numbers)
    return new_generation_path
    
def add_generation_to_list(new_generation_path):
    generation_name=os.path.basename(new_generation_path)
    generation_listfile=settings.get_generation_listfile()
    with open(generation_listfile,"a") as fil:
        fil.write(generation_name+"\n")
    return
def run_generation(generation_dir):
    jobfile_name=settings.g_joblistfilename
    cmd=f"serverJob --job {jobfile_name}"
    if settings.g_debug:
        print(f"would be executing \"{cmd}\" in {generation_dir}")
    else:
        subprocess.run(cmd,cwd=generation_dir)
def eval_generation(generation_nr):
    path_to_generation=settings.get_generation_path(generation_nr)
    population_to_add=read_population(path_to_generation)
    gen_nr_to_add=np.ones(population_to_add.shape[0],dtype=np.uint)
    if not settings.g_debug:
        download_results(path_to_generation)
    errors_to_add=np.zeros(population_to_add.shape[0])
    get_errors_of_population(path_to_generation,errors_to_add)
    return population_to_add,gen_nr_to_add,errors_to_add
def write_local_serverjobfile(path_to_calculation_dir):
    serverjob_file=os.path.join(path_to_calculation_dir,settings.g_joblistfilename)
    submit_cmd=add_jobdir_to_serverjob(settings.g_submit_cmd,path_to_calculation_dir)
    with open(serverjob_file,"w") as fil:
        fil.write(submit_cmd)

def add_jobdir_to_serverjob(submit_cmd,path_to_calculation_dir):
    relpath_from_rundir=os.path.relpath(path_to_calculation_dir,settings.g_run_dir)
    return submit_cmd+f" --jobDir {relpath_from_rundir}"
    
def get_errors_of_population(path_to_generation,errors_to_add):
    #errors_to_add=preallocated np.ndarray, of shape(n_calc,) to be filled by this function
    calculation_dirs=glob.glob(os.path.join(path_to_generation,settings.g_calculation_basename+"*"))
    get_gen_nr=lambda gen_dir: settings.get_only_number_of_string(os.path.basename(gen_dir))
    calculation_dirs.sort(key=get_gen_nr)
    for dir_nr,dir in enumerate(calculation_dirs):
        errors_to_add[dir_nr]=get_error_of_calculation(dir)
    

def get_error_of_calculation(calculation_dir):
    error_key="error="
    if settings.g_debug:
        error=np.random.uniform(0,1)#random error between 0 and 1
        
    else:
        executable=settings.g_post_cmd#"/home/markus/ParaView-5.9.0-MPI-Linux-Python3.8-64bit/python_scripts/auswerte_scripte/show_qs.py"
        complete_proc=subprocess.run(executable,cwd=calculation_dir,capture_output=True)#popen benutzen und err_ges printen
        output_lines=complete_proc.stdout.decode("ascii").splitlines()
        for line in output_lines:
            if line.startswith[error_key]:
                error=float(line.rsplit("=",1)[1])
                break
        else:
            raise ValueError(f"post-programm did not print error_message: {error_key}")
    print(f"evaluated {calculation_dir} to have error: {error}")
    return error
def download_results(path_to_generation):
    cmd=f"serverJob --job {settings.g_joblistfilename} --download"
    subprocess.run(cmd,path_to_generation)

def write_population(new_generation_path,population):
    population_file=os.path.join(new_generation_path,settings.g_local_pop_file)
    np.savetxt(population_file,population)

def read_population(new_generation_path):
    population_file=os.path.join(new_generation_path,settings.g_local_pop_file)
    population=np.loadtxt(population_file)
    return population

def create_calulation_dir(new_generation_path,specimen_nr,specimen_coords):
    calculation_dir=os.path.join(new_generation_path,settings.get_calculation_dirname(specimen_nr))
    create_new_path_in_project(calculation_dir)
    prepare_inputdir(calculation_dir,specimen_coords)

def save_current_state(population,errors,gen_numbers):
    if population.shape[0]==0:
        return
    latest_savefile=get_current_savefile()
    if latest_savefile is None:
        latest_number=0
    else:
        latest_number=settings.get_savefile_number(os.path.basename(latest_savefile))
    new_savefile_name=settings.get_savefile_name(latest_number+1)
    path_to_new_savefile=os.path.join(settings.get_savefile_dir(),new_savefile_name)
    write_savefile(path_to_new_savefile,population,errors,gen_numbers)
    pass

def read_current_state():
    current_savefile=get_current_savefile()
    population,gen_nr,errors=read_savefile(current_savefile)
    return population,gen_nr,errors


def write_savefile(path_to_new_savefile,population,errors,gen_numbers):
    errors2d=errors.reshape((errors.shape[0],1))
    gen_numbers2d=gen_numbers.reshape((gen_numbers.shape[0],1))
    data=np.concatenate((population,errors2d,gen_numbers2d),axis=1)
    np.savetxt(path_to_new_savefile,data)
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
        gen_nrs=np.uint(data[:,-2],dtype=np.uint)#first column
        errors=data[:,-1]#second column
        population=data[:,0:-2]
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
    #returns abspath to latest savefile
    dir_of_savefiles=settings.get_savefile_dir()
    if not os.path.isdir(dir_of_savefiles):
        os.makedirs(dir_of_savefiles)
        return None
    else:
        list_of_savefiles=glob.glob(os.path.join(dir_of_savefiles,"*"))
        if not len(list_of_savefiles):
            return None
        basename_of_savefiles=[os.path.basename(file) for file in list_of_savefiles]
        basename_of_savefiles.sort(key=settings.get_savefile_number,reverse=True)
        basename_of_newest_savefile=basename_of_savefiles[0]
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
    write_local_serverjobfile(input_dir)
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
        subprocess.run(cmd,cwd=input_dir,shell=True)

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
