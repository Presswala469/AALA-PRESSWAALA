from app.modules.station_support import repository as repo

def create(data, actor_user_id=None): return repo.create(data,actor_user_id)
def update(request_id,status,actor_user_id=None): return repo.update(request_id,status,actor_user_id)
def list_for_station(station_code): return repo.list_for_station(station_code)
