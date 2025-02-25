"""Base class for file readers"""

import csv


class BaseFileReader:
    """Base class for file readers"""

    def __init__(self, file_path: str):
        """Initialize the file reader with a file path"""
        self.file_path = file_path

    def read_csv_file(self) -> list[dict]:
        """Read the file and return a list of rows"""
        with open(self.file_path, "r") as file:
            reader = csv.reader(file)
            rows = list(reader)  # Convert iterator to list
            headers = rows[0]
            return [dict(zip(headers, row)) for row in rows[1:]]
