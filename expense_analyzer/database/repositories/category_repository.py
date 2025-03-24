from expense_analyzer.database.models import Category


from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


import logging
from typing import List, Optional


class CategoryRepository:
    """Repository for category data"""

    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(f"{__name__}.CategoryRepository")
        self.logger.debug("CategoryRepository initialized")

    def create_category(self, name: str, parent_id: Optional[int] = None) -> Category:
        """Create a new category"""
        self.logger.info(f"Creating new category: {name} (parent_id: {parent_id})")
        category = Category(name=name, parent_id=parent_id)
        self.db.add(category)
        try:
            self.db.commit()
            self.db.refresh(category)
            self.logger.debug(f"Category created successfully with ID: {category.id}")
            return category
        except IntegrityError:
            self.logger.warning(f"Integrity error when creating category '{name}', rolling back")
            self.db.rollback()
            raise

    def get_category(self, category_id: int) -> Optional[Category]:
        """Get a category by ID"""
        self.logger.debug(f"Getting category with ID: {category_id}")
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if category:
            self.logger.debug(f"Found category: {category.name} (ID: {category.id})")
        else:
            self.logger.debug(f"No category found with ID: {category_id}")
        return category

    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Get a category by name"""
        self.logger.debug(f"Getting category with name: {name}")
        category = self.db.query(Category).filter(Category.name == name).first()
        if category:
            self.logger.debug(f"Found category: {category.name} (ID: {category.id})")
        else:
            self.logger.debug(f"No category found with name: {name}")
        return category

    def get_all_categories(self) -> List[Category]:
        """Get all categories"""
        self.logger.debug("Getting all categories")
        categories = self.db.query(Category).all()
        self.logger.debug(f"Retrieved {len(categories)} categories")
        return categories

    def get_root_categories(self) -> List[Category]:
        """Get all root categories (categories without a parent)"""
        self.logger.debug("Getting all root categories")
        categories = self.db.query(Category).filter(Category.parent_id.is_(None)).all()
        self.logger.debug(f"Retrieved {len(categories)} root categories")
        return categories

    def get_subcategories(self, parent_id: int) -> List[Category]:
        """Get all subcategories of a parent category"""
        self.logger.debug(f"Getting subcategories for parent ID: {parent_id}")
        categories = self.db.query(Category).filter(Category.parent_id == parent_id).all()
        self.logger.debug(f"Retrieved {len(categories)} subcategories for parent ID: {parent_id}")
        return categories

    def get_all_subcategories(self) -> List[Category]:
        """Get all subcategories"""
        self.logger.debug("Getting all subcategories")
        categories = self.db.query(Category).filter(Category.parent_id.is_not(None)).all()
        self.logger.debug(f"Retrieved {len(categories)} subcategories")
        return categories