import logging
from datetime import datetime
from typing import Dict, List, Tuple

from expense_analyzer.database.connection import get_db
from expense_analyzer.database.models import Category, Transaction, VendorSummary
from expense_analyzer.database.repositories.category_repository import (
    CategoryRepository,
)
from expense_analyzer.database.repositories.transaction_category_repository import (
    TransactionCategoryRepository,
)
from expense_analyzer.database.repositories.transaction_view_repository import (
    TransactionViewRepository,
)
from expense_analyzer.models.reports import CategorySummary, OverviewSummary, ReportData, ReportDataItem


class ReportService:
    """Service for generating report data"""

    def __init__(self):
        self.logger = logging.getLogger("expense_analyzer.services.report_service")
        self.db = get_db()
        self.transaction_view_repository = TransactionViewRepository(self.db)
        self.repository = TransactionCategoryRepository(self.db)
        self.category_repository = CategoryRepository(self.db)

    def generate_report_data(self, year=datetime.now().year) -> ReportData:
        """Generate report data"""
        # Get transactions for the year
        categories = self.category_repository.get_all_categories()
        transaction_views = self.repository.get_transactions_by_year(year)
        transactions = [
            self._map_transaction_to_report_data_item(transaction, categories) for transaction in transaction_views
        ]

        return ReportData(
            year=year,
            per_month_data=self._get_per_month_data_for_year(transactions),
            per_year_data=self._get_per_year_data(transactions),
            average_month=self._get_average_month(),
            highest_spending_month=self._get_highest_spending_month(),
            highest_spending_vendor=self._get_highest_spending_vendor(),
            top_vendors=self._get_top_vendors(),
            top_expenses=self._get_top_expenses(categories),
            total_amount=self._get_total_expenses(transactions),
            total_transactions=len(transactions),
        )

    def _get_total_expenses(self, transactions: List[ReportDataItem]) -> float:
        """Get the total expenses"""
        total_expenses = 0
        for transaction in transactions:
            if transaction.amount < 0:
                total_expenses += abs(transaction.amount)
        return total_expenses

    def _map_transaction_to_report_data_item(
        self, transaction: Transaction, categories: List[Category]
    ) -> ReportDataItem:
        category = next((c for c in categories if c.id == transaction.category_id), None)
        parent_category = next((c for c in categories if c.id == category.parent_id), None)

        return ReportDataItem(
            date=transaction.date,
            amount=transaction.amount,
            category=parent_category,
            sub_category=category,
            vendor=transaction.vendor,
        )

    def _get_top_vendors(self) -> List[VendorSummary]:
        """Get the top 5 vendors by expense amount"""
        vendors = self.repository.get_top_vendors(limit=10)
        return vendors

    def _get_top_expenses(self, categories: List[Category]) -> List[ReportDataItem]:
        """Get the top 5 expenses by amount"""
        expenses = self.repository.get_top_expenses(limit=10)
        return [self._map_transaction_to_report_data_item(transaction, categories) for transaction in expenses]

    def _get_average_month(self) -> Dict[Category, CategorySummary]:
        """Get the average month data"""
        return {}

    def _get_highest_spending_month(self) -> Tuple[str, float]:
        """Get the highest spending month"""
        return {}

    def _get_highest_spending_vendor(self) -> Tuple[str, float]:
        """Get the highest spending vendor"""
        return {}

    def _get_category_summaries(self, transactions: List[ReportDataItem]) -> Dict[Category, CategorySummary]:
        """Get the category summaries"""
        # Group transactions by category
        category_summaries = {}
        for transaction in transactions:
            if transaction.category not in category_summaries:
                category_summaries[transaction.category] = []
            category_summaries[transaction.category].append(transaction)
        # Create a dictionary of category summaries
        category_summaries = {
            category: CategorySummary(category, transactions) for category, transactions in category_summaries.items()
        }
        return category_summaries

    def _get_per_month_data_for_year(
        self, transactions: List[ReportDataItem]
    ) -> Dict[str, OverviewSummary]:
        """Get the per month data for a given year"""
        # Group transactions by month
        per_month_transactions = {}
        for transaction in transactions:
            month = transaction.date.strftime("%B")  # Get month name
            if month not in per_month_transactions:
                per_month_transactions[month] = []
            per_month_transactions[month].append(transaction)

        # Sum the transactions by category
        per_month_data = {}
        for month, transactions in per_month_transactions.items():
            per_month_data[month] = OverviewSummary(self._get_category_summaries(transactions))

        return per_month_data

    def _get_per_year_data(self, transactions: List[ReportDataItem]) -> OverviewSummary:
        """Get the per year data"""
        return OverviewSummary(self._get_category_summaries(transactions))
