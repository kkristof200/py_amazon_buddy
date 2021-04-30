# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
import html, json, traceback, copy
from typing import Optional, List, Dict, Union, Tuple, Callable
from urllib.parse import unquote

# Pip
from requests import Response
from noraise import noraise
from bs4 import BeautifulSoup as bs
from bs4 import element as BS4Element
from kcu import request, kjson, strings
from unidecode import unidecode

# Local
from .models import SearchResultProduct, Product, BaseProduct, Review, ReviewImage

# -------------------------------------------------------------------------------------------------------------------------------- #



# --------------------------------------------------------- class: Parser -------------------------------------------------------- #

class Parser:

    # --------------------------------------------------------- Init --------------------------------------------------------- #

    def __init__(
        self,
        did_get_detected_callback: Optional[Callable] = None
    ):
        self.did_get_detected_callback = did_get_detected_callback


    # ---------------------------------------------------- Public methods ---------------------------------------------------- #

    def parse_product(self, response: Optional[Response], debug: bool = False) -> Optional[Product]:
        soup = self.__parse_response(response)

        if not soup:
            return None

        categories = []
        features = []
        videos = []

        parsed_json = self.__json_loads(strings.between(response.text, 'var obj = jQuery.parseJSON(\'', '\')'))

        if parsed_json is None:
            try:
                print('response            ', response)
                print('response.status_code', response.status_code)
                print('response.encoding   ', response.encoding)
            except Exception as e:
                print('ERROR while printing response:', e)

            if self.did_get_detected_callback:
                self.did_get_detected_callback()

            return None

        title = self.__normalized_text(parsed_json['title'])
        asin = parsed_json['mediaAsin']
        videos = parsed_json['videos']

        try:
            for feature in soup.find('div', {'class':'a-section a-spacing-medium a-spacing-top-small'}).find_all('span', {'class':'a-list-item'}):
                try:
                    if feature.find('span', {'id':'replacementPartsFitmentBulletInner'}):
                        continue

                    features.append(self.__normalized_text(feature.get_text()))
                except:
                    pass
        except Exception as e:
            if debug:
                print(e)

        try:
            for cat_a in soup.find('div', {'id':'wayfinding-breadcrumbs_container'}).find_all('a', class_='a-link-normal a-color-tertiary'):
                try:
                    categories.append(bs(cat_a.text, "lxml").text.replace('\\', '/').replace('<', ' ').replace('>', ' ').strip().lower())
                except:
                    pass
        except Exception as e:
            if debug:
                print(e)

        try:
            price_text = soup.find('span', {'id':'priceblock_ourprice'}).text.strip()
            price_float_text = ''.join([c for c in price_text if c in '0123456789.'])
            price = float(price_float_text)
        except:
            price = None

        details = {}

        for table in soup.find_all('table', class_='a-keyvalue prodDetTable'):
            for tr in table.find_all('tr'):
                try:
                    key = tr.find('th').get_text().strip()

                    if key is not None and key not in ['Customer Reviews', 'Best Sellers Rank']:
                        value = tr.find('td').get_text()
                        details[self.__normalized_text(key)] = self.__normalized_text(value)
                except:
                    pass

        image_details = {}

# self.__json_loads(strings.between(response.text, '\'colorImages\': { \'initial\':', '}]},') + '}]')

        colors = parsed_json.get('colorToAsin')

        if colors:
            for color_name, color_dict in colors.items():
                try:
                    _asin = color_dict['asin']
                    image_details[_asin] = {
                        'name' : color_name,
                        'image_urls' : []
                    }

                    images_by_color = parsed_json['colorImages'][color_name]

                    for elem in images_by_color:
                        img_url = elem.get('hiRes') or elem.get('large')

                        if img_url:
                            image_details[_asin]['image_urls'].append(img_url)
                except:
                    pass
        else:
            try:
                image_details[asin] = {
                    'name' : asin,
                    'image_urls' : [
                        e for e in [
                            e.get('hiRes') or e.get('large') for e in self.__json_loads(strings.between(response.text, '\'colorImages\': { \'initial\':', '}]},') + '}]')
                        ] if e
                    ]
                }
            except:
                pass

        added_video_urls = []

        for elem in videos:
            try:
                vid_url = elem['url']

                if vid_url in added_video_urls:
                    continue

                video = {'url':vid_url}

                video['title'] = elem['title'].strip()
                video['height'] = int(elem['videoHeight'] if 'videoHeight' in elem else elem['height'])
                video['width'] = int(elem['videoWidth'] if 'videoWidth' in elem else elem['width'])

                videos.append(video)
                added_video_urls.append(vid_url)
            except Exception as e:
                if debug:
                    print(e)

        associated_asins = []

        try:
            associated_asins_json = self.__json_loads(strings.between(response.text, 'dimensionToAsinMap :', '},').strip() + '}')

            if associated_asins_json is not None:
                for val in associated_asins_json.values():
                    associated_asins.append(val)
        except:
            pass

        related_products = []
        related_products_wrappers = [
            e for e in
            [soup.find('div', {'cel_widget_id': 'sims-consolidated-{}_csm_instrumentation_wrapper'.format(i)}) for i in range(4)]
            if e]

        for related_products_wrapper in related_products_wrappers:
            if related_products_wrapper:
                related_products_asins = []

                for li in related_products_wrapper.find_all('li', class_='a-carousel-card'):
                    related_product = self.__parse_similar_product(li)

                    if related_product and related_product.asin not in related_products_asins:
                        related_products.append(related_product)
                        related_products_asins.append(related_product.asin)

        comparison_table = soup.find('table', {'id':'HLCXComparisonTable'})
        similar_products = {}

        if comparison_table:
            similar_products = {}

            prices_row = comparison_table.find('tr', {'id':'comparison_price_row'})
            prices_spans = prices_row.find_all('span', class_='a-price')
            other_rows = comparison_table.find_all('tr', class_='comparison_other_attribute_row')

            for i, si_th in enumerate(comparison_table.find_all('th', {'role': 'columnheader'})):
                try:
                    si_asin = si_th['data-asin']
                    img = si_th.find('img')

                    similar_products[si_asin] = {
                        'product': BaseProduct(
                            title=self.__normalized_text(img['alt']),
                            asin=si_asin,
                            price=float(prices_spans[i].find('span').text.lstrip('$')),
                            main_image_url=img['data-src']
                        ),
                        'other_attributes': {}
                    }

                    for other_row in other_rows:
                        res = other_row.find_all('td')[i].find('span').text

                        if res == '—':
                            res = None

                        similar_products[si_asin]['other_attributes'][other_row.find('th').find('span').text] = res
                except:
                    pass

        if price == None and similar_products:
            this_similar_product = similar_products.get(asin, {}).get('product')

            if this_similar_product:
                price = this_similar_product.price

        try:
            descripton = soup.find('div', {'id':'productDescription'}).find('p').text.strip()
        except:
            descripton = None

        return Product(title, asin, price, categories, features, descripton, details, image_details, videos, related_products, similar_products)

    def parse_reviews_with_images(self, response: Optional[Response], debug: bool = False) -> Optional[List[ReviewImage]]:
        # 'https://www.amazon.com/gp/customer-reviews/aj/private/reviewsGallery/get-data-for-reviews-image-gallery-for-asin?asin='
        if not response or response.status_code not in [200, 201]:
            return None

        try:
            reviews_json = self.__json_loads(response.text)
        except Exception as e:
            if debug:
                print(e)

            return None

        reviews = {}
        details = reviews_json['images']

        for elem in details:
            try:
                author = elem['associatedReview']['author']['name']
                text = elem['associatedReview']['text']
                clean_text = bs(text, "lxml").text.replace('  ', ' ')
                review_key = elem['associatedReview']['reviewId']

                if review_key in reviews:
                    review = reviews[review_key]
                else:
                    review = {
                        'author': author,
                        'text': clean_text,
                        'rating': elem['associatedReview']['overallRating'],
                        'image_urls': []
                    }

                    if 'scores' in elem['associatedReview'] and 'helpfulVotes' in elem['associatedReview']['scores']:
                        review['upvotes'] = int(elem['associatedReview']['scores']['helpfulVotes'])
                    else:
                        review['upvotes'] = 0

                img_url = elem['mediumImage']
                review['image_urls'].append(img_url)

                reviews[review_key] = review
            except Exception as e:
                if debug:
                    print(e)

        return [ReviewImage(r['author'], r['text'], r['rating'], r['image_urls'], r['upvotes'])
                for r in sorted(reviews.values(), key=lambda k: k['upvotes'], reverse=True)]

    def parse_products(self, response: Optional[Response], debug: bool = False) -> List[SearchResultProduct]:
        soup = self.__parse_response(response)

        if not soup:
            return []

        products = []

        for div in [div for div in soup.find_all('div') if div.has_attr('data-asin') and len(div['data-asin']) > 0]:
            try:
                asin = div['data-asin']
                title = unidecode(html.unescape((div.find('span', class_='a-size-base-plus a-color-base a-text-normal') or div.find('span', class_='a-size-medium a-color-base a-text-normal')).text))

                try:
                    price = float(div.find('span', class_='a-price').find('span', class_='a-price-whole').text.replace(',', '')) + float(div.find('span', class_='a-price').find('span', class_='a-price-fraction').text.replace(',', '')) / 100
                except:# Exception as e:
                    price = None

                    # if debug:
                    #     print(e)

                try:
                    spans = [span['aria-label'] for span in div.find_all('span') if span.has_attr('aria-label')]
                    rating = float(spans[0].split(' ')[0])
                    review_count = int(spans[1].replace(',', ''))
                except:# Exception as e:
                    rating = 0
                    review_count = 0

                products.append(SearchResultProduct(asin, title, price, rating, review_count))
            except:# Exception as e:
                pass
                # if debug:
                #     print(e)

        return products

    def parse_reviews(
        self,
        response: Optional[Response],
        debug: bool = False
    ) -> List[Review]:
        soup = self.__parse_response(response)

        if not soup:
            return []

        return [r for r in [self.parse_review(element=e, debug=debug) for e in soup.find_all('div', {'data-hook':'review'})] if r]

    @noraise()
    def parse_review(
        self,
        element: Union[BS4Element.Tag, BS4Element.NavigableString],
        debug: bool = False
    ) -> Optional:#[Review]:
        id = element['id']
        reviewer_name = element.find('span', class_='a-profile-name').text.strip()
        rating = [int(c) for c in ''.join(element.find('i', class_='a-icon-star')['class']) if c.isnumeric()][0]

        helpful_score = 0
        helpful_score_element = element.find('span', class_='cr-vote-text')

        if helpful_score_element:
            text = helpful_score_element.text.strip().replace(',', '')

            helpful_score_numbers = [int(c) for c in text.split() if c.isnumeric()]
            helpful_score = helpful_score_numbers[0] if helpful_score_numbers else 1

        title = self.__normalized_text(element.find(attrs={'data-hook':'review-title'}).text)

        text_span = element.find(attrs={'data-hook':'review-body'})
        _text_span = text_span.find('span')

        if _text_span is not None:
            text_span = _text_span

        text = self.__normalized_text(text_span.text)

        language = 'en'
        translate_element = element.find('div', class_='cr-translate-this-review-section')
        foreign = translate_element is not None

        if foreign:
            t = unquote(translate_element.find('span')['data-reviews:ajax-post'])
            language = t.split('language\\":\\"')[-1].split('\\')[0]

        review_section_element = element.find('div', class_='review-image-tile-section')

        if review_section_element:
            image_urls = [e['src'].replace('._SY88', '') for e in review_section_element.find_all('img')]
        else:
            image_urls = []

        return Review(
            id=id,
            reviewer_name=reviewer_name,
            rating=rating,
            upvotes=helpful_score,
            title=title,
            text=text,
            language=language,
            foreign=foreign,
            image_urls=image_urls,
        )

    def parse_suggested_rh(self, response: Optional[Response], min_stars: int, debug: bool = False) -> Optional[str]:
        soup = self.__parse_response(response)

        if not soup:
            return None

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

        return None

    def parse_related_searches(self, response: Optional[Response], debug: bool = False) -> Optional[List[str]]:
        soup = self.__parse_response(response)

        if not soup:
            return None

        searches = []

        for a in soup.find_all('a', class_='a-link-normal s-no-outline'):
            try:
                img = a.find('img')

                if not img or not a['href'].startswith('/s'):
                    continue

                searches.append(img['alt'].replace(', End of \'Related searches\' list', ''))
            except Exception as e:
                if debug:
                    print(e)

        return searches


    # ---------------------------------------------------- Private methods --------------------------------------------------- #

    @noraise(print_exc=False)
    def __parse_similar_product(
        self,
        element: Union[BS4Element.Tag, BS4Element.NavigableString]
    ) -> Optional[BaseProduct]:
        price_title_a = element.find('div', class_='a-row a-color-price').find('a')

        return BaseProduct(
            title=self.__normalized_text(price_title_a['title']),
            asin=element.find('div')['data-asin'],
            price=float(price_title_a.find('span').text.lstrip('$')),
            main_image_url=element.find('img', class_='a-dynamic-image')['src'].replace('160,160', '')
        )

    @noraise()
    def __parse_response(
        self,
        response: Optional[Response],
        allowed_response_status_codes: List[int] = [200, 201]
    ) -> Optional[bs]:
        if response is None:
            return None

        if response.status_code not in allowed_response_status_codes:
            if response.status_code == 503 and self.did_get_detected_callback:
                self.did_get_detected_callback()

            return None

        return bs(response.content, 'lxml')

    @staticmethod
    def __normalized_text(s: str) -> str:
        s = s.strip()
        s = s.replace('<br />', '')
        s = unquote(s)
        s = html.unescape(s)
        s = '\n'.join([l.strip() for l in s.split('\n') if len(l.strip()) > 0])

        return unidecode(html.unescape(s))

    @staticmethod
    def __json_loads(s: str) -> Optional[Dict]:
        try:
            return json.loads(s)
        except:
            try:
                return json.loads(s.replace('\\\'', '\''))
            except Exception as e:
                print(e)

        return None

# -------------------------------------------------------------------------------------------------------------------------------- #