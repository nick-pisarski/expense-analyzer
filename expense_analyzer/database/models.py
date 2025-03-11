"""SQLAlchemy models for the expense analyzer"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from expense_analyzer.database.connection import Base
from expense_analyzer.models.source import Source


class Category(Base):
    """Category model"""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    # Relationships
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    transactions = relationship("Transaction", back_populates="category")


class Transaction(Base):
    """Transaction model"""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    vendor = Column(String, index=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text)
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
