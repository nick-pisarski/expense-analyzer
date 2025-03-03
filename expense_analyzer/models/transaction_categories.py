from enum import Enum
from typing import List


class TransactionCategory(Enum):
    """Categories for transactions"""

    EATING_OUT = "Eating Out"
    GROCERIES = "Groceries"
    GAS = "Gas"
    CHILDCARE = "Childcare"
    HEALTHCARE = "Healthcare"
    PERSONAL = "Personal"
    BEAUTY = "Beauty"

    # Shopping
    AMAZON = "Amazon"
    TARGET = "Target"

    # Pets
    PET_FOOD = "Pet Food"
    PET_HEALTHCARE = "Pet Healthcare"

    # Home
    HOME = "Home"
    CAR = "Car"
    CAR_INSURANCE = "Car Insurance"

    # Maid Service
    MAIDS = "Maid Service"

    # Subscriptions
    SUBSCRIPTIONS = "Subscriptions"

    # Other
    MISCELLANEOUS = "Miscellaneous"

    @classmethod
    def get_all_categories(cls) -> List[str]:
        """Get all categories as a list of strings"""
        return [category.value for category in cls]
