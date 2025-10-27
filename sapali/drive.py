from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
SCOPES=['https://www.googleapis.com/auth/drive.readonly']
def build_drive_from_json(creds_json):
    creds = service_account.Credentials.from_service_account_info(creds_json, scopes=SCOPES)
    return build('drive','v3',credentials=creds)
def list_files_in_folder(drive, folder_id):
    q=f"'%s' in parents and trashed=false"%folder_id
    return drive.files().list(q=q, fields='files(id,name,mimeType,modifiedTime)').execute().get('files',[])
def download_file_bytes(drive, file_id):
    req=drive.files().get_media(fileId=file_id); fh=io.BytesIO(); dl=MediaIoBaseDownload(fh, req); done=False
    while not done: status, done = dl.next_chunk()
    fh.seek(0); return fh.getvalue()
def export_google_doc_as_text(drive, file_id):
    data = drive.files().export(fileId=file_id, mimeType='text/plain').execute()
    return data.decode('utf-8','ignore') if isinstance(data, (bytes,bytearray)) else str(data)
