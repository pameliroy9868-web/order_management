-- db_scripts/create_orders.sql

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    courier_partner VARCHAR(50),
    company_name VARCHAR(255),
    tax_invoice_no VARCHAR(100),
    invoice_date DATE,
    order_date DATE,
    awb_number VARCHAR(50),
    order_id VARCHAR(50),
    sku_id VARCHAR(100),
    qty INT,
    hsn VARCHAR(20),
    gross_amount NUMERIC,
    discount NUMERIC,
    taxable_amount NUMERIC,
    total_other_charges NUMERIC,
    order_sequence INT DEFAULT 1,             -- sequence for tracking order lifecycle
    status VARCHAR(50) DEFAULT 'Pending',     -- current status
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Optional: enforce valid statuses from master_order_status
ALTER TABLE orders
ADD CONSTRAINT fk_status
FOREIGN KEY (status)
REFERENCES master_order_status(status_name);
