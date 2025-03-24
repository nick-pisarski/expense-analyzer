"""Unit tests for the TransactionRepository class."""

import unittest
from unittest.mock import MagicMock, patch
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from expense_analyzer.database.models import Transaction
from expense_analyzer.database.repositories.transaction_repository import TransactionRepository
from expense_analyzer.models.source import Source


class TestTransactionRepository(unittest.TestCase):
    """Test cases for the TransactionRepository class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_db = MagicMock(spec=Session)
        self.repo = TransactionRepository(self.mock_db)

        # Common test data
        self.transaction_data = {
            "vendor": "Test Vendor",
            "amount": -100.0,
            "date": date(2025, 3, 1),
            "description": "Test transaction",
            "source": Source.BANK_OF_AMERICA,
        }

    def test_create_unique_transaction(self):
        """Test creating a new unique transaction succeeds."""
        # Arrange
        self.mock_db.commit.return_value = None  # Normal commit, no exception

        # Act
        result = self.repo.create_transaction(self.transaction_data)

        # Assert
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()
        self.assertEqual(result.vendor, self.transaction_data["vendor"])
        self.assertEqual(result.amount, self.transaction_data["amount"])
        self.assertEqual(result.date, self.transaction_data["date"])
        self.assertEqual(result.description, self.transaction_data["description"])
        self.assertEqual(result.source, self.transaction_data["source"])

    def test_create_duplicate_transaction(self):
        """Test creating a duplicate transaction returns existing transaction."""
        # Arrange
        existing_transaction = Transaction(**self.transaction_data)

        # Mock the commit to raise IntegrityError
        self.mock_db.commit.side_effect = IntegrityError("statement", "params", "orig")

        # Mock the query to return existing transaction after rollback
        self.mock_db.query.return_value.filter.return_value.first.return_value = existing_transaction

        # Act
        result = self.repo.create_transaction(self.transaction_data)

        # Assert
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.rollback.assert_called_once()
        self.assertEqual(result.vendor, existing_transaction.vendor)
        self.assertEqual(result.amount, existing_transaction.amount)
        self.assertEqual(result.date, existing_transaction.date)
        self.assertEqual(result.description, existing_transaction.description)
        self.assertEqual(result.source, existing_transaction.source)

    def test_create_transaction_with_null_description(self):
        """Test creating transactions with null descriptions are still checked for uniqueness."""
        # Arrange
        transaction_data_no_description = self.transaction_data.copy()
        del transaction_data_no_description["description"]

        existing_transaction = Transaction(**transaction_data_no_description)

        # Mock the commit to raise IntegrityError
        self.mock_db.commit.side_effect = IntegrityError("statement", "params", "orig")

        # Mock the query to return existing transaction after rollback
        self.mock_db.query.return_value.filter.return_value.first.return_value = existing_transaction

        # Act
        result = self.repo.create_transaction(transaction_data_no_description)

        # Assert
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.rollback.assert_called_once()
        self.assertEqual(result.vendor, existing_transaction.vendor)
        self.assertEqual(result.amount, existing_transaction.amount)
        self.assertEqual(result.date, existing_transaction.date)
        self.assertIsNone(result.description)
        self.assertEqual(result.source, existing_transaction.source)

    def test_get_transaction(self):
        """Test retrieving a transaction by ID."""
        # Arrange
        transaction_id = 1
        mock_transaction = MagicMock(spec=Transaction)
        mock_transaction.id = transaction_id
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_transaction

        # Act
        result = self.repo.get_transaction(transaction_id)

        # Assert
        self.mock_db.query.assert_called_once_with(Transaction)
        self.mock_db.query.return_value.filter.assert_called_once()
        self.assertEqual(result, mock_transaction)

    def test_get_all_transactions(self):
        """Test retrieving all transactions."""
        # Arrange
        mock_transactions = [MagicMock(spec=Transaction) for _ in range(3)]
        self.mock_db.query.return_value.all.return_value = mock_transactions

        # Act
        result = self.repo.get_all_transactions()

        # Assert
        self.mock_db.query.assert_called_once_with(Transaction)
        self.mock_db.query.return_value.all.assert_called_once()
        self.assertEqual(result, mock_transactions)

    def test_get_transactions_by_date_range(self):
        """Test retrieving transactions within a date range."""
        # Arrange
        start_date = date(2025, 1, 1)
        end_date = date(2025, 3, 31)
        mock_transactions = [MagicMock(spec=Transaction) for _ in range(2)]
        self.mock_db.query.return_value.filter.return_value.all.return_value = mock_transactions

        # Act
        result = self.repo.get_transactions_by_date_range(start_date, end_date)

        # Assert
        self.mock_db.query.assert_called_once_with(Transaction)
        self.mock_db.query.return_value.filter.assert_called_once()
        self.assertEqual(result, mock_transactions)

    def test_get_top_expenses(self):
        """Test retrieving top expenses."""
        # Arrange
        limit = 5
        start_date = date(2025, 1, 1)
        end_date = date(2025, 3, 31)
        mock_transactions = [MagicMock(spec=Transaction) for _ in range(limit)]
        query_mock = self.mock_db.query.return_value
        filter_mock = query_mock.filter.return_value
        date_filter_mock = filter_mock.filter.return_value.filter.return_value
        order_mock = date_filter_mock.order_by.return_value
        order_mock.limit.return_value.all.return_value = mock_transactions

        # Act
        result = self.repo.get_top_expenses(limit, start_date, end_date)

        # Assert
        self.mock_db.query.assert_called_once_with(Transaction)
        query_mock.filter.assert_called_once()  # Filter for amount < 0
        self.assertEqual(result, mock_transactions)

    def test_summarize_by_vendor(self):
        """Test summarizing expenses by vendor."""
        # Arrange
        start_date = date(2025, 1, 1)
        end_date = date(2025, 3, 31)
        mock_results = [
            ("Vendor 1", -100.0),
            ("Vendor 2", -200.0),
        ]
        expected_summary = {
            "Vendor 1": 100.0,
            "Vendor 2": 200.0,
        }
        self.mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = mock_results

        # Act
        result = self.repo.summarize_by_vendor(start_date, end_date)

        # Assert
        self.mock_db.query.assert_called_once()
        self.assertEqual(result, expected_summary)

    def test_find_similar_transactions(self):
        """Test finding similar transactions using vector similarity."""
        # Arrange
        description = "Test description"
        limit = 3
        embedding = [0.1] * 1536
        mock_transactions = [MagicMock(spec=Transaction) for _ in range(limit)]

        # Mock the _generate_embedding method
        with patch.object(self.repo, "_generate_embedding", return_value=embedding) as mock_generate:
            # Set up the query chain
            query_mock = self.mock_db.query.return_value
            filter_mock = query_mock.filter.return_value
            order_mock = filter_mock.order_by.return_value
            order_mock.limit.return_value.all.return_value = mock_transactions

            # Act
            result = self.repo.find_similar_transactions(description, limit)

            # Assert
            mock_generate.assert_called_once_with(description)
            self.mock_db.query.assert_called_once_with(Transaction)
            self.assertEqual(result, mock_transactions)

    def test_find_similar_transactions_with_provided_embedding(self):
        """Test finding similar transactions with a provided embedding."""
        # Arrange
        description = "Test description"
        limit = 3
        embedding = [0.1] * 1536
        mock_transactions = [MagicMock(spec=Transaction) for _ in range(limit)]

        # Set up the query chain
        query_mock = self.mock_db.query.return_value
        filter_mock = query_mock.filter.return_value
        order_mock = filter_mock.order_by.return_value
        order_mock.limit.return_value.all.return_value = mock_transactions

        # Act
        result = self.repo.find_similar_transactions(description, limit, embedding)

        # Assert
        self.mock_db.query.assert_called_once_with(Transaction)
        self.assertEqual(result, mock_transactions)

    def test_generate_embedding(self):
        """Test generating an embedding for text."""
        # Arrange
        text = "Test text"
        expected_length = 1536

        # Act
        result = self.repo._generate_embedding(text)

        # Assert
        self.assertEqual(len(result), expected_length)
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], float)


if __name__ == "__main__":
    unittest.main()
