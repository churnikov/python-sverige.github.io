#! /usr/bin/env python3
# src: https://scriptreference.com/sending-emails-via-gmail-with-python/
import pickle
import os
import base64
import googleapiclient.discovery
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import csv
import argparse

SENTLIST="sentmail.list"

# Get the path to the pickle file
home_dir = os.path.expanduser('~')
pickle_path = os.path.join(home_dir, 'gmail.pickle')

# Load our pickled credentials
creds = pickle.load(open(pickle_path, 'rb'))

# Build the service
service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)

def sendMail(data):
    # Create a message
    my_email = 'info@pycon.se'
    # fields: Order ID,Order Date,Attendee Status,Name,Email,Event Name,Ticket Quantity,Ticket Type,Ticket Price,Buyer Name,Buyer Emaill
    fullName = data['Name']
    firstName = fullName.split()[1]
    email = data['Email']
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Survey regarding PyCon Sweden 2022'
    msg['From'] = f'{my_email}'
    msg['To'] = f'{email}'
    #msg['Cc'] = 'board@pycon.se'
    msgPlain = f'''Hej {firstName},

Thank you for joining PyCon Sweden 2022! We hope that you have had
a great conference experience! To help us improve, please take a
few minutes to give us your feedback. As this is our first in person
conference since 2019, your suggestions will be particularly valuable
for us to improve our future events.

https://forms.gle/QEh9HqYTe2zMLzMa6

Once again, thank you for your support, and hopefully see you again
next year!

Kind regards,
Python Sverige
'''
    #msgHtml = msgPlain
    #print(msgPlain)
    msg.attach(MIMEText(msgPlain, 'plain'))
    #msg.attach(MIMEText(msgHtml, 'html'))
    raw = base64.urlsafe_b64encode(msg.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}

    message1 = body
    message = (
        service.users().messages().send(
            userId="me", body=message1).execute())

    print(f'Message Id: {message["id"]} to {email} sent')
    #print(f'Message Id: {email} sent')
    print('====')


if __name__ == '__main__':
    "Parsing command line here"

    parser = argparse.ArgumentParser(description="It sends mail notification to talks/workshops authors")
    parser.add_argument("--csvfile", help="CSV file with forms answers")
    args = parser.parse_args()

    if args.csvfile == None:
        parser.print_help()
        sys.exit(os.EX_NOINPUT)
    
    already_sent = []
    try:
        with open(SENTLIST) as sentlist:
            for line in sentlist.readlines():
                already_sent.append(line.rstrip())
    except FileNotFoundError:
        pass

    with open(args.csvfile, newline='') as csvfile:
        csvreader = csv.DictReader(csvfile)
        # fields: Order ID,Order Date,Attendee Status,Name,Email,Event Name,Ticket Quantity,Ticket Type,Ticket Price,Buyer Name,Buyer Emaill
        for row in csvreader:
            ticketType = row['Ticket Type']
            fullName = row['Name']
            email = row['Email']
            if ticketType in [ 'Sponsors', 'Speakers', 'Volunteers and board']:
                print(f'{fullName} has ticket type {ticketType} so mail skipped')
                continue
            if email in already_sent:
                print(f'{fullName} already received survey, so mail skipped')
                continue

            try:
                sendMail(row)
                #print(f'sending mail to {email}...')
            except:
                print(f'Failed to send mail to {fullName}')
                continue
            print(f'Mail sent to {fullName} at {email} for ticket type {ticketType}')
            already_sent.append(email)

    with open(SENTLIST, 'w') as sentlist:
        for entry in already_sent:
            sentlist.write(f'{entry}\n')




