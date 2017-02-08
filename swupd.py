import telnetlib
import sys
import re
import time

PROMPT='LTP'
check_downgrade=False
check_personal_mode=False
TFTP_IP='192.168.16.40'
eq_id='NTU-2W'
filename_up=''
filename_down=''
DUT_IP=''
serial=None
k=0

def check_upd():
	tn.write('do show interface ont '+chan+r'/0 state'+'\r')
    buf=tn.read_until(PROMPT)
	print('in func\n')
	print(buf)
    if re.search('FWUPDATING', buf)!=None:
        return 1
	else:
		return 0
	

for i in sys.argv:
	if i == '-ip':
		DUT_IP = sys.argv[k+1]	
	elif i == '-d':
		check_downgrade=sys.argv[k+1]
	elif i == '-p':
		check_personal_rule=sys.argv[k+1]
	elif i == '-t':
        TFTP_IP=sys.argv[k+1]
    elif i == '-uf':
        filename_up=sys.argv[k+1]
    elif i == '-df':
        filename_down=sys.argv[k+1]
	
	k+=1
if DUT_IP=='':
	print('Error! You have to specify DUT IP. Use -ip <value> for it.\n')
	sys.exit(1)
elif re.match('[1-2]?[0-9]?[0-9]\.[1-2]?[0-9]?[0-9]\.[1-2]?[0-9]?[0-9]\.[1-2]?[0-9]?[0-9]$',DUT_IP)==None:
	print('Incorrect DUT IP address format. Check it.\n')
	sys.exit(1)
elif re.match('[1-2]?[0-9]?[0-9]\.[1-2]?[0-9]?[0-9]\.[1-2]?[0-9]?[0-9]\.[1-2]?[0-9]?[0-9]$',TFTP_IP)==None:
    print('Incorrect TFTP IP address format. Check it.\n')
    sys.exit(1)

else:
	print('Start test for IP '+DUT_IP+'\n')



tn = telnetlib.Telnet(DUT_IP,timeout=240)
print(tn.read_until('login:'))
tn.write('admin\r')
print(tn.read_until('assword:'))
tn.write('password\r')
tn.read_until('LTP-4X#')



#check is there files or not
#first download file for upgrade
#and if set flag - for downgrade

tn.write('show firmware ont\r')
fw=tn.read_until(PROMPT)



if re.search(filename_up, fw)==None:
	tn.write('copy tftp://'+TFTP_IP+'/'+filename_up+' fs://ont-firmware\r')
	tn.read_until(PROMPT)
else:
	print('skip')
if re.search(filename_down, fw)==None:
	tn.write('copy tftp://'+TFTP_IP+'/'+filename_down+' fs://ont-firmware\r')
	tn.read_until(PROMPT)
else:
    print('skip')

# delete all ONT
tn.write('configure terminal\r')
tn.read_until(PROMPT)
tn.write('no interface ont 0-3/0-127\r')
tn.read_until(PROMPT)
tn.write('do commit\r')
tn.read_until('config')
tn.write('exit\r')
tn.read_until(r'LTP-4X#')
time.sleep(10)
#add connected ONT
for i in range(0,4):
	tn.write('show interface ont '+str(i)+' unactivated\r')
	buf=tn.read_until(PROMPT) 
	result=re.search('ELTX\w{8}',buf)
	if result!=None:
		serial=result.group(0)
		chan=str(i)
		break
	else:
		result=re.search('454C5458\w{8}',buf)
		if result!=None:
			serial=result.group(0)
			chan=str(i)
            break

if serial!=None:
	tn.write('configure terminal\r')
	tn.read_until(PROMPT)
	tn.write('interface ont '+chan+'/0'+'\r')
    tn.read_until(PROMPT)
	tn.write('serial '+ serial+'\r')
	tn.read_until(PROMPT)
	tn.write('do commit\r')
    tn.read_until('LTP-4X(config')
else:
	print('No ONT connected to DUT, aborting\n')
	sys.exit(1)
time.sleep(10)

print('setup done\n')
#update ONT for lower version and test manual update

up_version=re.search('3\.[0-9]{2}\.[0-9]\.[0-9]+',filename_up)
up_version=up_version.group(0)

down_version=re.search('3\.[0-9]{2}\.[0-9]\.[0-9]+',filename_down)
down_version=down_version.group(0)

tn.write('do show interface ont ' +chan+'/0 state'+'\r')
buf=tn.read_until('config')
cur_version=re.search('3\.[0-9]{2}\.[0-9]\.[0-9]+',buf)
cur_version=cur_version.group(0)
if cur_version==up_version:
	filename_up,filename_down=filename_down, filename_up
tn.write('do update ont '+chan+'/0'+' filename '+filename_up+'\r')
tn.read_until(PROMPT)
print('start manual upd\n')
k=0

while k<5:
	if check_upd()==1:
		print('manual upd started\n')
		break
	else:
		time.sleep(100)
		k+=1
else:
	print('smth wrong, check manual update!\n')
	sys.exit(1)

time.sleep(900)

while check_upd()==1:
	print('manual upd not finished yet!\n')
	time.sleep(600)

tn.write('do show interface ont '+chan+'/0 state\r')
buf=tn.read_until(PROMPT)
cur_version=re.search('3\.[0-9]{2}\.[0-9]\.[0-9]+',buf)
cur_version=cur_version.group(0)

if cur_version!=up_version:
	print('version not changed, check manual update!\r')
	sys.exit(1)
else:
	print('manual ok\n')
	
#check if downgrade flag works (default - disabled)

print('start autoupdate test')
tn.write('exit\r')
tn.read_until(PROMPT)
tn.write('auto-update ont record autotest equipment-id '+eq_id+' fw-version not-match '+down_version+' filename '+filename_down+' postpone\r')
tn.read_until(PROMPT)

tn.write('do reconfigure interface ont '+chan+'/0\r')
tn.read_until(PROMPT)
k=0

while k<10:
        if check_upd()==1:
            print('dongrade is disabled but update process started!\n')
            sys.exit(1)            
        else:
            time.sleep(100)
            k+=1

else:
	print('downgrade flag ok!- update not started\n')
tn.write('no auto-update ont record autotest\r')
print(tn.read_until(PROMPT))

#check auto-update with downgrade in postpone mode

tn.write('auto-update ont record autotest equipment-id '+eq_id+' fw-version not-match '+down_version+' filename '+filename_down+' postpone downgrade enable\r')
tn.read_until(PROMPT)

k=0
while k<10:
    if check_upd()==1:
		print('update started without reconf in postpone mode!\n')
		sys.exit(1)
    else:
        time.sleep(100)
        k+=1

print('reconf to start update in postpone mode\n')
tn.write('do reconfigure interface ont '+chan+'/0\r')
tn.read_until(PROMPT)

k=0
while k<5:
	if check_upd()==1:
		print('postpone downgrade update process started!\n')
        break
    else:
        time.sleep(100)
        k+=1
else:
    print('update in postpone mode is broken!\n')
    sys.exit(1)

time.sleep(900)

while check_upd()==1:
	print('update not finisshed yet!\n')
	time.sleep(600)

tn.write('do show interface ont '+chan+'/0 state\r')
buf=tn.read_until(PROMPT)
cur_version=re.search('3\.[0-9]{2}\.[0-9]\.[0-9]+',buf)
cur_version=cur_version.group(0)
if cur_version!= down_version:
    print('version not changed, check downgrade postpone!\n')
    sys.exit(1)
else:
	print('downgrade postpone ok\n')

tn.write('no auto-update ont record autotest\r')
tn.read_until(PROMPT)

#check auto-update immediate 
tn.write('auto-update ont record autotest equipment-id '+eq_id+' fw-version not-match '+up_version+' filename '+filename_up+' immediate\r')
tn.read_until(PROMPT)


k=0
while k<10:
    if check_upd()==1:
        print('update process started in immediate mode!\n')
		break
    else:
        time.sleep(100)
        k+=1

else:
    print('update in immediate mode did not started!\n')
    sys.exit(1)

time.sleep(600)

if check_upd()==0:
    tn.write('do show interface ont '+chan+'/0 state\r')
    buf=tn.read_until(PROMPT)
    cur_version=re.search('3\.[0-9]{2}\.[0-9]\.[0-9]+',buf)
    cur_version=cur_version.group(0)
    if cur_version!= up_version:
        print('version not changed, check auto update immediate!\n')
        sys.exit(1)
    else:
        print('immediate ok\n')
else:
    print('update not finisshed!\n')
		
tn.write('no auto-update ont record autotest\r')
tn.read_until(PROMPT)
