from abc import ABC, abstractmethod
from expense_analyzer.models.expense_report_data import ExpenseReportData


class ExpenseReportGenerator(ABC):
    """Base class for expense report generators"""

    @abstractmethod
    def generate_report(self, expense_report_data: ExpenseReportData) -> str:
        """Generate a report"""
        pass
