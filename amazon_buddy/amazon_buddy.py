# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import Optional, List, Dict, Callable, Union
import urllib.parse
import time, random

# Pip
from noraise import noraise
from ksimpleapi import Api
from kcu import strings

# Local
from .models import Category, SortType, ReviewRatingFilter, ReviewSortType, SearchResultProduct, Product, Review, ReviewImage, AmazonError

from ._filter import ProductFilter, ReviewFilter
from ._parser import Parser
from ._rh import RH
from ._constants import ZIP_CODES_US

# -------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------ class: AmazonBuddy ------------------------------------------------------ #

class AmazonBuddy(Api):

    # --------------------------------------------------------- Init --------------------------------------------------------- #

    def __init__(
        self,
        user_agent: Optional[Union[str, List[str]]] = None,
        proxy: Optional[Union[str, List[str]]] = None,
        max_request_try_count: int = 1,
        sleep_s_between_failed_requests: Optional[float] = 0.5,
        keep_cookies: bool = True,
        allow_redirects: bool = False,
        use_cloudscrape: bool = False,
        error_callback: Optional[Callable[[AmazonError], None]] = None,
        referers: Union[str, List[str]] = 'https://www.amazon.com',
        debug: bool = False,
        set_us_address: bool = False,
        extra_headers: Optional[dict] = None,
        default_request_timeout: Optional[float] = None,
        domain: str = 'www.amazon.com',
        zip_codes: Optional[List[int]] = None
    ):
        """init function

        Args:
            user_agent (Optional[Union[str, List[str]]], optional): User agent(s) to use for requests. If list is provided, one will be chosen randomly. Defaults to None.
            proxy (Optional[Union[str, List[str]]], optional): Proxy/Proxies to use for requests. If list is provided, one will be chosen randomly. Defaults to None.
            max_request_try_count (int, optional): How many times does a request can be tried (if fails). Defaults to 1.
            sleep_s_between_failed_requests (Optional[float], optional): How much to wait between requests when retrying. Defaults to 0.5.
            keep_cookies (bool, optional): Wether to use cookies or not. Defaults to True.
            allow_redirects (bool, optional): Wether to allow request redirects or not. Defaults to False.
            use_cloudscrape (bool, optional): Wether to use CloudScrape library instead of requests. Defaults to False.
            error_callback (Callable, optional): Called, when amazon returns a bot response.
            debug (bool, optional): Show debug logs. Defaults to False.
        """

        extra_headers = extra_headers or {}
        extra_headers.update({
            'Host': domain,
            'Origin': 'https://{}'.format(domain),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })

        super().__init__(
            user_agent=user_agent,
            proxy=proxy,
            keep_cookies=keep_cookies,
            max_request_try_count=max_request_try_count,
            sleep_s_between_failed_requests=sleep_s_between_failed_requests,
            extra_headers=extra_headers,
            allow_redirects=allow_redirects,
            debug=debug,
            use_cloudscrape=use_cloudscrape,
            default_request_timeout=default_request_timeout
        )

        self.referers =  [referers] if isinstance(referers, str) else referers
        self.did_set_us_address = not set_us_address
        self._parser = Parser(error_callback)
        self.domain = domain
        self.zip_codes = zip_codes if zip_codes is not None else ZIP_CODES_US


    # ---------------------------------------------------- Public methods ---------------------------------------------------- #

    @noraise()
    def get_product_details(
        self,
        asin: str
    ) -> Optional[Product]:
        return self._parser.parse_product(
            self._get(
                'https://{}/dp/{}'.format(self.domain, asin),
                extra_headers={
                    'Referer': random.choice(self.referers),# 'https://www.amazon.com',
                }
            )
        )

    def get_product_reviews_with_images(
        self,
        asin: str
    ) -> Optional[List[ReviewImage]]:
        try:
            # return self._parser.parse_reviews_with_images(
            #     self._get('https://{}/gp/customer-reviews/aj/private/reviewsGallery/get-data-for-reviews-image-gallery-for-asin?asin={}'.format(self.domain, asin))
            # )
            data = 'asin={}noCache={}'.format(asin, int(time.time() * 1000))

            return self._parser.parse_reviews_with_images(
                self._post(
                    'https://{}/gp/customer-reviews/aj/private/reviewsGallery/get-data-for-reviews-image-gallery-for-asin'.format(self.domain),
                    body=data,
                    extra_headers={
                        'Accept': '*/*',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Length': len(data),
                        'Referer': 'https://{}/product-reviews/{}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'.format(self.domain, asin)
                    }
                )
            )
        except Exception as e:
            if self.debug:
                print(e)

            return None

    def get_related_searches(
        self,
        search_term: str,
        category: Optional[Union[Category, str]] = Category.ALL_DEPARTMENTS
    ) -> Optional[List[str]]:
        category = category or Category.ALL_DEPARTMENTS

        if type(category) == type(Category.ALL_DEPARTMENTS):
            category = category.value

        return self.__get_related_searches(
            'https://{}/s?k={}&i={}&ref=nb_sb_noss'.format(self.domain, urllib.parse.quote(search_term), category)
        )

    def get_trends(
        self,

        # url
        category: Optional[Union[Category, str]] = Category.ALL_DEPARTMENTS,
        locale: str = 'en_US',
        search_params: Union[str, List[str]] = 'abcdefghijklmnopqrstuvwxyz',

        # other
        return_dict: bool = False,
        max_results_per_letter: int = 10
    ) -> Union[List[str], Dict[str, List[str]]]:
        suggestions = {}

        for param in search_params:
            suggestions[str(param)] = self.__get_suggestions(
                category,
                str(param),
                locale,
                max_results_per_letter
            )

        if return_dict:
            return suggestions
        else:
            suggestions_ = []

            for v in suggestions.values():
                suggestions_.extend(v)

            return suggestions_

    def set_us_address(
        self,
        zip_code: Optional[int] = None
    ) -> bool:
        if self.did_set_us_address:
            return True

        self.keep_cookies = True
        self._get('https://{}'.format(self.domain))
        address_selections_res = self._get(
            'https://{}/gp/glow/get-address-selections.html?deviceType=desktop&pageType=Gateway&storeContext=NoStoreName'.format(self.domain),
            extra_headers={
                'Accept': 'text/html,*/*',
                'Referer': random.choice(self.referers),# 'https://www.amazon.com',
                'X-Requested-With': 'XMLHttpRequest'
            }
        )

        if not address_selections_res or not address_selections_res.text:
            if self.debug:
                print('Could not get address selection')

            return False

        csrf_token = strings.between(address_selections_res.text, 'CSRF_TOKEN : "', '"')

        if not csrf_token:
            if self.debug:
                print('Could not get csrf token')

            return False

        zip_code = zip_code or random.choice(self.zip_codes)

        data = 'locationType=LOCATION_INPUT&zipCode={}&storeContext=generic&deviceType=web&pageType=Gateway&actionSource=glow&almBrandId=undefined'.format(zip_code)

        res = self._post(
            'https://{}/gp/delivery/ajax/address-change.html'.format(self.domain),
            body=data,
            extra_headers={
                'Accept': 'text/html,*/*',
                'Content-Length': len(data),
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
                'contentType': 'application/x-www-form-urlencoded;charset=utf-8',
                'Referer': 'https://{}'.format(self.domain),
                'anti-csrftoken-a2z': csrf_token
            }
        )

        if res and res.status_code == 200:
            self.did_set_us_address = True

        return self.did_set_us_address

    def search_products(
        self,

        # url
        search_term: str,
        category: Optional[Union[Category, str]] = Category.ALL_DEPARTMENTS,
        sort_type: Optional[SortType] = None,

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
        use_us_address_if_needed: bool = True
    ) -> Optional[List[SearchResultProduct]]:
        category = category or Category.ALL_DEPARTMENTS

        if type(category) == type(Category.ALL_DEPARTMENTS):
            category = category.value

        base_url = 'https://{}/s?k={}&i={}'.format(self.domain, urllib.parse.quote(search_term), category)
        rh = RH.create_rh(min_price=min_price, max_price=max_price)
        # cat_id, ratings = cls.__get_search_cat_and_ratings(search_term, request)
        suggested_rh = self.__get_suggested_rh(base_url, min_rating, proxy=proxy, user_agent=user_agent) if min_rating else None

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

        if self._request.keep_cookies and not self.did_set_us_address and use_us_address_if_needed:
            self.set_us_address()

        return self.__solve(base_url, 'page', ProductFilter(min_price, max_price, min_rating, min_reviews, ignored_asins, ignored_title_strs), self._parser.parse_products, max_results, proxy=proxy, user_agent=user_agent)

    def get_reviews(
        self,

        # url
        asin: str,
        media_reviews_only: bool = False,
        verified_purchases_only: bool = False,
        review_rating_filter: Optional[ReviewRatingFilter] = None,
        review_sort_type: ReviewSortType = ReviewSortType.HELPFUL,

        # filter
        min_rating: float = 3.0,
        ignored_ids: Optional[List[str]] = None,
        ignore_foreign: bool = False,

        # request
        proxy: Optional[Union[str, List[str]]] = None,
        user_agent: Optional[str] = None,

        # other
        max_results: int = 100,
        debug: bool = False
    ) -> Optional[List[Review]]:
        base_url = 'https://{}/product-reviews/{}/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType={}&filterByStar={}&sortBy={}&formatType=current_format&mediaType={}'.format(
            self.domain,
            asin,
            'avp_only_reviews' if verified_purchases_only else 'all_reviews',
            (review_rating_filter or ReviewRatingFilter.STAR_ALL).value,
            (review_sort_type or ReviewSortType.HELPFUL).value,
            'media_reviews_only' if media_reviews_only else 'all_contents'
        )

        return self.__solve(base_url, 'pageNumber', ReviewFilter(min_rating, ignored_ids, ignore_foreign), self._parser.parse_reviews, max_results, proxy=proxy, user_agent=user_agent)


    # ---------------------------------------------------- Private methods --------------------------------------------------- #

    def __solve(
        self,
        base_url: str,
        page_param_name: str,
        filter,
        parse: Callable,
        max_results: int,
        proxy: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> List:
        p = 0
        l = []
        max_try = 3
        current_try = 1
        max_p = 50

        while len(l) < max_results and p <= max_p:
            p += 1
            url = base_url + '&{}={}'.format(page_param_name, p)
            # self.debug = False
            res = self._get(
                url,
                proxy=proxy or self.proxy,
                user_agent=user_agent or self.user_agent
            )

            new_elements = parse(
                res,
                debug=self.debug
            )
            filtered = filter.filter(new_elements)
            l.extend(filtered)

            if self.debug:
                print('URL: {} - Found {}|{}|{} - Page {}'.format(url, len(new_elements), len(filtered), len(l), p), end='\n')

            if len(new_elements) < 20 or (p > 25 and len(filtered) == 0):
                if current_try >= max_try:
                    return l

                current_try += 1
                time.sleep(1)

                continue

            current_try = 1

        if self.debug:
            print('Found {} - pages checked {}'.format(len(l), p))

        return l if len(l) > 0 else None

    def __get_suggested_rh(
        self,
        url: str,
        min_rating: int,
        max_try: int = 3,
        proxy: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[str]:
        current_try = 1

        while current_try <= max_try:
            rh = self._parser.parse_suggested_rh(self._get(
                url,
                proxy=proxy or self.proxy,
                user_agent=user_agent or self.user_agent,
                extra_headers={
                    'Referer': random.choice(self.referers),# 'https://www.amazon.com',
                }
            ), int(min_rating))

            if rh:
                return rh

            time.sleep(1)
            current_try += 1

        return None

    def __get_related_searches(
        self,
        url: str,
        max_try: int = 3,
        proxy: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[List[str]]:
        current_try = 1

        while current_try <= max_try:
            rs = self._parser.parse_related_searches(
                self._get(
                    url,
                    extra_headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Referer': random.choice(self.referers),# 'https://www.amazon.com',
                    },
                    proxy=proxy or self.proxy,
                user_agent=user_agent or self.user_agent
                )
            )

            if rs is not None:
                return rs

            time.sleep(1)
            current_try += 1

        return None

    def __get_suggestions(
        self,
        category: Category,
        letter: str,
        locale: str,
        max_results: int,
        proxy: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> List[str]:
        url = 'https://completion.amazon.com/api/2017/suggestions?lop={}&site-variant=desktop&client-info=amazon-search-ui&mid=ATVPDKIKX0DER&alias={}&ks=65&prefix={}&event=onKeyPress&limit=11&fb=1&suggestion-type=KEYWORD&_={}'.format(locale, category.value, letter, int(time.time()))
        suggestions = []

        try:
            j = self._get(
                url,
                extra_headers={
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Host': 'completion.amazon.com',
                    'Referer': random.choice(self.referers),# 'https://www.amazon.com',
                },
                use_cookies=False,
                proxy=proxy or self.proxy,
                user_agent=user_agent or self.user_agent
            ).json()

            for suggestion in j['suggestions']:
                suggestion = suggestion['value']

                if suggestion not in suggestions:
                    suggestions.append(suggestion)

                    if len(suggestions) >= max_results:
                        return suggestions

            return suggestions
        except Exception as e:
            if self.debug:
                print(e)

            return suggestions


# -------------------------------------------------------------------------------------------------------------------------------- #