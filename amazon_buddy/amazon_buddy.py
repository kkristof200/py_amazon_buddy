# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from typing import Optional, Union, List, Dict, Any, Union
import urllib.parse
import os

# Local
from .enums.category import Category
from .enums.sort_type import SortType
from .enums.product_condition import ProductCondition

from .models.product import *
from .models.review import Review

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# --------------------------------------------------------------- Constants -------------------------------------------------------------- #

LIMIT_MAX_PRODUCTS = 1000
LIMIT_MAX_REVIEWS  = 2000

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ---------------------------------------------------------- class: AmazonBuddy ---------------------------------------------------------- #

class AmazonBuddy:

    # -------------------------------------------------------- Public methods -------------------------------------------------------- #

    @classmethod
    def search_products(
        cls,

        # url
        search_term: str,
        category: Category = Category.ALL_DEPARTMENTS,
        sort_type: Optional[SortType] = None,

        # rh
        min_rating: Optional[float] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        product_condition: Optional[ProductCondition] = None,
        include_unavailable: Optional[bool] = None,

        # other js params
        max_results: int = 100,
        user_agent: Optional[str] = None,
        random_ua: bool = True,
        sort: bool = True,
        min_reviews: Optional[int] = 3,
        ignored_asins: List[str] = [],
        proxies: Optional[List[str]] = None,

        # post_scrape_filter
        ignored_title_strs: List[str] = [],

        # other
        debug: bool = False
    ) -> Optional[List[Union[Dict, Product]]]:
        products = cls.__exec_cmd(
            'products',
            user_agent=user_agent,
            random_ua=random_ua,
            extra_params={
                '-k': '\'' + search_term + '\'',
                '-c': category.value,
                '-n': max_results if max_results <= LIMIT_MAX_PRODUCTS else LIMIT_MAX_PRODUCTS,
                '--productsorttype': sort_type.value if sort_type else None,
                '--minPrice': min_price,
                '--maxPrice': max_price,
                '--minReviewCount': min_reviews,
                '--ignoredAsins': ','.join(ignored_asins) if ignored_asins and len(ignored_asins) > 0 else None,
                '--rh': cls.__create_rh(min_rating=min_rating, min_price=min_price, max_price=max_price, product_condition=product_condition, include_unavailable=include_unavailable),
                '--sort': sort
            },
            proxies=proxies,
            debug=debug
        )

        if products is None:
            return None

        filtered_products = []

        for product in products:
            try:
                from kcu import strings

                product = Product(product)

                if (cls.__contains_in(product.title, ignored_title_strs)):
                    continue

                filtered_products.append(product)
            except:
                pass

        return filtered_products

    @classmethod
    def get_reviews(
        cls,
        asin: str,
        min_rating: float = 0.0,
        max_results: int = 100,
        user_agent: Optional[str] = None,
        random_ua: bool = True,
        sort: bool = True,
        proxies: Optional[List[str]] = None,
        debug: bool = False
    ) -> Optional[List[Review]]:
        js = cls.__exec_cmd(
            'reviews ' + asin,
            user_agent=user_agent,
            random_ua=random_ua,
            extra_params={
                '-n': max_results if max_results <= LIMIT_MAX_REVIEWS else LIMIT_MAX_REVIEWS,
                '--min-rating': min_rating,
                '--sort': sort
            },
            proxies=proxies,
            debug=debug
        )

        if js:
            return [Review(j) for j in js]

        return None

    @classmethod
    def get_product_details(
        cls,
        asin: str,
        user_agent: Optional[str] = None,
        random_ua: bool = True,
        proxies: Optional[List[str]] = None,
        debug: bool = False
    ) -> Optional[Dict]:
        return cls.__exec_cmd(
            'asin ' + asin,
            user_agent=user_agent,
            random_ua=random_ua,
            proxies=proxies,
            debug=debug
        )


    # ------------------------------------------------------- Private methods -------------------------------------------------------- #

    @classmethod
    def __create_rh(
        cls,
        min_rating: Optional[float] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        product_condition: Optional[ProductCondition] = None,
        include_unavailable: Optional[bool] = None
    ) -> Optional[str]:
        rh_rating = cls.__create_min_rating_rh(min_rating)
        rh_price = cls.__create_price_rh(min_price, max_price)
        rh_product_condition = cls.__create_condition_rh(product_condition)
        rh_include_unavailable = cls.__create_include_unavailable_rh(include_unavailable)

        rhs = []

        if rh_rating:
            rhs.append('p_72:' + rh_rating)

        if rh_price:
            rhs.append('p_36:' + rh_price)

        if rh_product_condition:
            rhs.append('p_n_condition-type:' + rh_product_condition)

        if rh_include_unavailable:
            rhs.append('p_n_availability:' + rh_include_unavailable)

        return urllib.parse.quote(','.join(rhs)) if len(rhs) > 0 else None

    @staticmethod
    def __create_min_rating_rh(min_rating: Optional[float] = None) -> Optional[str]:
        if min_rating:
            if 1 < min_rating:
                if min_rating > 4:
                    min_rating = 4

                return '124891' + str(9-min_rating) + '011'

        return None
    
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

    @classmethod
    def __exec_cmd(
        cls,
        feature: str,
        user_agent: Optional[str] = None,
        random_ua: bool = True,
        proxies: Optional[List[str]] = None,
        extra_params: Optional[Dict[str, Any]] = None,
        debug: bool = False
    ) -> Optional[Union[List, Dict]]:
        params = extra_params or {}
        params['proxy'] = ','.join(proxies) if proxies and len(proxies) > 0 else None

        if user_agent:
            params['--ua'] = user_agent
        elif random_ua:
            from fake_useragent import FakeUserAgent

            params['--ua'] = FakeUserAgent().random

        params['--filetype'] = 'json'

        from kcu import sh, kjson, kpath

        resp = sh.sh(
            cls.__create_cmd(feature, params),
            debug=debug
        ).strip()

        try:
            path = resp.split('\'')[1].split('\'')[0]
        except Exception as e:
            print(e)

            return None

        if not os.path.exists(path):
            return None

        j = kjson.load(path)
        os.remove(path)

        return j
    
    @staticmethod
    def __create_cmd(feature: str, params: Dict[str, Any]) -> str:
        cmd = 'amazon-buddy' + ' ' + feature

        for k, v in params.items():
            if not v:
                continue

            if k == '--ua':
                v = '\'' + v.replace('\'', '\\\'') + '\''
            if isinstance(v, bool):
                v = str(v).lower()

            cmd += ' ' + k + ' ' + str(v)
        
        return cmd

    @staticmethod
    def __contains(s: str, strs: List[str]) -> bool:
        s = s.lower()

        for ss in strs:
            if s == ss:
                return True

        return False

    @staticmethod
    def __contains_in(s: str, strs: List[str]) -> bool:
        s = s.lower()

        for ss in strs:
            if ss in s:
                return True

        return False


# ---------------------------------------------------------------------------------------------------------------------------------------- #