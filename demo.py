from kcu import kjson

from amazon_buddy import AmazonBuddy

# kjson.print(AmazonBuddy.get_product_details('B01GW3H3U8'))
kjson.print(AmazonBuddy.get_reviews('B01GW3H3U8', min_rating=4))