# data_handler.py (snippet)

import os
import re
import pandas as pd
from .config import OUTPUT_CSV_PATH
from .utils import logger

def save_to_csv(data_list, sort_by="email_date", ascending=True):
    columns = [
        "subject",
        "from",
        "to",
        "email_date",
        "order_number",
        "order_date",
        "shipping_address",
        "item_name",
        "quantity",
        "price",
        "subtotal",
        "discount",
        "shipping_cost",
        "sales_tax",
        "total",
        "tracking_number",
        "shipped_date",
        # Add an "image_url" column
        "image_url"
    ]

    if not data_list:
        logger.info("No data to save.")
        return

    # Load existing or create a new DataFrame
    os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)
    if not os.path.exists(OUTPUT_CSV_PATH) or os.stat(OUTPUT_CSV_PATH).st_size == 0:
        df_existing = pd.DataFrame(columns=columns)
    else:
        df_existing = pd.read_csv(OUTPUT_CSV_PATH)

    df_new = pd.DataFrame(data_list)
    for col in columns:
        if col not in df_new.columns:
            df_new[col] = ""

    # Combine old + new
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)

    # Deduplicate by order_number
    df_combined.drop_duplicates(subset=["order_number"], keep='last', inplace=True)

    # Convert 'email_date' to datetime
    df_combined['email_date'] = pd.to_datetime(
        df_combined['email_date'],
        errors='coerce',
        utc=True
    )
    df_combined['email_date'] = df_combined['email_date'].dt.tz_convert('America/Los_Angeles')

    # Sort descending by default, so the newest is on top
    if sort_by in df_combined.columns:
        df_combined.sort_values(by=sort_by, ascending=ascending, inplace=True)
    else:
        logger.warning(f"Cannot sort by {sort_by}, column not found.")

    df_combined.to_csv(OUTPUT_CSV_PATH, index=False)
    logger.info(f"Data saved to {OUTPUT_CSV_PATH} and sorted by {sort_by} "
                f"({'ascending' if ascending else 'descending'})")
