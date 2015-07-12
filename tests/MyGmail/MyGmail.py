# Based on https://developers.google.com/gmail/api/quickstart/python

import httplib2
import os
import base64

from apiclient import discovery
from apiclient import errors

import oauth2client
from oauth2client import client
from oauth2client import tools

from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import mimetypes

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

def get_credentials(scopes, client_secret_file, application_name):
    """
    Gets valid user credentials from storage.

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
                                    'gmail-quickstart.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secret_file, scopes)
        flow.user_agent = application_name
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def initialize_service(scopes, client_secret_file, application_name):
    """
    Creates a Gmail API service object

    Args:
        scopes: Scope of Gmail API.
        client_secret_file: JSON file for app authorization w/ Gmail
        application_name: Application requesting Gmail service

    Returns:
        service: Authorized Gmail API service instnace
    """

    credentials = get_credentials(
            scopes, 
            client_secret_file, 
            application_name)

    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    return service


def create_draft(service, user_id, message_body):
    """
    Create and insert a draft email. 
    Print the returned draft's message and id.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
        message_body: The body of the email message, including headers.

    Reutrns:
        Draft object, including draft id and message meta data.
    """

    try:
        message = {'message': message_body}
        draft = service.users().drafts().create(userId=user_id, body = message).execute()

        print('Draft id: %s\nDraft message: %s' % (draft['id'], draft['message'] ))
        return draft
    except errors.HttpError as error:
        print('An error occured: %s' % error)
        return None

def create_message(sender, to, subject, message_text):
    """
    Create a message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

    Returns:
        An object containing a base64url encoded email object.
    """

    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    #return {'raw': base64.urlsafe_b64encode(bytes(message.as_string(), encoding="utf-8"))}
    # Updated from https://developers.google.com/gmail/api/v1/reference/users/messages/send
    #return {'raw': base64.urlsafe_b64encode(bytes(message.as_string(), 'utf_8') ) }
    return {'raw': base64.b64encode(message.as_string().encode('utf-8') ) }

def create_message_with_attachment(
        sender, to, subject, message_text, file_dir, filename):
    """
    Create a message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver
        subject: The subject of the email message.
        message_text: The text of the email message.
        file_dir: The directory containing the file to be attached.
        filename: The name of the file to be attached.

    Returns:
        An object containing a base64url encoded email object.
    """

    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    path = os.path.join(file_dir, filename)
    content_type, encoding = mimetypes.guess_type(path)

    if content_type is None or encoding is not None:
        content_type = 'application//octet-stream'

    main_type, sub_type = content_type.split('/', 1)

    if main_type == 'text':
        fp = open(path, 'rb')
        msg = MIMEText(fp.read(), _subtype = sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(path, 'rb')
        msg = MIMEImage(fp.read(), _subtype = sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(path, 'rb')
        msg = MIMEAudio(fp.read(), _subtype = sub_type)
        fp.close()
    else:
        fp = open(path, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    msg.add_header('Content-Disposition', 'attachment', filename = filename)
    message.attach(msg)

    return{'raw': base64.urlsafe_b64encode(message.as_string())}

def send_message(service, user_id, message):
    """
    Send an email message.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The sepcial value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

    Returns:
        Sent Message.
    """

    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

