import numpy as np 
import pandas as pd
import csv


class IPlogreader():
    def __init__(self, file=None):
        self.file = file # filepath to csv/text file containing log
        self.data = {'ip':[], 'time':[], 'bytes':[]}
        self.datalen = 0 # len of data
        self.load() # load data when initialized


    def ifip(self,ip): # Function to check if a given string is an ip address (Ipv4)
        ipsplit = ip.split('.') # split with '.' as a delimiter
        if(len(ipsplit)!=4): return False # cannot be more than 4 integers in the split
        for i in ipsplit:
            try: # check if each split is an integer 
                int(i)
                if(int(i) not in range(0,256)): # if integer, must be in [0,255]
                    return False
            except ValueError: # Cannot be a non-integer value
                return False
        return True # no error in address

    def load(self, verbose=True):   
        len = 0
        if self.file==None:
            print('No file to process! Cannot load data')
        else:
            with open(self.file,"r") as file:
                for line in file:
                    line = line.split(' ')
                    ip, time, status, bytes = line[0], line[1], line[-2], line[-1]
                    if(self.ifip(ip) and int(status)==200):
                        len += 1
                        self.data['ip'].append(ip)
                        self.data['time'].append(time.replace("[","").replace("]",""))
                        self.data['bytes'] .append(int(bytes))
            self.datalen = len
        
        if(verbose):
            print('Successfully loaded data!')

    
        

    def compute_bytes_per_ip(self,data): # for a given data, compute bytes processed by each ip address
        datalen = len(data['ip']) # length of data
        seen = {'ip':[], 'bytes':[]} # initialize seen dict to check uniqueness
        for i,ip in enumerate(data['ip']): 
            if(ip not in seen['ip']): # if unique ip
                seen['ip'].append(ip)
                seen['bytes'].append(0)
                for j in range(datalen): # loop through data to compute bytes processed by ip
                    if(data['ip'][j]==ip):
                        seen['bytes'][-1]+=data['bytes'][j]
        return seen

    # It is assumed that the data input is sorted by time in an ascending order
    def compute_bytes_per_ip_inHour(self, data, initial_time='29:00:00:00'):

        # set init ts 0:00:00:00 or custom value
        # loop through data till hit ts more than 1 hr from init ts - store intermediate data
        # for subset call compute_bytes_per_ip and append to list

        def generatewindows(initial_time): # generate windows
            initial_date, initial_hour,_,_=list(map(int, initial_time.split(':')))
            windows = [] 
            for days in range(initial_date,31):
                for hours in range(initial_hour,24):
                    windows.append([f'{days}:{hours}:00:00', f'{days}:{hours}:59:59'])
            return windows
            
        
        def get_ips_inwindow(data,window='30:0:00:00'): # 
            new = {'ip':[],'bytes':[]} # defined new dict 
            def inwindow(initial_time, time): # check if data winthin an hour from init_time
                    day, hour, min, sec = list(map(int, initial_time.split(':')))
                    day_, hour_, min_, sec_ = list(map(int, time.split(':')))
                    if(day_-day!=0 or hour_-hour!=0): # if difference is days and hours not zero, cannot be in window of an hour
                        return False
                    else:
                        min_diff = min_ - min
                        if(min_diff<0):
                            return False
                        else:
                            sec_diff = sec_ - sec
                            return True if 60*min_diff+sec_diff<3600 else False   
                            
            for i,time in enumerate(data['time']): # check if ip in window
                if(inwindow(window,time)): # add data if in window
                    new['ip'].append(data['ip'][i])
                    new['bytes'].append(data['bytes'][i])
            return new
        
        windows = generatewindows(initial_time=initial_time) # generate windows of durtion 1 hour from initial_time
        window_data = {'window':[],'ip_list':[],'bytes_list':[]} # dict of window_init time, ips and bytes in the window
        for window in windows:
            # print(window)
            win_data = get_ips_inwindow(self.data,window=window[0])
            win_data = self.compute_bytes_per_ip(data=win_data)
            window_data['window'].append(window)
            window_data['ip_list'].append(win_data['ip'])
            window_data['bytes_list'].append(win_data['bytes'])
            
        return window_data

    def ip_topK_bytes(self,data=None,sortby='bytes',address='ip',K=10): # get top K bytes of unique ip
        # get ip-bytes values and sort
        if(data==None):
            data=self.data
        
        sorted_data = self.data_sort(data=data, sortby=sortby,address=address, reverse=True);
        top_data = data_subset = {k:[v[index] for index in range(K)] for k,v in sorted_data.items() }
        
        return {key:top_data[key] for key in [address,'bytes']}
        

    def groupBySubnet(self,data=None, numbytes=2):
        # Given data, group ips by subnet and return statistics

        if(data==None):
            data=self.data # init data to self data if none
            
        def subnetValue(ip): # convert ip to subnet value of numbytes=numbytes
            splitip = ip.split('.')
            # print(splitip)
            subnet=''
            for j in range(numbytes):
                if(j!=numbytes-1):
                    subnet+=splitip[j]+'.'
                else:
                    subnet+=splitip[j]
            return subnet
          
            
        unique_data = self.compute_bytes_per_ip(data) # compute unique ip addresses
        seen = {'subnet':[], 'bytes':[]} # seen dictionary
        for i,ip in enumerate(unique_data['ip']): # go through each ip and assign to its subnet
            subnet = subnetValue(ip)
            if subnet not in seen['subnet']:
                seen['subnet'].append(subnet)
                seen['bytes'].append(0)
                for iters, ip_ in enumerate(unique_data['ip']):
                    if(subnetValue(ip_)==subnet):
                        seen['bytes'][-1]+=unique_data['bytes'][iters]
        return seen

    def compute_bytes_per_subnet_inHour(self, numbytes=2, initial_time='29:00:00:00'): # compute byte statistics in window for unique subnets
        window_data = self.compute_bytes_per_ip_inHour(self.data, initial_time=initial_time)
        def subnetValue(ip): # subnet for given ip
            splitip = ip.split('.')
            # print(splitip)
            subnet=''
            for j in range(numbytes):
                if(j!=numbytes-1):
                    subnet+=splitip[j]+'.'
                else:
                    subnet+=splitip[j]
            return subnet

        subnet_window_data = seen = {'window':[],'subnet_list':[], 'bytes_list':[]} # return window, subnets, bytes

        for i,window in enumerate(window_data['window']): 
            unique_data = {k.split('_')[0]:window_data[k][i] for k in ['ip_list','bytes_list']}
            seen = {'subnet':[], 'bytes':[]} # seen dictionary

            for i,ip in enumerate(unique_data['ip']): # go through each ip and assign to its subnet
                subnet = subnetValue(ip)
                if subnet not in seen['subnet']:
                    seen['subnet'].append(subnet)
                    seen['bytes'].append(0)
                    for iters, ip_ in enumerate(unique_data['ip']):
                        if(subnetValue(ip_)==subnet):
                            seen['bytes'][-1]+=unique_data['bytes'][iters]
                            
            subnet_window_data['window'].append(window)
            subnet_window_data['subnet_list'].append(seen['subnet'])
            subnet_window_data['bytes_list'].append(seen['bytes'])             
        return subnet_window_data
        

    def data_sort(self, data,sortby='bytes',address='ip', reverse=False): # sort data 
       # use address to sort ip data and subnet data  - reverse = False for ascending order
        data_combined = list(zip(data[address], data['bytes']))
        if(sortby=='bytes'): # if to sort by bytes
            data_combined_sorted = sorted(data_combined, key=lambda x:x[1],reverse=reverse)
        else: # if to sort by subnet/ip value
            data_combined_sorted = sorted(data_combined, key=lambda x:x[0],reverse=reverse)
    
        addresses_sorted, bytes_sorted = zip(*data_combined_sorted)
        return {address:addresses_sorted, 'bytes':bytes_sorted}
    
    