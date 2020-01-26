class AdBlock:

    def __init__(self, flyer_name, product_name):
        self.flyer_name = flyer_name
        self.product_name = product_name
        self.unit_promo_price = ""
        self.uom = ""
        self.least_unit_for_promo = ""
        self.save_per_unit = ""
        self.discount = ""
        self.organic = ""

    def set_dollar_price_per_unit(self, price, unit):
        self.unit_promo_price = price
        self.uom = unit

    def set_units_per_price(self, units, price):
        pass

    def set_buy_get_one_free(self):
        pass

    def set_half_off(self):
        pass

    def set_percentage_off(self):
        pass

    def set_dollar_price(self, price):
        pass

    def set_dollar_off(self, dollar_off):
        pass

    def set_dollar_off_per_pound(self, dollar_off):
        pass
