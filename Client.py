import struct, threading, socket, bcrypt, time

from NetworkConstants import receive_codes, send_codes, handshake_codes
from Network import *
import Network
import User


class Client(threading.Thread):
	def __init__(self, connection, address, server, pid):
		threading.Thread.__init__(self)

		self.connection = connection  # Connection Information
		self.address = address  # Client Address Properties
		self.server = server  # Reference to main server
		self.connected = True  # Connection status
		self.handshake = handshake_codes['UNKNOWN']  # Handshake status defaulted to unknown
		self.user = None  # Clients each have a user for the game
		self.pid = pid
		self.id = -1
		self.username = ""
		self.buffer = Network.Buff()

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

	def run(self):
		# Wait for handshake to complete before reading any data
		self.wait_for_handshake()
		# Handshake complete so execute main data read loop
		while self.connected:
			if self.user != None:
				if self.user.lastPing >= 1:
					self.disconnect_user()

			try:
				# Receive data from clients
				self.buffer.Buffer = self.connection.recv(1024)
				self.buffer.BufferO = self.buffer.Buffer

				while (len(self.buffer.Buffer)) > 0:
					packet_size = len(self.buffer.Buffer)

					msg_size = self.readushort()  # read the header

					# If we have not gotten enough data, keep receiving until we have
					while (len(self.buffer.Buffer) + 2 < msg_size):
						self.buffer.Buffer += self.connection.recv(1024)
						packet_size = len(self.buffer.Buffer) + 2
					self.handlepacket()

					# pop the remaining data in the packet
					while ((packet_size - len(self.buffer.Buffer)) < msg_size):
						self.readbyte()



			except ConnectionError:
				self.disconnect_user()

	def handlepacket(self):
		event_id = self.readbyte()

		if event_id == receive_codes['PING']:
			self.case_message_ping()
		elif event_id == receive_codes['DISCONNECT']:
			self.case_message_player_leave()
		elif event_id == receive_codes["REGISTER"]:
			self.case_message_player_register()
		elif event_id == receive_codes["LOGIN"]:
			self.case_messasge_player_login()
		elif event_id == receive_codes["MOVE"]:
			self.case_message_player_move()
		elif event_id == receive_codes["CHAT"]:
			self.case_message_player_chat()
		elif event_id == receive_codes["HP"]:
			self.case_message_player_hp()
		elif event_id == receive_codes["SHOOT"]:
			self.case_message_player_shoot()
		elif event_id == receive_codes["AIM"]:
			self.case_message_player_aim()
		elif event_id == receive_codes["ENT_DELETE"]:
			self.case_message_ent_delete()
		elif event_id == receive_codes["PLAYER_WEAPON_SWITCH"]:
			self.case_message_player_weapon_switch()
		elif event_id == receive_codes["UNLOCK_WEAPON"]:
			self.case_message_unlock_weapon()
		elif event_id == receive_codes["RECORD_KILLS"]:
			self.case_message_record_kills()

	# EVENTS ###############################################

	def case_message_ent_delete(self):
		eid = self.readbyte()

		# check if index exists first!
		list = self.server.entityMaster.entities

		for e in list:
			if e.eid == eid:
				self.server.entityMaster.entities.remove(e)

		self.clearbuffer()
		self.writebyte(send_codes["ENT_DELETE"])
		self.writebyte(eid)
		self.sendmessage_other()

	def case_message_player_chat(self):
		chat = self.readstring()
		# send to everyone
		self.clearbuffer()
		self.writebyte(send_codes["CHAT"])
		self.writebyte(self.pid)
		self.writestring(chat)
		self.sendmessage_all()

	def case_message_ping(self):

		# Move to separate, PLAYER JUST ENTERETED NEW ROOM event
		eMaster = self.server.entityMaster
		for e in eMaster.entities:
			eMaster.send_entity_create(e.eid, e.name, e.x, e.y)

		time = self.readint()

		if self.user != None:
			self.user.lastPing = 0

		self.clearbuffer()
		self.writebyte(send_codes["PING"])
		self.writeint(time)
		self.sendmessage()

	def case_messasge_player_login(self):
		username = self.readstring()
		password = self.readstring()

		login = True
		login_msg = ""

		# Check if correct username+password
		result = self.server.sql("SELECT * FROM users_creds WHERE username=?", (username,))
		if result == None:
			login = False
			login_msg = "Invalid username or password"
		if login:
			pwd = result["password"]
			if not bcrypt.checkpw(password.encode('utf8'), pwd):
				login = False
				login_msg = "Invalid username or password"

		# Check if they are already logged in
		for c in self.server.clients:
			if c.user != None and c.user.username == username:
				login = False
				login_msg = "You are already logged in!"

		# x = 0
		# y = 0
		# hp = 75

		self.clearbuffer()
		self.writebyte(send_codes["LOGIN"])
		self.writebit(login)

		# ini current client
		if login:
			user_data = self.server.sql("SELECT * FROM users_stats WHERE id=?", (result["id"],))

			self.writestring(username)
			self.writebyte(self.pid)
			self.id = user_data["id"]
			x = user_data["x"]
			y = user_data["y"]
			recordKills = user_data["recordKills"]
			hp = user_data["hp"]
			curWeapon = user_data["curWeapon"]
			w1unlock = user_data["w1unlock"]
			w2unlock = user_data["w2unlock"]
			self.writedouble(x)
			self.writedouble(y)
			self.writeint(recordKills)
			self.writeint(hp)
			self.writebyte(curWeapon)
			self.writebyte(w1unlock)
			self.writebyte(w2unlock)
			print("{0} logged in from {1}:{2}".format(username, self.address[0], self.address[1]))
			self.username = username
		else:
			self.writestring(login_msg)
		self.sendmessage()

		if login:
			self.user = User.User(x, y, hp, username, self)
			self.user.start()

			# Send new client info to other clients
			self.clearbuffer()
			self.writebyte(send_codes["JOIN"])
			self.writebyte(self.pid)
			self.writestring(self.username)
			self.writedouble(x)
			self.writedouble(y)
			self.writeint(recordKills)
			self.writeint(hp)
			self.writebyte(curWeapon)
			self.writebit(True)
			self.sendmessage_other()

			# time.sleep(1)
			# Get data from all other clients
			for c in self.server.clients:
				if id(c) != id(self) and c.user != None:
					self.clearbuffer()
					self.writebyte(send_codes["JOIN"])
					self.writebyte(c.pid)
					self.writestring(c.username)
					self.writedouble(c.user.x)
					self.writedouble(c.user.y)
					self.writeint(c.user.recordKills)
					self.writeint(c.user.hp)
					self.writebyte(c.user.curWeapon)
					self.writebit(False)
					self.sendmessage(buff=self.buffer)

	def case_message_player_register(self):
		username = self.readstring()
		password = self.readstring()
		result = self.server.sql("SELECT * FROM users_creds WHERE username=?;", (username,))
		if result == None:
			password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
			self.server.sql("INSERT INTO users_creds (username,password) VALUES(?,?)", (username, password))
			result = self.server.sql("SELECT * FROM users_creds WHERE username=?;", (username,))
			self.server.sql("INSERT INTO users_stats(id) VALUES(?)", (result["id"],))
			self.clearbuffer()
			self.writebyte(send_codes["REGISTER"])
			self.writebit(True)
			self.writestring(username)
			self.sendmessage()
			print("{0} registered from {1}:{2}".format(username, self.address[0], self.address[1]))
		else:
			self.clearbuffer()
			self.writebyte(send_codes["REGISTER"])
			self.writebit(False)
			self.writestring("There is already an account by that name")
			self.sendmessage()

	def case_message_player_move(self):
		# self.user.inputs=[self.readbit(),self.readbit(),self.readbit(),self.readbit()]
		self.user.x = self.readdouble()
		self.user.y = self.readdouble()
		self.user.hsp = self.readfloat()
		self.user.vsp = self.readfloat()

		# forward to other clients
		self.clearbuffer()
		self.writebyte(send_codes["MOVE"])
		self.writebyte(self.pid)
		self.writefloat(self.user.hsp)
		self.writefloat(self.user.vsp)
		# self.writebit(self.user.inputs[0])
		# self.writebit(self.user.inputs[1])
		# self.writebit(self.user.inputs[2])
		# self.writebit(self.user.inputs[3])
		self.writedouble(self.user.x)
		self.writedouble(self.user.y)
		self.sendmessage_other()

	def case_message_player_hp(self):
		self.user.hp = self.readint()

		self.clearbuffer()
		self.writebyte(send_codes["HP"])
		self.writebyte(self.pid)
		self.writeint(self.user.hp)
		self.sendmessage_other()

	def case_message_player_shoot(self):
		self.clearbuffer()
		self.writebyte(send_codes["SHOOT"])
		self.writebyte(self.pid)
		self.sendmessage_other()

	def case_message_unlock_weapon(self):
		whatWeapon = self.readbyte()
		whatStatus = self.readbyte()

		if whatWeapon == 2:
			self.user.w2unlock = whatStatus

	def case_message_record_kills(self):
		record = self.readint()
		self.user.recordKills = record

		self.clearbuffer()
		self.writebyte(send_codes["RECORD_KILLS"])
		self.writebyte(self.pid)
		self.writeint(record)
		self.sendmessage_other()

	def case_message_player_weapon_switch(self):
		self.user.curWeapon = self.readbyte()

		self.clearbuffer()
		self.writebyte(send_codes["PLAYER_WEAPON_SWITCH"])
		self.writebyte(self.pid)
		self.writebyte(self.user.curWeapon)
		self.sendmessage_other()

	def case_message_player_aim(self):
		aim = self.readint()

		self.clearbuffer()
		self.writebyte(send_codes["AIM"])
		self.writebyte(self.pid)
		self.writeint(aim)
		self.sendmessage_other()

	def case_message_player_leave(self):
		self.disconnect_user()

	# OTHER

	def wait_for_handshake(self):
		"""
			Wait for the handshake to complete before reading any other information
			TODO: Add better implementation for handshake
		"""

		while self.connected and self.handshake != handshake_codes["COMPLETED"]:

			if self.handshake == handshake_codes['UNKNOWN']:
				# First send message to client letting them know we are engaging in a handshake
				self.clearbuffer()
				self.writebyte(receive_codes['HANDSHAKE'])
				self.sendmessage()

				self.handshake = handshake_codes['WAITING_ACK']

			else:
				# Wait for handshake ack
				self.buffer.Buffer = self.connection.recv(1024)
				self.readushort()  # packet header
				event_id = self.readbyte()
				# event_id = struct.unpack('B', data[:2])[0]

				if event_id == receive_codes['HANDSHAKE']:
					# Received handshake successfully from client
					self.handshake = handshake_codes['COMPLETED']
					print("Handshake with {0} complete...".format(self.address[0]))

	def disconnect_user(self):
		"""
			Removes the user from the server after disconnection
		"""
		print("Disconnected from {0}:{1}".format(self.address[0], self.address[1]))

		# save into db
		if self.user != None:
			self.server.sql("UPDATE users_stats SET x=?, y=?, hp=?, curWeapon=?, w1unlock=?, w2unlock=?, recordKills=? WHERE id=?",
							(self.user.x, self.user.y, self.user.hp, self.user.curWeapon, self.user.w1unlock,
							 self.user.w2unlock, self.user.recordKills,self.id))
			self.server.sql("COMMIT")

		self.connected = False

		if self in self.server.clients:
			self.server.clients.remove(self)
			if self.user != None:
				self.user.Running = False
				# forward to other clients
				self.clearbuffer()
				self.writebyte(send_codes["LEAVE"])
				self.writebyte(self.pid)
				self.sendmessage_other()

	def kick_user(self):
		self.clearbuffer()
		self.writebyte(send_codes["CLOSE"])
		self.writestring("You have been kicked")
		self.sendmessage()
		self.disconnect_user()

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
