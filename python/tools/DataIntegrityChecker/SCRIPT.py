"""
Data Integrity Checker

This program provides tools to create and compare hash databases for the purpose of data integrity.

Dependencies:
- PyQt6.QtWidgets: For GUI file dialogs.
- os, sys, tempfile, hashlib, sqlite3, time, json: Standard Python libraries.
- typing: For type hints.
- multiprocessing.Pool: For parallel processing.

Functions:
- prompt_exit(): Exit the program with a prompt.
- ask_filelocation(filter, title='Select Hash Database'): Return the file path of the file selected.
- ask_directory(title='Select a Directory'): Return the directory path of the directory selected.
- ask_savefile(filter, title='Select a Save Location'): Return the file path of the file selected for saving.
- ask_save_summary_dialog(summary): Prompt user to save summary to a JSON file.
- save_json(summary, save_path): Save a summary to a JSON file.
- display_summary(summary): Display a summary of the comparison.
- is_database_valid(db_path): Check if the database is valid.
- create_hash(file_path): Create hash from file bytes using the chunk method.
- create_hash_db(hash_dir_path, db_save_path): Create a hash database from a directory path and save it.
- compare_databases(db1_path, db2_path): Compare two hash databases and return a summary of the differences.
- opt_1(): Create a hash database from a directory path and save it to a file path.
- opt_2(): Create and compare a temporary hash database to the selected hash database.
- opt_3(): Compare two hash databases.

Usage:
- Run this script to start the Data Integrity Checker application.
- Follow the on-screen prompts to create hash databases and compare them.
"""


import os
import sys
import tempfile
import hashlib
import sqlite3
import time
import json
from typing import Tuple
from multiprocessing import Pool
from PyQt6.QtWidgets import QApplication, QFileDialog


def prompt_exit() -> None:
    """Exit the program with a prompt."""
    input("\n\nPress ENTER to exit...")
    sys.exit()


def ask_filelocation(filter: str, title: str='Select Hash Database') -> str:
    """Return the file path of the file selected."""
    file_dialog = QFileDialog()
    file_dialog.setWindowTitle(title)
    file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
    file_dialog.setNameFilter(filter)

    if file_dialog.exec():
        return file_dialog.selectedFiles()[0]
    else:
        print('Canceled')
        prompt_exit()


def ask_directory(title: str='Select a Directory') -> str:
    """Return the directory path of the directory selected."""
    directory_dialog = QFileDialog()
    directory_dialog.setWindowTitle(title)
    directory_dialog.setFileMode(QFileDialog.FileMode.Directory)

    if directory_dialog.exec():
        return directory_dialog.selectedFiles()[0]
    else:
        print('Canceled')
        prompt_exit()


def ask_savefile(filter: str, title: str='Select a Save Location') -> str:
    """Return the file path of the file selected for saving."""
    file_dialog = QFileDialog()
    file_dialog.setWindowTitle(title)
    file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)  # Set the dialog mode to Save
    file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
    file_dialog.setNameFilter(filter)

    if file_dialog.exec():
        return file_dialog.selectedFiles()[0]
    else:
        print('Canceled')
        prompt_exit()


def ask_save_summary_dialog(summary: dict) -> None:
    print('\nSave summary to a json file? (y/n)')
    save_summary = input('Enter option: ')
    if save_summary.casefold() == 'y':
        print('Select a location to save the summary')
        summary_save_path = ask_savefile('JSON (*.json)')
        print(f'Selected Save Directory: {summary_save_path}')

        print('Saving Summary...')
        save_path = save_json(summary, summary_save_path)
        print(f"Summary saved to '{save_path}'")
    else:
        print('Canceled')
        prompt_exit()


def save_json(summary: dict, save_path: str) -> str:
    """Save a summary to a json file. Return the save path."""

    # change set to a list so that it can be serialized to json
    if not summary['common_files']:
        summary['common_files'] = []
    else:
        summary['common_files'] = list(summary['common_files'])
    if not summary['unique_files_db1']:
        summary['unique_files_db1'] = []
    else:
        summary['unique_files_db1'] = list(summary['unique_files_db1'])
    if not summary['unique_files_db2']:
        summary['unique_files_db2'] = []
    else:
        summary['unique_files_db2'] = list(summary['unique_files_db2'])
    if not summary['ok_files']:  # Already list
        summary['ok_files'] = []
    if not summary['bad_files']:  # Already list
        summary['bad_files'] = []
    if not summary['unknown']:  # Already list
        summary['unknown'] = []

    # create json format
    json_save = {
        'summary': {
            'number_common_files': summary['number_common_files'],
            'number_unique_files_db1': summary['number_unique_files_db1'],
            'number_unique_files_db2': summary['number_unique_files_db2'],
            'number_ok_files': summary['number_ok_files'],
            'number_bad_files': summary['number_bad_files'],
            'number_unknown_files': summary['number_unknown_files'],
            },
        'details': {
            'common_files': summary['common_files'],
            'unique_files_db1': summary['unique_files_db1'],
            'unique_files_db2': summary['unique_files_db2'],
            'ok_files': summary['ok_files'],
            'bad_files': summary['bad_files'],
            'unknown': summary['unknown'],
            }
        }
    
    # write summary to json file
    with open(save_path, 'w') as file:
        json.dump(json_save, file, indent=4)
    
    return save_path


def display_summary(summary: dict) -> None:
    """Display a summary of the comparison."""
    db1 = os.path.basename(summary['db1_path'])
    db2 = os.path.basename(summary['db2_path'])

    type_column = [
        "Type:",
        "Common Files",
        f"Unique Files in {db1}",
        f"Unique Files in {db2}",
        "Ok Files in Common",
        "Bad Files in Common",
        "Unknown Files in Common"
    ]
    number_column = [
        "Number:",
        str(summary['number_common_files']),
        str(summary['number_unique_files_db1']),
        str(summary['number_unique_files_db2']),
        str(summary['number_ok_files']),
        str(summary['number_bad_files']),
        str(summary['number_unknown_files'])
    ]

    type_column_width = max(len(type_item) for type_item in type_column)
    number_column_width = max(len(number_item) for number_item in number_column)
    total_length = type_column_width + 2 + number_column_width + 2  # 2 spaces between columns

    print(f"\n{'Summary':^{total_length}}")  # Centered
    print(f"{'-' * total_length}")

    for type_item, number_item in zip(type_column, number_column):  # Print columns side by side
        print(f"{type_item:<{type_column_width}}  {number_item}")


def is_database_valid(db_path: str) -> bool:
    """Check if the database is valid. Return True if valid, False if not."""
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM hashes')
        cursor.execute('SELECT working_directory FROM attributes')
        connection.close()
        return True
    except BaseException as error:
        print(f"Invalid database! | {error}")
        return False


def create_hash(file_path: str) -> Tuple[str, str]:
    """Create hash from file bytes using the chunk method, return hash as a string if found."""
    try:
        chunk_size = 4096
        file_size = os.path.getsize(file_path)

        if file_size > 1_000_000_000:  # If file size around 1 Gb or larger
            chunk_size = 8192

        hasher = hashlib.sha256()

        with open(file_path, 'rb') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)

        file_hash = hasher.hexdigest()
        return file_path, file_hash
    except BaseException as error:
        print(f"Failed to create hash! | {error}")
        return file_path, '?'


def create_hash_db(hash_dir_path: str, db_save_path: str) -> int:
    """Create a hash database from a directory path and save it to a file path. Return the file path and number of files hashed."""
    if os.path.exists(db_save_path):
        print(f"\nHash database already exists at '{db_save_path}'\nDelete it? (y/n)\n")
        delete_database = input('Enter option: ')
        if delete_database.casefold() == 'y':
            os.remove(db_save_path)
        else:
            print('Canceled')
            prompt_exit()

    connection = sqlite3.connect(db_save_path)
    cursor = connection.cursor()

    # Create table for hashes
    cursor.execute('''CREATE TABLE IF NOT EXISTS hashes (
                        file_path TEXT PRIMARY KEY,
                        calculated_hash TEXT
                    )''')
    # create attribute table
    cursor.execute('''CREATE TABLE IF NOT EXISTS attributes (
                        working_directory TEXT PRIMARY KEY
                    )''')
    # Insert working directory into the table
    cursor.execute('INSERT OR REPLACE INTO attributes (working_directory) VALUES (?)', (hash_dir_path,))

    # Batch size for parameterized queries
    max_time_per_batch = 3  # seconds
    batch_data = []

    print('\nCreating Hashes...\n')

    # Create a pool, default number of processes is the number of cores on the machine
    with Pool() as pool:
        start_time = time.time()  # Start timer
        for root, _, files in os.walk(hash_dir_path):
            file_paths = [os.path.join(root, file) for file in files]
            results = pool.map(create_hash, file_paths)  # Use workers to create hashes
            batch_data.extend(results)

            elapsed_time = time.time() - start_time
            if elapsed_time >= max_time_per_batch and batch_data:  # If the max time per batch has been reached and there are files to be inserted
                cursor.executemany('INSERT OR REPLACE INTO hashes (file_path, calculated_hash) VALUES (?, ?)', batch_data)
                print(f"Processed {len(batch_data)} files")
                batch_data = []
                start_time = time.time()

        if batch_data:  # If there are any remaining files to be inserted
            cursor.executemany('INSERT OR REPLACE INTO hashes (file_path, calculated_hash) VALUES (?, ?)', batch_data)
            print(f"Processed {len(batch_data)} files")

    sys.stdout.flush()
    connection.commit()
    connection.close()

    connection = sqlite3.connect(db_save_path)
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM hashes')
    num_files = cursor.fetchone()[0]
    connection.close()

    return db_save_path, num_files


def compare_databases(db1_path: str, db2_path: str) -> dict:
    """Compare two hash databases and return a summary of the differences."""
    connection1 = sqlite3.connect(db1_path)
    cursor1 = connection1.cursor()

    connection2 = sqlite3.connect(db2_path)
    cursor2 = connection2.cursor()

    cursor1.execute('SELECT file_path, calculated_hash FROM hashes')
    db1_files = {row[0]: row[1] for row in cursor1.fetchall()}

    cursor2.execute('SELECT file_path, calculated_hash FROM hashes')
    db2_files = {row[0]: row[1] for row in cursor2.fetchall()}

    print('\nScanning Databases...\n')
    print(f"Common files...")
    common_files = set(db1_files.keys()) & set(db2_files.keys())
    print('Unique files in the first database...')
    unique_files_db1 = set(db1_files.keys()) - set(db2_files.keys())
    print('Unique files in the second database...')
    unique_files_db2 = set(db2_files.keys()) - set(db1_files.keys())

    print('Comparing hashes...')
    ok_files = [(file_path, db1_files[file_path]) for file_path in common_files if db1_files[file_path] == db2_files[file_path]]
    bad_files = [(file_path, db1_files[file_path], db2_files[file_path]) for file_path in common_files if db1_files[file_path] != db2_files[file_path]]
    unknown = [file_path for file_path in common_files if db1_files[file_path] == '?' or db2_files[file_path] == '?']

    sys.stdout.flush()
    connection1.close()
    connection2.close()

    summary = {
        'db1_path': db1_path,
        'db2_path': db2_path,

        'number_common_files': len(common_files),
        'number_unique_files_db1': len(unique_files_db1),
        'number_unique_files_db2': len(unique_files_db2),
        'number_ok_files': len(ok_files),
        'number_bad_files': len(bad_files),
        'number_unknown_files': len(unknown),
        'common_files': common_files,
        'unique_files_db1': unique_files_db1,
        'unique_files_db2': unique_files_db2,
        'ok_files': ok_files,
        'bad_files': bad_files,
        'unknown': unknown,
    }

    return summary


def opt_1():
    """Create a hash database from a directory path and save it to a file path."""
    print('Select directory to start creating a hash database')
    directory_path = ask_directory('Select a Start Directory')
    print(f'Selected hash directory: {directory_path}')

    print('Select a location to store the hash database')
    db_save_path = ask_savefile('SQLite3 (*.sqlite3)')
    print(f'Selected Save Path: {db_save_path}')

    save_path, number_files = create_hash_db(directory_path, db_save_path)

    print(f"DONE!\n{number_files} Files Hashed\nHash database saved to '{save_path}'")


def opt_2():
    """Create and compare a temporary hash database to the selected hash database."""
    print('Select Hash Database')
    selected_db_path = ask_filelocation('SQLite3 (*.sqlite3)')
    print(f'Selected Hash Database: {selected_db_path}')

    if not is_database_valid(selected_db_path):
        print('Invalid File Detected')
        prompt_exit()
    
    connection = sqlite3.connect(selected_db_path)
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM hashes')
    num_files = cursor.fetchone()[0]
    cursor.execute('SELECT working_directory FROM attributes')
    working_directory = cursor.fetchone()[0]
    connection.close()

    with tempfile.TemporaryDirectory() as temp_dir_path:
        print()
        print(f"Temporary Directory Created: '{temp_dir_path}'")
        print(f"Hashing From: '{working_directory}'")
        temp_db = os.path.join(temp_dir_path, f'temp-db.sqlite3')
        print(f"Temporary DB: '{temp_db}'")

        database_path, _ = create_hash_db(working_directory, temp_db)
        summary = compare_databases(selected_db_path, database_path)

    display_summary(summary)
    ask_save_summary_dialog(summary)


def opt_3():
    """Compare two hash databases."""
    print('Select First Hash Database')
    db1_path = ask_filelocation(title='Select First Hash Database', filter='SQLite3 (*.sqlite3)')
    print(f'First Hash Database: {db1_path}')

    print('Select Second Hash Database')
    db2_path = ask_filelocation(title='Select Second Hash Database', filter='SQLite3 (*.sqlite3)')
    print(f'Second Hash Database: {db2_path}')

    if not is_database_valid(db1_path) and is_database_valid(db2_path):
        print('Invalid File Detected')
        prompt_exit()

    summary = compare_databases(db1_path, db2_path)
    display_summary(summary)
    ask_save_summary_dialog(summary)


if __name__ == '__main__':
    app = QApplication([])

    print("""
        Data Integrity Checker
        ----------------------
        For improved processing speed, turn off real-time protection in your antivirus software.

        Options:
        1. Create Hash Database
            - Create a hash database from a directory
        2. Check Data Integrity
            - Automatically creates a temporary database to compare it against the selected hash database.
              Temporary database is created based on what directory was selected to create the hash database.
        3. Compare Databases
            - Compare two hash databases
    """)

    main_option_selected = input('Enter option: ')

    if main_option_selected == '1':
        opt_1()
    elif main_option_selected == '2':
        opt_2()
    elif main_option_selected == '3':
        opt_3()
    else:
        print('Invalid Option Selected')
    
    prompt_exit()
