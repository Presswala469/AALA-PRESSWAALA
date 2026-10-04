STATES = ('BOOKING_CONFIRMED','PICKUP','IRON_STATION','RECEIVED','READY_FOR_DELIVERY','OUT_FOR_DELIVERY','DELIVERED','CANCELLED','ON_HOLD','REJECTED')
TRANSITIONS = {
 'BOOKING_CONFIRMED': {'PICKUP','CANCELLED'},
 'PICKUP': {'IRON_STATION','CANCELLED'},
 'IRON_STATION': {'RECEIVED','ON_HOLD','REJECTED'},
 'RECEIVED': {'READY_FOR_DELIVERY','ON_HOLD','REJECTED'},
 'READY_FOR_DELIVERY': {'OUT_FOR_DELIVERY','ON_HOLD'},
 'OUT_FOR_DELIVERY': {'DELIVERED','ON_HOLD'},
 'ON_HOLD': {'RECEIVED','READY_FOR_DELIVERY','OUT_FOR_DELIVERY','CANCELLED','REJECTED'},
 'REJECTED': set(), 'DELIVERED': set(), 'CANCELLED': set(),
}
def can_transition(current,new): return new in TRANSITIONS.get(current,set())
def transition(current,new):
 if not can_transition(current,new): raise ValueError(f'Invalid order transition: {current} -> {new}')
 return new
