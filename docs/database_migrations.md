# Database Migrations Guide

This document explains how to manage database schema changes using Alembic migrations in the Expense Analyzer.

## Creating a New Migration

Migrations can be created in two ways:

### 1. Auto-generate from Model Changes
After modifying SQLAlchemy models, generate a migration automatically:
```bash
alembic revision --autogenerate -m "description of your change"
```
This compares your database's current state with your SQLAlchemy models and creates a migration file.

### 2. Create Empty Migration
To create a migration manually:
```bash
alembic revision -m "description of your change"
```
You'll need to fill in the `upgrade()` and `downgrade()` functions yourself.

## Running Migrations

### Upgrade Database
To apply all pending migrations:
```bash
alembic upgrade head
```

To apply a specific number of migrations:
```bash
alembic upgrade +1  # Apply next migration
```

### Downgrade Database
To reverse the most recent migration:
```bash
alembic downgrade -1
```

To reverse all migrations:
```bash
alembic downgrade base
```

## Checking Migration Status

View current revision:
```bash
alembic current
```

View migration history:
```bash
alembic history
```

View pending migrations:
```bash
alembic history --indicate-current
```

## Best Practices

1. **Always Review Auto-generated Migrations**: Check that the generated migration correctly captures your intended changes.

2. **Test Migrations**: Always test both upgrade and downgrade operations in a development environment.

3. **Backup Data**: Before running migrations in production, always backup your database.

4. **Version Control**: Commit migration files to version control along with the model changes that required them.

## Common Issues

### Migration Not Detected
If your model changes aren't being detected during auto-generation:
- Ensure your models are properly imported in your Alembic env.py
- Verify that your model changes affect the database schema
- Check that your database URL is correct

### Conflicts
If you get conflicts when running migrations:
1. Check if someone else has added migrations
2. Pull latest changes from version control
3. Run `alembic heads` to check for multiple heads
4. If needed, create a merge migration: `alembic merge heads -m "merge branches"`

## Example

Here's an example of adding a unique constraint to the transactions table:

```python
# First, modify the model
class Transaction(Base):
    __table_args__ = (
        UniqueConstraint(
            'vendor', 
            'amount', 
            'date', 
            'description',
            name='uix_transaction_details'
        ),
    )

# Then generate and run the migration
$ alembic revision --autogenerate -m "add transaction uniqueness constraint"
$ alembic upgrade head

# If needed, rollback
$ alembic downgrade -1
```