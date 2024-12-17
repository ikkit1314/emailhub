from .email_fetcher import fetch_emails
from .parser import parse_email
from .attachment_handler import handle_attachments
from .data_handler import save_to_csv
from .utils import logger

def main():
    logger.info("Starting email parsing process.")
    emails = fetch_emails(criteria='UNSEEN')
    parsed_data = []
    
    for raw_email in emails:
        try:
            attachments = handle_attachments(raw_email)
            parsed = parse_email(raw_email)
            # You could store attachment file paths in parsed data if needed
            parsed["attachments"] = attachments
            parsed_data.append(parsed)
        except Exception as e:
            logger.error(f"Error parsing email: {e}", exc_info=True)
    
    if parsed_data:
        save_to_csv(parsed_data)
    else:
        logger.info("No new emails to process.")

if __name__ == "__main__":
    main()
