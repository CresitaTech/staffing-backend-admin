import imaplib
import pprint

imap_host = 'imap.gmail.com'
imap_user = 'kuriwaln@opallios.com'
imap_pass = 'Naresh@2252'

# connect to host using SSL
imap = imaplib.IMAP4_SSL(imap_host)

## login to server
imap.login(imap_user, imap_pass)

imap.select('Inbox')

# tmp, data = imap.search('Subject', 'ALL')
result, data = imap.search(None, 'Subject', '"{}"'.format('Daily Call Report'))

for num in data[0].split():
    tmp, data = imap.fetch(num, '(RFC822)')
    print('Message: {0}\n'.format(num))
    pprint.pprint(data[0][1])
    break
imap.close()
