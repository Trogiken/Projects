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


def main():
    if not is_admin():  # check if script is running as admin
        input("You must run this script as an administrator\n[Press ENTER to exit]")
        close(1)

    while True:
        os.system('cls')  # clear terminal

        user_query = input("Enter a process name (leave blank to list all processes)\n[0 to Exit]> ")
        if user_query == '0':
            close(0)

        print()

        # list processes
        print("Searching for processes...")
        listed_processes = list_processes(user_query)
        if listed_processes:  # check if any processes were found
            for prs in listed_processes:
                print(f'{prs["image_name"]}: {prs["pid"]}')
        else:
            reload = q_prompt('No processes found - Try Again?')
            if reload:
                continue
            else:
                close(0)

        # ask before killing
        user_verify = q_prompt('[WARNING] Kill the following processes?')
        if user_verify:
            os.system('cls')
            print('Killing processes...')
            pid_kill_list = [process['pid'] for process in listed_processes]  # extract pid's from processes
            kill_processes([pid.strip('"') for pid in pid_kill_list])  # pass pid's with internal double quotes removed
            time.sleep(3)  # delay for processes to clean up
        else:
            continue

        # query again and examine if there are process left
        new_query = list_processes(user_query)
        if new_query:
            print(f'Failed to kill the following processes:')
            for prs in new_query:
                print(f'{prs["image_name"]}: {prs["pid"]}')
        else:
            print(f'Successfully killed all {len(listed_processes)} processes')

        print()

        restart = q_prompt('Kill more processes?')
        if restart:
            continue
        else:
            close(0)


if __name__ == "__main__":
    main()
