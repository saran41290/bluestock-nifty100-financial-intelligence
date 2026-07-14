import pandas as pd
# Helper

def _to_number(value):

    if pd.isna(value):
        return None

    try:
        return float(str(value).replace(",", "").strip())

    except Exception:
        return None
    
    

