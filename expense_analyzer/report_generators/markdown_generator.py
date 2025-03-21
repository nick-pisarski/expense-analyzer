from typing import List, Dict
from expense_analyzer.database.models import VendorSummary
from expense_analyzer.models.reports import ReportData, ReportDataItem
from expense_analyzer.report_generators.base_generator import ExpenseReportGenerator


class MarkdownExpenseReportGenerator(ExpenseReportGenerator):
    """Generate a markdown expense report"""

    def generate_report(self, expense_report_data: ReportData) -> str:
        """Generate a markdown expense report"""
        md = self._generate_report_header()
        md += self._get_top_vendor_summary(expense_report_data.top_vendors)
        md += self._get_top_expenses_summary(expense_report_data.top_expenses)
        # md += self._generate_summary(expense_report_data)
        return md

    def _generate_report_header(self) -> str:
        """Generate a markdown report header"""
        return f"""# Expense Report\n\n"""

    def _generate_summary(self, expense_report_data: ReportData) -> str:
        """Generate a markdown summary"""
        return f"""# Expense Report
## Summary

- Period:             {expense_report_data.start_date.strftime('%m/%d/%Y')} - {expense_report_data.end_date.strftime('%m/%d/%Y')}
- Total Transactions: {expense_report_data.total_transactions}
- Total Expenses:     $({abs(expense_report_data.total_expenses):.2f})
- Total Paid:         ${expense_report_data.total_income:.2f}

"""

    def _generate_transaction_table(self, transactions: List[ReportDataItem], title: str) -> str:
        """Generate a markdown table of transactions"""
        md = f"## {title}\n"
        md += "| Date | Description | Amount |\n"
        md += "|------|-------------|--------|\n"
        for transaction in transactions:
            md += f"| {transaction.date_obj.strftime('%Y-%m-%d')} | {transaction.description} | ${transaction.absolute_amount:.2f} |\n"
        return md


    def _get_top_vendor_summary(self, top_vendors: List[VendorSummary]) -> str:
        """Generate a markdown summary of the top vendors"""
        md = f"## Top {len(top_vendors)} Vendors\n\n"
        md += "| Vendor | Count | Total Amount |\n\n"
        md += "|--------|-------|--------------|\n\n"
        for vendor in top_vendors:
            md += f"| {vendor.vendor} | {vendor.count} | ${vendor.total_amount:.2f} |\n\n"
        return md

    def _get_top_expenses_summary(self, top_expenses: List[ReportDataItem]) -> str:
        """Generate a markdown summary of the top expenses"""
        md = f"## Top {len(top_expenses)} Expenses\n\n"
        md += "| Date | Vendor | Amount | Category | Sub Category |\n\n"
        md += "|------|--------|--------|----------|--------------|\n\n"
        for expense in top_expenses:
            md += f"| {expense.date.strftime('%Y-%m-%d')} | {expense.vendor} | ${expense.amount:.2f} | {expense.category} | {expense.sub_category} |\n"
        return md
