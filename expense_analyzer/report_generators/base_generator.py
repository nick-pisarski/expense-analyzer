from abc import ABC, abstractmethod
from typing import Any, List
from expense_analyzer.models.reports import ReportData


class ExpenseReportGenerator(ABC):
    """Base class for expense report generators"""

    @abstractmethod
    def generate_report(self, expense_report_data: ReportData, verbose: bool = False) -> str:
        """Generate a report"""
        pass

    @abstractmethod
    def generate_transaction_table(self, report_data: ReportData) -> str:
        """Generate a transaction table"""
        pass
