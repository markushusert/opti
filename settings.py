import os
import sys
g_joblistfilename="sens.list"
g_workspacefolder=os.getcwd()
g_calculationfolder_rel="dummy_calc"

def get_calculationfolder():
    return os.path.join(g_workspacefolder,g_calculationfolder_rel)
def get_main_joblist_file():
    return os.path.join(g_workspacefolder,g_joblistfilename)
def get_to_link_dir():
    return os.path.join(g_workspacefolder,"param_files","to_copy")
def get_to_copy_dir():
    return os.path.join(g_workspacefolder,"param_files","to_link")

