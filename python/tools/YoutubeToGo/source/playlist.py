"""
This script reads playlist csv files from takeout.google.com and 
inserts them into the new account
"""

import csv
import source.api as api
from tkinter import filedialog
from os import path


def combine_playlists() -> list or bool:
    """Asks for playlist csv file(s) and returns processed data"""
    print("Select the playlist csv file(s)")
    file_paths = filedialog.askopenfilename(multiple=True)
    
    csv_data = []
    for file_path in file_paths:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            try:
                csvreader = csv.reader(csvfile)
            except csv.Error:
                print("Error reading file!")
                return False
            
            playlist_table = []
            video_table = []

            current_table = None
            for row in csvreader:
                if not any(row):
                    continue  # Skip empty rows

                # Check if the row represents the start of a table
                if row[0] == "Playlist Id":
                    current_table = "playlist"
                    continue
                elif row[0] == "Video Id":
                    current_table = "video"
                    continue

                if current_table == "playlist":
                    playlist_table.append(row)
                elif current_table == "video":
                    video_table.append(row)
                
            csv_data.append({
                "title": path.basename(file_path).split(".")[0],
                "description": playlist_table[0][4],
                "visibility": playlist_table[0][5].casefold(),
                "video_ids": [row[0] for row in video_table]
            })
    
    return csv_data


def playlist_prompt(playlist_data) -> bool:
    """Prints the playlist names and asks for confirmation"""
    print() # newline
    for playlist in playlist_data:
        print(f"{playlist['title']} ({len(playlist['video_ids'])} Videos)")
    print(f"\nCreate {len(playlist_data)} playlists?")

    while True:
        answer = input("Y/N: ").lower()
        if answer == "y":
            return True
        elif answer == "n":
            return False
        else:
            print("Invalid input. Try again.")


def create_playlist(title, description, visability, access_token) -> str or None:
    """Creates a playlist with the given title"""
    url = "https://youtube.googleapis.com/youtube/v3/playlists?part=snippet,status"
    request_body = {
        "snippet": {
            "title": title,
            "description": description
        },
        "status": {
            "privacyStatus": visability
        }
    }
    response = api.post_request(url, request_body, access_token)
    if not response:
        return None
    if not response.ok:
        print(f"Error creating playlist '{title}':\n{response.json()['error']['errors']}\n")
        return None
    
    playlist_id = response.json()["id"]
    print(f"\nCreated playlist '{title}' ({playlist_id})\n")

    return playlist_id

def add_videos_to_playlist(playlist_id, video_ids, access_token) -> bool:
    """Adds videos to a playlist, skipping duplicates"""
    url = "https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet"
    for video_id in video_ids:
        request_body = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
        response = api.post_request(url, request_body, access_token)
        if not response:
            return False
        if not response.ok:
            print(f"\nError adding video '{video_id}' to playlist\n{response.json()['error']['errors']}\n")
            continue
        print(f"Added video '{video_id}' to playlist")

    return True

def create_playlists(playlist_data, credentials) -> None:
    """Creates playlists and adds videos to them"""
    access_token = credentials.token
    for playlist in playlist_data:
        title = playlist["title"]
        description = playlist["description"]
        visibility = playlist["visibility"]
        playlist_id = create_playlist(title, description, visibility, access_token)
        if playlist_id:
            video_ids = playlist["video_ids"]
            add_videos_to_playlist(playlist_id, video_ids, access_token)
