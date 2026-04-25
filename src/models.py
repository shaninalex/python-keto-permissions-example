import json
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: str
    email: str
    groups: List[str]


@dataclass(frozen=True)
class Order:
    id: int
    code: str
    name: str
    total_price: float
    items: List[OrderItem]
    processed_at: datetime
    created_at: datetime


@dataclass(frozen=True)
class OrderItem:
    id: int
    code: str
    name: str
    count: int
    total_price: float


class DB:
    def __init__(self):
        self._orders: List[Order] = []
        self._users: List[User] = []
        self._init_orders("./resources/orders.json")
        self._init_users("./resources/users.json")

    def get_user(self, email: str) -> User:
        for user in self._users:
            if user.email == email:
                return user
        raise Exception(f"User with email {email} not found")

    def get_users(self) -> List[User]:
        return self._users

    def get_orders(self) -> List[Order]:
        return self._orders

    def _init_users(self, file: str):
        with open(file, "r") as f:
            json_data = json.load(f)
            for data in json_data:
                self._users.append(User(**data))

    def _init_orders(self, file: str):
        with open(file, "r") as f:
            data = json.load(f)
            for o in data:
                order_items: List[OrderItem] = list()
                for item in o['items']:
                    order_items.append(OrderItem(
                        id=item["id"],
                        code=item["code"],
                        name=item["name"],
                        count=item["count"],
                        total_price=item["total_price"],
                    ))
                self._orders.append(Order(
                    id=o["id"],
                    code=o["code"],
                    name=o['name'],
                    total_price=o['total_price'],
                    processed_at=o['processed_at'],
                    created_at=o['created_at'],
                    items=order_items,
                ))
