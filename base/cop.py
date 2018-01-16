# -*- coding: utf-8 -*-

from struct import pack
import tftplib

# Binary Cop file contains the one byte NodeID.
def CopFile(name, data):
    fp = open(name, "wb+")
    data = pack('>B', data)  # big-endian
    fp.write(data)
    fp.close()

def CopOpen(rack, slot, cpu, ip):
    
    # Write the NodeID into the 'cop_open' file.
    NodeID = tftplib.Tftplib_GetNodeIDFromSlotID(rack, slot, cpu)
    
    CopFile("cop_open", NodeID)
    
    # Upload the 'cop_open' file to the EIOCOM2 to enable the routing to the corresponding board.
    status, errinfo = tftplib.Tftplib_Upload(rack, slot, cpu, "cop_open", ip)
    
    return status, errinfo

def CopClose(rack, slot, cpu, ip):
    
    # Write the NodeID into the 'cop_close' file.
    NodeID = tftplib.Tftplib_GetNodeIDFromSlotID(rack, slot, cpu)
    
    CopFile("cop_close", NodeID)
    
    # Upload the 'cop_close' file to`the EIOCOM2 to disable the routing to the corresponding board.
    status, errinfo = tftplib.Tftplib_Upload(rack, slot, cpu, "cop_close", ip)
    
    return status, errinfo

if __name__ == '__main__':
    status, errinfo = CopOpen(1,3,'A','20.2.1.22')
    #print status, errinfo

    status, errinfo = CopClose(1,3,'A','20.2.1.22')
    #print status, errinfo