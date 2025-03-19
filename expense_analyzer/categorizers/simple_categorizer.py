from openai import OpenAI
from expense_analyzer.database.models import Transaction, Category
from typing import List
import logging

CATEGORIZER_PROMPT = """
You are a helpful assistant that categorizes transactions.

You are given a transaction and a list of similar transactions.

You need to categorize the transaction into one of the following categories:
{categories}

The transaction to categorize is:
{transaction}

The similar transactions are:
{similar_transactions}

Return the category id of the transaction and nothing else.
"""

class SimpleCategorizer:
    """Categorizer for transactions"""

    def __init__(self):
        self.logger = logging.getLogger("expense_analyzer.categorizers.SimpleCategorizer")
        self.logger.debug("SimpleCategorizer initialized")
        self.client = OpenAI()

    def _get_prompt(self, transaction: Transaction, similar_transactions: List[Transaction], sub_categories: List[Category]) -> str:
        """Get the prompt for the categorizer"""
        category_list = "\n".join([f"ID: {c.id} | Name: {c.name}" for c in sub_categories])
        similar_transactions_list = "\n".join([f"{t}" for t in similar_transactions])
        return CATEGORIZER_PROMPT.format(
            categories=category_list,
            transaction=transaction,
            similar_transactions=similar_transactions_list
        )

    def categorize(self, transaction: Transaction, similar_transactions: List[Transaction], sub_categories: List[Category]) -> Category | None:
        """Categorize a transaction"""
        prompt = self._get_prompt(transaction, similar_transactions, sub_categories)
        self.logger.debug(f"Prompt: {prompt}")
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
            ]
        )

        category_id = response.choices[0].message.content

        if category_id and category_id.isdigit():
            #Find category by id
            category = next((c for c in sub_categories if c.id == int(category_id)), None)
            self.logger.debug(f"Category Assigned: {category.name} ({category.id}) for transaction {transaction.id}")
            return category
        
        self.logger.warning(f"No category id or invalid category id returned for transaction {transaction.id} category_id: {category_id}")
        return None