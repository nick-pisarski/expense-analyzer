"""File reader for Bank of America CSV files"""

from expense_analyzer.file_readers.base_file_reader import BaseFileReader


class BankOfAmericaTransaction:
    """A transaction from Bank of America"""

    def __init__(self, data: dict):
        self.id = data["id"]
        self.vendor = data["vendor"]
        self.amount = data["amount"]
        self.date = data["date"]
        self.description = data["description"]

    def __str__(self):
        """String representation of the transaction"""
        return f"BankOfAmericaTransaction(id={self.id}, vendor={self.vendor}, amount={self.amount}, date={self.date}, description={self.description})"


class BankOfAmericaFileReader(BaseFileReader):
    """File reader for Bank of America CSV files"""

    def __init__(self, file_path: str):
        super().__init__(file_path)

    def read_transactions(self) -> list[BankOfAmericaTransaction]:
        """Read the file and return a list of transactions"""
        data = self.read_csv_file()
        return [BankOfAmericaTransaction(row) for row in data]

    def __str__(self):
        """String representation of the file reader"""
        return f"BankOfAmericaFileReader(file_path={self.file_path})"

    def __repr__(self):
        """Representation of the file reader"""
        return self.__str__()


if __name__ == "__main__":
    reader = BankOfAmericaFileReader("data/test.csv")
    transactions = reader.read_transactions()

    for transaction in transactions:
        print(transaction)
