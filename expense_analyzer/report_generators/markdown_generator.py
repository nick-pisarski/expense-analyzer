from typing import List, Dict
from expense_analyzer.models.expense_report_data import ExpenseReportData
from expense_analyzer.models.transaction import Transaction


class MarkdownExpenseReportGenerator:
    """Generate a markdown expense report"""

    def __init__(self, expense_report_data: ExpenseReportData):
        self.expense_report_data = expense_report_data

    def generate_report(self) -> str:
        """Generate a markdown expense report"""
        md = self._generate_report_header()
        md += self._generate_summary()
        md += self._generate_transaction_table(self.expense_report_data.top_expenses, "Top Expenses")
        md += self._generate_amount_by_vendor_table(self.expense_report_data.amount_by_vendor)
        md += self._generate_transaction_table(self.expense_report_data.transactions, "Transactions")
        return md

    def _generate_report_header(self) -> str:
        """Generate a markdown report header"""
        return f"""# Expense Report """

    def _generate_summary(self) -> str:
        """Generate a markdown summary"""
        return f"""# Expense Report
## Summary

- Period:             {self.expense_report_data.start_date.strftime('%m/%d/%Y')} - {self.expense_report_data.end_date.strftime('%m/%d/%Y')}
- Total Transactions: {self.expense_report_data.total_transactions}
- Total Expenses:     $({abs(self.expense_report_data.total_expenses):.2f})
- Total Paid:         ${self.expense_report_data.total_income:.2f}

"""

    def _generate_transaction_table(self, transactions: List[Transaction], title: str) -> str:
        """Generate a markdown table of transactions"""
        md = f"## {title}\n"
        md += "| Date | Description | Amount |\n"
        md += "|------|-------------|--------|\n"
        for transaction in transactions:
            md += f"| {transaction.date_obj.strftime('%Y-%m-%d')} | {transaction.description} | ${transaction.absolute_amount:.2f} |\n"
        return md

    def _generate_amount_by_vendor_table(self, amount_by_vendor: Dict[str, float]) -> str:
        """Generate a markdown table of amounts by vendor"""
        md = "## Amount by Vendor\n"
        md += "| Vendor | Amount |\n"
        md += "|--------|--------|\n"
        for vendor, amount in amount_by_vendor.items():
            md += f"| {vendor} | ${amount:.2f} |\n"
        return md
