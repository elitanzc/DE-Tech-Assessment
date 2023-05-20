-- CREATE MEMBERS TABLE
DROP TABLE IF EXISTS members;
CREATE TABLE members (
    membership_id VARCHAR PRIMARY KEY,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    mobile_no VARCHAR(8) NOT NULL,
    date_of_birth VARCHAR(8) NOT NULL
);

-- CREATE ITEMS TABLE
DROP TABLE IF EXISTS items;
CREATE TABLE items (
    item_name VARCHAR PRIMARY KEY,
    manufacturer_name VARCHAR NOT NULL,
    cost NUMERIC(10,2) NOT NULL,
    weight NUMERIC(10,2) NOT NULL
);

-- CREATE TRANSACTIONS TABLE
DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    membership_id VARCHAR REFERENCES members,
    total_price NUMERIC(10,2) NOT NULL,
    total_weight NUMERIC(10,2) NOT NULL
);

-- CREATE ORDERS TABLE
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
    transaction_id INTEGER REFERENCES transactions,
    item_name VARCHAR REFERENCES items,
    quantity INTEGER NOT NULL
);