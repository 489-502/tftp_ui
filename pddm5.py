#!/usr/bin/python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# FileName:     pddm5.py
# Description:  pddm5设备仿真     
# Author:       Christian He
# Version:      0.0.1
# Created:      2017-11-11
# Company:      CASCO
# LastChange:   create 2017-11-11
# History:          
#----------------------------------------------------------------------------

import sys
import os
import struct
import binascii
import matplotlib.pyplot as plt
import numpy as np
from struct import unpack_from
from base.basedevice import BaseDevice
from base.xmlparser import XmlParser
from base.loglog import LogLog
from PyQt5 import QtCore
from PyQt5.QtCore import QObject

class PDDM5( BaseDevice, QObject ):
    """
    PDDM5 Simulator
    """
    #tftp message head
    qMsgHead = '!BHIIIBBBH'
    
    MSG_HEAD_SIZE = struct.calcsize(qMsgHead)    
    
    PDA_HEAD_SIZE = 0xA5
    
    Signal = QtCore.pyqtSignal(str)
    
    Log = None
    
    msgHandler = None

    def __init__( self, name, id ):
        "init"
        BaseDevice.__init__( self, name, id )
        QObject.__init__(self) 

        #TODO: 初始化msghandler字典 消息ID:消息解析句柄
        self.msgHandler = {
                            1 : self.unpackVersInfoMsg,
                            12: self.unpackErrInfoMsg,
                            96: self.unpackPhaseMsg,
                            97: self.unpackIndiMsg,
                            98: self.unpackVoltMsg,
        }
        
    def logMes( self, level, mes ):
        " log mes"
        self.Log.logMes( level, mes )

    def fileParser(self, board, file):
        if board == self.getDeviceName() and os.path.isfile(file):
            # Read all the data from the file
            fp = open(file, 'rb')

            buffer = fp.read()
            
            fp.close()
            
            if len(buffer) > 0:
                # Check if the file is a pda bin file.
                if unpack_from('!I', buffer)[0] == 0xaaaaaaaa:
                    buffer = buffer[self.PDA_HEAD_SIZE:]
                
                # Unpack message header
                msghead = self.unpackMsgHead(buffer)
                
                # Unpack message body
                self.msgHandler[msghead[1]](msghead[1], buffer)
            else:
                self.Signal.emit('no content in the ' + file)
    
    def unpackMsgHead(self, buf):

        msghead = unpack_from(self.qMsgHead, buf)
            
        self.Signal.emit('Message Header:'
                     '\nversion: ' +     str(hex(msghead[0])) + 
                     '\nMsgId: ' +       str(hex(msghead[1])) + 
                     '\nCycleNo: ' +     str(hex(msghead[2])) +
                     '\nUTC_ms: ' +      str(hex(msghead[3])) +
                     '\nUTC_day: ' +     str(hex(msghead[4])) +
                     '\nMS: ' +          str(hex(msghead[5])) +
                     '\nBoardStatus: ' + str(hex(msghead[6])) +
                     '\nRackSlot: ' +    str(hex(msghead[7])) +
                     '\nMsgSize: ' +     str(hex(msghead[8])))
        
        return msghead
    
    def unpackVersInfoMsg(self, msgId, buf):
        versInfo = self.unpackAppMsg(msgId, buf[struct.calcsize( self.qMsgHead ):])
        
        self.Signal.emit('Version Info:'
                        '\nSwVersionA: ' + str(hex(versInfo[0])) + 
                        '\nSwVersionB: ' + str(hex(versInfo[1])) +
                        '\nSwCRC_CPUA: ' + str(hex(versInfo[2])) +
                        '\nSwCRC_CPUB: ' + str(hex(versInfo[3])) +
                        '\nFPGAVer_A: '  + str(hex(versInfo[4])) +
                        '\nFPGAVer_B: '  + str(hex(versInfo[5])))

    def unpackErrInfoMsg(self, msgId, buf):
        (type,) = unpack_from("!I", buf[struct.calcsize( self.qMsgHead ):])
        #print type
        buf = buf[struct.calcsize( self.qMsgHead ) + struct.calcsize( "!I" ):]
        for i in range(2):
            msgbody = self.unpackAppMsg(type, buf[i * self.getMsgDic()[type]['len'] : (i + 1) * self.getMsgDic()[type]['len']])
            #print msgbody
            if type == 0x11111111:
                self.Signal.emit('Relay Error: the ' + str(i+1) + ' time: ' +
                                '\nId: ' + str(hex(msgbody[0])) + 
                                '\nisClose: ' + str(hex(msgbody[1])) +
                                '\nb24V: ' + str(hex(msgbody[2])) +
                                '\nvalue: ' + str(hex(msgbody[3])))
            elif type == 0x22222222:
                self.Signal.emit('IndiLoop Error: the ' + str(i+1) + ' time: ' +
                                '\nId: ' + str(hex(msgbody[0])) + 
                                '\nisClose: ' + str(hex(msgbody[1])) +
                                '\nRMS: ' + str(hex(msgbody[2])) +
                                '\nCNT_POS: ' + str(hex(msgbody[3])) +
                                '\nCNT_NEG: '  + str(hex(msgbody[4])) +
                                '\nCNT_ZERO: '  + str(hex(msgbody[5])) +
                                '\nShape: ' + str(hex(msgbody[6])))

    #TODO: 增加其他消息解析，主要用struct模块、父类的unpack_from、unpackAppMsg接口，用matplotlib画图

    def unpackPhaseMsg(self, msgId, buf):
        c_current = []
        c_angle   = []
        b_current = []
        b_angle   = []
        a_current = []
        a_angle   = []
        
        (DrvDir, IndiBef, IndiAft) = unpack_from("!BBB", buf[struct.calcsize( self.qMsgHead ):])
        #print DrvDir, IndiBef, IndiAft
        
        buf = buf[struct.calcsize( self.qMsgHead ) + struct.calcsize( "!BBB" ):]
        
        for i in range(len(buf) / self.getMsgDic()[msgId]['len']):
            msgbody = self.unpackAppMsg(msgId, buf[i * self.getMsgDic()[msgId]['len'] : (i + 1) * self.getMsgDic()[msgId]['len']])
            #print msgbody
            c_current.append(msgbody[0])
            c_angle.append(msgbody[1])
            b_current.append(msgbody[2])
            b_angle.append(msgbody[3])
            a_current.append(msgbody[4])
            a_angle.append(msgbody[5])            

        for i in range(len(c_current)):    
            c_current[i] = 0.0122 * (c_current[i] * 8 + 3) + 0.0131
            b_current[i] = 0.0122 * (b_current[i] * 8 + 3) + 0.0131
            a_current[i] = 0.0122 * (a_current[i] * 8 + 3) + 0.0131
            c_angle[i] = c_angle[i] * 360 / 65535
            b_angle[i] = b_angle[i] * 360 / 65535
            a_angle[i] = a_angle[i] * 360 / 65535

        
        plt.subplot(211)
        plt.title('Drive Current with Dir ' + str(hex(DrvDir)) + ' from Indication ' + str(hex(IndiBef)) + ' to ' + str(hex(IndiAft)))
        plt.ylabel('RMS: A')
        plt.plot(np.array(c_current), 'r', label='C')
        plt.plot(np.array(b_current), 'g', label='B')
        plt.plot(np.array(a_current), 'b', label='A')
        plt.legend(loc='lower right', fancybox=True,shadow=True)
        plt.subplot(212)
        plt.title('Phase between Current and Voltage')
        plt.ylabel('Phase: Degree')
        plt.plot(np.array(c_angle), 'r', label='C')
        plt.plot(np.array(b_angle), 'g', label='B')
        plt.plot(np.array(a_angle), 'b', label='A')
        plt.legend(loc='lower right', fancybox=True,shadow=True)
        plt.show()
        
    def unpackIndiMsg(self, msgId, buf):
        volt      = []
        cur_in1   = []
        cur_out1  = []
        cur_in2   = []
        cur_out2  = []
        
        INDI_MSG_BODY_SIZE = self.getMsgDic()[msgId]['len']    
        INDI_MSG_SIZE = self.MSG_HEAD_SIZE + INDI_MSG_BODY_SIZE
        
        #Get the voltage in each message
        for i in range(len(buf) / INDI_MSG_SIZE):
            msgbody = self.unpackAppMsg(msgId, buf[i * INDI_MSG_SIZE + self.MSG_HEAD_SIZE : (i + 1) * INDI_MSG_SIZE])
            #print msgbody
            volt.append(msgbody[0])
            cur_in1.append(msgbody[1])
            cur_out1.append(msgbody[2])
            cur_in2.append(msgbody[3])
            cur_out2.append(msgbody[4])
            
        #Calculate the voltage and current RMS
        for i in range(len(volt)):
            volt[i]     *= 0.09847
            cur_in1[i]  *= 0.009825
            cur_out1[i] *= 0.009825
            cur_in2[i]  *= 0.009825
            cur_out2[i] *= 0.009825
            
        #Plot the voltage
        plt.subplot(211)
        plt.title('Indication Power Voltage')
        plt.ylabel('Voltage RMS: V')
        plt.axis([0, 100, 0, 200])
        plt.plot(np.array(volt), 'r')
        plt.subplot(212)
        plt.title('Indication Current')
        plt.ylabel('Current RMS: mA')
        plt.axis([0, 100, 0, 20])
        plt.Text('Red: R_IN; Green: R_OUT; Blue: N_IN; Pupple: N_OUT')
        plt.plot(np.array(cur_in1), 'r', label='R_IN')
        plt.plot(np.array(cur_out1), 'g', label='R_OUT')
        plt.plot(np.array(cur_in2), 'b', label='N_IN')
        plt.plot(np.array(cur_out2), 'y', label='N_OUT')    
        plt.legend(loc='lower right', fancybox=True,shadow=True)
        plt.show()
    
    def unpackVoltMsg(self, msgId, buf):
        c_volt = []
        b_volt = []
        a_volt = []
        
        VOLT_MSG_BODY_SIZE = self.getMsgDic()[msgId]['len']
        VOLT_MSG_SIZE = self.MSG_HEAD_SIZE + VOLT_MSG_BODY_SIZE
        
        #Get the voltage in each message
        for i in range(len(buf) / VOLT_MSG_SIZE):
            #TODO: try
            msgbody = self.unpackAppMsg(msgId, buf[i * VOLT_MSG_SIZE + self.MSG_HEAD_SIZE : (i + 1) * VOLT_MSG_SIZE])
            #print msgbody
            c_volt.append(msgbody[0])
            b_volt.append(msgbody[1])
            a_volt.append(msgbody[2])

        #Calculate the voltage RMS
        for i in range(len(c_volt)):
            c_volt[i] = (c_volt[i] * 4 + 1) * 0.39388
            b_volt[i] = (b_volt[i] * 4 + 1) * 0.39388
            a_volt[i] = (a_volt[i] * 4 + 1) * 0.39388
            
        #Plot the voltage
        plt.title('Drive Voltage')
        plt.ylabel('Voltage: V')
        plt.axis([0, 100, 0, 300])
        plt.plot(np.array(c_volt), 'r', label='C')
        plt.plot(np.array(b_volt), 'g', label='B')
        plt.plot(np.array(a_volt), 'b', label='A')
        plt.legend(loc='lower right', fancybox=True,shadow=True)    
        plt.show()
    
    def deviceInit( self, *args, **kwargs ):
        " pddm5 init"
        self.Log = LogLog()
        self.Log.orderLogger( kwargs['log'], type( self ).__name__ )

        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )

        self.importMsg( kwargs['msgFile'] )

        return True

    def deviceRun( self, *args, **kwargs ):
        "pddm5 run"
        self.logMes( 4, type( self ).__name__ + '.' + sys._getframe().f_code.co_name )

    def deviceEnd( self ):
        " ending device"
        self.Log.fileclose()         

if __name__ == '__main__':
    pddm5 = PDDM5( 'PDDM5', 1 )
    pddm5.deviceInit(msgFile = r'./config/pddm5_message.xml', \
                    log = r'./log/pddm5.log', \
                    )
    #print 'msg dic', pddm5.getMsgDic()
    pddm5.fileParser('pddm5', 'ftp_vers')
