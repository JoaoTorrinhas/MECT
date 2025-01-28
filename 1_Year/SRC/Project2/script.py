# pip install pygeoip
# pip install fastparquet 
# pip install dnspython
import pandas as pd
import numpy as np
import ipaddress
import dns.resolver
import dns.reversename
import pygeoip
import matplotlib.pyplot as plt 


datafile1= 'data5.parquet'
datafile='test5.parquet'

### IP geolocalization
gi=pygeoip.GeoIP('./GeoIP.dat')
gi2=pygeoip.GeoIP('./GeoIPASNum.dat')
addr='193.136.73.21'
cc=gi.country_code_by_addr(addr)
org=gi2.org_by_addr(addr)
print(cc,org)


### Read parquet data files
data=pd.read_parquet(datafile)
data1=pd.read_parquet(datafile1)



##############################

NET = ipaddress.IPv4Network('192.168.105.0/24')

private_data1 = data1[(data1['dst_ip'].apply(lambda x: ipaddress.IPv4Address(x) in NET)) ]

private_data = data[(data['dst_ip'].apply(lambda x: ipaddress.IPv4Address(x) in NET)) ]


download_bytes_ratio_data1 = private_data1['down_bytes'] / private_data1['up_bytes']
avg_ratio_data1 = download_bytes_ratio_data1.mean()
print("avg ratio", avg_ratio_data1)

download_bytes_ratio_data = private_data['down_bytes'] / private_data['up_bytes']

# Verify if download_bytes_ratio_data is 4 times higher than the average
is_ratio_higher = download_bytes_ratio_data > (3 * avg_ratio_data1)

# Filter data where ratio is higher
high_ratio_data = private_data[is_ratio_higher]

# Print the filtered data
print(high_ratio_data)
high_ratio_data.to_csv('high_ratio_data.csv', index=False) 


#####################


#descomentar bloco de baixo e comentar bloco de cima para testar

"""  #detect C&C
# Find private IP addresses
NET = ipaddress.IPv4Network('192.168.105.0/24')

# Filter the data based on private addresses and port 53
private_data1 = data1[(data1['src_ip'].apply(lambda x: ipaddress.IPv4Address(x) in NET)) & (data1['port'] == 53)]
private_data = data[(data['src_ip'].apply(lambda x: ipaddress.IPv4Address(x) in NET)) & (data['port'] == 53)]

# Count the number of connections from each source IP to private destination IPs
connection_counts_data1 = private_data1['src_ip'].value_counts().reset_index()
connection_counts_data1.columns = ['src_ip', 'connection_count_data1']
connection_counts_data1.to_csv('connection_counts_data1.csv', index=False)

connection_counts_data = private_data['src_ip'].value_counts().reset_index()
connection_counts_data.columns = ['src_ip', 'connection_count_data']
connection_counts_data.to_csv('connection_counts_data.csv', index=False)

# Merge the connection counts from both dataframes based on the source IP
merged_data = pd.merge(connection_counts_data1, connection_counts_data, on='src_ip', how='inner')

merged_data.to_csv('merged_data.csv', index=False)

# Filter the merged data to keep only the IP addresses with connection counts four times higher
filtered_data = merged_data[merged_data['connection_count_data'] > (4 * merged_data['connection_count_data1'])]

print("C&C DETECION")
filtered_data.to_csv('aumento.csv', index=False)
print("aumento exponencial")
print(filtered_data)

# Filter the merged data to keep only the IP addresses with connection counts four times higher
filtered_data2 = merged_data[merged_data['connection_count_data'] < (0.25 * merged_data['connection_count_data1'])]

filtered_data2.to_csv('decremento.csv', index=False)
print("decremento exponencial")
print(filtered_data2)  """









