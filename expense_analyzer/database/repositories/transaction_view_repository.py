import logging
from typing import List

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from expense_analyzer.database.models import TransactionView, VendorSummary


class TransactionViewRepository:
    """Repository for getting transactions with views"""

    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(f"{__name__}.TransactionViewRepository")
        self.logger.debug("TransactionViewRepository initialized")

    def get_transaction_views(self) -> List[TransactionView]:
        """Get all transaction views"""
        self.logger.debug("Getting all transaction views")
        transaction_views = self.db.query(TransactionView).all()
        return transaction_views

    def get_top_expenses(self, limit: int = 5) -> List[TransactionView]:
        """Get the top expenses"""
        self.logger.debug(f"Getting the top {limit} expenses")
        transaction_views = (
            self.db.query(TransactionView)
            .where(TransactionView.amount < 0)
            .order_by(TransactionView.amount.asc())
            .limit(limit)
            .all()
        )
        return transaction_views

    def get_top_vendors(self, limit: int = 5) -> List[VendorSummary]:
        """Get the top vendors with the most expenses (negative transactions)"""
        self.logger.debug(f"Getting the top {limit} vendors by expense amount")
        results = (
            self.db.query(
                TransactionView.vendor,
                func.count(TransactionView.id).label("transaction_count"),
                func.sum(TransactionView.amount).label("total_amount"),
            )
            .filter(TransactionView.amount < 0)  # Only get expenses (negative amounts)
            .group_by(TransactionView.vendor)
            .order_by(func.count(TransactionView.id).desc())  # ASC because expenses are negative
            .limit(limit)
            .all()
        )
        return [VendorSummary(vendor=r[0], count=r[1], total_amount=abs(r[2])) for r in results]

    def get_transactions_by_year(self, year: int) -> List[TransactionView]:
        """Get all transactions for a specific year"""
        transactions = (
            self.db.query(TransactionView)
            .filter(TransactionView.amount < 0)  # Only get expenses (negative amounts)
            .filter(extract("year", TransactionView.date) == year)
            .all()
        )
        return transactions
