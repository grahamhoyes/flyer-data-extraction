
import re
import pandas as pd


def get_units():
    df_units = pd.read_csv("files/units_dictionary.csv", header=0)
    units = df_units['units'].values
    return units


DOLLAR_PRICE_PER_UNIT = re.compile(r'\$([0-9]+)/(' + '|'.join(get_units()) + r')')
CENT_PRICE_PER_UNIT = re.compile(r'([0-9]+)¢/(' + '|'.join(get_units()) + r')')

UNITS_PER_DOLLAR_PRICE = re.compile(r'([0-9]+)/\$([0-9]+)')
UNITS_PER_CENT_PRICE = re.compile(r'([0-9]+)/([0-9]+)¢')

BUY_ONE_GET_ONE_FREE = re.compile(r'FREE')
HALF_OFF = re.compile(r'HALF\sOFF!')
PERCENTAGE_OFF = re.compile(r'([0-9]+)%\sOFF')

DOLLAR_PRICE = re.compile(r'\$([0-9]+)')
CENT_PRICE = re.compile(r'([0-9]+)¢')

DOLLAR_OFF = re.compile(r'\$([0-9]+)\sOFF')
CENT_OFF = re.compile(r'([0-9]+)¢\sOFF')

DOLLAR_OFF_PER_POUND = re.compile(r'\$([0-9]+)\sOFF\sPER\sPOUND')
CENT_OFF_PER_POUND = re.compile(r'([0-9]+)¢\sOFF\sPER\sPOUND')

