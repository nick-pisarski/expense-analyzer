"""Data access layer for the expense analyzer"""

from typing import List, Optional, Dict
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
import numpy as np

from expense_analyzer.database.models import Transaction, Category

# Configure logger
logger = logging.getLogger(__name__)


class TransactionRepository:
    """Repository for transaction data"""

    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(f"{__name__}.TransactionRepository")
        self.logger.debug("TransactionRepository initialized")

    def create_transaction(self, transaction_data: dict) -> Transaction:
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
            self.logger.warning(f"Integrity error when creating transaction, rolling back: {transaction_data}")
            self.db.rollback()
            # If unique constraint violated, return the existing transaction
            existing = (
                self.db.query(Transaction)
                .filter(
                    Transaction.date == transaction_data["date"],
                    Transaction.amount == transaction_data["amount"],
                    Transaction.vendor == transaction_data["vendor"],
                    Transaction.description == transaction_data.get("description"),
                )
                .first()
            )
            self.logger.info(f"Found existing transaction with ID: {existing.id if existing else None}")
            return existing

    def get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        """Get a transaction by ID"""
        self.logger.debug(f"Getting transaction with ID: {transaction_id}")
        transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if transaction:
            self.logger.debug(f"Found transaction: {transaction.id}")
        else:
            self.logger.debug(f"No transaction found with ID: {transaction_id}")
        return transaction

    def get_all_transactions(self) -> List[Transaction]:
        """Get all transactions"""
        self.logger.debug("Getting all transactions")
        transactions = self.db.query(Transaction).all()
        self.logger.debug(f"Retrieved {len(transactions)} transactions")
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

    def find_similar_transactions(self, description: str, limit: int = 5, embedding: Optional[List[float]] = None):
        """Find transactions with similar descriptions using vector similarity

        Args:
            description: The description to search for
            limit: The maximum number of results to return
            embedding: Optional pre-computed embedding for the description

        Returns:
            List of transactions with similar descriptions
        """
        self.logger.debug(f"Finding transactions similar to: '{description}' (limit: {limit})")
        if embedding is None:
            self.logger.debug("No embedding provided, generating one")
            embedding = self._generate_embedding(description)

        # Convert to numpy array
        embedding_array = np.array(embedding)

        # Query using cosine similarity
        transactions = (
            self.db.query(Transaction)
            .filter(Transaction.embedding.is_not(None))
            .order_by(Transaction.embedding.cosine_distance(embedding_array))
            .limit(limit)
            .all()
        )
        self.logger.debug(f"Found {len(transactions)} similar transactions")
        return transactions

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using a model of your choice

        This is a placeholder method. You'll need to implement this with your
        preferred embedding model (e.g., OpenAI, Sentence Transformers, etc.)

        Args:
            text: The text to generate an embedding for

        Returns:
            A list of floats representing the embedding
        """
        self.logger.debug(f"Generating embedding for text: '{text[:30]}...' if len(text) > 30 else text")
        # Placeholder - replace with actual embedding generation
        # Example with OpenAI:
        # from openai import OpenAI
        # client = OpenAI()
        # response = client.embeddings.create(input=text, model="text-embedding-ada-002")
        # return response.data[0].embedding

        # For now, return a dummy embedding of the right size
        self.logger.debug("Using placeholder embedding (this should be replaced with actual implementation)")
        return [0.0] * 1536


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
