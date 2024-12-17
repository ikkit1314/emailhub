from imapclient import IMAPClient
import ssl
from .config import IMAP_HOST, IMAP_USER, IMAP_PASS, IMAP_FOLDER
from .utils import logger

def fetch_emails(criteria='UNSEEN'):
    """
    Fetch emails from the IMAP folder based on the given criteria.
    Default criteria: UNSEEN emails.
    """
    logger.info("Connecting to IMAP server.")
    context = ssl.create_default_context()
    
    with IMAPClient(IMAP_HOST, ssl=True, ssl_context=context) as client:
        client.login(IMAP_USER, IMAP_PASS)
        logger.info(f"Logged in as {IMAP_USER}. Selecting folder {IMAP_FOLDER}.")
        client.select_folder(IMAP_FOLDER)
        
        # Search emails based on criteria (e.g., UNSEEN emails)
        messages = client.search(criteria)
        logger.info(f"Found {len(messages)} messages matching criteria '{criteria}'.")
        
        # Fetch full message data
        response = client.fetch(messages, ['RFC822', 'ENVELOPE'])
        
        # Return list of raw email messages
        emails = []
        for msg_id, data in response.items():
            raw_email = data[b'RFC822']
            emails.append(raw_email)
        
        return emails
