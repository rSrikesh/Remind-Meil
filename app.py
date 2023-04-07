from flask import Flask,jsonify,request
import imaplib
import email
from email.header import decode_header
from email2rem import Email2Reminder
import json
import os

app = Flask(__name__)
filename = 'data.json'

@app.route('/data', methods=['GET', 'POST'])
def data():
    imap = imaplib.IMAP4_SSL('imap.gmail.com')
    d = request.get_json()
    username = d['name']
    password= d['password']
    # username = "arlertarmin935@gmail.com"
    # password = "bxizxsbwaxgdelhv"
    imap.login(username, password)
    imap.select('inbox')
    criteria = '(UNSEEN)'
    result, data = imap.search(None, criteria)
    mails = []

    for num in data[0].split():
        result, data = imap.fetch(num, '(RFC822)')
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)
        from_email = email.utils.parseaddr(email_message['From'])[1]
        to_email = email.utils.parseaddr(email_message['To'])[1]
        subject = decode_header(email_message['Subject'])[0][0]
        date = email_message['Date']
        body = ''
        for part in email_message.walk():
            if part.get_content_type() == 'text/plain':
                charset = part.get_content_charset() or 'utf-8'
                body += part.get_payload(decode=True).decode(charset)
        
        email2rem = Email2Reminder(subject, body,21)
        mails.append(email2rem.extracts())
        

    imap.logout()

    if len(mails) == 0:
        return "No new mails"

    
    if not os.path.exists(filename):
        with open(filename, mode='w', encoding='utf-8') as f:
            json.dump([], f,indent=4)
        
    with open(filename) as feedsjson:
        feeds = json.load(feedsjson)

    feeds.append(mails)
    with open(filename, mode='w') as f:
        f.write(json.dumps(feeds, indent=4))

    return "debug"

    
app.run(host='127.0.0.1',port=5001,debug=True)
