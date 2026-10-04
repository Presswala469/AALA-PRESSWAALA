from app.modules.customers.repository import create_customer, get_customer

def create(data: dict):
    return create_customer(data)

def get(customer_id: str):
    return get_customer(customer_id)

