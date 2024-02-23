import os
from datetime import *
# import google API libraries
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
# libraries needed for emailing
import base64
import mimetypes
from email.message import EmailMessage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

EMAIL_TARGET = os.environ.get('ERROR_LOG_TARGET_EMAIL')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER')

# Google API Scopes that will be used. If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

# Get credentials from json file, ask for permissions on scope or use existing token.json approval, then build the "service" connection to Google API
creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('gmail', 'v1', credentials=creds)

if __name__ == '__main__': # main file execution
    errorCount = 0 # define an error counter
    errorString = "" # define empty string of errors we will add to later
    with open('warnings.txt','w') as warnings:
        with open('errors.txt','w') as errors:
            currentDir = os.getcwd() # get the current scripts direcotry
            parentDir = "" # reset parentDir to blank
            dirParts = currentDir.split("\\")
            for i in range(len(dirParts)-1): # go through as many parts as there are -1 to get the full path except the current actual directory, which results in our parent directory
                parentDir = parentDir + dirParts[i] + "\\" # append each part together replacing the \ to generate the parent directory

            entries = os.listdir(parentDir) # find all objects in this parent directory
            allDirectories = []
            for entry in entries:
                if os.path.isdir(parentDir + entry): # check to see if the entry is a directory or not, only continue if so
                    allDirectories.append(parentDir + entry)
            print(currentDir)
            print(parentDir)
            # print(entries)
            for directory in allDirectories:
                # print(f'Found directory {directory} in parent directory')
                entries = os.listdir(directory) # find all objects in the target directory
                for entry in entries:
                    if "log" in entry.lower() and not ".py" in entry.lower(): # look for files that have log in their name, case insensitive, but ignore this script and other .py scripts
                        logFile = directory + "\\" + entry
                        print(f'Found file {logFile} in {directory}')
                        with open(logFile,'r') as readFile:
                            for line in readFile:
                                if "ERROR" in line:
                                    print(line.strip() + "  |  " + logFile, file=errors) # strip the newline character off the end and output it, also add the file the error was found in
                                    errorCount += 1 # add 1 to error count
                                    errorString = errorString + line
                                if "WARN" in line:
                                    print(line.strip(), file=warnings)
    if errorCount > 0:
        print(f'Found {errorCount} errors, emailing summary')
        mime_message = EmailMessage() # create a email message object

        # headers
        mime_message['To'] = EMAIL_TARGET # the email address it is sent to
        mime_message['From'] = EMAIL_SENDER # this doesnt seem to do anything, it will always send from the email that is used for authentication
        mime_message['Subject'] = 'Error Report for ' + datetime.now().strftime('%Y-%m-%d') # subject line of the email, change to your liking

        mime_message.set_content(f"Warning, there were {errorCount} errors in recent scripts: \n{errorString}") # the body of the email, aka the text

        # attachment
        attachment_filename = "errors.txt" # tell the email what file we are attaching
        # guessing the MIME type
        type_subtype, _ = mimetypes.guess_type(attachment_filename)
        maintype, subtype = type_subtype.split('/')

        with open(attachment_filename, 'rb') as fp:
            attachment_data = fp.read() # read the file data in and store it in the attachment_data
        mime_message.add_attachment(attachment_data, maintype, subtype, filename="errors.txt") # add the attacment data to the message object, give it a filename that was our pdf file name

        # encoded message
        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }

        send_message = (service.users().messages().send(userId="me", body=create_message).execute())
        print(f'Email sent, message ID: {send_message["id"]}') # print out resulting message Id
    