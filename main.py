"""Main entry point for the expense analyzer"""

import logging
from datetime import datetime, timedelta

from expense_analyzer.expense_analyzer import ExpenseAnalyzer


def main():
    """Main entry point for the expense analyzer"""
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Example usage
    analyzer = ExpenseAnalyzer(input_dir="input", output_dir="output")

    # Process all documents
    analyzer.process_all_documents()

    # Generate and save current month's report
    report = analyzer.generate_expense_report()
    analyzer.save_expense_report(report)

    # Print some summary information
    print(f"\nProcessed {len(analyzer.transactions)} total transactions")
    print(f"Found {len([t for t in analyzer.transactions if t.is_expense])} expenses")

    # Show top 5 expenses
    print("\nTop 5 expenses:")
    for expense in analyzer.get_top_expenses(limit=5):
        print(f"{expense.date} - {expense.vendor}: ${expense.absolute_amount:.2f}")


if __name__ == "__main__":
    main()
