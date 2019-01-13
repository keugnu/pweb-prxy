#!/usr/bin/env python

import sys
import os
import re

from argparse import ArgumentParser
from socket import *


def getargs():
	parser = ArgumentParser(description='A caching web proxy written in python.')
	parser.add_argument('ipaddr', help='IP adrress of the proxy server')
	return parser.parse_args()


def main():
	args = getargs()
	print(args)

	# Create a server socket, bind it to a port and start listening
	port = 8888
	sock = socket(AF_INET, SOCK_STREAM)
	sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	# Fill in start.
	sock.bind((args.ipaddr, port)) # listening port 
	sock.listen(1)
	# Fill in end.
	while True:
		# Start receiving data from the client
		print(f"Listening on... {args.ipaddr}:{port}")
		clsock, claddr = sock.accept()
		print(f"Received a connection from: {claddr}")
		message = clsock.recv(1024)
		# print(message)
		# Extract the filename from the given message
		# print(message.split()[1])
		request_type = message.split()[0]
		filename = message.decode().split()[1].partition("/")[2]
		# file_exist = "false"
		# filename = filename

		try: # Check whether the file exist in the cache
			with open(filename[1:-1], "r") as fh:
				output = fh.readlines()
			# file_exist = "true"
			# ProxyServer finds a cache hit and generates a response message
			clsock.send("HTTP/1.0 200 OK\r\n".encode())
			clsock.send("Content-Type:text/html\r\n".encode())
			# Fill in start.
			for data in output:
				clsock.send(data.encode())
			# Fill in end.
			print("Served cached version")
			continue
		# Error handling for file not found in cache
		except IOError:
			print("Cache file does not exist")
		# Create a socket on the proxyserver
		# Fill in start.
		c = socket(AF_INET, SOCK_STREAM)
		# Fill in end.
		# print(filename)
		hostn = filename.replace("www.", "", 1)[1:-1]
		print(f"Attepting connection to: {hostn}")
		
		# Connect to the socket to port 80
		# Fill in start.
		c.connect((hostn, 80))
		# Fill in end.
		# Create a temporary file on this socket and ask port 80
		# for the file requested by the client
		fileobj = c.makefile('rwb', 0)
		print(vars(fileobj))
		subfile = filename.partition("/")[2]

		if request_type == 'GET':
			fileobj.write("".join(["GET ", "http://", hostn, "/", subfile, " HTTP/1.0\n\n"]).encode())
		else:
			fileobj.write("".join(["POST ", "http://", filename, " HTTP/1.0\n\n"]).encode())
			fileobj.write(re.split("\r\n", message.decode(), maxsplit=1)[1].encode())
		# Read the response into buffer
		# Fill in start.
		buf = fileobj.readlines()
		
		# HTTP response message for file not found
		if buf[0].split()[1] == '404':
			print("Server Response: {}".format(buf[0].split('\n', 1)[0]))
		# Fill in end.
		# Create a new file in the cache for the requested file.
		# Also send the response in the buffer to client socket
		# and the corresponding file in the cache
		else:
			with open(filename[1:-1], "wb") as fh:
		# Fill in start.
				for data in buf:
					fh.write(data)
					clsock.send(data)
				try:    
					print("Server Response: {}".format(buf[0].split('\n', 1)[0]))
				except Exception as e:
					print(e.__traceback__)
		# Fill in end.

		# Close the client and the server sockets
		clsock.close()
		# Fill in start.
		c.close()
	
if __name__ == '__main__':
	main()
