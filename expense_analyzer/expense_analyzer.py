"""Main controller class for expense analysis"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict

from expense_analyzer.file_readers.boa_pdf_reader import BankOfAmericaPdfReader
from expense_analyzer.models.boa_transaction import BankOfAmericaTransaction


class ExpenseAnalyzer:
    """Main controller class for analyzing expenses from various financial documents"""

    def __init__(self, input_dir: str, output_dir: str):
        """Initialize the ExpenseAnalyzer

        Args:
            input_dir (str): Directory containing input financial documents
            output_dir (str): Directory where analysis results will be saved
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.transactions: List[BankOfAmericaTransaction] = []
        self.logger = logging.getLogger(__name__)

        # Ensure directories exist
        self._setup_directories()

    def _setup_directories(self) -> None:
        """Create input and output directories if they don't exist"""
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for different banks/sources
        (self.input_dir / "bank_of_america").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
        (self.output_dir / "analytics").mkdir(exist_ok=True)

    def process_all_documents(self) -> None:
        """Process all documents in the input directory"""
        self.logger.info("Starting to process all documents")

        # Process Bank of America documents
        self._process_boa_documents()

        # TODO: Add processing for other banks/sources as needed

        self.logger.info(f"Processed {len(self.transactions)} total transactions")

    def _process_boa_documents(self) -> None:
        """Process all Bank of America PDF statements"""
        boa_dir = self.input_dir / "bank_of_america"
        if not boa_dir.exists():
            self.logger.warning(f"Bank of America directory not found: {boa_dir}")
            return

        for pdf_file in boa_dir.glob("*.pdf"):
            try:
                reader = BankOfAmericaPdfReader(str(pdf_file))
                transactions = reader.read_transactions()
                self.transactions.extend(transactions)
                self.logger.info(f"Processed {len(transactions)} transactions from {pdf_file.name}")
            except Exception as e:
                self.logger.error(f"Error processing {pdf_file.name}: {e}")

    def get_transactions_by_month(self) -> Dict[str, List[BankOfAmericaTransaction]]:
        """Group transactions by month

        Returns:
            Dict[str, List[BankOfAmericaTransaction]]: Transactions grouped by month (YYYY-MM)
        """
        monthly_transactions = defaultdict(list)
        for transaction in self.transactions:
            if transaction.date:
                month_key = transaction.date[:7]  # YYYY-MM format
                monthly_transactions[month_key].append(transaction)
        return dict(monthly_transactions)

    def get_top_expenses(
        self, limit: int = 10, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> List[BankOfAmericaTransaction]:
        """Get top expenses within an optional date range

        Args:
            limit (int, optional): Number of top expenses to return. Defaults to 10.
            start_date (Optional[str], optional): Start date in YYYY-MM-DD format. Defaults to None.
            end_date (Optional[str], optional): End date in YYYY-MM-DD format. Defaults to None.

        Returns:
            List[BankOfAmericaTransaction]: List of top expenses sorted by amount
        """
        expenses = [t for t in self.transactions if t.is_expense]

        if start_date:
            expenses = [t for t in expenses if t.date >= start_date]
        if end_date:
            expenses = [t for t in expenses if t.date <= end_date]

        expenses.sort(key=lambda t: t.absolute_amount, reverse=True)
        return expenses[:limit]

    def generate_monthly_report(self, month: Optional[str] = None) -> Dict:
        """Generate a monthly expense report

        Args:
            month (Optional[str], optional): Month in YYYY-MM format. Defaults to current month.

        Returns:
            Dict: Report containing total expenses, income, and transaction summaries
        """
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        # Filter transactions for the specified month
        month_transactions = [t for t in self.transactions if t.date and t.date.startswith(month)]

        expenses = [t for t in month_transactions if t.is_expense]
        income = [t for t in month_transactions if not t.is_expense]

        report = {
            "month": month,
            "total_transactions": len(month_transactions),
            "total_expenses": sum(t.amount for t in expenses),
            "total_income": sum(t.amount for t in income),
            "top_expenses": self.get_top_expenses(limit=5, start_date=f"{month}-01", end_date=f"{month}-31"),
            "expense_categories": self._summarize_categories(expenses),
        }

        return report

    def _summarize_categories(self, transactions: List[BankOfAmericaTransaction]) -> Dict[str, float]:
        """Summarize total amounts by category

        Args:
            transactions (List[BankOfAmericaTransaction]): List of transactions to summarize

        Returns:
            Dict[str, float]: Total amount spent in each category
        """
        categories = defaultdict(float)
        for transaction in transactions:
            categories[transaction.category] += transaction.absolute_amount
        return dict(categories)

    def save_monthly_report(self, report: Dict, month: str) -> None:
        """Save a monthly report to the output directory

        Args:
            report (Dict): Report data to save
            month (str): Month in YYYY-MM format
        """
        import json

        report_file = self.output_dir / "reports" / f"monthly_report_{month}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Saved monthly report to {report_file}")
