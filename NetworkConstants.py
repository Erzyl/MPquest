from enum import Enum




receive_codes = {
    "PING": 0,
    "HANDSHAKE": 1,
    "DISCONNECT": 2,
    "REGISTER":3,
    "LOGIN":4,
    "MOVE":5,
    "CHAT":6,
    "HP":7,
    "SHOOT":8,
    "AIM":9,
    "ENT_DELETE":10,
    "PLAYER_WEAPON_SWITCH":11,
    "UNLOCK_WEAPON":12,
    "RECORD_KILLS":13,
}

send_codes = {
	"PING":0,
    "REGISTER":3,
	"LOGIN":4,
	"MOVE":5,
	"JOIN":6,
	"LEAVE":7,
    "CHAT":8,
    "CLOSE":9,
    "HP": 10,
    "SHOOT":11,
    "AIM":12,
    "ENT_CREATE":13,
    "ENT_DELETE":14,
    "PLAYER_WEAPON_SWITCH":15,
    "RECORD_KILLS":16,
}


handshake_codes = {
    "UNKNOWN": 0,
    "WAITING_ACK": 1,
    "COMPLETED": 2
}

