import sys
import os
import settings
import shutil
import glob
import subprocess

def create_new_path_in_project(new_path):
    #adds new folder to the project by creating all needed directories and adding entries to all jobfiles
    base_folder=settings.g_workspacefolder

    #check if desired path lies in workspacefolder
    common_path_to_ws=os.path.commonpath([base_folder,os.path.abspath(new_path)])
    if common_path_to_ws!=settings.g_workspacefolder:
        print("ERROR, can only create new path inside of project")
        raise ValueError

    relpath_from_ws=os.path.normpath(os.path.relpath(new_path,base_folder))
    path_accum=base_folder
    #loop over all dirs between target and base
    for dir in relpath_from_ws.split(os.sep):
        path_accum=os.path.join(path_accum,dir)
        #if a dir does not exist, create it and add to superior joblist
        if not os.path.isdir(path_accum):
            create_new_dir(path_accum)

def create_new_dir(newdir):
    if not(os.path.isdir(newdir)):
        os.mkdir(newdir)
        #create empty joblist
        new_joblist=os.path.join(newdir,settings.g_joblistfilename)
        open(new_joblist,"a").close()
        mother_joblist=os.path.join(newdir,"..",settings.g_joblistfilename)
        add_childjob_to_motherjob(new_joblist,mother_joblist)

def create_empty_generation(generation_name):
    abspath_to_generation=os.path.join(settings.get_calculationfolder(),generation_name)
    create_new_path_in_project(abspath_to_generation)
    if False:
        os.makedirs(abspath_to_generation,exist_ok=True)
        generation_joblist=os.path.join(abspath_to_generation,settings.g_joblistfilename)
        #create empty joblist file
        open(generation_joblist,"a").close()
        #add generation joblist to main joblist
        add_childjob_to_motherjob(generation_joblist,settings.get_main_joblist_file())
        #add_generation_to_main_joblist(generation_joblist)
#def

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

def prepare_inputdir(input_dir):
    copied_files=get_files(input_dir)
    set_values(input_dir,copied_files)

def set_values(input_dir,copied_files):
    with open(os.path.join(input_dir,"parameter_values.txt")) as fil:
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
            os.symlink(file,os.path.basename(file))
            #print(f"linking {file}")

        except FileExistsError:
            pass
        except OSError:
            pass
    os.chdir(start_dir)
    #print(files_to_copy)
    return [os.path.basename(file) for file in files_to_copy]
