# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 15:12:37 2018

@author: Madhu
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from kivy.factory import Factory
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty

import os
import glob
import time

import csv
import datetime
import pandas as pd 

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

csvData = [['Timestamp', 'Farenheit']]
userData = [['Username', 'Password']]

class Root(BoxLayout):
    
    try:
        open('users.csv')
    except:    
        with open('users.csv', 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(userData)
    
    sensor_value_f = NumericProperty(0)
    
    rec1time = StringProperty('0')
    rec2time = StringProperty('0')
    rec3time = StringProperty('0')
    rec4time = StringProperty('0')
    rec5time = StringProperty('0')
    rec6time = StringProperty('0')
    rec7time = StringProperty('0')
    rec8time = StringProperty('0')
    rec9time = StringProperty('0')
    rec10time = StringProperty('0')
    rec1fahr = NumericProperty(0)
    rec2fahr = NumericProperty(0)
    rec3fahr = NumericProperty(0)
    rec4fahr = NumericProperty(0)
    rec5fahr = NumericProperty(0)
    rec6fahr = NumericProperty(0)
    rec7fahr = NumericProperty(0)
    rec8fahr = NumericProperty(0)
    rec9fahr = NumericProperty(0)
    rec10fahr = NumericProperty(0)
    
    def loginPage(self):
        self.clear_widgets()
        lPage = Factory.Login()
        self.add_widget(lPage)
    
    def signUpPage(self):
        self.clear_widgets()
        sPage = Factory.SignUp()
        self.add_widget(sPage)
        
    def validate(self, username, password, status):       
        reader = csv.reader(open("users.csv"))
        
        d={}

        for row in reader:
            d[row[0]]=row[1:]
        
        try:
            if((d[username])[0] == password):
                self.mainPage()
            else:
                status.text = "Wrong Password"
        except:
            status.text = "User not found"
            
    
    def signUp(self, name, passw, result):
        reader = csv.reader(open("users.csv"))
        
        d={}

        for row in reader:
            d[row[0]]=row[1:]
            
        try:
            d[name]
            result.text = "Username taken"
        except:    
            with open('users.csv', 'a', newline='') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow([name, passw])
        
            result.text = "Signed Up!"
    
    def mainPage(self):
        self.clear_widgets()
        mPage = Factory.MainPage()
        self.add_widget(mPage)
    
    def bpPage(self):
        self.clear_widgets()
        bPage = Factory.BpPage()
        self.add_widget(bPage)
    
    def tempPage(self):
        try:
            open('tempTest.csv')
        except:    
            with open('tempTest.csv', 'w', newline='') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerows(csvData)
        
        self.clear_widgets()
        tPage = Factory.TempPage()
        self.add_widget(tPage)
        
    def bpInst(self):
        self.clear_widgets()
        bInst = Factory.BpInst()
        self.add_widget(bInst)
        
    def tempInst(self):
        self.clear_widgets()
        tInst = Factory.TempInst()
        self.add_widget(tInst)
        
    def tempMeasure(self):
        self.sensor_value_c = 0
        self.sensor_value_f = 0
        
        self.clear_widgets()
        tMeasure = Factory.TempMeasure()
        self.add_widget(tMeasure)
        
        Clock.schedule_once(self.read_temp, 5)            

    def read_temp_raw(self):
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines
 
    def read_temp(self, dt=0):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            self.sensor_value_c = float(temp_string) / 1000.0
            self.sensor_value_f = self.sensor_value_c * 9.0 / 5.0 + 32.0
        
        with open('tempTest.csv', 'a', newline='') as csvFile:
            writer = csv.writer(csvFile)
            now = str(datetime.datetime.now().replace(microsecond=0))
            writer.writerow([now, self.sensor_value_f])
        
    def tempRecords(self):
        self.genRecords()
        
        self.clear_widgets()
        tRec = Factory.TempRecords()
        self.add_widget(tRec) 
        
    def ecgAnalyse(self):
       	hrw = 0.75 #One-sided window size, as proportion of the sampling frequency
        fs = 100 #The example dataset was recorded at 100Hz
	       dataset = read_csv('ecg.csv')
        dataset=dataset.drop('0',axis=1)
        dataset.columns=['hart']
        mov_avg = np.array(dataset['hart'].rolling(10).mean().dropna()) #Calculate moving average
        #Impute where moving average function returns NaN, which is the beginning of the signal where x hrw
        avg_hr = (np.mean(dataset.hart))
        mov_avg = [avg_hr if math.isnan(x) else x for x in mov_avg]
        mov_avg = [x*2 for x in mov_avg] #For now we raise the average by 20% to prevent the secondary heart contraction from interfering, in part 2 we will do this dynamically
        dataset.hart=dataset.hart.iloc[:len(mov_avg)]
        hartnew=dataset.hart.dropna()
        dataset.hart=hartnew
        dataset=dataset.dropna()
        dataset['hart_rollingmean'] = mov_avg #Append the moving average to the dataframe
        #Mark regions of interest
        window = []
        peaklist = []
        listpos = 0 #We use a counter to move over the different data columns
        rollingmean=hartnew.mean()+0.4
        for datapoint in dataset.hart:
            #rollingmean = dataset.hart_rollingmean[listpos]-2 #Get local mean
            if (datapoint < rollingmean) and (len(window) < 1): #If no detectable R-complex activity -> do nothing
                listpos += 1
            elif (datapoint > rollingmean): #If signal comes above local mean, mark ROI
                window.append(datapoint)
                listpos += 1
            else: #If signal drops below local mean -> determine highest point
                maximum = max(window)
                beatposition = listpos - len(window) + (window.index(max(window))) #Notate the position of the point on the X-axis
                peaklist.append(beatposition) #Add detected peak to list
                window = [] #Clear marked ROI
                listpos += 1
        ybeat = [dataset.hart[x] for x in peaklist] #Get the y-value of all peaks for plotting purposes
        RR_list = []
        cnt = 0
        while (cnt < (len(peaklist)-1)):
            RR_interval = (peaklist[cnt+1] - peaklist[cnt]) #Calculate distance between beats in # of samples
            ms_dist = ((RR_interval / fs) * 1000.0) #Convert sample distances to ms distances
            RR_list.append(ms_dist) #Append to list
            cnt += 1
        bpm = 60000 / np.mean(RR_list) #60000 ms (1 minute) / average R-R interval of signal
        #Setting up the plots of ECG (R peaks highlighted) and ECG moving average
        f, axarr = plt.subplots(2, sharex=True)
        f.suptitle(str(bpm)+' bps Heartrate')
        axarr[0].plot(dataset.hart, alpha=0.5, color='blue')
        axarr[0].scatter(peaklist, ybeat, color='red')
        axarr[0].set_xlabel('seconds')
        axarr[0].set_ylabel('Voltage reading')
        axarr[0].set_title('ECG Sensor Readings')
        #axarr[0].invert_yaxis()
        axarr[0].grid(True)
        axarr[1].plot(mov_avg, color ='green')
        axarr[1].set_xlabel('seconds')
        axarr[1].set_ylabel('Voltage reading')
        axarr[1].set_title('ECG Moving Average')
        axarr[1].grid(True)
        plt.savefig('heart1.png') 
        
    def genRecords(self):
        with open('tempTest.csv',"r") as f:
            reader = csv.reader(f,delimiter = ",")
            data = list(reader)
            row_count = len(data)
        
        mdata = pd.read_csv('tempTest.csv',delimiter=',')
        
        if row_count <= 11:
            try:
                self.rec1time = str(mdata.iloc[0][0])
                self.rec1fahr = str(mdata.iloc[0][1])
            except:
                pass
            
            try:
                self.rec2time = str(mdata.iloc[1][0])
                self.rec2fahr = str(mdata.iloc[1][1])
            except:
                pass
            
            try:
                self.rec3time = str(mdata.iloc[2][0])
                self.rec3fahr = str(mdata.iloc[2][1])
            except:
                pass
            
            try:
                self.rec4time = str(mdata.iloc[3][0])
                self.rec4fahr = str(mdata.iloc[3][1])
            except:
                pass
            
            try:
                self.rec5time = str(mdata.iloc[4][0])
                self.rec5fahr = str(mdata.iloc[4][1])
            except:
                pass
            
            try:
                self.rec6time = str(mdata.iloc[5][0])
                self.rec6fahr = str(mdata.iloc[5][1])
            except:
                pass
            
            try:
                self.rec7time = str(mdata.iloc[6][0])
                self.rec7fahr = str(mdata.iloc[6][1])
            except:
                pass
            
            try:
                self.rec8time = str(mdata.iloc[7][0])
                self.rec8fahr = str(mdata.iloc[7][1])
            except:
                pass
            
            try:
                self.rec9time = str(mdata.iloc[8][0])
                self.rec9fahr = str(mdata.iloc[8][1])
            except:
                pass
            
            try:
                self.rec10time = str(mdata.iloc[9][0])
                self.rec10fahr = str(mdata.iloc[9][1])
            except:
                pass
        else:
            
            self.rec1time = str(mdata.iloc[row_count-11][0])
            self.rec1fahr = str(mdata.iloc[row_count-11][1])
            
            self.rec2time = str(mdata.iloc[row_count-10][0])
            self.rec2fahr = str(mdata.iloc[row_count-10][1])
            
            self.rec3time = str(mdata.iloc[row_count-9][0])
            self.rec3fahr = str(mdata.iloc[row_count-9][1])
            
            self.rec4time = str(mdata.iloc[row_count-8][0])
            self.rec4fahr = str(mdata.iloc[row_count-8][1])
            
            self.rec5time = str(mdata.iloc[row_count-7][0])
            self.rec5fahr = str(mdata.iloc[row_count-7][1])
            
            self.rec6time = str(mdata.iloc[row_count-6][0])
            self.rec6fahr = str(mdata.iloc[row_count-6][1])
            
            self.rec7time = str(mdata.iloc[row_count-5][0])
            self.rec7fahr = str(mdata.iloc[row_count-5][1])
            
            self.rec8time = str(mdata.iloc[row_count-4][0])
            self.rec8fahr = str(mdata.iloc[row_count-4][1])
            
            self.rec9time = str(mdata.iloc[row_count-3][0])
            self.rec9fahr = str(mdata.iloc[row_count-3][1])
            
            self.rec10time = str(mdata.iloc[row_count-2][0])
            self.rec10fahr = str(mdata.iloc[row_count-2][1])
       
            
class HealthguiApp(App):
    pass        

if __name__ == '__main__':
    HealthguiApp().run()
