"""Unit tests for the CategoryRepository class."""

import unittest
from unittest.mock import MagicMock

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from expense_analyzer.database.models import Category
from expense_analyzer.database.repositories.category_repository import (
    CategoryRepository,
)


class TestCategoryRepository(unittest.TestCase):
    """Test cases for the CategoryRepository class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_db = MagicMock(spec=Session)
        self.repo = CategoryRepository(self.mock_db)

    def test_create_category(self):
        """Test creating a new category."""
        # Arrange
        category_name = "Test Category"
        parent_id = None

        # Act
        result = self.repo.create_category(category_name, parent_id)

        # Assert
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()
        self.assertEqual(result.name, category_name)
        self.assertEqual(result.parent_id, parent_id)

    def test_create_subcategory(self):
        """Test creating a subcategory."""
        # Arrange
        category_name = "Test Subcategory"
        parent_id = 1

        # Act
        result = self.repo.create_category(category_name, parent_id)

        # Assert
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()
        self.assertEqual(result.name, category_name)
        self.assertEqual(result.parent_id, parent_id)

    def test_create_duplicate_category_same_level(self):
        """Test creating a duplicate category at the same level raises an IntegrityError."""
        # Arrange
        category_name = "Duplicate Category"
        parent_id = None

        # Mock the commit method to raise IntegrityError
        self.mock_db.commit.side_effect = IntegrityError("Duplicate category", params=None, orig=None)

        # Act & Assert
        with self.assertRaises(IntegrityError):
            self.repo.create_category(category_name, parent_id)

        # Verify that rollback was called
        self.mock_db.rollback.assert_called_once()

    def test_create_duplicate_subcategory(self):
        """Test creating a duplicate subcategory under the same parent raises an IntegrityError."""
        # Arrange
        category_name = "Duplicate Subcategory"
        parent_id = 1

        # Mock the commit method to raise IntegrityError
        self.mock_db.commit.side_effect = IntegrityError("Duplicate subcategory", params=None, orig=None)

        # Act & Assert
        with self.assertRaises(IntegrityError):
            self.repo.create_category(category_name, parent_id)

        # Verify that rollback was called
        self.mock_db.rollback.assert_called_once()

    def test_create_same_category_name_different_parents(self):
        """Test creating categories with the same name but under different parents."""
        # Arrange
        category_name = "Same Name Category"
        parent_id_1 = 1
        parent_id_2 = 2

        # First call succeeds
        result1 = self.repo.create_category(category_name, parent_id_1)

        # Reset mock for second call
        self.mock_db.reset_mock()

        # Second call with different parent also succeeds
        result2 = self.repo.create_category(category_name, parent_id_2)

        # Assert
        self.assertEqual(result1.name, category_name)
        self.assertEqual(result1.parent_id, parent_id_1)
        self.assertEqual(result2.name, category_name)
        self.assertEqual(result2.parent_id, parent_id_2)
        self.assertEqual(self.mock_db.add.call_count, 1)  # Called once for the second category
        self.assertEqual(self.mock_db.commit.call_count, 1)  # Called once for the second category

    def test_get_category(self):
        """Test retrieving a category by ID."""
        # Arrange
        category_id = 1
        mock_category = MagicMock(spec=Category)
        mock_category.id = category_id
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_category

        # Act
        result = self.repo.get_category(category_id)

        # Assert
        self.mock_db.query.assert_called_once_with(Category)
        self.mock_db.query.return_value.filter.assert_called_once()
        self.assertEqual(result, mock_category)

    def test_get_category_by_name(self):
        """Test retrieving a category by name."""
        # Arrange
        category_name = "Test Category"
        mock_category = MagicMock(spec=Category)
        mock_category.name = category_name
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_category

        # Act
        result = self.repo.get_category_by_name(category_name)

        # Assert
        self.mock_db.query.assert_called_once_with(Category)
        self.mock_db.query.return_value.filter.assert_called_once()
        self.assertEqual(result, mock_category)

    def test_get_all_categories(self):
        """Test retrieving all categories."""
        # Arrange
        mock_categories = [MagicMock(spec=Category) for _ in range(3)]
        self.mock_db.query.return_value.all.return_value = mock_categories

        # Act
        result = self.repo.get_all_categories()

        # Assert
        self.mock_db.query.assert_called_once_with(Category)
        self.mock_db.query.return_value.all.assert_called_once()
        self.assertEqual(result, mock_categories)

    def test_get_root_categories(self):
        """Test retrieving root categories (categories without a parent)."""
        # Arrange
        mock_categories = [MagicMock(spec=Category) for _ in range(2)]
        self.mock_db.query.return_value.filter.return_value.all.return_value = mock_categories

        # Act
        result = self.repo.get_root_categories()

        # Assert
        self.mock_db.query.assert_called_once_with(Category)
        self.mock_db.query.return_value.filter.assert_called_once()
        self.assertEqual(result, mock_categories)

    def test_get_subcategories(self):
        """Test retrieving subcategories of a parent category."""
        # Arrange
        parent_id = 1
        mock_categories = [MagicMock(spec=Category) for _ in range(2)]
        self.mock_db.query.return_value.filter.return_value.all.return_value = mock_categories

        # Act
        result = self.repo.get_subcategories(parent_id)

        # Assert
        self.mock_db.query.assert_called_once_with(Category)
        self.mock_db.query.return_value.filter.assert_called_once()
        self.assertEqual(result, mock_categories)


if __name__ == "__main__":
    unittest.main()
