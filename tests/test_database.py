import os
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.utils.database import Base, Customer, Conversation, Order

# Load environment variables
load_dotenv()

@pytest.fixture
def db_session():
    """Create a database session for testing"""
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    yield session
    
    # Clean up
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_create_customer(db_session):
    """Test creating a customer"""
    customer = Customer(
        phone_number="+1234567890",
        name="Test Customer",
        email="test@example.com"
    )
    
    db_session.add(customer)
    db_session.commit()
    
    # Retrieve the customer
    retrieved_customer = db_session.query(Customer).filter_by(phone_number="+1234567890").first()
    
    assert retrieved_customer is not None
    assert retrieved_customer.name == "Test Customer"
    assert retrieved_customer.email == "test@example.com"

def test_create_conversation(db_session):
    """Test creating a conversation"""
    # Create a customer first
    customer = Customer(phone_number="+1234567890")
    db_session.add(customer)
    db_session.commit()
    
    # Create a conversation
    conversation = Conversation(
        customer_id=customer.id,
        message="Hello",
        response="Hi there!"
    )
    
    db_session.add(conversation)
    db_session.commit()
    
    # Retrieve the conversation
    retrieved_conversation = db_session.query(Conversation).filter_by(customer_id=customer.id).first()
    
    assert retrieved_conversation is not None
    assert retrieved_conversation.message == "Hello"
    assert retrieved_conversation.response == "Hi there!"

def test_create_order(db_session):
    """Test creating an order"""
    # Create a customer first
    customer = Customer(phone_number="+1234567890")
    db_session.add(customer)
    db_session.commit()
    
    # Create an order
    order = Order(
        customer_id=customer.id,
        order_number="ORD-123",
        status="pending",
        items={"product_id": 1, "quantity": 2},
        total_amount=2000,  # $20.00
        shipping_address={"street": "123 Main St", "city": "Anytown", "zip": "12345"}
    )
    
    db_session.add(order)
    db_session.commit()
    
    # Retrieve the order
    retrieved_order = db_session.query(Order).filter_by(order_number="ORD-123").first()
    
    assert retrieved_order is not None
    assert retrieved_order.status == "pending"
    assert retrieved_order.total_amount == 2000
    assert retrieved_order.items["product_id"] == 1
    assert retrieved_order.shipping_address["city"] == "Anytown" 