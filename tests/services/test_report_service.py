"""Unit tests for the ReportService class."""

import unittest
from datetime import date, datetime
from unittest.mock import MagicMock, patch

from expense_analyzer.database.models import Category, Transaction, VendorSummary
from expense_analyzer.models.reports import (
    AverageMonthSummary,
    CategorySummary,
    OverviewSummary,
    ReportData,
    ReportDataItem,
)
from expense_analyzer.services.report_service import ReportService


class TestReportService(unittest.TestCase):
    """Test cases for the ReportService class."""

    @patch("expense_analyzer.services.report_service.get_db")
    @patch("expense_analyzer.services.report_service.TransactionCategoryRepository")
    @patch("expense_analyzer.services.report_service.CategoryRepository")
    def setUp(
        self,
        mock_category_repo_class,
        mock_transaction_category_repo_class,
        mock_get_db,
    ):
        """Set up test fixtures before each test method."""
        # Setup mocks
        self.mock_db = MagicMock()
        mock_get_db.return_value = self.mock_db

        self.mock_transaction_category_repo = MagicMock()
        mock_transaction_category_repo_class.return_value = self.mock_transaction_category_repo

        self.mock_category_repo = MagicMock()
        mock_category_repo_class.return_value = self.mock_category_repo

        # Initialize service
        self.service = ReportService()

        # Common test data
        self.test_year = 2023
        
        # Create test categories
        self.parent_category = Category(id=1, name="Food", parent_id=None)
        self.sub_category = Category(id=2, name="Dining", parent_id=1)
        self.test_categories = [self.parent_category, self.sub_category]

        # Create test transactions
        self.test_transaction = Transaction(
            id=1,
            vendor="Test Restaurant",
            amount=-50.0,
            date=date(2023, 3, 15),
            description="Dinner",
            category_id=2  # Sub-category ID
        )
        
        # Create test vendor summaries
        self.test_vendor_summaries = [
            VendorSummary(vendor="Test Restaurant", total_amount=150.0, count=3),
            VendorSummary(vendor="Grocery Store", total_amount=120.0, count=2),
        ]

    def test_init(self):
        """Test service initialization."""
        self.assertIsNotNone(self.service)
        self.assertEqual(self.service.db, self.mock_db)
        self.assertEqual(self.service.repository, self.mock_transaction_category_repo)
        self.assertEqual(self.service.category_repository, self.mock_category_repo)

    def test_map_transaction_to_report_data_item(self):
        """Test mapping a transaction to a ReportDataItem."""
        # Act
        result = self.service._map_transaction_to_report_data_item(self.test_transaction, self.test_categories)
        
        # Assert
        self.assertIsInstance(result, ReportDataItem)
        self.assertEqual(result.date, self.test_transaction.date)
        self.assertEqual(result.amount, self.test_transaction.amount)
        self.assertEqual(result.category, self.parent_category)
        self.assertEqual(result.sub_category, self.sub_category)
        self.assertEqual(result.vendor, self.test_transaction.vendor)

    def test_get_total_expenses(self):
        """Test getting total expenses from transactions."""
        # Arrange
        transactions = [
            ReportDataItem(
                date=date(2023, 3, 15),
                amount=-50.0,
                category=self.parent_category,
                sub_category=self.sub_category,
                vendor="Test Restaurant"
            ),
            ReportDataItem(
                date=date(2023, 3, 16),
                amount=-30.0,
                category=self.parent_category,
                sub_category=self.sub_category,
                vendor="Test Restaurant"
            ),
            ReportDataItem(
                date=date(2023, 3, 17),
                amount=10.0,  # Positive amount, should be ignored
                category=self.parent_category,
                sub_category=self.sub_category,
                vendor="Refund"
            )
        ]
        
        # Act
        result = self.service._get_total_expenses(transactions)
        
        # Assert
        self.assertEqual(result, 80.0)  # 50 + 30

    def test_get_top_vendors(self):
        """Test getting top vendors by expense amount."""
        # Arrange
        self.mock_transaction_category_repo.get_top_vendors.return_value = self.test_vendor_summaries
        
        # Act
        result = self.service._get_top_vendors(self.test_year)
        
        # Assert
        self.assertEqual(result, self.test_vendor_summaries)
        self.mock_transaction_category_repo.get_top_vendors.assert_called_once_with(self.test_year, limit=10)

    def test_get_highest_spending_month(self):
        """Test getting the highest spending month."""
        # Arrange - Create mock summary objects that return the desired total_expenses
        january_summary = MagicMock(spec=OverviewSummary)
        january_summary.total_expenses = 100.0
        
        february_summary = MagicMock(spec=OverviewSummary)
        february_summary.total_expenses = 150.0
        
        march_summary = MagicMock(spec=OverviewSummary)
        march_summary.total_expenses = 80.0
        
        per_month_data = {
            "January": january_summary,
            "February": february_summary,
            "March": march_summary,
        }
        
        # Act
        month, summary = self.service._get_highest_spending_month(per_month_data)
        
        # Assert
        self.assertEqual(month, "February")
        self.assertEqual(summary.total_expenses, 150.0)

    def test_get_highest_spending_vendor(self):
        """Test getting the highest spending vendor."""
        # Act
        result = self.service._get_highest_spending_vendor(self.test_vendor_summaries)
        
        # Assert
        self.assertEqual(result.vendor, "Test Restaurant")
        self.assertEqual(result.total_amount, 150.0)

    def test_generate_report_data(self):
        """Test generating report data."""
        # Arrange
        self.mock_category_repo.get_all_categories.return_value = self.test_categories
        self.mock_transaction_category_repo.get_transactions_by_year.return_value = [self.test_transaction]
        self.mock_transaction_category_repo.get_top_vendors.return_value = self.test_vendor_summaries
        self.mock_transaction_category_repo.get_top_expenses.return_value = [self.test_transaction]
        
        # Act
        result = self.service.generate_report_data(self.test_year)
        
        # Assert
        self.assertIsInstance(result, ReportData)
        self.assertEqual(result.year, self.test_year)
        self.assertIsInstance(result.per_month_data, dict)
        self.assertIsInstance(result.per_year_data, OverviewSummary)
        self.assertIsInstance(result.average_month, AverageMonthSummary)
        self.assertEqual(len(result.top_vendors), len(self.test_vendor_summaries))
        self.assertEqual(result.total_transactions, 1)

    def test_get_per_month_data_for_year(self):
        """Test getting per month data for a year."""
        # Arrange
        transactions = [
            ReportDataItem(
                date=date(2023, 1, 15),
                amount=-50.0,
                category=self.parent_category,
                sub_category=self.sub_category,
                vendor="Test Restaurant"
            ),
            ReportDataItem(
                date=date(2023, 3, 16),
                amount=-30.0,
                category=self.parent_category,
                sub_category=self.sub_category,
                vendor="Test Restaurant"
            )
        ]
        
        # Act
        result = self.service._get_per_month_data_for_year(transactions)
        
        # Assert
        self.assertIn("January", result)
        self.assertIn("March", result)
        self.assertEqual(len(result), 2)  # Should have data for two months
        self.assertIsInstance(result["January"], OverviewSummary)
        self.assertIsInstance(result["March"], OverviewSummary)

    def test_get_average_month(self):
        """Test getting average month summary."""
        # Arrange
        transactions = [
            ReportDataItem(
                date=date(2023, 1, 15),
                amount=-50.0,
                category=self.parent_category,
                sub_category=self.sub_category,
                vendor="Test Restaurant"
            ),
            ReportDataItem(
                date=date(2023, 2, 16),
                amount=-30.0,
                category=self.parent_category,
                sub_category=self.sub_category,
                vendor="Test Restaurant"
            )
        ]
        
        # Act
        result = self.service._get_average_month(transactions)
        
        # Assert
        self.assertIsInstance(result, AverageMonthSummary)
        # Since we have transactions across 2 months and total expenses of 80,
        # the average should be 40
        self.assertEqual(result.estimated_total_expenses, -40.0)


if __name__ == "__main__":
    unittest.main() 