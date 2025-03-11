"""Unit tests for the database models."""

import unittest
from datetime import date

from expense_analyzer.database.models import Transaction, Category
from expense_analyzer.models.source import Source


class TestTransactionModel(unittest.TestCase):
    """Test cases for the Transaction model."""

    def test_transaction_properties(self):
        """Test the transaction properties."""
        # Test expense
        expense = Transaction(
            vendor="Test Vendor",
            amount=-100.0,
            date=date(2025, 3, 1),
            description="Test expense",
            source=Source.BANK_OF_AMERICA,
        )
        self.assertTrue(expense.is_expense)
        self.assertFalse(expense.is_income)
        self.assertEqual(expense.absolute_amount, 100.0)

        # Test income
        income = Transaction(
            vendor="Test Vendor",
            amount=200.0,
            date=date(2025, 3, 1),
            description="Test income",
            source=Source.BANK_OF_AMERICA,
        )
        self.assertFalse(income.is_expense)
        self.assertTrue(income.is_income)
        self.assertEqual(income.absolute_amount, 200.0)

        # Test zero amount
        zero = Transaction(
            vendor="Test Vendor",
            amount=0.0,
            date=date(2025, 3, 1),
            description="Test zero",
            source=Source.BANK_OF_AMERICA,
        )
        self.assertFalse(zero.is_expense)
        self.assertFalse(zero.is_income)
        self.assertEqual(zero.absolute_amount, 0.0)


class TestCategoryModel(unittest.TestCase):
    """Test cases for the Category model."""

    def test_category_relationships(self):
        """Test the category relationships."""
        # Create parent category
        parent = Category(name="Parent Category")

        # Create child category
        child = Category(name="Child Category", parent_id=1)  # Assuming parent.id would be 1

        # In a real database, we would set child.parent = parent
        # For this test, we'll manually set up the relationship
        parent.subcategories = [child]
        child.parent = parent

        # Test relationships
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.subcategories)
        self.assertEqual(len(parent.subcategories), 1)


if __name__ == "__main__":
    unittest.main()
