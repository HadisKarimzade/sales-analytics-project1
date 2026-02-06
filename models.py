"""
OOP models for the sales domain.

Requirements satisfied:
- Base Entity class (inheritance hierarchy)
- Product, Customer, Order classes
- input validation in __init__
- __str__ and __repr__ implemented
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict


class ValidationError(ValueError):
    """Raised when an object is created with invalid input."""


@dataclass
class Entity:
    """Base entity with an id (inheritance root)."""
    id: str

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValidationError("Entity id must be a non-empty string.")

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class Product(Entity):
    name: str
    category: str
    base_price: float

    def __post_init__(self) -> None:
        super().__post_init__()
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValidationError("Product name must be a non-empty string.")
        if not isinstance(self.category, str) or not self.category.strip():
            raise ValidationError("Product category must be a non-empty string.")
        try:
            self.base_price = float(self.base_price)
        except Exception as e:
            raise ValidationError("Product base_price must be numeric.") from e
        if self.base_price < 0:
            raise ValidationError("Product base_price must be >= 0.")


@dataclass
class Customer(Entity):
    name: str
    email: str
    lifetime_value: float = 0.0

    def __post_init__(self) -> None:
        super().__post_init__()
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValidationError("Customer name must be a non-empty string.")
        if not isinstance(self.email, str) or "@" not in self.email:
            # dataset may not have emails; we keep validation relaxed but meaningful
            raise ValidationError("Customer email must look like an email (contain '@').")
        try:
            self.lifetime_value = float(self.lifetime_value)
        except Exception as e:
            raise ValidationError("Customer lifetime_value must be numeric.") from e
        if self.lifetime_value < 0:
            raise ValidationError("Customer lifetime_value must be >= 0.")


@dataclass
class Order:
    order_id: str
    customer_id: str
    order_date: date
    product_category: str
    product_name: str
    quantity: int
    unit_price: float
    order_amount: float
    status: str

    def __post_init__(self) -> None:
        if not isinstance(self.order_id, str) or not self.order_id.strip():
            raise ValidationError("Order order_id must be a non-empty string.")
        if not isinstance(self.customer_id, str) or not self.customer_id.strip():
            raise ValidationError("Order customer_id must be a non-empty string.")
        if not isinstance(self.product_category, str) or not self.product_category.strip():
            raise ValidationError("Order product_category must be a non-empty string.")
        if not isinstance(self.product_name, str) or not self.product_name.strip():
            raise ValidationError("Order product_name must be a non-empty string.")
        if self.status not in {"completed", "cancelled", "pending"}:
            raise ValidationError("Order status must be one of: completed/cancelled/pending.")
        try:
            self.quantity = int(self.quantity)
        except Exception as e:
            raise ValidationError("Order quantity must be int.") from e
        if self.quantity <= 0:
            raise ValidationError("Order quantity must be > 0.")
        try:
            self.unit_price = float(self.unit_price)
            self.order_amount = float(self.order_amount)
        except Exception as e:
            raise ValidationError("Order unit_price and order_amount must be numeric.") from e
        if self.unit_price < 0 or self.order_amount < 0:
            raise ValidationError("Order prices must be >= 0.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "order_date": self.order_date,
            "product_category": self.product_category,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "order_amount": self.order_amount,
            "status": self.status,
        }

    def __str__(self) -> str:
        return f"Order(order_id={self.order_id}, customer_id={self.customer_id}, amount={self.order_amount:.2f}, status={self.status})"

    def __repr__(self) -> str:
        return self.__str__()
