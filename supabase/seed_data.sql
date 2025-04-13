-- Seed data for CRM database
-- This script will create 150 dummy entries across all tables

-- Function to generate random data
CREATE OR REPLACE FUNCTION generate_random_data() RETURNS void AS $$
DECLARE
    i INTEGER;
    customer_id UUID;
    merchant_id UUID;
    driver_id UUID;
    order_id UUID;
    order_status order_status;
    payment_status payment_status;
    driver_status driver_status;
    total_amount DECIMAL(10,2);
    item_count INTEGER;
    item_name VARCHAR(255);
    quantity INTEGER;
    unit_price DECIMAL(10,2);
    special_instructions TEXT;
    notification_type VARCHAR(50);
    notification_channel VARCHAR(50);
    notification_status VARCHAR(50);
BEGIN
    -- Create 50 customers
    FOR i IN 1..50 LOOP
        INSERT INTO customers (name, email, phone, address)
        VALUES (
            'Customer ' || i,
            'customer' || i || '@example.com',
            '+1' || LPAD(FLOOR(RANDOM() * 9000000000 + 1000000000)::TEXT, 10, '0'),
            'Address ' || i || ', City ' || (i % 10 + 1) || ', Country'
        )
        RETURNING id INTO customer_id;
        
        -- Create 1-3 orders for each customer
        FOR j IN 1..(FLOOR(RANDOM() * 3 + 1)) LOOP
            -- Select random merchant
            SELECT id INTO merchant_id FROM merchants ORDER BY RANDOM() LIMIT 1;
            
            -- Select random driver
            SELECT id INTO driver_id FROM drivers ORDER BY RANDOM() LIMIT 1;
            
            -- Select random statuses
            SELECT (ARRAY['pending', 'confirmed', 'preparing', 'ready_for_pickup', 'picked_up', 'delivered', 'cancelled'])[FLOOR(RANDOM() * 7 + 1)]::order_status INTO order_status;
            SELECT (ARRAY['pending', 'paid', 'failed', 'refunded'])[FLOOR(RANDOM() * 4 + 1)]::payment_status INTO payment_status;
            
            -- Calculate random total amount
            total_amount := (RANDOM() * 200 + 10)::DECIMAL(10,2);
            
            -- Create order
            INSERT INTO orders (
                customer_id, merchant_id, driver_id, status, total_amount, 
                payment_status, delivery_address, estimated_delivery_time
            )
            VALUES (
                customer_id, merchant_id, driver_id, order_status, total_amount,
                payment_status, 'Delivery Address ' || i || '-' || j, 
                CURRENT_TIMESTAMP + (RANDOM() * 24 * 60 * 60)::INTEGER * INTERVAL '1 second'
            )
            RETURNING id INTO order_id;
            
            -- Create 1-5 items for each order
            item_count := FLOOR(RANDOM() * 5 + 1);
            FOR k IN 1..item_count LOOP
                -- Select random item name
                SELECT (ARRAY['Pizza', 'Burger', 'Salad', 'Pasta', 'Sandwich', 'Soup', 'Dessert', 'Drink'])[FLOOR(RANDOM() * 8 + 1)] INTO item_name;
                
                -- Calculate random quantity and unit price
                quantity := FLOOR(RANDOM() * 3 + 1);
                unit_price := (RANDOM() * 20 + 5)::DECIMAL(10,2);
                
                -- Random special instructions
                IF RANDOM() > 0.7 THEN
                    special_instructions := 'Special instructions for ' || item_name;
                ELSE
                    special_instructions := NULL;
                END IF;
                
                -- Create order item
                INSERT INTO order_items (
                    order_id, item_name, quantity, unit_price, special_instructions
                )
                VALUES (
                    order_id, item_name, quantity, unit_price, special_instructions
                );
            END LOOP;
            
            -- Create 1-3 notifications for each order
            FOR l IN 1..(FLOOR(RANDOM() * 3 + 1)) LOOP
                -- Select random notification type and channel
                SELECT (ARRAY['order_confirmation', 'order_update', 'delivery_update', 'payment_receipt'])[FLOOR(RANDOM() * 4 + 1)] INTO notification_type;
                SELECT (ARRAY['email', 'sms', 'whatsapp', 'push'])[FLOOR(RANDOM() * 4 + 1)] INTO notification_channel;
                SELECT (ARRAY['pending', 'sent', 'failed'])[FLOOR(RANDOM() * 3 + 1)] INTO notification_status;
                
                -- Create notification
                INSERT INTO notifications (
                    customer_id, type, message, channel, status, sent_at
                )
                VALUES (
                    customer_id, notification_type, 
                    'Notification about ' || notification_type || ' for order ' || order_id,
                    notification_channel, notification_status,
                    CASE WHEN notification_status = 'sent' THEN CURRENT_TIMESTAMP ELSE NULL END
                );
            END LOOP;
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Create 20 merchants
INSERT INTO merchants (name, email, phone, address, business_type)
SELECT 
    'Merchant ' || i,
    'merchant' || i || '@example.com',
    '+1' || LPAD(FLOOR(RANDOM() * 9000000000 + 1000000000)::TEXT, 10, '0'),
    'Business Address ' || i || ', City ' || (i % 5 + 1) || ', Country',
    (ARRAY['Restaurant', 'Cafe', 'Bakery', 'Grocery', 'Pharmacy'])[FLOOR(RANDOM() * 5 + 1)]
FROM generate_series(1, 20) AS i;

-- Create 30 drivers
INSERT INTO drivers (name, email, phone, status, current_location)
SELECT 
    'Driver ' || i,
    'driver' || i || '@example.com',
    '+1' || LPAD(FLOOR(RANDOM() * 9000000000 + 1000000000)::TEXT, 10, '0'),
    (ARRAY['available', 'busy', 'offline'])[FLOOR(RANDOM() * 3 + 1)]::driver_status,
    point(
        (RANDOM() * 180 - 90)::DECIMAL(10,6),
        (RANDOM() * 360 - 180)::DECIMAL(10,6)
    )
FROM generate_series(1, 30) AS i;

-- Generate random data for customers, orders, items, and notifications
SELECT generate_random_data();

-- Drop the temporary function
DROP FUNCTION generate_random_data(); 