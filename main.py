"""Main entry point for the expense analyzer"""

import logging
from datetime import datetime, timedelta

from expense_analyzer.expense_analyzer import ExpenseAnalyzer
from expense_analyzer.report_generators import ConsoleExpenseReportGenerator, MarkdownExpenseReportGenerator


def main():
    """Main entry point for the expense analyzer"""
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Example usage
    analyzer = ExpenseAnalyzer(
        input_dir="input", output_dir="output", report_generator=MarkdownExpenseReportGenerator()
    )

    # Process all documents
    analyzer.process_all_documents()

    # Generate and save current month's report
    report = analyzer.generate_expense_report()
    analyzer.save_expense_report(report)

    # Print some summary information
    print(f"\nProcessed {len(analyzer.transactions)} total transactions")
    print(f"Found {len([t for t in analyzer.transactions if t.is_expense])} expenses")


if __name__ == "__main__":
    main()
