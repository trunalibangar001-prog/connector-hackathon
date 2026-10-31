import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def connect_gmail():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def get_emails(service):
    results = service.users().messages().list(
        userId="me",
        maxResults=10
    ).execute()

    messages = results.get("messages", [])

    emails = []

    for message in messages:
        email = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()

        headers = email["payload"].get("headers", [])

        data = {
            "id": message["id"],
            "from": "",
            "subject": "",
            "date": ""
        }

        for header in headers:
            if header["name"] == "From":
                data["from"] = header["value"]
            elif header["name"] == "Subject":
                data["subject"] = header["value"]
            elif header["name"] == "Date":
                data["date"] = header["value"]

        emails.append(data)

    return emails


if __name__ == "__main__":
    service = connect_gmail()
    emails = get_emails(service)

    print(json.dumps(emails, indent=2))

    with open("gmail_output.json", "w", encoding="utf-8") as file:
        json.dump(emails, file, indent=2, ensure_ascii=False)

    print("\nGmail connector test completed!")