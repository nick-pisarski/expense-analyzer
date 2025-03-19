from typing import List, Dict, Tuple
from dataclasses import dataclass
import logging
from expense_analyzer.database.models import Category, VendorSummary
from expense_analyzer.database.repository import CategoryRepository, TransactionRepository, TransactionViewRepository
from expense_analyzer.database.connection import get_db


@dataclass
class ReportDataItem:
    """Data class for storing report data item"""

    date: str
    amount: float
    category: Category
    sub_category: Category
    vendor: str
    description: str

    def __str__(self):
        return f"{self.date} - {self.vendor} - {self.amount} - {self.sub_category.name}{self.category.name})"


@dataclass
class ReportData:
    """Data class for storing report data"""

    # Data for pie charts
    per_month_data: Dict[str, List[ReportDataItem]]
    per_year_data: Dict[str, List[ReportDataItem]]
    average_month: Dict[Category, float]

    highest_spending_month: Tuple[str, float]
    highest_spending_vendor: Tuple[str, float]

    top_vendors: List[VendorSummary]
    top_expenses: List[ReportDataItem]


class ReportService:
    """Service for generating report data"""

    def __init__(self):
        self.logger = logging.getLogger("expense_analyzer.services.report_service")
        self.db = get_db()
        self.transaction_view_repository = TransactionViewRepository(self.db)

    def generate_report_data(self) -> ReportData:
        per_month_data = {}
        per_year_data = {}
        average_month = {}
        highest_spending_month = {}
        highest_spending_vendor = {}
        top_vendors = self._get_top_vendors()
        top_expenses = self._get_top_expenses()

        return ReportData(
            per_month_data,
            per_year_data,
            average_month,
            highest_spending_month,
            highest_spending_vendor,
            top_vendors,
            top_expenses,
        )

    def _get_top_vendors(self) -> List[VendorSummary]:
        """Get the top 5 vendors by expense amount"""
        vendors = self.transaction_view_repository.get_top_vendors(limit=5)
        return vendors

    def _get_top_expenses(self) -> List[ReportDataItem]:
        """Get the top 5 expenses by amount"""
        expenses = self.transaction_view_repository.get_top_expenses(limit=10)
        return expenses

    def _get_average_month(self) -> Dict[Category, float]:
        pass

    def _get_highest_spending_month(self) -> Tuple[str, float]:
        pass

    def _get_highest_spending_vendor(self) -> Tuple[str, float]:
        pass

    def _get_per_month_data(self) -> Dict[str, List[ReportDataItem]]:
        pass
