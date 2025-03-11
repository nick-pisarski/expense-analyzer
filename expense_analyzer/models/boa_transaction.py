from expense_analyzer.models.transaction import ReportTransaction
from expense_analyzer.models.source import Source


class BankOfAmericaTransaction(ReportTransaction):
    """A transaction from Bank of America"""

    def __init__(self, data: dict):
        super().__init__(data)

        # Additional properties from PDF
        self.posting_date = data.get("posting_date")
        self.reference_number = data.get("reference_number")
        self.account_number = data.get("account_number")
        self.transaction_type = data.get("transaction_type", self._determine_transaction_type())
        self.source = Source.BANK_OF_AMERICA

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
