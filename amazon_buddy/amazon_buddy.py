# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from typing import Optional, Union, List, Dict, Any
import os

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ---------------------------------------------------------- class: AmazonBuddy ---------------------------------------------------------- #

class AmazonBuddy:

    # -------------------------------------------------------- Public methods -------------------------------------------------------- #

    @classmethod
    def search_asins(
        cls,
        search_term: str,
        ignored_title_strs: List[str] = [],
        ignored_asins: List[str] = [],
        min_price: float = 50.0,
        min_reviews: int = 5,
        min_rating: float = 0.0,
        max_results: int = 100,
        random_ua: bool = True,
        sort: bool = True
    ) -> Optional[List[str]]:
        products = cls.__exec_cmd(
            'products',
            random_ua=random_ua,
            extra_params={
                '-k': '\'' + search_term + '\'',
                '-n': max_results,
                '--min-rating': min_rating,
                '--sort': sort
            }
        )

        if products is None:
            return None

        filtered_products = []

        for product in products:
            try:
                product['price'] = float(product['price'].replace(',', ''))
                product['asin'] = strings.string_between(product['url'].replace('%2F', '/'), '/dp/', '/')

                if (
                    product['price'] < min_price
                    or
                    product['reviews'] < min_reviews
                    or
                    self.__contains(product['asin'], ignored_asins)
                    or
                    self.__contains_in(product['title'], ignored_title_strs)
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
        sort: bool = True
    ) -> Optional[List[str]]:
        return cls.__exec_cmd(
            'reviews ' + asin,
            random_ua=random_ua,
            extra_params={
                '-n': max_results,
                '--min-rating': min_rating,
                '--sort': sort
            }
        )

    @classmethod
    def get_product_details(
        cls,
        asin: str,
        random_ua: bool = True
    ) -> Optional[List[str]]:
        return cls.__exec_cmd(
            'asin ' + asin,
            random_ua=random_ua
        )


    # ------------------------------------------------------- Private methods -------------------------------------------------------- #

    @classmethod
    def __exec_cmd(
        cls,
        feature: str,
        random_ua: bool = True,
        extra_params: Optional[Dict[str, Any]] = None
    ) -> Optional[Union[List, Dict]]:
        params = extra_params or {}
        params['--random-ua'] = random_ua
        params['--filetype'] = 'json'

        from kcu import sh, kjson, kpath

        resp = sh.sh(
            cls.__create_cmd(feature, params),
            debug=True
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