from typing import List, Dict
from expense_analyzer.models.expense_report_data import ExpenseReportData
from expense_analyzer.models.transaction import Transaction
from expense_analyzer.report_generators.base_generator import ExpenseReportGenerator


class MarkdownExpenseReportGenerator(ExpenseReportGenerator):
    """Generate a markdown expense report"""

    def generate_report(self, expense_report_data: ExpenseReportData) -> str:
        """Generate a markdown expense report"""
        md = self._generate_report_header()
        md += self._generate_summary(expense_report_data)
        md += self._generate_transaction_table(expense_report_data.top_expenses, "Top Expenses")
        md += self._generate_amount_by_vendor_table(expense_report_data.amount_by_vendor)
        md += self._generate_transaction_table(expense_report_data.transactions, "Transactions")
        return md

    def _generate_report_header(self) -> str:
        """Generate a markdown report header"""
        return f"""# Expense Report """

    def _generate_summary(self, expense_report_data: ExpenseReportData) -> str:
        """Generate a markdown summary"""
        return f"""# Expense Report
## Summary

- Period:             {expense_report_data.start_date.strftime('%m/%d/%Y')} - {expense_report_data.end_date.strftime('%m/%d/%Y')}
- Total Transactions: {expense_report_data.total_transactions}
- Total Expenses:     $({abs(expense_report_data.total_expenses):.2f})
- Total Paid:         ${expense_report_data.total_income:.2f}

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
