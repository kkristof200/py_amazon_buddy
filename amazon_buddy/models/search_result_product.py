# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import Optional

# Pip
from jsoncodable import JSONCodable

# -------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------- class: Product -------------------------------------------------------- #

class SearchResultProduct(JSONCodable):

    # --------------------------------------------------------- Init --------------------------------------------------------- #

    def __init__(
        self,
        domain: str,
        asin: str,
        title: str,
        price: float,
        rating: Optional[float],
        review_count: int
    ):
        self.asin = asin
        self.url = 'https://{}/dp/{}'.format(domain, asin)

        self.title = title
        self.price = price
        self.rating = rating
        self.review_count = review_count


# -------------------------------------------------------------------------------------------------------------------------------- #