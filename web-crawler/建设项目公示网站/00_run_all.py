import os
import subprocess

def find_and_run_py_files(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py") and file.startswith("get_") :
                py_file_path = os.path.join(root, file)
                print(f"Running: {py_file_path}")
                try:
                    subprocess.run(["python", py_file_path], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error running {py_file_path}: {e}")

# 示例：在当前目录及其子目录中查找并运行所有 .py 文件
find_and_run_py_files(r"Y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\github\Fi-Mao-Tech\web-crawler\建设项目公示网站")

py_file_path = r'Y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\github\Fi-Mao-Tech\web-crawler\建设项目公示网站\01_del_empty_folder.py'
subprocess.run(["python", py_file_path], check=True)

py_file_path = r'Y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\github\Fi-Mao-Tech\web-crawler\建设项目公示网站\02_move_folder_hz.py'
subprocess.run(["python", py_file_path], check=True)

py_file_path = r'Y:\GOA-AIGC\98-goaTrainingData\ArchOctopus\github\Fi-Mao-Tech\web-crawler\建设项目公示网站\02_move_folder_sh.py'
subprocess.run(["python", py_file_path], check=True)


