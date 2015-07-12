import base64

msg = 'Hello World'
msg = msg.encode('utf-8')

enc_msg = base64.b64encode(msg)


