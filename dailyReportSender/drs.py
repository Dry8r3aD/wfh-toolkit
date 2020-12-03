#!/usr/bin/python
# -*- coding: utf-8 -*-
import pickle
import base64
import datetime
import os.path
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SENDER_EMAIL = None
RECEIVER_EMAIL = None
CC_EMAILS = None

TOKEN_PATH = './token.pickle'
CREDENTIAL_PATH = './credentials.json'

ORGANAZATION = '소속'
NAME = "이름"
DEFAULT_TITLE_FORMAT = '[공유] {} {} 일일 업무보고서 ({})'
REPORT_LINK = "https://docs.google.com/spreadsheets/d/1EGnI9EYf7V9_uEzXrQkQiB9enjKZ_sE4MXQzGBQzGLY/edit?usp=sharing"


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def create_message(sender, to, subject, message_text, cc = None):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    if message['cc']:
        message['cc'] = cc;

    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    return {'raw': raw}

def send_message(service, user_id, message):
    message = (service.users().messages().send(userId=user_id, body=message).execute())
    print('Message Id: {}'.format(message['id']))
    return message

def main():
    cred = None

    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIAL_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=cred)

    today = datetime.date.today()
    md = '{}/{}'.format(str(today.month), str(today.day))
    subject = DEFAULT_TITLE_FORMAT.format(ORGANAZATION, NAME, md)
    print(subject)

    msg_text = '''안녕하세요, ''' + ORGANAZATION + ''' ''' + NAME + '''입니다.\n
일일 업무보고서 제출드립니다.
* ''' + REPORT_LINK + '''\n
고맙습니다.'''
    print(msg_text)

    msg = create_message(SENDER_EMAIL, RECEIVER_EMAIL, subject, msg_text, CC_EMAILS)
    send_message(service, 'me', msg)

if __name__ == '__main__':
    main()
