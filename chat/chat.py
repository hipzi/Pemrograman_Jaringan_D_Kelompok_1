import sys
import os
import json
import uuid
import logging
from queue import  Queue
from datetime import datetime

class Chat:
	def __init__(self):
		self.sessions={}
		self.users = {}
		self.group = {'username':[]}
		self.users['zahra']={ 'nama': 'Zahratul Millah', 'negara': 'Indonesia', 'password': 'malang', 'incoming' : {}, 'outgoing': {}}
		self.users['rofita']={ 'nama': 'Rofita Siti', 'negara': 'Indonesia', 'password': 'madiun', 'incoming' : {}, 'outgoing': {}}
		self.users['patrick']={ 'nama': 'Patrick', 'negara': 'Indonesia', 'password': 'jombang', 'incoming' : {}, 'outgoing': {}}
	def proses(self,data):
		j=data.split(" ")
		try:
			command=j[0].strip()
			if (command=='auth'):
				username=j[1].strip()
				password=j[2].strip()
				self.group['username'].append(username)
				return self.autentikasi_user(username,password)
			elif (command=='send'):
				sessionid = j[1].strip()
				usernameto = j[2].strip()
				message=""
				for w in j[3:]:
					message="{} {}" . format(message,w)
				usernamefrom = self.sessions[sessionid]['username']
				logging.warning("SEND: session {} send message from {} to {}" . format(sessionid, usernamefrom,usernameto))
				return self.send_message(sessionid,usernamefrom,usernameto,message)
			elif (command=='inbox'):
				sessionid = j[1].strip()
				username = self.sessions[sessionid]['username']
				logging.warning("INBOX: {}" . format(sessionid))
				return self.get_inbox(username)
			else:
				return {'status': 'ERROR', 'message': '**Protocol Tidak Benar'}
		except KeyError:
			return { 'status': 'ERROR', 'message' : 'Informasi tidak ditemukan'}
		except IndexError:
			return {'status': 'ERROR', 'message': '--Protocol Tidak Benar'}

	def autentikasi_user(self,username,password):
		if (username not in self.users):
			return { 'status': 'ERROR', 'message': 'User Tidak Ada' }
		if (self.users[username]['password']!= password):
			return { 'status': 'ERROR', 'message': 'Password Salah' }
		tokenid = str(uuid.uuid4()) 
		self.sessions[tokenid]={ 'username': username, 'userdetail':self.users[username]}
		return { 'status': 'OK', 'tokenid': tokenid }
	def get_user(self,username):
		if (username not in self.users):
			return False
		return self.users[username]
	def send_message(self,sessionid,username_from,username_dest,pesan):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		s_fr = self.get_user(username_from)

		if(username_dest == 'group'):
			for key in self.group['username']:
				if (key in self.users.keys()):
					s_to = self.get_user(key)
		
				if (s_fr==False or s_to==False):
					return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

				message = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': pesan, 'flag': 0 }
				outqueue_sender = s_fr['outgoing']
				inqueue_receiver = s_to['incoming']	

				try:	
					outqueue_sender[username_from].put(message)
				except KeyError:
					outqueue_sender[username_from]=Queue()
					outqueue_sender[username_from].put(message)
				try:
					inqueue_receiver[username_from].put(message)
				except KeyError:
					inqueue_receiver[username_from]=Queue()
					inqueue_receiver[username_from].put(message)
		else:
			s_to = self.get_user(username_dest)
		
			if (s_fr==False or s_to==False):
				return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

			message = { 'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': pesan, 'flag': 0 }
			outqueue_sender = s_fr['outgoing']
			inqueue_receiver = s_to['incoming']	

			try:	
				outqueue_sender[username_from].put(message)
			except KeyError:
				outqueue_sender[username_from]=Queue()
				outqueue_sender[username_from].put(message)
			try:
				inqueue_receiver[username_from].put(message)
			except KeyError:
				inqueue_receiver[username_from]=Queue()
				inqueue_receiver[username_from].put(message)
		return {'status': 'OK', 'message': 'Message Sent'}

	def send_file(self, sessionid, username_from, username_dest, filepath):
		if (sessionid not in self.sessions):
			return {'status': 'ERROR', 'message': 'Session Tidak Ditemukan'}
		s_fr = self.get_user(username_from)

		image = filepath
		with open(image, 'rb') as file:
			image_file = file.read()

		if (username_dest == 'group'):
			for key in self.group['username']:
				if (key in self.users.keys()):
					s_to = self.get_user(key)

				if (s_fr == False or s_to == False):
					return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

				message = {'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': image_file, 'flag': 1}
				outqueue_sender = s_fr['outgoing']
				inqueue_receiver = s_to['incoming']

				try:
					outqueue_sender[username_from].put(message)
				except KeyError:
					outqueue_sender[username_from] = Queue()
					outqueue_sender[username_from].put(message)
				try:
					inqueue_receiver[username_from].put(message)
				except KeyError:
					inqueue_receiver[username_from] = Queue()
					inqueue_receiver[username_from].put(message)
		else:
			s_to = self.get_user(username_dest)

			if (s_fr == False or s_to == False):
				return {'status': 'ERROR', 'message': 'User Tidak Ditemukan'}

			message = {'msg_from': s_fr['nama'], 'msg_to': s_to['nama'], 'msg': image_file, 'flag': 1}
			outqueue_sender = s_fr['outgoing']
			inqueue_receiver = s_to['incoming']

			try:
				outqueue_sender[username_from].put(message)
			except KeyError:
				outqueue_sender[username_from] = Queue()
				outqueue_sender[username_from].put(message)
			try:
				inqueue_receiver[username_from].put(message)
			except KeyError:
				inqueue_receiver[username_from] = Queue()
				inqueue_receiver[username_from].put(message)
		return {'status': 'OK', 'message': 'Message Sent'}

	def get_inbox(self,username):
		s_fr = self.get_user(username)
		incoming = s_fr['incoming']
		msgs={}
		for users in incoming:
			msgs[users]=[]
			n=0
			while not incoming[users].empty():
				msgs[users].append(s_fr['incoming'][users].get_nowait())

				if (msgs[users][n]['flag'] == 1):
					print("Receiving File")
					print(msgs[users][n]['msg'])
					recv_image = 'pict_' + datetime.now().strftime("%H%M%S") + '.jpg'
					data = msgs[users][n]['msg']
					with open(recv_image, 'wb') as file:
						file.write(data)
					print("File Received")

				n = n + 1

		for name in msgs.keys():
			pengirim = name

		return {'status': 'OK', 'messages': msgs}

if __name__=="__main__":
	j = Chat()
	#logging.warning("GROUP: {} {}" . format(j.group['username'], len(j.group['username']) ))
	sesi = j.proses("auth patrick jombang")
	sesi = j.proses("auth zahra malang")
	sesi = j.proses("auth rofita madiun")
	logging.warning("GROUP: {} {}" . format(j.group['username'], len(j.group['username']) ))
	# list = j.print_group()
	#list = j.init(self.users)
	#print(sesi)
	# print(list)
	#sesi = j.autentikasi_user('messi','surabaya')
	#print sesi
	tokenid = sesi['tokenid']
	#print(j.proses("send {} messi hello gimana kabarnya zah " . format(tokenid)))
	#print(j.proses("send {} zahra hello gimana kabarnya mes " . format(tokenid)))

	#send_message(sessionid,usernamefrom,usernameto,message)
	pc = j.send_message(tokenid,'rofita','rofita','rooop')
	send = j.send_message(tokenid,'rofita','group','halo rek, semangat2! progjar ez :)')
	print(send)
	print(pc)
	#print j.send_message(tokenid,'zahra','messi','hello mes')
	#print j.send_message(tokenid,'lineker','messi','hello si dari lineker')

	print(j.send_file(tokenid,'rofita','zahra','hello.jpg'))
	print(j.send_file(tokenid,'rofita','patrick','hello.jpg'))
	print(j.send_file(tokenid,'rofita','zahra','hi.jpg'))

	print("isi mailbox dari zahra")
	print(j.get_inbox('zahra'))
	# print("isi mailbox dari rofita")
	# print(j.get_inbox('rofita'))
	print("isi mailbox dari patrick")
	print(j.get_inbox('patrick'))
















