from datetime import datetime, timezone, timedelta
from app.core.config import settings
from app.core.database import get_connection


def set_rule(service_code: str, target_minutes: int, urgent_threshold_minutes: int = 60):
    if target_minutes <= 0 or urgent_threshold_minutes < 0:
        raise ValueError('Invalid TAT rule')
    if not settings.database_url:
        _rules[service_code]={'service_code':service_code,'target_minutes':target_minutes,'urgent_threshold_minutes':urgent_threshold_minutes,'active':True}
        return dict(_rules[service_code])
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''insert into service_tat_rules(service_code,target_minutes,urgent_threshold_minutes,active)
                           values(%s,%s,%s,true)
                           on conflict(service_code) do update set target_minutes=excluded.target_minutes,urgent_threshold_minutes=excluded.urgent_threshold_minutes,active=true,updated_at=now()
                           returning service_code,target_minutes,urgent_threshold_minutes,active''',(service_code,target_minutes,urgent_threshold_minutes))
            r=cur.fetchone(); conn.commit()
    return dict(zip(('service_code','target_minutes','urgent_threshold_minutes','active'),r))


def get_rule(service_code):
    if not settings.database_url: return dict(_rules[service_code]) if service_code in _rules else None
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('select service_code,target_minutes,urgent_threshold_minutes,active from service_tat_rules where service_code=%s and active=true',(service_code,)); r=cur.fetchone()
    return dict(zip(('service_code','target_minutes','urgent_threshold_minutes','active'),r)) if r else None


def calculate_due(service_code, started_at=None):
    rule=get_rule(service_code)
    if not rule: return None
    started=started_at or datetime.now(timezone.utc)
    if isinstance(started,str): started=datetime.fromisoformat(started.replace('Z','+00:00'))
    return started + timedelta(minutes=rule['target_minutes'])

_rules={}
