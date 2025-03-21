# This script is for intialization of all main folders in root directory

import os
import shutil


def is_folder_empty(folder_path):
    return not any(os.scandir(folder_path))  # Returns True if empty, False otherwise

                                                                           
dir_kat = os.path.join(os.getcwd(), 'Kategorie')
dir_vah = os.path.join(os.getcwd(), 'Vahy')
dir_los = os.path.join(os.getcwd(), 'Los')

needs_deletition = False
if not is_folder_empty(dir_kat):
    needs_deletition = True  
elif not is_folder_empty(dir_vah):
    needs_deletition = True  
elif not is_folder_empty(dir_los):
    needs_deletition = True  

if needs_deletition:
    print("Some folders are not empty, back up before deletition, than press enter...")
    input()

    shutil.rmtree(dir_kat, ignore_errors=True)
    shutil.rmtree(dir_vah, ignore_errors=True)
    shutil.rmtree(dir_los, ignore_errors=True)

    file_path = "./Vsichni.xlsx"
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)

if not (os.path.exists(dir_kat) or os.path.isdir(dir_kat)):
    os.mkdir(dir_kat)
if not (os.path.exists(dir_vah) or os.path.isdir(dir_vah)):
    os.mkdir(dir_vah)   
if not (os.path.exists(dir_los) or os.path.isdir(dir_los)):
    os.mkdir(dir_los)
