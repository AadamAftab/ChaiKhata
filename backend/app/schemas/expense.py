# app/schemas/expense.py
from pydantic import BaseModel, Field
from typing import Optional

class ExpenseCreateSchema(BaseModel):
    amount: float = Field(..., gt=0, description="The monetary value of the transaction, must be greater than zero.")
    source: str = Field(..., description="The merchant or origin source: 'Zepto', 'Zomato', 'Swiggy', 'Cali Burrito', or 'Cash'")
    category: str = Field(..., description="The thematic grouping: e.g., 'Snacks', 'Main Meals', 'Groceries'")
    description: Optional[str] = Field(None, max_length=150, description="Optional brief context text.")

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 180.50,
                "source": "Zepto",
                "category": "Snacks",
                "description": "Late-night instant Maggi haul"
            }
        }