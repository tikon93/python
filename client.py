import socket
import threading
import sys
UDP_IP = "127.0.0.1"
UDP_PORT = 9999
def send(e):
	while True:
		try:
			if not e.is_set():
				data=raw_input('')
				if data!=('exit'):
					sock.send(data+'\n')
				else:
					e.set()
					print('exiting line 15')
					break
			else:
				break
				print('exiting line 19')
		except:
			e.set()
			print('exiting line 21')
			break
def recv(e):
	while True:
		try:
			if not e.is_set():
				print(sock.recv(1024))
			else:
				break
				print('exiting line 29')
		except:
			e.set()
			print('exiting line 34')
			break
exit=threading.Event()
sock = socket.socket() 
sock.connect((UDP_IP,UDP_PORT))
username=raw_input('\nEnter username:')
sock.send(username)
s=threading.Thread(target=send,args=(exit,))
r=threading.Thread(target=recv,args=(exit,))
s.start()
r.start()

try:
	s.join()
	r.join()
finally:
	sock.shutdown(socket.SHUT_RDWR)
	sock.close()
	print('closing sock\n')
	sys.exit(0)


