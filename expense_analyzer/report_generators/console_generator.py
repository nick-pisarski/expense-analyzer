from expense_analyzer.models.expense_report_data import ExpenseReportData
from expense_analyzer.report_generators.base_generator import ExpenseReportGenerator


class ConsoleExpenseReportGenerator(ExpenseReportGenerator):
    """Generate a console expense report"""

    def generate_report(self, expense_report_data: ExpenseReportData) -> str:
        """Generate a console expense report"""
        report = self._generate_report_header(expense_report_data)
        report += self._generate_report_body(expense_report_data)
        return report

    def _generate_report_header(self, expense_report_data: ExpenseReportData) -> str:
        """Generate a report header"""
        return f"Expense Report for {expense_report_data.start_date} to {expense_report_data.end_date}"

    def _generate_report_body(self, expense_report_data: ExpenseReportData) -> str:
        """Generate a report body"""
        report = ""
        report += f"*" * 80 + "\n"
        report += f"Total Transactions: {expense_report_data.total_transactions}\n"
        report += f"Total Expenses: {expense_report_data.total_expenses}\n"
        report += f"Total Income: {expense_report_data.total_income}\n"
        report += f"*" * 80 + "\n"
        report += f"Top Expenses:\n"
        for expense in expense_report_data.top_expenses:
            report += f"{expense.vendor}: {expense.amount}\n"
        report += f"*" * 80 + "\n"
        return report
