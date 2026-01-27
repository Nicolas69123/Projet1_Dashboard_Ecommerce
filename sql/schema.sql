-- Table faits
CREATE TABLE fact_sales (
    invoice_no VARCHAR,
    stock_code VARCHAR,
    quantity INTEGER,
    invoice_date TIMESTAMP,
    customer_id DOUBLE,
    total_amount DOUBLE
);

-- Dimension produits
CREATE TABLE dim_products (
    stock_code VARCHAR PRIMARY KEY,
    description VARCHAR,
    unit_price DOUBLE
);

-- Dimension clients
CREATE TABLE dim_customers (
    customer_id DOUBLE PRIMARY KEY,
    country VARCHAR,
    is_identified BOOLEAN
);

-- Dimension temps
CREATE TABLE dim_date (
    date DATE PRIMARY KEY,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    month_name VARCHAR
);
