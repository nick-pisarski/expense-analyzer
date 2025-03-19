"""Data access layer for the expense analyzer"""

from typing import List, Optional, Dict
from datetime import datetime
import logging
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
import numpy as np

from expense_analyzer.database.models import Transaction, Category

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

    def get_top_expenses(
        self, limit: int = 10, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[Transaction]:
        """Get top expenses within an optional date range"""
        self.logger.debug(f"Getting top {limit} expenses between {start_date or 'any'} and {end_date or 'any'}")
        query = self.db.query(Transaction).filter(Transaction.amount < 0)

        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)

        transactions = query.order_by(Transaction.amount).limit(limit).all()
        self.logger.debug(f"Retrieved {len(transactions)} top expenses")
        return transactions

    def summarize_by_vendor(self, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Summarize expenses by vendor"""
        self.logger.debug(f"Summarizing expenses by vendor between {start_date} and {end_date}")
        results = (
            self.db.query(Transaction.vendor, func.sum(Transaction.amount).label("total"))
            .filter(Transaction.date >= start_date, Transaction.date <= end_date, Transaction.amount < 0)
            .group_by(Transaction.vendor)
            .all()
        )

        summary = {vendor: abs(total) for vendor, total in results}
        self.logger.debug(f"Generated summary for {len(summary)} vendors")
        return summary




class CategoryRepository:
    """Repository for category data"""

    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(f"{__name__}.CategoryRepository")
        self.logger.debug("CategoryRepository initialized")

    def create_category(self, name: str, parent_id: Optional[int] = None) -> Category:
        """Create a new category"""
        self.logger.info(f"Creating new category: {name} (parent_id: {parent_id})")
        category = Category(name=name, parent_id=parent_id)
        self.db.add(category)
        try:
            self.db.commit()
            self.db.refresh(category)
            self.logger.debug(f"Category created successfully with ID: {category.id}")
            return category
        except IntegrityError:
            self.logger.warning(f"Integrity error when creating category '{name}', rolling back")
            self.db.rollback()
            raise

    def get_category(self, category_id: int) -> Optional[Category]:
        """Get a category by ID"""
        self.logger.debug(f"Getting category with ID: {category_id}")
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if category:
            self.logger.debug(f"Found category: {category.name} (ID: {category.id})")
        else:
            self.logger.debug(f"No category found with ID: {category_id}")
        return category

    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Get a category by name"""
        self.logger.debug(f"Getting category with name: {name}")
        category = self.db.query(Category).filter(Category.name == name).first()
        if category:
            self.logger.debug(f"Found category: {category.name} (ID: {category.id})")
        else:
            self.logger.debug(f"No category found with name: {name}")
        return category

    def get_all_categories(self) -> List[Category]:
        """Get all categories"""
        self.logger.debug("Getting all categories")
        categories = self.db.query(Category).all()
        self.logger.debug(f"Retrieved {len(categories)} categories")
        return categories

    def get_root_categories(self) -> List[Category]:
        """Get all root categories (categories without a parent)"""
        self.logger.debug("Getting all root categories")
        categories = self.db.query(Category).filter(Category.parent_id.is_(None)).all()
        self.logger.debug(f"Retrieved {len(categories)} root categories")
        return categories

    def get_subcategories(self, parent_id: int) -> List[Category]:
        """Get all subcategories of a parent category"""
        self.logger.debug(f"Getting subcategories for parent ID: {parent_id}")
        categories = self.db.query(Category).filter(Category.parent_id == parent_id).all()
        self.logger.debug(f"Retrieved {len(categories)} subcategories for parent ID: {parent_id}")
        return categories

    def get_all_subcategories(self) -> List[Category]:
        """Get all subcategories"""
        self.logger.debug("Getting all subcategories")
        categories = self.db.query(Category).filter(Category.parent_id.is_not(None)).all()
        self.logger.debug(f"Retrieved {len(categories)} subcategories")
        return categories


class TransactionCategoryRepository:
    """Repository for getting transactions with categories"""

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