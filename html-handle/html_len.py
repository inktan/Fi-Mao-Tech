import os
import pandas as pd

html_paths = []
html_names = []
accepted_formats = (".html")

html_path_list =[
    r'Y:\GOA-AIGC\98-goaTrainingData\ArchOctopus',
    ]
for folder_path in html_path_list:
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(accepted_formats):
                file_path = os.path.join(root, file)
                html_paths.append(file_path)
                html_names.append(file)
                

print(html_paths)
print(len(html_paths))

# target_directory = r"Y:\GOA-AIGC\98-goaTrainingData\ArchOctopus"  # This is a placeholder path, you should replace it with the actual path
# directories_ending_with_20241012 = [
#     os.path.join(target_directory, d) for d in os.listdir(target_directory) 
#     if os.path.isdir(os.path.join(target_directory, d)) and d.endswith("20241012")
# ]
# print(directories_ending_with_20241012)

