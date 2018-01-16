import struct
import os
import sys
import time
import numpy as np
import matplotlib.pyplot as plt

# ftp_cur  id : 0x20
sddm_cur_id  = 32

# ftp_vers id : 0x01
sddm_vers_id = 1

# ftp_err  id : 0x0c
sddm_err_id  = 12

class sddm_msghead:
    def __init__(self):
        self.pattern = '!BHIIIBBBH'
        self.size    = struct.calcsize(self.pattern)
    def unpackhead(self, buf):
        self.head    = struct.unpack_from(self.pattern, buf)
        self.version = self.head[0]
        self.type    = self.head[1]
        self.cycleno = self.head[2]
        self.utc_ms  = self.head[3]
        self.utc_day = self.head[4]
        self.status  = self.head[5]
        self.error   = self.head[6]
        self.location= self.head[7]
        self.datasize= self.head[8]

class SDDM:
    def __init__(self):
        self.msghead = sddm_msghead()
    
    def unpackcurmsg(self, rack, slot, cpu, curfile):
        if cpu == "A":
            kgain = (1000.0 * 5.0) / (4096.0 * 3.0)
        else:
            kgain = (1000.0 * 5.0) / (4096.0 * 4.0)

        if os.path.isfile(curfile) == True:
            file   = open(curfile, 'rb')
            buffer = file.read()
            file.close()         
            idx     = 0          
            tc      = []         
            current = [[],[],[],[],[],[]]
            portnum = 0
            
            # reslove the all current message     
            while len(buffer[idx:]) > self.msghead.size:
                # unpack the message header
                self.msghead.unpackhead(buffer[idx:])
                # check the type of message
                if self.msghead.type != sddm_cur_id:
                    return (-1, 'this message is not ftp_cur')
                           
                idx = idx + self.msghead.size               
                # get the number of port used
                portnum = struct.unpack_from('!B', buffer[idx:])[0]
                # get the pattern of the data
                curmsgpattern = '!{0}H'.format(portnum)
                data = struct.unpack_from(curmsgpattern, buffer[(idx + 1):])
                idx = idx + self.msghead.datasize
                # store timecounter and current data into list
                tc.append(self.msghead.cycleno)
                for x in range(portnum):                 
                    current[x].append(data[x] * kgain)

            # get the index where the tc[index} > tc[index]
            repoint = 0
            if len(tc) > 1:
                for i in range(len(tc) - 1):
                    if tc[i] > tc[i + 1]:                       
                        repoint = i + 1
            # sort tc and current according to timecounter
            tc = tc[repoint:] + tc[:repoint]
            for x in range(portnum):
                current[x] = current[x][repoint:] + current[x][:repoint]

            # create figure, row = portnum, col = 1           
            fig, axs = plt.subplots(nrows = portnum, sharex = True, figsize=(12, 10))
            # set options
            title = 'Filament Current in CPU {0}(unit: mA)\n'.format(cpu) + 'Rack {0} Slot {1}'.format(rack, slot)
            fig.suptitle(title)
            plt.xlabel("Time Counter")
            # line color from port1 to port6
            color = 'bgrcmy'
            
            #title and xaxis, yaxis
            for x in range(portnum):
                # set lim for each y axies
                maxvalue = np.max(current[x]) + 10.0
                minvalue = np.min(current[x]) - 10.0
                axs[x].set_ylim(minvalue, maxvalue)
                # axs[x].set_yticks(np.arange(minvalue,maxvalue,1.0))
                axs[x].plot(tc, current[x], color[x], label = 'Port {0}'.format(x + 1))
                axs[x].grid()
                    
            # set legend
            legend = fig.legend(loc='upper right', shadow=True, facecolor='#00FFCC')
            
            # Save figures, name systime_SDDM_rack_slot_Current.png, dir images
            dir     = 'images'
            pngfile = dir + '/' + time.strftime('%Y_%m_%d_%H_%M_%S') + "_SDDM_{0}_{1}_CPU_{2}_Current.png".format(rack, slot, cpu)
            if os.path.exists(dir) == False:
                os.mkdir(dir)
            
            if os.path.exists(pngfile) == False:
                os.mknod(pngfile)
            
            fig.savefig(pngfile)
            
            # Show figure
            plt.show()
            
            return (0, 'ftp_cur unpack ok')
        else:
            return (-1, '{0} is not exist'.format(curfile))
        
    def unpackversmsg(self, rack, slot, cpu, verfile):
        if os.path.isfile(verfile) == True:
            file   = open(verfile, 'rb')
            buffer = file.read()
            file.close()
            self.msghead.unpackhead(buffer)
            if self.msghead.type != sddm_vers_id:
                return (-1, 'this message is not ftp_vers')
                
            #versinfo = struct.unpack_from('!6I2H', buffer[self.msghead.size:])
            versinfo = struct.unpack_from('!4BI4BI2I2H', buffer[self.msghead.size:])

            # Create a table to show the software information
            fig = plt.figure(figsize=(8, 4), dpi=120)
            
            # set options
            title = 'Software information of CPU {0}\n'.format(cpu) + 'Rack {0} Slot {1}'.format(rack, slot)
            plt.title(title)
            
            # draw tables
            versinfostr = 'SDDM Software Information:\n'
            columns = ('CPU A', 'CPU B')
            rows    = ('Sw version', 'Build', 'Sw ID', 'FPGA version')
            cell_text = []
            swvers    = []
            buildinfo = []
            swid      = []
            fpgavers  = []
            
            value = 'V{0}.{1}.{2}.{3}'.format(versinfo[0], versinfo[1], versinfo[2], versinfo[3])
            swvers.append(value)
            versinfostr = versinfostr + 'CPU A Version:\t' + value + '\n'
            
            value = '{0:08X}'.format(versinfo[4])
            buildinfo.append(value)
            versinfostr = versinfostr + 'CPU A Build:\t' + value + '\n'  
         
            value = 'V{0}.{1}.{2}.{3}'.format(versinfo[5], versinfo[6], versinfo[7], versinfo[8])
            swvers.append(value)
            versinfostr = versinfostr + 'CPU B Version:\t' + value + '\n'

            value = '{0:08X}'.format(versinfo[9])
            buildinfo.append(value)
            versinfostr = versinfostr + 'CPU A Build:\t' + value + '\n'

            value = '{0:08X}'.format(versinfo[10])
            swid.append(value)
            versinfostr = versinfostr + 'CPU A ID:\t\t' + value + '\n'
            
            value = '{0:08X}'.format(versinfo[11])      
            swid.append(value)
            versinfostr = versinfostr + 'CPU B ID:\t\t' + value + '\n'
            value = 'V{0}.{1}.{2}.{3}'.format((versinfo[12] & 0xF000)>>12,\
                                              (versinfo[12] & 0x0F00)>>8,\
                                              (versinfo[12] & 0x00F0)>>4,\
                                              (versinfo[12] & 0x000F))           

            fpgavers.append(value)
            versinfostr = versinfostr + 'FPGA A:\t\t' + value + '\n'
            value = 'V{0}.{1}.{2}.{3}'.format((versinfo[13] & 0xF000)>>12,\
                                              (versinfo[13] & 0x0F00)>>8,\
                                              (versinfo[13] & 0x00F0)>>4,\
                                              (versinfo[13] & 0x000F))
            fpgavers.append(value)
            versinfostr = versinfostr + 'FPGA B:\t\t' + value + '\n'
            
            cell_text.append(swvers)
            cell_text.append(buildinfo)
            cell_text.append(swid)
            cell_text.append(fpgavers)

            the_table = plt.table(cellText=cell_text, rowLabels=rows, colLabels=columns, cellLoc='center', loc='center')
            
            # axis off
            plt.axis('off')

            # Save figures, name systime_SDDM_rack_slot_version.png, dir images
            dir     = 'images'
            pngfile = dir + '/' + time.strftime('%Y_%m_%d_%H_%M_%S') + "_SDDM_{0}_{1}_CPU_{2}_Version.png".format(rack, slot, cpu)
            if os.path.exists(dir) == False:
                os.mkdir(dir)
            
            if os.path.exists(pngfile) == False:
                os.mknod(pngfile)
               
            fig.savefig(pngfile)
            
            # Show table
            plt.show()          
            return (0, versinfostr)
        else:
            return (-1, '{0} is not exist'.format(verfile))

    def show(self, rack, slot, cpu, file):
        if file == 'ftp_cur':
            return self.unpackcurmsg(rack, slot, cpu, file)
        elif file == 'ftp_vers':
            return self.unpackversmsg(rack, slot, cpu, file)
        else:
            return (-1, '{0}is not support ...yet!'.format(file))

