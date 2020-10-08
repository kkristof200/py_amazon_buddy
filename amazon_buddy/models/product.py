# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# Pip
from jsoncodable import JSONCodable

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------------ class: Product ------------------------------------------------------------ #

class Product(JSONCodable):

    # ------------------------------------------------------------- Init ------------------------------------------------------------- #

    def __init__(
        self,
        dict_: dict
    ):
        self.asin = dict_['asin']
        self.url = dict_['url']
        self.score = float(dict_['score'])
        self.sponsored = dict_['sponsored']
        self.amazonChoice = dict_['amazonChoice']
        self.bestSeller = dict_['bestSeller']
        self.amazonPrime = dict_['amazonPrime']
        self.title = dict_['title']
        self.thumbnail = dict_['thumbnail']

        self.position = ProductPosition(dict_['position'])
        self.price = ProductPrice(dict_['price'])
        self.rating = ProductRating(dict_['reviews'])


# ---------------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------- class: ProductPosition -------------------------------------------------------- #

class ProductPosition(JSONCodable):

    # ------------------------------------------------------------- Init ------------------------------------------------------------- #

    def __init__(
        self,
        dict_: dict
    ):
        self.page = dict_['page']
        self.position = dict_['position']
        self.global_position = dict_['global_position']


# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ---------------------------------------------------------- class: ProductPrice --------------------------------------------------------- #

class ProductPrice(JSONCodable):

    # ------------------------------------------------------------- Init ------------------------------------------------------------- #

    def __init__(
        self,
        dict_: dict
    ):
        self.current = dict_['current_price']
        self.full = dict_['before_price']
        self.currency = dict_['currency']
        self.discounted = dict_['discounted']
        self.savings_amount = dict_['savings_amount']
        self.savings_percent = dict_['savings_percent']


# ---------------------------------------------------------------------------------------------------------------------------------------- #



# --------------------------------------------------------- class: ProductRating --------------------------------------------------------- #

class ProductRating(JSONCodable):

    # ------------------------------------------------------------- Init ------------------------------------------------------------- #

    def __init__(
        self,
        dict_: dict
    ):
        self.value = dict_['rating']
        self.count = dict_['total_reviews']


# ---------------------------------------------------------------------------------------------------------------------------------------- #