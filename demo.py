from amazon_buddy import AmazonBuddy

print(AmazonBuddy.get_product_details('macbook'))
print(AmazonBuddy.get_reviews('B01GW3H3U8', min_rating=4))