import os
from process_control.auxiliary import tryint
import sys
import auxiliary as aux
import re
g_joblistfilename="sens.list"
g_workspacedir=os.getcwd()
g_calculationdir="dummy_calc"
g_settings_file="settings.txt"
g_param_file="params.txt"
g_savedir="saves"
g_savebasename="save_"

g_data_dir=".opti"
if not os.path.isdir(g_data_dir):
    print(f"current directory needs to contain a {g_data_dir}-directory")
    print("make sure you are starting script in correct directory")

g_settings_to_read=["g_dimension","g_pop_size","g_calculationdir"]
g_dimension=0
g_pop_size=0
g_calculationdir="/"#dummy settings for lynter

def get_savefile_name(number):
    return f"{g_savebasename}_{number}.txt"
def get_savefile_number(savefile_name):
    tokens=re.split('([0-9]+)', savefile_name)#split filename in numreic and alphabetical chunks
    numeric_tokens=[aux.tryint(token) for token in tokens if type(aux.tryint(token))]
    if len(numeric_tokens) !=1:
        raise Exception(f"only one number is supposed to be in string: {savefile_name}")
    else:
        return numeric_tokens[0]
def get_dir_of_savefiles():
    return os.path.join(g_workspacedir,g_calculationdir,"g_savedir")
def get_local_param_file():
    return g_param_file
def get_calculationdir():
    return os.path.join(g_workspacedir,g_calculationdir)
def get_main_joblist_file():
    return os.path.join(g_workspacedir,g_joblistfilename)
def get_to_link_dir():
    return os.path.join(g_workspacedir,"param_files","to_copy")
def get_to_copy_dir():
    return os.path.join(g_workspacedir,"param_files","to_link")
def read_settings():
    modell_file=os.path.join(g_workspacedir,g_data_dir,"settings.txt")
    if not os.path.isfile(modell_file):
        print(f"ERROR: trying to read {modell_file} to read settings, could not find file")
        print("make sure you started script in right dir")
        raise Exception
    else:
        with open(modell_file,"r") as fil:
            for key in g_settings_to_read:
                for line in fil:
                    if line.startswith(key+"="):
                        try:
                            value=line.rsplit("=",1)[1].strip()
                            globals()[key]=eval(value)
                        except:
                            print(f"error evaluating \"{value}\"")
                            raise Exception

                        if key.endswith("dir"):
                            #interpret paths in settings.txt relative to given textfile
                            globals()[key]=os.path.abspath(os.path.join(modell_file,globals()[key]))
                        break
                else:#key in settings.txt nicht gefunden
                    print(f"einstellung {key} not found in {os.path.abspath(modell_file)}")
                    raise Exception
read_settings()

