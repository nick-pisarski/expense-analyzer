"""Main entry point for the expense analyzer"""

from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta

from expense_analyzer.expense_analyzer import ExpenseAnalyzer
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
    results = analyzer.process_all_documents()

    print(results)


if __name__ == "__main__":
    main()
