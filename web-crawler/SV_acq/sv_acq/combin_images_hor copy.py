import os
import shutil

# Define a function to print all the directory paths in a given directory
def print_directory_paths(directory):
    for item in os.listdir(directory):
        source_folder = os.path.join(directory, item)
        if os.path.isdir(source_folder):
            print(source_folder)
            files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
                    
            first_half, second_half = files[:4], files[4:8]

            destination_folder1 = source_folder.replace('sv_degree_960_720','sv_degree_2017')
            if not os.path.exists(destination_folder1):
                os.makedirs(destination_folder1)
            for file in first_half:
                shutil.copy(os.path.join(source_folder, file), destination_folder1)

            destination_folder2 = source_folder.replace('sv_degree_960_720','sv_degree_new')
            if not os.path.exists(destination_folder2):
                os.makedirs(destination_folder2)
            for file in second_half:
                shutil.copy(os.path.join(source_folder, file), destination_folder2)
        
print_directory_paths(r'E:\work\sv_levon\sv_degree_960_720')
