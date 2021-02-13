# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
import urllib.parse
from typing import Optional

# Local
from .models import ProductCondition

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------------- class: Rh --------------------------------------------------------------- #

class RH:

    # -------------------------------------------------------- Public methods -------------------------------------------------------- #

    @classmethod
    def create_rh(
        cls,
        # min_rating: Optional[float] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        product_condition: Optional[ProductCondition] = None,
        include_unavailable: Optional[bool] = None
    ) -> Optional[str]:
        # rh_rating = cls.__create_min_rating_rh(min_rating)
        rh_price = cls.__create_price_rh(min_price, max_price)
        rh_product_condition = cls.__create_condition_rh(product_condition)
        rh_include_unavailable = cls.__create_include_unavailable_rh(include_unavailable)

        rhs = []

        # if rh_rating:
        #     rhs.append('p_72:' + rh_rating)

        if rh_price:
            rhs.append('p_36:' + rh_price)

        if rh_product_condition:
            rhs.append('p_n_condition-type:' + rh_product_condition)

        if rh_include_unavailable:
            rhs.append('p_n_availability:' + rh_include_unavailable)

        return urllib.parse.quote(','.join(rhs)) if len(rhs) > 0 else None


    # ------------------------------------------------------- Private methods -------------------------------------------------------- #

    # @staticmethod
    # def __create_min_rating_rh(min_rating: Optional[float] = None) -> Optional[str]:
    #     if min_rating:
    #         if 1 < min_rating:
    #             if min_rating > 4:
    #                 min_rating = 4

    #             return '124891' + str(9-int(min_rating)) + '011'

    #     return None

    @staticmethod
    def __create_price_rh(
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> Optional[str]:
        rh = ''

        if min_price and min_price > 0:
            rh += str(int(min_price * 100)) + '-'

        if max_price and max_price > 0 and (not min_price or min_price < max_price):
            if len(rh) == 0:
                rh = '-'

            rh += str(int(max_price * 100))

        return rh if len(rh) > 0 else None

    @staticmethod
    def __create_condition_rh(product_condition: Optional[ProductCondition] = None) -> Optional[str]:
        return str(product_condition.value) if product_condition else None

    @staticmethod
    def __create_include_unavailable_rh(include_unavailable: Optional[bool] = None) -> Optional[str]:
        return '1248816011' if include_unavailable else None


# ---------------------------------------------------------------------------------------------------------------------------------------- #