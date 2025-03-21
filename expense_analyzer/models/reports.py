from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
from expense_analyzer.database.models import Category, VendorSummary


@dataclass
class ReportDataItem:
    """Data class for storing report data item"""

    date: datetime
    amount: float
    category: Category
    sub_category: Category
    vendor: str

    def __str__(self):
        return f"{self.date} - {self.vendor} - {self.amount} - {self.sub_category.name}{self.category.name})"


@dataclass
class ReportData:
    """Data class for storing report data"""

    year: int
    # Data for pie charts
    per_month_data: Dict[str, Dict[Category, float]]
    per_year_data: Dict[Category, float]
    average_month: Dict[Category, float]

    highest_spending_month: Dict[str, float]
    highest_spending_vendor: Dict[str, float]

    top_vendors: List[VendorSummary]
    top_expenses: List[ReportDataItem]

    total_amount: float
    total_transactions: int

class CategorySummary:
    """Data class for storing category summary"""

    category: Category
    amount: float
    sub_categories: Dict[Category, float]
    transactions: List[ReportDataItem]

    def __init__(self, category: Category, transactions: List[ReportDataItem]):
        self.category = category
        self.amount = 0
        self.sub_categories = {}
        self.transactions = []
        self.amount = sum(transaction.amount for transaction in transactions)
        self.transactions = transactions

        for transaction in transactions:
            if transaction.sub_category not in self.sub_categories:
                self.sub_categories[transaction.sub_category] = 0
            self.sub_categories[transaction.sub_category] += transaction.amount

    def __str__(self):
        return f"{self.category.name} - {self.amount} - {self.sub_categories}"