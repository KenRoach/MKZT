from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from enum import Enum

class PaymentChannel(str, Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class PaymentRequest(BaseModel):
    order_id: str = Field(..., description="ID of the order to pay for")
    amount: float = Field(..., description="Amount to pay", gt=0)
    currency: str = Field(..., description="Currency code (e.g. USD)", min_length=3, max_length=3)
    channel: PaymentChannel = Field(..., description="Payment channel to use")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional payment metadata")

class RefundRequest(BaseModel):
    transaction_id: str = Field(..., description="ID of the transaction to refund")
    amount: float = Field(..., description="Amount to refund", gt=0)
    reason: Optional[str] = Field(None, description="Reason for the refund")

class PaymentResponse(BaseModel):
    status: PaymentStatus = Field(..., description="Status of the payment")
    transaction_id: str = Field(..., description="ID of the payment transaction")
    amount: float = Field(..., description="Amount paid")
    currency: str = Field(..., description="Currency code")
    payment_method: str = Field(..., description="Payment method used")
    payment_details: Dict[str, Any] = Field(..., description="Additional payment details")
    created_at: str = Field(..., description="When the payment was created")
    updated_at: str = Field(..., description="When the payment was last updated")

class RefundResponse(BaseModel):
    status: PaymentStatus = Field(..., description="Status of the refund")
    transaction_id: str = Field(..., description="ID of the refund transaction")
    amount: float = Field(..., description="Amount refunded")
    reason: Optional[str] = Field(None, description="Reason for the refund")
    refund_details: Dict[str, Any] = Field(..., description="Additional refund details")
    created_at: str = Field(..., description="When the refund was created")
    updated_at: str = Field(..., description="When the refund was last updated")

class PaymentStatusResponse(BaseModel):
    status: PaymentStatus = Field(..., description="Current status of the payment")
    transaction_id: str = Field(..., description="ID of the payment transaction")
    amount: float = Field(..., description="Amount paid")
    currency: str = Field(..., description="Currency code")
    payment_method: str = Field(..., description="Payment method used")
    payment_details: Dict[str, Any] = Field(..., description="Additional payment details")
    refund_details: Optional[Dict[str, Any]] = Field(None, description="Refund details if applicable")
    created_at: str = Field(..., description="When the payment was created")
    updated_at: str = Field(..., description="When the payment was last updated") 