# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import Optional

# Pip
from jsoncodable import JSONCodable

# -------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------ class: BaseProduct ------------------------------------------------------ #

class BaseProduct(JSONCodable):

    # --------------------------------------------------------- Init --------------------------------------------------------- #

    def __init__(
        self,
        title: str,
        asin: str,
        price: float,
        main_image_url: Optional[str] = None
    ):
        self.title = title
        self.asin = asin
        self.price = price
        self.main_image_url = main_image_url
        self.main_image_url_160 = None
        self.main_image_url_500 = None

        if main_image_url:
            image_id = main_image_url.split('/I/')[1].split('.')[0]
            image_url_format = 'https://m.media-amazon.com/images/I/{}._SL{{}}_.jpg'.format(image_id)

            self.main_image_url_160 = image_url_format.format('160')
            self.main_image_url_500 = image_url_format.format('500')


# -------------------------------------------------------------------------------------------------------------------------------- #