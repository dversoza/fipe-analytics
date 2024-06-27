from providers.fipe.utils import convert_brl_str_to_float, convert_month_str_to_int


def test_parses_pt_bt_month_names_into_int():
    assert convert_month_str_to_int("janeiro") == 1
    assert convert_month_str_to_int("fevereiro") == 2
    assert convert_month_str_to_int("março") == 3
    assert convert_month_str_to_int("abril") == 4
    assert convert_month_str_to_int("maio") == 5
    assert convert_month_str_to_int("junho") == 6
    assert convert_month_str_to_int("julho") == 7
    assert convert_month_str_to_int("agosto") == 8
    assert convert_month_str_to_int("setembro") == 9
    assert convert_month_str_to_int("outubro") == 10
    assert convert_month_str_to_int("novembro") == 11
    assert convert_month_str_to_int("dezembro") == 12


def test_parses_pt_br_price_into_float():
    assert str(convert_brl_str_to_float("R$ 1.000,00")) == str(1000.0)
    assert str(convert_brl_str_to_float("R$ 1.000,50")) == str(1000.5)
    assert str(convert_brl_str_to_float("R$ 1.000,99")) == str(1000.99)
    assert str(convert_brl_str_to_float("R$ 1.000")) == str(1000.0)
    assert str(convert_brl_str_to_float("R$ 1")) == str(1.0)
    assert str(convert_brl_str_to_float("R$ 1,50")) == str(1.5)
