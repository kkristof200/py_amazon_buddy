from amazon_buddy import Product, AmazonBuddy, Category, SortType

ab = AmazonBuddy(debug=True, user_agent='ADD_USER_AGENT')

# # products = ab.search_products(
# #     'face wash',
# #     sort_type=SortType.PRICE_HIGH_TO_LOW,
# #     min_price=0,
# #     category=Category.BEAUTY_AND_PERSONAL_CARE,
# #     max_results=20
# # )
# # print(len(products))
asin = 'B07RZV9LB7'

# # reviews = ab.get_reviews(asin=asin)
# # print(reviews)

ab.get_product_details(asin).save('{}.json'.format(asin))
# ab.get_product_details(asin).jsonprint()

# Product.load('/Users/kristofk/github/py_amazon_buddy/B0758GYJK2.json').jsonprint()