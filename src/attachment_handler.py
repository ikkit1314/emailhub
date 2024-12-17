import os
import email
from .utils import logger

def handle_attachments(raw_email, attachments_dir="attachments"):
    # Example of extracting and saving attachments
    # Create directory if not exists
    os.makedirs(attachments_dir, exist_ok=True)

    msg = email.message_from_bytes(raw_email)
    saved_attachments = []
    
    for part in msg.walk():
        if part.get_content_disposition() == 'attachment':
            filename = part.get_filename()
            if filename:
                filepath = os.path.join(attachments_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                logger.info(f"Saved attachment: {filepath}")
                saved_attachments.append(filepath)
    return saved_attachments
