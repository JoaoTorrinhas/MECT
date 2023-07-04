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
import ipaddress


def is_unusual_country(cc, normal_country_codes):
    return cc not in normal_country_codes

# Check if value1 is 60% greater than value2
def is_value_greater(value1, value2):
    difference = value1 - value2
    percentage_increase = (difference / value2) * 100

    if percentage_increase >= 60:
        return True
    else:
        return False


datafile_dataset5='dataset5/data5.parquet'
datafile_test5 = 'dataset5/test5.parquet'


### IP geolocalization
gi=pygeoip.GeoIP('GeoIP_DBs/GeoIP.dat')
gi2=pygeoip.GeoIP('GeoIP_DBs/GeoIPASNum.dat')

# Read parquet data files
data_dataset5=pd.read_parquet(datafile_dataset5)
#print(data_dataset5.to_string())

# Read parquet data files
data_test=pd.read_parquet(datafile_test5)
#print(data_test.to_string())



######################################### Análise do dataset normal #########################################
#TODO: Para testar esta análise, descomentar esta e comentar as outras para não demorar muito nem dar muitos resultados ao mesmo tempo


# Identify the most commonly used ports and their frequencies to gain an understanding of the port usage patterns.
port_counts = data_dataset5['port'].value_counts()
print("Port Distribution: ", port_counts)
plt.figure(figsize=(10, 6))
plt.bar(port_counts.index, port_counts.values)
plt.xlabel('Destination Port')
plt.ylabel('Frequency')
plt.title('Port Distribution')
plt.xticks(rotation=90)
plt.show()

# Determine the distribution of protocols (TCP or UDP) used in the dataset. Count the occurrences of each protocol to see the relative prevalence of each.
protocol_counts = data_dataset5['proto'].value_counts()

plt.figure(figsize=(8, 6))
plt.bar(protocol_counts.index, protocol_counts)
plt.xlabel('Protocol')
plt.ylabel('Count')
plt.title('Protocol Distribution')
plt.xticks(rotation=90)
plt.show()

# Top Source IP Addresses
top_source_ips = data_dataset5['src_ip'].value_counts().head(10)
print("Top Source IP Addresses: ", top_source_ips)
plt.figure(figsize=(10, 6))
plt.bar(top_source_ips.index, top_source_ips.values)
plt.xlabel('Source IP')
plt.ylabel('Frequency')
plt.title('Top Source IP Addresses')
plt.xticks(rotation=90)
plt.show()

# Top Destination IP Addresses
top_destination_ips = data_dataset5['dst_ip'].value_counts().head(10)
print("Top Destination IP Addresses: ", top_destination_ips)
plt.figure(figsize=(10, 6))
plt.bar(top_destination_ips.index, top_destination_ips.values)
plt.xlabel('Destination IP')
plt.ylabel('Frequency')
plt.title('Top Destination IP Addresses')
plt.xticks(rotation=90)
plt.show()


# Traffic Volume for different periods of time

# Convert the timestamp to a datetime object
data_dataset5['timestamp'] = pd.to_datetime(data_dataset5['timestamp'], unit='s')

# Extract the hour from the timestamp
data_dataset5['hour'] = data_dataset5['timestamp'].dt.hour
#print(data_dataset5['hour'])

# Calculate the total traffic volume (upload + download bytes) for each hour
traffic_by_hour = data_dataset5.groupby('hour')[['up_bytes', 'down_bytes']].sum()
print(traffic_by_hour)

# Plotting the traffic volume by hour
plt.figure(figsize=(10, 6))
x = list(range(24)) # 24 hours in a day
bar_width = 0.35  # Width of each bar

plt.bar(x, traffic_by_hour['up_bytes'], width=bar_width, label='Upload Bytes')
plt.bar([i + bar_width for i in x], traffic_by_hour['down_bytes'], width=bar_width, label='Download Bytes')

plt.xlabel('Hour of Day')
plt.ylabel('Traffic Volume (Bytes)')
plt.title('Traffic Volume by Hour')
plt.xticks([i + bar_width/2 for i in x], x) 
plt.legend()
plt.show()



######################################### Botnets #########################################
#TODO: Para testar esta análise, descomentar esta e comentar as outras para não demorar muito nem dar muitos resultados ao mesmo tempo

# #Calculate average of download and upload bytes
# avg_down_bytes_total = data_dataset5['down_bytes'].mean()
# avg_up_bytes_total = data_dataset5['up_bytes'].mean()

# #Find private ip addresses
# NET=ipaddress.IPv4Network('192.168.105.0/24')
# bprivate=data_dataset5.apply(lambda x: ipaddress.IPv4Address(x['dst_ip']) in NET,axis=1)
# bprivate_test=data_test.apply(lambda x: ipaddress.IPv4Address(x['dst_ip']) in NET,axis=1)

# # Find unique destination IP addresses in the test dataset that are private
# test_destinations_private = set(data_test[bprivate_test]['dst_ip'])

# # Find unique destination IP addresses in the normal dataset that are private
# normal_destinations_private = set(data_dataset5[bprivate]['dst_ip'])

# # Initialize a list to store botnet source IP addresses
# botnet_sources = []

# # Iterate over each private destination IP address in the test dataset
# for destination_ip in test_destinations_private:
#     # Get the source IP addresses in the test dataset for the current destination IP
#     test_sources = set(data_test[data_test['dst_ip'] == destination_ip]['src_ip'])
#     print("Destination IP: ", destination_ip)
#     print("test_sources: ", test_sources)
    
#     # Get the source IP addresses in the normal dataset for the current destination IP
#     normal_sources = set(data_dataset5[data_dataset5['dst_ip'] == destination_ip]['src_ip'])
#     print("Destination IP: ", destination_ip)
#     print("normal_sources: ", normal_sources)
    
#     # Find the source IP addresses that are in the test dataset but not in the normal dataset
#     botnet_sources.extend(list(test_sources - normal_sources))

# # Remove duplicates from the list of botnet source IP addresses
# botnet_sources = list(set(botnet_sources))
# print("Botnet Sources: ", botnet_sources)

# mean_down_bytes = []
# mean_up_bytes = []
# for ip_address in botnet_sources:
#     # Calculate the mean download and upload bytes for the current IP address
#     mean_down_bytes.append(data_test[data_test['src_ip'] == ip_address]['down_bytes'].mean())
#     mean_up_bytes.append(data_test[data_test['src_ip'] == ip_address]['up_bytes'].mean())


# # Plotting the means
# plt.figure(figsize=(10, 6))
# plt.plot(range(len(botnet_sources)), mean_down_bytes, 'bo-', label='Mean Download Bytes')
# plt.plot(range(len(botnet_sources)), mean_up_bytes, 'go-', label='Mean Upload Bytes')
# plt.axhline(y=avg_down_bytes_total, color='b', linestyle='--', label='Overall Mean Download Bytes')
# plt.axhline(y=avg_up_bytes_total, color='g', linestyle='--', label='Overall Mean Upload Bytes')
# plt.xlabel('Source IP')
# plt.ylabel('Mean Bytes')
# plt.title('Mean Download and Upload Bytes for Botnet Sources')
# plt.legend()
# plt.xticks(range(len(botnet_sources)), botnet_sources, rotation=90)
# plt.subplots_adjust(bottom=0.2)  # Adjust the bottom margin to make space for the subtitle
# plt.show()

######################################### Países esquisitos (demora por volta de 15/20 min a efetuar todas as comparações)#########################################
#TODO: Para testar esta análise, descomentar esta e comentar as outras para não demorar muito nem dar muitos resultados ao mesmo tempo

# #Calculate average of download and upload bytes
# avg_down_bytes_total = data_dataset5['down_bytes'].mean()
# avg_up_bytes_total = data_dataset5['up_bytes'].mean()


# #Is destination IPv4 a public address?
# NET=ipaddress.IPv4Network('192.168.105.0/24') #192.168.0.0/16
# bpublic=data_dataset5.apply(lambda x: ipaddress.IPv4Address(x['dst_ip']) not in NET,axis=1)
# #print(data_dataset5[bpublic]['dst_ip'])

# bpublic_test=data_test.apply(lambda x: ipaddress.IPv4Address(x['dst_ip']) not in NET,axis=1)

# #Geolocalization of public destination adddress
# cc=data_dataset5[bpublic]['dst_ip'].apply(lambda y:gi.country_code_by_addr(y)).to_frame(name='cc')
# cc_array = cc['cc'].array.unique()
# print("CC NORMAL",cc_array)

# cc_test = data_test[bpublic_test]['dst_ip'].apply(lambda y:gi.country_code_by_addr(y)).to_frame(name='cc')
# cc_array_test = cc_test['cc'].array.unique()
# print("CC WITH ANOMALIES",cc_array_test)

# avg_down_bytes_cc = []
# avg_up_bytes_cc = []
# unusual_countries = []
# for cc in cc_array_test:
#     if cc not in cc_array:
#         # Filter the data_test for the current country code to get the information of it
#         cc_data = data_test[data_test['dst_ip'].apply(lambda ip: gi.country_code_by_addr(ip)) == cc]
#         #print(cc_data)  
        
#         # Calculate the average downloaded bytes and uploaded bytes for this country
#         #avg_down_bytes_cc = cc_data['down_bytes'].mean()
#         #avg_up_bytes_cc = cc_data['up_bytes'].mean()
        
#         avg_down_bytes_cc.append(cc_data['down_bytes'].mean())
#         avg_up_bytes_cc.append(cc_data['up_bytes'].mean())
#         unusual_countries.append(cc)
#         # print("Avg has been calculated for this cc, download-> ", avg_down_bytes_cc) 
#         # print("Avg has been calculated for this cc, upload-> ", avg_up_bytes_cc)   
        
#         # # Check if the average downloaded bytes and uploaded bytes for this country are 50% greater/lower than the overall average
#         # if (avg_down_bytes_cc > 0.5 * avg_down_bytes_total or avg_down_bytes_cc < 0.5 * avg_down_bytes_total) or (avg_up_bytes_cc > 0.5 * avg_up_bytes_total or avg_up_bytes_cc < 0.5 * avg_up_bytes_total):        
#         #     unusual_countries.append(cc)

# print("Unusual Countries: ", unusual_countries)

# # Plot the graph
# plt.figure(figsize=(10, 6))
# plt.bar(unusual_countries, avg_down_bytes_cc, label='Average Download Bytes')
# plt.bar(unusual_countries, avg_up_bytes_cc, label='Average Upload Bytes')
# plt.axhline(y=avg_down_bytes_total, color='red', linestyle='--', label='Overall Average Download Bytes')
# plt.axhline(y=avg_up_bytes_total, color='green', linestyle='--', label='Overall Average Upload Bytes')
# plt.xlabel('Country Code (cc)')
# plt.ylabel('Average Bytes')
# plt.title('Average Download and Upload Bytes by Unusual Country')

# # Add subtitles for each bar
# for i in range(len(unusual_countries)):
#     plt.text(i, avg_down_bytes_cc[i], f"CC: {unusual_countries[i]}", ha='center')

# plt.legend()
# plt.show()

