from abc import ABC, abstractmethod

from expense_analyzer.models.reports import ReportData


class ExpenseReportGenerator(ABC):
    """Base class for expense report generators"""

    @abstractmethod
    def generate_report(self, expense_report_data: ReportData) -> str:
        """Generate a report"""
        pass
