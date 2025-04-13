-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
CREATE TYPE order_status AS ENUM ('pending', 'confirmed', 'preparing', 'ready_for_pickup', 'picked_up', 'delivered', 'cancelled');
CREATE TYPE payment_status AS ENUM ('pending', 'paid', 'failed', 'refunded');
CREATE TYPE driver_status AS ENUM ('available', 'busy', 'offline');

-- Create customers table
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50) UNIQUE,
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create merchants table
CREATE TABLE merchants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50) UNIQUE,
    address TEXT,
    business_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create drivers table
CREATE TABLE drivers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50) UNIQUE,
    status driver_status DEFAULT 'offline',
    current_location POINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id),
    merchant_id UUID REFERENCES merchants(id),
    driver_id UUID REFERENCES drivers(id),
    status order_status DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL,
    payment_status payment_status DEFAULT 'pending',
    delivery_address TEXT,
    estimated_delivery_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create order_items table
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id),
    item_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    description TEXT,
    special_instructions TEXT,
    product_id UUID REFERENCES products(id),
    variant_id UUID REFERENCES product_variants(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create notifications table
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id),
    type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    channel VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create products table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_id UUID REFERENCES merchants(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    base_price DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create product_variants table for different sizes/prices
CREATE TABLE product_variants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id),
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create customer_preferences table
CREATE TABLE customer_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id),
    dietary_restrictions TEXT[],
    favorite_items UUID[],
    preferred_payment_method VARCHAR(50),
    preferred_delivery_time TIME,
    notification_preferences JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create order_preferences table
CREATE TABLE order_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id),
    delivery_instructions TEXT,
    packaging_preferences TEXT,
    gift_message TEXT,
    special_requests TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create order_feedback table
CREATE TABLE order_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id),
    customer_id UUID REFERENCES customers(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    food_quality_rating INTEGER CHECK (food_quality_rating >= 1 AND food_quality_rating <= 5),
    delivery_rating INTEGER CHECK (delivery_rating >= 1 AND delivery_rating <= 5),
    service_rating INTEGER CHECK (service_rating >= 1 AND service_rating <= 5),
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create order_tracking table
CREATE TABLE order_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id),
    status order_status,
    location POINT,
    estimated_arrival_time TIMESTAMP WITH TIME ZONE,
    actual_arrival_time TIMESTAMP WITH TIME ZONE,
    driver_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create order_payment_details table
CREATE TABLE order_payment_details (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id),
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255),
    amount DECIMAL(10,2),
    currency VARCHAR(3),
    payment_status payment_status,
    refund_amount DECIMAL(10,2),
    refund_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create suppliers table
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_id UUID REFERENCES merchants(id),
    name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    payment_terms VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create inventory_items table
CREATE TABLE inventory_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_id UUID REFERENCES merchants(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    unit_of_measure VARCHAR(50),
    reorder_level INTEGER,
    reorder_quantity INTEGER,
    supplier_id UUID REFERENCES suppliers(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create inventory_stock table
CREATE TABLE inventory_stock (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inventory_item_id UUID REFERENCES inventory_items(id),
    quantity INTEGER NOT NULL,
    location VARCHAR(100),
    batch_number VARCHAR(100),
    expiry_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create inventory_transactions table
CREATE TABLE inventory_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inventory_item_id UUID REFERENCES inventory_items(id),
    transaction_type VARCHAR(50), -- 'purchase', 'sale', 'adjustment', 'transfer'
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2),
    supplier_id UUID REFERENCES suppliers(id),
    reference_number VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create product_inventory table (linking products to inventory items)
CREATE TABLE product_inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id),
    inventory_item_id UUID REFERENCES inventory_items(id),
    quantity_required DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create inventory_alerts table
CREATE TABLE inventory_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_id UUID REFERENCES merchants(id),
    inventory_item_id UUID REFERENCES inventory_items(id),
    alert_type VARCHAR(50), -- 'low_stock', 'expiry', 'reorder'
    message TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Create RLS policies
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE merchants ENABLE ROW LEVEL SECURITY;
ALTER TABLE drivers ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_variants ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_payment_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_stock ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE product_inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_alerts ENABLE ROW LEVEL SECURITY;

-- Create policies for customers
CREATE POLICY "Customers can view their own data"
    ON customers FOR SELECT
    USING (auth.uid() = id);

-- Create policies for merchants
CREATE POLICY "Merchants can view their own data"
    ON merchants FOR SELECT
    USING (auth.uid() = id);

-- Create policies for orders
CREATE POLICY "Customers can view their own orders"
    ON orders FOR SELECT
    USING (customer_id = auth.uid());

CREATE POLICY "Merchants can view their own orders"
    ON orders FOR SELECT
    USING (merchant_id = auth.uid());

CREATE POLICY "Drivers can view assigned orders"
    ON orders FOR SELECT
    USING (driver_id = auth.uid());

-- Create policies for products
CREATE POLICY "Merchants can manage their own products"
    ON products FOR ALL
    USING (auth.uid() = merchant_id);

CREATE POLICY "Anyone can view available products"
    ON products FOR SELECT
    USING (is_available = true);

-- Create policies for product variants
CREATE POLICY "Merchants can manage their product variants"
    ON product_variants FOR ALL
    USING (EXISTS (
        SELECT 1 FROM products 
        WHERE products.id = product_variants.product_id 
        AND products.merchant_id = auth.uid()
    ));

CREATE POLICY "Anyone can view available product variants"
    ON product_variants FOR SELECT
    USING (is_available = true);

-- Create policies for customer preferences
CREATE POLICY "Customers can manage their own preferences"
    ON customer_preferences FOR ALL
    USING (customer_id = auth.uid());

-- Create policies for order preferences
CREATE POLICY "Customers can view their order preferences"
    ON order_preferences FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM orders 
        WHERE orders.id = order_preferences.order_id 
        AND orders.customer_id = auth.uid()
    ));

-- Create policies for order feedback
CREATE POLICY "Customers can manage their order feedback"
    ON order_feedback FOR ALL
    USING (customer_id = auth.uid());

-- Create policies for order tracking
CREATE POLICY "Customers can view their order tracking"
    ON order_tracking FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM orders 
        WHERE orders.id = order_tracking.order_id 
        AND orders.customer_id = auth.uid()
    ));

-- Create policies for order payment details
CREATE POLICY "Customers can view their payment details"
    ON order_payment_details FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM orders 
        WHERE orders.id = order_payment_details.order_id 
        AND orders.customer_id = auth.uid()
    ));

-- Create policies for suppliers
CREATE POLICY "Merchants can manage their suppliers"
    ON suppliers FOR ALL
    USING (merchant_id = auth.uid());

-- Create policies for inventory items
CREATE POLICY "Merchants can manage their inventory items"
    ON inventory_items FOR ALL
    USING (merchant_id = auth.uid());

-- Create policies for inventory stock
CREATE POLICY "Merchants can manage their inventory stock"
    ON inventory_stock FOR ALL
    USING (EXISTS (
        SELECT 1 FROM inventory_items 
        WHERE inventory_items.id = inventory_stock.inventory_item_id 
        AND inventory_items.merchant_id = auth.uid()
    ));

-- Create policies for inventory transactions
CREATE POLICY "Merchants can manage their inventory transactions"
    ON inventory_transactions FOR ALL
    USING (EXISTS (
        SELECT 1 FROM inventory_items 
        WHERE inventory_items.id = inventory_transactions.inventory_item_id 
        AND inventory_items.merchant_id = auth.uid()
    ));

-- Create policies for product inventory
CREATE POLICY "Merchants can manage their product inventory"
    ON product_inventory FOR ALL
    USING (EXISTS (
        SELECT 1 FROM products 
        WHERE products.id = product_inventory.product_id 
        AND products.merchant_id = auth.uid()
    ));

-- Create policies for inventory alerts
CREATE POLICY "Merchants can manage their inventory alerts"
    ON inventory_alerts FOR ALL
    USING (merchant_id = auth.uid());

-- Create functions for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updating timestamps
CREATE TRIGGER update_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_merchants_updated_at
    BEFORE UPDATE ON merchants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_drivers_updated_at
    BEFORE UPDATE ON drivers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customer_preferences_updated_at
    BEFORE UPDATE ON customer_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_order_payment_details_updated_at
    BEFORE UPDATE ON order_payment_details
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_suppliers_updated_at
    BEFORE UPDATE ON suppliers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inventory_items_updated_at
    BEFORE UPDATE ON inventory_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inventory_stock_updated_at
    BEFORE UPDATE ON inventory_stock
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_product_inventory_updated_at
    BEFORE UPDATE ON product_inventory
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create indexes for products
CREATE INDEX idx_products_merchant_id ON products(merchant_id);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_product_variants_product_id ON product_variants(product_id);

-- Create indexes for customer preferences
CREATE INDEX idx_customer_preferences_customer_id ON customer_preferences(customer_id);

-- Create indexes for order preferences
CREATE INDEX idx_order_preferences_order_id ON order_preferences(order_id);

-- Create indexes for order feedback
CREATE INDEX idx_order_feedback_order_id ON order_feedback(order_id);
CREATE INDEX idx_order_feedback_customer_id ON order_feedback(customer_id);

-- Create indexes for order tracking
CREATE INDEX idx_order_tracking_order_id ON order_tracking(order_id);

-- Create indexes for order payment details
CREATE INDEX idx_order_payment_details_order_id ON order_payment_details(order_id);

-- Create indexes for inventory management
CREATE INDEX idx_suppliers_merchant_id ON suppliers(merchant_id);
CREATE INDEX idx_inventory_items_merchant_id ON inventory_items(merchant_id);
CREATE INDEX idx_inventory_items_category ON inventory_items(category);
CREATE INDEX idx_inventory_stock_item_id ON inventory_stock(inventory_item_id);
CREATE INDEX idx_inventory_transactions_item_id ON inventory_transactions(inventory_item_id);
CREATE INDEX idx_product_inventory_product_id ON product_inventory(product_id);
CREATE INDEX idx_product_inventory_item_id ON product_inventory(inventory_item_id);
CREATE INDEX idx_inventory_alerts_merchant_id ON inventory_alerts(merchant_id);
CREATE INDEX idx_inventory_alerts_item_id ON inventory_alerts(inventory_item_id);

-- Create function to check low stock
CREATE OR REPLACE FUNCTION check_low_stock()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.quantity <= (
        SELECT reorder_level 
        FROM inventory_items 
        WHERE id = NEW.inventory_item_id
    ) THEN
        INSERT INTO inventory_alerts (
            merchant_id,
            inventory_item_id,
            alert_type,
            message
        )
        SELECT 
            i.merchant_id,
            i.id,
            'low_stock',
            'Low stock alert for ' || i.name
        FROM inventory_items i
        WHERE i.id = NEW.inventory_item_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for low stock alerts
CREATE TRIGGER trigger_low_stock_alert
    AFTER UPDATE ON inventory_stock
    FOR EACH ROW
    EXECUTE FUNCTION check_low_stock(); 