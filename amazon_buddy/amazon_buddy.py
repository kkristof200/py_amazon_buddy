# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from typing import Optional, Union, List, Dict, Any, Union
import os

# Local
from .category import Category
from .sort_type import SortType
from .product import *
from .review import Review

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ---------------------------------------------------------- class: AmazonBuddy ---------------------------------------------------------- #

class AmazonBuddy:

    # -------------------------------------------------------- Public methods -------------------------------------------------------- #

    @classmethod
    def search_products(
        cls,
        search_term: str,
        category: Category = Category.ALL_DEPARTMENTS,
        sort_type: Optional[SortType] = None,
        ignored_title_strs: List[str] = [],
        ignored_asins: List[str] = [],
        min_price: float = 50.0,
        min_reviews: int = 5,
        min_rating: float = 0.0,
        max_results: int = 100,
        user_agent: Optional[str] = None,
        random_ua: bool = True,
        sort: bool = True,
        debug: bool = False
    ) -> Optional[List[Union[Dict, Product]]]:
        products = cls.__exec_cmd(
            'products',
            user_agent=user_agent,
            random_ua=random_ua,
            extra_params={
                '-k': '\'' + search_term + '\'',
                '-c': category.value,
                '-n': max_results if max_results <= 500 else 500,
                '--productsorttype': sort_type.value if sort_type else None,
                '--min-rating': min_rating,
                '--sort': sort
            },
            debug=debug
        )

        if products is None:
            return None

        filtered_products = []

        for product in products:
            try:
                from kcu import strings

                product = Product(product)

                if (
                    product.price.current < min_price
                    or
                    product.rating.count < min_reviews
                    or
                    cls.__contains(product.asin, ignored_asins)
                    or
                    cls.__contains_in(product.title, ignored_title_strs)
                ):
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
        debug: bool = False
    ) -> Optional[List[Review]]:
        js = cls.__exec_cmd(
            'reviews ' + asin,
            user_agent=user_agent,
            random_ua=random_ua,
            extra_params={
                '-n': max_results,
                '--min-rating': min_rating,
                '--sort': sort
            },
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
        debug: bool = False
    ) -> Optional[Dict]:
        return cls.__exec_cmd(
            'asin ' + asin,
            user_agent=user_agent,
            random_ua=random_ua,
            debug=debug
        )


    # ------------------------------------------------------- Private methods -------------------------------------------------------- #

    @classmethod
    def __exec_cmd(
        cls,
        feature: str,
        user_agent: Optional[str] = None,
        random_ua: bool = True,
        extra_params: Optional[Dict[str, Any]] = None,
        debug: bool = False
    ) -> Optional[Union[List, Dict]]:
        params = extra_params or {}

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
            core_file_name = resp.split(' ')[-1].split('_')[0].strip()
            paths = kpath.file_paths_from_folder(os.getcwd(), allowed_extensions=['.json'])
            path = None

            for _path in paths:
                if core_file_name in _path:
                    path = _path

                    break
            
            if path is None:
                return None

            # print('path', path)
        except:
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