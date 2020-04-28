import time,threading


class User(threading.Thread):

	def __init__(self, x, y, hp, username,client):
		threading.Thread.__init__(self)
		self.client = client
		self.x = x
		self.y = y
		self.username = username
		self.step = 0
		self.Running=True
		self.inputs = [0, 0, 0, 0] # left,right,up,down
		self.hp = hp
		self.hsp = 0
		self.vsp = 0
		self.lastPing = 0
		self.curWeapon = 0
		self.w1unlock = 1
		self.w2unlock = 0
		self.recordKills = 0

	def run(self):
		while self.Running:
			self.lastPing += 0.01



			start_time = time.time()
			self.move()

			self.step += 1
			end_time = time.time()

			time.sleep(max(.01666-(end_time-start_time), 0))  # Go at 60 steps/second

	def move(self):
		self.x += self.hsp
		self.y += self.vsp
		#if self.inputs[0]:
			#self.x -= hsp;
		#if self.inputs[1]:
			#self.x += speed
		#if self.inputs[2]:
		#	self.y -= speed
		#if self.inputs[3]:
			#self.y += speed




