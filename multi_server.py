import socket
import threading


def client_interact(sock, list):
	username=sock.recv(1024)
	while True:
		data=sock.recv(1024)
		for i in list:
			if i!=sock:
				i.send(username+': '+data+'\n')
				
list_socks=[]
list_threads=[]
BIND_IP='127.0.0.1'
BIND_PORT=9999
sock=socket.socket()
sock.bind((BIND_IP,BIND_PORT))
print('bind')
sock.listen(4)
print('listen')

while True:
	try:
		newsock,addr = sock.accept()
		list_socks.append(newsock)
		newthread=threading.Thread(target=client_interact,args=(newsock,list_socks))
		list_threads.append(newthread)
		newthread.start()
	except:
		sock.shutdown(socket.SHUT_RDWR)
		sock.close()