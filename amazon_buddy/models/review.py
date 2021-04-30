# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import List

# Pip
from jsoncodable import JSONCodable

# -------------------------------------------------------------------------------------------------------------------------------- #



# --------------------------------------------------------- class: Review -------------------------------------------------------- #

class Review(JSONCodable):

    # --------------------------------------------------------- Init --------------------------------------------------------- #

    def __init__(
        self,
        id: str,
        reviewer_name: str,
        rating: int,
        upvotes: int,
        title: str,
        text: str,
        language: str,
        foreign: bool,
        image_urls: List[str]
    ):
        self.id = id
        self.reviewer_name = reviewer_name
        self.rating = rating
        self.upvotes = upvotes
        self.title = title
        self.text = text
        self.language = language
        self.foreign = foreign
        self.image_urls = image_urls


    # --------------------------------------------------- Public properties -------------------------------------------------- #

    @property
    def has_images(self) -> bool:
        return len(self.image_urls) > 0


# -------------------------------------------------------------------------------------------------------------------------------- #