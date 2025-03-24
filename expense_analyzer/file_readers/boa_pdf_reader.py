"""File reader for Bank of America PDF statements"""

import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

import pdfplumber

from expense_analyzer.file_readers.base_file_reader import BaseFileReader
from expense_analyzer.models.boa_transaction import BankOfAmericaTransaction


@dataclass
class BankOfAmericaStatementInfo:
    """Statement information for Bank of America"""

    period_start: datetime
    period_end: datetime
    closing_date: datetime
    previous_balance: float
    payments_and_credits: float
    purchases_and_adjustments: float

    def __str__(self):
        """String representation of the statement info"""
        return f"""Bank of America Statement Summary
----------------------------------------
Period: {self.period_start.strftime('%B %d, %Y')} - {self.period_end.strftime('%B %d, %Y')}
Closing Date: {self.closing_date.strftime('%B %d, %Y')}

Financial Summary:
Previous Balance:          ${self.previous_balance:,.2f}
Payments and Credits:      ${self.payments_and_credits:,.2f}
Purchases and Adjustments: ${self.purchases_and_adjustments:,.2f}
"""

    def __repr__(self):
        """Representation of the statement info"""
        return f"Statement Info: {self.period_start} - {self.period_end}, Closing Date: {self.closing_date}, Previous Balance: {self.previous_balance}, Payments and Credits: {self.payments_and_credits}, Purchases and Adjustments: {self.purchases_and_adjustments}"


class BankOfAmericaPdfReader(BaseFileReader):
    """File reader for Bank of America PDF statements"""

    statement_info: dict = None

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.transactions = []
        self.logger = logging.getLogger("expense_analyzer.file_readers.BankOfAmericaPdfReader")

    def read_statement_info(self) -> dict:
        """Read the PDF file and return a dictionary of statement information"""
        try:
            with pdfplumber.open(self.file_path) as pdf:
                text = pdf.pages[0].extract_text()
                return self._extract_statement_info(text)
        except Exception as e:
            self.logger.error(f"Error reading statement info: {e}")
            return {}

    def read_transactions(self) -> list[BankOfAmericaTransaction]:
        """Read the PDF file and return a list of transactions"""
        try:
            with pdfplumber.open(self.file_path) as pdf:
                transaction_data = []
                transaction_id = 1  # Generate sequential IDs

                # Process each page
                for page_num, page in enumerate(pdf.pages, 1):
                    self.logger.debug(f"Processing page {page_num} of {len(pdf.pages)}")
                    text = page.extract_text()

                    if page_num == 1:
                        self.statement_info = self._extract_statement_info(text)

                    # Find the transactions section
                    sections = self._extract_transaction_sections(text)

                    if not sections:
                        self.logger.debug(f"No transaction sections found on page {page_num}")
                        continue

                    for section_name, section_text in sections.items():
                        # Extract transactions from each section
                        transactions = self._extract_transactions(section_text, section_name)

                        self.logger.debug(f"Found {len(transactions)} transactions in {section_name} section")

                        for transaction in transactions:
                            # Create a transaction object with a unique ID
                            transaction["id"] = f"BOA-PDF-{transaction_id}"
                            transaction_id += 1
                            transaction_data.append(transaction)

                # Convert to BankOfAmericaTransaction objects
                self.transactions = [BankOfAmericaTransaction(data) for data in transaction_data]
                return self.transactions

        except Exception as e:
            self.logger.error(f"Error reading PDF file: {e}")
            raise

    def _extract_statement_info(self, text: str) -> BankOfAmericaStatementInfo:
        """Extract statement information from the statement text

        Returns:
            BankOfAmericaStatementInfo: Statement information including:
                - period_start: Start date of statement period
                - period_end: End date of statement period
                - closing_date: The closing date of the statement
                - previous_balance: Previous statement balance
                - payments_and_credits: Total payments and credits
                - purchases_and_adjustments: Total purchases and adjustments
        """
        statement_info = {}

        # Extract statement closing date
        closing_date_match = re.search(r"Statement Closing Date\s+(\d{2}/\d{2}/\d{4})", text)
        if closing_date_match:
            statement_info["closing_date"] = datetime.strptime(closing_date_match.group(1), "%m/%d/%Y")

        # Extract statement period from account header (e.g., "September 22 - October 21, 2024")
        period_match = re.search(r"(\w+ \d{1,2}) - (\w+ \d{1,2}, \d{4})", text)
        if period_match:
            end_date = datetime.strptime(period_match.group(2), "%B %d, %Y")
            start_date = datetime.strptime(period_match.group(1), "%B %d")
            start_date = start_date.replace(year=end_date.year)
            statement_info["period_start"] = start_date
            statement_info["period_end"] = end_date

        # Extract previous balance
        previous_balance_match = re.search(r"Previous Balance\s+\$?([\d,]+\.\d{2})", text)
        if previous_balance_match:
            statement_info["previous_balance"] = float(previous_balance_match.group(1).replace(",", ""))

        # Extract payments and credits
        payments_match = re.search(r"Payments and Other Credits\s+-\$?([\d,]+\.\d{2})", text)
        if payments_match:
            statement_info["payments_and_credits"] = float(payments_match.group(1).replace(",", ""))

        # Extract purchases and adjustments
        purchases_match = re.search(r"Purchases and Adjustments\s+\$?([\d,]+\.\d{2})", text)
        if purchases_match:
            statement_info["purchases_and_adjustments"] = float(purchases_match.group(1).replace(",", ""))

        return BankOfAmericaStatementInfo(**statement_info)

    def _extract_transaction_sections(self, text: str) -> dict:
        """Extract transaction sections from the statement text"""
        sections = {}

        # Common section headers in Bank of America statements
        section_patterns = [
            # Updated patterns based on the actual PDF format
            (r"Payments and Other Credits\s+(.*?)(?=Purchases and Adjustments|Interest Charged|\Z)", "payment"),
            (r"Purchases and Adjustments\s+(.*?)(?=Payments and Other Credits|Interest Charged|\Z)", "purchase"),
            (r"Interest Charged\s+(.*?)(?=Payments and Other Credits|Purchases and Adjustments|\Z)", "interest"),
            # Keep original patterns as fallbacks
            (
                r"Deposits and other credits\s+(.*?)(?=Withdrawals and other debits|Card account transactions|TOTAL FEES CHARGED|\Z)",
                "deposit",
            ),
            (
                r"Withdrawals and other debits\s+(.*?)(?=Deposits and other credits|Card account transactions|TOTAL FEES CHARGED|\Z)",
                "withdrawal",
            ),
            (
                r"Card account transactions\s+(.*?)(?=Deposits and other credits|Withdrawals and other debits|TOTAL FEES CHARGED|\Z)",
                "card",
            ),
        ]

        for pattern, section_name in section_patterns:
            matches = re.search(pattern, text, re.DOTALL)
            if matches:
                sections[section_name] = matches.group(1).strip()

        return sections

    def _extract_transactions(self, section_text: str, section_type: str) -> list[dict]:
        """Extract individual transactions from a section"""
        transactions = []

        # Different patterns for different section types based on the actual PDF format
        patterns = {
            # Standard pattern for most transactions (matches the format in the sample PDF)
            # Format: MM/DD MM/DD Description RefNum AcctNum Amount
            "standard": r"(\d{2}/\d{2})\s+(\d{2}/\d{2})\s+(.*?)\s+(\d{4})\s+(\d{4})\s+([-+]?\$?[\d,]+\.\d{2})$",
            # Pattern for transactions with only one date field
            "simple_date": r"(\d{2}/\d{2})\s+(.*?)\s+([-+]?\$?[\d,]+\.\d{2})$",
            # Pattern for transactions without reference numbers
            "simple": r"(\d{2}/\d{2})\s+(\d{2}/\d{2})\s+(.*?)\s+([-+]?\$?[\d,]+\.\d{2})$",
            # Fallback patterns from the original implementation
            "card": r"(\d{2}/\d{2}/\d{2})\s+(.*?)\s+([-+]?\$?[\d,]+\.\d{2})(?:\s+\d+)?$",
            "purchase": r"(\d{2}/\d{2})\s+(.*?)\s+([-+]?\$?[\d,]+\.\d{2})$",
            "payment": r"(\d{2}/\d{2})\s+(\d{2}/\d{2})\s+(.*?)\s+(\d{4})\s+(\d{4})\s+([-+]?\$?[\d,]+\.\d{2})$",
        }

        # Try all patterns in sequence
        all_patterns = [
            patterns["standard"],
            patterns["simple"],
            patterns["simple_date"],
            patterns.get(section_type, ""),
        ]

        # Filter out empty patterns
        all_patterns = [p for p in all_patterns if p]

        # Try each pattern
        for pattern in all_patterns:
            transactions = self._try_pattern(section_text, pattern, section_type)
            if transactions:
                return transactions

        return []

    def _try_pattern(self, section_text: str, pattern: str, section_type: str) -> list[dict]:
        """Try to extract transactions using a specific pattern"""
        transactions = []

        # Skip header lines
        lines_to_process = []
        for line in section_text.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith("Transaction") or line.startswith("Date") or line.startswith("TOTAL"):
                continue
            lines_to_process.append(line)

        # Process each line
        for line in lines_to_process:
            match = re.search(pattern, line)
            if match:
                groups = match.groups()

                # Initialize transaction data with default values
                transaction_data = {
                    "date": "Unknown",
                    "posting_date": "Unknown",
                    "description": "",
                    "amount": 0.0,
                    "vendor": "Unknown",
                    "reference_number": None,
                    "account_number": None,
                    "transaction_type": section_type,
                    "id": None,  # Will be set in the calling method
                }

                # Handle different pattern formats based on the number of captured groups
                if len(groups) >= 6:  # Standard format with transaction date, posting date, etc.
                    trans_date, post_date, description, ref_num, acct_num, amount_str = groups
                    transaction_data["date"] = self._parse_date(trans_date)
                    transaction_data["posting_date"] = self._parse_date(post_date)
                    transaction_data["description"] = description.strip()
                    transaction_data["reference_number"] = ref_num
                    transaction_data["account_number"] = acct_num
                    transaction_data["amount"] = self._parse_amount(amount_str, section_type)
                elif len(groups) == 4:  # Simple format with transaction date, posting date, description, amount
                    trans_date, post_date, description, amount_str = groups
                    transaction_data["date"] = self._parse_date(trans_date)
                    transaction_data["posting_date"] = self._parse_date(post_date)
                    transaction_data["description"] = description.strip()
                    transaction_data["amount"] = self._parse_amount(amount_str, section_type)
                elif len(groups) == 3:  # Simple date format with just transaction date, description, amount
                    date_str, description, amount_str = groups
                    transaction_data["date"] = self._parse_date(date_str)
                    transaction_data["description"] = description.strip()
                    transaction_data["amount"] = self._parse_amount(amount_str, section_type)
                else:
                    self.logger.warning(f"Unexpected number of groups: {len(groups)} in line: {line}")
                    continue

                # Extract vendor from description
                # transaction_data["vendor"] = self._extract_vendor(transaction_data["description"])
                transaction_data["vendor"] = description

                transactions.append(transaction_data)
            else:
                # Log lines that didn't match the pattern for debugging
                if len(line) > 10 and not line.startswith("continued"):
                    self.logger.debug(f"Line didn't match pattern: {line}")

        return transactions

    def _parse_date(self, date_str: str) -> str:
        """Parse a date string into a standardized format"""
        try:
            # Handle different date formats
            if len(date_str) == 5:  # MM/DD format
                # Assume current year if only month and day are provided
                current_year = self.statement_info.closing_date.year
                return datetime.strptime(f"{date_str}/{current_year}", "%m/%d/%Y").strftime("%Y-%m-%d")
            else:  # MM/DD/YY format
                return datetime.strptime(date_str, "%m/%d/%y").strftime("%Y-%m-%d")
        except ValueError:
            self.logger.warning(f"Could not parse date: {date_str}")
            return "Unknown"

    def _parse_amount(self, amount_str: str, section_type: str) -> float:
        """Parse an amount string into a float with the correct sign"""
        # Clean up the amount string and convert to float
        amount_str = amount_str.replace("$", "").replace(",", "")
        try:
            amount = float(amount_str)

            # Adjust sign based on transaction type
            if section_type in ["withdrawal", "purchase"] and amount > 0:
                amount = -amount
            elif section_type in ["deposit", "payment"] and amount < 0:
                amount = abs(amount)

            return amount
        except ValueError:
            self.logger.warning(f"Could not parse amount: {amount_str}")
            return 0.0

    def _extract_vendor(self, description: str) -> str:
        """Extract vendor from description"""
        # Look for the first word that's not a date or transaction code
        words = description.split()
        vendor = "Unknown"
        for word in words:
            if not re.match(r"^\d+$", word) and not re.match(r"^\d{2}/\d{2}$", word):
                vendor = word
                break
        return vendor

    def __str__(self):
        """String representation of the file reader"""
        return f"BankOfAmericaPdfReader(file_path={self.file_path})"

    def __repr__(self):
        """Representation of the file reader"""
        return self.__str__()


if __name__ == "__main__":
    # Example usage
    import os
    import sys

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Navigate to the input directory
    input_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "input", "bank_of_america")

    # Process a sample PDF file
    sample_file = os.path.join(input_dir, "eStmt_2024-10-21.pdf")

    if os.path.exists(sample_file):
        reader = BankOfAmericaPdfReader(sample_file)

        transactions = reader.read_transactions()

        print(f"Found {len(transactions)} transactions:")
        for transaction in transactions[:5]:  # Print first 5 transactions
            print(f"Date: {transaction.date}, Posting Date: {transaction.posting_date}")
            print(f"Vendor: {transaction.vendor}, Amount: ${transaction.amount:.2f}")
            print(f"Description: {transaction.description}")
            print(f"Reference #: {transaction.reference_number}, Account #: {transaction.account_number}")
            print("-" * 50)

        # Group transactions by month
        months = defaultdict(list)
        for transaction in transactions:
            if transaction.month:
                months[transaction.month].append(transaction)

        print("\nTransactions by month:")
        for month, month_transactions in months.items():
            total = sum(t.amount for t in month_transactions)
            print(f"{month}: {len(month_transactions)} transactions, total: ${total:.2f}")

        # Show top expenses
        expenses = [t for t in transactions if t.is_expense]
        expenses.sort(key=lambda t: t.absolute_amount, reverse=True)

        print("\nTop 5 expenses:")
        for expense in expenses[:5]:
            print(f"{expense.date} - {expense.vendor}: ${expense.absolute_amount:.2f}")
    else:
        print(f"Sample file not found: {sample_file}")
