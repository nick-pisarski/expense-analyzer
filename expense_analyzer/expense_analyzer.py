"""Main controller class for expense analysis"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict

from expense_analyzer.file_readers import BankOfAmericaPdfReader
from expense_analyzer.models import ExpenseReportData, ReportTransaction
from expense_analyzer.report_generators import ExpenseReportGenerator
from expense_analyzer.services.expense_service import ExpenseService


class ExpenseAnalyzer:
    """Main controller class for analyzing expenses from various financial documents"""

    def __init__(self, input_dir: str, output_dir: str, report_generator: ExpenseReportGenerator):
        """Initialize the ExpenseAnalyzer

        Args:
            input_dir (str): Directory containing input financial documents
            output_dir (str): Directory where analysis results will be saved
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.transactions: List[ReportTransaction] = []
        self.logger = logging.getLogger(__name__)
        self.report_generator = report_generator
        # Ensure directories exist
        self._setup_directories()

    def _setup_directories(self) -> None:
        """Create input and output directories if they don't exist"""
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for different banks/sources
        (self.input_dir / "bank_of_america").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)

    def process_all_documents(self) -> None:
        """Process all documents in the input directory"""
        self.logger.info("Starting to process all documents")

        # Process Bank of America documents
        transactions_found = self._process_boa_documents()

        # Insert transactions into the database
        with ExpenseService() as expense_service:
            expense_service.insert_transactions(transactions_found)

        # TODO: Add processing for other banks/sources as needed

    def _process_boa_documents(self) -> List[ReportTransaction]:
        """Process all Bank of America PDF statements"""
        boa_dir = self.input_dir / "bank_of_america"
        if not boa_dir.exists():
            self.logger.warning(f"Bank of America directory not found: {boa_dir}")
            return

        transactions_found = []
        for pdf_file in list(boa_dir.glob("*.pdf")):
            try:
                reader = BankOfAmericaPdfReader(str(pdf_file))
                transactions = reader.read_transactions()
                transactions_found.extend(transactions)
                self.logger.info(f"Processed {len(transactions)} transactions from {pdf_file.name}")
            except Exception as e:
                self.logger.error(f"Error processing {pdf_file.name}: {e}")
        return transactions_found

    def get_transactions(self) -> List[ReportTransaction]:
        """Get all transactions"""
        with ExpenseService() as expense_service:
            return expense_service.get_all_transactions()

    def save_expense_report(self, report: ExpenseReportData, file_name: Optional[str] = None) -> None:
        """Save a monthly report to the output directory

        Args:
            report (Dict): Report data to save
            month (str): Month in YYYY-MM format
        """
        if file_name is None:
            file_name = f"expense_report_{report.start_date.strftime('%Y-%m')}-to-{report.end_date.strftime('%Y-%m')}"

        report_file = self.output_dir / "reports" / f"{file_name}.md"
        with open(report_file, "w") as f:
            f.write(self.report_generator.generate_report(report))

        self.logger.info(f"Saved monthly report to {report_file}")
