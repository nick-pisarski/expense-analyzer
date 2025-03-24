# Expense Analyzer

## Description

A workflow for gathering, categorizing, and summarizing expenses.

## Features

### File Consumption

The expense analyzer supports importing financial data from various file formats, making it easy to analyze transactions from different sources.

### Supported File Formats

Currently, the system can process:
- **Bank of America PDF Statements**: Using the specialized `boa_pdf_reader.py` parser to extract transaction data from Bank of America's PDF statement format

### How File Import Works

1. **Modular Reader Architecture**: The system uses a base reader interface defined in `base_file_reader.py` that standardizes how different file types are processed.

2. **Format-Specific Parsing**: Each financial institution has its own statement format. Dedicated readers (like the BoA PDF reader) handle the specific parsing logic for each format.

3. **Unified Transaction Model**: All readers convert the source-specific data into a standardized `ReportTransaction` format that includes:
   - Vendor information
   - Transaction amount
   - Transaction date
   - Description
   - Source identifier

4. **Database Integration**: Once parsed, these standardized transactions are inserted into the database via the `ExpenseService`, which also handles categorization.

### Extending for Additional Statement Types

The modular design makes it straightforward to add support for other financial institutions:

1. Create a new reader that extends the base file reader interface
2. Implement the parsing logic specific to that statement format
3. Register the new reader in the `__init__.py` file

This allows the system to evolve as you add new financial accounts or as financial institutions update their statement formats.

**Note:** If you have a statement format not currently supported, you can contribute by creating a new reader implementation following the existing pattern.

### Transaction Categorization

The expense analyzer uses a sophisticated approach to automatically categorize financial transactions:

### How Categorization Works

1. **Embedding-Based Similarity**: Each transaction is converted into a vector embedding using `TransactionEmbedder`, capturing the semantic meaning of the transaction details.

2. **Similar Transaction Lookup**: When categorizing a new transaction, the system finds similar transactions that have already been categorized by comparing vector embeddings.

3. **AI-Powered Categorization**: The `SimpleCategorizer` uses OpenAI's models (specifically gpt-4o-mini) to intelligently assign categories based on:
   - The transaction details (vendor, amount, date)
   - A list of similar transactions that have already been categorized
   - The available category options in the system

4. **Contextual Decision Making**: The LLM is provided with structured information about the transaction and similar categorized transactions, allowing it to make informed category assignments based on patterns in your spending history.

### Categorization Process

When a new transaction is processed:
1. The system embeds the transaction data
2. Finds the most similar transactions with existing categories (up to 10)
3. Sends this context along with the new transaction to the LLM
4. The LLM returns the most appropriate category ID
5. The category is assigned to the transaction

This approach allows for increasingly accurate categorization as more transactions are added to the system, effectively learning from your spending patterns.

### Expense Reports

The expense analyzer provides powerful reporting capabilities to help you understand your spending patterns and financial habits through detailed, customizable reports.

### Report Generation

Reports are generated using a modular architecture that allows for multiple output formats:

1. **Base Generator Interface**: All report generators extend the `ExpenseReportGenerator` base class, providing a consistent interface for creating reports in different formats.

2. **Markdown Reports**: The system currently includes a `MarkdownExpenseReportGenerator` that produces comprehensive, well-formatted Markdown reports that can be easily shared or converted to other formats.

3. **Extensible Design**: The architecture allows for additional report generators to be added (like PDF, HTML, or Excel) by implementing the base generator interface.

### Report Contents

Each generated report includes detailed financial insights:

#### Overview Information
- Total number of transactions
- Total expenses for the period
- Highest-spending vendor with amount
- Highest-spending month with amount

#### Detailed Breakdowns
- **Top Vendors**: Lists the top 10 vendors by spending amount, including transaction count and total spent with each
- **Top Expenses**: Details the 10 largest individual transactions with date, vendor, amount, and category information
- **Monthly Summaries**: Breaks down expenses and income for each month, including:
  - Total expenses, incomes, and net balance
  - Category-by-category breakdown
  - Subcategory details for each main category
  - Transaction lists (when verbose mode is enabled)
- **Yearly Summary**: Aggregated financial data for the entire year
- **Average Month**: Statistical projection of your typical monthly spending:
  - Estimated total monthly expenses
  - Category-level average monthly spending

### Data Model

The reporting system uses a structured data model:

- `ReportData`: The main container for all report information
- `OverviewSummary`: Aggregated financial data for a time period
- `CategorySummary`: Detailed breakdown of transactions within a category
- `ReportDataItem`: Individual transaction data formatted for reporting
- `AverageMonthSummary`: Statistical projections of typical monthly spending

### Creating Custom Reports

To extend reporting capabilities:

1. Create a new class that implements the `ExpenseReportGenerator` interface
2. Implement the `generate_report` method to process the `ReportData` 
3. Format the output as needed for your specific report type

This modular design allows the system to evolve as your reporting needs change, supporting new visualization methods or export formats.

## How to Run

*Coming Soon*

## Still To Do:

1. Tests need to be written
    1. `simple_categorizer.py`
    2. `transaction_embedder.py`
    3. `boa_pdf_ready.py`
    4. `markdown_generator.py`

2. Improved Report Generation
3. Documentation on running
4. Clean up the startup SQL script for categories