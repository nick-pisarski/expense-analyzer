"""Data access layer for the expense analyzer"""

from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
import numpy as np

from expense_analyzer.database.models import Transaction, Category


class TransactionRepository:
    """Repository for transaction data"""

    def __init__(self, db: Session):
        self.db = db

    def create_transaction(self, transaction_data: dict) -> Transaction:
        """Create a new transaction"""
        transaction = Transaction(**transaction_data)
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        """Get a transaction by ID"""
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()

    def get_all_transactions(self) -> List[Transaction]:
        """Get all transactions"""
        return self.db.query(Transaction).all()

    def get_transactions_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Transaction]:
        """Get transactions within a date range"""
        return self.db.query(Transaction).filter(Transaction.date >= start_date, Transaction.date <= end_date).all()

    def get_top_expenses(
        self, limit: int = 10, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[Transaction]:
        """Get top expenses within an optional date range"""
        query = self.db.query(Transaction).filter(Transaction.amount < 0)

        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)

        return query.order_by(Transaction.amount).limit(limit).all()

    def summarize_by_vendor(self, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Summarize expenses by vendor"""
        results = (
            self.db.query(Transaction.vendor, func.sum(Transaction.amount).label("total"))
            .filter(Transaction.date >= start_date, Transaction.date <= end_date, Transaction.amount < 0)
            .group_by(Transaction.vendor)
            .all()
        )

        return {vendor: abs(total) for vendor, total in results}

    def find_similar_transactions(self, description: str, limit: int = 5, embedding: Optional[List[float]] = None):
        """Find transactions with similar descriptions using vector similarity

        Args:
            description: The description to search for
            limit: The maximum number of results to return
            embedding: Optional pre-computed embedding for the description

        Returns:
            List of transactions with similar descriptions
        """
        if embedding is None:
            # If no embedding is provided, we'd need to generate one
            # This is a placeholder - you'll need to implement embedding generation
            embedding = self._generate_embedding(description)

        # Convert to numpy array
        embedding_array = np.array(embedding)

        # Query using cosine similarity
        return (
            self.db.query(Transaction)
            .filter(Transaction.embedding.is_not(None))
            .order_by(Transaction.embedding.cosine_distance(embedding_array))
            .limit(limit)
            .all()
        )

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using a model of your choice

        This is a placeholder method. You'll need to implement this with your
        preferred embedding model (e.g., OpenAI, Sentence Transformers, etc.)

        Args:
            text: The text to generate an embedding for

        Returns:
            A list of floats representing the embedding
        """
        # Placeholder - replace with actual embedding generation
        # Example with OpenAI:
        # from openai import OpenAI
        # client = OpenAI()
        # response = client.embeddings.create(input=text, model="text-embedding-ada-002")
        # return response.data[0].embedding

        # For now, return a dummy embedding of the right size
        return [0.0] * 1536


class CategoryRepository:
    """Repository for category data"""

    def __init__(self, db: Session):
        self.db = db

    def create_category(self, name: str, parent_id: Optional[int] = None) -> Category:
        """Create a new category"""
        category = Category(name=name, parent_id=parent_id)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def get_category(self, category_id: int) -> Optional[Category]:
        """Get a category by ID"""
        return self.db.query(Category).filter(Category.id == category_id).first()

    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Get a category by name"""
        return self.db.query(Category).filter(Category.name == name).first()

    def get_all_categories(self) -> List[Category]:
        """Get all categories"""
        return self.db.query(Category).all()

    def get_root_categories(self) -> List[Category]:
        """Get all root categories (categories without a parent)"""
        return self.db.query(Category).filter(Category.parent_id.is_(None)).all()

    def get_subcategories(self, parent_id: int) -> List[Category]:
        """Get all subcategories of a parent category"""
        return self.db.query(Category).filter(Category.parent_id == parent_id).all()
