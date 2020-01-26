import re
import pandas as pd
from ad_block import AdBlock


def get_units():
    df_units = pd.read_csv("files/units_dictionary.csv", header=0)
    units = df_units["units"].values
    return units


# Units
LONE_UNITS = re.compile(r"((?:[0-9]+)\s(?:" + "|".join(get_units()) + r"))")

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
RECEIVE_AN_EXTRA_PERCENTAGE_OFF = re.compile(r"RECEIVE\sAN\sEXTRA\s([0-9]+)%\sOFF")

DOLLAR_OFF_PER_POUND = re.compile(r"\$([0-9]+)\sOFF\sPER\sPOUND")
CENT_OFF_PER_POUND = re.compile(r"([0-9]+)¢\sOFF\sPER\sPOUND")

DOLLAR_OFF = re.compile(r"\$([0-9]+)\sOFF")
CENT_OFF = re.compile(r"([0-9]+)¢\sOFF")


# Savings
SAVE_CENTS_ON_PER_UNIT = re.compile(
    r"SAVE.{0,7}([0-9]+)¢/(" + "|".join(get_units()) + r")\son\s([0-9]+)"
)  # SAVE (up to) 98¢ on 2/lb
SAVE_DOLLARS_ON_PER_UNIT = re.compile(
    r"SAVE.{0,7}\$([0-9]+)/(" + "|".join(get_units()) + r")\son\s([0-9]+)"
)

DOLLAR_SAVE_PER_UNIT = re.compile(
    r"SAVE.{0,7}\$([0-9]+)/(" + "|".join(get_units()) + r")"
)
CENT_SAVE_PER_UNIT = re.compile(r"SAVE.{0,7}([0-9]+)¢/(" + "|".join(get_units()) + r")")

SAVE_CENTS_ON = re.compile(
    r"SAVE.{0,7}([0-9]+)¢\son\s([0-9]+)"
)  # SAVE (up to) 98¢ on 2
SAVE_DOLLARS_ON = re.compile(r"SAVE.{0,7}\$([0-9]+)\son\s([0-9]+)")

DOLLAR_SAVE = re.compile(r"SAVE.{0,7}\$([0-9]+)")
CENT_SAVE = re.compile(r"SAVE.{0,7}([0-9]+)¢")


def _is_within_spans(x, spans):
    for span in spans:
        if x[0] >= span[0] and x[1] <= span[1]:
            return True

    return False


def match_price_in_block(text, ad: AdBlock):
    """
    Yes, there is a more efficient way to write this. I lack the time to figure it out.
    :param text:
    :param ad:
    :return:
    """
    found_some_price_thing = True
    do_first_catchall = do_second_catchall = False

    # Savings
    sdopu_match = SAVE_DOLLARS_ON_PER_UNIT.search(text)
    scopu_match = SAVE_CENTS_ON_PER_UNIT.search(text)
    dspu_match = DOLLAR_SAVE_PER_UNIT.search(text)
    cspu_match = CENT_SAVE_PER_UNIT.search(text)
    sdo_match = SAVE_DOLLARS_ON.search(text)
    sco_match = SAVE_CENTS_ON.search(text)
    ds_match = DOLLAR_SAVE.search(text)
    cs_match = CENT_SAVE.search(text)

    savings_match_spans = []

    if sdopu_match:
        ad.set_save_dollars_per_unit_on_units(
            sdopu_match.group(1), sdopu_match.group(2), sdopu_match.group(3), False
        )
        savings_match_spans.append(sdopu_match.span(0))
    elif scopu_match:
        ad.set_save_dollars_per_unit_on_units(
            scopu_match.group(1), scopu_match.group(2), scopu_match.group(3), True
        )
        savings_match_spans.append(scopu_match.span(0))
    elif dspu_match:
        ad.set_save_dollars_per_unit(dspu_match.group(1), dspu_match.group(2), False)
        savings_match_spans.append(dspu_match.span(0))
    elif cspu_match:
        ad.set_save_dollars_per_unit(cspu_match.group(1), cspu_match.group(2), True)
        savings_match_spans.append(cspu_match.span(0))
    elif sdo_match:
        ad.set_save_dollars_on_units(sdo_match.group(1), sdo_match.group(2), False)
        savings_match_spans.append(sdo_match.span(0))
    elif sco_match:
        ad.set_save_dollars_on_units(sco_match.group(1), sco_match.group(2), True)
        savings_match_spans.append(sco_match.span(0))
    elif ds_match:
        ad.set_save_dollars(ds_match.group(1), False)
        savings_match_spans.append(ds_match.span(0))
    elif cs_match:
        ad.set_save_dollars(cs_match.group(1), True)
        savings_match_spans.append(cs_match.span(0))
    else:
        do_first_catchall = True

    # Prices
    dppu_match = DOLLAR_PRICE_PER_UNIT.search(text)
    cppu_match = CENT_PRICE_PER_UNIT.search(text)
    updp_match = UNITS_PER_DOLLAR_PRICE.search(text)
    upcp_match = UNITS_PER_CENT_PRICE.search(text)
    dp_match = DOLLAR_PRICE.search(text)
    cp_match = CENT_PRICE.search(text)
    bogo_match = BUY_ONE_GET_ONE_FREE.search(text)
    ho_match = HALF_OFF.search(text)
    po_match = PERCENTAGE_OFF.search(text)
    dopp_match = DOLLAR_OFF_PER_POUND.search(text)
    copp_match = CENT_OFF_PER_POUND.search(text)
    do_match = DOLLAR_OFF.search(text)
    co_match = CENT_OFF.search(text)

    if dppu_match and not _is_within_spans(dppu_match.span(0), savings_match_spans):
        ad.set_dollar_price_per_unit(dppu_match.group(1), dppu_match.group(2), False)
    elif cppu_match and not _is_within_spans(cppu_match.span(0), savings_match_spans):
        ad.set_dollar_price_per_unit(cppu_match.group(1), cppu_match.group(2), True)
    elif updp_match and not _is_within_spans(updp_match.span(0), savings_match_spans):
        ad.set_units_per_price(updp_match.group(1), updp_match.group(2), False)
    elif upcp_match and not _is_within_spans(upcp_match.span(0), savings_match_spans):
        ad.set_units_per_price(upcp_match.group(1), upcp_match.group(2), True)
    elif bogo_match and not _is_within_spans(bogo_match.span(0), savings_match_spans):
        ad.set_buy_get_one_free()
    elif ho_match and not _is_within_spans(ho_match.span(0), savings_match_spans):
        ad.set_half_off()
    elif po_match and not _is_within_spans(po_match.span(0), savings_match_spans):
        ad.set_percentage_off(po_match.group(1))
    elif dopp_match and not _is_within_spans(dopp_match.span(0), savings_match_spans):
        ad.set_dollar_off_per_pound(dopp_match.group(1), False)
    elif copp_match and not _is_within_spans(copp_match.span(0), savings_match_spans):
        ad.set_dollar_off_per_pound(copp_match.group(1), True)
    elif do_match and not _is_within_spans(do_match.span(0), savings_match_spans):
        ad.set_dollar_off(do_match.group(1), False)
    elif co_match and not _is_within_spans(co_match.span(0), savings_match_spans):
        ad.set_dollar_off(co_match.group(1), True)
    else:
        do_second_catchall = True
        found_some_price_thing = False

    if do_first_catchall and do_second_catchall:
        if dp_match and not _is_within_spans(dp_match.span(0), savings_match_spans):
            ad.set_dollar_price(dp_match.group(1), False)
        elif cp_match and not _is_within_spans(cp_match.span(0), savings_match_spans):
            ad.set_dollar_price(cp_match.group(1), True)

    raedo_match = RECEIVE_AN_EXTRA_PERCENTAGE_OFF.search(text)

    if raedo_match:
        ad.set_percentage_off(raedo_match.group(1))

    if ad.uom is None:
        lone_unit_match = LONE_UNITS.search(text)
        if lone_unit_match:
            ad.uom = lone_unit_match.group(1)

    return found_some_price_thing
