"""Main entry point for the expense analyzer"""

from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta

from expense_analyzer.expense_analyzer import ExpenseAnalyzer
from expense_analyzer.services.expense_service import ExpenseService
from expense_analyzer.report_generators import ConsoleExpenseReportGenerator, MarkdownExpenseReportGenerator
from expense_analyzer.utils.logging_config import configure_logging

load_dotenv()
configure_logging()


def main():
    """Main entry point for the expense analyzer"""
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Example usage
    analyzer = ExpenseAnalyzer(
        input_dir="input", output_dir="output", report_generator=MarkdownExpenseReportGenerator()
    )

    # Process all documents
    # results = analyzer.process_all_documents()

    # Using the ExpenseService to get transactions by date range

    with ExpenseService() as expense_service:
        results = expense_service.get_transactions_by_date_range(datetime(2025, 1, 1), datetime(2025, 12, 31))

    print(f"Found {len(results)} transactions")

    results_with_category = [result for result in results if result.category is not None]

    for result in results_with_category:
        print(f"{result.category.name}: {result.vendor} - ${result.absolute_amount:0.2f}")


if __name__ == "__main__":
    main()
