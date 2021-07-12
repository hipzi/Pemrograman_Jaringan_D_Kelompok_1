from socket import *
import socket
import time
import sys
import threading
import logging


class BackendList:
	def __init__(self):
		self.servers=[]
		self.servers.append(('192.168.122.134',9002))
		self.servers.append(('192.168.122.134',9003))
		self.servers.append(('192.168.122.134',9004))
		self.servers.append(('192.168.122.134',9005))
		self.servers.append(('192.168.122.134',9005))
		self.current=0
	def getserver(self):
		s = self.servers[self.current]
		self.current=self.current+1
		if (self.current>=len(self.servers)):
			self.current=0
		return s


class Backend(threading.Thread):
	def __init__(self,targetaddress):
		# logging.warning("hipzi")
		self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.my_socket.connect(targetaddress)
		threading.Thread.__init__(self)

	def run(self):
		try:
			self.my_socket.sendall(self.recv(8192))
		except:
			pass
		# logging.warning("socket open {}" . format(cli.fileno()))
		self.close()
		self.my_socket.close()
		# logging.warning("socket close {}" . format(cli.fileno()))

class ProcessTheClient(threading.Thread):
	logging.warning("zahra")
	def __init__(self, connection, address):
		self.connection = connection
		self.address = address
		threading.Thread.__init__(self)

	def run(self):
		data = self.connection.recv(8192)
		if data:
			# self.connection = self
			logging.warning("masuk ga?")
			self.connection.send(data)
			# self.backend.connection.sendall(data)
		else:
			logging.warning("e e eee")
		# logging.warning("open socket? {}" . format(self.connection.fileno()))
		# self.connection.shutdown(socket.SHUT_RDWR)
		self.connection.close()
		# logging.warning("keluar ga? {}" . format(self.connection.fileno()))

class Server(threading.Thread):
	def __init__(self,portnumber):
		self.the_clients = []
		self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.my_socket.bind(('',portnumber))
		self.my_socket.listen(5)
		self.bservers = BackendList()
		threading.Thread.__init__(self)
		logging.warning("load balancer running on port {}" . format(portnumber))

	def run(self):
		while True:
			pair = self.my_socket.accept()
			if pair is not None:
				sock, addr = pair			
				logging.warning("connection from {}" . format(repr(addr)))

				#menentukan ke server mana request akan diteruskan
				bs = self.bservers.getserver()
				logging.warning("koneksi dari {} diteruskan ke {}" . format(addr, bs))
				backend = Backend(bs)

				clt = ProcessTheClient(sock, addr)
				logging.warning("sock {}".format(sock))
				logging.warning("addr {}".format(addr))
				clt.backend = backend
				# logging.warning("ini apa 1 {}" . format(bs))
				# logging.warning("ini apa 2 {}" . format(backend))
				# logging.warning("ini apa 3 {}" . format(clt.backend))
				clt.start()
				self.the_clients.append(clt)
				logging.warning("socket {}" . format(sock.fileno()))
				time.sleep(0.01)	
				sock.close()	
				# sock.shutdown(socket.SHUT_RDWR)
				logging.warning("close {}" . format(sock.fileno()))
				# time.sleep(0.5)
				# self.threads.append(clt)
				# logging.warning("ini apa 4 {}" . format(self.the_clients))
				# for clt in self.the_clients:

def main():
	portnumber=18000
	try:
		portnumber=int(sys.argv[1])
	except:
		pass
	svr = Server(portnumber)
	svr.start()

if __name__=="__main__":
	main()


