import email
import re
from bs4 import BeautifulSoup
from .utils import logger

# Example regex patterns (customize as needed)
ORDER_NUMBER_REGEX = r"Order\s*Number:\s*(\w+)"
TRACKING_REGEX = r"Tracking\s*Number:\s*(\w+)"
# For recipient extraction, often "Delivered-To" or "X-Original-To" headers are used:
RECIPIENT_HEADERS = ["Delivered-To", "X-Original-To"]

def parse_email(raw_email):
    """
    Parse a raw email message to extract needed fields.
    """
    msg = email.message_from_bytes(raw_email)
    
    # Extract headers
    subject = msg.get('Subject', '')
    from_ = msg.get('From', '')
    date = msg.get('Date', '')
    
    recipient_email = None
    for header in RECIPIENT_HEADERS:
        val = msg.get(header, None)
        if val:
            recipient_email = val
            break
    
    if not recipient_email:
        # Fallback: Try from envelope data or other heuristic if catchall isn't in header
        # This might be domain-specific logic
        logger.warning("No explicit recipient header found.")
        recipient_email = "unknown@example.com"
    
    # Extract text content and HTML content
    text_content = ""
    html_content = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                text_content += part.get_payload(decode=True).decode(errors='replace')
            elif content_type == "text/html":
                html_content += part.get_payload(decode=True).decode(errors='replace')
    else:
        # If not multipart, assume text/plain
        text_content = msg.get_payload(decode=True).decode(errors='replace')
    
    # Use HTML content if available, otherwise text
    content_to_parse = html_content if html_content else text_content
    
    # For HTML, parse with BeautifulSoup if needed
    soup = BeautifulSoup(content_to_parse, "html.parser")
    parsed_text = soup.get_text(separator=' ')
    
    # Extract order number, tracking number, etc. using regex
    order_number = extract_field(parsed_text, ORDER_NUMBER_REGEX)
    tracking_number = extract_field(parsed_text, TRACKING_REGEX)
    
    # Additional logic to parse product details, line items, etc. would go here
    # This could involve more complex HTML parsing or regex.
    product_details = parse_product_details(parsed_text)
    
    return {
        "recipient_email": recipient_email,
        "order_number": order_number,
        "tracking_number": tracking_number,
        "sender_domain": extract_domain(from_),
        "date": date,
        "subject": subject,
        "raw_text": parsed_text,
        "product_details": product_details
    }

def extract_field(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else ""

def extract_domain(from_field):
    # Extract domain from email address in from field
    # from_field usually in form "Name <email@domain.com>"
    match = re.search(r'@([A-Za-z0-9.-]+\.[A-Za-z]+)', from_field)
    return match.group(1) if match else ""

def parse_product_details(text):
    # Placeholder function for extracting product details.
    # Implement logic depending on your email templates:
    # For example: "Product: Widget A (Qty: 2)"
    return "N/A"
