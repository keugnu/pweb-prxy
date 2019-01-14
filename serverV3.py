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

	port = 8888
	sock = socket(AF_INET, SOCK_STREAM)
	sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	sock.bind((args.ipaddr, port))
	sock.listen(1)
	while True:
		print(f"Listening on... {args.ipaddr}:{port}")
		clsock, claddr = sock.accept()
		print(f"Received a connection from: {claddr}")
		message = clsock.recv(1024)
		request_type = message.split()[0]
		filename = message.decode().split()[1].partition("/")[2]

		try:
			with open(filename[1:-1], "r") as fh:
				output = fh.readlines()
			clsock.send("HTTP/1.0 200 OK\r\n".encode())
			clsock.send("Content-Type:text/html\r\n".encode())
			for data in output:
				clsock.send(data.encode())
			print("Served cached version")
			continue
		except IOError:
			print("Cache file does not exist")
		c = socket(AF_INET, SOCK_STREAM)
		hostn = filename.replace("www.", "", 1)[1:-1]
		print(f"Attepting connection to: {hostn}")
		
		c.connect((hostn, 80))
		fileobj = c.makefile('rwb', 0)
		print(vars(fileobj))
		subfile = filename.partition("/")[2]

		if request_type == 'GET':
			fileobj.write("".join(["GET ", "http://", hostn, "/", subfile, " HTTP/1.0\n\n"]).encode())
		else:
			fileobj.write("".join(["POST ", "http://", filename, " HTTP/1.0\n\n"]).encode())
			fileobj.write(re.split("\r\n", message.decode(), maxsplit=1)[1].encode())
		buf = fileobj.readlines()
		
		if buf[0].split()[1] == '404':
			print("Server Response: {}".format(buf[0].split('\n', 1)[0]))
		else:
			with open(filename[1:-1], "wb") as fh:
				for data in buf:
					fh.write(data)
					clsock.send(data)
				try:    
					print("Server Response: {}".format(buf[0].split('\n', 1)[0]))
				except Exception as e:
					print(e.__traceback__)

		clsock.close()
		c.close()
	
if __name__ == '__main__':
	main()
