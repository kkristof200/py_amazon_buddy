import json
from amazon_buddy import AmazonBuddy, Category

print(json.dumps(AmazonBuddy.search_products('macbook', category=Category.COMPUTERS), indent=4))
# print(AmazonBuddy.get_reviews('B01GW3H3U8', min_rating=4))