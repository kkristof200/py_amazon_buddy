# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from typing import Optional, List, Dict, Union

# Pip
from jsoncodable import JSONCodable

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------------ class: Product ------------------------------------------------------------ #

class Product(JSONCodable):

    # ------------------------------------------------------------- Init ------------------------------------------------------------- #

    def __init__(
        self,
        title: str,
        price: float,
        categories: List[str],
        features: List[str],
        details: Dict[str, str],
        images: Dict[str, Dict[str, Union[str, List[str]]]],
        video_urls: List[str]
    ):
        self.title = title
        self.price = price
        self.categories = categories
        self.features = features
        self.details = details
        self.video_urls = video_urls
        self.images = {}
        self.asins = []
        self.image_urls = []

        for asin, image_dict in images.items():
            self.asins.append(asin)

            image_urls = image_dict['image_urls']
            self.images[asin] = ProductImageSet(asin, image_dict['name'], image_urls)
            
            for image_url in image_urls:
                if image_url not in self.image_urls:
                    self.image_urls.append(image_url)

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------- class: ProductImageSet -------------------------------------------------------- #

class ProductImageSet(JSONCodable):

    # ------------------------------------------------------------- Init ------------------------------------------------------------- #

    def __init__(
        self,
        asin: str,
        name: str,
        urls: List[str]
    ):
        self.asin = asin
        self.name = name
        self.urls = urls


# ---------------------------------------------------------------------------------------------------------------------------------------- #