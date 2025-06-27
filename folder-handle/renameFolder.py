import os

def rename_subfolders(parent_directory):
    if not os.path.isdir(parent_directory):
        print(f"Error: The directory '{parent_directory}' does not exist.")
        return

    print(f"Scanning directory: {parent_directory}")

    for item_name in os.listdir(parent_directory):
        item_path = os.path.join(parent_directory, item_name)

        if os.path.isdir(item_path):  # Check if it's a directory
            if '_' in item_name:
                try:
                    parts = item_name.split('_', 1) # Split only on the first underscore
                    if len(parts) == 2:
                        new_name = f"{parts[1]}_{parts[0]}"
                        new_item_path = os.path.join(parent_directory, new_name)

                        if os.path.exists(new_item_path):
                            print(f"Warning: New name '{new_name}' already exists. Skipping '{item_name}'.")
                        else:
                            os.rename(item_path, new_item_path)
                            print(f"Renamed '{item_name}' to '{new_name}'")
                    else:
                        print(f"Skipping '{item_name}': Does not contain exactly one underscore for splitting.")
                except Exception as e:
                    print(f"Error renaming '{item_name}': {e}")
            else:
                print(f"Skipping '{item_name}': No underscore found in name.")
        else:
            print(f"Skipping '{item_name}': Not a directory.")

# --- How to use the script ---
if __name__ == "__main__":
    folder_to_process = r'Y:\GOA-项目公示数据\公众号\好房档案'

    print(f"\nAttempting to process folders in: {folder_to_process}\n")
    rename_subfolders(folder_to_process)
    print("\nRenaming process complete.")