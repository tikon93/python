import re
import socket
config={'pool':[ '192.168.1.60',
			   '192.168.1.61'
			   ],
		'router': '192.168.1.1',
		'mask':'255.255.255.0',
		'leasetime': '600'
}

bind_ip='192.168.1.1'
bind_port=67

byte_leasetime=[]
leasetime = int(config['leasetime'])
full_leasetime = '0' * (8-len(hex(leasetime).split('x')[1])) + hex(leasetime).split('x')[1]
ind=0
while ind<len(full_leasetime):
	byte_leasetime.append(full_leasetime[ind:ind+2])
	ind+=2
	
def getClientAddr(message_byte):
	return message_byte[28:34]
	
def getXID(message_byte)
	return message_byte[4:8]

def getAllOptions(message_byte):
	options={}
	ind=240
	while ind<len(message_byte):
		if message_byte[ind]!=255:
			option_length = message_byte[ind+1]
			options[message_byte[ind]] = message_byte[ind+2:ind+2+option_length]
			ind+=2+option_length
		else:
			return options
def stringToList(str, sep):
	ret=[]
	for s int str.split(sep):
		ret.append(int(s))
	return ret	
			
def createOffer(XID, ciaddr, options, byte_leasetime):
	offer = []
	offer.append(2)  #op
	offer.append(1)	#hw type
	offer.append(6)	#hw len
	offer.append(0)	#hops
	for  byte in XID:	#XID
		offer.append(byte)
	offer.append(0)	#seconds
	offer.append(0)
	offer.append(0)	#bootp flags
	offer.append(0)
	for byte in ciaddr:	#ciaddr
		offer.append(byte)
	for byte in pool[0]: #yiaddr
		offer.append(byte)
	for byte in range(4): #siaddr
		offer.append(byte)
	for byte in range(4): #giaddr
		offer.append(byte)
	for byte in options[61][1:]:	#chaddr
		offer.append(byte)
	for byte in range(10):	#chaddr padding
		offer.append(byte)
	for byte in range(64):	# hostname
		offer.append(byte)
	for byte in range(128):	# filename
		offer.append(byte)
	offer.append(99)	#Magic cookie
	offer.append(130)
	offer.append(83)
	offer.append(99)
		#start to fill options
	offer.append(53) #DHCP type Offer
	offer.append(1)
	offer.append(2)
	offer.append(54)	#serverip
	offer.append(4)
	for byte in stringToList(bind_ip) 
		offer.append(byte)
	offer.append(51)	#leasetime
	offer.append(4)
	for byte in byte_leasetime:
		offer.append(byte)
	offer.append(1)	#mask
	offer.append(4)
	for byte in stringToList(config['mask'],'.')
		offer.append(byte)
	offer.append(3)	#defgw
	offer.append(4)
	for byte in stringToList(config['mask'],'.')
		offer.append(byte)
	
	
	
	
	
	







message_byte=[]
message='01010600a07cefae00000000000000000000000000000000000000000022b050597100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000638253633501017401013d07010022b05059713204c0a801640c0f656c7465782d3165366635643330623c084d53465420352e30370b010f03062c2e2f1f21f92b2b02dc00ff'
k=0
while k<len(message):
	message_byte.append(int(message[k:k+2],16))
	k+=2

