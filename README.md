# amazon_buddy

![python_version](https://img.shields.io/static/v1?label=Python&message=3.5%20|%203.6%20|%203.7&color=blue) [![PyPI downloads/month](https://img.shields.io/pypi/dm/amazon_buddy?logo=pypi&logoColor=white)](https://pypi.python.org/pypi/amazon_buddy)

## Description

Amazon scraper.

## Install

~~~~bash
pip install amazon_buddy
# or
pip3 install amazon_buddy
~~~~

## Usage

~~~~python
from amazon_buddy import AmazonBuddy, Category, SortType

ab = AmazonBuddy(debug=True, user_agent='ADD_USER_AGENT')

products = ab.search_products(
    'face wash',
    sort_type=SortType.PRICE_HIGH_TO_LOW,
    min_price=0,
    category=Category.BEAUTY_AND_PERSONAL_CARE,
    max_results=20
)
print(len(products))
asin = 'B0758GYJK2'

reviews = ab.get_reviews(asin=asin)
print(reviews)

ab.get_product_details(asin).save('{}.json'.format(asin))
~~~~