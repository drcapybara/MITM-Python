#!/usr/bin/env python3

import socket
import ssl
import pprint
import threading

def process_request(ssock_for_browser):
	hostname = 'www.ray2021.com'

	cadir = './client-certs'

	# Set up the TLS context
	context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)  # For Ubuntu 20.04 VM
	# context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)      # For Ubuntu 16.04 VM

	context.load_verify_locations(capath=cadir)
	context.verify_mode = ssl.CERT_REQUIRED
	context.check_hostname = False

	# Make a connection to the real server
	sock_for_server = socket.create_connection((hostname, 443))
	ssock_for_server = context.wrap_socket(sock_for_server, server_hostname=hostname,
                            do_handshake_on_connect=False)
	
	print(ssock_for_server.getpeername())
	
	request = ssock_for_browser.recv(2048)
	
	if request:
		# Forward request to server
		ssock_for_server.sendall(request)
		print(request)
		# Get response from server, and forward it to browser
		response = ssock_for_server.recv(2048)
		while response:
			ssock_for_browser.sendall(response) # Forward to browser
			response = ssock_for_server.recv(2048)
	ssock_for_browser.shutdown(socket.SHUT_RDWR)
	ssock_for_browser.close()


sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock_listen.bind(('10.9.0.143', 443))
print('Binding to 10.9.0.143...')
print('Listening for TLS handshake...')
sock_listen.listen(5)

SERVER_CERT = './server-certs/server.crt'
SERVER_PRIVATE = './server-certs/server.key'


context_srv = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)  # For Ubuntu 20.04 VM
# context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)      # For Ubuntu 16.04 VM
context_srv.load_cert_chain(SERVER_CERT, SERVER_PRIVATE)


while True:
	sock_for_browser, fromaddr = sock_listen.accept()
	ssock_for_browser = context_srv.wrap_socket(sock_for_browser, server_side=True)
	x = threading.Thread(target=process_request, args=(ssock_for_browser,))
	x.start()
