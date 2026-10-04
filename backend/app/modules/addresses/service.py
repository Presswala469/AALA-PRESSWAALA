from app.modules.addresses.repository import add, list_for_customer

def create(data: dict):
    return add(data)

def list_current_and_history(customer_id: str):
    return list_for_customer(customer_id)

