from amazon_buddy import AmazonBuddy, Category, SortType
from randomua import RandomUA

products = AmazonBuddy.search_products(
    'electric bike',
    category=Category.ALL_DEPARTMENTS,
    sort_type=SortType.REVIEW_RANK,
    min_rating=3.0,
    min_price=24.99,
    min_reviews=3,
    max_results=1000,
    user_agent=RandomUA.firefox(),
    debug=True
)
print(len(products))

print(AmazonBuddy.get_related_searches('electric bike', category=Category.ALL_DEPARTMENTS, user_agent=RandomUA.firefox(), debug=True))

reviews = AmazonBuddy.get_reviews(asin='B07PBKYGMR', user_agent=RandomUA.random(), debug=True)
print(len(reviews))