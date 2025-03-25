from typing import Dict, List, Optional

from expense_analyzer.database.models import Category, VendorSummary
from expense_analyzer.models.reports import (
    AverageMonthSummary,
    CategorySummary,
    OverviewSummary,
    ReportData,
    ReportDataItem,
)
from expense_analyzer.report_generators.base_generator import ExpenseReportGenerator


class MarkdownExpenseReportGenerator(ExpenseReportGenerator):
    """Generate a markdown expense report"""

    def __init__(self):
        self.verbose = False

    def generate_report(self, expense_report_data: ReportData, verbose: bool = False) -> str:
        """Generate a markdown expense report"""
        self.verbose = verbose
        md = f"# {expense_report_data.year} Expense Report\n\n"
        md += self._generate_summary(expense_report_data)
        md += self._get_top_vendor_summary(expense_report_data.top_vendors)
        md += self._get_year_summary(expense_report_data.year, expense_report_data.per_year_data)
        md += self._get_average_month_summary(expense_report_data.average_month)
        md += self._get_top_expenses_summary(expense_report_data.top_expenses)
        md += self._get_per_month_summary(expense_report_data.per_month_data)
        return md

    def _generate_summary(self, report_data: ReportData) -> str:
        """Generate a markdown summary"""
        md = f"**Total Transactions:**      {report_data.total_transactions}\n"
        md += f"**Total Expenses:**         ${abs(report_data.total_amount):.2f}\n"
        md += f"**Top Vendor:**             {report_data.highest_spending_vendor.vendor} (${report_data.highest_spending_vendor.total_amount:.2f})\n"
        md += f"**Highest Spending Month:** {report_data.highest_spending_month[0]} (${report_data.highest_spending_month[1].total_expenses:.2f})\n"
        md += f"**Lowest Spending Month:**  {report_data.lowest_spending_month[0]} (${report_data.lowest_spending_month[1].total_expenses:.2f})\n"
        return md

    def _get_top_vendor_summary(self, top_vendors: List[VendorSummary]) -> str:
        """Generate a markdown summary of the top vendors"""
        md = f"## Top {len(top_vendors)} Vendors\n\n"
        md += "| Vendor | Count | Total Amount |\n"
        md += "|--------|-------|--------------|\n"
        for vendor in top_vendors:
            md += f"| {vendor.vendor} | {vendor.count} | ${vendor.total_amount:.2f} |\n"
        md += "\n"
        return md

    def _get_top_expenses_summary(self, top_expenses: List[ReportDataItem]) -> str:
        """Generate a markdown summary of the top expenses"""
        md = f"## Top {len(top_expenses)} Expenses\n\n"
        md += "| Date | Vendor | Amount | Category | Sub Category |\n"
        md += "|------|--------|--------|----------|--------------|\n"
        for expense in top_expenses:
            md += f"| {expense.date.strftime('%Y-%m-%d')} | {expense.vendor} | ${expense.amount:.2f} | {expense.category.name} | {expense.sub_category.name} |\n"
        md += "\n"
        return md

    def _get_average_month_summary(self, average_month: AverageMonthSummary) -> str:
        """Generate a markdown summary of the average month"""
        md = "## Average Month\n\n"
        md += f"**Estimated Total Expenses:** ${average_month.estimated_total_expenses:.2f}\n"
        md += "\n"
        md += "| Category | Amount |\n"
        md += "|----------|--------|\n"
        for category, amount in average_month.category_summaries.items():
            md += f"| {category.name} | ${amount:>7.2f} |\n"
        md += "\n"
        return md

    def _generate_transaction_table(self, transactions: List[ReportDataItem], title: Optional[str] = None) -> str:
        """Generate a markdown table of transactions"""
        md = ""
        if title:
            md += f"{title}\n\n"
        md += "| Date | Vendor | Amount | Category | Sub Category |\n"
        md += "|------|--------|--------|----------|--------------|\n"
        for transaction in transactions:
            md += f"| {transaction.date.strftime('%Y-%m-%d')} | {transaction.vendor[:20]} | ${transaction.amount:.2f} | {transaction.category.name} | {transaction.sub_category.name[:20]} |\n"
        return md

    def _get_category_summary(self, category: Category, category_data: CategorySummary) -> str:
        """Generate a markdown summary of the category summary"""
        md = ""
        md += f"#### {category.name}\n\n"
        md += f"**Total Expenses:** ${category_data.expenses:>7.2f}\n"
        md += f"**Total Incomes:**  ${category_data.incomes:>7.2f}\n"
        md += f"**Transactions:**    {len(category_data.transactions):>7}\n\n"
        md += "| Sub Category | Amount |\n"
        md += "|--------------|--------|\n"
        for sub_category, amount in category_data.sub_categories.items():
            md += f"| {sub_category.name} | ${amount:>7.2f} |\n"
        md += "\n"
        md += self._generate_transaction_table(category_data.transactions)
        md += "\n"
        return md

    def _get_category_summary_table(self, data: CategorySummary) -> str:
        """Generate a markdown table of the category summary"""
        md = ""
        md += "| Category | Expenses | Incomes | # Transactions |\n"
        md += "|----------|----------|---------|----------------|\n"
        for category, data in data.items():
            md += f"| {category.name} | ${data.expenses:.2f} | ${data.incomes:.2f} | {len(data.transactions)} |\n"
        md += "\n"
        return md

    def _get_overview_summary(self, data: OverviewSummary) -> str:
        """Generate a markdown summary of the overview summary"""
        md = ""
        md += f"**Total Expenses:** ${data.total_expenses:>7.2f}\n"
        md += f"**Total Incomes:**  ${data.total_incomes:>7.2f}\n"
        md += f"**Net Balance:**    ${data.net_balance:>7.2f}\n\n"
        md += self._get_category_summary_table(data.category_summaries)
        if self.verbose:
            md += "#### Category Details\n\n"
            for category, data in data.category_summaries.items():
                md += self._get_category_summary(category, data)
        return md

    def _get_per_month_summary(self, per_month_data: Dict[str, OverviewSummary]) -> str:
        """Generate a markdown summary of the per month data"""
        md = "## Per Month Summary\n\n"
        for month, data in per_month_data.items():
            md += f"### {month}\n\n"
            md += self._get_overview_summary(data)
        return md

    def _get_year_summary(self, year: int, year_data: OverviewSummary) -> str:
        """Generate a markdown summary of the year data"""
        md = f"## {year} summary \n\n"
        md += self._get_overview_summary(year_data)
        return md

    def generate_transaction_table(self, report_data: ReportData, title: Optional[str] = None) -> str:
        """Generate a markdown table of transactions"""
        md = f"{title}\n\n" if title else f"# {report_data.year} Transactions\n\n"
        md += self._generate_transaction_table(report_data.get_transactions())
        return md
