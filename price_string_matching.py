
import re
import pandas as pd


def get_units():
    df_units = pd.read_csv("files/units_dictionary.csv", header=0)
    units = df_units['units'].values
    return units


# Prices
DOLLAR_PRICE_PER_UNIT = re.compile(r'\$([0-9]+)/(' + '|'.join(get_units()) + r')')  # $99/lb
CENT_PRICE_PER_UNIT = re.compile(r'([0-9]+)¢/(' + '|'.join(get_units()) + r')')

UNITS_PER_DOLLAR_PRICE = re.compile(r'([0-9]+)/\$([0-9]+)')  # 3/$1
UNITS_PER_CENT_PRICE = re.compile(r'([0-9]+)/([0-9]+)¢')

DOLLAR_PRICE = re.compile(r'\$([0-9]+)')  # $1
CENT_PRICE = re.compile(r'([0-9]+)¢')


# TODO: All of these per unit
# Savings in red
BUY_ONE_GET_ONE_FREE = re.compile(r'FREE')
HALF_OFF = re.compile(r'HALF\sOFF')
PERCENTAGE_OFF = re.compile(r'([0-9]+)%\sOFF')


# Savings
DOLLAR_OFF_PER_POUND = re.compile(r'\$([0-9]+)\sOFF\sPER\sPOUND')
CENT_OFF_PER_POUND = re.compile(r'([0-9]+)¢\sOFF\sPER\sPOUND')

SAVE_CENTS_ON = re.compile(r'SAVE ([0-9]+)¢ on ([0-9]+)')  # SAVE 98¢ on 2
SAVE_DOLLARS_ON = re.compile(r'SAVE \$([0-9]+) on ([0-9]+)')

SAVE_CENTS_UP_TO_ON = re.compile(r'SAVE up to ([0-9]+)¢ on ([0-9]+)')  # SAVE up to 98¢ on 2
SAVE_DOLLARS_UP_TO_ON = re.compile(r'SAVE up to \$([0-9]+)¢ on ([0-9]+)')

SAVE_CENTS_UP_TO = re.compile(r'SAVE up to ([0-9]+)¢')  # SAVE up to 98¢
SAVE_DOLLARS_UP_TO = re.compile(r'SAVE up to \$([0-9]+)')

DOLLAR_SAVE = re.compile(r'SAVE.{0,7}\$([0-9]+)')
CENT_SAVE = re.compile(r'SAVE.{0,7}([0-9]+)¢')

DOLLAR_OFF = re.compile(r'\$([0-9]+)\sOFF')
CENT_OFF = re.compile(r'([0-9]+)¢\sOFF')


def match_price_in_block(text, ad):
    match = DOLLAR_PRICE_PER_UNIT.match(text, re.IGNORECASE)
    if match:
        ad.uom = match.group(0)