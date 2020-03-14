
from __future__ import print_function
import pickle
import os.path
import random
import csv
import smtplib
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user']


def create_user(service, account, password, first_name, last_name,
                alt_email, phone):

    user = {
        "primaryEmail": account,
        "name": {
            "givenName": first_name,
            "familyName": last_name,
        },
        "isAdmin": False,
        "isDelegatedAdmin": False,
        "agreedToTerms": True,
        "password": password,
        "changePasswordAtNextLogin": True,
        "emails": [
            {
                "address": alt_email,
                "type": "home",
                "customType": "",
                "primary": True
            }
        ],
        "phones": [
            {
                "value": phone,
                "type": "mobile"
            }
        ],
        "orgUnitPath": "/hcs-pt/pt-teachers",
        "includeInGlobalAddressList": True
    }

    response = service.users().insert(body=user).execute()
    return response


def send_mail(email, first_name, account, password):

    message = """\

        Dear {0},
        
        To facilitate online teaching, HCS Potomac created a school email account for you,
        
        Email: {1}
        Password: {2}
        
        This is just a gmail account. You should go to gmail.com and login with above
        credentials. It should ask you to change password once logged in.
        
        If you encounter any issues, feel free to contact me.
        
        Zhihong Zhang
        
        """
    body = message.format(first_name, account, password)

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "zhihong@gmail.com"

    server = smtplib.SMTP_SSL(smtp_server, port)
    server.login(sender_email, 'xxxxx')
    msg = MIMEText(body)
    msg['Subject'] = 'HCS Email Account'
    msg['From'] = sender_email
    msg['To'] = email

    result = server.sendmail(sender_email, email, msg.as_string())
    print(result)
    server.quit()

def generate_password(account):
    num = hash(account)%1000000
    return 'Hcs-' + str(num)

def build_service():

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/Users/zhangz/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('admin', 'directory_v1', credentials=creds)
    return service

def main():

    service = build_service()

    with open('/Users/zhangz/Downloads/hcs.csv') as f:
        reader = csv.reader(f, delimiter=',')

        for row in reader:
            first_name = row[1]
            last_name = row[2]
            alt_email = row[4]
            phone = row[5]
            account = row[6]
            password = generate_password(account)

            create_user(service, account, password, first_name, last_name, alt_email, phone)

            if alt_email:
                send_mail(alt_email, first_name, account, password)

            print('Account: ' + account + ' Password: ' + password + ' Alt Email: ' + alt_email)



if __name__ == '__main__':
    main();
