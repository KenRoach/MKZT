# Sequence Diagrams

## Order Processing Flow

```mermaid
sequenceDiagram
    participant C as Customer
    participant W as WhatsApp/Web
    participant A as API Gateway
    participant O as Order Service
    participant M as Merchant
    participant D as Driver
    participant N as Notification Service

    C->>W: Place Order
    W->>A: POST /orders
    A->>O: Create Order
    O->>M: Notify New Order
    M->>O: Accept Order
    O->>D: Find Available Driver
    D->>O: Accept Delivery
    O->>N: Send Notifications
    N->>C: Order Confirmed
    N->>M: Order Assigned
    N->>D: Delivery Details
```

## Payment Processing Flow

```mermaid
sequenceDiagram
    participant C as Customer
    participant A as API Gateway
    participant P as Payment Service
    participant G as Payment Gateway
    participant O as Order Service
    participant N as Notification Service

    C->>A: Initiate Payment
    A->>P: Process Payment
    P->>G: Payment Request
    G->>P: Payment Response
    P->>O: Update Order Status
    O->>N: Send Confirmation
    N->>C: Payment Receipt
```

## Driver Assignment Flow

```mermaid
sequenceDiagram
    participant O as Order Service
    participant AI as AI Service
    participant D as Driver Pool
    participant DS as Driver Service
    participant N as Notification Service

    O->>AI: Request Driver Assignment
    AI->>D: Find Optimal Driver
    D->>DS: Check Driver Status
    DS->>AI: Driver Availability
    AI->>O: Driver Assignment
    O->>N: Notify Assignment
    N->>D: Delivery Request
```

## Real-time Order Tracking

```mermaid
sequenceDiagram
    participant C as Customer
    participant W as WebSocket
    participant D as Driver App
    participant L as Location Service
    participant N as Notification Service

    D->>L: Update Location
    L->>W: Broadcast Update
    W->>C: Location Update
    D->>L: Status Change
    L->>N: Trigger Notification
    N->>C: Status Update
```

## Merchant Order Management

```mermaid
sequenceDiagram
    participant M as Merchant
    participant A as API Gateway
    participant O as Order Service
    participant K as Kitchen Display
    participant N as Notification Service

    M->>A: View Orders
    A->>O: Get Orders
    O->>M: Active Orders
    M->>O: Update Status
    O->>K: Update Display
    O->>N: Notify Customer
```

## AI Prediction Flow

```mermaid
sequenceDiagram
    participant S as Scheduler
    participant AI as AI Service
    participant D as Data Lake
    participant M as ML Models
    participant C as Cache

    S->>AI: Trigger Prediction
    AI->>D: Fetch Historical Data
    D->>AI: Raw Data
    AI->>M: Process Data
    M->>AI: Predictions
    AI->>C: Cache Results
```

## Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant A as Auth Service
    participant T as Token Service
    participant R as Role Service
    participant S as Session Store

    U->>A: Login Request
    A->>T: Generate Tokens
    T->>R: Get User Roles
    R->>T: Role Permissions
    T->>S: Store Session
    S->>A: Session Created
    A->>U: Auth Response
```

## Notification Flow

```mermaid
sequenceDiagram
    participant E as Event Source
    participant N as Notification Service
    participant Q as Message Queue
    participant P as Push Service
    participant S as SMS Service
    participant W as WhatsApp Service

    E->>N: Trigger Notification
    N->>Q: Queue Message
    Q->>P: Push Notification
    Q->>S: SMS Message
    Q->>W: WhatsApp Message
```

## Error Handling Flow

```mermaid
sequenceDiagram
    participant S as Service
    participant E as Error Handler
    participant L as Logger
    participant M as Monitoring
    participant A as Alert Service

    S->>E: Error Occurs
    E->>L: Log Error
    E->>M: Update Metrics
    M->>A: Threshold Exceeded
    A->>E: Alert Team
```

## Data Sync Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Sync Service
    participant DB as Database
    participant Q as Queue
    participant W as WebSocket

    C->>S: Request Sync
    S->>DB: Get Changes
    DB->>S: Changes
    S->>Q: Queue Updates
    Q->>W: Push Updates
    W->>C: Sync Complete
``` 