import scapy.all as scapy

def scan_network(network):
    arp_request = scapy.ARP(pdst=network)
    ether = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp_request

    answered, _ = scapy.srp(
        packet,
        timeout=1,
        verbose=False
    )

    devices = []

    for sent, received in answered:
        devices.append({
            "ip": received.psrc,
            "mac": received.hwsrc
        })

    return devices


def print_result(devices):
    print("IP Address\t\tMAC Address")
    print("------------------------------------------")

    for device in devices:
        print(f"{device['ip']}\t\t{device['mac']}")


scan_result = scan_network("10.0.2.1/24")
print_result(scan_result)