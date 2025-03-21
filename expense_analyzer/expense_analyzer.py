"""Main controller class for expense analysis"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple

from expense_analyzer.file_readers import BankOfAmericaPdfReader
from expense_analyzer.models import ExpenseReportData, ReportTransaction
from expense_analyzer.report_generators import ExpenseReportGenerator
from expense_analyzer.services.expense_service import ExpenseService
from expense_analyzer.services.report_service import ReportService


class ProcessDocumentsResult:
    """Result of processing documents"""

    def __init__(
        self,
        transactions_found: List[ReportTransaction],
        files_processed: int,
        transactions_inserted: int,
        success: bool,
    ):
        self.transactions_found = transactions_found
        self.files_processed = files_processed
        self.transactions_inserted = transactions_inserted
        self.success = success

    def __str__(self) -> str:
        return (
            f"Documents processed: {self.files_processed}\n"
            f"Transactions found: {len(self.transactions_found)}\n"
            f"New transactions inserted: {self.transactions_inserted}\n"
            f"Successful: {self.success}"
        )

    def __repr__(self) -> str:
        return f"ProcessDocumentsResult(transactions_found={self.transactions_found}, files_processed={self.files_processed}, transactions_inserted={self.transactions_inserted}, success={self.success})"


class ExpenseAnalyzer:
    """Main controller class for analyzing expenses from various financial documents and generating various reports"""

    def __init__(self, input_dir: str, output_dir: str, report_generator: ExpenseReportGenerator):
        """Initialize the ExpenseAnalyzer

        Args:
            input_dir (str): Directory containing input financial documents
            output_dir (str): Directory where analysis results will be saved
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.transactions: List[ReportTransaction] = []
        self.logger = logging.getLogger("expense_analyzer.expense_analyzer")
        self.report_generator = report_generator
        self.report_service = ReportService()
        # Ensure directories exist
        self._setup_directories()

    def _setup_directories(self) -> None:
        """Create input and output directories if they don't exist"""
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for different banks/sources
        (self.input_dir / "bank_of_america").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)

    def process_all_documents(self) -> ProcessDocumentsResult:
        """Process all documents in the input directory"""
        self.logger.info("Starting to process all documents")

        transactions_found_in_docs = 0
        files_processed = 0
        transactions_inserted = 0

        # Process Bank of America documents
        transactions_found, files_processed = self._process_boa_documents()
        transactions_found_in_docs += len(transactions_found)
        files_processed += files_processed

        # TODO: Add processing for other banks/sources as needed

        # Insert transactions into the database
        with ExpenseService() as expense_service:
            transactions_inserted = expense_service.insert_transactions(transactions_found)

        return ProcessDocumentsResult(
            transactions_found=transactions_found,
            files_processed=files_processed,
            transactions_inserted=transactions_inserted,
            success=True,
        )

    def _process_boa_documents(self) -> Tuple[List[ReportTransaction], int]:
        """Process all Bank of America PDF statements"""
        boa_dir = self.input_dir / "bank_of_america"
        if not boa_dir.exists():
            self.logger.warning(f"Bank of America directory not found: {boa_dir}")
            return
        files_found = list(boa_dir.glob("*.pdf"))
        if not files_found:
            self.logger.warning(f"No Bank of America PDF files found in {boa_dir}")
            return [], 0

        transactions_found = []
        for pdf_file in files_found:
            try:
                reader = BankOfAmericaPdfReader(str(pdf_file))
                transactions = reader.read_transactions()
                transactions_found.extend(transactions)
                self.logger.info(f"Processed {len(transactions)} transactions from {pdf_file.name}")
            except Exception as e:
                self.logger.error(f"Error processing {pdf_file.name}: {e}")
        return transactions_found, len(files_found)

    def _process_tdecu_documents(self) -> Tuple[List[ReportTransaction], int]:
        """Process all TDECU PDF statements"""
        raise NotImplementedError("TDECU processing not implemented")

    def categorize_transactions_without_category(self) -> None:
        """Categorize transactions. Looks for all transactions in the database that do not have a category
        and categorizes them, then re-embeds them."""

        # TODO: This function should not be in the ExpenseAnalyzer class. It should be in the ExpenseService class.
        with ExpenseService() as expense_service:
            transactions = expense_service.get_transactions_without_category()
            self.logger.info(f"Categorizing {len(transactions)} transactions without a category")
            expense_service.update_transactions_category(transactions)
            self.logger.debug(f"Categorizing Complete")

    def generate_reports(self, year: int, file_name: Optional[str] = None) -> str:
        """Generate a monthly report and save it to the output directory

        Args:
            year (int): Year to generate report for
            file_name (str): File name to save report to
        """
        if file_name is None:
            file_name = f"expense_report_{year}"

        report_file = self.output_dir / "reports" / f"{file_name}.md"
        report_data = self.report_service.generate_report_data(year)
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(self.report_generator.generate_report(report_data))

        self.logger.info(f"Saved monthly report to {report_file}")
