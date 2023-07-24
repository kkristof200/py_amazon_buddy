# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# Pip
from jsoncodable import JSONCodable
from typing import List, Optional

# -------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------ class: ReviewImage ------------------------------------------------------ #

class ReviewImage(JSONCodable):

    # --------------------------------------------------------- Init --------------------------------------------------------- #

    def __init__(
        self,
        author: str,
        title: str,
        text: str,
        rating: int,
        image_urls: List[str],
        upvotes: int
    ):
        self.author = author
        self.title = title
        self.text = text
        self.rating = rating
        self.image_urls = image_urls
        self.upvotes = upvotes


# -------------------------------------------------------------------------------------------------------------------------------- #