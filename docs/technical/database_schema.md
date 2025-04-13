# Database Schema Documentation

## Overview
The system uses PostgreSQL via Supabase for data storage, with real-time capabilities and row-level security.

## Core Tables

### Users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50) UNIQUE,
    full_name VARCHAR(255),
    role user_role NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE user_role AS ENUM ('customer', 'merchant', 'driver', 'admin');
```

### Orders
```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES users(id),
    merchant_id UUID REFERENCES merchants(id),
    driver_id UUID REFERENCES users(id),
    status order_status NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    special_instructions TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE order_status AS ENUM (
    'pending', 'confirmed', 'preparing', 
    'ready', 'picked_up', 'delivered', 'cancelled'
);
```

### Order Items
```sql
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id),
    product_id UUID REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    special_instructions TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Merchants
```sql
CREATE TABLE merchants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    business_name VARCHAR(255) NOT NULL,
    business_type merchant_type NOT NULL,
    status merchant_status NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE merchant_status AS ENUM ('active', 'inactive', 'suspended');
CREATE TYPE merchant_type AS ENUM ('restaurant', 'grocery', 'pharmacy');
```

### Products
```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_id UUID REFERENCES merchants(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category_id UUID REFERENCES categories(id),
    status product_status NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE product_status AS ENUM ('available', 'out_of_stock', 'discontinued');
```

### Deliveries
```sql
CREATE TABLE deliveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id),
    driver_id UUID REFERENCES users(id),
    status delivery_status NOT NULL,
    pickup_location JSONB NOT NULL,
    dropoff_location JSONB NOT NULL,
    estimated_delivery_time TIMESTAMP WITH TIME ZONE,
    actual_delivery_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE delivery_status AS ENUM (
    'assigned', 'en_route_to_merchant', 'at_merchant',
    'picked_up', 'en_route_to_customer', 'delivered'
);
```

## Analytics Tables

### Order Analytics
```sql
CREATE TABLE order_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id),
    preparation_time INTERVAL,
    delivery_time INTERVAL,
    customer_rating SMALLINT,
    driver_rating SMALLINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Driver Analytics
```sql
CREATE TABLE driver_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    driver_id UUID REFERENCES users(id),
    date DATE NOT NULL,
    orders_completed INTEGER DEFAULT 0,
    total_earnings DECIMAL(10,2) DEFAULT 0,
    online_hours INTERVAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Indexes
```sql
-- Orders
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_merchant_id ON orders(merchant_id);
CREATE INDEX idx_orders_driver_id ON orders(driver_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- Products
CREATE INDEX idx_products_merchant_id ON products(merchant_id);
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_status ON products(status);

-- Deliveries
CREATE INDEX idx_deliveries_order_id ON deliveries(order_id);
CREATE INDEX idx_deliveries_driver_id ON deliveries(driver_id);
CREATE INDEX idx_deliveries_status ON deliveries(status);
```

## Row Level Security (RLS)
```sql
-- Users table policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own data"
    ON users FOR SELECT
    USING (auth.uid() = id);

-- Orders table policies
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Customers can view their orders"
    ON orders FOR SELECT
    USING (auth.uid() = customer_id);

CREATE POLICY "Merchants can view their orders"
    ON orders FOR SELECT
    USING (auth.uid() IN (
        SELECT user_id FROM merchants WHERE id = merchant_id
    ));
```

## Triggers
```sql
-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Order status change notification trigger
CREATE OR REPLACE FUNCTION notify_order_status_change()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify(
        'order_status_change',
        json_build_object(
            'order_id', NEW.id,
            'status', NEW.status
        )::text
    );
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER order_status_change_trigger
    AFTER UPDATE OF status ON orders
    FOR EACH ROW
    EXECUTE FUNCTION notify_order_status_change();
```

## Backup and Recovery
- Daily full backups
- Point-in-time recovery enabled
- 30-day retention period
- Automated backup testing

## Performance Considerations
- Partitioning for large tables
- Regular vacuum and analyze
- Index maintenance
- Query optimization

## Security Measures
- Encryption at rest
- Column-level encryption for sensitive data
- Audit logging
- Access control policies 