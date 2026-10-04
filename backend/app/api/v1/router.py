from fastapi import APIRouter
from app.core.config import settings
from app.modules.auth.router import router as auth_router
from app.modules.company.router import router as company_router
from app.modules.customers.router import router as customer_router
from app.modules.addresses.router import router as address_router
from app.modules.services_catalog.router import router as services_router
from app.modules.garments.router import router as garments_router
from app.modules.pricing.router import router as pricing_router
from app.modules.orders.router import router as orders_router
from app.modules.pickup.router import router as pickup_router
from app.modules.partners.router import router as partners_router
from app.modules.station_operations.router import router as station_router
from app.modules.delivery.router import router as delivery_router
from app.modules.payments.router import router as payments_router
from app.modules.invoices.router import router as invoices_router
from app.modules.offers.router import router as offers_router
from app.modules.complaints.router import router as complaints_router
from app.modules.notifications.router import router as notifications_router
from app.modules.hangers.router import router as hangers_router
from app.modules.inventory.router import router as inventory_router
from app.modules.audit.router import router as audit_router
from app.modules.reports.router import router as reports_router
from app.modules.service_controls.router import router as service_controls_router
from app.modules.admin_ops.router import router as admin_ops_router
from app.modules.release.router import router as release_router

router = APIRouter(prefix=settings.api_prefix)

@router.get("/health", tags=["system"])
def health():
    return {"status": "ok", "service": "aala-presswaala-api", "version": settings.app_version}

@router.get("/ready", tags=["system"])
def readiness():
    return {"status": "ready", "environment": settings.environment, "database_configured": bool(settings.database_url)}

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(company_router, prefix="/company", tags=["company"])
router.include_router(customer_router, prefix="/customers", tags=["customers"])
router.include_router(address_router, prefix="/addresses", tags=["addresses"])

router.include_router(services_router, prefix="/services", tags=["services"])
router.include_router(garments_router, prefix="/garments", tags=["garments"])
router.include_router(pricing_router, prefix="/pricing", tags=["pricing"])
router.include_router(orders_router, prefix="/orders", tags=["orders"])
router.include_router(pickup_router, prefix="/pickups", tags=["pickups"])
router.include_router(partners_router, prefix="/partners", tags=["partners"])
router.include_router(station_router, prefix="/station", tags=["station-operations"])
router.include_router(delivery_router, prefix="/delivery", tags=["delivery"])
router.include_router(payments_router, prefix="/payments", tags=["payments"])
router.include_router(invoices_router, prefix="/invoices", tags=["invoices"])
router.include_router(offers_router, prefix="/offers", tags=["offers"])
router.include_router(complaints_router, prefix="/complaints", tags=["complaints"])
router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
router.include_router(hangers_router, prefix="/hangers", tags=["hangers"])
router.include_router(inventory_router, prefix="/inventory", tags=["inventory"])
router.include_router(audit_router, prefix="/audit", tags=["audit"])
router.include_router(reports_router, prefix="/reports", tags=["reports"])
router.include_router(service_controls_router, prefix="/service-controls", tags=["service-controls"])
router.include_router(admin_ops_router, prefix="/admin", tags=["admin-operations"])
router.include_router(release_router, prefix="/release", tags=["release"])
