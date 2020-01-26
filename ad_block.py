class AdBlock:

    def __init__(self, flyer_name, product_name):
        self.flyer_name = flyer_name
        self.product_name = product_name
        self.unit_promo_price = None
        self.uom = None
        self.least_unit_for_promo = 1
        self.save_per_unit = None
        self.discount = None
        self.organic = 1 if "organic" in product_name.lower() else 0

        self.dollar_off = None

        self.is_buy_one_get_one_free = False
        self.is_half_off = False
        self.is_percentage_off = False

    def convert_to_dollars(self, price, is_cents):
        price = float(price)
        if is_cents:
            price /= 100
        elif price > 10:
            price /= 100
        return price

    def set_dollar_price_per_unit(self, price, unit, is_cents):
        self.unit_promo_price = self.convert_to_dollars(price, is_cents)
        self.uom = unit

    def set_units_per_price(self, units, price, is_cents):
        units = int(units)
        price = self.convert_to_dollars(price, is_cents)
        self.unit_promo_price = price / units
        self.least_unit_for_promo = units

    def set_dollar_price(self, price, is_cents):
        self.unit_promo_price = self.convert_to_dollars(price, is_cents)

    def set_buy_get_one_free(self):
        self.least_unit_for_promo = 2
        self.is_buy_one_get_one_free = True

    def set_half_off(self):
        self.is_half_off = True

    def set_percentage_off(self, discount):
        if self.is_percentage_off is True:
            self.discount += discount
            return
        self.is_percentage_off = True
        self.discount = float(discount)/100

    def set_dollar_off(self, dollar_off, is_cents):
        self.save_per_unit = self.convert_to_dollars(dollar_off, is_cents)

    def set_dollar_off_per_pound(self, dollar_off, is_cents):
        self.uom = 'lb'
        self.save_per_unit = self.convert_to_dollars(dollar_off, is_cents)

    def set_save_dollars_on_units(self, savings, units, is_cents):
        self.save_per_unit = self.convert_to_dollars(savings, is_cents)
        self.least_unit_for_promo = int(units)

    def set_save_dollars_per_unit_on_units(self, savings, per_unit, units, is_cents):
        self.save_per_unit = self.convert_to_dollars(savings, is_cents)
        self.least_unit_for_promo = int(units)
        self.uom = per_unit

    def set_save_dollars(self, savings, is_cents):
        self.save_per_unit = self.convert_to_dollars(savings, is_cents)

    def set_save_dollars_per_unit(self, savings, unit, is_cents):
        self.save_per_unit = self.convert_to_dollars(savings, is_cents)
        self.uom = unit

    def set_units(self, unit):
        self.uom = unit

    def combine_information(self):

        if self.is_buy_one_get_one_free or self.is_half_off:
            self.discount = 0.5
            if self.unit_promo_price is not None:
                self.save_per_unit = self.unit_promo_price
            if self.save_per_unit is not None:
                self.unit_promo_price = self.save_per_unit

        try:
            self.discount = self.save_per_unit / (self.unit_promo_price + self.save_per_unit)
        except:
            pass

        if self.unit_promo_price and isinstance(self.unit_promo_price, float):
            self.unit_promo_price = "{0:.2f}".format(self.unit_promo_price)

        if self.save_per_unit and isinstance(self.save_per_unit, float):
            self.save_per_unit = "{0:.2f}".format(self.save_per_unit)

        if self.discount and isinstance(self.discount, float):
            self.discount = "{0:.2f}".format(self.discount)

    def get_row(self):
        return [
            self.flyer_name,
            self.product_name,
            self.unit_promo_price,
            self.uom,
            self.least_unit_for_promo,
            self.save_per_unit,
            self.discount,
            self.organic
        ]
