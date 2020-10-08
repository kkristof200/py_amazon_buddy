import json
from amazon_buddy import AmazonBuddy, Category, SortType

from randomua import RandomUA

products = AmazonBuddy.search_products(
    'rice cooker',
    category=Category.HOME_AND_KITCHEN,
    sort_type=SortType.PRICE_HIGH_TO_LOW,
    min_rating=3,
    min_price=200.0,
    min_reviews=5,
    max_results=500,
    include_unavailable=True,
    user_agent=RandomUA.chrome(),
    debug=True
)

for product in products:
    product.jsonprint()

print(len(products))
# products[0].jsonprint()

# reviews = AmazonBuddy.get_reviews(asin='B0758GYJK2')
# reviews[0].jsonprint()





# https://www.amazon.com/s?k=rice+cooker&i=garden

# &rh=p_36%

# 3A10000
# 100-0
# https://www.amazon.com/s?k=rice+cooker&i=garden&rh=p_36%3A10000-
# 100-200
# https://www.amazon.com/s?k=rice+cooker&i=garden&rh=p_36%3A10000-20000


# https://www.amazon.com/s?k=rice+cooker&i=garden&rh=p_36%3A10000-&qid=1602158374&rnid=386465011&ref=sr_nr_p_36_5
# https://www.amazon.com/s?k=rice+cooker&i=garden&rh=p_36%3A10000-&qid=1602158374&rnid=386465011&ref=sr_nr_p_36_5