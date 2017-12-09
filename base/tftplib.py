# -*- coding: utf-8 -*-
import sys
import pycurl
import subprocess

#Port per Guest board, the first of 20 is used by TFTP.
NB_PORT_BY_GUEST = 20

# Default connection opening timeout (in sec)
DEFAULT_TFTP_CONNECT_TIMEOUT = 3

# Default total transfer timeout (in sec)
DEFAULT_MAX_TFTP_TIMEOUT = 30

# Tftplib_GetModuleIDFromSlotID
def Tftplib_GetModuleIDFromSlotID(rack, slot):
	
	#Module_ID = 16 * (RackNO-1) + SlotNO + 3
	ModuleID = 16 * (rack - 1) + slot + 3
	
	return ModuleID

# Tftplib_GetNodeIDFromSlotID
def Tftplib_GetNodeIDFromSlotID(rack, slot, cpu):

	ModuleID = Tftplib_GetModuleIDFromSlotID(rack, slot)
	
	# NodeID_CPUA = Module_ID * 2
	# NodeID_CPUB = Module_ID * 2 + 1
	if cpu == 'A':
		NodeID = ModuleID * 2
	else:
		NodeID = ModuleID * 2 + 1
	
	return NodeID
	
# Tftplib_GetPortIDFromSlotID
def Tftplib_GetPortIDFromSlotID(rack, slot, cpu):
	
	NodeID = Tftplib_GetNodeIDFromSlotID(rack, slot, cpu)
	
	#PortID = 1024 + NodeID * NB_PORT_BY_GUEST
	PortID = 1024 + NodeID * NB_PORT_BY_GUEST 
	
	return PortID
	
# Tftplib_Download
def Tftplib_Download(rack, slot, cpu, file, ip):

	PortID = Tftplib_GetPortIDFromSlotID(rack, slot, cpu)

	f = open(file, 'wb')
	
	curl = pycurl.Curl()
	curl.setopt(curl.URL, "tftp://" + ip + ":" + str(PortID) + "/" + file)   # URL
	#curl.setopt(curl.VERBOSE, True)   # debug mode
	curl.setopt(curl.CONNECTTIMEOUT, DEFAULT_TFTP_CONNECT_TIMEOUT)
	curl.setopt(curl.TIMEOUT, DEFAULT_MAX_TFTP_TIMEOUT)
	curl.setopt(curl.WRITEDATA, f)
	try:
		curl.perform()
	except pycurl.error, e:
		(returncode, errinfo) = e
	else:
		returncode = 0
		errinfo = ''
	finally:
		curl.close()
		f.close()
		
	#child = subprocess.Popen("curl tftp://" + ip + ":" + str(PortID) + "/" + file + " -s -S --connect-timeout " + str(DEFAULT_TFTP_CONNECT_TIMEOUT) + " --max-time " + str(DEFAULT_MAX_TFTP_TIMEOUT) + " -o " + file, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
	
	#errinfo = child.communicate()[1]
	
	#returncode = child.wait()
	
	return returncode, errinfo

# Tftplib_UpLoad
def Tftplib_Upload(rack, slot, cpu, file, ip):
	
	PortID = Tftplib_GetPortIDFromSlotID(rack, slot, cpu)
	
	f = open(file, 'rb')
	
	curl = pycurl.Curl()
	curl.setopt(curl.URL, "tftp://" + ip + "/" + file)   # URL
	#curl.setopt(curl.VERBOSE, True)   # debug mode
	curl.setopt(curl.CONNECTTIMEOUT, DEFAULT_TFTP_CONNECT_TIMEOUT)
	curl.setopt(curl.TIMEOUT, DEFAULT_MAX_TFTP_TIMEOUT)
	curl.setopt(curl.READDATA, f)
	curl.setopt(curl.UPLOAD, 1) # upload file
	try:
		curl.perform()
	except pycurl.error, e:
		(returncode, errinfo) = e
	else:
		returncode = 0
		errinfo = ''
	finally:
		curl.close()
		f.close()
		
	#child = subprocess.Popen("curl tftp://" + ip + "/" + file + " -s -S -T " + file + " --connect-timeout " + str(DEFAULT_TFTP_CONNECT_TIMEOUT) + " --max-time " + str(DEFAULT_MAX_TFTP_TIMEOUT), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	
	#errinfo = child.communicate()[1]

	#returncode = child.wait()

	return returncode, errinfo

if __name__ == '__main__':
	status, errinfo = Tftplib_Upload(1, 5, 'A', 'cop_open', '20.2.1.22')
	print 'Tftplib_Upload status: ', status
	print 'errinfo', errinfo
	
	status, errinfo = Tftplib_Download(1, 5, 'A', 'ftp_indi', '20.2.1.22')
	print 'Tftplib_Upload status: ', status
	print 'errinfo', errinfo
