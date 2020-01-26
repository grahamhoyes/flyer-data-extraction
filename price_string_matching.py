import re
import pandas as pd
from ad_block import AdBlock


def get_units():
    df_units = pd.read_csv("files/units_dictionary.csv", header=0)
    units = df_units["units"].values
    return units


# Prices
DOLLAR_PRICE_PER_UNIT = re.compile(
    r"\$([0-9]+)/(" + "|".join(get_units()) + r")"
)  # $199/lb
CENT_PRICE_PER_UNIT = re.compile(r"([0-9]+)¢/(" + "|".join(get_units()) + r")")

UNITS_PER_DOLLAR_PRICE = re.compile(r"([0-9]+)/\$([0-9]+)")  # 3/$1
UNITS_PER_CENT_PRICE = re.compile(r"([0-9]+)/([0-9]+)¢")

DOLLAR_PRICE = re.compile(r"\$([0-9]+)")  # $1
CENT_PRICE = re.compile(r"([0-9]+)¢")


# TODO: All of these per unit
# Savings in red
BUY_ONE_GET_ONE_FREE = re.compile(r"BUY\sONE,*\sGET\sONE\sFREE")
HALF_OFF = re.compile(r"HALF\sOFF")
PERCENTAGE_OFF = re.compile(r"([0-9]+)%\sOFF")

DOLLAR_OFF_PER_POUND = re.compile(r"\$([0-9]+)\sOFF\sPER\sPOUND")
CENT_OFF_PER_POUND = re.compile(r"([0-9]+)¢\sOFF\sPER\sPOUND")

DOLLAR_OFF = re.compile(r"\$([0-9]+)\sOFF")
CENT_OFF = re.compile(r"([0-9]+)¢\sOFF")


# Savings
SAVE_CENTS_ON_PER_UNIT = re.compile(r"SAVE.{0,7}([0-9]+)¢/(" + "|".join(get_units()) + r") on ([0-9]+)")  # SAVE (up to) 98¢ on 2/lb
SAVE_DOLLARS_ON_PER_UNIT = re.compile(r"SAVE.{0,7}\$([0-9]+)/(" + "|".join(get_units()) + r") on ([0-9]+)")

DOLLAR_SAVE_PER_UNIT = re.compile(r"SAVE.{0,7}\$([0-9]+)/(" + "|".join(get_units()) + r")")
CENT_SAVE_PER_UNIT = re.compile(r"SAVE.{0,7}([0-9]+)¢/(" + "|".join(get_units()) + r")")

SAVE_CENTS_ON = re.compile(r"SAVE.{0,7}([0-9]+)¢ on ([0-9]+)")  # SAVE (up to) 98¢ on 2
SAVE_DOLLARS_ON = re.compile(r"SAVE.{0,7}\$([0-9]+) on ([0-9]+)")

DOLLAR_SAVE = re.compile(r"SAVE.{0,7}\$([0-9]+)")
CENT_SAVE = re.compile(r"SAVE.{0,7}([0-9]+)¢")


def match_price_in_block(text, ad: AdBlock):
    """
    Yes, there is a more efficient way to write this. I lack the time to figure it out.
    :param text:
    :param ad:
    :return:
    """
    # Prices
    dppu_match = DOLLAR_PRICE_PER_UNIT.match(text, re.IGNORECASE)
    cppu_match = CENT_PRICE_PER_UNIT.match(text, re.IGNORECASE)
    updp_match = UNITS_PER_DOLLAR_PRICE.match(text, re.IGNORECASE)
    upcp_match = UNITS_PER_CENT_PRICE.match(text, re.IGNORECASE)
    dp_match = DOLLAR_PRICE.match(text, re.IGNORECASE)
    cp_match = CENT_PRICE.match(text, re.IGNORECASE)
    bogo_match = BUY_ONE_GET_ONE_FREE.match(text, re.IGNORECASE)
    ho_match = HALF_OFF.match(text, re.IGNORECASE)
    po_match = PERCENTAGE_OFF.match(text, re.IGNORECASE)
    dopp_match = DOLLAR_OFF_PER_POUND.match(text, re.IGNORECASE)
    copp_match = CENT_OFF_PER_POUND.match(text, re.IGNORECASE)
    do_match = DOLLAR_OFF.match(text, re.IGNORECASE)
    co_match = CENT_OFF.match(text, re.IGNORECASE)

    if dppu_match:
        ad.set_dollar_price_per_unit(dppu_match.group(1), dppu_match.group(2), False)
    elif cppu_match:
        ad.set_dollar_price_per_unit(cppu_match.group(1), dppu_match.group(2), True)
    elif updp_match:
        ad.set_units_per_price(updp_match.group(1), updp_match.group(2), False)
    elif upcp_match:
        ad.set_units_per_price(upcp_match.group(1), updp_match.group(2), True)
    elif bogo_match:
        ad.set_buy_get_one_free()
    elif ho_match:
        ad.set_half_off()
    elif po_match:
        ad.set_percentage_off(po_match.group(1))
    elif dopp_match:
        ad.set_dollar_off_per_pound(dopp_match.group(1), False)
    elif copp_match:
        ad.set_dollar_off_per_pound(copp_match.group(1), True)
    elif do_match:
        ad.set_dollar_off(do_match.group(1), False)
    elif co_match:
        ad.set_dollar_off(co_match.group(1), True)
    elif dp_match:
        ad.set_dollar_price(dp_match.group(1), False)
    elif cp_match:
        ad.set_dollar_price(cp_match.group(1), True)

    # Savings
    sdopu_match = SAVE_DOLLARS_ON_PER_UNIT.match(text, re.IGNORECASE)
    scopu_match = SAVE_CENTS_ON_PER_UNIT.match(text, re.IGNORECASE)
    dspu_match = DOLLAR_SAVE_PER_UNIT.match(text, re.IGNORECASE)
    cspu_match = CENT_SAVE_PER_UNIT.match(text, re.IGNORECASE)
    sdo_match = SAVE_DOLLARS_ON.match(text, re.IGNORECASE)
    sco_match = SAVE_CENTS_ON.match(text, re.IGNORECASE)
    ds_match = DOLLAR_SAVE.match(text, re.IGNORECASE)
    cs_match = CENT_SAVE.match(text, re.IGNORECASE)

    if sdopu_match:
        ad.set_save_dollars_per_unit_on_units(sdopu_match.group(1), sdopu_match.group(2), sdopu_match.group(3), False)
    elif scopu_match:
        ad.set_save_dollars_per_unit_on_units(scopu_match.group(1), scopu_match.group(2), scopu_match.group(3), True)
    elif dspu_match:
        ad.set_save_dollars_per_unit(dspu_match.group(1), dspu_match.group(2), False)
    elif cspu_match:
        ad.set_save_dollars_per_unit(cspu_match.group(1), cspu_match.group(2), True)
    elif sdo_match:
        ad.set_save_dollars_on_units(sdo_match.group(1), sdo_match.group(2), False)
    elif sco_match:
        ad.set_save_dollars_on_units(sco_match.group(1), sco_match.group(2), True)
    elif ds_match:
        ad.set_save_dollars(ds_match.group(1), False)
    elif cs_match:
        ad.set_save_dollars(cs_match.group(1), True)
