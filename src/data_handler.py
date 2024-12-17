import os
import pandas as pd
from .config import OUTPUT_CSV_PATH
from .utils import logger

def save_to_csv(data_list):
    """
    Save parsed data to a CSV. 
    Deduplicate if desired.
    """
    # Create directory if not exists
    os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)
    
    if os.path.exists(OUTPUT_CSV_PATH):
        df_existing = pd.read_csv(OUTPUT_CSV_PATH)
    else:
        df_existing = pd.DataFrame()
    
    df_new = pd.DataFrame(data_list)
    # Deduplication based on order_number (or any unique field)
    if not df_existing.empty:
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.drop_duplicates(subset=["order_number"], keep='last', inplace=True)
    else:
        df_combined = df_new
    
    df_combined.to_csv(OUTPUT_CSV_PATH, index=False)
    logger.info(f"Data saved to {OUTPUT_CSV_PATH}")
