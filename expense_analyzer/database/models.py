"""SQLAlchemy models for the expense analyzer"""

from dataclasses import dataclass
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from expense_analyzer.database.connection import Base
from expense_analyzer.models.source import Source


class Category(Base):
    """Category model"""

    __tablename__ = "categories"
    __table_args__ = (
        # Enforce uniqueness on name and parent_id combination
        # This allows the same category name under different parent categories
        UniqueConstraint("name", "parent_id", name="uix_category_name_parent"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # Removed unique=True as it's now part of the composite constraint
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # Relationships
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    transactions = relationship("Transaction", back_populates="category")


class Transaction(Base):
    """Transaction model"""

    __tablename__ = "transactions"
    __table_args__ = (
        # Enforce uniqueness on date, amount, vendor, and description
        # description can be NULL and still maintain uniqueness
        UniqueConstraint("date", "amount", "vendor", "description", name="uix_transaction_unique"),
    )

    id = Column(Integer, primary_key=True, index=True)
    vendor = Column(String, index=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)  # Explicitly mark as nullable
    source = Column(Enum(Source), default=Source.UNKNOWN)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Vector embedding for semantic search (if needed)
    embedding = Column(Vector(1536), nullable=True)  # Using 1536 dimensions as requested

    # Relationships
    category = relationship("Category", back_populates="transactions")

    @property
    def is_expense(self):
        """Check if the transaction is an expense"""
        return self.amount < 0

    @property
    def is_income(self):
        """Check if the transaction is income"""
        return self.amount > 0

    @property
    def absolute_amount(self):
        """Get the absolute amount of the transaction"""
        return abs(self.amount)

    def __repr__(self):
        return f"<Transaction(id={self.id}, vendor={self.vendor}, amount={self.amount}, date={self.date}, description={self.description}, source={self.source}, category_id={self.category_id})>"

    def __str__(self):
        return f"Transaction(id={self.id}, vendor={self.vendor}, amount={self.amount}, date={self.date}, description={self.description}, source={self.source}, category_id={self.category_id})"


class TransactionView(Base):
    """Transaction view model"""

    __tablename__ = "transaction_with_category_view"

    # Make it clear this is a view by adding mapper args
    __mapper_args__ = {
        "primary_key": ["id"],  # Specify primary key as a list of column names
    }
    id = Column(Integer, primary_key=True)  # Remove index=True as it's not needed for views
    vendor = Column(String)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    category_name = Column(String)
    parent_category_name = Column(String)

    def __str__(self):
        space = 40
        return f"{self.date} | {self.vendor[:space]:<{space}} | ${abs(self.amount):>7.2f} | {self.category_name}[{self.parent_category_name}]"

    def __repr__(self):
        return f"TransactionView(id={self.id}, vendor={self.vendor}, amount={self.amount}, date={self.date}, category_name={self.category_name}, parent_category_name={self.parent_category_name})"


@dataclass
class VendorSummary:
    vendor: str
    count: int
    total_amount: float

    def __str__(self):
        return f"{self.vendor[:40]:<40} | {self.count:>4} | ${self.total_amount:>7.2f}"
