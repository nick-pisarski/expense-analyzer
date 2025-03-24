from datetime import datetime
from typing import Optional

from expense_analyzer.models.source import Source


class ReportTransaction:
    """Class for all transactions"""

    def __init__(self, data: dict):
        """Initialize the transaction"""

        # Main fields
        self.id = data["id"]
        self.vendor = data["vendor"]
        self.amount = data["amount"]
        self.date = data["date"]
        self.description = data["description"]
        self.source = data["source"] if "source" in data else Source.UNKNOWN
        self.category = None

    def _determine_transaction_type(self) -> str:
        """Determine the transaction type based on the amount"""
        if self.amount < 0:
            return "expense"
        elif self.amount > 0:
            return "income"
        else:
            return "neutral"

    @property
    def is_expense(self) -> bool:
        """Check if the transaction is an expense"""
        return self.amount < 0

    @property
    def is_income(self) -> bool:
        """Check if the transaction is income"""
        return self.amount > 0

    @property
    def absolute_amount(self) -> float:
        """Get the absolute amount of the transaction"""
        return abs(self.amount)

    @property
    def date_obj(self) -> Optional[datetime]:
        """Get the transaction date as a datetime object"""
        try:
            return datetime.strptime(self.date, "%Y-%m-%d")
        except (ValueError, TypeError):
            return None

    @property
    def month(self) -> Optional[str]:
        """Get the month of the transaction"""
        if self.date_obj:
            return self.date_obj.strftime("%B")
        return None

    @property
    def year(self) -> Optional[int]:
        """Get the year of the transaction"""
        if self.date_obj:
            return self.date_obj.year
        return None

    def __str__(self):
        """String representation of the transaction"""
        transaction_type = "expense" if self.is_expense else "income" if self.is_income else "neutral"
        amount_str = f"${abs(self.amount):.2f}"
        return f"{self.vendor} - {amount_str} ({transaction_type}) on {self.date}"

    def __repr__(self):
        """Representation of the transaction"""
        return f"Transaction(id={self.id}, vendor={self.vendor}, amount={self.amount}, date={self.date}, description={self.description}, category={self.category})"
