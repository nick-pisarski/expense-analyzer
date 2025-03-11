-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify it's installed
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Note: Configuration parameters like vector.dim_limit and vector.hnsw_ef_search
-- are not supported in this version of pgvector (0.5.1)

-- Create a test table to verify functionality with 1536 dimensions
CREATE TABLE IF NOT EXISTS vector_test (
  id SERIAL PRIMARY KEY,
  embedding VECTOR(1536)
);

-- Insert a test vector to verify functionality
-- Create a vector with 1536 zeros (simplified for demonstration)
DO $$
DECLARE
  test_vector VECTOR(1536);
BEGIN
  -- Initialize vector with zeros
  test_vector := ARRAY(SELECT 0.0 FROM generate_series(1, 1536))::vector;
  
  -- Insert the test vector
  INSERT INTO vector_test (embedding) VALUES (test_vector);
END $$;

-- Verify the test table was created
SELECT * FROM vector_test LIMIT 1;
