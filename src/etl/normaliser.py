import re


def normalize_ticker(ticker: str) -> str:
    """
    Normalize NSE ticker symbols.
    """

    if ticker is None:
        return ""

    return str(ticker).strip().upper()


def normalize_year(year: str) -> str:
    """
    Convert financial year formats into YYYY-MM.
    """

    if year is None:
        return ""

    year = str(year).strip()

    # Mar-24 -> 2024-03
    match = re.match(r"([A-Za-z]{3})-(\d{2})", year)

    if match:
        month = match.group(1)
        yr = int(match.group(2))

        if yr >= 90:
            year_num = 1900 + yr
        else:
            year_num = 2000 + yr

        months = {
            "Jan": "01",
            "Feb": "02",
            "Mar": "03",
            "Apr": "04",
            "May": "05",
            "Jun": "06",
            "Jul": "07",
            "Aug": "08",
            "Sep": "09",
            "Oct": "10",
            "Nov": "11",
            "Dec": "12",
        }

        return f"{year_num}-{months[month]}"

    return year