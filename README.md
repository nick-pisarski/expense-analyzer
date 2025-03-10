# Expense Analyzer

## Description

A workflow for gathering, categorizing, and summarizing expenses, then creating a budget based on that.

## Steps

1. Read the `.csv` files row by row and use the LLM to extract information into a common structure
2. Populate the category, and insert into the postgres database
3. Generate Reports and Pie Graphs

## Reports

- Pie Graph of Spending per Category
- Vendor with most money spent
- Most Common Vendor

Collect the above for the following:

- Per Year
- Per Month
- Average Month

## To do

- Implement Categories and applying them to Transactions
- Report Generation
    - Markdown Summary
    - PDF with graphs, etc
- Implement Other File Readers
    - Bank Statements

## Features

### Transaction Categorization

Coming Soon

### Postgres SQL

Transactions will be stored in a Postgres Database for easy query 

- Must Check for duplicates in the database when inserting a record
    - How to verify uniqueness? Date, Vendor, Amount?
- Must a service class for interfacing with database
- It should have the `pgvector` plugin for embeddings
