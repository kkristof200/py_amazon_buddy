# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from typing import Optional, List, Dict, Callable, Union
import urllib.parse
import os, time

# Local
from .enums.category import Category
from .enums.sort_type import SortType

from .models.search_result_product import SearchResultProduct
from .models.product import Product
from .models.review import Review

from .filter import ProductFilter, ReviewFilter
from .parser import Parser
from .request import Request
from .rh import RH

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ---------------------------------------------------------- class: AmazonBuddy ---------------------------------------------------------- #

class AmazonBuddy:

    # -------------------------------------------------------- Public methods -------------------------------------------------------- #

    @classmethod
    def get_related_searches(
        cls,

        # url
        search_term: str,
        category: Optional[Union[Category, str]] = Category.ALL_DEPARTMENTS,

        # request
        proxy: Optional[str] = None,
        proxies: Optional[List[str]] = None,
        user_agent: Optional[str] = None,

        # other
        debug: bool = False
    ) -> List[str]:
        category = category or Category.ALL_DEPARTMENTS

        if type(category) == type(Category.ALL_DEPARTMENTS):
            category = category.value

        return cls.__get_related_searches(
            'https://www.amazon.com/s?k={}&i={}'.format(urllib.parse.quote(search_term), category),
            Request(user_agent, keep_cookies=True, proxy=proxy, proxies=proxies, debug=debug)
        )

    @classmethod
    def search_products(
        cls,

        # url
        search_term: str,
        category: Optional[Union[Category, str]] = Category.ALL_DEPARTMENTS,
        sort_type: Optional[SortType] = None,

        # # rh
        # product_condition: Optional[ProductCondition] = None,
        # include_unavailable: Optional[bool] = None,

        # filter
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        min_reviews: Optional[int] = 3,
        ignored_asins: List[str] = [],
        ignored_title_strs: List[str] = [],

        # request
        proxy: Optional[str] = None,
        proxies: Optional[List[str]] = None,
        user_agent: Optional[str] = None,

        # other
        max_results: int = 100,
        use_us_address: bool = True,
        debug: bool = False
    ) -> Optional[List[SearchResultProduct]]:
        category = category or Category.ALL_DEPARTMENTS

        if type(category) == type(Category.ALL_DEPARTMENTS):
            category = category.value

        base_url = 'https://www.amazon.com/s?k={}&i={}'.format(urllib.parse.quote(search_term), category)
        rh = RH.create_rh(min_price=min_price, max_price=max_price)
        request = Request(user_agent, keep_cookies=True, proxy=proxy, proxies=proxies, debug=debug)
        # cat_id, ratings = cls.__get_search_cat_and_ratings(search_term, request)
        suggested_rh = cls.__get_suggested_rh(base_url, min_rating, request)

        if suggested_rh:
            rh = suggested_rh + ('%2C' + rh) if rh else ''

        # if category == Category.ALL_DEPARTMENTS:
        #     # if cat_id:
        #     #     rh = 'n%3A' + cat_id + ('%2C' + rh if rh else '')
        #     pass
        # else:
        #     base_url += 'i={}'.format(urllib.parse.quote(category.value))
        
        if sort_type:
            base_url += '&s={}'.format(sort_type.value)

        if rh:
            base_url += '&rh={}'.format(rh)

        request = Request(user_agent, keep_cookies=True, debug=debug)

        if use_us_address:
            request.set_us_address()

        return cls.__solve(base_url, 'page', request, ProductFilter(min_price, max_price, min_rating, min_reviews, ignored_asins, ignored_title_strs), Parser.parse_products, max_results, debug=debug)

    @classmethod
    def get_reviews(
        cls,

        # url
        asin: str,

        # filter
        min_rating: float = 3.0,

        # request
        proxy: Optional[str] = None,
        proxies: Optional[List[str]] = None,
        user_agent: Optional[str] = None,

        # other
        max_results: int = 100,
        debug: bool = False
    ) -> Optional[List[Review]]:
        request = Request(user_agent, keep_cookies=True, proxy=proxy, proxies=proxies, debug=debug)
        request.get('https://www.amazon.com/dp/{}'.format(asin))
        base_url = 'https://www.amazon.com/product-reviews/{}?ie=UTF8&reviewerType=all_reviews&sortBy=helpful'.format(asin)

        return cls.__solve(base_url, 'pageNumber', request, ReviewFilter(min_rating), Parser.parse_reviews, max_results, debug=debug)


    # ------------------------------------------------------- Private methods -------------------------------------------------------- #

    @staticmethod
    def __solve(base_url: str, page_param_name: str, request: Request, filter, parse: Callable, max_results: int, debug: bool = False) -> List:
        p = 1
        l = []
        max_try = 3
        current_try = 1
        max_p = 50

        while len(l) < max_results and p <= max_p:
            url = base_url + '&{}={}'.format(page_param_name, p)
            request.debug = False
            new_elements = parse(request.get(url), debug=True)
            filtered = filter.filter(new_elements)
            l.extend(filtered)

            if debug:
                print('URL: {} - Found {}|{}|{} - Page {}'.format(url, len(new_elements), len(filtered), len(l), p), end='\n')

            if len(new_elements) < 7:
                if current_try >= max_try:
                    return l

                current_try += 1
                time.sleep(1)
                continue
            elif p > 25 and len(filtered) == 0:
                if current_try >= max_try:
                    return l

                current_try += 1
                p += 1
                time.sleep(1)
                continue

            p += 1
            current_try = 1

        print(' Found {} - Page {}'.format(len(l), p))

        return l if len(l) > 0 else None

    @staticmethod
    def __get_suggested_rh(url: str, min_rating: int, request: Request, max_try: int = 3) -> Optional[str]:
        current_try = 1

        while current_try <= max_try:
            rh = Parser.parse_suggested_rh(request.get(url), int(min_rating), debug=request.debug)

            if rh:
                return rh

            time.sleep(1)
            current_try += 1

        return None
    
    @staticmethod
    def __get_related_searches(url: str, request: Request, max_try: int = 3) -> List[str]:
        current_try = 1

        while current_try <= max_try:
            rh = Parser.parse_related_searches(request.get(url), debug=request.debug)

            if rh:
                return rh

            time.sleep(1)
            current_try += 1

        return []

# ---------------------------------------------------------------------------------------------------------------------------------------- #