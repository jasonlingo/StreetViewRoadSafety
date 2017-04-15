import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import httplib2
import datetime
import time

from apiclient import errors
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.file import Storage
from oauth2client import client
from oauth2client import tools

from config import CONFIG

APPLICATION_NAME = 'Drive API'
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# Check https://developers.google.com/drive/scopes for all available scopes.
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

def GDriveUpload(imageList, folderName):
    """
    Create a public folder on Google Drive and upload images to it.

    Args:
      (list) imageList: the images to be uploaded.
      (String) folderName: the folder's name on Google Drive.
    Returns:
      (dictionary) a dictionary of uploaded images and their public link.
    """

    # Get an authorization from Google Drive API.
    # Redirect URI for installed apps.
    REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

    # # Run through the OAuth flow and retrieve credentials.
    # # flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, redirect_uri=REDIRECT_URI)
    # flow = flow_from_clientsecrets(CLIENT_SECRET_FILE,
    #                                scope=OAUTH_SCOPE,
    #                                redirect_uri=REDIRECT_URI)
    # authorize_url = flow.step1_get_authorize_url()
    # print 'Go to the following link in your browser: ' + authorize_url
    #
    # # Open a web page using the authorize_url to get an authorization code.
    # webbrowser.open_new(authorize_url)
    #
    # # User inputs the authorization code.
    # code = raw_input('Enter verification code: ').strip()
    # credentials = flow.step2_exchange(code)
    credentials = get_credentials()

    # Create an httplib2.Http object and authorize it with our credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Build a Google Drive service.
    drive_service = build('drive', 'v2', http=http)

    # Create a public folder on Google Drive.
    folder = create_public_folder(drive_service, folderName + "-" + datetime.datetime.now().strftime("%y-%m-%d-%H-%M"))

    # Get the folder id from the replied data.
    folder_id = folder['id']

    # Upload images to Google Drive.
    links = {}
    for image in imageList:
        try:
            # Upload images.
            # insert_file( drive service, image name, description, folder id on Google Drive, media type, the address of the image)
            file = insert_file(drive_service, image.split("/")[-1], "street view image", folder_id, 'image/jpeg', image)
            while file is None:
                print "sleep for one second"
                time.sleep(1)
                file = insert_file(drive_service, image.split("/")[-1], "street view image", folder_id, 'image/jpeg', image)

            print image + " uploaded!"

            # Get the public web link of the uploaded image.
            templink = file['webContentLink'].strip().split("&")[0]
            links[image] = templink
        except:
            print file


    return links


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-Python.json')

    store = Storage(credential_path)
    credentials = store.get()
    clientSecretFile = CONFIG["gdrive"]["clientSecretPath"]
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(clientSecretFile, OAUTH_SCOPE)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def create_public_folder(service, folderName):
    """
    Create a public folder on Google Drive.

    Args:
      (Google service) service: the Google drive service.
      (String) folderName: the name of the folder that is going to be created.
    Returns:
      (dictionary) information of the created folder.
    """

    # Parameters for uploading images.
    body = {
        'title': folderName,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    # Insert the image
    file = service.files().insert(body=body).execute()

    # Parameters for setting the privacy of the new folder.
    permission = {
        'value': '',
        'type': 'anyone',
        'role': 'reader'
    }

    # Set the privacy of the created folder.
    service.permissions().insert(fileId=file['id'], body=permission).execute()

    return file


def insert_file(service, title, description, parent_id, mime_type, filename):
    """
    Insert new file.

    Args:
      service: Drive API service instance.
      (String) title: Title of the file to insert, including the extension.
      (String) description: Description of the file to insert.
      (String) parent_id: Parent folder's ID.
      (String) mime_type: MIME type of the file to insert.
      (String) filename: Filename of the file to insert.
    Returns:
      (dictionary) Inserted file metadata if successful, None otherwise.
    """

    # Parameters for uploading a file.
    media_body = MediaFileUpload(filename, mimetype=mime_type, resumable=True)
    body = {
        'title': title,
        'description': description,
        'mimeType': mime_type
    }

    # Set the parent folder.
    if parent_id:
        body['parents'] = [{'id': parent_id}]

    try:
        # Insert a file.
        file = service.files().insert(
            body=body,
            media_body=media_body).execute()
        return file
    except errors.HttpError, error:
        print 'An error occured: %s' % error
        return None
