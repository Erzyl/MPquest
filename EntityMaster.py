import random

from NetworkConstants import receive_codes, send_codes, handshake_codes
import struct,threading,socket,time
from Network import *
import Network
from Entity import Entity


class EntityMaster(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)

        self.buffer = Network.Buff()
        self.entities = []
        self.running = True
        self.server = server

        self.eCurId = 1

        self.wep_doSpawn = 1
        self.wep_timer = 0
        self.wep_timeToRespawn = 5
        self.wep_spawnLocations = []
        self.wep_spawnLocations.append((3000, 950))

        self.hp_doSpawn = 1
        self.hp_timer = 0
        self.hp_timeToRespawn = 5
        self.hp_spawnLocations = []
        self.hp_spawnLocations.append((2200, 900))
        self.hp_spawnLocations.append((1300, 2200))
        self.hp_spawnLocations.append((2900, 3300))

    def run(self):

        while self.running:
            time.sleep(1 / 1000)

            # HANDLE WEP SPAWN
            name = "o_w2pickup"
            if self.wep_doSpawn == 1:
                self.wep_doSpawn = 0
                spot = 0
                xx = self.wep_spawnLocations[spot][0]
                yy = self.wep_spawnLocations[spot][1]
                self.spawnNew(self.eCurId, name, xx, yy)

            exists = 0
            if len(self.entities) != 0:
                for e in self.entities:
                    if e.name == name:
                        exists = 1
            if exists == 0:
                self.wep_timer += 1 / 1000

                if self.wep_timer >= self.wep_timeToRespawn:
                    self.wep_doSpawn = 1
                    self.wep_timer = 0
            else:
                self.wep_timer = 0

            #HANDLE HP SPAWN
            name = "o_healthPacket"
            if self.hp_doSpawn == 1:
                self.hp_doSpawn = 0
                spot = round(random.randrange(0, 3))
                xx = self.hp_spawnLocations[spot][0]
                yy = self.hp_spawnLocations[spot][1]
                self.spawnNew(self.eCurId,name, xx, yy)

            exists = 0
            if len(self.entities) != 0:
                for e in self.entities:
                    if e.name == name:
                        exists = 1
            if exists == 0:
                self.hp_timer += 1 / 1000

                if self.hp_timer >= self.hp_timeToRespawn:
                    self.hp_doSpawn = 1
                    self.hp_timer = 0
            else:
                self.hp_timer = 0




    def spawnNew(self, id, name, x, y):
        print("Spawning entity: {0} ({1},{2})".format(name, x, y))
        entity = Entity(self, id, name, x, y)
        entity.start()
        self.send_entity_create(id, name, x, y)
        self.entities.append(entity)
        self.eCurId += 1

    def send_entity_create(self, id, name, x, y):
        self.clearbuffer()
        self.writebyte(send_codes["ENT_CREATE"])
        self.writebyte(id)
        self.writestring(name)
        self.writedouble(x)
        self.writedouble(y)
        self.sendmessage_other()




    ## MAKE INTO OWN SCRIPT
    def sendmessage(self, buff=None, debug=False):
        if buff == None:
            buff = self.buffer
        types = ''.join(buff.BufferWriteT)
        length = struct.calcsize("=" + types)
        buff.BufferWrite[0] = length  # set the header length

        self.connection.send(struct.pack("=" + types, *buff.BufferWrite))
        if debug == True:
            print(*buff.BufferWrite, ''.join(buff.BufferWriteT), struct.pack("=" + types, *buff.BufferWrite))


    def sendmessage_other(self):
        for c in self.server.clients:
            if id(c) != id(self) and c.user != None:
                c.sendmessage(self.buffer)


    def sendmessage_all(self):
        for c in self.server.clients:
            if c.user != None:
                c.sendmessage(self.buffer)


    def clearbuffer(self):
        self.buffer.clearbuffer()


    def writebit(self, b):
        self.buffer.writebit(b)


    def writebyte(self, b):
        self.buffer.writebyte(b)


    def writestring(self, b):
        self.buffer.writestring(b)


    def writeint(self, b):
        self.buffer.writeint(b)


    def writedouble(self, b):
        self.buffer.writedouble(b)


    def writefloat(self, b):
        self.buffer.writefloat(b)


    def writeshort(self, b):
        self.buffer.writeshort(b)


    def writeushort(self, b):
        self.buffer.writeushort(b)


    def readstring(self):
        return self.buffer.readstring()


    def readbyte(self):
        return self.buffer.readbyte()


    def readbit(self):
        return self.buffer.readbit()


    def readint(self):
        return self.buffer.readint()


    def readdouble(self):
        return self.buffer.readdouble()


    def readfloat(self):
        return self.buffer.readfloat()


    def readshort(self):
        return self.buffer.readshort()


    def readushort(self):
        return self.buffer.readushort()