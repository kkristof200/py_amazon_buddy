# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from typing import Optional, List

# Local
from ..models import Review

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ---------------------------------------------------------- class: ReviewFilter --------------------------------------------------------- #

class ReviewFilter:

    # ------------------------------------------------------------- Init ------------------------------------------------------------- #

    def __init__(
        self,
        min_rating: Optional[int] = None,
        ignored_ids: Optional[List[str]] = None,
        ignore_foreign: bool = True
    ):
        self.min_rating = min_rating or 0
        self.ignored_ids = ignored_ids or []
        self.ignore_foreign = ignore_foreign


    # -------------------------------------------------------- Public methods -------------------------------------------------------- #

    def filter(self, reviews: List[Review]) -> List[Review]:
        filtered = []

        for r in reviews:
            r_id = r.id.lower()

            if r_id in self.ignored_ids:
                # print('includes')
                continue

            if r.rating < self.min_rating:
                # print('low rating')
                continue

            if self.ignore_foreign and r.foreign:
                continue

            self.ignored_ids.append(r_id)
            filtered.append(r)

        return filtered


# ---------------------------------------------------------------------------------------------------------------------------------------- #