# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
import html
from typing import Optional, List
from requests import Response

# Pip
from bs4 import BeautifulSoup as bs
from kcu import request, kjson
from unidecode import unidecode

# Local
from .models.product import Product
from .models.review import Review

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------------ class: Parser ------------------------------------------------------------- #

class Parser:
    # -------------------------------------------------------- Public methods -------------------------------------------------------- #

    @classmethod
    def parse_products(cls, response: Optional[Response], debug: bool = False) -> List[Product]:
        if not response or response.status_code not in [200, 201]:
            return []
        
        products = []

        try:
            soup = bs(response.text, 'lxml')

            for div in [div for div in soup.find_all('div') if div.has_attr('data-asin') and len(div['data-asin']) > 0]:
                try:
                    asin = div['data-asin']
                    title = unidecode(html.unescape((div.find('span', class_='a-size-base-plus a-color-base a-text-normal') or div.find('span', class_='a-size-medium a-color-base a-text-normal')).text))

                    try:
                        price = float(div.find('span', class_='a-price').find('span', class_='a-price-whole').text.replace(',', '')) + float(div.find('span', class_='a-price').find('span', class_='a-price-fraction').text.replace(',', '')) / 100
                    except Exception as e:
                        price = None

                        # if debug:
                        #     print(e)

                    try:
                        spans = [span['aria-label'] for span in div.find_all('span') if span.has_attr('aria-label')]
                        rating = float(spans[0].split(' ')[0])
                        review_count = int(spans[1].replace(',', ''))
                    except:
                        rating = 0
                        review_count = 0

                    products.append(Product(asin, title, price, rating, review_count))
                except Exception as e:
                    pass
                    # if debug:
                    #     print(e)
        except Exception as e:
            if debug:
                print(e)

        return products

    @classmethod
    def parse_reviews(cls, response: Optional[Response], debug: bool = False) -> List[Review]:
        if not response or response.status_code not in [200, 201]:
            return None

        reviews = []

        try:
            soup = bs(response.text, 'lxml')

            for div in soup.find_all('div', {'data-hook':'review'}):
                try:
                    id = div['id']
                    name = unidecode(html.unescape(div.find('span', class_='a-profile-name').text.strip()))
                    rating = int(div.find('a', class_='a-link-normal').text.split('.')[0].strip())
                    title = unidecode(html.unescape(div.find('a', {'data-hook':'review-title'}).find('span').text.strip()))
                    text = unidecode(html.unescape(div.find('span', {'data-hook':'review-body'}).find('span').text.strip()))

                    try:
                        helpful_score = int(div.find('span', {'data-hook':'review-vote-statement'}.text.split(' ')[0]))
                    except:
                        helpful_score = 0
                    
                    reviews.append(Review(id, name, rating, helpful_score, title, text))
                except Exception as e:
                    if debug:
                        print(e)
        except Exception as e:
            if debug:
                print(e)

        return reviews

    @classmethod
    def parse_suggested_rh(cls, response: Optional[Response], min_stars: int, debug: bool = False) -> Optional[str]:
        if not response or response.status_code not in [200, 201]:
            return None

        try:
            soup = bs(response.content, 'lxml')

            for a in soup.find_all('a', class_='a-link-normal s-navigation-item'):
                try:
                    if not a.find('i', class_='a-icon a-icon-star-medium a-star-medium-{}'.format(min_stars)):
                        continue

                    href = a['href']

                    if 'rh=n%3A' in href:
                        return 'n' + href.split('rh=n')[1].split('&')[0]
                except Exception as e:
                    if debug:
                        print(e)
        except Exception as e:
            if debug:
                print(e)

        return None
    
    @classmethod
    def parse_related_searches(cls, response: Optional[Response], debug: bool = False) -> Optional[List[str]]:
        if not response or response.status_code not in [200, 201]:
            return None

        searches = []

        try:
            soup = bs(response.content, 'lxml')

            for a in soup.find_all('a', class_='a-link-normal s-no-outline'):
                try:
                    img = a.find('img')

                    if not img or not a['href'].startswith('/s'):
                        continue

                    searches.append(img['alt'].replace(', End of \'Related searches\' list', ''))
                except Exception as e:
                    if debug:
                        print(e)
        except Exception as e:
            if debug:
                print(e)

        return searches


# ---------------------------------------------------------------------------------------------------------------------------------------- #