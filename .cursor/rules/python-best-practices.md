# Python Best Practices

## Code Formatting with Black

Black is our chosen code formatter with a line length of 120 characters. Follow these guidelines:

1. **Configuration**:
   - Use the project's `.pre-commit-config.yaml` to ensure Black runs automatically
   - Do not override Black's formatting decisions with inline comments
   - The project uses a line length of 120 characters

2. **Integration**:
   - Configure your editor to run Black on save
   - Run `black .` before committing if not using pre-commit hooks
   - Do not mix other formatters with Black

3. **Style Consistency**:
   - Accept Black's opinionated formatting
   - Use double quotes for strings (Black will enforce this)
   - Let Black handle line breaks and whitespace

## Docstrings

Use Google-style docstrings for all public functions, classes, and methods:

```python
def process_transaction(transaction_data: dict, category_map: dict = None) -> dict:
    """Process a financial transaction and assign a category.
    
    Args:
        transaction_data: Dictionary containing transaction information.
            Must include 'amount' and 'description' keys.
        category_map: Optional mapping of keywords to categories.
            Defaults to None, which uses the standard category map.
            
    Returns:
        Processed transaction with added 'category' and 'processed_date' fields.
        
    Raises:
        ValueError: If transaction_data is missing required fields.
        CategoryError: If unable to assign a category.
    """
```

### Docstring Guidelines:

1. **Class Docstrings**:
   - Describe the class's purpose and behavior
   - Document public attributes and methods
   - Include examples for complex classes

2. **Function Docstrings**:
   - Document parameters with type information
   - Describe return values
   - Document exceptions that may be raised
   - Include examples for complex functions

3. **Module Docstrings**:
   - Place at the top of the file
   - Describe the module's purpose and contents
   - List key classes and functions

## Type Annotations

Use type hints consistently:

```python
def calculate_monthly_total(
    transactions: List[Dict[str, Any]], 
    month: int, 
    year: int
) -> Decimal:
    """Calculate the total expenses for a specific month."""
```

1. **Type Annotation Guidelines**:
   - Use type hints for all function parameters and return values
   - Import types from `typing` module (`List`, `Dict`, `Optional`, etc.)
   - Use `Any` sparingly, only when truly necessary
   - Use `Optional[Type]` instead of `Type | None` for Python 3.9 compatibility

## Logging

Use the standard Python logging module with consistent patterns:

```python
import logging

# Module-level logger
logger = logging.getLogger(__name__)

def process_file(filepath: str) -> int:
    """Process a transaction file and return the number of records processed."""
    try:
        logger.info("Processing file: %s", filepath)
        # Processing logic here
        record_count = 42  # Example count
        logger.info("Successfully processed %d records from %s", record_count, filepath)
        return record_count
    except Exception as e:
        logger.exception("Error processing file %s: %s", filepath, str(e))
        raise
```

### Logging Guidelines:

1. **Logger Setup**:
   - Create a module-level logger using `logging.getLogger(__name__)`
   - Do not configure loggers in modules (configuration belongs in the application entry point)
   - Use consistent logger names based on module structure

2. **Log Levels**:
   - `DEBUG`: Detailed information for debugging
   - `INFO`: Confirmation that things are working as expected
   - `WARNING`: Indication that something unexpected happened, but the application still works
   - `ERROR`: Due to a more serious problem, the application couldn't perform a function
   - `CRITICAL`: A serious error indicating the application may be unable to continue running

3. **Log Message Format**:
   - Use string formatting with logger methods, not f-strings
   - Include relevant context in log messages
   - For exceptions, use `logger.exception()` to include the traceback

4. **Sensitive Data**:
   - Never log sensitive information (passwords, API keys, personal data)
   - Mask or truncate sensitive fields when logging

## Error Handling

Follow these error handling practices:

1. **Custom Exceptions**:
   - Create custom exception classes for business logic errors
   - Inherit from appropriate base exceptions
   - Use descriptive names that indicate the error condition

   ```python
   class CategoryAssignmentError(Exception):
       """Raised when a transaction cannot be assigned to a category."""
       pass
   ```

2. **Exception Handling**:
   - Be specific about which exceptions to catch
   - Avoid bare `except:` clauses
   - Re-raise exceptions when appropriate
   - Log exceptions before re-raising

   ```python
   try:
       result = process_transaction(data)
   except (ValueError, KeyError) as e:
       logger.error("Invalid transaction data: %s", str(e))
       raise InvalidTransactionError(f"Could not process transaction: {e}") from e
   ```

## Testing

Follow these testing best practices:

1. **Test Structure**:
   - Use pytest for all tests
   - Name test files with `test_` prefix
   - Group tests by functionality or module
   - Use descriptive test names that explain the test case

2. **Test Coverage**:
   - Aim for high test coverage of business logic
   - Test happy paths and edge cases
   - Use parameterized tests for multiple similar test cases

3. **Fixtures and Mocks**:
   - Use pytest fixtures for test setup
   - Use mocks to isolate units of code
   - Create reusable fixtures for common test scenarios

   ```python
   @pytest.fixture
   def sample_transaction():
       return {
           "date": "2023-01-15",
           "amount": 42.50,
           "description": "GROCERY STORE PURCHASE",
           "vendor": "WHOLE FOODS"
       }
   
   def test_categorize_transaction(sample_transaction):
       result = categorize_transaction(sample_transaction)
       assert result["category"] == "Groceries"
   ```

## Performance Considerations

1. **Pandas Efficiency**:
   - Use vectorized operations instead of loops
   - Chain operations when appropriate
   - Use appropriate data types to reduce memory usage
   - Consider chunking for large datasets

2. **Resource Management**:
   - Use context managers (`with` statements) for file and database operations
   - Close connections and file handles explicitly when not using context managers
   - Use generators for large datasets to minimize memory usage

3. **Profiling**:
   - Use profiling tools to identify bottlenecks
   - Optimize only after measuring performance
   - Document performance considerations for complex operations 