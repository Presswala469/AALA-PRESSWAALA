from enum import StrEnum


class UserRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    STATION_MANAGER = "station_manager"
    PARTNER = "partner"
    CUSTOMER = "customer"


class OrderStatus(StrEnum):
    BOOKING_CONFIRMED = "booking_confirmed"
    PICKUP_ASSIGNED = "pickup_assigned"
    PICKED_UP = "picked_up"
    STATION_RECEIVED = "station_received"
    READY_FOR_DELIVERY = "ready_for_delivery"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class StationStatus(StrEnum):
    RECEIVED = "received"
    READY_FOR_DELIVERY = "ready_for_delivery"
    ON_HOLD = "on_hold"
    REJECTED = "rejected"


class AuditAction(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    RECOVERY = "recovery"
