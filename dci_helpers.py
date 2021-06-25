def arp_parser(command_output_list=[], arp_info_dict_list=[]):
    d_list = []
    for arp_info_dict in arp_info_dict_list:
        tenant_name = arp_info_dict["Tenant Name"]
        vrf_name = arp_info_dict["Vrf Name"]
        vlan = arp_info_dict["Vlan"]
        interface = arp_info_dict["Interface"]
        for line in command_output_list:
            line = line.strip()
            line_list = line.split()
            if interface in line and "Dynamic" in line and interface == line_list[5]:
                line_list = line.split()
                ip = line_list[0]
                mac = line_list[2]
                d = {"TENANT NAME": tenant_name, "VRF NAME": vrf_name, "VLAN": vlan, "IP": ip, "MAC": mac, "INTERFACE": interface}
                if d not in d_list:
                    d_list.append(d)

    return d_list


def route_parser(command_output_list, tenant_name, vrf_name):
    d_list = []
    for line in command_output_list:
        line = line.strip()
        if "." in line and "/" in line:
            line_list = line.split()
            if "C" in line_list[0]:
                continue
            elif "L" in line_list[0]:
                continue
            elif "S" in line_list[0]:
                protocol = "Static"
            elif "B" in line_list[0]:
                protocol = "BGP"
            else:
                protocol = "Other"
            prefix = line_list[1]
            d = {"TENANT NAME": tenant_name, "VRF NAME": vrf_name, "PREFIX": prefix, "PROTOCOL": protocol}
            if d not in d_list:
                d_list.append(d)

    return d_list


def static_route_parser(command_output_list, tenant_name, vrf_name):
    d_list = []
    for line in command_output_list:
        line = line.strip()
        if "." in line and "/" in line:
            line_list = line.split()
            if "S" == line_list[0]:
                prefix = line_list[1]
                nexthop = line_list[4].strip(",")
                d = {"TENANT NAME": tenant_name, "VRF NAME": vrf_name, "PREFIX": prefix, "NEXTHOP": nexthop}
                if d not in d_list:
                    d_list.append(d)
            if "S*" == line_list[0]:
                prefix = line_list[1]
                nexthop = line_list[4].strip(",")
                d = {"TENANT NAME": tenant_name, "VRF NAME": vrf_name, "PREFIX": prefix, "NEXTHOP": nexthop}
                if d not in d_list:
                    d_list.append(d)

    return d_list


def bgp_route_parser(command_output_list, tenant_name, vrf_name, vlan):
    d_list = []
    for line in command_output_list:
        line = line.strip()
        if "." in line and "/" in line:
            line_list = line.split()
            if "*" == line_list[0]:
                prefix = line_list[1]
                nexthop = line_list[2]
                d = {"TENANT NAME": tenant_name, "VRF NAME": vrf_name, "VLAN": vlan, "PREFIX": prefix, "NEXTHOP": nexthop}
                if d not in d_list:
                    d_list.append(d)

    return d_list


def mac_parser(command_output, tenant_name, vlan, evi_id):
    d_list = []
    for line in command_output:
        line = line.strip()
        if "MPLS" in line:
            line_list = line.split()
            mac_address = line_list[2]
            ip_address = line_list[3]
            next_hop = line_list[4]
            if "Bundle" in line:
                mac_type = "FABRIC"
            else:
                mac_type = "EVPN"
            d = {"TENANT NAME": tenant_name, "VLAN": vlan, "MAC": mac_address, "IP": ip_address, "NEXTHOP": next_hop, "TYPE": mac_type, "EVI": evi_id}
            if d not in d_list:
                d_list.append(d)

    return d_list


def interface_parser(command_output, tenant_name, interface):
    d_list = []
    flag = False
    for line in command_output:
        if "Layer 2 Transport Mode" in line:
            flag = True
    if flag:
        input_bytes = 0; input_packets = 0; output_bytes = 0; output_packets = 0; input_drops = 0; output_drops = 0
        for line in command_output:
            line = line.strip()
            if "packets input" in line:
                line_list = line.split()
                input_bytes = line_list[3]
                input_packets = line_list[0]
            elif "packets output" in line:
                line_list = line.split()
                output_bytes = line_list[3]
                output_packets = line_list[0]
            elif "input drops" in line:
                line_list = line.split()
                input_drops = line_list[0]
            elif "output drops" in line:
                line_list = line.split()
                output_drops = line_list[0]
            else:
                continue
        d = {"TENANT NAME": tenant_name, "INTERFACE": interface, "INPUT BYTES": input_bytes, "INPUT PACKETS": input_packets, "OUTPUT BYTES": output_bytes, "OUTPUT PACKTES": output_packets, "INPUT DROPS": input_drops, "OUTPUT DROPS": output_drops}
        if d not in d_list:
            d_list.append(d)
    else:
        input_bps = 0; input_pps = 0; output_bps = 0; output_pps = 0; input_drops = 0; output_drops = 0
        for line in command_output:
            line = line.strip()
            if "input rate" in line:
                line_list = line.split()
                input_bps = line_list[4]
                input_pps = line_list[6]
            elif "output rate" in line:
                line_list = line.split()
                output_bps = line_list[4]
                output_pps = line_list[6]
            elif "input drops" in line:
                line_list = line.split()
                input_drops = line_list[5]
            elif "output drops" in line:
                line_list = line.split()
                output_drops = line_list[5]
            else:
                continue
        d = {"TENANT NAME": tenant_name, "INTERFACE": interface, "INPUT BPS": input_bps, "INPUT PPS": input_pps, "OUTPUT BPS": output_bps, "OUTPUT PPS": output_pps, "INPUT DROPS": input_drops, "OUTPUT DROPS": output_drops}
        if d not in d_list:
            d_list.append(d)

    return d_list


def bgp_neighbor_session_parser(vrf, neighbor, command_output_1_list, command_output_2_list):
    accepted = 0; bestpath = 0; state = ""
    for line in command_output_1_list:
        if "BGP state =" in line:
            state = line.split()[3].strip(",")
        elif "accepted prefixes" in line:
            accepted = line.split()[0]
            bestpath = line.split()[3]
    i = 0
    for line in command_output_2_list:
        if "/" in line:
            i += 1
    d = {"NEIGHBOR": neighbor, "VRF": vrf, "STATE": state, "ACCEPTED ROUTES": accepted, "BESTPATHS": bestpath, "ADVERTISED ROUTES": str(i)}

    return d


def netmiko_bgp_neighbor_session_parser(command_output_1_list, command_output_2_list):
    accepted = 0; bestpath = 0; state = ""
    for line in command_output_1_list:
        if "BGP state =" in line:
            state = line.split()[3].strip(",")
        elif "accepted prefixes" in line:
            accepted = line.split()[0]
            bestpath = line.split()[3]
    i = 0
    for line in command_output_2_list:
        if "/" in line:
            i += 1

    return state, accepted, bestpath, str(i)
