import json
from amazon_buddy import AmazonBuddy, Category, SortType

from randomua import RandomUA

products = AmazonBuddy.search_products('face wash', sort_type=SortType.PRICE_HIGH_TO_LOW, min_price=0, category=Category.BEAUTY_AND_PERSONAL_CARE, max_results=1000, user_agent=RandomUA.chrome(), debug=True)
print(products)

reviews = AmazonBuddy.get_reviews(asin='B0758GYJK2')
print(reviews)