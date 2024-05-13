# google connection
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import streamlit as st
import json

def upload_file_link(folder_id='1fkRcfgfBdvdtd6cR5BjJKyWFrD49GhCY'):
    # Connext to google drive
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    if 'log' not in st.session_state:
        # Create a flow instance to handle the authorization process
        flow = InstalledAppFlow.from_client_config({
            "installed": {
                "client_id": "740552604902-540pdaimb8r2mp1j0dsuqqp3ub1ds3jf.apps.googleusercontent.com",
                "client_secret": "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",
                "project_id": "videoappmarce",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
            }
        }, SCOPES)
        
        # Perform the authorization flow
        credentials = flow.run_local_server(port=0)
        
        # Create a service object for interacting with the Drive API
        drive_service = build('drive', 'v3', credentials=credentials)
    
        st.session_state['log'] = True
        st.session_state['credentials'] = credentials
        st.session_state['drive_service'] = drive_service
    else:
        # Retrieve the previously stored credentials and drive_service
        credentials = st.session_state['credentials']
        drive_service = st.session_state['drive_service']
    
    def list_files(folder_id):
        results = drive_service.files().list(
            q=f"'{folder_id}' in parents",
            pageSize=1000, # You can change the page size as needed
            fields="nextPageToken, files(id, name)"
        ).execute()
        items = results.get('files', [])
        return items
    
    # extract folders
    folders = list_files(folder_id)
    
    dct_files = {}
    for fold in folders:
        dct_files[fold['name']] = {}
        for i in list_files(fold['id']):
            if i['name'].split('.')[0] not in dct_files[fold['name']].keys():
                dct_files[fold['name']][i['name'].split('.')[0]] = {}

            if i['name'].split('.')[-1] == 'jpg':
                dct_files[fold['name']][i['name'].split('.')[0]]['image'] = i['id']
            else:
                dct_files[fold['name']][i['name'].split('.')[0]]['video'] = i['id']
    
    with open('drive_links.json', 'w') as f:
        json.dump(dct_files, f)
        
    st.write('Files uploaded!')