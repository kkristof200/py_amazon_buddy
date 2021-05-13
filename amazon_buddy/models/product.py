# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import Optional, List, Dict, Union

# Local
from .base_product import BaseProduct
from .product_image_set import ProductImageSet
from .product_video import ProductVideo
from .product_detail import ProductDetail

# -------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------- class: Product -------------------------------------------------------- #

class Product(BaseProduct):

    # --------------------------------------------------------- Init --------------------------------------------------------- #

    def __init__(
        self,
        title: str,
        asin: str,
        price: float,
        categories: List[str],
        features: List[str],
        descripton: Optional[str],
        details: Dict[str, str],
        images: Dict[str, Dict[str, Union[str, List[str]]]],
        videos_details: List[Dict[str, Union[str, int]]],
        related_products: List[BaseProduct],
        similar_products: Dict[str, Dict[str, any]]
    ):
        main_image_url = None
        associated_asins = []
        asins = [asin]
        _images = {}
        image_urls = []

        if images:
            for assoc_asin, image_dict in images.items():
                if assoc_asin != asin:
                    associated_asins.append(assoc_asin)

                if assoc_asin not in asins:
                    asins.append(assoc_asin)

                if image_dict and 'image_urls' in image_dict:
                    _image_urls = image_dict['image_urls']
                    _images[assoc_asin] = ProductImageSet(assoc_asin, image_dict['name'], image_urls)

                    for image_url in _image_urls:
                        if image_url not in image_urls:
                            image_urls.append(image_url)

                        if not main_image_url and (assoc_asin == asin or asin not in images.keys()):
                            main_image_url = image_url

        super().__init__(title, asin, price, main_image_url)

        self.related_products = related_products
        self.similar_products = similar_products

        self.asins = asins
        self.associated_asins = associated_asins
        self.images = _images
        self.image_urls = image_urls

        self.categories = categories or []
        self.features = features or []
        self.videos = []
        self.video_urls = []

        self.details = [ProductDetail(k, v) for k, v in details.items()]

        if videos_details:
            for video in videos_details:
                if 'title' in video and 'height' in video and 'width' in video and 'url' in video:
                    self.videos.append(ProductVideo(video['url'], video['title'], video['height'], video['width']))
                    self.video_urls.append(video['url'])


# -------------------------------------------------------------------------------------------------------------------------------- #