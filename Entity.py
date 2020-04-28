import threading


class Entity(threading.Thread):
    def __init__(self, entityMaster, eid, name, x, y):
        threading.Thread.__init__(self)

        self.entityMaster = entityMaster
        self.eid = eid
        self.name = name
        self.x = x
        self.y = y
        self.active = True


