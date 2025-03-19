from typing import List
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from expense_analyzer.database.repository import (
    TransactionRepository,
    CategoryRepository,
    TransactionCategoryRepository,
)
from expense_analyzer.database.connection import get_db
from expense_analyzer.models.transaction import ReportTransaction
from expense_analyzer.database.models import Transaction, Category
from expense_analyzer.embedder.transaction_embedder import TransactionEmbedder
from expense_analyzer.categorizers import SimpleCategorizer

class ExpenseService:
    """Service for managing expense data"""

    def __init__(self):
        self.db: Session = get_db()

        self.transaction_repository = TransactionRepository(self.db)
        self.category_repository = CategoryRepository(self.db)
        self.transaction_category_repository = TransactionCategoryRepository(self.db)

        self.embedder = TransactionEmbedder()
        self.categorizer = SimpleCategorizer()

        self.logger = logging.getLogger("expense_analyzer.services.ExpenseService")
        self.logger.debug("ExpenseService initialized")

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
        sub_categories = self.category_repository.get_all_subcategories()
        success_count = 0
        for transaction in database_transactions:
            category: Category = self._get_category_for_transaction(transaction, sub_categories)
            if category:
                transaction["category_id"] = category.id

            # Embed the transaction
            embedding = self.embedder.embed_transaction(transaction)
            transaction["embedding"] = embedding

            transaction = self.transaction_repository.create_transaction(transaction)
            if transaction:
                success_count += 1
        self.logger.debug(f"Successfully inserted {success_count} transactions")
        return success_count

    def get_transactions_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Transaction]:
        """Get transactions from the database"""
        transactions = self.transaction_category_repository.get_transactions_by_date_range(start_date, end_date)
        return transactions

    def get_all_transactions(self) -> List[ReportTransaction]:
        """Get all transactions"""
        return self.transaction_category_repository.get_transactions()

    def get_transactions_without_category(self) -> List[Transaction]:
        """Get all transactions without a category"""
        return self.transaction_repository.get_transactions_without_category()

    def get_transactions_with_category(self) -> List[Transaction]:
        """Get all transactions with a category"""
        return self.transaction_category_repository.get_transactions_with_category()

    def embed_transactions(self) -> None:
        """Embeds valid transaction, ie they have category"""
        transactions = self.get_transactions_with_category()
        embeddings = self.embedder.embed_transactions(transactions)
        for transaction, embedding in zip(transactions, embeddings):
            transaction.embedding = embedding
            self.transaction_repository.update_transaction(transaction)
    
    def find_similar_transactions(self, transaction: Transaction, limit: int = 5) -> List[Transaction]:
        """Find similar transactions"""
        embedding = transaction.embedding
        if embedding is None:
            self.logger.warning("Transaction has no embedding")
            embedding = self.embedder.embed_transaction(transaction)
        return self.transaction_category_repository.find_similar_transactions(embedding, limit)

    def update_transactions_category(self, transactions: List[Transaction]) -> None:
        """Update the category of a transaction and re-embed it"""
        sub_categories = self.category_repository.get_all_subcategories()
        for transaction in transactions:
            category = self._get_category_for_transaction(transaction, sub_categories)
            if category:
                transaction.category = category
                self.logger.debug(f"Updating transaction {transaction.id} with category {category.name}")

                embedding = self.embedder.embed_transaction(transaction)
                transaction.embedding = embedding

                self.transaction_repository.update_transaction(transaction)

    def _get_category_for_transaction(self, transaction: Transaction, sub_categories: List[Category]) -> Category | None:
        """Get a category for a transaction"""

        # Search for similar transactions
        embedding = self.embedder.embed_transaction(transaction)
        similar_transactions = self.transaction_category_repository.find_similar_transactions(embedding, 10)

        # Use catergorizer to categorize the transaction
        category = self.categorizer.categorize(transaction, similar_transactions, sub_categories)

        return category

        # raise NotImplementedError("Categorization not implemented")
