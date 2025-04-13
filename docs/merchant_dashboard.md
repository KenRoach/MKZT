# Merchant Dashboard Setup Guide

This guide will help you set up a basic merchant dashboard using Supabase UI for quick implementation.

## Prerequisites

- A Supabase account
- Access to your project's Supabase dashboard
- Basic knowledge of SQL and database management

## Setting Up the Supabase UI Dashboard

### 1. Access the Supabase Dashboard

1. Log in to your Supabase account at [https://app.supabase.io](https://app.supabase.io)
2. Select your project
3. Navigate to the "Table Editor" section

### 2. Create Database Views for the Dashboard

Create the following SQL views to make it easier to query data for the dashboard:

```sql
-- View for order summary
CREATE VIEW order_summary AS
SELECT 
  o.id,
  o.merchant_id,
  o.customer_id,
  o.status,
  o.total_amount,
  o.created_at,
  o.updated_at,
  c.name AS customer_name,
  c.phone AS customer_phone,
  c.email AS customer_email,
  d.name AS driver_name,
  d.phone AS driver_phone
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.id
LEFT JOIN drivers d ON o.driver_id = d.id;

-- View for order items
CREATE VIEW order_items_summary AS
SELECT 
  oi.id,
  oi.order_id,
  oi.item_name,
  oi.quantity,
  oi.unit_price,
  oi.special_instructions,
  o.merchant_id
FROM order_items oi
JOIN orders o ON oi.order_id = o.id;

-- View for merchant metrics
CREATE VIEW merchant_metrics AS
SELECT 
  merchant_id,
  COUNT(*) AS total_orders,
  SUM(total_amount) AS total_revenue,
  AVG(total_amount) AS avg_order_value,
  COUNT(CASE WHEN status IN ('completed', 'delivered') THEN 1 END) AS completed_orders,
  COUNT(CASE WHEN status = 'pending' THEN 1 END) AS pending_orders,
  COUNT(CASE WHEN status = 'preparing' THEN 1 END) AS preparing_orders,
  COUNT(CASE WHEN status = 'ready' THEN 1 END) AS ready_orders,
  COUNT(CASE WHEN status = 'cancelled' THEN 1 END) AS cancelled_orders
FROM orders
GROUP BY merchant_id;
```

### 3. Create a Dashboard in Supabase

1. Navigate to the "Dashboard" section in the Supabase UI
2. Click "Create Dashboard"
3. Name it "Merchant Dashboard"

### 4. Add Widgets to the Dashboard

Add the following widgets to your dashboard:

#### Orders Table

1. Click "Add Widget"
2. Select "Table"
3. Configure the query:
   ```sql
   SELECT * FROM order_summary WHERE merchant_id = '{{merchant_id}}' ORDER BY created_at DESC LIMIT 50
   ```
4. Set the title to "Recent Orders"

#### Order Status Chart

1. Click "Add Widget"
2. Select "Chart" (Bar chart)
3. Configure the query:
   ```sql
   SELECT status, COUNT(*) FROM orders WHERE merchant_id = '{{merchant_id}}' GROUP BY status
   ```
4. Set the title to "Orders by Status"

#### Revenue Chart

1. Click "Add Widget"
2. Select "Chart" (Line chart)
3. Configure the query:
   ```sql
   SELECT DATE_TRUNC('day', created_at) AS date, SUM(total_amount) AS revenue 
   FROM orders 
   WHERE merchant_id = '{{merchant_id}}' AND created_at >= NOW() - INTERVAL '30 days'
   GROUP BY date
   ORDER BY date
   ```
4. Set the title to "Revenue (Last 30 Days)"

#### Popular Items

1. Click "Add Widget"
2. Select "Table"
3. Configure the query:
   ```sql
   SELECT item_name, SUM(quantity) AS total_quantity 
   FROM order_items_summary 
   WHERE merchant_id = '{{merchant_id}}' AND created_at >= NOW() - INTERVAL '30 days'
   GROUP BY item_name 
   ORDER BY total_quantity DESC 
   LIMIT 10
   ```
4. Set the title to "Popular Items"

### 5. Create a Filter for Merchant ID

1. Click "Add Filter"
2. Select "Text" as the filter type
3. Set the name to "merchant_id"
4. Set the default value to your test merchant ID

## Using the Dashboard

1. Access the dashboard through the Supabase UI
2. Use the merchant_id filter to view data for a specific merchant
3. View orders, metrics, and popular items
4. Click on an order to view details

## Next Steps

For a more advanced dashboard, consider:

1. Building a custom React application using the API endpoints we've created
2. Adding more interactive features like order status updates
3. Implementing real-time updates using Supabase's real-time subscriptions
4. Adding more advanced analytics and reporting

## API Endpoints

The following API endpoints are available for building a custom dashboard:

- `GET /merchant/dashboard/orders` - Get orders for the current merchant
- `GET /merchant/dashboard/orders/{order_id}` - Get detailed information about a specific order
- `PUT /merchant/dashboard/orders/{order_id}/status` - Update the status of an order
- `GET /merchant/dashboard/metrics` - Get performance metrics for the merchant
- `GET /merchant/dashboard/popular-items` - Get popular items for the merchant 