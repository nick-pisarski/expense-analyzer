from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple

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


class CategorySummary:
    """data class for storing category summary"""

    category: Category
    sub_categories: dict[Category, float]
    transactions: list[ReportDataItem] = []

    def __init__(self, category: Category, transactions: list[ReportDataItem]):
        self.category = category
        self.sub_categories = {}
        self.transactions = transactions

        for transaction in transactions:
            if transaction.sub_category not in self.sub_categories:
                self.sub_categories[transaction.sub_category] = 0
            self.sub_categories[transaction.sub_category] += transaction.amount

    def __str__(self):
        return f"{self.category.name} - {self.expenses} - {self.incomes} - {len(self.transactions)}"

    @property
    def expenses(self) -> float:
        """Get the total expenses"""
        return sum(transaction.amount for transaction in self.transactions if transaction.amount < 0)

    @property
    def incomes(self) -> float:
        """Get the total incomes"""
        return sum(transaction.amount for transaction in self.transactions if transaction.amount > 0)


class OverviewSummary:
    """data class for storing overview summary"""

    category_summaries: Dict[Category, CategorySummary]

    def __init__(self, category_summaries: Dict[Category, CategorySummary]):
        self.category_summaries = category_summaries

    @property
    def total_expenses(self) -> float:
        """Get the total expenses"""
        total_expenses = 0
        for category_summary in self.category_summaries.values():
            total_expenses += category_summary.expenses
        return total_expenses

    @property
    def total_incomes(self) -> float:
        """Get the total incomes"""
        total_incomes = 0
        for category_summary in self.category_summaries.values():
            total_incomes += category_summary.incomes
        return total_incomes

    @property
    def net_balance(self) -> float:
        """Get the net balance"""
        return self.total_incomes - abs(self.total_expenses)


@dataclass
class AverageMonthSummary:
    """data class for storing average month summary"""

    estimated_total_expenses: float
    category_summaries: Dict[Category, float]


@dataclass
class ReportData:
    """Data class for storing report data"""

    year: int
    # Data for pie charts
    per_month_data: Dict[str, OverviewSummary]
    per_year_data: OverviewSummary
    average_month: AverageMonthSummary

    highest_spending_month: Tuple[str, float]
    lowest_spending_month: Tuple[str, float]
    highest_spending_vendor: Tuple[str, float]

    top_vendors: List[VendorSummary]
    top_expenses: List[ReportDataItem]

    total_amount: float
    total_transactions: int

    def get_transactions(self) -> List[ReportDataItem]:
        """Get all transactions"""
        transactions = [
            transaction
            for category_summary in self.per_year_data.category_summaries.values()
            for transaction in category_summary.transactions
        ]
        # sort by date
        transactions.sort(key=lambda x: x.date)

        return transactions
