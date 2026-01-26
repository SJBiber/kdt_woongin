-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Products Table
CREATE TABLE IF NOT EXISTS zigzag_products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_major TEXT NOT NULL,
    brand_name TEXT,
    product_name TEXT NOT NULL,
    final_price INTEGER,
    review_count INTEGER DEFAULT 0,
    rating_average FLOAT DEFAULT 0.0,
    image_url TEXT,
    product_url TEXT UNIQUE NOT NULL,
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Reviews Table
CREATE TABLE IF NOT EXISTS zigzag_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES zigzag_products(id) ON DELETE CASCADE,
    content TEXT,
    rating INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexing for performance
CREATE INDEX IF NOT EXISTS idx_products_category ON zigzag_products(category_major);
CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON zigzag_reviews(product_id);
