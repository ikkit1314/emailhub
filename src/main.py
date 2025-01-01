# src/main.py
import json
import os
from src.email_fetcher import fetch_emails
from src.parser import parse_email
from src.data_handler import save_to_csv
from src.utils import logger

import sys
import os


def load_accounts():
    # Determine the directory where the bundled files are located
    if hasattr(sys, '_MEIPASS'):  # PyInstaller sets this when bundling
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    accounts_path = os.path.join(base_dir, 'accounts.json')

    print(f"Base directory: {base_dir}")
    print(f"Looking for accounts.json at: {accounts_path}")

    # Ensure accounts.json exists
    if not os.path.exists(accounts_path):
        raise FileNotFoundError(f"'accounts.json' not found at: {accounts_path}")

    # Load the JSON file
    with open(accounts_path, 'r', encoding='utf-8') as f:
        return json.load(f)



def main():
    logger.info("Starting email parsing process.")
    accounts = load_accounts()
    orders_dict = []

    # Gather all parsed emails from all accounts before saving
    all_parsed_emails = []

    for account in accounts:
        fetched = fetch_emails(account)
        for raw_email in fetched:
            parsed = parse_email(raw_email)
            if not parsed:
                continue
            all_parsed_emails.append(parsed)

    # Build orders_dict (merge/track orders+shipments)
    merged_orders = {}
    for parsed in all_parsed_emails:
        order_number = parsed.get("order_number", "")
        if not order_number:
            continue
        is_order = bool(parsed.get("subtotal") or parsed.get("item_name"))
        is_shipment = bool(parsed.get("tracking_number"))
        if order_number in merged_orders:
            existing = merged_orders[order_number]
            if is_order and not (existing.get("subtotal") or existing.get("item_name")):
                for k, v in parsed.items():
                    if v:
                        existing[k] = v
            elif is_shipment:
                if parsed.get("tracking_number"):
                    existing["tracking_number"] = parsed["tracking_number"]
                if parsed.get("shipped_date"):
                    existing["shipped_date"] = parsed["shipped_date"]
        else:
            merged_orders[order_number] = parsed

    final_data = []
    for order in merged_orders.values():
        if order.get("subtotal") or order.get("item_name"):
            final_data.append(order)

    if final_data:
        save_to_csv(final_data, sort_by="email_date", ascending=False)
    else:
        logger.info("No complete orders found.")




if __name__ == "__main__":
    main()
    
