from MyGmail import *

"""
For all auth scopes, see
https://developers.google.com/gmail/api/auth/scopes
"""

scopes = 'https://www.googleapis.com/auth/gmail.compose'
client_secret_file = 'client_secret.json'
application_name = 'Test MyGmail API'

service = initialize_service(
            scopes, 
            client_secret_file, 
            application_name)

sender = 'ichiro.python@gmail.com'
to = 'ichiro.wahid@gmail.com'
subject = 'Hello from MyGmail API!'
message_text = 'Hello world!'

msg = create_message(sender, to, subject, message_text)

userId = 'me'
sent_msg = send_message(service, userId, msg)

