def get_pending_orders(producer_id: int = 1):
    """Returns pending orders for a given producer."""
    # Mock implementation to replace truncated code
    # In production, this queries the SQLite database/connection.py
    return [
        {"order_id": 101, "product": "Widget A", "quantity": 50, "status": "pending"},
        {"order_id": 102, "product": "Widget B", "quantity": 20, "status": "pending"}
    ]
