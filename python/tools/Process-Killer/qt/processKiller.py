import os
import sys
import subprocess
import time
import signal


def list_processes(requested_process=None):
    """Return a list of all processes or a list of processes matching the requested process name"""
    all_processes = subprocess.check_output('tasklist /fo csv /nh', shell=True).decode().splitlines()

    process_list = []
    for process in all_processes:
        image_name, pid, *_ = process.split(',')
        if requested_process is None or requested_process.lower() in image_name.lower():
            process_list.append({'image_name': image_name, 'pid': pid})

    return process_list


def kill_processes(processes: list):
    """Kill a list of processes by pid"""
    for pid in processes:
        try:
            pid = int(pid)
        except (ValueError, TypeError):
            raise f"failed to make pid an integer | {type(pid)}: {pid}"

        try:
            os.kill(pid, signal.SIGTERM)
        except Exception:
            continue


def q_prompt(question: str):
    """Prompt the user with a yes/no question"""
    print()

    print(question + " (y/n)")
    user = input("> ").lower()

    if user == 'y':
        return True
    elif user == 'n':
        return False
    else:
        q_prompt(question)


def is_admin():
    """Return True if script is running as admin"""
    try:
        # assuming powershell is installed and set to PATH
        result = subprocess.check_output(['powershell', '-Command', '([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)'])
        return result.decode().strip() == 'True'
    except subprocess.CalledProcessError:
        return False


def close(exit_code: int=0):
    """Close the script"""
    print("Exiting...")
    sys.exit(exit_code)
