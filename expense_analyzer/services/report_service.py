from datetime import datetime
from typing import List, Dict, Tuple
import logging
from expense_analyzer.database.models import Category, VendorSummary, TransactionView
from expense_analyzer.database.repository import TransactionViewRepository
from expense_analyzer.database.connection import get_db
from expense_analyzer.models.reports import ReportData, ReportDataItem, CategorySummary, VendorSummary


class ReportService:
    """Service for generating report data"""

    def __init__(self):
        self.logger = logging.getLogger("expense_analyzer.services.report_service")
        self.db = get_db()
        self.transaction_view_repository = TransactionViewRepository(self.db)

    def generate_report_data(self, year = datetime.now().year) -> ReportData:
        """Generate report data"""
        per_month_data = self._get_per_month_data_for_year(year)
        per_year_data = self._get_per_year_data(year)
        average_month = {}
        highest_spending_month = {}
        highest_spending_vendor = {}
        top_vendors = self._get_top_vendors()
        top_expenses = self._get_top_expenses()

        return ReportData(
            year,
            per_month_data,
            per_year_data,
            average_month,
            highest_spending_month,
            highest_spending_vendor,
            top_vendors,
            top_expenses,
        )
    def _map_transaction_to_report_data_item(self, transaction: TransactionView) -> ReportDataItem:
        return ReportDataItem(transaction.date, transaction.amount, transaction.parent_category_name, transaction.category_name, transaction.vendor, )

    def _get_top_vendors(self) -> List[VendorSummary]:
        """Get the top 5 vendors by expense amount"""
        vendors = self.transaction_view_repository.get_top_vendors(limit=5)
        return vendors

    def _get_top_expenses(self) -> List[ReportDataItem]:
        """Get the top 5 expenses by amount"""
        expenses = self.transaction_view_repository.get_top_expenses(limit=10)
        return [self._map_transaction_to_report_data_item(transaction) for transaction in expenses]

    def _get_average_month(self) -> Dict[Category, float]:
        pass

    def _get_highest_spending_month(self) -> Tuple[str, float]:
        pass

    def _get_highest_spending_vendor(self) -> Tuple[str, float]:
        pass


    def _get_category_summaries(self, transactions: List[ReportDataItem]) -> Dict[Category, CategorySummary]:
        """Get the category summaries"""
        #Group transactions by category
        category_summaries = {}
        for transaction in transactions:
            if transaction.category not in category_summaries:
                category_summaries[transaction.category] = []
            category_summaries[transaction.category].append(transaction)
        #Create a dictionary of category summaries
        category_summaries = {category: CategorySummary(category, transactions) for category, transactions in category_summaries.items()}
        return category_summaries

    def _get_per_month_data_for_year(self, year: int) -> Dict[str, Dict[Category, float]]:
        """Get the per month data for a given year"""
        # Initialize dictionary with all months
        per_month_data = {
            'January': [], 'February': [], 'March': [], 'April': [],
            'May': [], 'June': [], 'July': [], 'August': [],
            'September': [], 'October': [], 'November': [], 'December': []
        }

        # Get transactions for the year
        transactions = self.transaction_view_repository.get_transactions_by_year(year)
        transactions = [self._map_transaction_to_report_data_item(transaction) for transaction in transactions]
        # Group transactions by month
        for transaction in transactions:
            month = transaction.date.strftime('%B')  # Get month name
            per_month_data[month].append(transaction)

        # Sum the transactions by category
        for month in per_month_data:    
            per_month_data[month] = self._get_category_summaries(per_month_data[month])

        return per_month_data

    def _get_per_year_data(self, year: int) -> Dict[Category, float]:
        """Get the per year data"""
        transactions = self.transaction_view_repository.get_transactions_by_year(year)
        transactions = [self._map_transaction_to_report_data_item(transaction) for transaction in transactions]
        per_year_data = self._get_category_summaries(transactions)
        return per_year_data
    
    
