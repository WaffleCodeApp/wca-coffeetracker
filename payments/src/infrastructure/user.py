from dataclasses import dataclass


@dataclass
class User:
    id: str
    email: str
    name: str
    role: str
    customer_id: str
    picture: str
    phone_number: str
    enabled: bool
