from expense_analyzer.database.models import Category, Transaction


import numpy as np
from sqlalchemy.orm import Session, joinedload


import logging
from datetime import datetime
from typing import List, Optional


class TransactionCategoryRepository:
    """Repository for getting transactions with categories TODO: Needs Tests"""

    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(f"{__name__}.TransactionCategoryRepository")
        self.logger.debug("TransactionCategoryRepository initialized")

    def get_transactions(self) -> List[Transaction]:
        """Get all transactions with categories"""
        self.logger.debug("Getting all transactions with categories")
        transactions = self.db.query(Transaction).options(joinedload(Transaction.category)).all()
        return transactions

    def get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        """Get a transaction with a specific category"""
        self.logger.debug(f"Getting transaction with ID: {transaction_id}")
        transaction = (
            self.db.query(Transaction)
            .options(joinedload(Transaction.category))
            .filter(Transaction.id == transaction_id)
            .first()
        )
        return transaction

    def get_transactions_with_category(self) -> List[Transaction]:
        """Get all transactions with a category"""
        self.logger.debug("Getting all transactions with a category")
        transactions = (
            self.db.query(Transaction)
            .options(joinedload(Transaction.category))
            .filter(Transaction.category_id.is_not(None))
            .all()
        )
        return transactions

    def get_transactions_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Transaction]:
        """Get all transactions within a date range"""
        self.logger.debug(f"Getting all transactions between {start_date} and {end_date}")
        transactions = (
            self.db.query(Transaction)
            .options(joinedload(Transaction.category))
            .filter(Transaction.date >= start_date, Transaction.date <= end_date)
            .all()
        )
        return transactions

    def get_transactions_by_category(self, category_id: int) -> List[Transaction]:
        """Get all transactions with a specific category"""
        self.logger.debug(f"Getting all transactions with category ID: {category_id}")
        transactions = (
            self.db.query(Transaction)
            .options(joinedload(Transaction.category))
            .filter(Category.id == category_id)
            .all()
        )
        return transactions

    def get_transactions_by_category_name(self, category_name: str) -> List[Transaction]:
        """Get all transactions with a specific category by name"""
        self.logger.debug(f"Getting all transactions with category name: {category_name}")
        transactions = (
            self.db.query(Transaction)
            .options(joinedload(Transaction.category))
            .filter(Category.name == category_name)
            .all()
        )
        return transactions

    def find_similar_transactions(self, embedding: List[float], limit: int = 5):
        """Find transactions with similar descriptions using vector similarity

        Args:
            description: The description to search for
            limit: The maximum number of results to return
            embedding: Optional pre-computed embedding for the description

        Returns:
            List of transactions with similar descriptions
        """
        self.logger.debug(f"Finding similar transactions (limit: {limit})")

        # Convert to numpy array
        embedding_array = np.array(embedding)

        # Query using cosine similarity
        transactions = (
            self.db.query(Transaction)
            .options(joinedload(Transaction.category))
            .filter(Transaction.embedding.is_not(None), Transaction.category_id.is_not(None))
            .order_by(Transaction.embedding.cosine_distance(embedding_array))
            .limit(limit)
            .all()
        )
        self.logger.debug(f"Found {len(transactions)} similar transactions")
        return transactions