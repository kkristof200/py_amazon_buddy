# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
import html, json
from typing import Optional, List, Dict
from requests import Response

# Pip
from bs4 import BeautifulSoup as bs
from kcu import request, kjson, strings
from unidecode import unidecode

# Local
from .models.search_result_product import SearchResultProduct
from .models.product import Product
from .models.review import Review
from .models.review_image import ReviewImage

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------------ class: Parser ------------------------------------------------------------- #

class Parser:

    # -------------------------------------------------------- Public methods -------------------------------------------------------- #

    @classmethod
    def parse_product(cls, response: Optional[Response], debug: bool = False) -> Optional[Product]:
        if not response or response.status_code not in [200, 201]:
            return None
        
        categories = []
        features = []
        videos = []

        soup = bs(response.content, 'lxml')
        parsed_json = cls.__json_loads(strings.between(response.text, 'var obj = jQuery.parseJSON(\'', '\')'))

        if parsed_json is None:
            return None
        
        images = parsed_json
        title = parsed_json['title'].strip()
        asin = parsed_json['mediaAsin']
        videos = parsed_json['videos']

        try:
            for feature in soup.find('div', {'class':'a-section a-spacing-medium a-spacing-top-small'}).find_all('span', {'class':'a-list-item'}):
                try:
                    features.append(feature.get_text().strip())
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
            price_text = soup.find('span', {'id':'priceblock_ourprice'}).text.replace('$', '').strip()
            price = float(price_text)
        except:
            price = None

        try:
            table_for_product_info = soup.find('table', {'id':'productDetails_detailBullets_sections1', 'class':'a-keyvalue prodDetTable'})

            details = {}
            if table_for_product_info is not None:
                for tr in table_for_product_info.find_all('tr'):
                    key = tr.find('th').get_text().strip()

                    if key is not None and key not in ['Customer Reviews', 'Best Sellers Rank']:
                        value = tr.find('td').get_text().strip()
                        details[key] = value
        except:
            pass

        image_details = {}

        if 'colorToAsin' in images and images['colorToAsin'] is not None:
            colors = images['colorToAsin']

            for color_name, color_dict in colors.items():
                _asin = color_dict['asin']
                image_details[_asin] = {
                    'name' : color_name,
                    'image_urls' : []
                }
                
                images_by_color = images['colorImages'][color_name]

                for elem in images_by_color:
                    if 'hiRes' in elem: 
                        image_details[_asin]['image_urls'].append(elem['hiRes'])

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
          
        if image_details is None or image_details == {}:
            try:
                images_json = cls.__json_loads(strings.between(response.text, '\'colorImages\': { \'initial\': ', '}]},') + '}]')

                if images_json is not None:
                    image_details[asin] = {
                        'name' : asin,
                        'image_urls' : []
                    }

                    for image_json in images_json:
                        try:
                            image_details[asin]['image_urls'].append(image_json['large'])
                        except Exception as e:
                            if debug:
                                print(e)
            except:
                pass

        associated_asins = []

        try:
            associated_asins_json = cls.__json_loads(strings.between(response.text, 'dimensionToAsinMap :', '},').strip() + '}')

            if associated_asins_json is not None:
                for val in associated_asins_json.values():
                    associated_asins.append(val)
        except:
            pass

        return Product(title, asin, price, categories, features, details, image_details, videos)

    @classmethod
    def parse_reviews_with_images(cls, response: Optional[Response], debug: bool = False) -> Optional[List[ReviewImage]]:
        # 'https://www.amazon.com/gp/customer-reviews/aj/private/reviewsGallery/get-data-for-reviews-image-gallery-for-asin?asin='
        if not response or response.status_code not in [200, 201]:
            return None
            
        try:
            reviews_json = cls.__json_loads(response.text)
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
    
    @classmethod
    def parse_products(cls, response: Optional[Response], debug: bool = False) -> List[SearchResultProduct]:
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

                    products.append(SearchResultProduct(asin, title, price, rating, review_count))
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

                    rating = int(div.find('i', class_='a-icon-star').find('span').text.split('.')[0].strip())
                    title = unidecode(html.unescape(div.find(None, {'data-hook':'review-title'}).find('span').text.strip()))
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

            return None

        return searches
    
    # -------------------------------------------------------- Private methods -------------------------------------------------------- #
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

# ---------------------------------------------------------------------------------------------------------------------------------------- #