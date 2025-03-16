import google_auth_oauthlib.flow
import google.oauth2.credentials
import requests
from tkinter import filedialog
from os import path


def get_credentials() -> google.oauth2.credentials.Credentials or bool:
    """Performs OAuth2 authorization and returns credentials"""
    print("Select the 'client_secrets.json' file")
    file_path = filedialog.askopenfilename()

    if not path.exists(file_path):
        print("File not found!")
        return False

    try:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file=file_path,
            scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]
        )
        credentials = flow.run_local_server(port=8080)
        return credentials
    except BaseException as err:
        print(f"\nError getting credentials:\n{err}")
        return False


def post_request(url, request_body, access_token) -> requests.Response or bool:
    """Sends a POST request to the YouTube Data API"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(
            url=url,
            json=request_body,
            headers=headers
        )
        return response
    except BaseException as err:
        print(f"\nError sending request:\n{err}")
        return False