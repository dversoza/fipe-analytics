from providers.fipe.api import _mes_str_to_int, _price_str_to_float


def test_parses_pt_bt_month_names_into_int():
    assert _mes_str_to_int("janeiro") == "01"
    assert _mes_str_to_int("fevereiro") == "02"
    assert _mes_str_to_int("março") == "03"
    assert _mes_str_to_int("abril") == "04"
    assert _mes_str_to_int("maio") == "05"
    assert _mes_str_to_int("junho") == "06"
    assert _mes_str_to_int("julho") == "07"
    assert _mes_str_to_int("agosto") == "08"
    assert _mes_str_to_int("setembro") == "09"
    assert _mes_str_to_int("outubro") == "10"
    assert _mes_str_to_int("novembro") == "11"
    assert _mes_str_to_int("dezembro") == "12"


def test_parses_pt_br_price_into_float():
    assert _price_str_to_float("R$ 1.000,00") == 1000.0
    assert _price_str_to_float("R$ 1.000,50") == 1000.5
    assert _price_str_to_float("R$ 1.000,99") == 1000.99
    assert _price_str_to_float("R$ 1.000") == 1000.0
    assert _price_str_to_float("R$ 1.000,") == 1000.0
