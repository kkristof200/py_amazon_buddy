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
from .models.review_image import ReviewImage

from .filter import ProductFilter, ReviewFilter
from .parser import Parser
from .request import Request
from .rh import RH

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ---------------------------------------------------------- class: AmazonBuddy ---------------------------------------------------------- #

class AmazonBuddy:

    # -------------------------------------------------------- Public methods -------------------------------------------------------- #

    @classmethod
    def get_product_details(
        cls,

        #url
        asin: str,

        # request
        proxy: Optional[Union[str, List[str]]] = None,
        user_agent: Optional[str] = None,

        # other
        debug: bool = False
    ) -> Optional[Product]:
        try:
            return Parser.parse_product(
                Request(
                    user_agent,
                    keep_cookies=True,
                    proxy=proxy,
                    debug=debug
                ).get('https://www.amazon.com/dp/{}'.format(asin)),
                debug=debug
            )
        except Exception as e:
            if debug:
                print(e)

            return None

    @classmethod
    def get_product_reviews_with_images(
        cls,

        # url
        asin: str,

        # request
        proxy: Optional[Union[str, List[str]]] = None,
        user_agent: Optional[str] = None,
        
        # other
        debug: bool = False
    ) -> Optional[List[ReviewImage]]:
        try:
            return Parser.parse_reviews_with_images(
                Request(
                    user_agent, 
                    keep_cookies=True, 
                    proxy=proxy, 
                    debug=debug
                ).get('https://www.amazon.com/gp/customer-reviews/aj/private/reviewsGallery/get-data-for-reviews-image-gallery-for-asin?asin={}'.format(asin)), 
                debug=debug
            )
        except Exception as e:
            if debug:
                print(e)

            return None

    @classmethod
    def get_related_searches(
        cls,

        # url
        search_term: str,
        category: Optional[Union[Category, str]] = Category.ALL_DEPARTMENTS,

        # request
        proxy: Optional[Union[str, List[str]]] = None,
        user_agent: Optional[str] = None,

        # other
        debug: bool = False
    ) -> Optional[List[str]]:
        category = category or Category.ALL_DEPARTMENTS

        if type(category) == type(Category.ALL_DEPARTMENTS):
            category = category.value

        return cls.__get_related_searches(
            'https://www.amazon.com/s?k={}&i={}'.format(urllib.parse.quote(search_term), category),
            Request(user_agent, keep_cookies=True, proxy=proxy, debug=debug)
        )

    @classmethod
    def get_trends(
        cls,

        # url
        category: Optional[Union[Category, str]] = Category.ALL_DEPARTMENTS,
        locale: str = 'en_US',
        search_letters: str = 'abcdefghijklmnopqrstuvwxyz',

        # request
        proxy: Optional[Union[str, List[str]]] = None,
        user_agent: Optional[str] = None,

        # other
        return_dict: bool = False,
        max_results_per_letter: int = 10,
        debug: bool = False
    ) -> Union[List[str], Dict[str, List[str]]]:
        suggestions = {}
        request = Request(proxy, user_agent, keep_cookies=True, debug=debug)

        for char in search_letters:
            suggestions[str(char)] = cls.__get_suggestions(
                category,
                str(char),
                locale,
                max_results_per_letter,
                request,
                debug
            )

        if return_dict:
            return suggestions
        else:
            suggestions_ = []

            for v in suggestions.values():
                suggestions_.extend(v)

            return suggestions_

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
        proxy: Optional[Union[str, List[str]]] = None,
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
        request = Request(user_agent, keep_cookies=True, proxy=proxy, debug=debug)
        # cat_id, ratings = cls.__get_search_cat_and_ratings(search_term, request)
        suggested_rh = cls.__get_suggested_rh(base_url, min_rating, request) if min_rating else None

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
        proxy: Optional[Union[str, List[str]]] = None,
        user_agent: Optional[str] = None,

        # other
        max_results: int = 100,
        debug: bool = False
    ) -> Optional[List[Review]]:
        request = Request(user_agent, keep_cookies=True, proxy=proxy, debug=debug)
        request.get('https://www.amazon.com/dp/{}'.format(asin))
        base_url = 'https://www.amazon.com/product-reviews/{}?ie=UTF8&reviewerType=all_reviews&sortBy=helpful'.format(asin)

        return cls.__solve(base_url, 'pageNumber', request, ReviewFilter(min_rating), Parser.parse_reviews, max_results, debug=debug)


    # ------------------------------------------------------- Private methods -------------------------------------------------------- #

    @staticmethod
    def __solve(base_url: str, page_param_name: str, request: Request, filter, parse: Callable, max_results: int, debug: bool = False) -> List:
        p = 0
        l = []
        max_try = 3
        current_try = 1
        max_p = 50

        while len(l) < max_results and p <= max_p:
            p += 1
            url = base_url + '&{}={}'.format(page_param_name, p)
            request.debug = False
            new_elements = parse(request.get(url), debug=True)
            filtered = filter.filter(new_elements)
            l.extend(filtered)

            if debug:
                print('URL: {} - Found {}|{}|{} - Page {}'.format(url, len(new_elements), len(filtered), len(l), p), end='\n')

            if len(new_elements) < 20 or (p > 25 and len(filtered) == 0):
                if current_try >= max_try:
                    return l

                current_try += 1
                time.sleep(1)

                continue

            current_try = 1

        print('Found {} - pages checked {}'.format(len(l), p))

        return l if len(l) > 0 else None

    @staticmethod
    def __get_suggested_rh(
        url: str,
        min_rating: int,
        request: Request,
        max_try: int = 3
    ) -> Optional[str]:
        current_try = 1

        while current_try <= max_try:
            rh = Parser.parse_suggested_rh(request.get(url), int(min_rating), debug=request.debug)

            if rh:
                return rh

            time.sleep(1)
            current_try += 1

        return None
    
    @staticmethod
    def __get_related_searches(url: str, request: Request, max_try: int = 3) -> Optional[List[str]]:
        current_try = 1

        while current_try <= max_try:
            rs = Parser.parse_related_searches(request.get(url), debug=request.debug)

            if rs:
                return rs

            time.sleep(1)
            current_try += 1

        return None


    @staticmethod
    def __get_product_reviews_with_images(url: str, request: Request, max_try: int = 3) -> Optional[List[ReviewImage]]:
        current_try = 1

        while current_try <= max_try:
            reviews = Parser.parse_reviews_with_images(request.get(url), debug=request.debug)

            if reviews:
                return reviews

            time.sleep(1)
            current_try += 1

        return None

    @staticmethod
    def __get_suggestions(category: Category, letter: str, locale: str, max_results: int, request: Request, debug: bool) -> List[str]:
        import time
        from kcu import request

        url = 'https://completion.amazon.com/api/2017/suggestions?lop={}&site-variant=desktop&client-info=amazon-search-ui&mid=ATVPDKIKX0DER&alias={}&ks=65&prefix={}&event=onKeyPress&limit=11&fb=1&suggestion-type=KEYWORD&_={}'.format(locale, category.value, letter, int(time.time()))
        suggestions = []

        try:
            j = request.get(url, debug=debug).json()

            for suggestion in j['suggestions']:
                suggestion = suggestion['value']

                if suggestion not in suggestions:
                    suggestions.append(suggestion)

                    if len(suggestions) >= max_results:
                        return suggestions

            return suggestions
        except Exception as e:
            if debug:
                print(e)

            return suggestions


# ---------------------------------------------------------------------------------------------------------------------------------------- #