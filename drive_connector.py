import os
import json

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def connect_drive():
    creds = None

    if os.path.exists("drive_token.json"):
        creds = Credentials.from_authorized_user_file("drive_token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("drive_token.json", "w") as token:
            token.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def get_drive_files(service):
    results = service.files().list(
        pageSize=20,
        fields="files(id, name, mimeType, modifiedTime)"
    ).execute()

    return results.get("files", [])


if __name__ == "__main__":
    service = connect_drive()

    files = get_drive_files(service)

    output = {
        "connector": "Google Drive",
        "status": "success",
        "files": files
    }

    with open("drive_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("Drive connector test completed!")
    print(f"Files found: {len(files)}")