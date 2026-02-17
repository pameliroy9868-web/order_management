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


CREATE TABLE claims (

    id SERIAL PRIMARY KEY,

    suborder_number TEXT,
    order_number TEXT,

    ticket_id TEXT UNIQUE,

    ticket_status TEXT,

    created_date TIMESTAMP,

    issue TEXT,

    product_name TEXT,
    sku TEXT,
    variation TEXT,

    qty INTEGER,

    meesho_pid TEXT,

    last_update TEXT,
    reopen_validity TEXT,
    cpp_flag TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);