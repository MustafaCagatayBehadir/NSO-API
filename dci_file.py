import pandas as pd


class DciFile:

    def __init__(self, file_name=None, tenant_list=[]):
        self.df_service_base = pd.read_excel(file_name, sheet_name="SERVICE BASE")
        self.df_service_base = self.df_service_base.astype({"SHARED TENANT": bool})  # convert columns to bool and str
        self.df_vrf = pd.read_excel(file_name, sheet_name="VRF")
        self.df_vrf = self.df_vrf.astype({"DEFAULT ORIGINATE": bool, "DISABLE PRIMARY RT": bool, "RP MANAGEMENT 888": bool, "VRF POLICY": bool})
        self.df_l3direct = pd.read_excel(file_name, sheet_name="L3DIRECT")
        self.df_l3direct = self.df_l3direct.astype({"SHUTDOWN": bool, "SERVICE POLICY": bool})
        self.df_l3direct_static = pd.read_excel(file_name, sheet_name="L3DIRECT STATIC")
        self.df_l3direct_bgp = pd.read_excel(file_name, sheet_name="L3DIRECT BGP")
        self.df_l3direct_bgp = self.df_l3direct_bgp.astype({"ENABLE MAX PATHS": bool, "BFD STATUS": bool, "BFD DISABLE FAST DETECT": bool, "NEXTHOPSELF": bool,
                                                            "REMOVE PRIVATE AS": bool, "DEFAULT ORIGINATE": bool, "SOFT RECONFIGURATION": bool, "SHUTDOWN": bool,
                                                            "LOCAL AS STATUS": bool, "LOCAL AS NO PREPEND": bool, "LOCAL AS REPLACE AS": bool, "CUSTOM TIMERS STATUS": bool})
        self.df_l2ext = pd.read_excel(file_name, sheet_name="L2EXTERNAL")
        self.tenant_list = tenant_list
        self.arp_info_dict_list = []
        self.route_info_dict_list = []
        self.static_route_info_dict_list = []
        self.bgp_route_info_dict_list = []
        self.mac_info_dict_list = []
        self.interface_info_dict_list = []

    def create_arp_info_dict_list(self):
        df = self.df_service_base
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            if tenant_name not in self.tenant_list:
                continue
            pod_number = str(int(df.loc[index]["POD"]))  #Convert float to int then int to string
            vrf_name = df.loc[index]["VRF NAME"]
            encap_id = str(int(df.loc[index]["ENCAP ID"]))  #Convert float to int then int to string
            if pod_number == "1":
                interface = f"Bundle-Ether11.{encap_id}"
            elif pod_number == "2":
                interface = f"Bundle-Ether14.{encap_id}"
            else:
                raise Exception("!!!Invalid POD Number!!!")
            arp_info_dict = {"Tenant Name": tenant_name, "Vrf Name": vrf_name, "Vlan": encap_id, "Interface": interface}
            if arp_info_dict not in self.arp_info_dict_list:
                self.arp_info_dict_list.append(arp_info_dict)

        return self.arp_info_dict_list

    def create_route_info_dict_list(self):
        df = self.df_service_base
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            if tenant_name not in self.tenant_list:
                continue
            vrf_name = df.loc[index]["VRF NAME"]
            if "int" not in vrf_name and "INT" not in vrf_name and "L2" not in vrf_name and "l2" not in vrf_name:
                command = f"show route vrf {vrf_name}"
                route_info_dict = {"Tenant Name": tenant_name, "Vrf Name": vrf_name, "Command": command}
                if route_info_dict not in self.route_info_dict_list:
                    self.route_info_dict_list.append(route_info_dict)

        return self.route_info_dict_list

    def create_static_info_dict_list(self):
        df = self.df_service_base
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            if tenant_name not in self.tenant_list:
                continue
            pod_number = str(int(df.loc[index]["POD"]))  #Convert float to int then int to string
            vrf_name = df.loc[index]["VRF NAME"]
            encap_id = str(int(df.loc[index]["ENCAP ID"]))  #Convert float to int then int to string
            if pod_number == "1":
                interface = f"Bundle-Ether11.{encap_id}"
            elif pod_number == "2":
                interface = f"Bundle-Ether14.{encap_id}"
            else:
                raise Exception("!!!Invalid POD Number!!!")
            if "int" in vrf_name or "INT" in vrf_name:
                command = f"show route next-hop {interface}"
                static_route_info_dict = {"Tenant Name": tenant_name, "Vrf Name": vrf_name,  "Command": command}
                if static_route_info_dict not in self.static_route_info_dict_list:
                    self.static_route_info_dict_list.append(static_route_info_dict)
            elif "L2" in vrf_name or "l2" in vrf_name:
                continue
            else:
                command = f"show route vrf {vrf_name} static"
                static_route_info_dict = {"Tenant Name": tenant_name, "Vrf Name": vrf_name, "Command": command}
                if static_route_info_dict not in self.static_route_info_dict_list:
                    self.static_route_info_dict_list.append(static_route_info_dict)

        return self.static_route_info_dict_list

    def create_bgp_route_info_dict_list(self):
        df_service = self.df_service_base
        df_bgp = self.df_l3direct_bgp
        for bgp_index in df_bgp.index.values:
            tenant_name = df_bgp.loc[bgp_index]["TENANT NAME"]
            if tenant_name not in self.tenant_list:
                continue
            service_name = df_bgp.loc[bgp_index]["SERVICE NAME"]
            encap_id = df_bgp.loc[bgp_index]["ENCAP ID"]
            bgp_peer = df_bgp.loc[bgp_index]["BGP PEER"]
            for service_index in df_service.index.values:
                if service_name == df_service.loc[service_index]["SERVICE NAME"]:
                    vrf_name = df_service.loc[service_index]["VRF NAME"]
                    if "int" in vrf_name or "INT" in vrf_name:
                        command = f"show bgp neighbors {bgp_peer} received routes"
                        bgp_info_dict = {"Tenant Name": tenant_name, "Vrf Name": vrf_name, "Vlan": encap_id, "Command": command}
                        if bgp_info_dict not in self.bgp_route_info_dict_list:
                            self.bgp_route_info_dict_list.append(bgp_info_dict)
                    elif "L2" in vrf_name or "l2" in vrf_name:
                        continue
                    else:
                        command = f"show bgp vrf {vrf_name} neighbors {bgp_peer} received routes"
                        bgp_info_dict = {"Tenant Name": tenant_name, "Vrf Name": vrf_name, "Vlan": encap_id, "Command": command}
                        if bgp_info_dict not in self.bgp_route_info_dict_list:
                            self.bgp_route_info_dict_list.append(bgp_info_dict)
        return self.bgp_route_info_dict_list

    def create_mac_info_dict_list(self):
        df = self.df_l2ext
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            if tenant_name not in self.tenant_list:
                continue
            encap_id = str(int(df.loc[index]["ENCAP ID"]))  #Convert float to int then int to string
            evi = str(int(df.loc[index]["EVI"]))  #Convert float to int then int to string
            command = f"show evpn evi vpn-id {evi} mac"
            mac_info_dict = {"Tenant Name": tenant_name, "Vlan": encap_id, "Evi": evi, "Command": command}
            if mac_info_dict not in self.mac_info_dict_list:
                self.mac_info_dict_list.append(mac_info_dict)

        return self.mac_info_dict_list

    def create_interface_info_dict_list(self):
        df_l3 = self.df_l3direct
        df_l2 = self.df_l2ext
        for index in df_l3.index.values:
            tenant_name = df_l3.loc[index]["TENANT NAME"]
            if tenant_name not in self.tenant_list:
                continue
            l3direct_name = df_l3.loc[index]["L3 DIRECT NAME"]
            encap_id = str(int(df_l3.loc[index]["ENCAP ID"]))  #Convert float to int then int to string
            if l3direct_name == "BLF_801_802_DCI_VPC_INTPOL":
                interface = f"Bundle-Ether11.{encap_id}"
                command = f"show interface Bundle-Ether11.{encap_id}"
                interface_info_dict = {"Tenant Name": tenant_name, "Interface": interface, "Command": command}
            elif l3direct_name == "BLF_803_804_DCI_VPC_INTPOL":
                interface = f"Bundle-Ether12.{encap_id}"
                command = f"show interface Bundle-Ether12.{encap_id}"
                interface_info_dict = {"Tenant Name": tenant_name, "Interface": interface, "Command": command}
            elif l3direct_name == "BLF_901_902_DCI_VPC_INTPOL":
                interface = f"Bundle-Ether14.{encap_id}"
                command = f"show interface Bundle-Ether14.{encap_id}"
                interface_info_dict = {"Tenant Name": tenant_name, "Interface": interface, "Command": command}
            else:
                raise Exception("!!!Invalid L3DIRECT Name!!!")
            if interface_info_dict not in self.interface_info_dict_list:
                self.interface_info_dict_list.append(interface_info_dict)
        for index in df_l2.index.values:
            tenant_name = df_l2.loc[index]["TENANT NAME"]
            if tenant_name not in self.tenant_list:
                continue
            l2ext_name = df_l2.loc[index]["DCI INTERFACE"]
            encap_id = str(int(df_l2.loc[index]["ENCAP ID"]))  #Convert float to int then int to string
            if l2ext_name == "BLF_801_802_DCI_VPC_INTPOL":
                interface = f"Bundle-Ether11.{encap_id}"
                command = f"show interface Bundle-Ether11.{encap_id}"
                interface_info_dict = {"Tenant Name": tenant_name, "Interface": interface, "Command": command}
            elif l2ext_name == "BLF_803_804_DCI_VPC_INTPOL":
                interface = f"Bundle-Ether12.{encap_id}"
                command = f"show interface Bundle-Ether12.{encap_id}"
                interface_info_dict = {"Tenant Name": tenant_name, "Interface": interface, "Command": command}
            elif l2ext_name == "BLF_901_902_DCI_VPC_INTPOL":
                interface = f"Bundle-Ether14.{encap_id}"
                command = f"show interface Bundle-Ether14.{encap_id}"
                interface_info_dict = {"Tenant Name": tenant_name, "Interface": interface, "Command": command}
            else:
                raise Exception("!!!Invalid L2EXT Name!!!")
            if interface_info_dict not in self.interface_info_dict_list:
                self.interface_info_dict_list.append(interface_info_dict)

        return self.interface_info_dict_list
