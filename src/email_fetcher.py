# src/email_fetcher.py
import ssl
from imapclient import IMAPClient
from .config import IMAP_HOST, IMAP_USER, IMAP_PASS, IMAP_FOLDER
from .utils import logger

def fetch_emails(account=None):
    if account is not None:
        host = account["IMAP_HOST"]
        user = account["IMAP_USER"]
        password = account["IMAP_PASS"]
    else:
        host = IMAP_HOST
        user = IMAP_USER
        password = IMAP_PASS

    logger.info("Connecting to IMAP server.")
    context = ssl.create_default_context()

    with IMAPClient(host, ssl=True, ssl_context=context) as client:
        client.login(user, password)
        logger.info(f"Logged in as {user}. Selecting folder 'popmart_order'.")
        client.select_folder("popmart_order")
        criteria = ['ALL']
        messages = client.search(criteria)
        logger.info(f"Found {len(messages)} messages for {user} in 'popmart_order'.")

        emails = []
        if messages:
            response = client.fetch(messages, ['BODY[]', 'ENVELOPE'])
            for msg_id, data in response.items():
                if b'BODY[]' in data:
                    emails.append(data[b'BODY[]'])
                else:
                    logger.warning(f"No BODY[] found for message {msg_id}")
        return emails
