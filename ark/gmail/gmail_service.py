import pickle
import os

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

dirname = os.path.dirname(__file__)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


class GmailService:
    def __init__(self, credentials=None, pickle_file=None):
        self.credentials = credentials or os.path.join(dirname, "credentials.json")
        self.pickle_file = pickle_file or os.path.join(dirname, "token.pickle")

    def get_serivce(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.pickle_file):
            with open(self.pickle_file, "rb") as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.pickle_file, "wb") as token:
                pickle.dump(creds, token)

        return build("gmail", "v1", credentials=creds, cache_discovery=False)

    def search_message(self, service, user_id, search):
        results = service.users().messages().list(userId=user_id, labelIds=["INBOX"], q="is:unread " + search).execute()
        return [msg["id"] for msg in results.get("messages", [])]

    def get_message(self, service, user_id, msg_id):
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        return message

    def mark_read(self, service, user_id, msg_id):
        message = (
            service.users().messages().modify(userId=user_id, id=msg_id, body={"removeLabelIds": ["UNREAD"]}).execute()
        )
        return message