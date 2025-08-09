import os
import sys
import shutil


#lembrar de colocar o kct da / logo no comeco da str
local_path = "/mnt/c/Users/Ângelo/Desktop/Database"
external_path = "/mnt/d/Database"


def compare(rel_path):

    local_tmp = os.path.join(local_path, rel_path)
    external_tmp = os.path.join(external_path, rel_path)
    try:
        #if it is a dir, we'll analyse all the files within it to get the most recent mtime
        time_local = get_mtime_dir(local_tmp) if os.path.isdir(local_tmp) else os.stat(local_tmp).st_mtime
        time_external = get_mtime_dir(external_tmp) if os.path.isdir(external_tmp) else os.stat(external_tmp).st_mtime
    except FileNotFoundError:
        print(f"Error: {local_tmp} or {external_tmp} does not exist in some location")
        sys.exit()

    if time_local < time_external:
        return external_tmp, local_tmp
    else:
        return local_tmp, external_tmp
    

def get_mtime_dir(path):
    '''
    This will not work in the following case:
    1.You create a folder.
    2.You add some files.
    3.You remove all the files, leaving it empty again.
    '''
    for dirpath, dirnames, filenames in os.walk(path):
        mtime = os.stat(path).st_mtime

        for dir in dirnames:
            dir_path = os.path.join(dirpath, dir)
            mtime = os.stat(dir_path).st_mtime if os.stat(dir_path).st_mtime > mtime else mtime
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            mtime = os.stat(file_path).st_mtime if os.stat(file_path).st_mtime > mtime else mtime

        return mtime


def update_dir(source, destiny):

    #creating lists with all files and dirs to create on the destiny
    add_files = [
        entity for entity in os.listdir(source) if entity not in os.listdir(destiny) and os.path.isfile(os.path.join(source, entity))
    ]
    delete_files = [
        entity for entity in os.listdir(destiny) if entity not in os.listdir(source) and os.path.isfile(os.path.join(destiny, entity))
    ]
    
    add_folders = [
        entity for entity in os.listdir(source) if entity not in os.listdir(destiny) and os.path.isdir(os.path.join(source, entity))
    ]
    delete_folders = [
        entity for entity in os.listdir(destiny) if entity not in os.listdir(source) and os.path.isdir(os.path.join(destiny, entity))
    ]

    for file in add_files:
        shutil.copy2(os.path.join(source,file), os.path.join(destiny, file)) #already copying the metadata
    for file in delete_files:
        os.remove(os.path.join(destiny, file))

    for dir in add_folders:
        os.mkdir(os.path.join(destiny, dir)) #we want to create step by step (the subfolders - if any- will be added later)
        shutil.copystat(os.path.join(source, dir), os.path.join(destiny, dir)) #copying the metadata (if no, mtime will be set to the current time)
    for dir in delete_folders: 
        shutil.rmtree(os.path.join(destiny, dir)) #but we want to delete everything at once

    
    print("-------------------------")
    print(f"Source folder: {source}")
    print(f"Destiny folder: {destiny}")
    print()
    print("Adding the following files:" if add_files else "")
    print(add_files if add_files else "")
    print("Deleting the following files:" if delete_files else "")
    print(delete_files if delete_files else "")
    print()
    print("Adding the following folders:" if add_folders else "")
    print(add_folders if add_folders else "")
    print("Deleting the following folders:" if delete_folders else "")
    print(delete_folders if delete_folders else "")
    print("-------------------------")
    


def update_file(source, destiny):

    os.remove(destiny)

    #copying file to the destiny's directory
    shutil.copy2(source, os.path.dirname(destiny))


def main():

    path = local_path
    for dirpath, dirnames, filenames in os.walk(path):
        print("=========================")
        print(f"Analysing {dirpath}")

        #Analysing the current dir (what is directly inside of it) - Here we will delete or add things
        #passing the path starting on the mother dir
        source, destiny = compare(os.path.relpath(dirpath, path))
        update_dir(source, destiny)

        # Update the dirnames list given by os.walk (only add new folders)
        current_subdirs = set(dirnames)  # dirs os.walk already knows about
        all_subdirs = {
            d for d in os.listdir(dirpath)
            if os.path.isdir(os.path.join(dirpath, d))
        }
        new_subdirs = all_subdirs - current_subdirs
        dirnames.extend(new_subdirs)  # only add new ones

        #Analysing the files inside of the current dir
        for filename in filenames:
            #passing the realtive path, same as above
            source, destiny = compare(os.path.relpath(os.path.join(dirpath, filename), path))
            update_file(source, destiny)


if __name__ == "__main__":
    print("Starting")
    print(f"{os.path.exists(local_path)} and {os.path.exists(external_path)}")
    main()
    print("finishing")