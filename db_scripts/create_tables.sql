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


SELECT
order_id,
awb_number,
'Ordered' as status,
order_date as event_date , *
FROM orders
WHERE order_id ILIKE '%193098461679219712_1%' OR awb_number ILIKE '%193098461679219712_1%'
UNION ALL
SELECT
suborder_number as order_id,
awb_number,
return_status as status,
return_created_date as event_date, *
FROM meesho_returns
WHERE suborder_number ILIKE '%193098461679219712_1%' OR awb_number ILIKE '%193098461679219712_1%'
ORDER BY COALESCE(event_date, '1900-01-01') ASC


SELECT * FROM (

    SELECT
        order_id,
        awb_number,
        'Ordered' as status,
        order_date as event_date
    FROM orders
    WHERE order_id ILIKE '%193098461679219712_1%' OR awb_number ILIKE '%193098461679219712_1%'

    UNION ALL

    SELECT
        suborder_number as order_id,
        awb_number,
        return_status as status,
        return_created_date as event_date
    FROM meesho_returns
    WHERE suborder_number ILIKE '%193098461679219712_1%' OR awb_number ILIKE '%193098461679219712_1%'
    ) AS combined
    ORDER BY COALESCE(event_date, '1900-01-01') ASC
