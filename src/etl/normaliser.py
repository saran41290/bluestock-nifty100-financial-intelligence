import re


def normalize_ticker(ticker: str) -> str:
    """Normalize NSE ticker symbols."""
    if ticker is None:
        return ""
    return str(ticker).strip().upper()


def normalize_year(year: str) -> str:
    """Convert financial year formats into YYYY-MM."""
    if year is None:
        return ""
    year_str = str(year).strip()
    if not year_str:
        return ""

    # Already YYYY-MM
    if re.match(r"^\d{4}-\d{2}$", year_str):
        return year_str

    # FY23 / FY2023
    match_fy = re.match(r"^FY\s*(\d{2,4})$", year_str, re.IGNORECASE)
    if match_fy:
        yr_val = match_fy.group(1)
        yr_num = (2000 + int(yr_val)) if len(yr_val) == 2 else int(yr_val)
        return f"{yr_num}-03"

    # 2023 (4-digit year) -> 2023-03
    if re.match(r"^\d{4}$", year_str):
        return f"{year_str}-03"

    # March-2023 / March 2023
    months_full = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12"
    }
    match_full = re.match(r"^([A-Za-z]+)[\s\-]+(\d{4})$", year_str)
    if match_full:
        m_name = match_full.group(1).lower()
        yr_num = match_full.group(2)
        if m_name in months_full:
            return f"{yr_num}-{months_full[m_name]}"

    # Mar-23 / Mar 23 / Mar-2023
    match_short = re.match(r"^([A-Za-z]{3})[\s\-]+(\d{2,4})$", year_str)
    if match_short:
        m_name = match_short.group(1).title()
        yr_val = match_short.group(2)
        if len(yr_val) == 2:
            yr = int(yr_val)
            yr_num = 1900 + yr if yr >= 90 else 2000 + yr
        else:
            yr_num = int(yr_val)

        months = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
            "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
            "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
        }
        if m_name in months:
            return f"{yr_num}-{months[m_name]}"

    return "PARSE_ERROR"