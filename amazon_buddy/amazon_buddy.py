# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from typing import Optional, Union, List, Dict, Any
import os

# Local
from .category import Category

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ---------------------------------------------------------- class: AmazonBuddy ---------------------------------------------------------- #

class AmazonBuddy:

    # -------------------------------------------------------- Public methods -------------------------------------------------------- #

    @classmethod
    def search_products(
        cls,
        search_term: str,
        category: Category = Category.ALL_DEPARTMENTS,
        ignored_title_strs: List[str] = [],
        ignored_asins: List[str] = [],
        min_price: float = 50.0,
        min_reviews: int = 5,
        min_rating: float = 0.0,
        max_results: int = 100,
        random_ua: bool = True,
        sort: bool = True,
        debug: bool = False
    ) -> Optional[List[str]]:
        products = cls.__exec_cmd(
            'products',
            random_ua=random_ua,
            extra_params={
                '-k': '\'' + search_term + '\'',
                '-c': category.value,
                '-n': max_results,
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

                product['price'] = float(product['price'].replace(',', ''))
                product['asin'] = strings.between(product['url'].replace('%2F', '/'), '/dp/', '/')

                if (
                    product['price'] < min_price
                    or
                    product['reviews'] < min_reviews
                    or
                    cls.__contains(product['asin'], ignored_asins)
                    or
                    cls.__contains_in(product['title'], ignored_title_strs)
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
        random_ua: bool = True,
        sort: bool = True,
        debug: bool = False
    ) -> Optional[List[str]]:
        return cls.__exec_cmd(
            'reviews ' + asin,
            random_ua=random_ua,
            extra_params={
                '-n': max_results,
                '--min-rating': min_rating,
                '--sort': sort
            },
            debug=debug
        )

    @classmethod
    def get_product_details(
        cls,
        asin: str,
        random_ua: bool = True,
        debug: bool = False
    ) -> Optional[List[str]]:
        return cls.__exec_cmd(
            'asin ' + asin,
            random_ua=random_ua,
            debug=debug
        )


    # ------------------------------------------------------- Private methods -------------------------------------------------------- #

    @classmethod
    def __exec_cmd(
        cls,
        feature: str,
        random_ua: bool = True,
        extra_params: Optional[Dict[str, Any]] = None,
        debug: bool = False
    ) -> Optional[Union[List, Dict]]:
        params = extra_params or {}
        params['--random-ua'] = random_ua
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

            print('path', path)
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
            if k == '--random-ua':
                k = '--ua'

                from fake_useragent import FakeUserAgent

                v = '\'' + FakeUserAgent().random.replace('\'', '\\\'') + '\''
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