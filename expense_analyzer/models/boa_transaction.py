from datetime import datetime
from typing import Optional


class BankOfAmericaTransaction:
    """A transaction from Bank of America"""

    def __init__(self, data: dict):
        self.id = data["id"]
        self.vendor = data["vendor"]
        self.amount = data["amount"]
        self.date = data["date"]
        self.description = data["description"]

        # Additional properties from PDF
        self.posting_date = data.get("posting_date")
        self.reference_number = data.get("reference_number")
        self.account_number = data.get("account_number")
        self.transaction_type = data.get("transaction_type", self._determine_transaction_type())
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
        base_info = (
            f"BankOfAmericaTransaction(id={self.id}, vendor={self.vendor}, amount=${self.amount:.2f}, date={self.date}"
        )

        # Add additional properties if they exist
        additional_info = []
        if self.posting_date:
            additional_info.append(f"posting_date={self.posting_date}")
        if self.reference_number:
            additional_info.append(f"ref_num={self.reference_number}")
        if self.account_number:
            additional_info.append(f"acct_num={self.account_number}")
        if self.category:
            additional_info.append(f"category={self.category}")
        if self.transaction_type:
            additional_info.append(f"type={self.transaction_type}")

        # Add description at the end as it can be long
        additional_info.append(f"description={self.description}")

        # Combine all information
        if additional_info:
            return base_info + ", " + ", ".join(additional_info) + ")"
        else:
            return base_info + ")"

    def __repr__(self):
        """Representation of the transaction"""
        return self.__str__()
