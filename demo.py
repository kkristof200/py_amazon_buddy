import json
from amazon_buddy import AmazonBuddy, Category, SortType

from randomua import RandomUA

# products = AmazonBuddy.search_products('air mattress', category=Category.HOME_AND_KITCHEN, ignored_title_strs=['$', 'card', 'gift', 'code', 'service', 'currency', '(xbox', 'madden', 'fifa', 'hfl', 'nhl', 'ncaa', 'nba', 'digital', 'iphone', 'ipad', 'free'], min_price=99.0, min_reviews=3, min_rating=3.0, max_results=20, user_agent=RandomUA.random(), sort_type=SortType.PRICE_HIGH_TO_LOW, sort=True, debug=True)

# AmazonBuddy.search_products(
#     'rice cooker',
#     category=Category.HOME_AND_KITCHEN,
#     sort_type=SortType.PRICE_HIGH_TO_LOW,
#     min_rating=3,
#     min_price=200.0,
#     min_reviews=5,
#     max_results=500,
#     include_unavailable=True,
#     user_agent=RandomUA.chrome(),
#     debug=True
# )

# for product in products:
#     product.jsonprint()

# print(len(products))


# from kcu import kjson

# details = AmazonBuddy.get_product_details('B011T7IVUI', user_agent=RandomUA.random(), debug=True)

# kjson.save('t.json', details)
# products[0].jsonprint()

reviews = AmazonBuddy.get_reviews(asin='B07L52KP31')
reviews[0].jsonprint()





# https://www.amazon.com/s?k=rice+cooker&i=garden

# &rh=p_36%

# 3A10000
# 100-0
# https://www.amazon.com/s?k=rice+cooker&i=garden&rh=p_36%3A10000-
# 100-200
# https://www.amazon.com/s?k=rice+cooker&i=garden&rh=p_36%3A10000-20000


# https://www.amazon.com/s?k=rice+cooker&i=garden&rh=p_36%3A10000-&qid=1602158374&rnid=386465011&ref=sr_nr_p_36_5
# https://www.amazon.com/s?k=rice+cooker&i=garden&rh=p_36%3A10000-&qid=1602158374&rnid=386465011&ref=sr_nr_p_36_5