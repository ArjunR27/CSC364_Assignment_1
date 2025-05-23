import socket
import sys
import time
import os
import glob


# Helper Functions

# The purpose of this function is to set up a socket connection.
def create_socket(host, port):
    # 1. Create a socket.
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 2. Try connecting the socket to the host and port.
    try:
        soc.connect((host, port))
    except:
        print("Connection Error to", port)
        sys.exit()
    # 3. Return the connected socket.
    return soc


# The purpose of this function is to read in a CSV file.
def read_csv(path):
    # 1. Open the file for reading.
    table_file = open(path, "r")
    # 2. Store each line.
    table = table_file.readlines()
    # 3. Create an empty list to store each processed row.
    table_list = []
    # 4. For each line in the file:
    for line in table: 
        # 5. split it by the delimiter,
        split_line = line.split(",")
        # 6. remove any leading or trailing spaces in each element, and
        cleaned = []
        for element in split_line:
            cleaned.append(element.strip())
            # 7. append the resulting list to table_list.
        table_list.append(cleaned)
    # 8. Close the file and return table_list.
    table_file.close()
    return table_list


# The purpose of this function is to find the default port
# when no match is found in the forwarding table for a packet's destination IP.
def find_default_gateway(table):
    # 1. Traverse the table, row by row,
    ## for ...:
        # 2. and if the network destination of that row matches 0.0.0.0,
        ## if ...:
            # 3. then return the interface of that row.
            ## return ...
    for row in table:
        if row[0] == '0.0.0.0':
            return row[-1]

# The purpose of this function is to generate a forwarding table that includes the IP range for a given interface.
# In other words, this table will help the router answer the question:
# Given this packet's destination IP, which interface (i.e., port) should I send it out on?
def generate_forwarding_table_with_range(table):
    # 1. Create an empty list to store the new forwarding table.
    new_table = []
    # 2. Traverse the old forwarding table, row by row,
    for row in table:
        # 3. and process each network destination other than 0.0.0.0
        # (0.0.0.0 is only useful for finding the default port).
        if row[0] != '0.0.0.0':
            # 4. Store the network destination and netmask.
            network_dst_string = row[0]
            netmask_string = row[1]
            # 5. Convert both strings into their binary representations.
            network_dst_bin = ip_to_bin(network_dst_string)
            netmask_bin = ip_to_bin(netmask_string)
            # 6. Find the IP range.
            ip_range = find_ip_range(network_dst_bin, netmask_bin)
            # 7. Build the new row.
            new_row = [ip_range[0], ip_range[1], row[-2], row[-1]]
            # 8. Append the new row to new_table.
            new_table.append(new_row)
    # 9. Return new_table.
    return new_table


# The purpose of this function is to convert a string IP to its binary representation.
def ip_to_bin(ip):
    # 1. Split the IP into octets.
    ip_octets = ip.split(".")
    # 2. Create an empty string to store each binary octet.
    ip_bin_string = ""
    # 3. Traverse the IP, octet by octet,
    for octet in ip_octets:
        # 4. and convert the octet to an int,
        int_octet = int(octet)
        # 5. convert the decimal int to binary,
        bin_octet = bin(int_octet)
        # 6. convert the binary to string and remove the "0b" at the beginning of the string,
        bin_octet_string = str(bin_octet)[2:]
        # 7. while the sting representation of the binary is not 8 chars long,
        # then add 0s to the beginning of the string until it is 8 chars long
        # (needs to be an octet because we're working with IP addresses).
        while len(bin_octet_string) != 8:
            bin_octet_string = "0" + bin_octet_string
        # 8. Finally, append the octet to ip_bin_string.
        ip_bin_string += bin_octet_string
    # 9. Once the entire string version of the binary IP is created, convert it into an actual binary int.
    # ip_int = int(ip_bin_string, 2)
    # 10. Return the binary representation of this int.
    return ip_bin_string


# The purpose of this function is to find the range of IPs inside a given a destination IP address/subnet mask pair.
def find_ip_range(network_dst, netmask):
    network_dst_int = int(network_dst, 2)
    netmask_int = int(netmask, 2)
    # 1. Perform a bitwise AND on the network destination and netmask
    # to get the minimum IP address in the range.

    minimum_ip_address_int = network_dst_int & netmask_int
    ## bitwise_and = ...
    # 2. Perform a bitwise NOT on the netmask
    # to get the number of total IPs in this range.
    num_total_ips = bit_not(netmask_int)
    # Because the built-in bitwise NOT or compliment operator (~) works with signed ints,
    # we need to create our own bitwise NOT operator for our unsigned int (a netmask).
    # 3. Add the total number of IPs to the minimum IP
    # to get the maximum IP address in the range.

    maximum_ip_address_int = minimum_ip_address_int + num_total_ips
    # 4. Return a list containing the minimum and maximum IP in the range.

    min_ip = bin(minimum_ip_address_int)[2:]
    max_ip = bin(maximum_ip_address_int)[2:]
    return [min_ip, max_ip]


# The purpose of this function is to perform a bitwise NOT on an unsigned integer.
def bit_not(n, numbits=32):
    return (1 << numbits) - 1 - n


# The purpose of this function is to write packets/payload to file.
def write_to_file(path, packet_to_write, send_to_router=None):
    # 1. Open the output file for appending.
    out_file = open(path, "a")
    # 2. If this router is not sending, then just append the packet to the output file.
    if not send_to_router:
        out_file.write(packet_to_write + "\n")
    # 3. Else if this router is sending, then append the intended recipient, along with the packet, to the output file.
    else:
        out_file.write(packet_to_write + " " + "to Router " + send_to_router + "\n")
    # 4. Close the output file.
    out_file.close()


# Main Program

# 0. Remove any output files in the output directory
# (this just prevents you from having to manually delete the output files before each run).
files = glob.glob('./output/*')
for f in files:
    os.remove(f)

# 1. Connect to the appropriate sending ports (based on the network topology diagram).

socket_2 = create_socket('127.0.0.1',8002)
socket_4 = create_socket('127.0.0.1',8004)

# 2. Read in and store the forwarding table.
forwarding_table = read_csv('./input/router_1_table.csv')
# 3. Store the default gateway port.
default_gateway_port = find_default_gateway(forwarding_table)
# 4. Generate a new forwarding table that includes the IP ranges for matching against destination IPS.
forwarding_table_with_range = generate_forwarding_table_with_range(forwarding_table)

# 5. Read in and store the packets.
packets_table = read_csv('./input/packets.csv')

# 6. For each packet,
for packet in packets_table:
    # 7. Store the source IP, destination IP, payload, and TTL.
    sourceIP = packet[0]
    destinationIP = packet[1]
    payload = packet[2]
    ttl = packet[3]

    # 8. Decrement the TTL by 1 and construct a new packet with the new TTL.

    new_ttl = int(ttl) - 1
    new_packet = [sourceIP, destinationIP, payload, str(new_ttl)]

    if new_ttl == 0:
        print("DISCARD:", new_packet)
        packet_str = ",".join(map(str, new_packet))
        write_to_file("./output/discarded_by_router_1.txt", packet_str)
        continue

    # 9. Convert the destination IP into an integer for comparison purposes.
    destinationIP_bin = ip_to_bin(destinationIP)
    destinationIP_int = int(destinationIP_bin, 2)
    ## destinationIP_bin = ...
    ## destinationIP_int = ...
        
    # 9. Find the appropriate sending port to forward this new packet to.
    sending_port = 0
    gateway = None
    for element in forwarding_table_with_range:
        if int(element[0], 2) <= destinationIP_int <= int(element[1], 2):
            gateway = element[2]
            sending_port = element[3]
    
    # 10. If no port is found, then set the sending port to the default port.
    ## ...
    if sending_port == 0:
        sending_port = default_gateway_port


    # 11. Either
    # (a) send the new packet to the appropriate port (and append it to sent_by_router_1.txt),
    # (b) append the payload to out_router_1.txt without forwarding because this router is the last hop, or
    # (c) append the new packet to discarded_by_router_1.txt and do not forward the new packet
    if sending_port == '8002':
        print("sending packet", new_packet, "to Router 2")
        packet_str = ",".join(map(str, new_packet))
        socket_2.sendall(packet_str.encode())
        write_to_file("./output/sent_by_router_1.txt", packet_str, "2")
    elif sending_port == '8004':
        print("sending packet", new_packet, "to Router 4")
        packet_str = ",".join(map(str, new_packet))
        socket_4.sendall(packet_str.encode())
        write_to_file("./output/sent_by_router_1.txt", packet_str, "4")
    elif sending_port == '127.0.0.1' and gateway == '127.0.0.1':
        print("OUT:", payload)
        write_to_file("./output/out_router_1.txt", payload)
    else:
        print("DISCARD:", new_packet)
        packet_str = ",".join(map(str, new_packet))
        write_to_file("./output/discarded_by_router_1.txt", packet_str)

    time.sleep(1)
