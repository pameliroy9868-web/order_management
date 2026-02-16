CREATE TABLE meesho_returns (

    id SERIAL PRIMARY KEY,

    suborder_number TEXT UNIQUE,

    sku TEXT,

    product_name TEXT,

    courier_partner TEXT,

    awb_number TEXT,

    return_status TEXT,

    return_reason TEXT,

    detailed_return_reason TEXT,

    return_created_date DATE,

    qty INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);
