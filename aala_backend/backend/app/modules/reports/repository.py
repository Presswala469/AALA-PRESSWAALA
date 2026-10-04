from copy import deepcopy
from datetime import datetime, timezone
from app.core.config import settings
from app.core.database import get_connection


def _date_clause(column, filters, params):
    clause = ""
    if filters.get("date_from"):
        clause += f" and {column} >= %s"
        params.append(filters["date_from"])
    if filters.get("date_to"):
        clause += f" and {column} < (%s::date + interval '1 day')"
        params.append(filters["date_to"])
    return clause


def _query(sql, params, keys):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return [dict(zip(keys, row)) for row in cur.fetchall()]


def report(report_type, filters):
    f = {k: v for k, v in filters.items() if v is not None}
    limit = f.get("limit", 500)
    if not settings.database_url:
        from app.modules.reports import service
        return service._memory_report(report_type, f)

    p = []
    date_filter = _date_clause("o.created_at", f, p)
    station_join = ""
    station_filter = ""
    if f.get("station_code"):
        station_join = " left join station_receiving sr_filter on sr_filter.order_id=o.order_id"
        station_filter = " and sr_filter.station_code=%s"
        p.append(f["station_code"])
    partner_join = ""
    partner_filter = ""
    if f.get("partner_id"):
        partner_join = " left join pickup_records pr_filter on pr_filter.order_id=o.order_id"
        partner_filter = " and pr_filter.partner_id=%s"
        p.append(f["partner_id"])
    customer_filter = " and o.customer_id=%s" if f.get("customer_id") else ""
    if f.get("customer_id"): p.append(f["customer_id"])
    status_filter = " and o.status=%s" if f.get("status") else ""
    if f.get("status"): p.append(f["status"])
    service_filter = " and o.service_code=%s" if f.get("service_code") else ""
    if f.get("service_code"): p.append(f["service_code"])

    if report_type == "revenue":
        sql = f"""select count(*)::int as order_count, coalesce(sum(o.subtotal),0) as gross_subtotal,
            coalesce(sum(o.discount),0) as discounts, coalesce(sum(o.total),0) as net_revenue,
            coalesce(sum(case when o.payment_method='COD' then o.total else 0 end),0) as cod_value,
            coalesce(sum(case when o.payment_method<>'COD' then o.total else 0 end),0) as prepaid_value
            from orders o{station_join}{partner_join} where 1=1{date_filter}{station_filter}{partner_filter}{customer_filter}{status_filter}{service_filter}"""
        return _query(sql, p, ["order_count","gross_subtotal","discounts","net_revenue","cod_value","prepaid_value"])

    if report_type == "orders":
        p2 = list(p)
        sql = f"""select o.order_id,o.customer_id,o.address_id,o.service_code,o.pickup_slot_id,o.status,
            o.subtotal,o.discount,o.total,o.payment_method,o.offer_code,o.created_at
            from orders o{station_join}{partner_join} where 1=1{date_filter}{station_filter}{partner_filter}{customer_filter}{status_filter}{service_filter}
            order by o.created_at desc limit %s"""
        p2.append(limit)
        return _query(sql, p2, ["order_id","customer_id","address_id","service_code","pickup_slot_id","status","subtotal","discount","total","payment_method","offer_code","created_at"])

    if report_type == "customers":
        p=[]; df=_date_clause("c.created_at", f, p)
        city = ""; 
        if f.get("city"): city=" and exists (select 1 from customer_addresses ca where ca.customer_id=c.id and ca.city=%s and ca.is_current=true)"; p.append(f["city"])
        p.append(limit)
        return _query(f"""select c.customer_id,c.global_customer_number,c.name,c.mobile_number,c.email,c.status,c.created_at,
            count(o.order_id)::int as order_count,coalesce(sum(o.total),0) as lifetime_value
            from customers c left join orders o on o.customer_id=c.customer_id where 1=1{df}{city}
            group by c.id order by c.created_at desc limit %s""", p,
            ["customer_id","global_customer_number","name","mobile_number","email","status","created_at","order_count","lifetime_value"])

    if report_type == "partners":
        p=[]; df=_date_clause("p.created_at", f, p)
        station="" 
        if f.get("station_code"): station=" and exists (select 1 from partner_station_assignments psa where psa.partner_id=p.partner_id and psa.station_code=%s and psa.active=true)"; p.append(f["station_code"])
        p.append(limit)
        return _query(f"""select p.partner_id,p.employee_id,p.name,p.mobile_number,p.active,p.created_at,
            count(distinct pr.order_id)::int as pickup_orders,count(distinct dj.order_id)::int as delivery_orders
            from partners p left join pickup_records pr on pr.partner_id=p.partner_id
            left join delivery_jobs dj on dj.partner_id=p.partner_id where 1=1{df}{station}
            group by p.id order by p.created_at desc limit %s""", p,
            ["partner_id","employee_id","name","mobile_number","active","created_at","pickup_orders","delivery_orders"])

    if report_type == "stations":
        p=[]; df=_date_clause("sr.received_at", f, p)
        station="" 
        if f.get("station_code"): station=" and sr.station_code=%s"; p.append(f["station_code"])
        return _query(f"""select sr.station_code,count(*)::int as received_orders,
            coalesce(sum(sr.partner_handover_quantity),0)::int as handover_quantity,
            coalesce(sum(sr.station_received_quantity),0)::int as received_quantity,
            coalesce(sum(case when sr.discrepancy then 1 else 0 end),0)::int as discrepancy_count
            from station_receiving sr where 1=1{df}{station} group by sr.station_code order by sr.station_code""", p,
            ["station_code","received_orders","handover_quantity","received_quantity","discrepancy_count"])

    if report_type == "garments":
        p=[]; df=_date_clause("o.created_at", f, p)
        if f.get("service_code"): df += " and o.service_code=%s"; p.append(f["service_code"])
        p.append(limit)
        return _query(f"""select oi.garment_code,sum(oi.quantity)::int as quantity,
            sum(oi.line_total) as revenue, count(distinct oi.order_id)::int as order_count
            from order_items oi join orders o on o.order_id=oi.order_id where 1=1{df}
            group by oi.garment_code order by quantity desc limit %s""", p,
            ["garment_code","quantity","revenue","order_count"])

    if report_type == "hangers":
        p=[]; df=_date_clause("h.created_at", f, p)
        if f.get("customer_id"): df += " and h.customer_id=%s"; p.append(f["customer_id"])
        p.append(limit)
        return _query(f"""select h.status,sum(h.quantity)::int as quantity,count(*)::int as record_count
            from hangers h where 1=1{df} group by h.status order by h.status limit %s""", p,
            ["status","quantity","record_count"])

    if report_type == "bags_boxes":
        p=[]; clauses=[]
        if f.get("item_type"): clauses.append("item_type=%s");p.append(f["item_type"])
        if f.get("status"): clauses.append("status=%s");p.append(f["status"])
        where = (" where " + " and ".join(clauses)) if clauses else ""
        return _query(f"select item_type,status,count(*)::int as quantity from bags_boxes{where} group by item_type,status order by item_type,status",p,["item_type","status","quantity"])

    if report_type == "offers":
        p=[]; df=_date_clause("o.created_at", f, p)
        offer="" 
        if f.get("offer_code"): offer=" and o.offer_code=%s"; p.append(f["offer_code"])
        p.append(limit)
        return _query(f"""select coalesce(o.offer_code,'(none)') as offer_code,count(*)::int as order_count,
            coalesce(sum(o.discount),0) as discount_value,coalesce(sum(o.total),0) as revenue
            from orders o where 1=1{df}{offer} group by o.offer_code order by order_count desc limit %s""", p,
            ["offer_code","order_count","discount_value","revenue"])

    if report_type == "complaints":
        p=[]; df=_date_clause("c.created_at", f, p)
        category="" 
        if f.get("category"): category=" and c.category=%s";p.append(f["category"])
        status="" 
        if f.get("status"): status=" and c.status=%s";p.append(f["status"])
        p.append(limit)
        return _query(f"select complaint_id,order_id,customer_id,category,description,status,assigned_to,remarks,created_at,updated_at from complaints c where 1=1{df}{category}{status} order by c.created_at desc limit %s",p,
            ["complaint_id","order_id","customer_id","category","description","status","assigned_to","remarks","created_at","updated_at"])

    if report_type == "customer_locations":
        p=[]; city="" 
        if f.get("city"): city=" and ca.city=%s";p.append(f["city"])
        p.append(limit)
        return _query(f"""select c.customer_id,c.global_customer_number,c.name,ca.label,ca.address_line,ca.city,ca.state,ca.pincode,
            ca.building_society,ca.latitude,ca.longitude,ca.is_current,ca.updated_at
            from customers c join customer_addresses ca on ca.customer_id=c.id where 1=1{city}
            order by ca.updated_at desc limit %s""",p,
            ["customer_id","global_customer_number","name","label","address_line","city","state","pincode","building_society","latitude","longitude","is_current","updated_at"])

    if report_type == "customer_history":
        p=[]; cid="" 
        if f.get("customer_id"): cid=" and c.customer_id=%s";p.append(f["customer_id"])
        p.append(limit)
        return _query(f"""select c.customer_id,c.global_customer_number,h.source_address_id,h.address_snapshot,h.changed_at,h.changed_by
            from customers c join customer_address_history h on h.customer_id=c.id where 1=1{cid}
            order by h.changed_at desc limit %s""",p,
            ["customer_id","global_customer_number","source_address_id","address_snapshot","changed_at","changed_by"])

    raise ValueError("Unsupported report type")

