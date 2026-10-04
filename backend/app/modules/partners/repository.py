from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from app.core.config import settings
from app.core.database import get_connection

_partners = {}
_assignments = {}
_arrivals = {}
_verifications = {}
_damage = {}
_bags = {}
_pickups = {}


def _pid():
    return f"PAR-{uuid4().hex[:8].upper()}"


def _active_status_sql():
    return "(lower(coalesce(status,'')) in ('active','enabled'))"


def create_partner(data):
    # In-memory compatibility keeps the legacy PAR-* identifier.
    pid = _pid()
    row = {**data, "partner_id": pid, "created_at": datetime.now(timezone.utc).isoformat()}
    if not settings.database_url:
        _partners[pid] = row
        if data.get("station_code"):
            _assignments[pid] = {
                "partner_id": pid,
                "station_code": data["station_code"],
                "assigned_at": datetime.now(timezone.utc).isoformat(),
                "active": True,
            }
        return deepcopy(row)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """insert into users(mobile_number,full_name,mobile_verified_at)
                   values(%s,%s,now())
                   on conflict (mobile_number) do update
                   set full_name=excluded.full_name, updated_at=now()
                   returning id""",
                (data["mobile_number"], data["name"]),
            )
            user_id = cur.fetchone()[0]

            cur.execute("select id from roles where code='partner'")
            role = cur.fetchone()
            if not role:
                raise ValueError("Partner role is not configured")
            cur.execute(
                "insert into user_roles(user_id,role_id) values(%s,%s) on conflict do nothing",
                (user_id, role[0]),
            )

            # LIVE Supabase schema: partners.id is the partner identity.
            cur.execute(
                """insert into partners(id,user_id,employee_id,name,mobile_number,status)
                   values(gen_random_uuid(),%s,%s,%s,%s,%s)
                   returning id,created_at""",
                (user_id, data["employee_id"], data["name"], data["mobile_number"],
                 "ACTIVE" if data.get("active", True) else "INACTIVE"),
            )
            partner_id, created_at = cur.fetchone()

            if data.get("station_code"):
                cur.execute(
                    "select id,station_code from stations where station_code=%s limit 1",
                    (data["station_code"],),
                )
                station = cur.fetchone()
                if not station:
                    raise ValueError("Station not found")
                cur.execute(
                    """update partner_station_assignments
                       set is_active=false, assigned_to=current_date
                       where partner_id=%s and is_active=true""",
                    (partner_id,),
                )
                cur.execute(
                    """insert into partner_station_assignments
                       (id,partner_id,station_id,assigned_from,is_active)
                       values(gen_random_uuid(),%s,%s,current_date,true)""",
                    (partner_id, station[0]),
                )

            conn.commit()

    row = {
        "partner_id": str(partner_id),
        "employee_id": data["employee_id"],
        "name": data["name"],
        "mobile_number": data["mobile_number"],
        "active": data.get("active", True),
        "station_code": data.get("station_code"),
        "created_at": created_at.isoformat(),
    }
    return deepcopy(row)


def list_partners(station_code=None):
    if not settings.database_url:
        return [
            deepcopy(x) for x in _partners.values()
            if not station_code or _assignments.get(x["partner_id"], {}).get("station_code") == station_code
        ]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """select p.id,p.employee_id,p.name,p.mobile_number,
                          (lower(coalesce(p.status,'')) in ('active','enabled')) as active,
                          s.station_code
                   from partners p
                   left join partner_station_assignments a
                     on a.partner_id=p.id and a.is_active=true
                   left join stations s on s.id=a.station_id
                   where (%s is null or s.station_code=%s)
                   order by p.name""",
                (station_code, station_code),
            )
            rows = cur.fetchall()
    return [
        dict(zip(("partner_id", "employee_id", "name", "mobile_number", "active", "station_code"), r))
        for r in rows
    ]


def assign(pid, station):
    if not settings.database_url:
        if pid not in _partners and pid not in _assignments:
            raise ValueError("Partner not found")
        row = {
            "partner_id": pid,
            "station_code": station,
            "assigned_at": datetime.now(timezone.utc).isoformat(),
            "active": True,
        }
        _assignments[pid] = row
        return deepcopy(row)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select id from partners where id=%s and " + _active_status_sql(),
                (pid,),
            )
            partner = cur.fetchone()
            if not partner:
                raise ValueError("Partner not found")

            cur.execute("select id,station_code from stations where station_code=%s limit 1", (station,))
            station_row = cur.fetchone()
            if not station_row:
                raise ValueError("Station not found")

            cur.execute(
                """update partner_station_assignments
                   set is_active=false, assigned_to=current_date
                   where partner_id=%s and is_active=true""",
                (partner[0],),
            )
            cur.execute(
                """insert into partner_station_assignments
                   (id,partner_id,station_id,assigned_from,is_active)
                   values(gen_random_uuid(),%s,%s,current_date,true)
                   returning assigned_from""",
                (partner[0], station_row[0]),
            )
            assigned_from = cur.fetchone()[0]
            conn.commit()

    return {
        "partner_id": str(partner[0]),
        "station_code": station_row[1],
        "assigned_at": assigned_from,
        "active": True,
    }


def assignment(pid):
    if not settings.database_url:
        return deepcopy(_assignments.get(pid))

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """select p.id,s.station_code,a.assigned_from,a.is_active
                   from partner_station_assignments a
                   join partners p on p.id=a.partner_id
                   join stations s on s.id=a.station_id
                   where p.id=%s and a.is_active=true
                   order by a.assigned_from desc limit 1""",
                (pid,),
            )
            r = cur.fetchone()
    return dict(zip(("partner_id", "station_code", "assigned_at", "active"), r)) if r else None


def get_partner(pid):
    if not settings.database_url:
        return deepcopy(_partners.get(pid))

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """select id,employee_id,name,mobile_number,
                          (lower(coalesce(status,'')) in ('active','enabled')) as active
                   from partners where id=%s""",
                (pid,),
            )
            r = cur.fetchone()
    return dict(zip(("partner_id", "employee_id", "name", "mobile_number", "active"), r)) if r else None


def record(key, store, data):
    store[key] = deepcopy(data)
    return deepcopy(data)


def get_store(store, key):
    return deepcopy(store.get(key))
