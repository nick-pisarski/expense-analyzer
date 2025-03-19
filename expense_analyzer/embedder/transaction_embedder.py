from typing import List
from expense_analyzer.database.models import Transaction
from openai import OpenAI


class TransactionEmbedder:
    """Embedder for transactions"""

    def __init__(self):
        """Initialize the TransactionEmbedder"""
        super().__init__()
        self.client = OpenAI()
        self.model = "text-embedding-3-small"

    def _transform_transaction_to_text(self, transaction: Transaction) -> str:
        """Transform a transaction into a text string"""
        return (
            f"Date: {transaction.date} "
            f"Amount: {transaction.amount} "
            f"Type: {'expense' if transaction.is_expense else 'income'} "
            f"Vendor: {transaction.vendor} "
            f"Description: {transaction.description or ''} "
            f"Source: {transaction.source.value} "
            f"Category: {transaction.category.name if transaction.category else 'Uncategorized'}"
        )

    def embed_transaction(self, transaction: Transaction) -> List[float]:
        """Embed a transaction into a vector embedding.

        Args:
            transaction: The transaction to embed

        Returns:
            A list of floats representing the embedding vector
        """
        text = self._transform_transaction_to_text(transaction)
        return self._embed_text(text)

    def embed_transactions(self, transactions: List[Transaction]) -> List[List[float]]:
        """Embed a batch of transactions into a list of vector embeddings.

        Args:
            transactions: List of transactions to embed

        Returns:
            List of embedding vectors, one for each input transaction
        """
        texts = [self._transform_transaction_to_text(transaction) for transaction in transactions]
        return self._embed_batch(texts)

    def _embed_text(self, text: str) -> List[float]:
        """Embed a text string into a vector embedding.

        Args:
            text: The text to embed

        Returns:
            A list of floats representing the embedding vector
        """
        response = self.client.embeddings.create(model=self.model, input=text)
        return response.data[0].embedding

    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of text strings into a list of vector embeddings.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors, one for each input text
        """
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [embedding.embedding for embedding in response.data]
