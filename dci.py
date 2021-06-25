from dci_file import DciFile
from netmiko import Netmiko
from time import sleep, strftime
import dci_helpers as helpers
import pandas as pd


class Dci(DciFile):

    def __init__(self, host="127.0.0.1", file_name=None, tenant_list=[]):
        super().__init__(file_name, tenant_list)
        self.host = host
        self.file_name = file_name
        self.tenant_list = tenant_list
        self.net_connect = None
        self.arp_command_list = ["show arp", "show arp vrf all"]
        self.d_arp = {}
        self.d_route = {}
        self.d_static_route = {}
        self.d_bgp_route = {}
        self.d_mac_address = {}
        self.d_interface_statistics = {}
        self.df_arp_postcheck = pd.DataFrame()
        self.df_route_postcheck = pd.DataFrame()
        self.df_static_route_postcheck = pd.DataFrame()
        self.df_bgp_route_postcheck = pd.DataFrame()
        self.df_mac_postcheck = pd.DataFrame()
        self.df_interface_postcheck = pd.DataFrame()
        self.df_summary_postcheck = pd.DataFrame()
        self.df_vrf_summary_postcheck = pd.DataFrame()
        self.df_evi_summary_postcheck = pd.DataFrame()

    def netmiko_dci(self):
        try:
            dci = {"device_type": "cisco_xr", "ip": self.host, "username": "DNSERVICES_RO", "password": "VRTat635"}
            self.net_connect = Netmiko(**dci)
            print(f"{self.host} ; CONNECTION ESTABLISHED")
        except Exception as err:
            raise Exception(err)

    def create_arp_postcheck(self):
        d_arp_list = []
        arp_info_dict_list = self.create_arp_info_dict_list()
        for arp_command in self.arp_command_list:
            print(arp_command)
            command_output = self.net_connect.send_command(arp_command)
            sleep(1)
            print(command_output)
            d_arp_list.extend(helpers.arp_parser(command_output.splitlines(), arp_info_dict_list))
        i = 0
        for d_dict in d_arp_list:
            self.d_arp.update({i: d_dict})
            i += 1
        if not self.d_arp:
            self.d_arp = {0: {"TENANT NAME": "", "VRF NAME": "", "VLAN": "", "IP": "", "MAC": "", "INTERFACE": ""}}

    def create_route_postcheck(self):
        d_route_list = []
        route_info_dict_list = self.create_route_info_dict_list()
        for route_info_dict in route_info_dict_list:
            tenant_name = route_info_dict["Tenant Name"]
            vrf_name = route_info_dict["Vrf Name"]
            route_command = route_info_dict["Command"]
            print(route_command)
            command_output = self.net_connect.send_command(route_command)
            sleep(1)
            print(command_output)
            d_route_list.extend(helpers.route_parser(command_output.splitlines(), tenant_name, vrf_name))
        i = 0
        for d_dict in d_route_list:
            self.d_route.update({i: d_dict})
            i += 1
        if not self.d_route:
            self.d_route = {0: {"TENANT NAME": "", "VRF NAME": "", "VLAN": "", "PREFIX": "", "PROTOCOL": ""}}

    def create_static_route_postcheck(self):
        d_static_route_list = []
        static_route_info_dict_list = self.create_static_info_dict_list()
        for static_route_info_dict in static_route_info_dict_list:
            tenant_name = static_route_info_dict["Tenant Name"]
            vrf_name = static_route_info_dict["Vrf Name"]
            static_route_command = static_route_info_dict["Command"]
            print(static_route_command)
            command_output = self.net_connect.send_command(static_route_command)
            sleep(1)
            print(command_output)
            d_static_route_list.extend(helpers.static_route_parser(command_output.splitlines(), tenant_name, vrf_name))
        i = 0
        for d_dict in d_static_route_list:
            self.d_static_route.update({i: d_dict})
            i += 1
        if not self.d_static_route:
            self.d_static_route = {0: {"TENANT NAME": "", "VRF NAME": "", "VLAN": "", "PREFIX": "", "PROTOCOL": ""}}

    def create_bgp_route_postcheck(self):
        d_bgp_route_list = []
        bgp_route_info_dict_list = self.create_bgp_route_info_dict_list()
        for bgp_route_info_dict in bgp_route_info_dict_list:
            tenant_name = bgp_route_info_dict["Tenant Name"]
            vrf_name = bgp_route_info_dict["Vrf Name"]
            vlan = bgp_route_info_dict["Vlan"]
            bgp_route_command = bgp_route_info_dict["Command"]
            print(bgp_route_command)
            command_output = self.net_connect.send_command(bgp_route_command)
            sleep(1)
            print(command_output)
            d_bgp_route_list.extend(helpers.bgp_route_parser(command_output.splitlines(), tenant_name, vrf_name, vlan))
        i = 0
        for d_dict in d_bgp_route_list:
            self.d_bgp_route.update({i: d_dict})
            i += 1
        if not self.d_bgp_route:
            self.d_bgp_route = {0: {"TENANT NAME": "", "VRF NAME": "", "VLAN": "", "PREFIX": "", "PROTOCOL": ""}}

    def create_mac_address_postcheck(self):
        d_mac_address_list = []
        mac_info_dict_list = self.create_mac_info_dict_list()
        for mac_info_dict in mac_info_dict_list:
            tenant_name = mac_info_dict["Tenant Name"]
            vlan = mac_info_dict["Vlan"]
            evi_id = mac_info_dict["Evi"]
            mac_command = mac_info_dict["Command"]
            print(mac_command)
            command_output = self.net_connect.send_command(mac_command)
            sleep(1)
            print(command_output)
            d_mac_address_list.extend(helpers.mac_parser(command_output.splitlines(), tenant_name, vlan, evi_id))
        i = 0
        for d_dict in d_mac_address_list:
            self.d_mac_address.update({i: d_dict})
            i += 1
        if not self.d_mac_address:
            self.d_mac_address = {0: {"TENANT NAME": "", "VLAN": "", "MAC": "", "IP": "", "NEXTHOP": "", "TYPE": "", "EVI": ""}}

    def create_interface_statistics_postcheck(self):
        d_interface_statistics_list = []
        interface_info_dict_list = self.create_interface_info_dict_list()
        for interface_info_dict in interface_info_dict_list:
            tenant_name = interface_info_dict["Tenant Name"]
            interface = interface_info_dict["Interface"]
            interface_command = interface_info_dict["Command"]
            print(interface_command)
            command_output = self.net_connect.send_command(interface_command)
            sleep(1)
            print(command_output)
            d_interface_statistics_list.extend(helpers.interface_parser(command_output.splitlines(), tenant_name, interface))
        i = 0
        for d_dict in d_interface_statistics_list:
            self.d_interface_statistics.update({i: d_dict})
            i += 1
        if not self.d_interface_statistics:
            self.d_interface_statistics = {0: {"TENANT NAME": "", "INPUT BPS": "", "INPUT PPS": "", "OUTPUT BPS": "",
                                               "OUTPUT PPS": "", "INPUT DROPS": "", "OUTPUT DROPS": ""}}

    def __create_df_arp_postcheck(self, tenant_name=None):
        df_arp = pd.DataFrame.from_dict(self.d_arp, orient="index")
        if not df_arp.empty:
            self.df_arp_postcheck = df_arp[df_arp["TENANT NAME"] == tenant_name].reset_index(drop=True)
        else:
            self.df_arp_postcheck = pd.DataFrame({"TENANT NAME": [], "VRF NAME": [], "VLAN": [], "IP": [], "MAC": [], "INTERFACE": []})

    def __create_df_route_postcheck(self, tenant_name=None):
        df_route = pd.DataFrame.from_dict(self.d_route, orient="index")
        if not df_route.empty:
            self.df_route_postcheck = df_route[df_route["TENANT NAME"] == tenant_name].reset_index(drop=True)
        else:
            self.df_route_postcheck = pd.DataFrame({"TENANT NAME": [], "VRF NAME": [], "VLAN": [], "PREFIX": [], "PROTOCOL": []})

    def __create_df_static_route_postcheck(self, tenant_name=None):
        df_static_route = pd.DataFrame.from_dict(self.d_static_route, orient="index")
        if not df_static_route.empty:
            self.df_static_route_postcheck = df_static_route[df_static_route["TENANT NAME"] == tenant_name].reset_index(drop=True)
        else:
            self.df_static_route_postcheck = pd.DataFrame({"TENANT NAME": [], "VRF NAME": [], "VLAN": [], "PREFIX": [], "PROTOCOL": []})

    def __create_df_bgp_route_postcheck(self, tenant_name=None):
        df_bgp_route = pd.DataFrame.from_dict(self.d_bgp_route, orient="index")
        if not df_bgp_route.empty:
            self.df_bgp_route_postcheck = df_bgp_route[df_bgp_route["TENANT NAME"] == tenant_name].reset_index(drop=True)
        else:
            self.df_bgp_route_postcheck = pd.DataFrame({"TENANT NAME": [], "VRF NAME": [], "VLAN": [], "PREFIX": [], "PROTOCOL": []})

    def __create_df_mac_postcheck(self, tenant_name=None):
        df_mac = pd.DataFrame.from_dict(self.d_mac_address, orient="index")
        if not df_mac.empty:
            self.df_mac_postcheck = df_mac[df_mac["TENANT NAME"] == tenant_name].reset_index(drop=True)
        else:
            self.df_mac_postcheck = pd.DataFrame({"TENANT NAME": [], "VLAN": [], "MAC": [], "IP": [], "NEXTHOP": [], "TYPE": [], "EVI": []})

    def __create_df_interface_postcheck(self, tenant_name=None):
        df_interface = pd.DataFrame.from_dict(self.d_interface_statistics, orient="index")
        if not df_interface.empty:
            self.df_interface_postcheck = df_interface[df_interface["TENANT NAME"] == tenant_name]
        else:
            self.df_interface_postcheck = pd.DataFrame({"TENANT NAME": [], "INPUT BPS": [], "INPUT PPS": [], "OUTPUT BPS": [], "OUTPUT PPS": [], "INPUT DROPS": [], "OUTPUT DROPS": []})

    def __create_df_summary_postcheck(self, tenant_name=None):
        arp_count = self.df_arp_postcheck.shape[0]
        route_count = self.df_route_postcheck.shape[0]
        static_route_count = self.df_static_route_postcheck.shape[0]
        bgp_route_count = self.df_bgp_route_postcheck.shape[0]
        mac_count = self.df_mac_postcheck.shape[0]
        self.df_summary_postcheck = pd.DataFrame.from_dict({tenant_name: {"ARP COUNT": arp_count, "ROUTE COUNT": route_count, "STATIC ROUTE COUNT": static_route_count, "BGP ROUTE COUNT": bgp_route_count, "MAC COUNT": mac_count}}, orient="index")

    def __create_df_vrf_summary_postcheck(self):
        vrf_list = []
        d_vrf_summary = {}
        [vrf_list.append(self.df_arp_postcheck.loc[index]["VRF NAME"]) for index in self.df_arp_postcheck.index.values if self.df_arp_postcheck.loc[index]["VRF NAME"] not in vrf_list and self.df_arp_postcheck.loc[index]["VRF NAME"] != ""]
        [vrf_list.append(self.df_route_postcheck.loc[index]["VRF NAME"]) for index in self.df_route_postcheck.index.values if self.df_route_postcheck.loc[index]["VRF NAME"] not in vrf_list and self.df_route_postcheck.loc[index]["VRF NAME"] != ""]
        [vrf_list.append(self.df_static_route_postcheck.loc[index]["VRF NAME"]) for index in self.df_static_route_postcheck.index.values if self.df_static_route_postcheck.loc[index]["VRF NAME"] not in vrf_list and self.df_static_route_postcheck.loc[index]["VRF NAME"] != ""]
        [vrf_list.append(self.df_bgp_route_postcheck.loc[index]["VRF NAME"]) for index in self.df_bgp_route_postcheck.index.values if self.df_bgp_route_postcheck.loc[index]["VRF NAME"] not in vrf_list and self.df_bgp_route_postcheck.loc[index]["VRF NAME"] != ""]
        for vrf in vrf_list:
            arp_count = 0; route_count = 0; static_route_count = 0; bgp_route_count = 0
            for index in self.df_arp_postcheck.index.values:
                if vrf == self.df_arp_postcheck.loc[index]["VRF NAME"]:
                    arp_count += 1
            for index in self.df_route_postcheck.index.values:
                if vrf == self.df_route_postcheck.loc[index]["VRF NAME"]:
                    route_count += 1
            for index in self.df_static_route_postcheck.index.values:
                if vrf == self.df_static_route_postcheck.loc[index]["VRF NAME"]:
                    static_route_count += 1
            for index in self.df_bgp_route_postcheck.index.values:
                if vrf == self.df_bgp_route_postcheck.loc[index]["VRF NAME"]:
                    bgp_route_count += 1
            d_vrf_summary.update({vrf: {"ARP COUNT": arp_count, "ROUTE COUNT": route_count, "STATIC ROUTE COUNT": static_route_count, "BGP ROUTE COUNT": bgp_route_count}})
        if not d_vrf_summary:
            d_vrf_summary = {0: {"ARP COUNT": "", "ROUTE COUNT": "", "STATIC ROUTE COUNT": "", "BGP ROUTE COUNT": ""}}
        self.df_vrf_summary_postcheck = pd.DataFrame.from_dict(d_vrf_summary, orient="index")

    def __create_df_evi_summary_postcheck(self):
        evi_list = []
        d_evi_summary = {}
        [evi_list.append(self.df_mac_postcheck.loc[index]["EVI"]) for index in self.df_mac_postcheck.index.values if self.df_mac_postcheck.loc[index]["EVI"] not in evi_list and self.df_mac_postcheck.loc[index]["EVI"] != ""]
        for evi in evi_list:
            mac_count = 0
            for index in self.df_mac_postcheck.index.values:
                if evi == self.df_mac_postcheck.loc[index]["EVI"]:
                    mac_count += 1
            d_evi_summary.update({evi: {"MAC COUNT": mac_count}})
        if not d_evi_summary:
            d_evi_summary = {0: {"MAC COUNT": ""}}
        self.df_evi_summary_postcheck = pd.DataFrame.from_dict(d_evi_summary, orient="index")

    def write_excel(self):
        for tenant in self.tenant_list:
            file = "DCI_POSTCHECK_{}_{}.xlsx".format(tenant, strftime("%Y-%m-%d_%H-%M-%S"))
            self.__create_df_arp_postcheck(tenant)
            self.__create_df_route_postcheck(tenant)
            self.__create_df_static_route_postcheck(tenant)
            self.__create_df_bgp_route_postcheck(tenant)
            self.__create_df_mac_postcheck(tenant)
            self.__create_df_interface_postcheck(tenant)
            self.__create_df_summary_postcheck(tenant)
            self.__create_df_vrf_summary_postcheck()
            self.__create_df_evi_summary_postcheck()
            with pd.ExcelWriter(file) as writer:
                self.df_arp_postcheck.to_excel(writer, sheet_name="ARP")
                self.df_route_postcheck.to_excel(writer, sheet_name="ROUTE")
                self.df_static_route_postcheck.to_excel(writer, sheet_name="STATIC ROUTE")
                self.df_bgp_route_postcheck.to_excel(writer, sheet_name="BGP ROUTE")
                self.df_mac_postcheck.to_excel(writer, sheet_name="MAC")
                self.df_interface_postcheck.to_excel(writer, sheet_name="INTERFACE STATISTICS")
                self.df_summary_postcheck.to_excel(writer, sheet_name="TENANT SUMMARY")
                self.df_vrf_summary_postcheck.to_excel(writer, sheet_name="VRF SUMMARY")
                self.df_evi_summary_postcheck.to_excel(writer, sheet_name="EVI SUMMARY")

    def disconnect(self):
        self.net_connect.disconnect()
