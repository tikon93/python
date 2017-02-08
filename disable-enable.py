import time
import sys
import telnetlib
import re

DUT_IP=''
PROMPT='LTP'
serials={}

k=0
for i in sys.argv:
	if i == '-ip':
		DUT_IP = sys.argv[k+1]
	if i == '-d':
		DUT_TYPE = sys.argv[k+1]
	k+=1
def cleanup():
	tn.write('configure terminal\r')
	tn.read_until(PROMPT)
	tn.write('no interface ont 0-3/0-127\r')
	tn.read_until(PROMPT)
	tn.write('do commit\r')
	tn.read_until('config')
	tn.write('exit\r')
	tn.read_until(r'LTP-4X#')
	time.sleep(5)
	
def disable_all(channel_list, serial_list):
	for channel in channel_list:
		for serial in serial_list[channel]:
			tn.write('send ploam disable-sn mode disable ont serial '+serial+'\r')
			tn.read_until(PROMPT)
	for channel in channel_list:
		tn.write('show interface ont '+channel+' online\r')
		buf=tn.read_until(PROMPT)
		if re.match('OK',buf)==None:
			continue
		else:
			print('there is online ONT, disable not ok!')
			return(1)
	return(0)

def checkstate(id):
	tn.write('show interface ont '+id+' state\r')
	buf=tn.read_until(PROMPT)
	state=re.findall('State: *(\S*)',buf)
	return state

def config_all_ONT(channel_list):
	serial_list={}
	count = 0
	for channel in channel_list:
		tn.write('show interface ont '+channel+' unactivated\r')
		buf=tn.read_until(PROMPT)
		serial_list[channel]=(re.findall('ELTX\w{8}',buf))
	tn.write('configure terminal\r')
	tn.read_until(PROMPT)
	for channel in channel_list:
		index=0
		for serial in serial_list[channel]:
			tn.write('interface ont '+channel+'/'+str(index)+'\r')
			tn.read_until(PROMPT)
			tn.write('serial '+serial+'\r')
			tn.read_until(PROMPT)
			tn.write('exit\r')
			tn.read_until(PROMPT)
			index+=1
			count+=1
	tn.write('do commit\r')
	tn.read_until(PROMPT)
	tn.write('exit\r')
	tn.read_until(PROMPT)
	time.sleep(20)
	tn.write('show interface ont '+channel_list[0]+'-'+channel_list[-1]+' online\r')
	buf=tn.read_until(PROMPT)
	if len(re.findall('ELTX\w{8}',buf))==count:
		return serial_list
	else:
		return 1
	
if DUT_TYPE=='4':
	channel_list=['0', '1']
elif DUT_TYPE=='8':
	channel_list==['0','4']
else:
	print('incorrect board type, must be 4 or 8\n')
	sys.exit(1)
if DUT_IP=='':
	print('Error! You have to specify DUT IP. Use -ip <value> for it.\n')
	sys.exit(1)
elif re.match('[1-2]?[0-9]?[0-9]\.[1-2]?[0-9]?[0-9]\.[1-2]?[0-9]?[0-9]\.[1-2]?[0-9]?[0-9]$',DUT_IP)==None:
	print('Incorrect DUT IP address format. Check it.\n')
	sys.exit(1)	

tn=telnetlib.Telnet(DUT_IP,timeout=240)
tn.read_until('login:')
tn.write('admin\r')
tn.read_until('assword:')
tn.write('password\r')
tn.read_until('#')

cleanup()

serials=config_all_ONT(channel_list)
if serials==1:
	print('couldnt config ONT\n')
	sys.exit(1)

if disable_all(channel_list,serials)==0:
	tn.write('send ploam disable-sn mode enable ont 0/0\r')
	tn.read_until(PROMPT)
	time.sleep(5)
	if checkstate('0/0')!='DISABLED':
		print('enable by id is ok\n')
	else:
		print('enable by id is not ok\n')
	
	tn.write('send ploam disable-sn mode enable-all gpon-port '+channel_list[1]+'\r')
	tn.read_until(PROMPT)
	time.sleep(5)
	for serial in serials[channel_list[1]]:
		if checkstate(serial)!='DISABLED':
			continue
		else:
			print(serial+' not enabled after enable-all on channel!\n')

if disable_all(channel_list,serials)==0:
	tn.write('send ploam disable-sn mode enable-all\r')
	tn.read_until(PROMPT)
	time.sleep(5)
	for channel in channel_list:
		for serial in serials[channel]:
			if checkstate(serial)!='DISABLED':
				continue
			else:
				print(serial+' not enabled after global enable-all!\n')
				
sys.exit(1)
