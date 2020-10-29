# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from typing import Optional, List, Union
from requests import Response
import random

# Pip
from kcu.request import request, RequestMethod

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------------ class: Request ------------------------------------------------------------ #

class Request:

    # ------------------------------------------------------------- Init ------------------------------------------------------------- #

    def __init__(
        self,
        user_agent: Optional[str] = None,
        proxy: Optional[Union[str, List[str]]] = None,
        keep_cookies: bool = True,
        debug: bool = False
    ):
        self.user_agent = user_agent
        self.cookies = None
        self.keep_cookies = keep_cookies
        self.debug = debug

        if type(proxy) == list:
            proxy = random.choice(proxy) if len(proxy) > 0 else None

        self.proxy = proxy

    def set_us_address(self):
        self.keep_cookies = True

        self.get('https://www.amazon.com')
        self.__request('https://www.amazon.com/gp/delivery/ajax/address-change.html', RequestMethod.POST, body={
            'locationType':'LOCATION_INPUT',
            'zipCode':'90001',
            'storeContext':'generic',
            'deviceType':'web',
            'pageType':'Gateway',
            'actionSource':'glow',
            'almBrandId':'undefined'
        })

    def get(self, url: str):
        return self.__request(url, RequestMethod.GET)


    # ------------------------------------------------------- Private methods -------------------------------------------------------- #

    def __request(self, url: str, method: RequestMethod, body: Optional[dict] = None) -> Optional[Response]:
        headers = {
            'Host': 'www.amazon.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'TE': 'Trailers'
        }

        if self.cookies:
            headers['Cookie'] = self.cookies

        res = request(url, method, headers=headers, user_agent=self.user_agent, data=body, debug=self.debug, max_request_try_count=2, sleep_time=0.5, proxy_ftp=self.proxy, proxy_http=self.proxy, proxy_https=self.proxy)

        if self.keep_cookies and res and res.cookies:
            cookie_strs = []

            for k, v in res.cookies.get_dict().items():
                cookie_strs.append(k+'='+v)

            self.cookies = '; '.join(cookie_strs)

        return res


        




    # ------------------------------------------------------ Public properties ------------------------------------------------------- #



    # -------------------------------------------------------- Public methods -------------------------------------------------------- #



    # ------------------------------------------------------ Private properties ------------------------------------------------------ #



    # ------------------------------------------------------- Private methods -------------------------------------------------------- #




# ---------------------------------------------------------------------------------------------------------------------------------------- #