# Author: Rayan Elahmadi
# Created: 07/08/2020
# Python App 
#	Accesses Tektronix DP73304D Scope over ethernet 
#	Launches GUI
#	Requires IP address of Scope
# User can 
#	Set sampling rate and save waveform to default csv file 
#	Collect measurements, 
#	Displays, in realtime, waveforms in time-domain and frequency-domain (spectrum)
# 	Save waveform to default csv file DataWave.csv (in user's current directory) 

import sys
import pyvisa as visa
import math
import time
import datetime
import numpy as np
import pylab
from struct import unpack
from tkinter import *
from tkinter.ttk import *
import matplotlib.pyplot as plt
from multiprocessing import Process
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#import cv2

class DPO():
    
    def connect(self,addr):
        self._ethernet_IP = addr
        try:
            idn = self.get_idn()
        except:
            print("Could not connect to {}".format(addr))
            self._ethernet_IP = ""
            return -1
        
        self._idn = idn
        print("Connected to {} with ID {}".format(self._ethernet_IP, idn))

        return (0)
    
    
   
    def query(self, cmd):
        rm  = visa.ResourceManager()
        inst = rm.open_resource(self._ethernet_IP)
        return(inst.query(cmd))

    def write(self, cmd):
        rm  = visa.ResourceManager()
        inst = rm.open_resource(self._ethernet_IP)
        return(inst.write(cmd))

###############################################################################
    def get_idn(self):
        return(self.query('*IDN?'))
   
    def pk2pk(self):
        self.write(':MEASU:IMM:SOU1 CH4')
        self.write(':MEASU:IMM:TYP PK2Pk')
        x = self.query(':MEASU:IMM:VAL?')
        return x
    def freq(self):
        self.write(':MEASU:IMM:SOU1 CH4')
        self.write(':MEASU:IMM:TYP FREQ')
        z = self.query(':MEASU:IMM:VAL?')
        return z
    def peri(self):
        self.write(':MEASU:IMM:SOU1 CH4')
        self.write(':MEASU:IMM:TYP PERI')
        t = self.query(':MEASU:IMM:VAL?')
        return t
    def fall(self):
        self.write(':MEASU:IMM:SOU1 CH4')
        self.write(':MEASU:IMM:TYP FALL')
        p = self.query(':MEASU:IMM:VAL?')
        return p
    def rise(self):
        self.write(':MEASU:IMM:SOU1 CH4')
        self.write(':MEASU:IMM:TYP RIS')
        b = self.query(':MEASU:IMM:VAL?')
        return b
    def sample(self, aq):
        sr = self.write(f'HOR:MODE:SAMPLER {aq}')
        return sr


        
 
    def get_data(self):
        rm = visa.ResourceManager()
        scope = rm.open_resource(self._ethernet_IP)

        scope.write('DATA:SOU CH4')
        scope.write('DATA:WIDTH 1')
        scope.write('DATA:ENC RPB')


        ymult = float(scope.query('WFMPRE:YMULT?'))
        yzero = float(scope.query('WFMPRE:YZERO?'))
        yoff = float(scope.query('WFMPRE:YOFF?'))
        xincr = float(scope.query('WFMPRE:XINCR?'))


        scope.write('CURVE?')
        data = scope.read_raw()
        headerlen = 2 + int(data[1])
        header = data[:headerlen]
        ADC_wave = data[headerlen:-1]

        ADC_wave = np.array(unpack('%sB' % len(ADC_wave),ADC_wave))

        Volts = (ADC_wave - yoff) * ymult  + yzero

        Time = np.arange(0, xincr * len(Volts), xincr)
        return Time, Volts, xincr
    def times(self):
        Time, Volts, xincr = self.get_data()
        return xincr
    def sampr (self):
        Time, VOlts, xincr = self.get_data()
        return 1/xincr


    def save(self):
        Time, Volts, xincr = self.get_data()
        with open('DataWave.csv', 'w') as f:
            tim = str(Time)
            vol = str(Volts)
            dd = len(Time)
            for i in range(dd): 
                f.write(str(Time[i]) + ', ' + str(Volts[i]) + '\r')
            f.close()
          
        

    
    def spectrum(self):
       
       
        Time, Volts, xincr = self.get_data()

        s=Volts
        fft = np.fft.fft(s)
        #T = Time[1] - Time[0]

        N=len(Volts)
      
        f = np.linspace(0, 1 / xincr, N)
                
        mag=np.abs(fft)[:N // 2]
        maximum=0
        for i,value in enumerate(mag):
            if value>maximum:
                maximum=value
                index=i

        plt.ylabel("Amplitude")
        plt.xlabel("Frequency [MHz]")
        #plt.bar(f[:N // 2], np.abs(fft)[:N // 2] * 1 / N, width=1.5)
        
        plt.plot(0.5*f[:N // 2]/1e6, np.abs(fft)[:N // 2] * 1 / N)
        plt.draw()
        plt.pause(0.0001)
        plt.clf()
    
        
    def rt_scope(self, window):
        Time, Volts, xincr = self.get_data()
    
        plt.plot(Time[:len(Volts)], Volts)
        plt.draw()
        plt.pause(0.0001)
        plt.clf()

def main():
    rm = visa.ResourceManager()
    
    #g = rm.list_resources()

    inp = "TCPIP0::" + input("enter IP Address: ") + "::inst0::INSTR"
    #time.sleep(10)
    
    #cd = g[0]
    
    
    dpo = DPO()

    dpo.connect(inp)

    



    
    
    y = dpo.pk2pk()

    l = dpo.freq()

    k = dpo.peri()
  
    r = dpo.fall()

    a = dpo.rise()

    ts = dpo.times()

    rsamp = dpo.sampr()

    window = Tk()
    
    window.geometry('500x300')

    window.title("Measurements from Oscilloscope")

    selected = DoubleVar()

    (Label(window, text='Pk-Pk (mV)')).grid(row=0, column=0)
    (Label(window, text='Freq (MHz)')).grid(row=1, column=0)
    (Label(window, text='Period (ps)')).grid(row=2, column=0)
    (Label(window, text='Fall Time (ps)')).grid(row=3, column=0)
    (Label(window, text='Rise Time (ps)')).grid(row=4, column=0)
    (Label(window, text='Time Step (ps)')).grid(row=5, column=0)
    (Label(window, text='Sample Rate (GS/s): ')).grid(row=6, column=0)
    (Label(window, text='Sample Rate (S/s): ')).grid(row=15, column=0)
    
    e6 = Entry(window)
    e6.grid(row=15, column=1)
    
    def samplerate():
        
        aq = e6.get()
        dpo.sample(aq)
        
    button2 = Button(window, text="Set", command=samplerate)
    button2.grid(row=15, column=2)

    button3 = Button(window, text="Save Waveform to csv File", command=dpo.save)
    button3.grid(row=13, column=5, pady=15)
                     
    
    

    

    
    


    def clicked():
        v = selected.get()
        if v == 0:
            while True:
                dpo.get_data()
                dpo.rt_scope(window)
                y = dpo.pk2pk()
                
                l = dpo.freq()

                k = dpo.peri()
          
                r = dpo.fall()

                a = dpo.rise()

                ts = dpo.times()

                rsamp = dpo.sampr()
                
                e1 = Entry(window)
                e1.grid(row=0, column=1)
                e1.insert(0, round(float(y) * 1000, 1))
                
                window.update()
                
            
                
                
                e2 = Entry(window)
                e2.grid(row=1, column=1)
                
                e2.insert(0, round((float(l))/1000000, 1))
                    
                e3 = Entry(window)
                e3.grid(row=2, column=1)
                e3.insert(0, round(float(k) * 1000000000000, 1))
                        
                e4 = Entry(window)
                e4.grid(row=3, column=1)
                e4.insert(0, round(float(r) * 1000000000000, 1))
                
                e5 = Entry(window)
                e5.grid(row=4, column=1)
                e5.insert(0, round(float(a) * 1000000000000, 1))

                e7 = Entry(window)
                e7.grid(row=5, column=1)
                e7.insert(0, round(float(ts) * 1000000000000, 1))

                e8 = Entry(window)
                e8.grid(row=6, column=1)
                e8.insert(0, rsamp/(10 ** 9))
                
                
        
    def clicked1():
        v = selected.get()
        if v == 0:
            while True:
                dpo.get_data()
                
                dpo.spectrum()
                
                y = dpo.pk2pk()
                
                l = dpo.freq()

                k = dpo.peri()
          
                r = dpo.fall()

                a = dpo.rise()

                ts = dpo.times()

                rsamp = dpo.sampr()
                
                e1 = Entry(window)
                e1.grid(row=0, column=1)
                e1.insert(0, round((float(y)) * 1000, 1))
                window.update()
                
                e2 = Entry(window)
                e2.grid(row=1, column=1)
                e2.insert(0, round((float(l))/1000000, 1))
                    
                e3 = Entry(window)
                e3.grid(row=2, column=1)
                e3.insert(0, round(float(k) * 1000000000000, 1))
                        
                e4 = Entry(window)
                e4.grid(row=3, column=1)
                e4.insert(0, round(float(r) * 1000000000000, 1))
                
                e5 = Entry(window)
                e5.grid(row=4, column=1)
                e5.insert(0, round(float(a) * 1000000000000, 1))

                e7 = Entry(window)
                e7.grid(row=5, column=1)
                e7.insert(0, round(float(ts) * 1000000000000, 1))

                e8 = Entry(window)
                e8.grid(row=6, column=1)
                e8.insert(0, rsamp/(10 ** 9))

    button = Button(window, text="Spectrum", command=clicked1)
    button.grid(row=3, column=5)

    button1 = Button(window, text="Oscilloscope", command=clicked)
    button1.grid(row=4, column=5)


 
    



          

    

    
    
    

    

    
    



    window.mainloop()
    
    

if __name__ == '__main__':
    main()



