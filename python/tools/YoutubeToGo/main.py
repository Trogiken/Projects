"""
This program is a tool to reinstate subscriptions and playlists after switching accounts or bans.

------------------------------------------------

Prerequisites:
1. Download your data from takeout.google.com (If you've been banned already, there will be no data to download):
    * Go to https://takeout.google.com/settings/takeout
    * Deselect all and select only "YouTube and YouTube Music"
    * Select "All YouTube data included"
    * Select "Multiple formats" and "CSV"
    * Click on "Next step" and then "Create export"
    * Wait for the export to finish and download the file.

2. Create a Project and Enable the YouTube Data API:
    * Go to the https://console.developers.google.com.
    * Create a new project or select an existing one.
    * Select Enable APIs and services and search for "YouTube Data API"
    * Enable it for your project.

3. Obtain API Credentials:
    * Click on "Credentials" in the left-hand menu.
    * Click on the "Create Credentials" button and select "OAuth client ID."
    * Select External and click on the "Create" button.
    * Fill out the form with information (can be anything)
    * Save and Continue
    * Enable all scopes related to the YouTube Data API
    * Finish the setup
    * Publish the app
    * Go back to the Credentials page and create a new OAuth client ID as a Desktop app.
    * Download the JSON file.
"""

import source.subscribe as subs
import source.playlist as plst
import source.api as api
from source.misc import incomplete_function


def paused_exit(code=0):
    """Exits the program after user input"""
    input("\nPress Enter to exit")
    exit(code)


def option_prompt():
    """Prints the options and asks for input"""
    print(
        "\nOptions:\n"
        "1. Subscribe to Channels\n"
        "2. Create Playlists\n"
        "0. Exit"
    )
    while True:
        answer = input("Enter option number: ")
        if answer == "1":
            return 1
        elif answer == "2":
            return 2
        elif answer == "0":
            return 0
        else:
            print("Invalid input. Try again.")


def subscribe_mode():
    """Subscribe to channels logic"""
    channel_data = subs.get_file_data()
    if not channel_data:
        paused_exit(1)
    credentials = api.get_credentials()
    if not credentials:
        paused_exit(1)
    
    if subs.subscribe_prompt(channel_data):
        subs.subscribe_to_channels(channel_data, credentials)


def playlist_mode():
    """Create playlists logic"""
    playlist_data = plst.combine_playlists()
    if not playlist_data:
        paused_exit(1)
    credentials = api.get_credentials()
    if not credentials:
        paused_exit(1)
    
    if plst.playlist_prompt(playlist_data):
        plst.create_playlists(playlist_data, credentials)


if __name__ == "__main__":
    option = option_prompt()
    if option == 0:
        exit()
    elif option == 1:
        subscribe_mode()
    elif option == 2:
        playlist_mode()
    else:
        raise Exception("Error getting option")

    paused_exit()
