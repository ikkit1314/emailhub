from imapclient import IMAPClient
import ssl
from src.config import IMAP_HOST, IMAP_USER, IMAP_PASS

context = ssl.create_default_context()

with IMAPClient(IMAP_HOST, ssl=True, ssl_context=context) as client:
    client.login(IMAP_USER, IMAP_PASS)
    folders = client.list_folders()
    for folder in folders:
        print(folder)
