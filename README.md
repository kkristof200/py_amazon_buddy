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

ab = AmazonBuddy(debug=True)

products = ab.search_products(
    'face wash',
    sort_type=SortType.PRICE_HIGH_TO_LOW,
    min_price=0,
    category=Category.BEAUTY_AND_PERSONAL_CARE,
    max_results=1000
)
print(len(products))

reviews = ab.get_reviews(asin='B0758GYJK2')
print(reviews)
~~~~
