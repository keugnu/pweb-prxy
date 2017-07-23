from socket import *
import sys
import re

if len(sys.argv) <= 1:
    print 'Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server'
    sys.exit(2)
# Create a server socket, bind it to a port and start listening
tcpSerPort = 8888
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# Fill in start.
tcpSerSock.bind(("",tcpSerPort)) #listening port 
tcpSerSock.listen(1)
# Fill in end.
while 1:
	# Start receiving data from the client
	print 'Ready to serve...'
	tcpCliSock, addr = tcpSerSock.accept()
	print 'Received a connection from:', addr
	message = tcpCliSock.recv(1024) # added code
	print message
	# Extract the filename from the given message
	print message.split()[1]
	requestType = message.split()[0]
	filename = message.split()[1].partition("/")[2]
	fileExist = "false"
	filetouse = "/" + filename

	try: # Check whether the file exist in the cache
		f = open(filetouse[1:], "r")
		outputdata = f.readlines()
		fileExist = "true"
		# ProxyServer finds a cache hit and generates a response message
		tcpCliSock.send("HTTP/1.0 200 OK\r\n")
		tcpCliSock.send("Content-Type:text/html\r\n")
		# Fill in start.
		for data in outputdata:
			tcpCliSock.send(data)
		# Fill in end.
		print 'Read from cache'
		continue
	# Error handling for file not found in cache
	except IOError:
		print "Cache file does not exist"
	# Create a socket on the proxyserver
	# Fill in start.
	c = socket(AF_INET, SOCK_STREAM)
	# Fill in end.

	hostn = filename.replace("www.","",1).partition("/")[0]
	print 'going to connect to: ', hostn
	
	# Connect to the socket to port 80
	# Fill in start.
	c.connect((hostn,80))
	# Fill in end.
	# Create a temporary file on this socket and ask port 80
	#for the file requested by the client
	fileobj = c.makefile('r', 0)
	subfile = filename.partition("/")[2]

	if requestType == 'GET':
		fileobj.write("GET "+"http://" + hostn + "/" + subfile + " HTTP/1.0\n\n")
	else:
		fileobj.write("POST "+"http://" + filename + " HTTP/1.0\n\n")
		msg_body = re.split("\r\n",message, maxsplit=1)[1]
	#print "Message Body: ",msg_body
		fileobj.write(msg_body)
	# Read the response into buffer
	# Fill in start.
	tmpBuffer = fileobj.readlines()
	
	# HTTP response message for file not found
	if tmpBuffer[0].split()[1] == '404':
		print 'Server Response:',tmpBuffer[0].split("\n", 1)[0]
	# Fill in end.
	# Create a new file in the cache for the requested file.
	# Also send the response in the buffer to client socket
	# and the corresponding file in the cache
	else:
		tmpFile = open("./" + filename,"wb")
	# Fill in start.
		for data in tmpBuffer:
			tmpFile.write(data)
			tcpCliSock.send(data)
		tmpFile.close()
		try:    
			print 'Server Response:',tmpBuffer[0].split("\n", 1)[0]
			tmpBuffer = ""
		except Exception as e:
			print ""
	# Fill in end.

	# Close the client and the server sockets
	tcpCliSock.close()
	# Fill in start.
	c.close()
	
	# Fill in end.