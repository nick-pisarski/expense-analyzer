-- Seed script for categories and subcategories
-- This script creates a comprehensive set of categories and subcategories for expense tracking

-- First, ensure we're working with a clean slate for categories
-- TRUNCATE TABLE categories CASCADE;

-- Root categories
INSERT INTO categories (name, parent_id) VALUES
('Childcare', NULL),
('Healthcare', NULL),
('Food and Beverage', NULL),
('Entertainment', NULL),
('Housing (Mortgage and Taxes)', NULL),
('Housing Other (Utilities, repairs, etc.)', NULL),
('Transportation (Gas, Car, etc.)', NULL),
('Savings and Insurance (401k, IRA, etc.)', NULL),
('Personal Care (Charity, Misc, Other, etc.)', NULL),
('Miscellaneous', NULL);

--subcategories

-- Housing (Mortgage and Taxes) subcategories
WITH parent AS (SELECT id FROM categories WHERE name = 'Housing (Mortgage and Taxes)')
INSERT INTO categories (name, parent_id)
SELECT name, parent.id FROM parent, (VALUES
    ('Mortgage and Escrow'),
    ('Flood Insurance')
) AS subcategories(name);

-- Housing Other subcategories
WITH parent AS (SELECT id FROM categories WHERE name = 'Housing Other (Utilities, repairs, etc.)')
INSERT INTO categories (name, parent_id)
SELECT name, parent.id FROM parent, (VALUES
    ('Cell Phone'),
    ('Electricity'),
    ('Cable/Internet'),
    ('Maid Service'),
    ('Natural Gas'),
    ('Water and Sewer')
) AS subcategories(name);

-- Transportation subcategories
WITH parent AS (SELECT id FROM categories WHERE name = 'Transportation (Gas, Car, etc.)')
INSERT INTO categories (name, parent_id)
SELECT name, parent.id FROM parent, (VALUES
    ('Car Loan'),
    ('Car Insurance'),
    ('Car Registration'),
    ('Car Gas'),
    ('Public Transportation (E-Z Pass, etc.)')
) AS subcategories(name);

-- Entertainment subcategories
WITH parent AS (SELECT id FROM categories WHERE name = 'Entertainment')
INSERT INTO categories (name, parent_id)
SELECT name, parent.id FROM parent, (VALUES
    ('Subscriptions')
) AS subcategories(name);

-- Childcare subcategories
WITH parent AS (SELECT id FROM categories WHERE name = 'Childcare')
INSERT INTO categories (name, parent_id)
SELECT name, parent.id FROM parent, (VALUES
    ('Childcare/School Tuition')
) AS subcategories(name);

-- Food and Beverage subcategories
WITH parent AS (SELECT id FROM categories WHERE name = 'Food and Beverage')
INSERT INTO categories (name, parent_id)
SELECT name, parent.id FROM parent, (VALUES
    ('Eating Out'),
    ('Groceries'),
    ('Pet Food'),
    ('Costco')
) AS subcategories(name);

-- Healthcare subcategories
WITH parent AS (SELECT id FROM categories WHERE name = 'Healthcare')
INSERT INTO categories (name, parent_id)
SELECT name, parent.id FROM parent, (VALUES
    ('Pet Healthcare'),
    ('HSA/Dental (Nick)'),
    ('HSA (Sydney)')
) AS subcategories(name);

-- Personal Care subcategories
WITH parent AS (SELECT id FROM categories WHERE name = 'Personal Care (Charity, Misc, Other, etc.)')
INSERT INTO categories (name, parent_id)
SELECT name, parent.id FROM parent, (VALUES
    ('Beauty (Hair, Nails, etc.)'),
    ('Amazon'),
    ('Target')
) AS subcategories(name);

-- Savings and Insurance subcategories
WITH parent AS (SELECT id FROM categories WHERE name = 'Savings and Insurance (401k, IRA, etc.)')
INSERT INTO categories (name, parent_id)
SELECT name, parent.id FROM parent, (VALUES
    ('Life Insurance (Nick)'),
    ('Life Insurance (Sydney)'),
    ('Savings (House)'),
    ('Savings (Personal)'),
    ('Savings (529 Everett)'),
    ('Savings (529 Ava)'),
    ('Retirement (401k) (Nick)'),
    ('Retirement (401k) (Sydney)'),
    ('Retirement (IRA) (Nick)'),
    ('Retirement (IRA) (Sydney)'),
    ('Non-Retirement Account'),
    ('Employee Stock Purchase Plan')
) AS subcategories(name);

-- Miscellaneous subcategories
WITH parent AS (SELECT id FROM categories WHERE name = 'Miscellaneous')
INSERT INTO categories (name, parent_id)
SELECT name, parent.id FROM parent, (VALUES
    ('Other')
) AS subcategories(name);

-- Verify categories were created
SELECT COUNT(*) FROM categories;

-- Display the category hierarchy
WITH RECURSIVE category_tree AS (
  SELECT id, name, parent_id, 0 AS level, name AS path
  FROM categories
  WHERE parent_id IS NULL
  
  UNION ALL
  
  SELECT c.id, c.name, c.parent_id, ct.level + 1, ct.path || ' > ' || c.name
  FROM categories c
  JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT path, level
FROM category_tree
ORDER BY path; 