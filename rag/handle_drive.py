import os.path
import json
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# from 
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]

# function to download specified file id
def download_file(file_id,creds):
  # print('starting...')
  # print(file_id)
  # print(creds)
  try:
    service = build("drive", "v3", credentials=creds)
    req = service.files().get_media(fileId=file_id)
    file = io.BytesIO()

    downloader = MediaIoBaseDownload(file, req)
    done = False
    while done is False:
      status, done = downloader.next_chunk()
      print(f"Download {int(status.progress() * 100)}%.")

  except HttpError as error:
    print(f"An error occurred: {error}")
    file = None

  return file.getvalue()


def extract_pdf_metadata():
  """Shows basic usage of the Drive v3 API.
  queries the respected folder files or the particular file using their ids.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("drive", "v3", credentials=creds)

    # Call the Drive v3 API
    print("calling api...")
    # demo folder id
    folder_id = "1Ccz5XU9YTMHf9xxIpN7q3T8DYIqU9-ZW"
    # demo fild id
    file_id = "1Gq3ZIv0uOJuBSYFCPY0rKxlTQqb8fNUi"
#     results = (
#     # query to get all the pdf from a folder
#     service.files()
#     .list(q=f"'{folder_id}' in parents and trashed = false", fields="nextPageToken, files(id, name, webViewLink, webViewLink, webContentLink)")
#     .execute()
# )
#     if not items:
#       print("No files found.")
#       return
    # items = results.get("files", [])
    file_metadata = service.files().get(fileId=file_id, fields="id, name, mimeType, webViewLink").execute()

    # print("Files:")
    print("writing to file_info.json...")
    # with open("file_info.json", "w") as f:
    #   json.dump(items,f,indent=4)
    with open("./temp/demo_file_info.json", "w") as f:
      file_metadata = [file_metadata]
      json.dump(file_metadata,f,indent=4)  
    print("Done.")
    # for item in items:
    #   print(f"{item['name']} ({item['id']})" )
  except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
    print(f"An error occurred: {error}")




if __name__ == "__main__":
    """
    function to query google drive api to get folders or file metadata information and writes to json file
    """
    extract_pdf_metadata()
    
    """
    function to download the pdfs from google drive api using the extracted pdf's file Id.
    """
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        file_info = None
        with open("./temp/demo_file_info.json", "r") as f:
            file_info = json.load(f)
        for item in file_info:
            file_Id = item["id"]
            downloaded_content = download_file(file_Id,creds=creds)
            if downloaded_content:
                with open(f"./downloaded-files/{file_Id}.pdf", "wb") as f:
                    f.write(downloaded_content)
                print("file downloaded successfully")
            else:
                print('error!!')


# [
#     {
#         "id": "1Gq3ZIv0uOJuBSYFCPY0rKxlTQqb8fNUi",
#         "name": "test3.pdf",
#         "mimeType": "application/pdf",
#         "webViewLink": "https://drive.google.com/file/d/1Gq3ZIv0uOJuBSYFCPY0rKxlTQqb8fNUi/view?usp=drivesdk"
#     }
# ]