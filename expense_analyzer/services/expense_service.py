from typing import List
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from expense_analyzer.database.repository import TransactionRepository, CategoryRepository
from expense_analyzer.database.connection import get_db
from expense_analyzer.models.transaction import ReportTransaction
from expense_analyzer.database.models import Transaction, Category


class ExpenseService:
    def __init__(self):
        self.db: Session = get_db()
        self.transaction_repository = TransactionRepository(self.db)
        self.category_repository = CategoryRepository(self.db)
        self.logger = logging.getLogger("expense_analyzer.services.ExpenseService")
        self.logger.debug("ExpenseService initialized")

        # TODO: Add logic to categorize transactions
        # self.categorizer = Categorizer()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup method to close database connection"""
        if hasattr(self, "db"):
            self.logger.debug("Closing database connection")
            self.db.close()

    def close(self):
        """Explicit method to close the database connection"""
        if hasattr(self, "db"):
            self.logger.debug("Closing database connection")
            self.db.close()

    def _convert_report_transactions_to_database_transactions(
        self, transactions: List[ReportTransaction]
    ) -> List[Transaction]:
        """Convert ReportTransaction objects to Transaction objects"""
        database_transactions = []
        self.logger.debug(f"Converting {len(transactions)} transactions to database transactions")
        for transaction in transactions:

            database_transaction = {
                "vendor": transaction.vendor,
                "amount": transaction.amount,
                "date": transaction.date,
                "description": transaction.description,
                "source": transaction.source,
            }
            database_transactions.append(database_transaction)
        return database_transactions

    def insert_transactions(self, transactions: List[ReportTransaction]) -> int:
        """Insert transactions into the database"""
        self.logger.debug(f"Inserting {len(transactions)} transactions into the database")
        # Insert transactions into the database
        database_transactions: List[dict] = self._convert_report_transactions_to_database_transactions(transactions)
        success_count = 0
        for transaction in database_transactions:
            transaction = self.transaction_repository.create_transaction(transaction)
            if transaction:
                success_count += 1
        self.logger.debug(f"Successfully inserted {success_count} transactions")
        return success_count

    def get_transactions_by_date_range(self, start_date: datetime, end_date: datetime) -> List[ReportTransaction]:
        """Get transactions from the database"""
        return self.transaction_repository.get_transactions_by_date_range(start_date, end_date)

    def get_all_transactions(self) -> List[ReportTransaction]:
        """Get all transactions"""
        return self.transaction_repository.get_all_transactions()

    def _get_category_for_transaction(self, transaction: Transaction) -> Category:
        """Get a category for a transaction"""

        # Fetch all subcategories from the database
        # subcategories = self.category_repository.get_subcategories()

        # Search for similar transactions
        # similar_transactions = self.transaction_repository.find_similar_transactions(transaction)

        # Use catergorizer to categorize the transaction
        # category = self.categorizer.categorize(transaction)

        # return category

        # TODO: Implement categorization logic
        raise NotImplementedError("Categorization not implemented")
