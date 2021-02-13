# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from typing import Optional, List

# Local
from ..models import SearchResultProduct

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# --------------------------------------------------------- class: ProductFilter --------------------------------------------------------- #

class ProductFilter:

    # ------------------------------------------------------------- Init ------------------------------------------------------------- #

    def __init__(
        self,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        min_reviews: Optional[int] = None,
        ignored_asins: Optional[List[str]] = None,
        ignored_title_strs: Optional[List[str]] = None
    ):
        self.min_price = min_price or 0
        self.max_price = max_price or 9999999999999
        self.min_rating = min_rating or 0
        self.min_reviews = min_reviews or 0
        self.ignored_asins = [ia.lower() for ia in ignored_asins] if ignored_asins else []
        self.ignored_title_strs = [ts.lower() for ts in ignored_title_strs] if ignored_title_strs else []


    # -------------------------------------------------------- Public methods -------------------------------------------------------- #

    def filter(self, products: List[SearchResultProduct]) -> List[SearchResultProduct]:
        filtered = []

        for p in products:
            try:
                if p.price < self.min_price:
                    # print(p.price, '<', self.min_price)
                    continue
                elif p.price > self.max_price:
                    # print(p.price, '>', self.min_price)
                    continue
                elif p.rating < self.min_rating:
                    # print(p.rating, '<', self.min_rating)
                    continue
                elif p.review_count < self.min_reviews:
                    # print(p.review_count, '<', self.min_reviews)
                    continue
                elif p.asin.lower() in self.ignored_asins:
                    # print('ignored asin', p.asin)
                    continue
                elif self.__contains_in(p.title, self.ignored_title_strs):
                    # print('ignored title str', p.title)
                    continue

                filtered.append(p)

                # if p.price >= self.min_price and p.price <= self.max_price and p.rating >= self.min_rating and p.review_count >= self.min_reviews and p.asin.lower() not in self.ignored_asins and not self.__contains_in(p.title, self.ignored_title_strs):
                #     filtered.append(p)
            except:
                pass

            self.ignored_asins.append(p.asin.lower())

        return filtered


    # ------------------------------------------------------- Private methods -------------------------------------------------------- #

    @staticmethod
    def __contains_in(s: str, strs: List[str]) -> bool:
        s = s.lower()

        for ss in strs:
            if ss in s:
                return True

        return False


# ---------------------------------------------------------------------------------------------------------------------------------------- #