from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from expense_analyzer.models.transaction import ReportTransaction


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
