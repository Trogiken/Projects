"""Sort dir files by extension into folders"""
import os
import sys
from tkinter import filedialog


def intense_gather_files(directory: str) -> dict:
    """Gather and sort files by extension, including subdirectories"""
    gathered_data = {}

    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist")
        return gathered_data
    if not os.path.isdir(directory):
        print(f"'{directory}' is not a directory")
        return gathered_data

    for root, _, files in os.walk(directory):
        for file in files:
            _, extension = os.path.splitext(file)  # Get file extension (filename.pdf.txt -> .txt)
            extension = extension[1:]  # Remove '.' from extension

            if not extension:  # If file has no extension
                extension = 'NOEXTENSION'
            if extension not in gathered_data:
                gathered_data[extension] = []
            file_path = os.path.join(root, file)
            gathered_data[extension].append((file, file_path))  # Append tuple of filename and path (filename, path)

    return gathered_data


def normal_gather_files(directory: str) -> dict:
    """Gather and sort file by extension"""
    gathered_data = {}

    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist")
        return gathered_data
    if not os.path.isdir(directory):
        print(f"'{directory}' is not a directory")
        return gathered_data
    files_in_directory = [file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))]  # List of only files in directory
    if ( len(files_in_directory) == 1 and os.path.basename(__file__) in os.listdir(directory) ) or ( not len(files_in_directory) ):  # If only file in directory is this script or no FILES in directory
        print(f"No files in '{directory}' to sort")
        return gathered_data

    for file in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, file)):  # Don't continue if file is directory
            continue

        _, extension = os.path.splitext(file)  # Get last file extension (filename.pdf.txt -> .txt)
        extension = extension[1:]  # Remove '.' from extension

        if not extension:  # If file has no extension
            extension = 'NOEXTENSION'
        if not extension in gathered_data:
            gathered_data.update({extension: []})
        gathered_data[extension].append((file, os.path.join(directory, file)))  # Append tuple of filename and path (filename, path)
    
    return gathered_data


def move_file(source, destination):
    """
    Move the file to the destination path
    If destination path already exists, rename the file with index
    """
    if os.path.exists(destination):
        file_name, file_extension = os.path.splitext(os.path.basename(source))  # get filename and extension
        index = 1
        while True:
            new_file_name = f"{file_name}_{index}{file_extension}"  # new filename with index
            new_destination = os.path.join(os.path.dirname(destination), new_file_name)  # new destination using new filename
            if not os.path.exists(new_destination):  # if new destination doesn't exist, move file
                os.rename(source, new_destination)
                break
            index += 1
    else:  # if destination doesn't exist, move file
        os.rename(source, destination)


if __name__ == '__main__':
    print("""
    ____  _                __                      _____            __           
   / __ \(_)_______  _____/ /_____  _______  __   / ___/____  _____/ /____  _____
  / / / / / ___/ _ \/ ___/ __/ __ \/ ___/ / / /   \__ \/ __ \/ ___/ __/ _ \/ ___/
 / /_/ / / /  /  __/ /__/ /_/ /_/ / /  / /_/ /   ___/ / /_/ / /  / /_/  __/ /    
/_____/_/_/   \___/\___/\__/\____/_/   \__, /   /____/\____/_/   \__/\___/_/     
                                      /____/                                     
    """)
    input('\nPress ENTER to continue...\n')

    # choose between normal and intense gathering
    print("Choose gathering method:")
    print("1. Normal - Scan and sort selected directory")
    print("2. Intense - Scan and sort selected directory and subdirectories")
    while True:
        method = input("Method: ")
        if method == '1':
            gather_files = normal_gather_files
            break
        elif method == '2':
            gather_files = intense_gather_files
            break
        else:
            print("Invalid input")
            continue
    
    # Choose directory to sort
    gather_dir = filedialog.askdirectory(title="Select directory to sort")
    save_directory = gather_dir
    if not gather_dir:
        print("No directory selected")
        sys.exit()

    # Display settings
    print()
    if gather_files == normal_gather_files:
        print("Normal mode selected")
    elif gather_files == intense_gather_files:
        print("Intense mode selected")
    print(f'Gather Directory: {gather_dir}')
    print(f'Save Directory: {save_directory}')

    # Ask to change save directory
    change_save = input('Change save directory? y/n: ')
    if change_save.lower() == 'y':
        save_directory = filedialog.askdirectory(title="Select directory to save sorted files")
        if not save_directory:
            print("No directory selected")
            sys.exit()
        print(f'New Save Directory: {save_directory}')
    elif change_save.lower() == 'n':
        pass
    else:
        print("Invalid input")
        sys.exit()
    
    input('\nPress ENTER to continue...\n')
    
    # Sort files
    print(f"Gathering files in '{gather_dir}'...\n")
    data = gather_files(gather_dir)
    for extension in data.keys():
        header = f"[{extension}'s]"
        print(header)
        print('-' * len(header))
        for filename, filepath in data.get(extension):  # for file (filename.extension, filename path)
            if not filename == os.path.basename(__file__):  # if current file is not main script
                extension_folder = os.path.join(save_directory, extension)
                if not os.path.exists(extension_folder):  # Don't create folder if it already exists
                    os.makedirs(extension_folder)
                move_file(filepath, os.path.join(extension_folder, filename))
            print(f"{filename} : {filepath}")
        print()
