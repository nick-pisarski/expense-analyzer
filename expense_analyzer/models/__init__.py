"""Models for expense analyzer"""

from expense_analyzer.models.transaction import Transaction
from expense_analyzer.models.boa_transaction import BankOfAmericaTransaction

__all__ = ["Transaction", "BankOfAmericaTransaction"]
