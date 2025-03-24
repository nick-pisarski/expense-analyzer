"""Unit tests for the TransactionCategoryRepository class."""

import logging
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

import numpy as np
from sqlalchemy import extract, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from expense_analyzer.database.models import Category, Transaction, VendorSummary
from expense_analyzer.database.repositories.transaction_category_repository import (
    TransactionCategoryRepository,
)


class TestTransactionCategoryRepository(unittest.TestCase):
    """Test cases for the TransactionCategoryRepository class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_db = MagicMock(spec=Session)
        self.repo = TransactionCategoryRepository(self.mock_db)

    def test_init_creates_logger(self):
        """Test that logger is created during initialization."""
        # Act
        repo = TransactionCategoryRepository(self.mock_db)
        
        # Assert
        self.assertIsNotNone(repo.logger)
        self.assertEqual(repo.logger.name, "expense_analyzer.database.repositories.transaction_category_repository.TransactionCategoryRepository")

    @patch("logging.getLogger")
    def test_logger_debug_called(self, mock_get_logger):
        """Test that logger.debug is called during initialization."""
        # Arrange
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Act
        repo = TransactionCategoryRepository(self.mock_db)
        
        # Assert
        mock_get_logger.assert_called_once_with("expense_analyzer.database.repositories.transaction_category_repository.TransactionCategoryRepository")
        mock_logger.debug.assert_called_once_with("TransactionCategoryRepository initialized")

    def test_get_transactions(self):
        """Test retrieving all transactions with categories."""
        # Arrange
        mock_transactions = [MagicMock(spec=Transaction) for _ in range(3)]
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        options_mock.all.return_value = mock_transactions

        # Act
        result = self.repo.get_transactions()

        # Assert
        self.mock_db.query.assert_called_once_with(Transaction)
        query_mock.options.assert_called_once()
        options_mock.all.assert_called_once()
        self.assertEqual(result, mock_transactions)
        
    def test_get_transactions_empty_result(self):
        """Test retrieving all transactions with categories when no transactions exist."""
        # Arrange
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        options_mock.all.return_value = []

        # Act
        result = self.repo.get_transactions()

        # Assert
        self.mock_db.query.assert_called_once_with(Transaction)
        query_mock.options.assert_called_once()
        options_mock.all.assert_called_once()
        self.assertEqual(result, [])
        self.assertEqual(len(result), 0)

    def test_get_transactions_handles_exception(self):
        """Test that get_transactions handles exceptions gracefully."""
        # Arrange
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        options_mock.all.side_effect = SQLAlchemyError("Database error")
        
        # Act/Assert
        with self.assertRaises(SQLAlchemyError):
            self.repo.get_transactions()

    def test_get_transaction(self):
        """Test retrieving a transaction by ID."""
        # Arrange
        transaction_id = 1
        mock_transaction = MagicMock(spec=Transaction)
        mock_transaction.id = transaction_id
        
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        filter_mock = options_mock.filter.return_value
        filter_mock.first.return_value = mock_transaction

        # Act
        result = self.repo.get_transaction(transaction_id)

        # Assert
        self.mock_db.query.assert_called_once_with(Transaction)
        query_mock.options.assert_called_once()
        options_mock.filter.assert_called_once()
        filter_mock.first.assert_called_once()
        self.assertEqual(result, mock_transaction)
        
    def test_get_transaction_not_found(self):
        """Test retrieving a non-existent transaction by ID."""
        # Arrange
        transaction_id = 999
        
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        filter_mock = options_mock.filter.return_value
        filter_mock.first.return_value = None

        # Act
        result = self.repo.get_transaction(transaction_id)

        # Assert
        self.assertIsNone(result)
        
    def test_get_transactions_with_category(self):
        """Test retrieving all transactions that have a category assigned."""
        # Arrange
        mock_transactions = [MagicMock(spec=Transaction) for _ in range(2)]
        
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        filter_mock = options_mock.filter.return_value
        filter_mock.all.return_value = mock_transactions

        # Act
        result = self.repo.get_transactions_with_category()

        # Assert
        self.mock_db.query.assert_called_once_with(Transaction)
        query_mock.options.assert_called_once()
        options_mock.filter.assert_called_once()
        filter_mock.all.assert_called_once()
        self.assertEqual(result, mock_transactions)
        
    def test_get_transactions_with_category_empty_result(self):
        """Test retrieving transactions with categories when none have categories."""
        # Arrange
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        filter_mock = options_mock.filter.return_value
        filter_mock.all.return_value = []

        # Act
        result = self.repo.get_transactions_with_category()

        # Assert
        self.mock_db.query.assert_called_once_with(Transaction)
        query_mock.options.assert_called_once()
        options_mock.filter.assert_called_once()
        filter_mock.all.assert_called_once()
        self.assertEqual(result, [])
        self.assertEqual(len(result), 0)
        
    def test_get_transactions_by_date_range(self):
        """Test retrieving transactions within a date range."""
        # Arrange
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)
        mock_transactions = [MagicMock(spec=Transaction) for _ in range(5)]
        
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        filter_mock = options_mock.filter.return_value
        filter_mock.all.return_value = mock_transactions

        # Act
        result = self.repo.get_transactions_by_date_range(start_date, end_date)

        # Assert
        self.mock_db.query.assert_called_once_with(Transaction)
        query_mock.options.assert_called_once()
        options_mock.filter.assert_called_once()
        filter_mock.all.assert_called_once()
        self.assertEqual(result, mock_transactions)
        
    def test_get_transactions_by_date_range_invalid_dates(self):
        """Test retrieving transactions with start date after end date."""
        # Arrange
        start_date = datetime(2023, 12, 31)
        end_date = datetime(2023, 1, 1)  # End date before start date
        mock_transactions = []
        
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        filter_mock = options_mock.filter.return_value
        filter_mock.all.return_value = mock_transactions

        # Act
        result = self.repo.get_transactions_by_date_range(start_date, end_date)

        # Assert
        self.mock_db.query.assert_called_once_with(Transaction)
        query_mock.options.assert_called_once()
        options_mock.filter.assert_called_once()
        filter_mock.all.assert_called_once()
        self.assertEqual(result, [])
        self.assertEqual(len(result), 0)
        
    def test_get_transactions_by_category(self):
        """Test retrieving transactions by category ID."""
        # Arrange
        category_id = 1
        mock_transactions = [MagicMock(spec=Transaction) for _ in range(3)]
        
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        filter_mock = options_mock.filter.return_value
        filter_mock.all.return_value = mock_transactions

        # Act
        result = self.repo.get_transactions_by_category(category_id)

        # Assert
        self.mock_db.query.assert_called_once_with(Transaction)
        query_mock.options.assert_called_once()
        options_mock.filter.assert_called_once()
        filter_mock.all.assert_called_once()
        self.assertEqual(result, mock_transactions)
        
    def test_get_transactions_by_category_nonexistent(self):
        """Test retrieving transactions for a category that doesn't exist."""
        # Arrange
        category_id = 999  # Non-existent category
        
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        filter_mock = options_mock.filter.return_value
        filter_mock.all.return_value = []

        # Act
        result = self.repo.get_transactions_by_category(category_id)

        # Assert
        self.mock_db.query.assert_called_once_with(Transaction)
        query_mock.options.assert_called_once()
        options_mock.filter.assert_called_once()
        filter_mock.all.assert_called_once()
        self.assertEqual(result, [])
        self.assertEqual(len(result), 0)
        
    def test_get_transactions_by_category_name(self):
        """Test retrieving transactions by category name."""
        # Arrange
        category_name = "Entertainment"
        mock_transactions = [MagicMock(spec=Transaction) for _ in range(3)]
        
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        filter_mock = options_mock.filter.return_value
        filter_mock.all.return_value = mock_transactions

        # Act
        result = self.repo.get_transactions_by_category_name(category_name)

        # Assert
        self.mock_db.query.assert_called_once_with(Transaction)
        query_mock.options.assert_called_once()
        options_mock.filter.assert_called_once()
        filter_mock.all.assert_called_once()
        self.assertEqual(result, mock_transactions)
        
    def test_get_transactions_by_category_name_nonexistent(self):
        """Test retrieving transactions for a category name that doesn't exist."""
        # Arrange
        category_name = "NonExistentCategory"  
        
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        filter_mock = options_mock.filter.return_value
        filter_mock.all.return_value = []

        # Act
        result = self.repo.get_transactions_by_category_name(category_name)

        # Assert
        self.mock_db.query.assert_called_once_with(Transaction)
        query_mock.options.assert_called_once()
        options_mock.filter.assert_called_once()
        filter_mock.all.assert_called_once()
        self.assertEqual(result, [])
        self.assertEqual(len(result), 0)

    def test_find_similar_transactions(self):
        """Test finding transactions with similar descriptions using vector similarity."""
        # Arrange
        embedding = [0.1, 0.2, 0.3]
        limit = 5
        mock_transactions = [MagicMock(spec=Transaction) for _ in range(limit)]
        
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        filter_mock = options_mock.filter.return_value
        order_by_mock = filter_mock.order_by.return_value
        limit_mock = order_by_mock.limit.return_value
        limit_mock.all.return_value = mock_transactions

        # Act
        with patch('numpy.array', return_value=np.array(embedding)) as mock_np_array:
            result = self.repo.find_similar_transactions(embedding, limit)

        # Assert
        mock_np_array.assert_called_once_with(embedding)
        self.mock_db.query.assert_called_once_with(Transaction)
        query_mock.options.assert_called_once()
        options_mock.filter.assert_called_once()
        filter_mock.order_by.assert_called_once()
        order_by_mock.limit.assert_called_once_with(limit)
        limit_mock.all.assert_called_once()
        self.assertEqual(result, mock_transactions)
        
    def test_find_similar_transactions_empty_embedding(self):
        """Test finding similar transactions with an empty embedding."""
        # Arrange
        embedding = []
        limit = 5
        
        # Act/Assert
        with self.assertRaises(ValueError):
            with patch('numpy.array', side_effect=ValueError("empty array")) as mock_np_array:
                self.repo.find_similar_transactions(embedding, limit)
                
        # Assert
        mock_np_array.assert_called_once_with(embedding)
        
    def test_find_similar_transactions_custom_limit(self):
        """Test finding transactions with custom limit."""
        # Arrange
        embedding = [0.1, 0.2, 0.3]
        limit = 10  # Custom limit
        mock_transactions = [MagicMock(spec=Transaction) for _ in range(limit)]
        
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        filter_mock = options_mock.filter.return_value
        order_by_mock = filter_mock.order_by.return_value
        limit_mock = order_by_mock.limit.return_value
        limit_mock.all.return_value = mock_transactions

        # Act
        with patch('numpy.array', return_value=np.array(embedding)) as mock_np_array:
            result = self.repo.find_similar_transactions(embedding, limit)

        # Assert
        order_by_mock.limit.assert_called_once_with(limit)
        self.assertEqual(len(result), limit)

    def test_get_top_expenses(self):
        """Test retrieving top expenses for a year."""
        # Arrange
        year = 2023
        limit = 5
        mock_transactions = [MagicMock(spec=Transaction) for _ in range(limit)]
        
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        where_mock = options_mock.where.return_value
        order_by_mock = where_mock.order_by.return_value
        limit_mock = order_by_mock.limit.return_value
        limit_mock.all.return_value = mock_transactions

        # Act
        result = self.repo.get_top_expenses(year, limit)

        # Assert
        self.mock_db.query.assert_called_once_with(Transaction)
        query_mock.options.assert_called_once()
        options_mock.where.assert_called_once()
        where_mock.order_by.assert_called_once()
        order_by_mock.limit.assert_called_once_with(limit)
        limit_mock.all.assert_called_once()
        self.assertEqual(result, mock_transactions)
        
    def test_get_top_expenses_custom_limit(self):
        """Test retrieving top expenses with custom limit."""
        # Arrange
        year = 2023
        limit = 10
        mock_transactions = [MagicMock(spec=Transaction) for _ in range(limit)]
        
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        where_mock = options_mock.where.return_value
        order_by_mock = where_mock.order_by.return_value
        limit_mock = order_by_mock.limit.return_value
        limit_mock.all.return_value = mock_transactions

        # Act
        result = self.repo.get_top_expenses(year, limit)

        # Assert
        order_by_mock.limit.assert_called_once_with(limit)
        self.assertEqual(len(result), limit)
        
    def test_get_top_expenses_no_expenses(self):
        """Test retrieving top expenses when no expenses exist for the year."""
        # Arrange
        year = 2020  # Year with no expenses
        limit = 5
        
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        where_mock = options_mock.where.return_value
        order_by_mock = where_mock.order_by.return_value
        limit_mock = order_by_mock.limit.return_value
        limit_mock.all.return_value = []

        # Act
        result = self.repo.get_top_expenses(year, limit)

        # Assert
        self.assertEqual(result, [])
        self.assertEqual(len(result), 0)

    def test_get_top_vendors(self):
        """Test retrieving top vendors for a year."""
        # Arrange
        year = 2023
        limit = 5
        mock_results = [
            ('Vendor1', 10, -500.0),
            ('Vendor2', 5, -300.0),
            ('Vendor3', 3, -200.0),
        ]
        expected_summaries = [
            VendorSummary(vendor='Vendor1', count=10, total_amount=500.0),
            VendorSummary(vendor='Vendor2', count=5, total_amount=300.0),
            VendorSummary(vendor='Vendor3', count=3, total_amount=200.0),
        ]
        
        query_mock = self.mock_db.query.return_value
        where_mock = query_mock.where.return_value
        group_by_mock = where_mock.group_by.return_value
        order_by_mock = group_by_mock.order_by.return_value
        limit_mock = order_by_mock.limit.return_value
        limit_mock.all.return_value = mock_results

        # Act
        result = self.repo.get_top_vendors(year, limit)

        # Assert
        self.mock_db.query.assert_called_once()
        query_mock.where.assert_called_once()
        where_mock.group_by.assert_called_once_with(Transaction.vendor)
        group_by_mock.order_by.assert_called_once()
        order_by_mock.limit.assert_called_once_with(limit)
        limit_mock.all.assert_called_once()
        
        self.assertEqual(len(result), len(expected_summaries))
        for i, summary in enumerate(result):
            self.assertEqual(summary.vendor, expected_summaries[i].vendor)
            self.assertEqual(summary.count, expected_summaries[i].count)
            self.assertEqual(summary.total_amount, expected_summaries[i].total_amount)
            
    def test_get_top_vendors_custom_limit(self):
        """Test retrieving top vendors with custom limit."""
        # Arrange
        year = 2023
        limit = 10
        mock_results = [('Vendor1', 10, -500.0)]  # Just need one for this test
        
        query_mock = self.mock_db.query.return_value
        where_mock = query_mock.where.return_value
        group_by_mock = where_mock.group_by.return_value
        order_by_mock = group_by_mock.order_by.return_value
        limit_mock = order_by_mock.limit.return_value
        limit_mock.all.return_value = mock_results

        # Act
        result = self.repo.get_top_vendors(year, limit)

        # Assert
        order_by_mock.limit.assert_called_once_with(limit)
        
    def test_get_top_vendors_no_vendors(self):
        """Test retrieving top vendors when no vendors exist for the year."""
        # Arrange
        year = 2020  # Year with no vendors
        limit = 5
        
        query_mock = self.mock_db.query.return_value
        where_mock = query_mock.where.return_value
        group_by_mock = where_mock.group_by.return_value
        order_by_mock = group_by_mock.order_by.return_value
        limit_mock = order_by_mock.limit.return_value
        limit_mock.all.return_value = []

        # Act
        result = self.repo.get_top_vendors(year, limit)

        # Assert
        self.assertEqual(result, [])
        self.assertEqual(len(result), 0)
        
    def test_get_top_vendors_database_error(self):
        """Test that get_top_vendors handles database errors."""
        # Arrange
        year = 2023
        limit = 5
        
        query_mock = self.mock_db.query.return_value
        query_mock.where.side_effect = SQLAlchemyError("Database error")
        
        # Act/Assert
        with self.assertRaises(SQLAlchemyError):
            self.repo.get_top_vendors(year, limit)

    def test_get_transactions_by_year(self):
        """Test retrieving all transactions for a specific year."""
        # Arrange
        year = 2023
        mock_transactions = [MagicMock(spec=Transaction) for _ in range(10)]
        
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        where_mock = options_mock.where.return_value
        where_mock.all.return_value = mock_transactions

        # Act
        result = self.repo.get_transactions_by_year(year)

        # Assert
        self.mock_db.query.assert_called_once_with(Transaction)
        query_mock.options.assert_called_once()
        options_mock.where.assert_called_once()
        where_mock.all.assert_called_once()
        self.assertEqual(result, mock_transactions)
        
    def test_get_transactions_by_year_no_transactions(self):
        """Test retrieving transactions for a year with no transactions."""
        # Arrange
        year = 2020  # Year with no transactions
        
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        where_mock = options_mock.where.return_value
        where_mock.all.return_value = []

        # Act
        result = self.repo.get_transactions_by_year(year)

        # Assert
        self.assertEqual(result, [])
        self.assertEqual(len(result), 0)
        
    def test_get_transactions_by_year_invalid_year(self):
        """Test retrieving transactions with an invalid year format."""
        # Arrange
        year = "invalid_year"  # Non-integer year
        
        # Set up the mocks to raise the expected SQLAlchemy error when extract function is called
        query_mock = self.mock_db.query.return_value
        options_mock = query_mock.options.return_value
        # Simulate the error being raised when SQLAlchemy tries to process the invalid year
        options_mock.where.side_effect = SQLAlchemyError("Invalid input syntax for type integer")
        
        # Act/Assert
        with self.assertRaises(SQLAlchemyError):
            self.repo.get_transactions_by_year(year)


if __name__ == "__main__":
    unittest.main() 