import imaplib
import email
from email.header import decode_header
import os
import pandas as pd
import numpy as np
import logging

from staffingapp.settings import PARSER_EMAIL, PARSER_PASSWORD

logger = logging.getLogger(__name__)

# account credentials
# username = "khuriwaln@cresitatech.com"
# password = "khuriwaln@123$"
# imap_server = "imap.secureserver.net"


# number of top emails to fetch
N = 3
resultDf = []


# total number of emails
# messages = int(messages[0])

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)


# Function to get email content part i.e its body part
def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)


# Function to search for a key value pair
def search(key, value, con):
    result, data = con.search(None, key, '"{}"'.format(value))
    return data


# Function to get the list of emails under this label
def get_emails(result_bytes):
    imap_server = 'imap.gmail.com'
    username = str(PARSER_EMAIL)
    password = str(PARSER_PASSWORD)

    # create an IMAP4 class with SSL
    imap = imaplib.IMAP4_SSL(imap_server)
    # authenticate
    imap.login(username, password)

    status, messages = imap.select("INBOX")

    msgs = []  # all the email data are pushed inside an array
    for num in result_bytes[0].split():
        typ, data = imap.fetch(num, '(RFC822)')
        msgs.append(data)

    return msgs


def extractBody(emailString):
    salutes = ["Name"]  # A list containing greetings key words, like 'dear', 'hi', etc
    goodbyes = [
        "Here is your Click to Call Outbound Report"]  # A list containing email footers like 'best regards' 'bye', etc

    # Split your email by line breaks and make everything lowercase
    emailLines = emailString.lower().split("\n")
    normalLines = emailString.split("\n")

    # Start and end points to extract the text
    start = -1
    end = len(emailLines) - 1

    for i in range(len(emailLines)):
        line = emailLines[i]

        # Check if any salute words in this line
        if len([s for s in salutes if s in line]) and start == -1:
            start = i + 1
            continue

        # Check if any goodbyes in this line
        if len([s for s in goodbyes if s in line]) and end == len(emailLines) - 1:
            end = i
            break

    if start == -1:
        return "\n".join(normalLines[:end])
    else:
        return "\n".join(normalLines[start:end])


def getCustomerCalls():
    imap_server = 'imap.gmail.com'
    username = str(PARSER_EMAIL)
    password = str(PARSER_PASSWORD)

    # create an IMAP4 class with SSL
    imap = imaplib.IMAP4_SSL(imap_server)
    # authenticate
    imap.login(username, password)

    status, messages = imap.select("INBOX")
    
    # fetching emails from this user "tu**h*****1@gmail.com"
    # msgs = get_emails(search('FROM', 'MY_ANOTHER_GMAIL_ADDRESS', con))
    messages = get_emails(search('Subject', 'Daily Call Report', imap))
    for msg in messages[::-1]:
        #    for sent in msg:
        # for i in range(messages, messages - N, -1):
        # fetch the email message by ID
        #    res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)

                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)

                # decode the email date
                mailDate, encoding = decode_header(msg["Date"])[0]
                if isinstance(mailDate, bytes):
                    # if it's a bytes, decode to str
                    mailDate = mailDate.decode(encoding)

                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            logger.info(body)
                        elif "attachment" in content_disposition:
                            # download attachment
                            filename = part.get_filename()
                            if filename:
                                folder_name = clean(subject)
                                if not os.path.isdir(folder_name):
                                    # make a folder for this email (named after the subject)
                                    os.mkdir(folder_name)
                                filepath = os.path.join(folder_name, filename)
                                # download attachment and save it
                                open(filepath, "wb").write(part.get_payload(decode=True))
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        # print only text email parts
                        logger.info(body)

                if content_type == "text/html":
                    # if it's HTML, create a new HTML file and open it in browser
                    folder_name = clean(subject)
                    if not os.path.isdir(folder_name):
                        # make a folder for this email (named after the subject)
                        os.mkdir(folder_name)
                    filename = "index.html"
                    filepath = os.path.join(folder_name, filename)
                    # write the file
                    open(filepath, "w").write(body)
                    # open in the default browser
                    # webbrowser.open(filepath)
                    table_MN = pd.read_html(filepath,
                                            match='Daily Report', encoding='latin1')

                    logger.info('Tables found:===================', len(table_MN))
                    logger.info("Date========:", mailDate)
                    logger.info("Subject =>:", subject)
                    logger.info("From =>:", From)


                    df = table_MN[0]
                    df.head()
                    df.columns = ['recruiter_name', 'attempted_calls', 'connected_calls', 'missed_calls']

                    df['attempted_calls'] = df['attempted_calls'].replace(np.nan, "NA")
                    df['connected_calls'] = df['connected_calls'].replace(np.nan, "NA")
                    df['missed_calls'] = df['missed_calls'].replace(np.nan, "NA")
                    df['recruiter_name'] = df['recruiter_name'].replace(np.nan, "NA")

                    # print(df)
                    df = df.query('attempted_calls != "NA" ')
                    # print("==================== Second Table ========================")
                    df = df.query('recruiter_name != "Name" and attempted_calls != "Follow us" ')
                    df['attempted_calls'] = df['attempted_calls'].astype(int)
                    df['connected_calls'] = df['connected_calls'].astype(int)
                    df['missed_calls'] = df['missed_calls'].astype(int)
                    resultDf = df
                    return df

                logger.info("=" * 100)
    # close the connection and logout

    imap.close()
    imap.logout()


# result = getCustomerCalls()
# print(result)
