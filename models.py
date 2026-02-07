from dataclasses import dataclass


@dataclass
class Entity:
    id: str

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("id must be a non-empty string")

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id})"

    def __repr__(self):
        return self.__str__()


@dataclass
class Product(Entity):
    name: str
    category: str
    base_price: float

    def __post_init__(self):
        super().__post_init__()
        if not self.name.strip():
            raise ValueError("name required")
        if not self.category.strip():
            raise ValueError("category required")
        self.base_price = float(self.base_price)


@dataclass
class Customer(Entity):
    name: str
    email: str
    lifetime_value: float = 0.0

    def __post_init__(self):
        super().__post_init__()
        if not self.name.strip():
            raise ValueError("name required")
        if "@" not in self.email:
            raise ValueError("invalid email")
        self.lifetime_value = float(self.lifetime_value)


@dataclass
class Order:
    order_id: str
    customer_id: str
    order_date: object
    amount: float
    status: str

    def __post_init__(self):
        if not self.order_id.strip():
            raise ValueError("order_id required")
        if not self.customer_id.strip():
            raise ValueError("customer_id required")
        self.amount = float(self.amount)

    def __str__(self):
        return f"Order({self.order_id}, {self.customer_id}, {self.amount}, {self.status})"

    def __repr__(self):
        return self.__str__()
