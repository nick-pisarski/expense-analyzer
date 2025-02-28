# Expense Analyzer Project Rules

## About This Project

This is a Python-based expense analysis system that processes financial data to provide insights and budgeting recommendations. The project uses modern Python tools and practices including Poetry for dependency management and pre-commit hooks for code quality.

## Technical Stack

- **Python**: ^3.9
- **Key Dependencies**:
  - psycopg2-binary: PostgreSQL database integration
  - pandas: Data manipulation and analysis
  - openai: LLM integration for expense categorization
  - matplotlib: Visualization and reporting
- **Development Tools**:
  - pytest: Testing framework
  - black: Code formatting
  - pre-commit: Git hooks for code quality

## Project Structure

```
expense-analyzer/
├── expense_analyzer/     # Main package directory
│   ├── file_readers/    # CSV and data input processing
│   └── models/          # Data models and database schemas
├── data/                # Data storage directory
└── tests/               # Test suite
```