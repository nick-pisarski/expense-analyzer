"""Unit tests for the ExpenseService class."""

import unittest
from datetime import date, datetime
from unittest.mock import MagicMock, patch

from expense_analyzer.database.models import Category, Transaction
from expense_analyzer.embedder.transaction_embedder import TransactionEmbedder
from expense_analyzer.models.source import Source
from expense_analyzer.models.transaction import ReportTransaction
from expense_analyzer.services.expense_service import ExpenseService


class TestExpenseService(unittest.TestCase):
    """Test cases for the ExpenseService class."""

    @patch("expense_analyzer.services.expense_service.get_db")
    @patch("expense_analyzer.services.expense_service.TransactionRepository")
    @patch("expense_analyzer.services.expense_service.CategoryRepository")
    @patch("expense_analyzer.services.expense_service.TransactionCategoryRepository")
    @patch("expense_analyzer.services.expense_service.TransactionEmbedder")
    @patch("expense_analyzer.services.expense_service.SimpleCategorizer")
    def setUp(
        self,
        mock_categorizer_class,
        mock_embedder_class,
        mock_transaction_category_repo_class,
        mock_category_repo_class,
        mock_transaction_repo_class,
        mock_get_db,
    ):
        """Set up test fixtures before each test method."""
        # Setup mocks
        self.mock_db = MagicMock()
        mock_get_db.return_value = self.mock_db

        self.mock_transaction_repo = MagicMock()
        mock_transaction_repo_class.return_value = self.mock_transaction_repo

        self.mock_category_repo = MagicMock()
        mock_category_repo_class.return_value = self.mock_category_repo

        self.mock_transaction_category_repo = MagicMock()
        mock_transaction_category_repo_class.return_value = self.mock_transaction_category_repo

        self.mock_embedder = MagicMock()
        mock_embedder_class.return_value = self.mock_embedder

        self.mock_categorizer = MagicMock()
        mock_categorizer_class.return_value = self.mock_categorizer

        # Initialize service
        self.service = ExpenseService()

        # Common test data
        self.report_transaction_dict = {
            "id": 1,
            "vendor": "Test Vendor",
            "amount": -100.0,
            "date": "2025-03-01",
            "description": "Test transaction",
            "source": Source.BANK_OF_AMERICA,
        }

        self.report_transaction = ReportTransaction(self.report_transaction_dict)

        self.db_transaction = Transaction(
            id=1,
            vendor="Test Vendor",
            amount=-100.0,
            date=date(2025, 3, 1),
            description="Test transaction",
            source=Source.BANK_OF_AMERICA,
        )

        self.test_category = Category(id=1, name="Test Category")
        self.db_transaction.category = self.test_category

        self.test_embedding = [0.1, 0.2, 0.3]  # Simple mock embedding

    def test_init(self):
        """Test service initialization."""
        self.assertIsNotNone(self.service)
        self.assertEqual(self.service.db, self.mock_db)
        self.assertEqual(self.service.transaction_repository, self.mock_transaction_repo)
        self.assertEqual(self.service.category_repository, self.mock_category_repo)
        self.assertEqual(self.service.transaction_category_repository, self.mock_transaction_category_repo)
        self.assertEqual(self.service.embedder, self.mock_embedder)
        self.assertEqual(self.service.categorizer, self.mock_categorizer)

    def test_enter_exit(self):
        """Test context manager behavior."""
        with self.service as service:
            self.assertEqual(service, self.service)
        self.mock_db.close.assert_called_once()

    def test_close(self):
        """Test explicit close method."""
        self.service.close()
        self.mock_db.close.assert_called_once()

    def test_convert_report_transactions_to_database_transactions(self):
        """Test converting ReportTransaction objects to database-compatible dictionaries."""
        # Arrange
        report_transactions = [self.report_transaction]

        # Act
        result = self.service._convert_report_transactions_to_database_transactions(report_transactions)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["vendor"], "Test Vendor")
        self.assertEqual(result[0]["amount"], -100.0)
        self.assertEqual(result[0]["date"], "2025-03-01")
        self.assertEqual(result[0]["description"], "Test transaction")
        self.assertEqual(result[0]["source"], Source.BANK_OF_AMERICA)

    def test_insert_transactions(self):
        """Test inserting transactions into the database."""
        # Arrange
        report_transactions = [self.report_transaction]
        self.mock_category_repo.get_all_subcategories.return_value = [self.test_category]
        self.mock_categorizer.categorize.return_value = self.test_category
        self.mock_embedder.embed_transaction.return_value = self.test_embedding
        self.mock_transaction_repo.create_transaction.return_value = self.db_transaction

        # Act
        result = self.service.insert_transactions(report_transactions)

        # Assert
        self.assertEqual(result, 1)
        self.mock_category_repo.get_all_subcategories.assert_called_once()
        self.mock_categorizer.categorize.assert_called_once()
        self.mock_embedder.embed_transaction.assert_called()
        self.mock_transaction_repo.create_transaction.assert_called_once()

    def test_insert_transactions_no_category_match(self):
        """Test inserting transactions that don't match a category."""
        # Arrange
        report_transactions = [self.report_transaction]
        self.mock_category_repo.get_all_subcategories.return_value = [self.test_category]
        self.mock_categorizer.categorize.return_value = None  # No category match
        self.mock_embedder.embed_transaction.return_value = self.test_embedding
        self.mock_transaction_repo.create_transaction.return_value = self.db_transaction

        # Act
        result = self.service.insert_transactions(report_transactions)

        # Assert
        self.assertEqual(result, 1)
        self.mock_category_repo.get_all_subcategories.assert_called_once()
        self.mock_categorizer.categorize.assert_called_once()
        self.mock_embedder.embed_transaction.assert_called()
        self.mock_transaction_repo.create_transaction.assert_called_once()

        # Verify the transaction was created without a category_id
        called_transaction = self.mock_transaction_repo.create_transaction.call_args[0][0]
        self.assertNotIn("category_id", called_transaction)

    def test_insert_transactions_creation_failure(self):
        """Test handling transaction creation failures."""
        # Arrange
        report_transactions = [self.report_transaction]
        self.mock_category_repo.get_all_subcategories.return_value = [self.test_category]
        self.mock_categorizer.categorize.return_value = self.test_category
        self.mock_embedder.embed_transaction.return_value = self.test_embedding
        self.mock_transaction_repo.create_transaction.return_value = None  # Creation failed

        # Act
        result = self.service.insert_transactions(report_transactions)

        # Assert
        self.assertEqual(result, 0)  # No transactions created successfully

    def test_get_transactions_by_date_range(self):
        """Test retrieving transactions by date range."""
        # Arrange
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 3, 31)
        expected_transactions = [self.db_transaction]
        self.mock_transaction_category_repo.get_transactions_by_date_range.return_value = expected_transactions

        # Act
        result = self.service.get_transactions_by_date_range(start_date, end_date)

        # Assert
        self.mock_transaction_category_repo.get_transactions_by_date_range.assert_called_once_with(start_date, end_date)
        self.assertEqual(result, expected_transactions)

    def test_get_all_transactions(self):
        """Test retrieving all transactions."""
        # Arrange
        expected_transactions = [self.report_transaction]
        self.mock_transaction_category_repo.get_transactions.return_value = expected_transactions

        # Act
        result = self.service.get_all_transactions()

        # Assert
        self.mock_transaction_category_repo.get_transactions.assert_called_once()
        self.assertEqual(result, expected_transactions)

    def test_get_transactions_without_category(self):
        """Test retrieving transactions without a category."""
        # Arrange
        expected_transactions = [self.db_transaction]
        self.mock_transaction_repo.get_transactions_without_category.return_value = expected_transactions

        # Act
        result = self.service.get_transactions_without_category()

        # Assert
        self.mock_transaction_repo.get_transactions_without_category.assert_called_once()
        self.assertEqual(result, expected_transactions)

    def test_get_transactions_with_category(self):
        """Test retrieving transactions with a category."""
        # Arrange
        expected_transactions = [self.db_transaction]
        self.mock_transaction_category_repo.get_transactions_with_category.return_value = expected_transactions

        # Act
        result = self.service.get_transactions_with_category()

        # Assert
        self.mock_transaction_category_repo.get_transactions_with_category.assert_called_once()
        self.assertEqual(result, expected_transactions)

    def test_embed_transactions(self):
        """Test embedding transactions."""
        # Arrange
        transactions = [self.db_transaction]
        embeddings = [self.test_embedding]
        self.mock_transaction_category_repo.get_transactions_with_category.return_value = transactions
        self.mock_embedder.embed_transactions.return_value = embeddings

        # Act
        self.service.embed_transactions()

        # Assert
        self.mock_transaction_category_repo.get_transactions_with_category.assert_called_once()
        self.mock_embedder.embed_transactions.assert_called_once_with(transactions)
        self.mock_transaction_repo.update_transaction.assert_called_once()

        # Verify transaction was updated with embedding
        self.assertEqual(self.db_transaction.embedding, self.test_embedding)

    def test_find_similar_transactions_with_existing_embedding(self):
        """Test finding similar transactions when transaction has an embedding."""
        # Arrange
        transaction = self.db_transaction
        transaction.embedding = self.test_embedding
        expected_similar = [MagicMock(spec=Transaction) for _ in range(5)]
        self.mock_transaction_category_repo.find_similar_transactions.return_value = expected_similar

        # Act
        result = self.service.find_similar_transactions(transaction)

        # Assert
        self.mock_transaction_category_repo.find_similar_transactions.assert_called_once_with(self.test_embedding, 5)
        self.mock_embedder.embed_transaction.assert_not_called()  # Shouldn't be called if embedding exists
        self.assertEqual(result, expected_similar)

    def test_find_similar_transactions_without_embedding(self):
        """Test finding similar transactions when transaction has no embedding."""
        # Arrange
        transaction = self.db_transaction
        transaction.embedding = None
        expected_similar = [MagicMock(spec=Transaction) for _ in range(5)]
        self.mock_embedder.embed_transaction.return_value = self.test_embedding
        self.mock_transaction_category_repo.find_similar_transactions.return_value = expected_similar

        # Act
        result = self.service.find_similar_transactions(transaction)

        # Assert
        self.mock_embedder.embed_transaction.assert_called_once_with(transaction)
        self.mock_transaction_category_repo.find_similar_transactions.assert_called_once_with(self.test_embedding, 5)
        self.assertEqual(result, expected_similar)

    def test_update_transactions_category(self):
        """Test updating transaction categories."""
        # Arrange
        transactions = [self.db_transaction]
        self.mock_category_repo.get_all_subcategories.return_value = [self.test_category]
        self.mock_categorizer.categorize.return_value = self.test_category
        self.mock_embedder.embed_transaction.return_value = self.test_embedding

        # Act
        self.service.update_transactions_category(transactions)

        # Assert
        self.mock_category_repo.get_all_subcategories.assert_called_once()
        self.mock_categorizer.categorize.assert_called_once()
        self.mock_embedder.embed_transaction.assert_called()
        self.mock_transaction_repo.update_transaction.assert_called_once_with(self.db_transaction)

        # Verify transaction was updated
        self.assertEqual(self.db_transaction.category, self.test_category)
        self.assertEqual(self.db_transaction.embedding, self.test_embedding)

    def test_get_category_for_transaction(self):
        """Test getting a category for a transaction."""
        # Arrange
        transaction = self.db_transaction
        sub_categories = [self.test_category]
        similar_transactions = [MagicMock(spec=Transaction) for _ in range(10)]

        self.mock_embedder.embed_transaction.return_value = self.test_embedding
        self.mock_transaction_category_repo.find_similar_transactions.return_value = similar_transactions
        self.mock_categorizer.categorize.return_value = self.test_category

        # Act
        result = self.service._get_category_for_transaction(transaction, sub_categories)

        # Assert
        self.mock_embedder.embed_transaction.assert_called_once_with(transaction)
        self.mock_transaction_category_repo.find_similar_transactions.assert_called_once_with(self.test_embedding, 10)
        self.mock_categorizer.categorize.assert_called_once_with(transaction, similar_transactions, sub_categories)
        self.assertEqual(result, self.test_category)


if __name__ == "__main__":
    unittest.main()
