import csv
import io
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from app.core.constants import UserRole
from app.core.permissions import require_role
from app.modules.reports.schemas import ReportFilters
from app.modules.reports import service

router = APIRouter()
_admin = Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN))

@router.get('/types', dependencies=[_admin])
def types():
    return {'report_types': sorted(service.REPORT_TYPES)}

@router.get('/{report_type}', dependencies=[_admin])
def report(
    report_type: str,
    date_from: str | None = Query(None), date_to: str | None = Query(None),
    station_code: str | None = Query(None), partner_id: str | None = Query(None),
    customer_id: str | None = Query(None), status: str | None = Query(None),
    service_code: str | None = Query(None), city: str | None = Query(None),
    offer_code: str | None = Query(None), item_type: str | None = Query(None),
    category: str | None = Query(None), limit: int = Query(500, ge=1, le=5000),
):
    filters = ReportFilters.model_validate({k:v for k,v in locals().items() if k not in {'report_type'}})
    return {'report_type': report_type, 'filters': filters.model_dump(exclude_none=True), 'rows': service.generate(report_type, filters.model_dump(exclude_none=True))}

@router.get('/{report_type}/export.csv', dependencies=[_admin])
def export_csv(
    report_type: str,
    date_from: str | None = Query(None), date_to: str | None = Query(None),
    station_code: str | None = Query(None), partner_id: str | None = Query(None),
    customer_id: str | None = Query(None), status: str | None = Query(None),
    service_code: str | None = Query(None), city: str | None = Query(None),
    offer_code: str | None = Query(None), item_type: str | None = Query(None),
    category: str | None = Query(None), limit: int = Query(5000, ge=1, le=5000),
):
    filters = ReportFilters.model_validate({k:v for k,v in locals().items() if k not in {'report_type'}})
    rows = service.generate(report_type, filters.model_dump(exclude_none=True))
    output = io.StringIO()
    if rows:
        keys=[]
        for row in rows:
            for key in row.keys():
                if key not in keys: keys.append(key)
        writer=csv.DictWriter(output,fieldnames=keys,extrasaction='ignore'); writer.writeheader()
        writer.writerows(rows)
    else:
        output.write('no_data\n')
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type='text/csv', headers={'Content-Disposition': f'attachment; filename={report_type}.csv'})

