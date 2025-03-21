from typing import List, Dict
from datetime import datetime

from expense_analyzer.models.transaction import ReportTransaction
from dataclasses import dataclass


@dataclass
class ExpenseReportData:
    """Data class for expense report"""

    start_date: datetime
    end_date: datetime
    total_transactions: int
    total_expenses: float
    total_income: float
    top_expenses: List[ReportTransaction]
    transactions: List[ReportTransaction]
    amount_by_vendor: Dict[str, float]
