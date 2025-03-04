CREATE TABLE bot_v2.dealers_info (
    dealer_id INT PRIMARY KEY,
    dealer_name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(50) NOT NULL,
    credit_app_link TEXT NOT NULL,
    inventory_link TEXT NOT NULL,
    offers_test_drive BOOLEAN NOT NULL DEFAULT 0,
    welcome_message TEXT NOT NULL,
    shipping BOOLEAN NOT NULL DEFAULT 0,
    trade_ins BOOLEAN NOT NULL DEFAULT 0,
    opening_hours TEXT NOT NULL,
    offer_finance BOOLEAN NOT NULL DEFAULT 0,
    financing_type VARCHAR(255) NOT NULL,
    bot_behavior TEXT NOT NULL
);
