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
                -- Select random item name and description
                SELECT 
                    (ARRAY['Pizza', 'Burger', 'Salad', 'Pasta', 'Sandwich', 'Soup', 'Dessert', 'Drink'])[FLOOR(RANDOM() * 8 + 1)] INTO item_name;
                
                -- Generate description based on item name
                special_instructions := CASE item_name
                    WHEN 'Pizza' THEN 'Freshly baked pizza with your choice of toppings'
                    WHEN 'Burger' THEN 'Juicy beef patty with fresh vegetables and special sauce'
                    WHEN 'Salad' THEN 'Fresh mixed greens with seasonal vegetables'
                    WHEN 'Pasta' THEN 'Al dente pasta with homemade sauce'
                    WHEN 'Sandwich' THEN 'Fresh bread with premium fillings'
                    WHEN 'Soup' THEN 'Homemade soup made with fresh ingredients'
                    WHEN 'Dessert' THEN 'Sweet treat made in-house'
                    WHEN 'Drink' THEN 'Refreshing beverage of your choice'
                END;
                
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
                    order_id, item_name, quantity, unit_price, description, special_instructions
                )
                VALUES (
                    order_id, item_name, quantity, unit_price, description, special_instructions
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

-- Create sample products for each merchant
DO $$
DECLARE
    merchant_record RECORD;
    product_id UUID;
    category VARCHAR(100);
    base_price DECIMAL(10,2);
    product_name VARCHAR(255);
    product_description TEXT;
BEGIN
    FOR merchant_record IN SELECT id, business_type FROM merchants LOOP
        -- Create 5-10 products for each merchant
        FOR i IN 1..FLOOR(RANDOM() * 6 + 5) LOOP
            -- Select random category and price based on business type
            CASE merchant_record.business_type
                WHEN 'Restaurant' THEN
                    category := (ARRAY['Appetizers', 'Main Courses', 'Desserts', 'Beverages'])[FLOOR(RANDOM() * 4 + 1)];
                    base_price := CASE category
                        WHEN 'Appetizers' THEN (RANDOM() * 10 + 5)::DECIMAL(10,2)
                        WHEN 'Main Courses' THEN (RANDOM() * 20 + 10)::DECIMAL(10,2)
                        WHEN 'Desserts' THEN (RANDOM() * 8 + 3)::DECIMAL(10,2)
                        WHEN 'Beverages' THEN (RANDOM() * 5 + 2)::DECIMAL(10,2)
                    END;
                WHEN 'Cafe' THEN
                    category := (ARRAY['Coffee', 'Tea', 'Pastries', 'Snacks'])[FLOOR(RANDOM() * 4 + 1)];
                    base_price := CASE category
                        WHEN 'Coffee' THEN (RANDOM() * 6 + 3)::DECIMAL(10,2)
                        WHEN 'Tea' THEN (RANDOM() * 5 + 2)::DECIMAL(10,2)
                        WHEN 'Pastries' THEN (RANDOM() * 7 + 4)::DECIMAL(10,2)
                        WHEN 'Snacks' THEN (RANDOM() * 8 + 3)::DECIMAL(10,2)
                    END;
                WHEN 'Bakery' THEN
                    category := (ARRAY['Bread', 'Pastries', 'Cakes', 'Cookies'])[FLOOR(RANDOM() * 4 + 1)];
                    base_price := CASE category
                        WHEN 'Bread' THEN (RANDOM() * 8 + 4)::DECIMAL(10,2)
                        WHEN 'Pastries' THEN (RANDOM() * 7 + 3)::DECIMAL(10,2)
                        WHEN 'Cakes' THEN (RANDOM() * 30 + 20)::DECIMAL(10,2)
                        WHEN 'Cookies' THEN (RANDOM() * 5 + 2)::DECIMAL(10,2)
                    END;
                ELSE
                    category := 'General';
                    base_price := (RANDOM() * 15 + 5)::DECIMAL(10,2);
            END CASE;

            -- Generate product name and description
            product_name := category || ' Item ' || i;
            product_description := 'Delicious ' || LOWER(category) || ' from ' || merchant_record.business_type;

            -- Insert product
            INSERT INTO products (
                merchant_id, name, description, base_price, category
            ) VALUES (
                merchant_record.id, product_name, product_description, base_price, category
            ) RETURNING id INTO product_id;

            -- Create variants if applicable
            IF category IN ('Coffee', 'Tea', 'Beverages') THEN
                -- Size variants
                INSERT INTO product_variants (product_id, name, price)
                VALUES 
                    (product_id, 'Small', base_price),
                    (product_id, 'Medium', base_price * 1.3),
                    (product_id, 'Large', base_price * 1.6);
            ELSIF category IN ('Cakes', 'Pastries') THEN
                -- Portion variants
                INSERT INTO product_variants (product_id, name, price)
                VALUES 
                    (product_id, 'Single', base_price),
                    (product_id, 'Family', base_price * 2.5);
            END IF;
        END LOOP;
    END LOOP;
END $$;

-- Update order items to reference products
UPDATE order_items oi
SET product_id = p.id,
    variant_id = pv.id
FROM products p
LEFT JOIN product_variants pv ON pv.product_id = p.id
WHERE oi.item_name = p.name
AND (pv.name = 'Medium' OR pv.id IS NULL)
LIMIT 1000; 