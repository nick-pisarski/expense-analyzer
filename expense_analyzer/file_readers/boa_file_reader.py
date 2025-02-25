"""File reader for Bank of America CSV files"""

from expense_analyzer.file_readers.base_file_reader import BaseFileReader


class BankOfAmericaFileReader(BaseFileReader):
    """File reader for Bank of America CSV files"""

    def __init__(self, file_path: str):
        super().__init__(file_path)

    def read_file(self):
        """Read the file and return a list of rows"""
        pass

    def get_data(self):
        """Get the data from the file"""
        pass

    def __str__(self):
        """String representation of the file reader"""
        return f"BankOfAmericaFileReader(file_path={self.file_path})"

    def __repr__(self):
        """Representation of the file reader"""
        return self.__str__()
