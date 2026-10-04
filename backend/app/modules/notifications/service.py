from datetime import datetime, timezone
from app.modules.notifications import repository as repo
from app.modules.notifications import provider

DEFAULT_EVENT_CHANNELS = {
    "REGISTRATION": ["PUSH","IN_APP"], "BOOKING": ["PUSH","IN_APP"],
    "ASSIGNMENT": ["PUSH","IN_APP"], "ARRIVAL_PICKUP": ["PUSH","IN_APP"],
    "STATION_RECEIPT": ["PUSH","IN_APP"], "STATUS": ["PUSH","IN_APP"],
    "READY": ["PUSH","IN_APP"], "OUT_FOR_DELIVERY": ["PUSH","IN_APP"],
    "DELIVERED": ["PUSH","IN_APP"], "INVOICE": ["PUSH","IN_APP","EMAIL"],
    "OFFERS": ["PUSH","IN_APP"], "DELAY": ["PUSH","IN_APP"],
    "SERVICE_AVAILABILITY": ["PUSH","IN_APP"], "COMPLAINT": ["PUSH","IN_APP"],
    "OTP": ["SMS"],
}

def queue(data, actor_user_id=None):
    return repo.create(data, actor_user_id=actor_user_id)

def dispatch_event(data, actor_user_id=None):
    event = data["event_type"]
    channels = data.get("channels") or DEFAULT_EVENT_CHANNELS.get(event, ["PUSH","IN_APP"])
    channels = [c for c in channels if c in {"IN_APP","PUSH","SMS","WHATSAPP","EMAIL"}]
    channels = repo.allowed_channels(data["recipient_id"], event, channels)
    results=[]
    base_key=data.get("idempotency_key")
    for channel in channels:
        key=f"{base_key}:{channel}" if base_key else None
        results.append(queue({
            "recipient_id":data["recipient_id"], "channel":channel,
            "title":data["title"], "message":data["message"], "data":data.get("data") or {},
            "event_type":event, "idempotency_key":key, "priority":data.get("priority","NORMAL")
        }, actor_user_id=actor_user_id))
    return results

def mark(nid,status,actor_user_id=None):
    return repo.update(nid,status,actor_user_id=actor_user_id)

def list_for_recipient(recipient_id):
    return repo.for_recipient(recipient_id)

def register_device(data, actor_user_id=None):
    return repo.register_device(data["user_id"],data["platform"],data["token"],
                                data.get("installation_id"),data.get("device_id"),data.get("app_version"),
                                actor_user_id=actor_user_id)

def deactivate_device(token, actor_user_id=None):
    return repo.deactivate_device(token, actor_user_id=actor_user_id)

def get_device_owner(token):
    return repo.get_device_owner(token)

def set_preference(data, actor_user_id=None):
    return repo.set_preference(data["user_id"],data["event_type"],data["channel"],data["enabled"],actor_user_id)

def get_preferences(user_id,event_type=None):
    return repo.get_preferences(user_id,event_type)

def send(nid):
    item=repo.get(nid)
    if not item:
        return None
    channel=item["channel"]
    recipient_id=item["recipient_id"]
    tokens=repo.active_tokens(recipient_id) if channel=="PUSH" else [None]
    if not tokens:
        return repo.update(nid,"FAILED",attempt_count=1,failure_code="NO_DEVICE_TOKEN",
                           failure_reason="No active device token available")
    last=None
    successes=0
    attempts=0
    for token in tokens:
        # One provider call per active app instance. Retry scheduling is represented in the DB;
        # a worker/cron can safely call send() again without duplicate notification creation.
        attempt_no=repo.next_attempt_no(nid)
        result=provider.send(channel,token,item["title"],item["message"],item.get("data") or {})
        attempts += 1
        repo.add_attempt(nid,attempt_no,result.provider,"SENT" if result.success else "FAILED",
                         result.message_id,result.error_code,result.error_message,target_token=token)
        last=result
        if result.success:
            successes += 1
        elif result.permanent_token_failure and token:
            repo.deactivate_token(token)
    if successes:
        return repo.update(nid,"SENT",provider=last.provider,provider_message_id=last.message_id,
                           attempt_count=attempts,sent_at=datetime.now(timezone.utc).isoformat(),
                           failure_code=None,failure_reason=None)
    return repo.update(nid,"FAILED",provider=last.provider,attempt_count=attempts,
                       failure_code=last.error_code,failure_reason=last.error_message)

def get(nid):
    return repo.get(nid)
