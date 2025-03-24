"""Data access layer for the expense analyzer"""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from expense_analyzer.database.models import Transaction


class TransactionRepository:
    """Repository for transaction data"""

    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger("expense_analyzer.database.TransactionRepository")
        self.logger.debug("TransactionRepository initialized")

    def create_transaction(self, transaction_data: dict) -> Optional[Transaction]:
        """Create a new transaction"""
        self.logger.info(
            f"Creating new transaction: {transaction_data.get('vendor')} - {transaction_data.get('amount')}"
        )
        transaction = Transaction(**transaction_data)
        self.db.add(transaction)

        try:
            self.db.commit()
            self.db.refresh(transaction)
            self.logger.debug(f"Transaction created successfully with ID: {transaction.id}")
            return transaction
        except IntegrityError:
            self.logger.warning(
                f"Duplicate transaction found for {transaction_data.get('vendor')} - {transaction_data.get('amount')}"
            )
            self.logger.debug(f"Integrity error when creating transaction, rolling back: {transaction_data}")
            self.db.rollback()
            return None

    def get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        """Get a transaction by ID"""
        self.logger.debug(f"Getting transaction with ID: {transaction_id}")
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()

    def update_transaction(self, transaction: Transaction) -> None:
        """Update a transaction"""
        self.logger.debug(f"Updating transaction with ID: {transaction.id}")
        try:
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            self.logger.debug(f"Successfully updated transaction with ID: {transaction.id}")
        except IntegrityError:
            self.logger.warning(f"Integrity error when updating transaction, rolling back: {transaction}")
            self.db.rollback()

    def get_all_transactions(self) -> List[Transaction]:
        """Get all transactions"""
        self.logger.debug("Getting all transactions")
        transactions = self.db.query(Transaction).all()
        self.logger.debug(f"Retrieved {len(transactions)} transactions")
        return transactions

    def get_transactions_without_category(self) -> List[Transaction]:
        """Get all transactions without a category"""
        self.logger.debug("Getting all transactions without a category")
        transactions = self.db.query(Transaction).filter(Transaction.category_id.is_(None)).all()
        self.logger.debug(f"Retrieved {len(transactions)} transactions without a category")
        return transactions

    def get_transactions_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Transaction]:
        """Get transactions within a date range"""
        self.logger.debug(f"Getting transactions between {start_date} and {end_date}")
        transactions = (
            self.db.query(Transaction).filter(Transaction.date >= start_date, Transaction.date <= end_date).all()
        )
        self.logger.debug(f"Retrieved {len(transactions)} transactions in date range")
        return transactions
