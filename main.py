"""Main entry point for the expense analyzer"""

from datetime import datetime
from pprint import pprint

from dotenv import load_dotenv

from expense_analyzer.database.models import Transaction
from expense_analyzer.expense_analyzer import ExpenseAnalyzer
from expense_analyzer.report_generators.markdown_generator import (
    MarkdownExpenseReportGenerator,
)
from expense_analyzer.services.expense_service import ExpenseService
from expense_analyzer.services.report_service import ReportService
from expense_analyzer.utils.logging_config import configure_logging

load_dotenv()
configure_logging()


def print_transaction(transaction: Transaction):
    """Print a transaction"""
    space = 40
    print(
        f"{transaction.date} | {transaction.vendor[:space]:<{space}} | ${transaction.absolute_amount:>7.2f} | {transaction.category.name if transaction.category else 'Uncategorized'}"
    )


def similar_transaction(transaction_id: int):
    """Find similar transactions"""
    transaction = None
    similar_transactions = []
    with ExpenseService() as expense_service:
        transaction = expense_service.transaction_category_repository.get_transaction(transaction_id)
        similar_transactions = expense_service.find_similar_transactions(transaction)

    print("Transaction:")
    print_transaction(transaction)
    print()
    print("Similar transactions:")
    for transaction in similar_transactions:
        print_transaction(transaction)


def use_service_to_get_transactions(start_date: datetime, end_date: datetime):
    """Use the ExpenseService to get transactions by date range"""
    results = []
    with ExpenseService() as expense_service:
        results = expense_service.get_transactions_by_date_range(start_date, end_date)
    print(f"Found {len(results)} transactions")
    for result in results:
        print_transaction(result)


def categorize_transactions(transaction_id: int):
    """Categorize a transaction"""
    transaction = None
    category = None
    with ExpenseService() as expense_service:
        transaction = expense_service.transaction_category_repository.get_transaction(transaction_id)
        sub_categories = expense_service.category_repository.get_all_subcategories()
        category = expense_service._get_category_for_transaction(transaction, sub_categories)

    print("Transaction:")
    print_transaction(transaction)
    print()
    print("Category:")
    print(category.name)


def test_report_service():
    """Test the ReportService"""
    report_service = ReportService()
    report = report_service.generate_report_data(2025)
    pprint(report)


def main():
    """Main entry point for the expense analyzer"""
    # Configure logging    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Example usage
    analyzer = ExpenseAnalyzer(
        input_dir="input", output_dir="output", report_generator=MarkdownExpenseReportGenerator(verbose=False)
    )
    analyzer.generate_reports(2024)
    analyzer.generate_reports(2025)

    # Process all documents
    # results = analyzer.process_all_documents()

    # transactions by date range
    # use_service_to_get_transactions()

    # Test the similarity of transactions
    # similar_transaction()

    # Test the categorization of transactions
    # categorize_transactions()

    # Test the report generation
    # test_report_service()


if __name__ == "__main__":
    main()
