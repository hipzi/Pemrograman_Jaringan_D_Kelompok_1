from socket import *
import socket
import threading
import time
import sys
import logging
import os.path
from datetime import datetime
from urllib.parse import unquote
import re

class ReverseProxy:
	def __init__(self):
		self.url_list = {}
		self.url_list['/images/']=("localhost", 8888)
		self.url_list['/pdf/']=("localhost", 8887)
		self.main_server = ("localhost", 8889)

	def proses(self,data):
		data_response={}
		requests = data.split("\r\n")
		baris = requests[0]

		all_headers = [n for n in requests[1:] if n!='']
		j = baris.split(" ")
		method=j[0].upper().strip()
		url_address = j[1].strip()
		if(url_address[-1] != '/'):
			data = data.replace(url_address, url_address+'/')
			url_address += '/'

		for url, server in self.url_list.items() :
			re_match = re.match(url, url_address)
			if re_match :
				data_response['server'] = server
				#redirect ke default server
				data_response['request'] = data.replace(url, '/')
	
		if "server" not in data_response :
			data_response['server'] = self.main_server
			data_response['request'] = data
		
		return data_response

class ProcessTheClient(threading.Thread):
	def __init__(self, connection, address):
		self.connection = connection
		self.address = address
		threading.Thread.__init__(self)

	def run(self):
		rcv=""
		#reverseProxy=ReverseProxy()
		while True:
			try:
				data = self.connection.recv(8192)
				data = data.decode()
				self.destination_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				if data:
					data_response = ReverseProxy().proses(data)
					self.destination_sock.connect(data_response['server'])
					self.destination_sock.sendall(data_response['request'].encode())
					while(True):
						data_balasan = self.destination_sock.recv(32)
						if(data_balasan == ''):
							break
						self.connection.sendall(data_balasan)
					# logging.warning(data)
					# logging.warning(data_balasan)
				else:
					break
			except OSError as e:
				pass
		self.connection.close()



class Server(threading.Thread):
	def __init__(self):
		self.the_clients = []
		self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		threading.Thread.__init__(self)

	def run(self):
		self.my_socket.bind(('0.0.0.0', 18000))
		self.my_socket.listen(1)
		while True:
			self.connection, self.client_address = self.my_socket.accept()
			logging.warning("connection from {}".format(self.client_address))

			clt = ProcessTheClient(self.connection, self.client_address)
			clt.start()
			self.the_clients.append(clt)



def main():
	svr = Server()
	svr.start()

if __name__=="__main__":
	main()

