import locale
from datetime import datetime


def convert_month_str_to_int(month_str: str, _locale: str = "pt_BR.UTF-8") -> int:
    # ex. "junho" -> "06"
    locale.setlocale(locale.LC_TIME, _locale)
    month_value = datetime.strptime(month_str, "%B").strftime("%m")
    return int(month_value)


def convert_brl_str_to_float(brl_str):
    # ex. "R$ 1.000,00" -> 1000.0
    formatted_str = brl_str.replace("R$", "").replace(".", "").replace(",", ".")
    return float(formatted_str)
