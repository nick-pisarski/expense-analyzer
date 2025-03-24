import logging
from typing import List

from openai import OpenAI

from expense_analyzer.database.models import Category, Transaction

CATEGORIZER_PROMPT = """
You are a helpful assistant that is very good at assigning categorizes to financial transactions.

You are given a transaction and a list of similar transactions that have already been categorized.

You need to categorize the transaction into one of the following categories:
{categories}

Here are the similar transactions that have already been categorized and could be useful for making the categorization:
{similar_transactions}

The transaction to categorize is:
{transaction}

Use all of the information provided to make the best categorization.
If a category is not clearly assigned, return only the word 'None'.

Return the category id of the transaction and nothing else.
"""


class SimpleCategorizer:
    """Categorizer for transactions"""

    def __init__(self):
        self.logger = logging.getLogger("expense_analyzer.categorizers.SimpleCategorizer")
        self.logger.debug("SimpleCategorizer initialized")
        self.client = OpenAI()

    def _get_transaction_string(self, transaction: Transaction) -> str:
        """Get the string representation of a transaction"""
        return f"{transaction.id} | {transaction.vendor} | {transaction.amount} | {transaction.date} | {transaction.category_id} | {transaction.category.name if transaction.category else 'None'}"

    def _get_prompt(
        self, transaction: Transaction, similar_transactions: List[Transaction], sub_categories: List[Category]
    ) -> str:
        """Get the prompt for the categorizer"""
        category_list = "\n".join([f"ID: {c.id} | Name: {c.name}" for c in sub_categories])

        transaction_header = "ID | Vendor | Amount | Date | Category ID | Category Name"
        similar_transactions_list = (
            transaction_header + "\n" + "\n".join([self._get_transaction_string(t) for t in similar_transactions])
        )
        transaction_string = transaction_header + "\n" + self._get_transaction_string(transaction)
        return CATEGORIZER_PROMPT.format(
            categories=category_list, transaction=transaction_string, similar_transactions=similar_transactions_list
        )

    def categorize(
        self, transaction: Transaction, similar_transactions: List[Transaction], sub_categories: List[Category]
    ) -> Category | None:
        """Categorize a transaction"""
        prompt = self._get_prompt(transaction, similar_transactions, sub_categories)
        self.logger.debug(f"Prompt: {prompt}")
        response = self.client.chat.completions.create(
            # TODO: Update model to be an environment variable
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
            ],
        )

        category_id = response.choices[0].message.content.strip()
        self.logger.debug(f"Category ID from LLM: {category_id}")
        if category_id and category_id.isdigit():
            # Find category by id
            category = next((c for c in sub_categories if c.id == int(category_id)), None)
            self.logger.info(
                f"Category Assigned: {category.name} ({category.id}) for transaction {transaction.vendor} ({transaction.id})"
            )
            return category

        self.logger.warning(
            f"No category id or invalid category id returned for transaction {transaction.id} category_id: {category_id}"
        )
        return None
