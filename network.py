import logging
import subprocess
import re

def createSubInterface(dev, vlanid, **addr):
	#logging.debug('\n________________________\n\nstart func\n\n________________________')
	ip=''
	mac=''
	if len(addr) > 2:
		logging.error('More then four arg passed to createSubInterface()')
		return 0
	try:
		mac=addr['mac']
		if re.match('(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$',mac)==None:
			logging.error('Incorrect mac addr format')
			return 0
	except:
		logging.debug('use mac from parental interface')
	try:
		ip=addr['ip']
		if re.match('(?:[1-2]?[0-9]?[0-9]\.){3}[1-2]?[0-9]?[0-9]$',ip)==None:
			logging.error('Incorrect ip addr format')
			return 0
	except:
		logging.debug('create interface without ip')
	dev_name = dev+'_'+vlanid
	command_add = 'ip link add link '+dev+' name '+dev_name+' type vlan id '+vlanid  #add interface with dev_name
	try:
		subprocess.call(command_add, shell=True)
		logging.debug('created interface '+dev_name)
	except:
		logging.error("couldn't create interface"+dev_name)
		return 0		
	if ip!='':
		subprocess.call('ip addr add '+ip+' dev '+dev_name, shell=True)
		logging.debug('added ip '+ip+' to '+dev_name)
	if mac!='':
		subprocess.call('ip link set dev '+dev_name+' address '+mac, shell=True)
		logging.debug('set mac '+mac+' to '+dev_name)
	command_up = 'ip link set '+dev_name+' up'
	subprocess.call(command_up, shell=True)
	logging.debug(dev_name+' is up')
	return dev_name
	
