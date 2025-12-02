import re


def reformat_date(date_str):
    day, month, year = date_str.split('.')
    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"


def is_valid_date(date_str):
    pattern = r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.(20[0-9][0-9]|21[0-9][0-9])$"
    if re.match(pattern, date_str):
        return True
    else:
        return False
