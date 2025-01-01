# parser.py
import email
import re
from bs4 import BeautifulSoup
from email.header import decode_header
from .utils import logger

def parse_email(raw_email):
    msg = email.message_from_bytes(raw_email)
    subject = decode_subject(msg.get('Subject', ''))
    from_ = msg.get('From', '')
    email_date = msg.get('Date', '')
    to_ = msg.get('To', '')

    html_content = get_html_content(msg)
    image_url = extract_second_image_url(html_content)  # Use the second image URL

    is_order = bool(re.search(r'order', subject, re.IGNORECASE) and re.search(r'confirmed|summary', subject, re.IGNORECASE))
    is_shipment = bool(re.search(r'shipment|on the way', subject, re.IGNORECASE))

    if is_order:
        data = parse_order_email(html_content, subject, email_date, from_)
        data["image_url"] = image_url
        data["to"] = to_
        return data
    elif is_shipment:
        data = parse_shipment_email(html_content, subject, email_date, from_)
        data["image_url"] = image_url
        data["to"] = to_
        return data
    else:
        logger.info(f"Skipping email with subject: {subject}")
        return None

def extract_second_image_url(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    images = soup.find_all("img")
    if len(images) >= 2:
        return images[1].get("src") or ""
    return ""

def decode_subject(subject):
    decoded_subject_parts = decode_header(subject)
    subject_decoded = ""
    for part, encoding in decoded_subject_parts:
        if isinstance(part, bytes):
            subject_decoded += part.decode(encoding or 'utf-8')
        else:
            subject_decoded += part
    return subject_decoded

def get_html_content(msg):
    if msg.is_multipart():
        html_content = ""
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html_content += part.get_payload(decode=True).decode(errors='replace')
        return html_content
    else:
        if msg.get_content_type() == "text/html":
            return msg.get_payload(decode=True).decode(errors='replace')
    return ""

def parse_order_email(html_content, subject, email_date, from_):
    text = BeautifulSoup(html_content, "html.parser").get_text(separator='\n').strip()
    order_number = extract_field(text, r"Order number:\s*(#[A-Za-z0-9]+)")
    if not order_number:
        order_number = extract_field(subject, r"[Oo]rder\s*(#[A-Za-z0-9]+)")

    order_date = extract_field(text, r"Date:\s*([\w\s,]+)")
    shipping_address = extract_multiline_field(text, "Shipping Address", ["ITEMS", "Subtotal", "TOTAL"])
    item_name, quantity, price = parse_item_line(text)
    subtotal = extract_price(text, r"Subtotal.*?([A-Z]*\$[\d\.]+)")
    discount = extract_price(text, r"Discount.*?([A-Z]*\$[\d\.]+)")
    shipping_cost = extract_price(text, r"Shipping.*?([A-Z]*\$[\d\.]+)")
    sales_tax = extract_price(text, r"Sales Tax.*?([A-Z]*\$[\d\.]+)")
    total = extract_price(text, r"TOTAL\s*([A-Z]*\$[\d\.]+)")

    return {
        "subject": subject,
        "from": from_,
        "email_date": email_date,
        "order_number": order_number,
        "order_date": order_date,
        "shipping_address": shipping_address,
        "item_name": item_name,
        "quantity": quantity,
        "price": price,
        "subtotal": subtotal,
        "discount": discount,
        "shipping_cost": shipping_cost,
        "sales_tax": sales_tax,
        "total": total,
        "tracking_number": "",
    }

def parse_shipment_email(html_content, subject, email_date, from_):
    text = BeautifulSoup(html_content, "html.parser").get_text(separator='\n').strip()
    order_number = extract_field(subject, r"order\s*(#[A-Za-z0-9]+)", flags=re.IGNORECASE)
    if not order_number:
        order_number = extract_field(text, r"order\s*(#[A-Za-z0-9]+)", flags=re.IGNORECASE)
    tracking_number = extract_field(text, r"Tracking number:\s*(\S+)")
    return {
        "subject": subject,
        "from": from_,
        "email_date": email_date,
        "order_number": order_number,
        "order_date": "",
        "shipping_address": "",
        "item_name": "",
        "quantity": "",
        "price": "",
        "subtotal": "",
        "discount": "",
        "shipping_cost": "",
        "sales_tax": "",
        "total": "",
        "tracking_number": tracking_number,
        "shipped_date": email_date
    }

def extract_field(text, pattern, flags=0):
    match = re.search(pattern, text, flags)
    return match.group(1).strip() if match else ""

def extract_multiline_field(text, start_label, stop_labels):
    pattern = re.escape(start_label) + r"(.*?)(?:" + "|".join(map(re.escape, stop_labels)) + ")"
    match = re.search(pattern, text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""

def parse_item_line(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    headers_needed = ["ITEMS", "NAME", "SIZE", "QTY", "PRICE"]
    headers_found = []
    start_index = None

    for i, line in enumerate(lines):
        words = line.upper().split()
        if headers_needed and headers_needed[0] in words:
            headers_found.append(headers_needed.pop(0))
            if start_index is None:
                start_index = i
            if not headers_needed:
                break

    if headers_needed:
        return "", "", ""

    current_index = i + 1
    non_item_phrases = {"VIEW YOUR ORDER", "ORDER SUMMARY"}
    while current_index < len(lines):
        candidate = lines[current_index]
        if candidate.upper() in non_item_phrases:
            current_index += 1
            continue
        break

    if current_index >= len(lines):
        return "", "", ""

    item_name = lines[current_index].strip()
    current_index += 1
    if current_index >= len(lines):
        return item_name, "", ""

    item_size = lines[current_index].strip()
    current_index += 1
    if current_index >= len(lines):
        return item_name, "", ""

    quantity = lines[current_index].strip()
    current_index += 1
    if current_index >= len(lines):
        return item_name, quantity, ""

    price = lines[current_index].strip()
    return f"{item_name} ({item_size})", quantity, price

def extract_price(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""
