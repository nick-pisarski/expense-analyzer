from typing import List
from datetime import datetime

from expense_analyzer.models.transaction import Transaction
from dataclasses import dataclass


@dataclass
class ExpenseReportData:
    """Data class for expense report"""

    start_date: datetime
    end_date: datetime
    total_transactions: int
    total_expenses: float
    total_income: float
    top_expenses: List[Transaction]

    def _generate_transaction_table(self, transactions: List[Transaction]) -> str:
        """Generate a markdown table of transactions"""
        md = "| Date | Description | Amount |\n"
        md += "|------|-------------|--------|\n"
        for transaction in transactions:
            md += f"| {transaction.date_obj.strftime('%Y-%m-%d')} | {transaction.description} | ${transaction.absolute_amount:.2f} |\n"
        return md

    def to_markdown(self) -> str:
        """Convert the expense report data to a markdown string"""
        md = f"""# Expense Report

## Summary

- Period:             {self.start_date.strftime('%m/%d/%Y')} - {self.end_date.strftime('%m/%d/%Y')}
- Total Transactions: {self.total_transactions}
- Total Expenses:     $({abs(self.total_expenses):.2f})
- Total Paid:         ${self.total_income:.2f}

## Top Expenses

"""
        md += self._generate_transaction_table(self.top_expenses)

        return md
