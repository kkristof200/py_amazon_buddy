from amazon_buddy import Product, AmazonBuddy, Category, SortType
from fake_useragent import UserAgent

ua = UserAgent()
ab = AmazonBuddy(
    debug=False,
    user_agent=ua.random,
    use_cloudscrape=True,
    set_us_address=True,
)
# # products = ab.search_products(
# #     'face wash',
# #     sort_type=SortType.PRICE_HIGH_TO_LOW,
# #     min_price=0,
# #     category=Category.BEAUTY_AND_PERSONAL_CARE,
# #     max_results=20
# # )
# # print(len(products))
asin = 'B08WJ3GYC9'

# d = ab.get_product_details(asin=asin)
d = ab.get_product_reviews_with_images(asin=asin)
# d = ab.get_related_searches(asin=asin)
print(d)

# ab.get_product_details(asin).save('{}.json'.format(asin))
# ab.get_product_details(asin).jsonprint()

# Product.load('/Users/kristofk/github/py_amazon_buddy/B0758GYJK2.json').jsonprint()