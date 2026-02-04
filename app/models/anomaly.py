"""Anomaly detection models."""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class AnomalyType(str, Enum):
    """Types of anomalies that can be detected."""
    PRICE_INCREASE = "price_increase"
    QUANTITY_DEVIATION = "quantity_deviation"
    NEW_ITEM = "new_item"
    AMOUNT_DEVIATION = "amount_deviation"


class AnomalyDetail(BaseModel):
    """Details about a specific anomaly."""
    type: AnomalyType
    item_name: Optional[str] = None
    severity: int = Field(ge=0, le=100, description="Severity score 0-100")
    description: str


class AnomalyResult(BaseModel):
    """Result of anomaly detection analysis."""
    is_suspicious: bool
    risk_score: int = Field(ge=0, le=100, description="Overall risk score 0-100")
    anomalies: List[AnomalyDetail]
    explanation: str
