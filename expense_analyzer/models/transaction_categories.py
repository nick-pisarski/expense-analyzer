from enum import Enum
from typing import List


class TransactionCategory(Enum):
    """Categories for transactions"""

    CHILDCARE = "Childcare"
    HEALTHCARE = "Healthcare"
    FOOD_AND_BEVERAGE = "Food and Beverage"

    ENTERTAINMENT = "Entertainment"
    HOUSING_MORTGAGE = "Housing (Mortgage and Taxes)"
    HOUSING_OTHER = "Housing Other (Utilities, repairs, etc.)"
    PERSONAL_CARE = "Personal Care (Charity, Misc, Other, etc.)"
    TRANSPORTATION = "Transportation (Gas, Car, etc.)"
    SAVINGS_AND_INSURANCE = "Savings and Personal Insurance (401k, IRA, etc.)"
    MISCELLANEOUS = "Miscellaneous"


class TransactionSubCategory(Enum):
    """Subcategories for transactions"""

    # HOUSING_MORTGAGE
    MORTGAGE = "Mortgage and Escrow"
    FLOOD_INSURANCE = "Flood Insurance"

    # HOUSING_OTHER
    CELL_PHONE = "Cell Phone"
    ELECTRICITY = "Electricity"
    CABLE_INTERNET = "Cable/Internet"
    MAIDS = "Maid Service"
    NATURAL_GAS = "Natural Gas"
    WATER_AND_SEWER = "Water and Sewer"

    # TRANSPORTATION
    CAR_LOAN = "Car Loan"
    CAR_INSURANCE = "Car Insurance"
    CAR_REGISTRATION = "Car Registration"
    CAR_GAS = "Car Gas"
    PUBLIC_TRANSPORTATION = "Public Transportation (E-Z Pass, etc.)"

    # Entertainment
    SUBSCRIPTIONS = "Subscriptions"

    # Childcare
    CHILDCARE_SHCOOL = "Childcare/School Tuition"

    # Food and Beverage
    EATING_OUT = "Eating Out"
    GROCERIES = "Groceries"
    PET_FOOD = "Pet Food"
    COSTCO = "Costco"

    # Healthcare
    PET_HEALTHCARE = "Pet Healthcare"
    HSA_NICK = "HSA/Dental (Nick)"
    HSA_SYDNEY = "HSA (Sydney)"

    # Personal Care
    BEAUTY = "Beauty (Hair, Nails, etc.)"
    AMAZON = "Amazon"
    TARGET = "Target"

    # Savings and Insurance
    LIFE_INSURANCE_NICK = "Life Insurance (Nick)"
    LIFE_INSURANCE_SYDNEY = "Life Insurance (Sydney)"
    SAVINGS_HOUSE = "Savings (House)"
    SAVINGS_PERSONAL = "Savings (Personal)"
    SAVINGS_529_EVERETT = "Savings (529 Everett)"
    SAVINGS_529_AVA = "Savings (529 Ava)"
    RETIREMENT_401K_NICK = "Retirement (401k) (Nick)"
    RETIREMENT_401K_SYDNEY = "Retirement (401k) (Sydney)"
    RETIREMENT_IRA_NICK = "Retirement (IRA) (Nick)"
    RETIREMENT_IRA_SYDNEY = "Retirement (IRA) (Sydney)"
    NON_RETIREMENT_ACCOUNT = "Non-Retirement Account"
    ESPP = "ESPP"

    # Other
    MISCELLANEOUS = "Miscellaneous"

    @classmethod
    def get_all_categories(cls) -> List[str]:
        """Get all categories as a list of strings"""
        return [category.value for category in cls]


# Map of each transaction subcategories to categories
TRANSACTION_SUBCATEGORY_TO_CATEGORY = {
    TransactionSubCategory.MORTGAGE: TransactionCategory.HOUSING_MORTGAGE,
    TransactionSubCategory.FLOOD_INSURANCE: TransactionCategory.HOUSING_MORTGAGE,
    TransactionSubCategory.CELL_PHONE: TransactionCategory.HOUSING_OTHER,
    TransactionSubCategory.ELECTRICITY: TransactionCategory.HOUSING_OTHER,
    TransactionSubCategory.CABLE_INTERNET: TransactionCategory.HOUSING_OTHER,
    TransactionSubCategory.MAIDS: TransactionCategory.HOUSING_OTHER,
    TransactionSubCategory.NATURAL_GAS: TransactionCategory.HOUSING_OTHER,
    TransactionSubCategory.WATER_AND_SEWER: TransactionCategory.HOUSING_OTHER,
    TransactionSubCategory.CAR_LOAN: TransactionCategory.TRANSPORTATION,
    TransactionSubCategory.CAR_INSURANCE: TransactionCategory.TRANSPORTATION,
    TransactionSubCategory.CAR_REGISTRATION: TransactionCategory.TRANSPORTATION,
    TransactionSubCategory.CAR_GAS: TransactionCategory.TRANSPORTATION,
    TransactionSubCategory.PUBLIC_TRANSPORTATION: TransactionCategory.TRANSPORTATION,
    TransactionSubCategory.SUBSCRIPTIONS: TransactionCategory.ENTERTAINMENT,
    TransactionSubCategory.CHILDCARE_SHCOOL: TransactionCategory.CHILDCARE,
    TransactionSubCategory.EATING_OUT: TransactionCategory.FOOD_AND_BEVERAGE,
    TransactionSubCategory.GROCERIES: TransactionCategory.FOOD_AND_BEVERAGE,
    TransactionSubCategory.PET_FOOD: TransactionCategory.FOOD_AND_BEVERAGE,
    TransactionSubCategory.COSTCO: TransactionCategory.FOOD_AND_BEVERAGE,
    TransactionSubCategory.PET_HEALTHCARE: TransactionCategory.HEALTHCARE,
    TransactionSubCategory.HSA_NICK: TransactionCategory.HEALTHCARE,
    TransactionSubCategory.HSA_SYDNEY: TransactionCategory.HEALTHCARE,
    TransactionSubCategory.BEAUTY: TransactionCategory.PERSONAL_CARE,
    TransactionSubCategory.AMAZON: TransactionCategory.PERSONAL_CARE,
    TransactionSubCategory.TARGET: TransactionCategory.PERSONAL_CARE,
    TransactionSubCategory.LIFE_INSURANCE_NICK: TransactionCategory.SAVINGS_AND_INSURANCE,
    TransactionSubCategory.LIFE_INSURANCE_SYDNEY: TransactionCategory.SAVINGS_AND_INSURANCE,
    TransactionSubCategory.SAVINGS_HOUSE: TransactionCategory.SAVINGS_AND_INSURANCE,
    TransactionSubCategory.SAVINGS_PERSONAL: TransactionCategory.SAVINGS_AND_INSURANCE,
    TransactionSubCategory.SAVINGS_529_EVERETT: TransactionCategory.SAVINGS_AND_INSURANCE,
    TransactionSubCategory.SAVINGS_529_AVA: TransactionCategory.SAVINGS_AND_INSURANCE,
    TransactionSubCategory.RETIREMENT_401K_NICK: TransactionCategory.SAVINGS_AND_INSURANCE,
    TransactionSubCategory.RETIREMENT_401K_SYDNEY: TransactionCategory.SAVINGS_AND_INSURANCE,
    TransactionSubCategory.RETIREMENT_IRA_NICK: TransactionCategory.SAVINGS_AND_INSURANCE,
    TransactionSubCategory.RETIREMENT_IRA_SYDNEY: TransactionCategory.SAVINGS_AND_INSURANCE,
    TransactionSubCategory.NON_RETIREMENT_ACCOUNT: TransactionCategory.SAVINGS_AND_INSURANCE,
    TransactionSubCategory.ESPP: TransactionCategory.SAVINGS_AND_INSURANCE,
    TransactionSubCategory.MISCELLANEOUS: TransactionCategory.MISCELLANEOUS,
}


def get_category_from_subcategory(subcategory: TransactionSubCategory) -> TransactionCategory:
    """Get the category from the subcategory"""
    return TRANSACTION_SUBCATEGORY_TO_CATEGORY[subcategory]


def get_subcategories_from_category(category: TransactionCategory) -> List[TransactionSubCategory]:
    """Get all subcategories from the category"""
    return [
        subcategory
        for subcategory in TransactionSubCategory
        if TRANSACTION_SUBCATEGORY_TO_CATEGORY[subcategory] == category
    ]
