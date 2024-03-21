# ELENE6889
# Readme file for Assignment 1 
# pkk2125

The app has a class that has various methods to compute the required statistics

Initially, we load the data input to the class init function. Then, we compute the required statistics using the methods defined.
The code contains extensive comments that explain what each method does.

Here, a brief description is given.

IPlogreader: This is a class containing the dataloader and methods to compute statistics

load: This methods converts the input csv file to a dictionary with keys - ip, time, and bytes. 
This code revolves around manipulating this dictionary database
compute_bytes_per_ip: This returns a dictionary of unique ips and corresponding bytes
compute_bytes_per_ip_inHour: This returns a dict of unique ips and bytes for a given window of 1 hour
ip_topK_bytes: This returns a dict of unique ips and bytes of size 'K', sorted by number of bytes
groupBySubnet: Given data is grouped by subnet value. Can choose number of bytes per subnet using the numbytes parameter
compute_bytes_per_subnet_inHour: Compute statistics in 1 hour window for each subnet
data_sort: A method to sort the given data. use sortby to choose what key to sort dict by and address to choose if data is subnet or ip.
