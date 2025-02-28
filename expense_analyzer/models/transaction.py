from dataclasses import dataclass


@dataclass
class Transaction:
    """Class for all transactions"""

    id: str
    vendor: str
    amount: float
    date: str
    description: str
    category: str

    def __str__(self):
        """String representation of the transaction"""
        return f"Transaction(id={self.id}, vendor={self.vendor}, amount={self.amount}, date={self.date}, description={self.description})"
