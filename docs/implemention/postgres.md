# Setting up PostgreSQL with pgvector for Expense Analyzer

This document outlines how to set up PostgreSQL with the pgvector extension for the Expense Analyzer application.

## 1. Install PostgreSQL and pgvector

### Using Docker (recommended for consistent development)

Create a `docker-compose.yml` file in the project root:

```yaml
version: '3.8'

services:
  postgres:
    image: ankane/pgvector:latest
    environment:
      POSTGRES_USER: expense_user
      POSTGRES_PASSWORD: expense_password
      POSTGRES_DB: expense_analyzer
      # This environment variable ensures pgvector is enabled
      POSTGRES_INITDB_ARGS: "--data-checksums"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      # Mount an initialization script to enable the extension
      - ./init-scripts:/docker-entrypoint-initdb.d

volumes:
  postgres_data:
```

Create a directory called init-scripts in your project root and add a file named `01-enable-pgvector.sql` with the following content:

```sql
-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify it's installed
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Set the maximum number of dimensions (if needed)
-- ALTER SYSTEM SET vector.dim_limit = 1536;  -- Default is 2000

-- Set the similarity search algorithm (exact or approximate)
-- ALTER SYSTEM SET vector.hnsw_ef_search = 100;  -- Higher values = more accurate but slower

-- Reload the configuration
-- SELECT pg_reload_conf();
```

Start the container:

```bash
docker-compose up -d
```

Connect to the database:

```bash
docker-compose exec postgres psql -U expense_user -d expense_analyzer
```

Check if pgvector is enabled:

```sql
expense_analyzer=# SELECT * FROM pg_extension WHERE extname = 'vector';
```

## 2. Add Required Dependencies

Update your `pyproject.toml` to include the necessary dependencies:

```toml
[tool.poetry.dependencies]
python = "^3.9"
psycopg2-binary = "^2.9"
sqlalchemy = "^2.0"
alembic = "^1.12"
pgvector = "^0.2.0"  # Python client for pgvector
```

Install the dependencies:

```bash
poetry update
```

## 3. Database Module Structure

Create the following directory structure:

```
expense_analyzer/
├── database/
│   ├── __init__.py
│   ├── models.py         # SQLAlchemy models
│   ├── connection.py     # Database connection management
│   ├── repository.py     # Data access layer
│   └── migrations/       # Alembic migrations
```

## 4. Database Connection Configuration

Create `expense_analyzer/database/connection.py`:

```python
"""Database connection management"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment variable or use default
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://expense_user:expense_password@localhost:5432/expense_analyzer"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 5. Define SQLAlchemy Models

Create `expense_analyzer/database/models.py`:

```python
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
    
    # Vector embedding for semantic search (if needed)
    embedding = Column(Vector(384), nullable=True)  # Adjust dimension as needed
    
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

## 6. Create Repository Layer

Create `expense_analyzer/database/repository.py`:

```python
"""Data access layer for the expense analyzer"""

from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from expense_analyzer.database.models import Transaction, Category, Report

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
    
    def get_transactions_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[Transaction]:
        """Get transactions within a date range"""
        return self.db.query(Transaction).filter(
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()
    
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
        results = self.db.query(
            Transaction.vendor,
            func.sum(Transaction.amount).label("total")
        ).filter(
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.amount < 0
        ).group_by(Transaction.vendor).all()
        
        return {vendor: abs(total) for vendor, total in results}

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
    
    def get_all_categories(self) -> List[Category]:
        """Get all categories"""
        return self.db.query(Category).all()

```

## 7. Set Up Database Migrations with Alembic

Initialize Alembic:

```bash
# Install Alembic if not already installed
pip install alembic

# Initialize Alembic in your project
cd /path/to/expense-analyzer
alembic init expense_analyzer/database/migrations
```

Update `alembic.ini` to point to your database:

```ini
sqlalchemy.url = postgresql://expense_user:expense_password@localhost:5432/expense_analyzer
```

Update `expense_analyzer/database/migrations/env.py` to import your models:

```python
# Add this near the top of the file
from expense_analyzer.database.models import Base
target_metadata = Base.metadata
```

Create your first migration:

```bash
alembic revision --autogenerate -m "Initial database schema"
```

Apply the migration:

```bash
alembic upgrade head
```

## 8. Update ExpenseAnalyzer Class

Modify the ExpenseAnalyzer class to use the database instead of in-memory storage:

```python
"""Main controller class for expense analysis"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from expense_analyzer.file_readers import BankOfAmericaPdfReader
from expense_analyzer.models import ExpenseReportData
from expense_analyzer.report_generators import ExpenseReportGenerator
from expense_analyzer.database.connection import get_db
from expense_analyzer.database.repository import TransactionRepository, ReportRepository


class ExpenseAnalyzer:
    """Main controller class for analyzing expenses from various financial documents"""

    def __init__(self, input_dir: str, output_dir: str, report_generator: ExpenseReportGenerator, db: Session = None):
        """Initialize the ExpenseAnalyzer"""
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(__name__)
        self.report_generator = report_generator
        self.db = db or next(get_db())
        self.transaction_repo = TransactionRepository(self.db)
        self.report_repo = ReportRepository(self.db)
        
        # Ensure directories exist
        self._setup_directories()

    # ... rest of the class implementation, updated to use repositories ...
```

## 9. Using pgvector for Semantic Search

If you want to use pgvector for semantic search (e.g., finding similar transactions), you can add this functionality:

```python
from pgvector.sqlalchemy import Vector
import numpy as np

# In your repository class
def find_similar_transactions(self, description: str, limit: int = 5):
    """Find transactions with similar descriptions using vector similarity"""
    # Generate embedding for the query (using your preferred embedding model)
    embedding = generate_embedding(description)
    
    # Convert to numpy array
    embedding_array = np.array(embedding)
    
    # Query using cosine similarity
    return self.db.query(Transaction).order_by(
        Transaction.embedding.cosine_distance(embedding_array)
    ).limit(limit).all()

# Function to generate embeddings (implement with your preferred model)
def generate_embedding(text: str) -> List[float]:
    """Generate embedding for text using a model of your choice"""
    # Implementation depends on your embedding model
    # Example with sentence-transformers:
    # from sentence_transformers import SentenceTransformer
    # model = SentenceTransformer('all-MiniLM-L6-v2')
    # return model.encode(text).tolist()
    pass
```

## 10. Environment Configuration

Update your `.env` file to include database configuration:

```
DATABASE_URL=postgresql://expense_user:expense_password@localhost:5432/expense_analyzer
```

And update `.env.example` as a reference:

```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

## Next Steps

1. Implement data migration from your current file-based system to the database
2. Add unit tests for the database repositories
3. Consider adding indexes to improve query performance
4. Implement transaction categorization using pgvector for semantic similarity 