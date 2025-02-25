"""Base class for file readers"""


class BaseFileReader:
    """Base class for file readers"""

    def __init__(self, file_path: str):
        """Initialize the file reader with a file path"""
        self.file_path = file_path

    def read_file(self):
        """Read the file and return a list of rows"""
        raise NotImplementedError("Subclasses must implement read_file()")

    def get_data(self):
        """Get the data from the file"""
        raise NotImplementedError("Subclasses must implement get_data()")
