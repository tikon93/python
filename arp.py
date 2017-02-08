from scapy.all import *


p=rdpcap("test1.pcap")
print_user('done')
for i in p:
	if p[i].getlayer(Ether).type == '2054':
		print(i)
	print('tick')


i = 0
start = 0
stop = 0
join = []
for pack in p:
   if (pack.load[0]=='\x11')&(pack.load[4:8]=='\x00\x00\x00\x00') :
      print('GQ at'+str(i))
      stop = i
      k = 1
      while start<stop:
         if p[start].load[0] == '\x16':
            join.append(ord(p[start].load[7]))
         start+=1
      while k <=100:
         if k in join:
            k += 1
         else:
            print('no join for '+str(k)+' group in resp for GQ'+str(stop))
            k=101
      join = []
   i += 1







   'no join for'+k+'group in resp for GQ'+stop