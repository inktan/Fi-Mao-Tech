file_path = r'd:\ProgramData\GitHub\RevitApi_\tools_2025\InfoStrucFormwork\merged_output.cs'
with open(file_path, 'r') as file:
    lines = file.readlines()
modified_lines = [line for line in lines if not line.strip().startswith('//')]
with open(file_path, 'w') as file:
    file.writelines(modified_lines)

