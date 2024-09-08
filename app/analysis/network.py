from scapy.all import rdpcap, IP

def analyze_network_traffic(pcap_path):
    packets = rdpcap(pcap_path)
    network_data = []
    for packet in packets:
        if packet.haslayer(IP):
            ip_src = packet[IP].src
            ip_dst = packet[IP].dst
            network_data.append({'src': ip_src, 'dst': ip_dst})
    return network_data
