import requests
import json
import urllib3
import nso_helpers as helpers
import pandas as pd
import logging
from nso_file import NsoFile


class Nso(NsoFile):

    def __init__(self, protocol="https", host="127.0.0.1", port="8888", username="admin", password="Tellcom123!", disable_warnings=True, cert_verify=False, file_name=None):
        super().__init__(file_name)
        self.file_name = file_name
        self.protocol = protocol
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.verify = cert_verify
        self.url = f"{protocol}://{host}:{port}/jsonrpc"
        self.cookies_string = None
        self.th_id = None
        self.df_pa_problems = pd.DataFrame()
        self.df_vrf_problems = pd.DataFrame()
        self.df_tenant_problems = pd.DataFrame()
        self.df_service_problems = pd.DataFrame()
        self.df_node_id_problems = pd.DataFrame()
        self.df_port_pa_externally_used_by = pd.DataFrame()
        self.df_l2ext_problems = pd.DataFrame()
        if disable_warnings:
            urllib3.disable_warnings()
            logging.getLogger("urllib3").propagate = False

    def cookies(self):
        auth = {"jsonrpc": "2.0", "id": 1, "method": "login", "params": {"user": self.username, "passwd": self.password}}
        authenticate = requests.post(self.url, json=auth, verify=self.verify)
        self.cookies_string = authenticate.cookies
        self.__logging_output(self.cookies_string.__str__())

    def start_new_read_transaction(self):
        payload = {"jsonrpc": "2.0", "id": 1, "method": "new_trans", "params": {"db": "running", "mode": "read"}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.th_id = json.loads(response)["result"]["th"]
        self.__logging_output(f"New Read Transaction:{response}")

    def start_new_read_write_transaction(self):
        payload = {"jsonrpc": "2.0", "id": 1, "method": "new_trans", "params": {"db": "running", "mode": "read_write"}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.th_id = json.loads(response)["result"]["th"]
        self.__logging_output(f"New Read WriteTransaction:{response}")
########################################################################################################################
# Dictionary Example for tenant_info_dict
# tenant_info_dict = {"Tenant Name":tenant_name,"Shared Tenant":True}

    def __create_tenant(self, tenant_info_dict):
        tenant_name = tenant_info_dict["Tenant Name"]
        shared_tenant_status = tenant_info_dict["Shared Tenant"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_tenant}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Tenant {tenant_name}:{response}")
        if shared_tenant_status:
            self.__create_shared_tenant(tenant_name)

    def __create_shared_tenant(self, tenant_name):
        xpath_shared_tenant = f"/acidc/tenants{{{tenant_name}}}/shared-tenant"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_shared_tenant}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Shared Tenant {tenant_name}:{response}")

    def create_tenants(self):
        [self.__create_tenant(tenant_info_dict) for tenant_info_dict in self.create_tenant_info_dict_list()]
########################################################################################################################
# Dictionary Example for service_info_dict
# service_info_dict = {"Tenant Name":tenant_name,"Service Name":service_name,"Fabric":fabric}

    def __create_service(self, service_info_dict):
        tenant_name = service_info_dict["Tenant Name"]
        service_name = service_info_dict["Service Name"]
        fabric = service_info_dict["Fabric"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_service = xpath_tenant + f"/service/dclan{{{service_name}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_service}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Service {service_name}:{response}")
        xpath_fabric = xpath_service + "/fabric"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_fabric, "value": fabric}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Service {service_name} Fabric:{response}")

    def create_services(self):
        [self.__create_service(service_info_dict) for service_info_dict in self.create_service_info_dict_list()]
########################################################################################################################
# Dictionary Example for vrf_info_dict
# vrf_info_dict = {"Tenant Name": "T0001", "Vrf Name": "Private0001", "Default Originate": True, "Vrf Type": "Private",
#                  "Vpn Id": "1000", "Disable Primary RT": True, "Custom Import RT List": ["34984:888", "34984:889"],
#                  "Custom Export RT List": ["34984:888", "34984:889"], "Policy": "ank-aci-corp-fabric-1", "RP Management 888":True,
#                  "Static": "RP_STATIC_INTO_BGP_VRF", "Connected": "CPL_0002", "Vrf Export Policy":vrf_export_policy_name,
#                  "Vrf Import Policy":vrf_import_policy_name, "Vrf Export Policy Prefix List": "PL0001", "Vrf Export Policy Local Preference": "100",
#                  "Vrf Import Policy Prefix List": "PL0002"}

    def __create_vrf_isolated(self, vrf_info_dict):
        tenant_name = vrf_info_dict["Tenant Name"]
        vrf_name = vrf_info_dict["Vrf Name"]
        default_originate_status = vrf_info_dict["Default Originate"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_vrf = xpath_tenant + f"/vrf{{{vrf_name}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_vrf}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create {vrf_name} VRF:{response}")
        xpath_vrf_type = xpath_vrf + "/vrf-type"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_vrf_type, "value": "isolated"}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value {vrf_name} VRF type isolated:{response}")
        if default_originate_status:
            xpath_default_originate = xpath_vrf + "/default-originate"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_default_originate}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            self.__logging_output(f"Create {vrf_name} Default Originate:{response}")

    def __create_vrf_internet(self, vrf_info_dict):
        tenant_name = vrf_info_dict["Tenant Name"]
        vrf_name = vrf_info_dict["Vrf Name"]
        default_originate_status = vrf_info_dict["Default Originate"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_vrf = xpath_tenant + f"/vrf{{{vrf_name}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_vrf}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create {vrf_name} VRF:{response}")
        xpath_vrf_type = xpath_vrf + "/vrf-type"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_vrf_type, "value": "internet"}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value {vrf_name} VRF type internet:{response}")
        if default_originate_status:
            xpath_default_originate = xpath_vrf + "/default-originate"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_default_originate}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            self.__logging_output(f"Create {vrf_name} Default Originate:{response}")

    def __create_vrf_private(self, vrf_info_dict):
        tenant_name = vrf_info_dict["Tenant Name"]
        vrf_name = vrf_info_dict["Vrf Name"]
        default_originate_status = vrf_info_dict["Default Originate"]
        vpn_id = vrf_info_dict["Vpn Id"]
        disable_primary_rt_status = vrf_info_dict["Disable Primary RT"]
        custom_import_rt_list = vrf_info_dict["Custom Import RT List"]
        custom_export_rt_list = vrf_info_dict["Custom Export RT List"]
        policy = vrf_info_dict["Policy"]
        rp_management_888_status = vrf_info_dict["RP Management 888"]
        static_policy_name = vrf_info_dict["Static"]
        connected_policy_name = vrf_info_dict["Connected"]
        vrf_policy_status = vrf_info_dict["Vrf Policy"]
        vrf_export_policy_name = vrf_info_dict["Vrf Export Policy"]
        vrf_import_policy_name = vrf_info_dict["Vrf Import Policy"]
        vrf_export_policy_prefix_list_name = vrf_info_dict["Vrf Export Policy Prefix List"]
        vrf_export_policy_local_preference = vrf_info_dict["Vrf Export Policy Local Preference"]
        vrf_import_policy_prefix_list_name = vrf_info_dict["Vrf Import Policy Prefix List"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_vrf = xpath_tenant + f"/vrf{{{vrf_name}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_vrf}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create {vrf_name} VRF:{response}")
        xpath_vrf_type = xpath_vrf + "/vrf-type"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_vrf_type, "value": "private"}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create {vrf_name} VRF type private:{response}")
        xpath_vpn_id = xpath_vrf + "/vpn-id"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_vpn_id, "value": vpn_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value {vrf_name} VRF Vpn-Id:{response}")
        if default_originate_status:
            xpath_default_originate = xpath_vrf + "/default-originate"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_default_originate}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            self.__logging_output(f"Create {vrf_name} Default Originate:{response}")
        if disable_primary_rt_status:
            xpath_disable_primary_rt = xpath_vrf + "/disable-primary-rt"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_disable_primary_rt}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            self.__logging_output(f"Create {vrf_name} Disable Primary RT:{response}")
        if custom_import_rt_list is not None:
            custom_import_rt = " ".join(str(x) for x in custom_import_rt_list)
            xpath_custom_import_rt = xpath_vrf + "/custom-import-rt"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_custom_import_rt, "value": custom_import_rt}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            self.__logging_output(f"Set Value {vrf_name} VRF Custom Import RT:{response}")
        if custom_export_rt_list is not None:
            custom_export_rt = " ".join(str(x) for x in custom_export_rt_list)
            xpath_custom_export_rt = xpath_vrf + "/custom-export-rt"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_custom_export_rt, "value": custom_export_rt}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            self.__logging_output(f"Set Value {vrf_name} VRF Custom Export RT:{response}")
        if vrf_policy_status:
            xpath_policy = xpath_vrf + f"/policy{{{policy}}}"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_policy}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            self.__logging_output(f"Create {vrf_name} Policy:{response}")
            if rp_management_888_status:
                self.__enable_rp_management_888(xpath_policy)
            if static_policy_name is not None:
                self.__vrf_policy_static(xpath_policy, static_policy_name)
            if connected_policy_name is not None:
                self.__vrf_policy_connected(xpath_policy, connected_policy_name)
            if vrf_export_policy_name is not None:
                xpath_policy_vrf = xpath_policy + "/vrf"
                payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_policy_vrf}}
                req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
                response = req.text
                self.__logging_output(f"Create {vrf_name} Policy Vrf:{response}")
                self.__vrf_export_policy(xpath_policy_vrf, vrf_export_policy_name, vrf_export_policy_prefix_list_name, vrf_export_policy_local_preference)
            if vrf_import_policy_name is not None:
                xpath_policy_vrf = xpath_policy + "/vrf"
                payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_policy_vrf}}
                req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
                response = req.text
                self.__logging_output(f"Create {vrf_name} Policy Vrf:{response}")
                self.__vrf_import_policy(xpath_policy_vrf, vrf_import_policy_name, vrf_import_policy_prefix_list_name)

    def __enable_rp_management_888(self, xpath_policy):
        xpath_enable_rp_management_888 = xpath_policy + "/enable-rp-managment-888"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_enable_rp_management_888, "value": True}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create RP Management  888:{response}")

    def __vrf_policy_static(self, xpath_policy, static_policy_name):
        xpath_policy_static = xpath_policy + "/static"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_policy_static}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create VRF Policy Static:{response}")
        if static_policy_name == "STATIC-INTO-BGP-VRF":
            xpath_policy_static_into_bgp_vrf = xpath_policy_static + "/STATIC-INTO-BGP-VRF"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_policy_static_into_bgp_vrf}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            self.__logging_output(f"Create VRF Policy Static into BGP VRF:{response}")
        else:
            xpath_policy_static_custom_policy = xpath_policy_static + "/custom-policy"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_policy_static_custom_policy, "value": static_policy_name}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            self.__logging_output(f"Create VRF Policy Static Custom Policy:{response}")

    def __vrf_policy_connected(self, xpath_policy, connected_policy_name):
        xpath_policy_connected = xpath_policy + "/connected"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_policy_connected}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create VRF Policy Connected:{response}")
        xpath_policy_connected_custom_policy = xpath_policy_connected + "/custom-policy"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_policy_connected_custom_policy, "value": connected_policy_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create VRF Policy Connected Custom Policy:{response}")

    def __vrf_export_policy(self, xpath_policy_vrf, vrf_export_policy_name, vrf_export_policy_prefix_list_name, vrf_export_policy_local_preference):
        if vrf_export_policy_name == "TENANT-EBGP-INET-ONLY-LOCAL-PREF":
            self.__vrf_export_policy_tenant_ebgp_inet_only_local_pref(xpath_policy_vrf, vrf_export_policy_prefix_list_name, vrf_export_policy_local_preference)
        elif vrf_export_policy_name == "FULL-ROUTE-NO-DEFAULT":
            self.__vrf_export_policy_full_route_no_default(xpath_policy_vrf)
        elif vrf_export_policy_name == "RP-INTERNET-EXPORT":
            self.__vrf_export_policy_rp_internet_export(xpath_policy_vrf, vrf_export_policy_prefix_list_name)
        else:
            self.__vrf_export_policy_custom(xpath_policy_vrf, vrf_export_policy_name)

    def __vrf_export_policy_tenant_ebgp_inet_only_local_pref(self, xpath_policy_vrf, prefix_list_name, local_preference):
        xpath_vrf_export_policy_prefix_list = xpath_policy_vrf + "/export-policy/TENANT-EBGP-INET-ONLY-LOCAL-PREF/prefix-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_vrf_export_policy_prefix_list, "value": prefix_list_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value VRF Export Policy Tenant-EBGP-Inet-Only-Local-Pref Prefix List {prefix_list_name}:{response}")
        if local_preference is not None:
            xpath_vrf_export_policy_local_pref = xpath_policy_vrf + "/export-policy/TENANT-EBGP-INET-ONLY-LOCAL-PREF/local-pref"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_vrf_export_policy_local_pref, "value": local_preference}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            self.__logging_output(f"Set Value VRF Export Policy Tenant-EBGP-Inet-Only-Local-Pref Local Pref {local_preference}:{response}")

    def __vrf_export_policy_full_route_no_default(self, xpath_policy_vrf):
        xpath_vrf_export_policy = xpath_policy_vrf + "/export-policy/FULL-ROUTE-NO-DEFAULT"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_vrf_export_policy}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create VRF Export Policy FULL-ROUTE-NO-DEFAULT:{response}")

    def __vrf_export_policy_rp_internet_export(self, xpath_policy_vrf, prefix_list_name):
        xpath_vrf_export_policy_prefix_list = xpath_policy_vrf + "/export-policy/RP-INTERNET-EXPORT/prefix-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_vrf_export_policy_prefix_list, "value": prefix_list_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value VRF Export Policy RP-INTERNET-EXPORT Prefix List {prefix_list_name}:{response}")

    def __vrf_export_policy_custom(self, xpath_policy_vrf, policy_name):
        xpath_vrf_export_policy = xpath_policy_vrf + "/export-policy/custom-policy"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_vrf_export_policy, "value": policy_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value VRF Export Policy Custom Policy {policy_name}:{response}")

    def __vrf_import_policy(self, xpath_policy_vrf, vrf_import_policy_name, vrf_import_policy_prefix_list_name):
        if vrf_import_policy_name == "RP-MANAGEMENT-888":
            self.__vrf_import_policy_rp_management_888(xpath_policy_vrf)
        elif vrf_import_policy_name == "RP-L3VPN-FROM-TCELL-GRT":
            self.__vrf_import_policy_rp_l3vpn_from_tcell_gtr(xpath_policy_vrf, vrf_import_policy_prefix_list_name)
        elif vrf_import_policy_name == "SDWAN-MANAGEMENT-888-POLICY":
            self.__vrf_import_policy_sdwan_management_888_policy(xpath_policy_vrf)
        elif vrf_import_policy_name == "SDWAN-POLICY-ONLY":
            self.__vrf_import_policy_sdwan_policy_only(xpath_policy_vrf)
        else:
            self.__vrf_import_policy_custom(xpath_policy_vrf, vrf_import_policy_name)

    def __vrf_import_policy_rp_management_888(self, xpath_policy_vrf):
        xpath_vrf_import_policy = xpath_policy_vrf + "/import-policy/RP-MANAGEMENT-888"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_vrf_import_policy}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create VRF Import Policy RP-MANAGEMENT-888:{response}")

    def __vrf_import_policy_rp_l3vpn_from_tcell_gtr(self, xpath_policy_vrf, prefix_list_name):
        xpath_vrf_import_policy_prefix_list = xpath_policy_vrf + "/import-policy/RP-L3VPN-FROM-TCELL-GRT/prefix-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_vrf_import_policy_prefix_list, "value": prefix_list_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value VRF Import Policy RP-L3VPN-FROM-TCELL-GRT Prefix List {prefix_list_name}:{response}")

    def __vrf_import_policy_sdwan_management_888_policy(self, xpath_policy_vrf):
        xpath_vrf_import_policy = xpath_policy_vrf + "/import-policy/SDWAN-MANAGEMENT-888-POLICY"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_vrf_import_policy}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create VRF Import Policy SDWAN-MANAGEMENT-888-POLICY:{response}")

    def __vrf_import_policy_sdwan_policy_only(self, xpath_policy_vrf):
        xpath_vrf_import_policy = xpath_policy_vrf + "/import-policy/SDWAN-POLICY-ONLY"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_vrf_import_policy}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create VRF Import Policy SDWAN-POLICY-ONLY:{response}")

    def __vrf_import_policy_custom(self, xpath_policy_vrf, policy_name):
        xpath_vrf_import_policy = xpath_policy_vrf + "/import-policy/custom-policy"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_vrf_import_policy, "value": policy_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value VRF Import Policy Custom Policy {policy_name}:{response}")

    def __create_vrf(self, vrf_info_dict):
        vrf_type = vrf_info_dict["Vrf Type"]
        if vrf_type == "isolated":
            self.__create_vrf_isolated(vrf_info_dict)
        elif vrf_type == "internet":
            self.__create_vrf_internet(vrf_info_dict)
        elif vrf_type == "private":
            self.__create_vrf_private(vrf_info_dict)
        else:
            raise Exception("!!!Invalid VRF Type!!!")

    def create_vrfs(self):
        [self.__create_vrf(vrf_info_dict) for vrf_info_dict in self.create_vrf_info_dict_list()]
########################################################################################################################
# Dictionary Example for bd_info_dict
# bd_info_dict = {"Tenant Name": "T0001", "Service Name": "S0001", "Bd Name": "BD0001", "Vrf Name": "Private0001"}

    def __create_bd(self, bd_info_dict):
        tenant_name = bd_info_dict["Tenant Name"]
        service_name = bd_info_dict["Service Name"]
        bd_name = bd_info_dict["Bd Name"]
        vrf_name = bd_info_dict["Vrf Name"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_service = xpath_tenant + f"/service/dclan{{{service_name}}}"
        xpath_bd = xpath_service + f"/bd{{{bd_name}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_bd}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create BD {bd_name}:{response}")
        xpath_bd_vrf = xpath_bd + "/vrf"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_bd_vrf, "value": vrf_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value {bd_name} VRF:{response}")

    def create_bds(self):
        [self.__create_bd(bd_info_dict) for bd_info_dict in self.create_bd_info_dict_list()]
########################################################################################################################
# Dictionary Example for epg_info_dict
# epg_info_dict = {"Tenant Name": "T0001", "Service Name": "S0001", "Bd Name": "BD0001", "Epg Name": "EPG0001"}

    def __create_epg(self, epg_info_dict):
        tenant_name = epg_info_dict["Tenant Name"]
        service_name = epg_info_dict["Service Name"]
        bd_name = epg_info_dict["Bd Name"]
        epg_name = epg_info_dict["Epg Name"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_service = xpath_tenant + f"/service/dclan{{{service_name}}}"
        xpath_bd = xpath_service + f"/bd{{{bd_name}}}"
        xpath_epg = xpath_bd + f"/epg{{{epg_name}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_epg}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Epg {epg_name}:{response}")

    def create_epgs(self):
        [self.__create_epg(epg_info_dict) for epg_info_dict in self.create_epg_info_dict_list()]
########################################################################################################################
# Dictionary Example for encap_info_dict
# encap_info_dict = {"Tenant Name": "T0001", "Service Name": "S0001", "Bd Name": "BD0001", "Epg Name": "EPG0001", "Encap Id": "1001"}

    def __create_encap(self, encap_info_dict):
        tenant_name = encap_info_dict["Tenant Name"]
        service_name = encap_info_dict["Service Name"]
        bd_name = encap_info_dict["Bd Name"]
        epg_name = encap_info_dict["Epg Name"]
        encap_id = encap_info_dict["Encap Id"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_service = xpath_tenant + f"/service/dclan{{{service_name}}}"
        xpath_bd = xpath_service + f"/bd{{{bd_name}}}"
        xpath_epg = xpath_bd + f"/epg{{{epg_name}}}"
        xpath_encap = xpath_epg + f"/encap{{{encap_id}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_encap}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Encap {encap_id}:{response}")

    def create_encaps(self):
        [self.__create_encap(encap_info_dict) for encap_info_dict in self.create_encap_info_dict_list()]
########################################################################################################################
# List Example for pa_info_list
# pa_info_list = {"Tenant Name":tenant_name,"Pa Name":pa_name,"Fabric":fabric,"Pod":pod,"Pa Type":pa_type,"Interface Profile":interface_profile,"Node  Id":node_id,
#                "Node Port List":[node_port1,node_port2]},"Node Id 1":node_id_1,"Node Id 2":node_id_2,"Node 1 Port List":[node_port1,node_port2],"Node 2 Port List":[node_port1,node_port2]}

    def __create_pa_sa(self, pa_info_dict):
        tenant_name = pa_info_dict["Tenant Name"]
        pa_name = pa_info_dict["Pa Name"]
        fabric = pa_info_dict["Fabric"]
        pod = pa_info_dict["Pod"]
        interface_profile = pa_info_dict["Interface Profile"]
        node_id = pa_info_dict["Node Id"]
        node_port = " ".join(str(x).strip("Ethernet") for x in pa_info_dict["Node Port List"])
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_pa = xpath_tenant + f"/port/pa{{{pa_name}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_pa}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Tenant {tenant_name} Port PA {pa_name}:{response}")
        xpath_pa_fabric = xpath_pa + "/fabric"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_fabric, "value": fabric}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Fabric {fabric}:{response}")
        xpath_pa_pod = xpath_pa + "/pod"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_pod, "value": pod}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Pod {pod}:{response}")
        xpath_pa_type = xpath_pa + "/type"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_type, "value": "SA"}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Type SA:{response}")
        xpath_pa_profile = xpath_pa + "/interface-profile"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_profile, "value": interface_profile}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Interface Profile {interface_profile}:{response}")
        xpath_pa_node_id = xpath_pa + "/node-id"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_node_id, "value": node_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Node Id {node_id}:{response}")
        xpath_pa_node_port = xpath_pa + "/node-port"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_node_port, "value": node_port}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Node Port {node_port}:{response}")

    def __create_pa_pc(self, pa_info_dict):
        tenant_name = pa_info_dict["Tenant Name"]
        pa_name = pa_info_dict["Pa Name"]
        fabric = pa_info_dict["Fabric"]
        pod = pa_info_dict["Pod"]
        interface_profile = pa_info_dict["Interface Profile"]
        node_id = pa_info_dict["Node Id"]
        node_ports = " ".join(str(x).strip("Ethernet") for x in pa_info_dict["Node Port List"])
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_pa = xpath_tenant + f"/port/pa{{{pa_name}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_pa}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create PA {pa_name}:{response}")
        xpath_pa_fabric = xpath_pa + "/fabric"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_fabric, "value": fabric}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Fabric {fabric}:{response}")
        xpath_pa_pod = xpath_pa + "/pod"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_pod, "value": pod}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Pod {pod}:{response}")
        xpath_pa_type = xpath_pa + "/type"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_type, "value": "PC"}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Type PC:{response}")
        xpath_pa_profile = xpath_pa + "/bundle-interface-profile"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_profile, "value": interface_profile}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Interface Profile {interface_profile}:{response}")
        xpath_pa_node_id = xpath_pa + "/node-id"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_node_id, "value": node_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Node Id {node_id}:{response}")
        xpath_pa_node_port = xpath_pa + "/node-port"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_node_port, "value": node_ports}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Node Port {node_ports}:{response}")

    def __create_pa_vpc(self, pa_info_dict):
        tenant_name = pa_info_dict["Tenant Name"]
        pa_name = pa_info_dict["Pa Name"]
        fabric = pa_info_dict["Fabric"]
        pod = pa_info_dict["Pod"]
        interface_profile = pa_info_dict["Interface Profile"]
        node_id_1 = pa_info_dict["Node Id 1"]
        node_id_2 = pa_info_dict["Node Id 2"]
        node_id_1_ports = " ".join(str(x).strip("Ethernet") for x in pa_info_dict["Node Id 1 Port List"])
        node_id_2_ports = " ".join(str(x).strip("Ethernet") for x in pa_info_dict["Node Id 2 Port List"])
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_pa = xpath_tenant + f"/port/pa{{{pa_name}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_pa}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create PA {pa_name}:{response}")
        xpath_pa_fabric = xpath_pa + "/fabric"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_fabric, "value": fabric}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Fabric {fabric}:{response}")
        xpath_pa_pod = xpath_pa + "/pod"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_pod, "value": pod}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Pod {pod}:{response}")
        xpath_pa_type = xpath_pa + "/type"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_type, "value": "VPC"}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Type VPC:{response}")
        xpath_pa_profile = xpath_pa + "/bundle-interface-profile"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_profile, "value": interface_profile}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Interface Profile {interface_profile}:{response}")
        xpath_pa_node_id_1 = xpath_pa + "/node-1-id"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_node_id_1, "value": node_id_1}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Node 1 Id {node_id_1}:{response}")
        xpath_pa_node_id_2 = xpath_pa + "/node-2-id"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_node_id_2, "value": node_id_2}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Node 2 Id {node_id_2}:{response}")
        xpath_pa_node_1_port = xpath_pa + "/node-1-port"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_node_1_port, "value": node_id_1_ports}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Node 1 Port {node_id_1_ports}:{response}")
        xpath_pa_node_2_port = xpath_pa + "/node-2-port"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_pa_node_2_port, "value": node_id_2_ports}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value PA {pa_name} Node 2 Port {node_id_2_ports}:{response}")

    def __create_pa(self, pa_info_dict):
        pa_type = pa_info_dict["Pa Type"]
        if pa_type == "SA":
            self.__create_pa_sa(pa_info_dict)
        elif pa_type == "PC":
            self.__create_pa_pc(pa_info_dict)
        elif pa_type == "VPC":
            self.__create_pa_vpc(pa_info_dict)
        else:
            raise Exception("!!!Invalid Port Type!!!")

    def create_pas(self):
        [self.__create_pa(pa_info_dict) for pa_info_dict in self.create_pa_info_dict_list()]

    def create_pa_portgroups(self, tenant=None, dc_id=None):
        [self.__create_pa(pa_info_dict) for pa_info_dict in self.create_pa_portgroups_info_dict_list(tenant_name=tenant, dc_id=dc_id)]

########################################################################################################################
# Dictionary Example for tenant_pa_info_dict
# tenant_pa_info_dict = {"Tenant Name": "T0001", "Service Name": "S0001", "Bd Name": "BD0001", "Epg Name": "EPG0001",
#                        "Encap Id": "1001", "Tenant Pa Type": "external", "External Tenant Name": "T0002", "Pa Name": "SA0001", "Mode": "regular"}

    def __create_tenant_pa(self, tenant_pa_info_dict):
        tenant_name = tenant_pa_info_dict["Tenant Name"]
        service_name = tenant_pa_info_dict["Service Name"]
        bd_name = tenant_pa_info_dict["Bd Name"]
        epg_name = tenant_pa_info_dict["Epg Name"]
        encap_id = tenant_pa_info_dict["Encap Id"]
        tenant_pa_type = tenant_pa_info_dict["Tenant Pa Type"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_service = xpath_tenant + f"/service/dclan{{{service_name}}}"
        xpath_bd = xpath_service + f"/bd{{{bd_name}}}"
        xpath_epg = xpath_bd + f"/epg{{{epg_name}}}"
        xpath_encap = xpath_epg + f"/encap{{{encap_id}}}"
        if tenant_pa_type == "internal":
            self.__create_internal_tenant_pa(xpath_encap, tenant_pa_info_dict)
        elif tenant_pa_type == "external":
            self.__create_external_tenant_pa(xpath_encap, tenant_pa_info_dict)
        else:
            raise Exception("!!!Invalid Tenant PA Type!!!")

    def __create_internal_tenant_pa(self, xpath_encap, tenant_pa_info_dict):
        tenant_pa_name = tenant_pa_info_dict["Pa Name"]
        tenant_pa_mode = tenant_pa_info_dict["Mode"]
        xpath_tenant_pa = xpath_encap + f"/tenant-pa{{{tenant_pa_name}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_tenant_pa}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Tenant Pa {tenant_pa_name}:{response}")
        xpath_tenant_pa_mode = xpath_tenant_pa + "/mode"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_tenant_pa_mode, "value": tenant_pa_mode}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Tenant Pa {tenant_pa_name} Mode:{response}")

    def __create_external_tenant_pa(self, xpath_encap, tenant_pa_info_dict):
        external_tenant_name = tenant_pa_info_dict["External Tenant Name"]
        tenant_pa_name = tenant_pa_info_dict["Pa Name"]
        tenant_pa_mode = tenant_pa_info_dict["Mode"]
        external_tenant_pa_name = f"{external_tenant_name} {tenant_pa_name}"
        xpath_external_tenant_pa = xpath_encap + f"/external-tenant-pa{{{external_tenant_pa_name}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_external_tenant_pa}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"External Tenant Name {external_tenant_name} Create External Tenant Pa {tenant_pa_name}:{response}")
        xpath_external_tenant_pa_mode = xpath_external_tenant_pa + "/mode"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_external_tenant_pa_mode, "value": tenant_pa_mode}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"External Tenant Name {external_tenant_name} Set Value External Tenant Pa {tenant_pa_name} Mode:{response}")

    def create_tenant_pas(self):
        [self.__create_tenant_pa(tenant_pa_info_dict) for tenant_pa_info_dict in self.create_tenant_pa_info_dict_list()]

    def create_tenant_pa_portgroups(self, tenant=None, dc_id=None):
        [self.__create_tenant_pa(tenant_pa_info_dict) for tenant_pa_info_dict in self.create_tenant_pa_portgroups_info_dict_list(tenant_name=tenant, dc_id=dc_id)]
########################################################################################################################
# Dictionary Example for prefix_list_info_dict
# prefix_list_info_dict = {"Tenant Name": "T0001", "Prefix List Name": "PL0001", "IPv4-Prefix": "10.10.10.0/24", "Eq": "24", "Ge": None, "Le": None}

    def __create_prefix_list(self, prefix_list_info_dict):
        tenant_name = prefix_list_info_dict["Tenant Name"]
        prefix_list_name = prefix_list_info_dict["Prefix List Name"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_prefix_list = xpath_tenant + f"/prefix-list{{{prefix_list_name}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create",
                   "params": {"th": self.th_id, "path": xpath_prefix_list}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Prefix List {prefix_list_name}:{response}")
        prefix = prefix_list_info_dict["IPv4-Prefix"]
        eq = prefix_list_info_dict["Eq"]
        ge = prefix_list_info_dict["Ge"]
        le = prefix_list_info_dict["Le"]
        xpath_prefix_list_prefix = xpath_prefix_list + f"/ipv4-prefix{{{prefix}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create",
                   "params": {"th": self.th_id, "path": xpath_prefix_list_prefix}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Prefix {prefix}:{response}")
        if eq is not None:
            xpath_prefix_list_prefix_eq = xpath_prefix_list_prefix + "/eq"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_prefix_list_prefix_eq, "value": eq}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            self.__logging_output(f"Set Value {prefix} Exact Match:{response}")
        else:
            xpath_prefix_list_prefix_ge = xpath_prefix_list_prefix + "/ge"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_prefix_list_prefix_ge, "value": ge}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            self.__logging_output(f"Set Value {prefix} GE:{response}")
            xpath_prefix_list_prefix_le = xpath_prefix_list_prefix + "/le"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_prefix_list_prefix_le, "value": le}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            self.__logging_output(f"Set Value {prefix} LE:{response}")

    def create_prefix_lists(self):
        [self.__create_prefix_list(prefix_list_info_dict) for prefix_list_info_dict in self.create_prefix_list_info_dict_list()]
########################################################################################################################
# Dictionary Example for l3direct_info_dict
# l3direct_info_dict = {"Tenant Name": "T0001", "Service Name": "S0001", "Bd Name": "BD0001", "Epg Name": "EPG0001", "Encap Id": "1001", "L3 Direct Name": #"BLF_801_802_DCI_VPC_INTPOL", "IPv4 Network": "10.10.10.1/24","Secondary IPv4 Network List": ["20.20.20.1/24", "30.30.30.1/24"], "Shutdown": True, "Service Policy": True, "Input Policy Map": "100M", "Output Policy Map": "100M"}

    def __create_l3direct(self, l3direct_info_dict):
        tenant_name = l3direct_info_dict["Tenant Name"]
        service_name = l3direct_info_dict["Service Name"]
        bd_name = l3direct_info_dict["Bd Name"]
        epg_name = l3direct_info_dict["Epg Name"]
        encap_id = l3direct_info_dict["Encap Id"]
        l3direct_name = l3direct_info_dict["L3 Direct Name"]
        ipv4_network = l3direct_info_dict["IPv4 Network"]
        secondary_ipv4_network_list = l3direct_info_dict["Secondary IPv4 Network List"]
        shutdown_status = l3direct_info_dict["Shutdown"]
        service_policy_status = l3direct_info_dict["Service Policy"]
        input_pmap = l3direct_info_dict["Input Policy Map"]
        output_pmap = l3direct_info_dict["Output Policy Map"]
        mtu = l3direct_info_dict["Mtu"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_service = xpath_tenant + f"/service/dclan{{{service_name}}}"
        xpath_bd = xpath_service + f"/bd{{{bd_name}}}"
        xpath_epg = xpath_bd + f"/epg{{{epg_name}}}"
        xpath_encap = xpath_epg + f"/encap{{{encap_id}}}"
        xpath_l3direct = xpath_encap + "/l3direct"
        xpath_l3direct_name = xpath_l3direct + "/name"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_l3direct_name, "value": l3direct_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value L3Direct Name {l3direct_name}:{response}")
        xpath_ipv4_network = xpath_l3direct + "/ipv4-network"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_ipv4_network, "value": ipv4_network}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value L3Direct IPv4 Network {ipv4_network}:{response}")
        if secondary_ipv4_network_list is not None:
            self.__create_l3direct_secondary_networks(xpath_l3direct, secondary_ipv4_network_list)
        if shutdown_status:
            self.__create_l3direct_shutdown(xpath_l3direct)
        if service_policy_status:
            self.__create_l3direct_service_policy(xpath_l3direct, input_pmap, output_pmap)
        if mtu is not None:
            self.__create_l3direct_mtu(xpath_l3direct, mtu)

    def __create_l3direct_secondary_networks(self, xpath_l3direct, secondary_ipv4_network_list):
        secondary_ipv4_networks = " ".join(str(x) for x in secondary_ipv4_network_list)
        xpath_secondary_ipv4_network = xpath_l3direct + "/secondary-ipv4-networks"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_secondary_ipv4_network, "value": secondary_ipv4_networks}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value L3Direct Secondary IPv4 Network {secondary_ipv4_networks}:{response}")

    def __create_l3direct_shutdown(self, xpath_l3direct):
        xpath_l3direct_shutdown = xpath_l3direct + "/shutdown"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_l3direct_shutdown}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create L3Direct Shutdown:{response}")

    def __delete_l3direct_shutdown(self, l3direct_info_dict):
        tenant_name = l3direct_info_dict["Tenant Name"]
        service_name = l3direct_info_dict["Service Name"]
        bd_name = l3direct_info_dict["Bd Name"]
        epg_name = l3direct_info_dict["Epg Name"]
        encap_id = l3direct_info_dict["Encap Id"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_service = xpath_tenant + f"/service/dclan{{{service_name}}}"
        xpath_bd = xpath_service + f"/bd{{{bd_name}}}"
        xpath_epg = xpath_bd + f"/epg{{{epg_name}}}"
        xpath_encap = xpath_epg + f"/encap{{{encap_id}}}"
        xpath_l3direct = xpath_encap + "/l3direct"
        xpath_l3direct_shutdown = xpath_l3direct + "/shutdown"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "delete", "params": {"th": self.th_id, "path": xpath_l3direct_shutdown}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Tenant:{tenant_name} Service Name:{service_name} Delete L3Direct Shutdown:{response}")

    def __create_l3direct_service_policy(self, xpath_l3direct, input_pmap, output_pmap):
        xpath_service_policy = xpath_l3direct + "/service-policy"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_service_policy}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create L3Direct Service Policy:{response}")
        xpath_service_policy_input = xpath_service_policy + "/input"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_service_policy_input, "value": input_pmap}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value L3Direct Input Service Policy {input_pmap}:{response}")
        xpath_service_policy_output = xpath_service_policy + "/output"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_service_policy_output, "value": output_pmap}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value L3Direct Output Service Policy {output_pmap}:{response}")

    def __create_l3direct_mtu(self, xpath_l3direct, mtu):
        xpath_l3direct_mtu = xpath_l3direct + "/mtu"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_l3direct_mtu, "value": int(mtu)}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value L3Direct MTU {int(mtu)}:{response}")

    def create_l3directs(self):
        [self.__create_l3direct(l3direct_info_dict) for l3direct_info_dict in self.create_l3direct_info_dict_list()]

    def delete_l3direct_shutdowns(self, group_name):
        [self.__delete_l3direct_shutdown(delete_l3direct_shutdown_info_dict) for delete_l3direct_shutdown_info_dict in self.create_delete_l3direct_shutdown_info_dict_list(group_name)]
########################################################################################################################
# Dictionary Example for static_routing_info_dict
# l3direct_static_info_dict= {"Tenant Name": "T0001", "Service Name": "S0001", "Bd Name": "BD0001", "Epg Name": "EPG0001", "Encap Id": "1001",
# "IPv4 Prefix": "40.40.40.0/24", "Nexthop": "10.10.10.2", "Administrative Distance": "10", "Tag": "100"}

    def __create_l3direct_static(self, l3direct_static_info_dict):
        tenant_name = l3direct_static_info_dict["Tenant Name"]
        service_name = l3direct_static_info_dict["Service Name"]
        bd_name = l3direct_static_info_dict["Bd Name"]
        epg_name = l3direct_static_info_dict["Epg Name"]
        encap_id = l3direct_static_info_dict["Encap Id"]
        prefix = l3direct_static_info_dict["IPv4 Prefix"]
        nexthop = l3direct_static_info_dict["Nexthop"]
        description = service_name[5:]   #Description is getting from service name by omitting "GBZ3-"
        administrative_distance = l3direct_static_info_dict["Administrative Distance"]
        tag = l3direct_static_info_dict["Tag"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_service = xpath_tenant + f"/service/dclan{{{service_name}}}"
        xpath_bd = xpath_service + f"/bd{{{bd_name}}}"
        xpath_epg = xpath_bd + f"/epg{{{epg_name}}}"
        xpath_encap = xpath_epg + f"/encap{{{encap_id}}}"
        xpath_l3direct = xpath_encap + "/l3direct"
        xpath_prefix = xpath_l3direct + f"/static/prefix{{{prefix}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_prefix}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Static Route {prefix}:{response}")
        xpath_nexthop = xpath_prefix + "/via"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_nexthop, "value": nexthop}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Static Route {prefix} nexthop:{response}")
        xpath_description = xpath_prefix + "/description"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_description, "value": description}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Static Route {prefix} description:{response}")
        if tag is not None:
            xpath_tag = xpath_prefix + "/tag"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_tag, "value": tag}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            self.__logging_output(f"Set Value Static Route {prefix} Tag:{response}")
        if administrative_distance is not None:
            xpath_ad = xpath_prefix + "/administrative-distance"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_ad, "value": administrative_distance}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            self.__logging_output(f"Set Value Static Route {prefix} Ad:{response}")

    def create_l3direct_statics(self):
        [self.__create_l3direct_static(l3direct_static_info_dict) for l3direct_static_info_dict in self.create_l3direct_static_info_dict_list()]
########################################################################################################################
# Dictionary Example for ospf_routing_info_dict
# l3direct_ospf_info_dict = {"Tenant Name": "T0001", "Service Name": "S0001", "Bd Name": "BD0001", "Epg Name": "EPG0001", "Encap Id": "1001",
#                           "Process Id": "1", "Default Originate": True, "Area": "0.0.0.1"}

    def __create_l3direct_ospf(self, l3direct_ospf_info_dict):
        tenant_name = l3direct_ospf_info_dict["Tenant Name"]
        service_name = l3direct_ospf_info_dict["Service Name"]
        bd_name = l3direct_ospf_info_dict["Bd Name"]
        epg_name = l3direct_ospf_info_dict["Epg Name"]
        encap_id = l3direct_ospf_info_dict["Encap Id"]
        process_id = l3direct_ospf_info_dict["Process Id"]
        default_originate_status = l3direct_ospf_info_dict["Default Originate"]
        area = l3direct_ospf_info_dict["Area"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_service = xpath_tenant + f"/service/dclan{{{service_name}}}"
        xpath_bd = xpath_service + f"/bd{{{bd_name}}}"
        xpath_epg = xpath_bd + f"/epg{{{epg_name}}}"
        xpath_encap = xpath_epg + f"/encap{{{encap_id}}}"
        xpath_l3direct = xpath_encap + "/l3direct"
        xpath_ospf = xpath_l3direct + "/ospf"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_ospf}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create L3Direct Ospf:{response}")
        xpath_ospf_process_id = xpath_ospf + "/processes-id"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_ospf_process_id, "value": process_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value L3Direct Ospf Process ID:{response}")
        xpath_ospf_area = xpath_ospf + "/area"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_ospf_area, "value": area}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value L3Direct Ospf Area:{response}")
        if default_originate_status:
            xpath_ospf_default_originate = xpath_ospf + "/default-originate"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_ospf_default_originate}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            self.__logging_output(f"Create L3Direct Ospf Default Originate:{response}")

    def create_l3direct_ospfs(self):
        [self.__create_l3direct_ospf(l3direct_ospf_info_dict) for l3direct_ospf_info_dict in self.create_l3direct_ospf_info_dict_list()]

########################################################################################################################
############################################BGP RPL INBOUND#########################################################

    def __route_policies_inbound_tenant_ebgp_inet_123(self, xpath_neighbor, prefix_list_name):
        xpath_rpl_in_tenant_ebgp_inet_123 = xpath_neighbor + "/inbound-policy/TENANT-EBGP-INET-123/prefix-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_tenant_ebgp_inet_123, "value": prefix_list_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy TENANT-EBGP-INET-123 Prefix List:{response}")

    def __route_policies_inbound_tenant_ebgp_inet_only_local_pref(self, xpath_neighbor, prefix_list_name):
        xpath_rpl_in_tenant_ebgp_inet_only_local_pref = xpath_neighbor + "/inbound-policy/TENANT-EBGP-INET-ONLY-LOCAL-PREF/prefix-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_tenant_ebgp_inet_only_local_pref, "value": prefix_list_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy TENANT-EBGP-ONLY-LOCAL-PREF Prefix List:{response}")

    def __route_policies_inbound_tenant_ebgp_inet_only_customer_routes(self, xpath_neighbor, prefix_list_name):
        xpath_rpl_out_tenant_ebgp_inet_only_customer_routes_prefix_list = xpath_neighbor + "/inbound-policy/TENANT-EBGP-INET-ONLY-CUSTOMER-ROUTES/prefix-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_out_tenant_ebgp_inet_only_customer_routes_prefix_list, "value": prefix_list_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy TENANT-EBGP-INET-ONLY-CUSTOMER-ROUTES Prefix List::{response}")

    def __route_policies_inbound_tenant_ebgp_inet_123_local_pref(self, xpath_neighbor, local_pref, prefix_list_name):
        xpath_rpl_in_tenant_ebgp_inet_123_local_pref = xpath_neighbor + "/inbound-policy/TENANT-EBGP-INET-123-LOCAL-PREF/local-pref"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_tenant_ebgp_inet_123_local_pref, "value": local_pref}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy TENANT-EBGP-ONLY-LOCAL-PREF Local Preference:{response}")
        xpath_rpl_in_tenant_ebgp_inet_123_prefix_list = xpath_neighbor + "/inbound-policy/TENANT-EBGP-INET-123-LOCAL-PREF/prefix-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_tenant_ebgp_inet_123_prefix_list, "value": prefix_list_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy TENANT-EBGP-ONLY-LOCAL-PREF Prefix List:{response}")

    def __route_policies_inbound_tenant_ebgp_inet_123_named_comm_local_pref(self, xpath_neighbor, local_pref, prefix_list_name, community_name):
        xpath_rpl_in_tenant_ebgp_inet_123_named_comm_local_pref = xpath_neighbor + "/inbound-policy/TENANT-EBGP-INET-123-NAMED-COMM-LOCAL-PREF/local-pref"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_tenant_ebgp_inet_123_named_comm_local_pref, "value": local_pref}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy TENANT-EBGP-INET-123-NAMED-COMM-LOCAL-PREF Local Preference:{response}")
        xpath_rpl_in_tenant_ebgp_inet_123_named_comm_prefix_list = xpath_neighbor + "/inbound-policy/TENANT-EBGP-INET-123-NAMED-COMM-LOCAL-PREF/prefix-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_tenant_ebgp_inet_123_named_comm_prefix_list, "value": prefix_list_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy TENANT-EBGP-INET-123-NAMED-COMM-LOCAL-PREF Prefix List:{response}")
        xpath_rpl_in_tenant_ebgp_inet_123_named_comm_community_name = xpath_neighbor + "/inbound-policy/TENANT-EBGP-INET-123-NAMED-COMM-LOCAL-PREF/community-name"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_tenant_ebgp_inet_123_named_comm_community_name, "value": community_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy TENANT-EBGP-INET-123-NAMED-COMM-LOCAL-PREF Community Name:{response}")

    def __route_policies_inbound_tenant_ebgp_inet_123_custom_comm_local_pref(self, xpath_neighbor, local_pref, prefix_list_name, community_name, community_list):
        xpath_rpl_in_tenant_ebgp_inet_123_custom_comm_local_pref = xpath_neighbor + "/inbound-policy/TENANT-EBGP-INET-123-CUSTOM-COMM-LOCAL-PREF/local-pref"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_tenant_ebgp_inet_123_custom_comm_local_pref, "value": local_pref}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy TENANT-EBGP-INET-123-CUSTOM-COMM-LOCAL-PREF Local Preference:{response}")
        xpath_rpl_in_tenant_ebgp_inet_123_custom_comm_local_pref_prefix_list = xpath_neighbor + "/inbound-policy/TENANT-EBGP-INET-123-CUSTOM-COMM-LOCAL-PREF/prefix-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_tenant_ebgp_inet_123_custom_comm_local_pref_prefix_list, "value": prefix_list_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy TENANT-EBGP-INET-123-CUSTOM-COMM-LOCAL-PREF Prefix List:{response}")
        xpath_rpl_in_tenant_ebgp_inet_123_custom_comm_local_pref_comm_name = xpath_neighbor + "/inbound-policy/TENANT-EBGP-INET-123-CUSTOM-COMM-LOCAL-PREF/community-name"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_tenant_ebgp_inet_123_custom_comm_local_pref_comm_name, "value": community_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy TENANT-EBGP-INET-123-CUSTOM-COMM-LOCAL-PREF Community Name:{response}")
        community_list_string = " ".join(str(x) for x in community_list)
        xpath_rpl_in_tenant_ebgp_inet_123_custom_comm_local_pref_comm_list = xpath_neighbor + "/inbound-policy/TENANT-EBGP-INET-123-CUSTOM-COMM-LOCAL-PREF/community-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_tenant_ebgp_inet_123_custom_comm_local_pref_comm_list, "value": community_list_string}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy TENANT-EBGP-INET-123-CUSTOM-COMM-LOCAL-PREF Community List:{response}")

    def __route_policies_inbound_tenant_ebgp_inet_sol_origin_123_local_pref(self, xpath_neighbor, local_pref, prefix_list_name):
        xpath_rpl_in_tenant_ebgp_sol_origin_123_local_pref = xpath_neighbor + "/inbound-policy/TENANT-EBGP-INET-SOL-ORIGIN-123-LOCAL-PREF/local-pref"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_tenant_ebgp_sol_origin_123_local_pref, "value": local_pref}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy ENANT-EBGP-INET-SOL-ORIGIN-123-LOCAL-PREF Local Preference:{response}")
        xpath_rpl_in_tenant_ebgp_sol_origin_123_local_pref_prefix_list = xpath_neighbor + "/inbound-policy/TENANT-EBGP-INET-SOL-ORIGIN-123-LOCAL-PREF/prefix-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_tenant_ebgp_sol_origin_123_local_pref_prefix_list, "value": prefix_list_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy ENANT-EBGP-INET-SOL-ORIGIN-123-LOCAL-PREF Prefix List:{response}")

    def __route_policies_inbound_default_only(self, xpath_neighbor):
        xpath_rpl_in_default_only = xpath_neighbor + "/inbound-policy/DEFAULT-ONLY"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_rpl_in_default_only}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Inbound Policy Default Only:{response}")

    def __route_policies_inbound_deny_default(self, xpath_neighbor):
        xpath_rpl_in_deny_default = xpath_neighbor + "/inbound-policy/DENY-DEFAULT"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_rpl_in_deny_default}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Inbound Policy Deny Default:{response}")

    def __route_policies_inbound_deny_any(self, xpath_neighbor):
        xpath_rpl_in_deny_any = xpath_neighbor + "/inbound-policy/DENY-ANY"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_rpl_in_deny_any}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Inbound Policy Deny Any:{response}")

    def __route_policies_inbound_inet_123_as_path_prepend(self, xpath_neighbor, as_path, multiplier, prefix_list_name):
        xpath_rpl_in_inet_123_as_path_prepend_as_path = xpath_neighbor + "/inbound-policy/INET-123-AS-PATH-PREPEND/as-values{" + f"{as_path}" + "}/multiplier"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_inet_123_as_path_prepend_as_path, "value": multiplier}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy INET-123-AS-PATH-PREPEND AS Values::{response}")
        xpath_rpl_in_inet_123_as_path_prepend_prefix_list = xpath_neighbor + "/inbound-policy/INET-123-AS-PATH-PREPEND/prefix-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_inet_123_as_path_prepend_prefix_list, "value": prefix_list_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy INET-123-AS-PATH-PREPEND Prefix List:{response}")

    def __route_policies_inbound_local_pref_444(self, xpath_neighbor, prefix_list_name, local_pref):
        xpath_rpl_in_local_pref_444_prefix_list = xpath_neighbor + "/inbound-policy/LOCAL-PREF-444/prefix-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_local_pref_444_prefix_list, "value": prefix_list_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy LOCAL-PREF-444 Prefix List::{response}")
        xpath_rpl_in_local_pref_444_local_pref = xpath_neighbor + "/inbound-policy/LOCAL-PREF-444/local-pref"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_local_pref_444_local_pref, "value": local_pref}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy LOCAL-PREF-444 Local Preference:{response}")

    def __route_policies_inbound_local_pref_666_and_444(self, xpath_neighbor, prefix_list_name, blackhole_prefix_list_name, local_pref):
        xpath_rpl_in_local_pref_666_and_444_prefix_list = xpath_neighbor + "/inbound-policy/LOCAL-PREF-666-AND-444/prefix-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_local_pref_666_and_444_prefix_list, "value": prefix_list_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy LOCAL-PREF-666-AND-444 Prefix List:{response}")
        xpath_rpl_in_local_pref_666_and_444_blackhole_prefix_list = xpath_neighbor + "/inbound-policy/LOCAL-PREF-666-AND-444/blackhole-prefix-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_local_pref_666_and_444_blackhole_prefix_list, "value": blackhole_prefix_list_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy LOCAL-PREF-666-AND-444 Blackhole Prefix List:{response}")
        xpath_rpl_in_local_pref_666_and_444_local_pref = xpath_neighbor + "/inbound-policy/LOCAL-PREF-666-AND-444/local-pref"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_local_pref_666_and_444_local_pref, "value": local_pref}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy LOCAL-PREF-666-AND-444 Local Preference:{response}")

    def __route_policies_inbound_private_as_456(self, xpath_neighbor, prefix_list_name, blackhole_prefix_list_name, local_pref):
        xpath_rpl_in_private_as_456_prefix_list = xpath_neighbor + "/inbound-policy/PRIVATE-AS-456/prefix-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_private_as_456_prefix_list, "value": prefix_list_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy PRIVATE-AS-456 Prefix List:{response}")
        xpath_rpl_in_private_as_456_blackhole_prefix_list = xpath_neighbor + "/inbound-policy/PRIVATE-AS-456/blackhole-prefix-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_private_as_456_blackhole_prefix_list, "value": blackhole_prefix_list_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy PRIVATE-AS-456 Blackhole Prefix List:{response}")
        xpath_rpl_in_private_as_456_blackhole_local_pref = xpath_neighbor + "/inbound-policy/PRIVATE-AS-456/local-pref"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_private_as_456_blackhole_local_pref, "value": local_pref}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy PRIVATE-AS-456 Local Preference:{response}")

    def __route_policies_inbound_custom_policy(self, xpath_neighbor, policy_name):
        xpath_rpl_in_custom_policy = xpath_neighbor + "/inbound-policy/custom-policy"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_in_custom_policy, "value": policy_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Inbound Policy Custom Policy {policy_name}:{response}")

########################################################################################################################
############################################BGP RPL OUTBOUND############################################################

    def __route_policies_outbound_pass_all(self, xpath_neighbor):
        xpath_rpl_out_custom_policy = xpath_neighbor + "/outbound-policy/PASS-ALL"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_rpl_out_custom_policy}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Outbound Policy PASS-ALL:{response}")

    def __route_policies_outbound_default_only(self, xpath_neighbor):
        xpath_rpl_out_default_only = xpath_neighbor + "/outbound-policy/DEFAULT-ONLY"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_rpl_out_default_only}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Outbound Policy DEFAULT-ONLY:{response}")

    def __route_policies_outbound_deny_default(self, xpath_neighbor):
        xpath_rpl_out_deny_default = xpath_neighbor + "/outbound-policy/DENY-DEFAULT"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_rpl_out_deny_default}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Outbound Policy DENY-DEFAULT:{response}")

    def __route_policies_outbound_deny_any(self, xpath_neighbor):
        xpath_rpl_out_deny_any = xpath_neighbor + "/outbound-policy/DENY-ANY"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_rpl_out_deny_any}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Outbound Policy DENY-ANY:{response}")

    def __route_policies_outbound_tenant_ebgp_inet_full_route_no_default(self, xpath_neighbor):
        xpath_rpl_out_tenant_ebgp_inet_full_route_no_default = xpath_neighbor + "/outbound-policy/TENANT-EBGP-INET-FULL-ROUTE-NO-DEFAULT"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_rpl_out_tenant_ebgp_inet_full_route_no_default}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Outbound Policy TENANT-EBGP-INET-FULL-ROUTE-NO-DEFAULT:{response}")

    def __route_policies_outbound_tenant_ebgp_inet_only_customer_routes(self, xpath_neighbor, prefix_list_name):
        xpath_rpl_out_tenant_ebgp_inet_only_customer_routes_prefix_list = xpath_neighbor + "/outbound-policy/TENANT-EBGP-INET-ONLY-CUSTOMER-ROUTES/prefix-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_out_tenant_ebgp_inet_only_customer_routes_prefix_list, "value": prefix_list_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Outbound Policy TENANT-EBGP-INET-ONLY-CUSTOMER-ROUTES Prefix List::{response}")

    def __route_policies_outbound_tenant_ebgp_inet_full_route(self, xpath_neighbor):
        xpath_rpl_out_tenant_ebgp_inet_full_route = xpath_neighbor + "/outbound-policy/TENANT-EBGP-INET-FULL-ROUTE"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_rpl_out_tenant_ebgp_inet_full_route}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Outbound Policy TENANT-EBGP-INET-FULL-ROUTE:{response}")

    def __route_policies_outbound_ebgp_peering_no_default(self, xpath_neighbor):
        xpath_rpl_out_ebgp_peering_no_default = xpath_neighbor + "/outbound-policy/EBGP-PEERING-NO-DEFAULT"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_rpl_out_ebgp_peering_no_default}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Outbound Policy EBGP-PEERING-NO-DEFAULT:{response}")

    def __route_policies_outbound_ebgp_peering_with_default(self, xpath_neighbor):
        xpath_rpl_out_ebgp_peering_with_default = xpath_neighbor + "/outbound-policy/EBGP-PEERING-WITH-DEFAULT"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_rpl_out_ebgp_peering_with_default}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create Outbound Policy EBGP-PEERING-WITH-DEFAULT:{response}")

    def __route_policies_outbound_inet_123_as_path_prepend(self, xpath_neighbor, as_path, multiplier, prefix_list_name):
        xpath_rpl_out_inet_123_as_path_prepend_as_path = xpath_neighbor + "/outbound-policy/INET-123-AS-PATH-PREPEND/as-values{" + f"{as_path}" + "}/multiplier"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_out_inet_123_as_path_prepend_as_path, "value": multiplier}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Outbound Policy INET-123-AS-PATH-PREPEND AS Path:{response}")
        xpath_rpl_out_inet_123_as_path_prepend_prefix_list = xpath_neighbor + "/outbound-policy/INET-123-AS-PATH-PREPEND/prefix-list"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_out_inet_123_as_path_prepend_prefix_list, "value": prefix_list_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Outbound Policy INET-123-AS-PATH-PREPEND Prefix List:{response}")

    def __route_policies_outbound_custom_policy(self, xpath_neighbor, policy_name):
        xpath_rpl_out_custom_policy = xpath_neighbor + "/outbound-policy/custom-policy"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_rpl_out_custom_policy, "value": policy_name}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value Outbound Policy Custom Policy {policy_name}:{response}")

########################################################################################################################
# l3direct_bgp_info_dict = {"Tenant Name": "T0001", "Service Name": "S0001", "Bd Name": "BD0001", "Epg Name": "EPG0001", "Encap Id": "1000", "Enable Max Paths": True,
#                           "Bfd Status": False, "Bfd Min Interval": None, "Bfd Disable Fast Detect": False, "Bfd Multiplier": None, "Bgp Peer": "10.10.10.3", "Remote As": "9121", "Nexthopself": True,
#                           "Remove Private As": True, "Max Prefix": "1000", "Action": "restart", "Default Originate":True, "Password": "cisco", "Soft Reconfiguration": True, "Shutdown": True, "Update Source": "LOCAL",
#                           "Loopback Ip": "10.210.254.111, "Local As Status": True, "Local As": "65001", "Local As No Prepend": True, "Local As Replace As": True, "Custom Timers": True, "Keepalive": "10", "Hold Time": "40",
#                           "In Rpl Name": "Tenant EBGP Inet 123 Local Pref", "In Rpl Custom Policy Name": None, "In Rpl Prefix List": "PL0001", "In Rpl Blackhole Prefix List": None,
#                           "In Rpl Local Preference": "225", "In Rpl Community Name": None, "In Rpl Community List": None, "In Rpl As Path": None, "In Rpl Multiplier": None,
#                           "Out Rpl Name": "Inet 123 As Path Prepend", "Out Rpl Custom Policy Name": None, "Out Rpl Prefix List": "PL0002", "Out Rpl As Path": "34984", "Out Rpl Multiplier": "3"}

    def __create_l3direct_bgp(self, l3direct_bgp_info_dict):
        tenant_name = l3direct_bgp_info_dict["Tenant Name"]
        service_name = l3direct_bgp_info_dict["Service Name"]
        bd_name = l3direct_bgp_info_dict["Bd Name"]
        epg_name = l3direct_bgp_info_dict["Epg Name"]
        encap_id = l3direct_bgp_info_dict["Encap Id"]
        enable_max_path_status = l3direct_bgp_info_dict["Enable Max Paths"]
        bfd_status = l3direct_bgp_info_dict["Bfd Status"]
        bgp_peer = l3direct_bgp_info_dict["Bgp Peer"]
        remote_as = l3direct_bgp_info_dict["Remote As"]
        nexthopself_status = l3direct_bgp_info_dict["Nexthopself"]
        remove_private_as_status = l3direct_bgp_info_dict["Remove Private As"]
        max_prefix = l3direct_bgp_info_dict["Max Prefix"]
        action = l3direct_bgp_info_dict["Action"]
        default_originate_status = l3direct_bgp_info_dict["Default Originate"]
        password = l3direct_bgp_info_dict["Password"]
        soft_reconfiguration_status = l3direct_bgp_info_dict["Soft Reconfiguration"]
        shutdown_status = l3direct_bgp_info_dict["Shutdown"]
        update_source = l3direct_bgp_info_dict["Update Source"]
        loopback_ip = l3direct_bgp_info_dict["Loopback Ip"]
        local_as_status = l3direct_bgp_info_dict["Local As Status"]
        timers_status = l3direct_bgp_info_dict["Custom Timers"]
        rpl_in_name = l3direct_bgp_info_dict["In Rpl Name"]
        custom_rpl_in_name = l3direct_bgp_info_dict["In Rpl Custom Policy Name"]
        rpl_out_name = l3direct_bgp_info_dict["Out Rpl Name"]
        custom_rpl_out_name = l3direct_bgp_info_dict["Out Rpl Custom Policy Name"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_service = xpath_tenant + f"/service/dclan{{{service_name}}}"
        xpath_bd = xpath_service + f"/bd{{{bd_name}}}"
        xpath_epg = xpath_bd + f"/epg{{{epg_name}}}"
        xpath_encap = xpath_epg + f"/encap{{{encap_id}}}"
        xpath_l3direct = xpath_encap + "/l3direct"
        xpath_bgp = xpath_l3direct + "/bgp"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_bgp}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create L3Direct Bgp:{response}")
        xpath_neighbor = xpath_bgp + f"/neighbor{{{bgp_peer}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_neighbor}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create BGP Neighbor {bgp_peer}:{response}")
        xpath_remote_as = xpath_neighbor + "/remote-as"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_remote_as, "value": remote_as}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value BGP Neighbor {bgp_peer} AS Path:{response}")
        if enable_max_path_status:
            self.__bgp_enable_max_paths(xpath_bgp)
        if bfd_status:
            self.__bgp_bfd(xpath_bgp, l3direct_bgp_info_dict)
        if nexthopself_status:
            self.__bgp_neighbor_nexthopself(xpath_neighbor)
        if remove_private_as_status:
            self.__bgp_neighbor_remove_private_as(xpath_neighbor)
        if max_prefix is not None:
            self.__bgp_neighbor_max_prefix(xpath_neighbor, max_prefix)
        if action is not None:
            self.__bgp_neighbor_action(xpath_neighbor, action)
        if default_originate_status:
            self.__bgp_neighbor_default_originate(xpath_neighbor)
        if password is not None:
            self.__bgp_neighbor_password(xpath_neighbor, password)
        if soft_reconfiguration_status:
            self.__bgp_neighbor_soft_reconfiguration(xpath_neighbor)
        if shutdown_status:
            self.__bgp_neighbor_shutdown(xpath_neighbor)
        if update_source == "loopback":
            self.__bgp_neighbor_update_source(xpath_neighbor, loopback_ip)
        if local_as_status:
            self.__bgp_neighbor_local_as(xpath_neighbor, l3direct_bgp_info_dict)
        if timers_status:
            self.__bgp_neighbor_timers(xpath_neighbor, l3direct_bgp_info_dict)
        if rpl_in_name is not None:
            self.__bgp_neighbor_inbound_rpl(xpath_neighbor, l3direct_bgp_info_dict)
        if custom_rpl_in_name is not None:
            self.__bgp_neighbor_inbound_rpl(xpath_neighbor, l3direct_bgp_info_dict)
        if rpl_out_name is not None:
            self.__bgp_neighbor_outbound_rpl(xpath_neighbor, l3direct_bgp_info_dict)
        if custom_rpl_out_name is not None:
            self.__bgp_neighbor_outbound_rpl(xpath_neighbor, l3direct_bgp_info_dict)

    def __bgp_enable_max_paths(self, xpath_bgp):
        xpath_enable_max_paths = xpath_bgp + "/enable-maximum-paths"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_enable_max_paths}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create BGP Enable Max Paths:{response}")

    def __bgp_bfd(self, xpath_bgp, l3direct_bgp_info_dict):
        bfd_min_interval = l3direct_bgp_info_dict["Bfd Min Interval"]
        bfd_multiplier = l3direct_bgp_info_dict["Bfd Multiplier"]
        disable_fast_detect_status = l3direct_bgp_info_dict["Bfd Disable Fast Detect"]
        xpath_bgp_bfd = xpath_bgp + "/bfd"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_bgp_bfd}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create BGP BFD:{response}")
        xpath_bgp_bfd_min_interval = xpath_bgp_bfd + "/minimum-interval"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_bgp_bfd_min_interval, "value": bfd_min_interval}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value BGP BFD Minimum Interval:{response}")
        xpath_bgp_bfd_multiplier = xpath_bgp_bfd + "/multiplier"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_bgp_bfd_multiplier, "value": bfd_multiplier}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value BGP BFD Multiplier:{response}")
        if disable_fast_detect_status:
            xpath_bgp_bfd_disable_fast_detect = xpath_bgp_bfd + "/disable-fast-detect"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_bgp_bfd_disable_fast_detect}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            self.__logging_output(f"Create BGP BFD Disable-Fast-Detect:{response}")

    def __bgp_neighbor_nexthopself(self, xpath_neighbor):
        xpath_nexthopself = xpath_neighbor + "/next-hop-self"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_nexthopself, "value": True}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value BGP Neighbor Nexthopself:{response}")

    def __bgp_neighbor_unset_nexthopself_(self, xpath_neighbor):
        xpath_nexthopself = xpath_neighbor + "/next-hop-self"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_nexthopself, "value": False}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Unset Value BGP Neighbor Nexthopself:{response}")

    def __bgp_neighbor_remove_private_as(self, xpath_neighbor):
        xpath_remove_private_as = xpath_neighbor + "/remove-private-as"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_remove_private_as}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value BGP Neighbor Remove Private AS:{response}")

    def __bgp_neighbor_max_prefix(self, xpath_neighbor, max_prefix):
        xpath_max_prefix = xpath_neighbor + "/max-prefix"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_max_prefix, "value": max_prefix}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value BGP Neighbor Max Prefix:{response}")

    def __bgp_neighbor_action(self, xpath_neighbor, action):
        xpath_action = xpath_neighbor + "/action"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_action, "value": action}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value BGP Neighbor Action:{response}")

    def __bgp_neighbor_default_originate(self, xpath_neighbor):
        xpath_default_originate = xpath_neighbor + "/default-originate"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_default_originate}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value BGP Neighbor Default Originate:{response}")

    def __bgp_neighbor_password(self, xpath_neighbor, password):
        xpath_password = xpath_neighbor + "/password"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_password, "value": password}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value BGP Neighbor Password:{response}")

    def __bgp_neighbor_soft_reconfiguration(self, xpath_neighbor):
        xpath_soft_reconfiguration = xpath_neighbor + "/soft-reconfiguration"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_soft_reconfiguration}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create BGP Neighbor Soft Reconfiguration:{response}")

    def __bgp_neighbor_shutdown(self, xpath_neighbor):
        xpath_shutdown = xpath_neighbor + "/shutdown"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_shutdown}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create BGP Neighbor Shutdown:{response}")

    def __bgp_neighbor_update_source(self, xpath_neighbor, loopback_ip):
        xpath_update_source = xpath_neighbor + "/loopback"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_update_source}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create BGP Neighbor Update Source:{response}")
        xpath_update_source_loopback_ip = xpath_update_source + "/loopback-ip"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_update_source_loopback_ip, "value": loopback_ip}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value BGP Neighbor Update Source Loopback Ip:{response}")

    def __bgp_neighbor_local_as(self, xpath_neighbor, l3direct_bgp_info_dict):
        local_as = l3direct_bgp_info_dict["Local As"]
        local_as_no_prepend = l3direct_bgp_info_dict["Local As No Prepend"]
        local_as_replace_as = l3direct_bgp_info_dict["Local As Replace As"]
        xpath_local_as = xpath_neighbor + "/local-as/as-number"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_local_as, "value": local_as}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value BGP Neighbor Local AS:{response}")
        if local_as_no_prepend:
            self.__bgp_neighbor_local_as_no_prepend(xpath_neighbor)
        if local_as_replace_as:
            self.__bgp_local_as_replace_as(xpath_neighbor)

    def __bgp_neighbor_local_as_no_prepend(self, xpath_neighbor):
        xpath_local_as_no_prepend = xpath_neighbor + "/local-as/no-prepend"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_local_as_no_prepend}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create BGP Neighbor Local AS No-Prepend:{response}")

    def __bgp_local_as_replace_as(self, xpath_neighbor):
        xpath_local_as_replace_as = xpath_neighbor + "/local-as/replace-as"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_local_as_replace_as}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create BGP Neighbor Local AS Replace AS:{response}")

    def __bgp_neighbor_timers(self, xpath_neighbor, l3direct_bgp_info_dict):
        keepalive = l3direct_bgp_info_dict["Keepalive"]
        holdtime = l3direct_bgp_info_dict["Hold Time"]
        xpath_timer = xpath_neighbor + "/timers"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_timer}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create BGP Neighbor Custom Timers:{response}")
        xpath_timer_keepalive = xpath_timer + "/keepalive"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_timer_keepalive, "value": keepalive}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create BGP Neighbor Custom Timers Keepalive:{response}")
        xpath_timer_holdtime = xpath_timer + "/holdtime"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_timer_holdtime, "value": holdtime}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create BGP Neighbor Custom Timers Hold Time:{response}")

    def __bgp_neighbor_inbound_rpl(self, xpath_neighbor, l3direct_bgp_info_dict):
        name = l3direct_bgp_info_dict["In Rpl Name"]
        custom_policy_name = l3direct_bgp_info_dict["In Rpl Custom Policy Name"]
        prefix_list_name = l3direct_bgp_info_dict["In Rpl Prefix List"]
        blackhole_prefix_list_name = l3direct_bgp_info_dict["In Rpl Blackhole Prefix List"]
        local_pref = l3direct_bgp_info_dict["In Rpl Local Preference"]
        community_name = l3direct_bgp_info_dict["In Rpl Community Name"]
        community_list = l3direct_bgp_info_dict["In Rpl Community List"]
        as_path = l3direct_bgp_info_dict["In Rpl As Path"]
        multiplier = l3direct_bgp_info_dict["In Rpl Multiplier"]
        if name == "TENANT-EBGP-INET-123":
            self.__route_policies_inbound_tenant_ebgp_inet_123(xpath_neighbor, prefix_list_name)
        elif name == "TENANT-EBGP-INET-ONLY-LOCAL-PREF":
            self.__route_policies_inbound_tenant_ebgp_inet_only_local_pref(xpath_neighbor, prefix_list_name)
        elif name == "TENANT-EBGP-INET-ONLY-CUSTOMER-ROUTES":
            self.__route_policies_inbound_tenant_ebgp_inet_only_customer_routes(xpath_neighbor, prefix_list_name)
        elif name == "TENANT-EBGP-INET-123-LOCAL-PREF":
            self.__route_policies_inbound_tenant_ebgp_inet_123_local_pref(xpath_neighbor, local_pref, prefix_list_name)
        elif name == "TENANT-EBGP-INET-123-NAMED-COMM-LOCAL-PREF":
            self.__route_policies_inbound_tenant_ebgp_inet_123_named_comm_local_pref(xpath_neighbor, local_pref, prefix_list_name, community_name)
        elif name == "TENANT-EBGP-INET-123-CUSTOM-COMM-LOCAL-PREF":
            self.__route_policies_inbound_tenant_ebgp_inet_123_custom_comm_local_pref(xpath_neighbor, local_pref, prefix_list_name, community_name, community_list)
        elif name == "TENANT-EBGP-INET-SOL-ORIGIN-123-LOCAL-PREF":
            self.__route_policies_inbound_tenant_ebgp_inet_sol_origin_123_local_pref(xpath_neighbor, local_pref, prefix_list_name)
        elif name == "DEFAULT-ONLY":
            self.__route_policies_inbound_default_only(xpath_neighbor)
        elif name == "DENY-DEFAULT":
            self.__route_policies_inbound_deny_default(xpath_neighbor)
        elif name == "DENY-ANY":
            self.__route_policies_inbound_deny_any(xpath_neighbor)
        elif name == "INET-123-AS-PATH-PREPEND":
            self.__route_policies_inbound_inet_123_as_path_prepend(xpath_neighbor, as_path, multiplier, prefix_list_name)
        elif name == "LOCAL-PREF-444":
            self.__route_policies_inbound_local_pref_444(xpath_neighbor, prefix_list_name, local_pref)
        elif name == "LOCAL-PREF-666-AND-444":
            self.__route_policies_inbound_local_pref_666_and_444(xpath_neighbor, prefix_list_name, blackhole_prefix_list_name, local_pref)
        elif name == "PRIVATE-AS-456":
            self.__route_policies_inbound_private_as_456(xpath_neighbor, prefix_list_name, blackhole_prefix_list_name, local_pref)
        elif custom_policy_name is not None:
            self.__route_policies_inbound_custom_policy(xpath_neighbor, custom_policy_name)
        else:
            raise Exception("!!!Invalid Inbound Route Policy!!!")

    def __bgp_neighbor_outbound_rpl(self, xpath_neighbor, l3direct_bgp_info_dict):
        name = l3direct_bgp_info_dict["Out Rpl Name"]
        custom_policy_name = l3direct_bgp_info_dict["Out Rpl Custom Policy Name"]
        prefix_list_name = l3direct_bgp_info_dict["Out Rpl Prefix List"]
        as_path = l3direct_bgp_info_dict["Out Rpl As Path"]
        multiplier = l3direct_bgp_info_dict["Out Rpl Multiplier"]
        if name == "PASS-ALL":
            self.__route_policies_outbound_pass_all(xpath_neighbor)
        elif name == "DEFAULT-ONLY":
            self.__route_policies_outbound_default_only(xpath_neighbor)
        elif name == "DENY-DEFAULT":
            self.__route_policies_outbound_deny_default(xpath_neighbor)
        elif name == "DENY-ANY":
            self.__route_policies_outbound_deny_any(xpath_neighbor)
        elif name == "TENANT-EBGP-INET-FULL-ROUTE-NO-DEFAULT":
            self.__route_policies_outbound_tenant_ebgp_inet_full_route_no_default(xpath_neighbor)
        elif name == "TENANT-EBGP-INET-ONLY-CUSTOMER-ROUTES":
            self.__route_policies_outbound_tenant_ebgp_inet_only_customer_routes(xpath_neighbor, prefix_list_name)
        elif name == "TENANT-EBGP-INET-FULL-ROUTE":
            self.__route_policies_outbound_tenant_ebgp_inet_full_route(xpath_neighbor)
        elif name == "EBGP-PEERING-NO-DEFAULT":
            self.__route_policies_outbound_ebgp_peering_no_default(xpath_neighbor)
        elif name == "EBGP-PEERING-WITH-DEFAULT":
            self.__route_policies_outbound_ebgp_peering_with_default(xpath_neighbor)
        elif name == "INET-123-AS-PATH-PREPEND":
            self.__route_policies_outbound_inet_123_as_path_prepend(xpath_neighbor, as_path, multiplier, prefix_list_name)
        elif custom_policy_name is not None:
            self.__route_policies_outbound_custom_policy(xpath_neighbor, custom_policy_name)
        else:
            raise Exception("!!!Invalid Outbound Route Policy!!!")

    def create_l3direct_bgps(self):
        [self.__create_l3direct_bgp(l3direct_bgp_info_dict) for l3direct_bgp_info_dict in self.create_l3direct_bgp_info_dict_list()]
########################################################################################################################
# Dictionary Example for aggregate_routing_info_dict
# aggregate_routing_info_dict = {"Tenant Name": "T0001", "Service Name": "S0001", "Bd Name": "BD0001",
#                                "Epg Name": "EPG0001", "Encap Id": "1001", "IPv4 Prefix": "40.0.0.0/8", "Summary Only": True}
    
    def __create_l3direct_aggregate(self, l3direct_aggregate_info_dict):
        tenant_name = l3direct_aggregate_info_dict["Tenant Name"]
        service_name = l3direct_aggregate_info_dict["Service Name"]
        bd_name = l3direct_aggregate_info_dict["Bd Name"]
        epg_name = l3direct_aggregate_info_dict["Epg Name"]
        encap_id = l3direct_aggregate_info_dict["Encap Id"]
        ipv4_prefix = l3direct_aggregate_info_dict["IPv4 Prefix"]
        summary_only_status = l3direct_aggregate_info_dict["Summary Only"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_service = xpath_tenant + f"/service/dclan{{{service_name}}}"
        xpath_bd = xpath_service + f"/bd{{{bd_name}}}"
        xpath_epg = xpath_bd + f"/epg{{{epg_name}}}"
        xpath_encap = xpath_epg + f"/encap{{{encap_id}}}"
        xpath_l3direct = xpath_encap + "/l3direct"
        xpath_aggregate = xpath_l3direct + f"/aggregate-address{{{ipv4_prefix}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_aggregate}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create L3Direct Aggregate Address {ipv4_prefix}:{response}")
        if summary_only_status:
            xpath_aggregate_summary_only = xpath_aggregate + "/summary-only"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_aggregate_summary_only, "value": True}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            self.__logging_output(f"Set Value L3Direct Aggregate Address {ipv4_prefix} Summary Only:{response}")
            
    def create_l3direct_aggregates(self):
        [self.__create_l3direct_aggregate(l3direct_aggregate_info_dict) for l3direct_aggregate_info_dict in self.create_l3direct_aggregate_info_dict_list()]
########################################################################################################################
# Dictionary Example for l2ext_info_dict
# l2ext_info_dict = {"Tenant Name": "T0001", "Service Name": "S0001", "Bd Name": "BD0001", "Epg Name": "EPG0001", "Encap Id": "1001",
#                   "Dci Interface": "BLF_801_802_DCI_VPC_INTPOL", "Type": "EVPN", "Evi": "1001", "Circuit Id": None, "Neighbor Ip": None, "Pw Class": None, "Mtu": 9000}
    
    def __create_l2ext(self, l2ext_info_dict):
        tenant_name = l2ext_info_dict["Tenant Name"]
        service_name = l2ext_info_dict["Service Name"]
        bd_name = l2ext_info_dict["Bd Name"]
        epg_name = l2ext_info_dict["Epg Name"]
        encap_id = l2ext_info_dict["Encap Id"]
        dci_interface = l2ext_info_dict["Dci Interface"]
        l2ext_type = l2ext_info_dict["Type"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_service = xpath_tenant + f"/service/dclan{{{service_name}}}"
        xpath_bd = xpath_service + f"/bd{{{bd_name}}}"
        xpath_epg = xpath_bd + f"/epg{{{epg_name}}}"
        xpath_encap = xpath_epg + f"/encap{{{encap_id}}}"
        xpath_l2ext = xpath_encap + "/l2ext"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_l2ext}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Create L2Ext:{response}")
        xpath_l2ext_dci_interface = xpath_l2ext + "/name"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_l2ext_dci_interface, "value": dci_interface}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value L2Ext Name {dci_interface}:{response}")
        if l2ext_type == "EVPN":
            self.__create_l2ext_evpn(xpath_l2ext, l2ext_info_dict)
        elif l2ext_type == "VPLS":
            self.__create_l2ext_vpls(xpath_l2ext, l2ext_info_dict)
        else:
            raise Exception("!!!Invalid L2Ext Type!!!")

    def __create_l2ext_evpn(self, xpath_l2ext, l2ext_info_dict):
        evi = l2ext_info_dict["Evi"]
        mtu = l2ext_info_dict["Mtu"]
        xpath_l2ext_type = xpath_l2ext + "/type"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_l2ext_type, "value": "evpn"}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value L2VPN Type EVPN:{response}")
        xpath_l2ext_evi = xpath_l2ext + "/evi"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_l2ext_evi, "value": evi}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value EVPN EVI {evi}:{response}")
        xpath_l2ext_mtu = xpath_l2ext + "/mtu"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"path": xpath_l2ext_mtu, "value": mtu, "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value EVPN MTU {mtu}:{response}")

    def __create_l2ext_vpls(self, xpath_l2ext, l2ext_info_dict):
        circuit_id = l2ext_info_dict["Circuit Id"]
        neighbor_ip = l2ext_info_dict["Neighbor Ip"]
        pw_class = l2ext_info_dict["Pw Class"]
        xpath_l2ext_type = xpath_l2ext + "/type"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_l2ext_type, "value": "vpls"}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value L2VPN Type VPLS:{response}")
        xpath_l2ext_circuit_id = xpath_l2ext + "/circuit-id"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_l2ext_circuit_id, "value": circuit_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value VPLS Circuit Id {circuit_id}:{response}")
        xpath_l2ext_neighbor = xpath_l2ext + f"/neighbor{{{neighbor_ip}}}/pw-class"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_l2ext_neighbor, "value": pw_class}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Set Value VPLS Neighbor {neighbor_ip} and PW Class {pw_class}:{response}")

    def create_l2externals(self):
        [self.__create_l2ext(l2ext_info_dict) for l2ext_info_dict in self.create_l2ext_info_dict_list()]
########################################################################################################################
# transit_leaf_encap_info_dict =  {"Tenant Name": "ANADOLUHOLDING", "Service Name": "ANADOLUHOLDING-L2-VLAN2631", "Bd Name": "VLAN_2631_BD", "Epg Name": "VLAN_2631_EPG", "Encap Id": "2631"}
    
    def __create_transit_leaf_tenant_pa(self, transit_leaf_encap_info_dict, tenant_pa_name):
        tenant_name = transit_leaf_encap_info_dict["Tenant Name"]
        service_name = transit_leaf_encap_info_dict["Service Name"]
        bd_name = transit_leaf_encap_info_dict["Bd Name"]
        epg_name = transit_leaf_encap_info_dict["Epg Name"]
        encap_id = transit_leaf_encap_info_dict["Encap Id"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_service = xpath_tenant + f"/service/dclan{{{service_name}}}"
        xpath_bd = xpath_service + f"/bd{{{bd_name}}}"
        xpath_epg = xpath_bd + f"/epg{{{epg_name}}}"
        xpath_encap = xpath_epg + f"/encap{{{encap_id}}}"
        external_tenant_name = "TRANSIT_LEAF"
        tenant_pa_mode = "regular"
        external_tenant_pa_name = f"{external_tenant_name} {tenant_pa_name}"
        xpath_external_tenant_pa = xpath_encap + f"/external-tenant-pa{{{external_tenant_pa_name}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "create", "params": {"th": self.th_id, "path": xpath_external_tenant_pa}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"{tenant_name} {service_name} {bd_name} {epg_name} {encap_id} Create External Tenant Pa {tenant_pa_name}:{response}")
        xpath_external_tenant_pa_mode = xpath_external_tenant_pa + "/mode"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "set_value", "params": {"th": self.th_id, "path": xpath_external_tenant_pa_mode, "value": tenant_pa_mode}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"{tenant_name} {service_name} {bd_name} {epg_name} {encap_id} Set Value External Tenant Pa {tenant_pa_name} Mode:{response}")

    def create_transit_leaf_tenant_pas(self, tenant_pa_name=None, fabric=None):
        query_l2ext_encap_id_info_dict_list = self.__query_l2ext_encap_id(fabric_condition=fabric)
        [self.__create_transit_leaf_tenant_pa(transit_leaf_encap_info_dict, tenant_pa_name) for transit_leaf_encap_info_dict in self.create_transit_leaf_encap_info_dict_list(query_l2ext_encap_id_info_dict_list)]
########################################################################################################################
# transit_leaf_encap_info_dict =  {"Tenant Name": "ANADOLUHOLDING", "Service Name": "ANADOLUHOLDING-L2-VLAN2631", "Bd Name": "VLAN_2631_BD", "Epg Name": "VLAN_2631_EPG", "Encap Id": "2631", "Tenant Pa Name": "transit_leaf_lf_105-106_4344"}

    def __query_transit_leaf_tenant_pa(self):
        xpath_external_tenant_pa = f"/acidc/tenants/acidc-services:service/dclan/bd/epg/encap/external-tenant-pa[tenant='TRANSIT_LEAF']"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "query", "params": {"context_node": "/acidc", "xpath_expr": xpath_external_tenant_pa,
                   "selection": ["../../../../../../tenant", "../../../../name", "../../../name", "../../name", "../dot1q", "tenant-pa"],
                   "result_as": "keypath-value", "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        response_dict = json.loads(response)
        transit_leaf_tenant_pa_info_dict_list = helpers.query_transit_leaf_tenant_pa_helper(response_dict)

        return transit_leaf_tenant_pa_info_dict_list

    def __remove_transit_leaf_tenant_pa(self, external_tenant_pa_info_dict):
        tenant_name = external_tenant_pa_info_dict["Tenant Name"]
        service_name = external_tenant_pa_info_dict["Service Name"]
        bd_name = external_tenant_pa_info_dict["Bd Name"]
        epg_name = external_tenant_pa_info_dict["Epg Name"]
        encap_id = external_tenant_pa_info_dict["Encap Id"]
        tenant_pa_name = external_tenant_pa_info_dict["Tenant Pa Name"]
        external_tenant_name = "TRANSIT_LEAF"
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_service = xpath_tenant + f"/service/dclan{{{service_name}}}"
        xpath_bd = xpath_service + f"/bd{{{bd_name}}}"
        xpath_epg = xpath_bd + f"/epg{{{epg_name}}}"
        xpath_encap = xpath_epg + f"/encap{{{encap_id}}}"
        external_tenant_pa_name = f"{external_tenant_name} {tenant_pa_name}"
        xpath_external_tenant_pa = xpath_encap + f"/external-tenant-pa{{{external_tenant_pa_name}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "delete", "params": {"path": xpath_external_tenant_pa, "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Tenant:{tenant_name} Service:{service_name} Delete External Tenant Pa {external_tenant_pa_name}:{response}")

    def remove_transit_leaf_tenant_pas(self, pa_name):
        [self.__remove_transit_leaf_tenant_pa(external_tenant_pa_info_dict) for external_tenant_pa_info_dict in self.__query_transit_leaf_tenant_pa()]
########################################################################################################################
# Dictionary Example for tenant_pa_info_dict
# tenant_pa_info_dict = {"Tenant Name": "T0001", "Service Name": "S0001", "Bd Name": "BD0001", "Epg Name": "EPG0001",
#                        "Encap Id": "1001", "Tenant Pa Type": "external", "External Tenant Name": "T0002", "Pa Name": "SA0001", "Mode": "regular"}

    def __remove_tenant_pa(self, tenant_pa_info_dict):
        tenant_name = tenant_pa_info_dict["Tenant Name"]
        service_name = tenant_pa_info_dict["Service Name"]
        bd_name = tenant_pa_info_dict["Bd Name"]
        epg_name = tenant_pa_info_dict["Epg Name"]
        encap_id = tenant_pa_info_dict["Encap Id"]
        tenant_pa_type = tenant_pa_info_dict["Tenant Pa Type"]
        tenant_pa_name = tenant_pa_info_dict["Pa Name"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_service = xpath_tenant + f"/service/dclan{{{service_name}}}"
        xpath_bd = xpath_service + f"/bd{{{bd_name}}}"
        xpath_epg = xpath_bd + f"/epg{{{epg_name}}}"
        xpath_encap = xpath_epg + f"/encap{{{encap_id}}}"
        if tenant_pa_type == "internal":
            xpath_tenant_pa = xpath_encap + f"/tenant-pa{{{tenant_pa_name}}}"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "delete", "params": {"path": xpath_tenant_pa, "th": self.th_id}}
        else:
            external_tenant_name = tenant_pa_info_dict["External Tenant Name"]
            xpath_external_tenant_pa = xpath_encap + f"external-tenant-pa{{{external_tenant_name} {tenant_pa_name}}}"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "delete", "params": {"path": xpath_external_tenant_pa, "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Tenant:{tenant_name} Service:{service_name} Delete Tenant Pa {tenant_pa_name}:{response}")

    def remove_tenant_pas(self):
        [self.__remove_tenant_pa(tenant_pa_info_dict) for tenant_pa_info_dict in self.create_tenant_pa_info_dict_list()]
########################################################################################################################
# Dictionary Example for pa_info_dict
# pa_info_dict= {"Tenant Name":tenant_name,"Pa Name":pa_name,"Fabric":fabric,"Pod":pod,"Pa Type":pa_type,"Interface Profile":interface_profile,"Node  Id":node_id,
#                "Node Port List":[node_port1,node_port2]},"Node Id 1":node_id_1,"Node Id 2":node_id_2,"Node 1 Port List":[node_port1,node_port2],"Node 2 Port List":[node_port1,node_port2]}

    def __remove_port_pa(self, pa_info_dict):
        tenant_name = pa_info_dict["Tenant Name"]
        pa_name = pa_info_dict["Pa Name"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_pa = xpath_tenant + f"/port/pa{{{pa_name}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "delete", "params": {"path": xpath_pa, "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Tenant:{tenant_name} Delete Port Pa {pa_name}:{response}")

    def remove_port_pas(self):
        [self.__remove_port_pa(pa_info_dict) for pa_info_dict in self.create_pa_info_dict_list()]
########################################################################################################################
# Dictionary Example for service_info_dict
# service_info_dict = {"Tenant Name":tenant_name,"Service Name":service_name,"Fabric":fabric}

    def __remove_service(self, service_info_dict):
        tenant_name = service_info_dict["Tenant Name"]
        service_name = service_info_dict["Service Name"]
        xpath_tenant = f"/acidc/tenants{{{tenant_name}}}"
        xpath_service = xpath_tenant + f"/service/dclan/{{{service_name}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "delete", "params": {"path": xpath_service, "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Tenant:{tenant_name} Delete Service {service_name}:{response}")

    def remove_services(self):
        [self.__remove_service(service_info_dict) for service_info_dict in self.create_service_info_dict_list()]
########################################################################################################################
# Dictionary Example for query_port_pa_info_dict
# query_port_pa_info_dict = {'Pa Name': 'solvoyo_lf331_e4', 'Fabric': 'gbz-aci-sol-fabric-5-6', 'Pa Type': 'SA', 'Node Id': '331',
#                           'Node Port': '1/4', 'Node Id 1': None, 'Node Id 1 Port': None, 'Node Id 2': None, 'Node Id 2 Port': None}

    def __query_port_pa(self):
        xpath_port_pa = "/acidc/tenants/acidc-pa:port/pa/fabric"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "query", "params": {"context_node": "/acidc", "xpath_expr": xpath_port_pa,
                   "selection": ["name", "fabric", "type", "node-id", "node-port-flat", "node-1-id", "node-1-port-flat", "node-2-id", "node-2-port-flat"],
                   "result_as": "keypath-value", "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        response_dict = json.loads(response)
        query_port_pa_info_dict_list = helpers.query_port_pa_helper(response_dict)

        return query_port_pa_info_dict_list

    def __query_port_pa_conditional(self, name_condition, tenant_condition, fabric_condition):
        xpath_port_pa = f"/acidc/tenants/acidc-pa:port/pa/name[contains(.,'{name_condition}') and ../fabric='{fabric_condition}' and ../../../tenant='{tenant_condition}']"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "query", "params": {"context_node": "/acidc", "xpath_expr": xpath_port_pa,
                   "selection": ["../../../tenant", ".", "../fabric"],
                   "result_as": "keypath-value", "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        response_dict = json.loads(response)
        query_port_pa_conditional_info_dict_list = helpers.query_port_pa_conditional_helper(response_dict)

        return query_port_pa_conditional_info_dict_list

    def __query_port_pa_externally_used_by(self, port_pa_info_dict_list=[]):
        externally_used_by_dict_list = []
        for port_pa_info_dict in port_pa_info_dict_list:
            tenant_name = port_pa_info_dict["Tenant Name"]
            pa_name = port_pa_info_dict["Pa Name"]
            xpath_port_pa_externally_used_by = f"/acidc/tenants{{{tenant_name}}}/port/pa{{{pa_name}}}"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "query", "params": {"xpath_expr": "external-used-by", "result_as": "keypath-value", "selection": ["tenant", "dclan"], "context_node": xpath_port_pa_externally_used_by, "th": 1}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            response_dict = json.loads(response)
            externally_used_by_dict_list.extend(helpers.query_port_pa_externally_used_by_helper(pa_name, response_dict))
        self.df_port_pa_externally_used_by = helpers.query_port_pa_externally_used_by_df_helper(externally_used_by_dict_list)
        self.__query_to_file(self.df_port_pa_externally_used_by, "PA EXTERNALLY USED BY")

    def precheck_port_pa(self):
        pa_problems = []
        port_pa_info_dict_list = self.create_pa_info_dict_list()
        query_port_pa_info_dict_list = self.__query_port_pa()
        for port_pa_info_dict in port_pa_info_dict_list:
            fabric = port_pa_info_dict["Fabric"]
            tenant_name = port_pa_info_dict["Tenant Name"]
            pa_name = port_pa_info_dict["Pa Name"]
            pa_type = port_pa_info_dict["Pa Type"]
            interface_profile = port_pa_info_dict["Interface Profile"]
            node_id = port_pa_info_dict["Node Id"]
            node_port_list = port_pa_info_dict["Node Port List"]
            node_id_1 = port_pa_info_dict["Node Id 1"]
            node_id_2 = port_pa_info_dict["Node Id 2"]
            node_id_1_port_list = port_pa_info_dict["Node Id 1 Port List"]
            node_id_2_port_list = port_pa_info_dict["Node Id 2 Port List"]
            if pa_type == "SA":
                pa_problems.extend(helpers.precheck_port_pa_sa_helper(fabric, tenant_name, pa_name, interface_profile, node_id, node_port_list, query_port_pa_info_dict_list))
            elif pa_type == "PC":
                pa_problems.extend(helpers.precheck_port_pa_pc_helper(fabric, tenant_name, pa_name, node_id, node_port_list, query_port_pa_info_dict_list))
            elif pa_type == "VPC":
                pa_problems.extend(helpers.precheck_port_pa_vpc_helper(fabric, tenant_name, pa_name, node_id_1, node_id_1_port_list, node_id_2, node_id_2_port_list, query_port_pa_info_dict_list))
            else:
                raise Exception("Invalid Port PA Type!!!")
        self.df_pa_problems = helpers.precheck_port_pa_df(pa_problems)

    def get_port_pa_with_conditions(self, name_condition, tenant_condition, fabric_condition):
        query_port_pa_conditional_info_dict_list = self.__query_port_pa_conditional(name_condition, tenant_condition, fabric_condition)
        self.__query_port_pa_externally_used_by(query_port_pa_conditional_info_dict_list)
########################################################################################################################
# Dictionary Example for query_vrf_info_dict
# query_vrf_info_dict = {'Tenant Name': 'ADALET-BAKANLIGI', 'Vrf Name': 'ADALET-BAKANLIGI-mpls', 'Vpn Id': '4154'}

    def __query_vrf(self):
        xpath_vrf = "/acidc/tenants/acidc-services:vrf[vrf-type='private']"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "query", "params": {"context_node": "/acidc", "xpath_expr": xpath_vrf,
                   "selection": ["../tenant", "name", "vpn-id"], "result_as": "keypath-value", "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        response_dict = json.loads(response)
        query_vrf_info_dict_list = helpers.query_vrf_helper(response_dict)

        return query_vrf_info_dict_list

    def precheck_vrf(self):
        vrf_info_dict_list = self.create_vrf_info_dict_list()
        query_vrf_info_dict_list = self.__query_vrf()
        vrf_problems = helpers.precheck_vpn_id_helper(vrf_info_dict_list, query_vrf_info_dict_list)
        self.df_vrf_problems = helpers.precheck_vrf_df(vrf_problems)
########################################################################################################################
# Dictionary Example for query_tenant_info_dict
# query_tenant_info_dict = {'Tenant Name': 'ADALET-BAKANLIGI'}

    def __query_tenant(self):
        xpath_tenant = "/acidc/tenants"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "query", "params": {"context_node": "/acidc", "xpath_expr": xpath_tenant,
                   "selection": ["tenant"], "result_as": "keypath-value", "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        response_dict = json.loads(response)
        query_tenant_info_dict_list = helpers.query_tenant_helper(response_dict)

        return query_tenant_info_dict_list

    def precheck_tenant(self):
        tenant_info_dict_list = self.create_tenant_info_dict_list()
        query_tenant_info_dict_list = self.__query_tenant()
        tenant_problems = helpers.precheck_tenant_helper(tenant_info_dict_list, query_tenant_info_dict_list)
        self.df_tenant_problems = helpers.precheck_tenant_df(tenant_problems)
########################################################################################################################
# Dictionary Example for query_tenant_info_dict
# service_info_dict = {"Tenant Name":tenant_name,"Service Name":service_name,"Fabric":fabric}

    def __query_service(self):
        xpath_service = "/acidc/tenants/service/dclan"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "query", "params": {"context_node": "/acidc", "xpath_expr": xpath_service,
                   "selection": ["../../tenant", "name", "fabric"], "result_as": "keypath-value", "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        response_dict = json.loads(response)
        query_service_info_dict_list = helpers.query_service_helper(response_dict)

        return query_service_info_dict_list

    def precheck_service(self):
        service_info_dict_list = self.create_service_info_dict_list()
        query_service_info_dict_list = self.__query_service()
        service_problems = helpers.precheck_service_helper(service_info_dict_list, query_service_info_dict_list)
        self.df_service_problems = helpers.precheck_service_df(service_problems)
########################################################################################################################
# Dictionary Example for query_node_info_dict
# node_info_dict = {"Fabric":fabric_name,"Pod":pod_id,"Node Id":node_id}

    def __query_node_id(self, fabric):
        xpath_node = f"/acidc/acidc-env:environment/fabric[name='{fabric}']/available/pod/node"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "query", "params": {"context_node": "/acidc", "xpath_expr": xpath_node,
                   "selection": ["../../../name", "../id", "id"], "result_as": "keypath-value", "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        response_dict = json.loads(response)
        query_node_id_info_dict_list = helpers.query_node_id_helper(response_dict)

        return query_node_id_info_dict_list

    def precheck_node_id(self, fabric):
        port_pa_info_dict_list = self.create_pa_info_dict_list()
        query_node_id_info_dict_list = self.__query_node_id(fabric)
        node_id_problems = helpers.precheck_node_id_helper(port_pa_info_dict_list, query_node_id_info_dict_list)
        self.df_node_id_problems = helpers.precheck_node_id_df(node_id_problems)

########################################################################################################################
# Dictionary Example for query_l2ext_encap_id_info_dict
# query_l2ext_encap_id_info_dict = {'Tenant Name': 'AKER', 'Service Name': 'GBZ3-AKER_MAGAZA-L2-VLAN2727', 'Encap Id': '2727'}

    def __query_l2ext_encap_id(self, fabric_condition):
        xpath_l2ext = f"/acidc/tenants/acidc-services:service/dclan/bd/epg/encap/l2ext[type='evpn' and ../../../../fabric='{fabric_condition}']"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "query", "params": {"context_node": "/acidc", "xpath_expr": xpath_l2ext, "selection": ["evi", "../dot1q", "../../../name", "../../../../name", "../../../../../../tenant"], "result_as": "keypath-value", "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        response_dict = json.loads(response)
        query_l2ext_encap_id_info_dict_list = helpers.query_l2ext_encap_id_helper(response_dict)

        return query_l2ext_encap_id_info_dict_list

########################################################################################################################
    def precheck_l2ext(self, fabric):
        l2ext_info_dict_list = self.create_l2ext_info_dict_list()
        query_l2ext_info_dict_list = self.__query_l2ext_encap_id(fabric)
        query_transit_leaf_tenant_pa_info_dict_list = self.__query_transit_leaf_tenant_pa()
        l2ext_problems = helpers.precheck_l2ext_helper(l2ext_info_dict_list, query_transit_leaf_tenant_pa_info_dict_list, query_l2ext_info_dict_list)
        self.df_l2ext_problems = helpers.precheck_l2ext_df_helper(l2ext_problems)

########################################################################################################################
# Dictionary Example for query_l2ext_encap_id_info_dict
# query_l3direct_bgp_info_dict = {'Tenant Name': 'AKER', 'Service Name': 'GBZ3-AKER_MAGAZA-L2-VLAN2727'}

    def __query_l3direct_bgp(self):
        xpath_l3direct_bgp = f"/acidc/tenants/acidc-services:service/dclan/bd/epg/encap/l3direct/bgp"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "query",
                   "params": {"context_node": "/acidc", "xpath_expr": xpath_l3direct_bgp,
                              "selection": ["../../../../../../../tenant", "../../../../../name"],
                              "result_as": "keypath-value", "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        response_dict = json.loads(response)
        query_l3direct_bgp_info_dict_list = helpers.query_l3direct_bgp_helper(response_dict)

        return query_l3direct_bgp_info_dict_list

    def get_l3direct_bgp(self):
        df = pd.DataFrame.from_dict(self.__query_l3direct_bgp(), orient="index")
        with pd.ExcelWriter("NSO_L3DIRECT_BGP.xlsx") as writer:
            df.to_excel(writer, sheet_name="BGP")

########################################################################################################################

    def precheck_to_file(self):
        helpers.precheck_file(self.df_tenant_problems, self.df_service_problems, self.df_pa_problems, self.df_vrf_problems, self.df_node_id_problems, self.df_l2ext_problems, self.file_name)

########################################################################################################################

    @staticmethod
    def __query_to_file(df=pd.DataFrame(), file_name=None):
        helpers.query_file(df, file_name)

########################################################################################################################

    def __logging_output(self, logging_message):
        print(logging_message)
        if '{"jsonrpc":"2.0","result":{},"id":1}' in logging_message or '{"jsonrpc":"2.0","result":{"th":1},"id":1}' in logging_message or 'RequestsCookieJar' in logging_message:
            self.logger.info(logging_message)
        elif 'dry_run_result' in logging_message:
            pass
        else:
            self.logger.error(logging_message)

########################################################################################################################

    def validate_commit(self):
        payload = {"jsonrpc": "2.0", "id": 1, "method": "validate_commit", "params": {"th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Validate Commit:{response}")

########################################################################################################################

    def clear_validate_lock(self):
        payload = {"jsonrpc": "2.0", "id": 1, "method": "clear_validate_lock", "params": {"th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Clear Validate Lock:{response}")

########################################################################################################################

    def get_transaction_change(self, devices_list=[]):
        payload = {"jsonrpc": "2.0", "id": 1, "method": "get_trans_changes", "params": {"th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Get Transaction Change:{response}")
        flag = helpers.get_transaction_change_helper(response, devices_list)
        if flag:
            self.clear_validate_lock()
            raise Exception("!!!Transaction Change On Modifed Devices Out Of This Fabric!!!")

########################################################################################################################

    def commit_nonetworking(self):
        payload = {"jsonrpc": "2.0", "id": 1, "method": "commit", "params": {"th": self.th_id, "flags": ["no-networking"]}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Commit No-Networking:{response}")

########################################################################################################################

    def commit_dryrun(self):
        payload = {"jsonrpc": "2.0", "id": 1, "method": "commit", "params": {"th": self.th_id, "flags": ["dry-run=cli"]}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Commit Dry-Run:{response}")
        response_dict = json.loads(response)
        output = helpers.commit_dryrun_helper(response_dict)
        file_name = "NSO_POSTCHECK_{}.txt".format(self.file_name.strip(".xlsx"))
        with open(file_name, "w") as f:
            f.write(output)
########################################################################################################################

    def commit(self):
        payload = {"jsonrpc": "2.0", "id": 1, "method": "commit", "params": {"th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.__logging_output(f"Commit:{response}")
