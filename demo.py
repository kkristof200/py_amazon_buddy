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
