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
