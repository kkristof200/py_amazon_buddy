# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from typing import Optional, List, Dict, Union

# Pip
from jsoncodable import JSONCodable

# Local
from .product_image_set import ProductImageSet
from .product_video import ProductVideo
from .product_detail import ProductDetail

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------------ class: Product ------------------------------------------------------------ #

class Product(JSONCodable):

    # ------------------------------------------------------------- Init ------------------------------------------------------------- #

    def __init__(
        self,
        title: str,
        asin: str,
        price: float,
        categories: List[str],
        features: List[str],
        details: Dict[str, str],
        images: Dict[str, Dict[str, Union[str, List[str]]]],
        videos_details: List[Dict[str, Union[str, int]]]
    ):
        self.title = title
        self.asin = asin
        self.price = price
        self.categories = categories or []
        self.features = features or []
        self.videos = []
        self.video_urls = []
        self.images = {}
        self.associated_asins = []
        self.asins = [asin]
        self.image_urls = []

        self.details = [ProductDetail(k, v) for k, v in details.items()]

        if images:
            for assoc_asin, image_dict in images.items():
                if assoc_asin != asin:
                    self.associated_asins.append(assoc_asin)

                if assoc_asin not in self.asins:
                    self.asins.append(assoc_asin)

                if image_dict is not None and 'image_urls' in image_dict:
                    image_urls = image_dict['image_urls']
                    self.images[assoc_asin] = ProductImageSet(assoc_asin, image_dict['name'], image_urls)

                    for image_url in image_urls:
                        if image_url not in self.image_urls:
                            self.image_urls.append(image_url)

        if videos_details:
            for video in videos_details:
                if 'title' in video and 'height' in video and 'width' in video and 'url' in video:
                    self.videos.append(ProductVideo(video['url'], video['title'], video['height'], video['width']))
                    self.video_urls.append(video['url'])


# ---------------------------------------------------------------------------------------------------------------------------------------- #