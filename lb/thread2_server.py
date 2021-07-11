import socket
import time
import sys
import threading
import logging
from http import HttpServer

httpserver = HttpServer()
rcv = ""

class ProcessTheClient(threading.Thread):
	def __init__(self, connection, address):
		self.connection = connection
		self.address = address
		threading.Thread.__init__(self)

	def run(self):
		rcv=""
		while True:
			try:
				data = self.connection.recv(32)
				if data:
					#merubah input dari socket (berupa bytes) ke dalam string
					#agar bisa mendeteksi \r\n
					d = data.decode()
					rcv=rcv+d
					if rcv[-2:]=='\r\n':
						#end of command, proses string
						logging.warning("data dari client: {}" . format(rcv))
						hasil = httpserver.proses(rcv)
						#hasil akan berupa bytes
						#untuk bisa ditambahi dengan string, maka string harus di encode
						hasil=hasil+"\r\n\r\n".encode()
						logging.warning("balas ke  client: {}" . format(hasil))
						#hasil sudah dalam bentuk bytes
						self.connection.sendall(hasil)
						rcv=""
						self.connection.close()
				else:
					break
			except OSError as e:
				pass
		self.connection.close()

class Server(threading.Thread):
	def __init__(self,portnumber):
		self.the_clients = []        
		# asyncore.dispatcher.__init__(self)
		self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.my_socket.bind(('',portnumber))
		self.my_socket.listen(5)
		logging.warning("running on port {}" . format(portnumber))
		threading.Thread.__init__(self)

	def run(self):
		# logging.warning("zahra")
		while True:
			# self.connection, self.client_address = self.my_socket.accept()
			# logging.warning("connection from {}".format(self.client_address))
			pair = self.my_socket.accept()
			sock, addr = pair
			logging.warning("connection from {}".format(addr))
			logging.warning("sock {}".format(sock))
			logging.warning("addr {}".format(addr))

			clt = ProcessTheClient(sock, addr)
			clt.start()
			self.the_clients.append(clt)    

	# def run_accept(self):
	# 	pair = self.my_socket.accept()
	# 	if pair is not None:
	# 		sock, addr = pair
	# 		logging.warning("connection from {}" . format(repr(addr)))
			
	# 		clt = ProcessTheClient(sock)
	# 		clt.start()
	# 		self.the_clients.append(clt)


def main():
	portnumber=9002
	try:
		portnumber=int(sys.argv[1])
	except:
		pass
	svr = Server(portnumber)
	svr.start()

if __name__=="__main__":
	main()
