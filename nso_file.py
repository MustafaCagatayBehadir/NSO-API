import pandas as pd
import numpy as np
import helpers
import logging
from time import strftime


class NsoFile:

    def __init__(self, file_name=None):
        logging.basicConfig(level=logging.DEBUG)
        self.file_name = file_name
        self.df_service_base = pd.read_excel(self.file_name, sheet_name="SERVICE BASE")
        self.df_service_base.fillna({"SHARED TENANT": False}, inplace=True)
        self.df_service_base.replace({np.nan: None}, inplace=True)
        self.df_service_base = self.df_service_base.astype({"SHARED TENANT": bool})
        self.df_vrf = pd.read_excel(self.file_name, sheet_name="VRF")
        self.df_vrf.fillna({"DEFAULT ORIGINATE": False, "DISABLE PRIMARY RT": False, "RP MANAGEMENT 888": False, "VRF POLICY": False}, inplace=True)
        self.df_vrf.replace({np.nan: None}, inplace=True)
        self.df_vrf = self.df_vrf.astype({"DEFAULT ORIGINATE": bool, "DISABLE PRIMARY RT": bool, "RP MANAGEMENT 888": bool, "VRF POLICY": bool})
        self.df_pa = pd.read_excel(self.file_name, sheet_name="PA")
        self.df_pa.replace({np.nan: None}, inplace=True)
        self.df_prefix_list = pd.read_excel(self.file_name, sheet_name="PREFIX LIST")
        self.df_prefix_list.replace({np.nan: None}, inplace=True)
        self.df_l3direct = pd.read_excel(self.file_name, sheet_name="L3DIRECT")
        self.df_l3direct.fillna({"SHUTDOWN": False, "SERVICE POLICY": False}, inplace=True)
        self.df_l3direct.replace({np.nan: None}, inplace=True)
        self.df_l3direct = self.df_l3direct.astype({"SHUTDOWN": bool, "SERVICE POLICY": bool})
        self.df_l3direct_static = pd.read_excel(self.file_name, sheet_name="L3DIRECT STATIC")
        self.df_l3direct_static.replace({np.nan: None}, inplace=True)
        self.df_l3direct_ospf = pd.read_excel(self.file_name, sheet_name="L3DIRECT OSPF")
        self.df_l3direct_ospf.fillna({"DEFAULT ORIGINATE": False}, inplace=True)
        self.df_l3direct_ospf.replace({np.nan: None}, inplace=True)
        self.df_l3direct_ospf = self.df_l3direct_ospf.astype({"DEFAULT ORIGINATE": bool})
        self.df_l3direct_aggregate = pd.read_excel(self.file_name, sheet_name="L3DIRECT AGGREGATE")
        self.df_l3direct_aggregate.fillna({"SUMMARY ONLY": False}, inplace=True)
        self.df_l3direct_aggregate.replace({np.nan: None}, inplace=True)
        self.df_l3direct_aggregate = self.df_l3direct_aggregate.astype({"SUMMARY ONLY": bool})
        self.df_l3direct_bgp = pd.read_excel(self.file_name, sheet_name="L3DIRECT BGP")
        self.df_l3direct_bgp.fillna({"ENABLE MAX PATHS": False, "BFD STATUS": False, "BFD DISABLE FAST DETECT": False, "NEXTHOPSELF": False,
                                     "REMOVE PRIVATE AS": False, "DEFAULT ORIGINATE": False, "SOFT RECONFIGURATION": False, "SHUTDOWN": False,
                                     "LOCAL AS STATUS": False, "LOCAL AS NO PREPEND": False, "LOCAL AS REPLACE AS": False, "CUSTOM TIMERS STATUS": False}, inplace=True)
        self.df_l3direct_bgp.replace({np.nan: None}, inplace=True)
        self.df_l3direct_bgp = self.df_l3direct_bgp.astype({"ENABLE MAX PATHS": bool, "BFD STATUS": bool, "BFD DISABLE FAST DETECT": bool, "NEXTHOPSELF": bool,
                                                            "REMOVE PRIVATE AS": bool, "DEFAULT ORIGINATE": bool, "SOFT RECONFIGURATION": bool, "SHUTDOWN": bool,
                                                            "LOCAL AS STATUS": bool, "LOCAL AS NO PREPEND": bool, "LOCAL AS REPLACE AS": bool, "CUSTOM TIMERS STATUS": bool})
        self.df_l2ext = pd.read_excel(self.file_name, sheet_name="L2EXTERNAL")
        self.df_l2ext.replace({np.nan: None}, inplace=True)
        self.df_delete_l3direct_shutdown = pd.read_excel(self.file_name, sheet_name="L3DIRECT")
        self.tenant_info_dict_list = []
        self.service_info_dict_list = []
        self.vrf_info_dict_list = []
        self.bd_info_dict_list = []
        self.epg_info_dict_list = []
        self.encap_info_dict_list = []
        self.pa_info_dict_list = []
        self.pa_info_dict_list_with_df = []
        self.tenant_pa_info_dict_list = []
        self.tenant_pa_info_dict_list_with_df = []
        self.prefix_list_info_dict_list = []
        self.l3direct_info_dict_list = []
        self.l3direct_static_info_dict_list = []
        self.l3direct_ospf_info_dict_list = []
        self.l3direct_bgp_info_dict_list = []
        self.l3direct_aggregate_info_dict_list = []
        self.l2ext_info_dict_list = []
        self.transit_leaf_encap_info_dict_list = []
        self.delete_l3direct_shutdown_info_dict_list = []
        # Create logger for nso provision
        self.logger = logging.getLogger("NSO LOGGER")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        # create console handler with a higher log level
        self.ch_error = logging.StreamHandler()
        self.ch_error.setLevel(logging.ERROR)
        self.ch_error.setFormatter(logging.Formatter('Date-Time : %(asctime)s : %(levelname)s : %(message)s'))
        # create file handler which logs even debug messages
        self.fh_debug = logging.FileHandler("log/{}_nso_provision_debug_{}.log".format(self.file_name, strftime("%Y-%m-%d_%H-%M-%S")))
        self.fh_debug.setLevel(logging.DEBUG)
        # create file handler which logs error messages
        self.fh_error = logging.FileHandler("log/{}_nso_provision_error_{}.log".format(self.file_name, strftime("%Y-%m-%d_%H-%M-%S")))
        self.fh_error.setLevel(logging.ERROR)
        # create formatter and add it to the handlers
        self.fh_debug.setFormatter(logging.Formatter('Date-Time : %(asctime)s : %(levelname)s : %(message)s'))
        self.fh_error.setFormatter(logging.Formatter('Date-Time : %(asctime)s : %(levelname)s : %(message)s'))
        # add the handlers to the logger
        self.logger.addHandler(self.fh_debug)
        self.logger.addHandler(self.fh_error)
        self.logger.addHandler(self.ch_error)
########################################################################################################################
############################################Tenant Info Dictionary List#################################################

    def create_tenant_info_dict_list(self):
        df = self.df_service_base
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            shared_tenant_status = df.loc[index]["SHARED TENANT"]
            tenant_info_dict = {"Tenant Name": tenant_name, "Shared Tenant": shared_tenant_status}
            if tenant_info_dict not in self.tenant_info_dict_list:
                self.tenant_info_dict_list.append(tenant_info_dict)
        self.tenant_info_dict_list = sorted(self.tenant_info_dict_list, key=lambda k: k["Tenant Name"])

        return self.tenant_info_dict_list
########################################################################################################################
############################################Service Info Dictionary List################################################

    def create_service_info_dict_list(self):
        df = self.df_service_base
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            service_name = df.loc[index]["SERVICE NAME"]
            fabric = df.loc[index]["FABRIC"]
            service_info_dict = {"Tenant Name": tenant_name, "Service Name": service_name, "Fabric": fabric}
            if service_info_dict not in self.service_info_dict_list:
                self.service_info_dict_list.append(service_info_dict)
        service_info_dict_list = sorted(self.service_info_dict_list, key=lambda k: k["Tenant Name"])

        return service_info_dict_list
########################################################################################################################
############################################VRF Info Dictionary List####################################################

    def create_vrf_info_dict_list(self):
        df = self.df_vrf
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            vrf_name = df.loc[index]["VRF NAME"]
            default_originate_status = df.loc[index]["DEFAULT ORIGINATE"]
            vrf_type = df.loc[index]["VRF TYPE"]
            vpn_id = df.loc[index]["VPN ID"]
            disable_primary_rt_status = df.loc[index]["DISABLE PRIMARY RT"]
            custom_import_rt_list = df.loc[index]["CUSTOM IMPORT RT LIST"]
            custom_export_rt_list = df.loc[index]["CUSTOM EXPORT RT LIST"]
            policy = df.loc[index]["FABRIC"]
            rp_management_888_status = df.loc[index]["RP MANAGEMENT 888"]
            static = df.loc[index]["STATIC"]
            connected = df.loc[index]["CONNECTED"]
            vrf_policy_status = df.loc[index]["VRF POLICY"]
            vrf_export_policy = df.loc[index]["VRF EXPORT POLICY"]
            vrf_import_policy = df.loc[index]["VRF IMPORT POLICY"]
            vrf_export_policy_prefix_list = df.loc[index]["VRF EXPORT POLICY PREFIX LIST"]
            vrf_export_policy_local_preference = df.loc[index]["VRF EXPORT POLICY LOCAL PREFERENCE"]
            vrf_import_policy_prefix_list = df.loc[index]["VRF IMPORT POLICY PREFIX LIST"]
            vrf_info_dict = {"Tenant Name": tenant_name, "Vrf Name": vrf_name,
                             "Default Originate": default_originate_status, "Vrf Type": vrf_type,
                             "Vpn Id": vpn_id, "Disable Primary RT": disable_primary_rt_status,
                             "Custom Import RT List": custom_import_rt_list,
                             "Custom Export RT List": custom_export_rt_list, "Policy": policy,
                             "RP Management 888": rp_management_888_status,
                             "Static": static, "Connected": connected, "Vrf Policy": vrf_policy_status,
                             "Vrf Export Policy": vrf_export_policy, "Vrf Import Policy": vrf_import_policy,
                             "Vrf Export Policy Prefix List": vrf_export_policy_prefix_list,
                             "Vrf Export Policy Local Preference": vrf_export_policy_local_preference,
                             "Vrf Import Policy Prefix List": vrf_import_policy_prefix_list}
            if vrf_info_dict not in self.vrf_info_dict_list:
                self.vrf_info_dict_list.append(vrf_info_dict)
        self.vrf_info_dict_list = helpers.vrf_info_dict_list_helper(self.vrf_info_dict_list)
        return self.vrf_info_dict_list
########################################################################################################################
############################################BD Info Dictionary List#####################################################

    def create_bd_info_dict_list(self):
        bd_info_dict_list = []
        df = self.df_service_base
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            service_name = df.loc[index]["SERVICE NAME"]
            vrf_name = df.loc[index]["VRF NAME"]
            bd_name = df.loc[index]["BRIDGE DOMAIN NAME"]
            bd_info_dict = {"Tenant Name": tenant_name, "Service Name": service_name, "Bd Name": bd_name, "Vrf Name": vrf_name}
            if bd_info_dict not in bd_info_dict_list:
                bd_info_dict_list.append(bd_info_dict)
        bd_info_dict_list = sorted(bd_info_dict_list, key=lambda k: k["Tenant Name"])

        return bd_info_dict_list
########################################################################################################################
############################################EPG Info Dictionary List####################################################

    def create_epg_info_dict_list(self):
        df = self.df_service_base
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            service_name = df.loc[index]["SERVICE NAME"]
            bd_name = df.loc[index]["BRIDGE DOMAIN NAME"]
            epg_name = df.loc[index]["EPG NAME"]
            epg_info_dict = {"Tenant Name": tenant_name, "Service Name": service_name, "Bd Name": bd_name, "Epg Name": epg_name}
            if epg_info_dict not in self.epg_info_dict_list:
                self.epg_info_dict_list.append(epg_info_dict)
        self.epg_info_dict_list = sorted(self.epg_info_dict_list, key=lambda k: k["Tenant Name"])

        return self.epg_info_dict_list
########################################################################################################################
############################################ENCAP Info Dictionary List##################################################

    def create_encap_info_dict_list(self):
        df = self.df_service_base
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            service_name = df.loc[index]["SERVICE NAME"]
            bd_name = df.loc[index]["BRIDGE DOMAIN NAME"]
            epg_name = df.loc[index]["EPG NAME"]
            encap_id = df.loc[index]["ENCAP ID"]
            encap_info_dict = {"Tenant Name": tenant_name, "Service Name": service_name, "Bd Name": bd_name,
                               "Epg Name": epg_name, "Encap Id": encap_id}
            if encap_info_dict not in self.encap_info_dict_list:
                self.encap_info_dict_list.append(encap_info_dict)
        self.encap_info_dict_list = helpers.encap_info_dict_list_helper(self.encap_info_dict_list)

        return self.encap_info_dict_list
########################################################################################################################
############################################PORT PA Info Dictionary List################################################

    def create_pa_info_dict_list(self):
        df = self.df_pa
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            pa_name = df.loc[index]["PA NAME"]
            fabric = df.loc[index]["FABRIC"]
            pod = df.loc[index]["POD"]
            pa_type = df.loc[index]["PA TYPE"]
            interface_profile = df.loc[index]["INTERFACE PROFILE"]
            node_id = df.loc[index]["NODE ID"]
            node_port_list = df.loc[index]["NODE PORT LIST"]
            node_id_1 = df.loc[index]["NODE ID 1"]
            node_id_2 = df.loc[index]["NODE ID 2"]
            node_id_1_port_list = df.loc[index]["NODE ID 1 PORT LIST"]
            node_id_2_port_list = df.loc[index]["NODE ID 2 PORT LIST"]
            tenant_pa_type = df.loc[index]["TENANT PA TYPE"]
            external_tenant_name = df.loc[index]["EXTERNAL TENANT NAME"]
            if tenant_pa_type == "internal":
                pa_info_dict = {"Tenant Name": tenant_name, "Pa Name": pa_name, "Fabric": fabric, "Pod": pod,
                                "Pa Type": pa_type, "Interface Profile": interface_profile, "Node Id": node_id,
                                "Node Port List": node_port_list, "Node Id 1": node_id_1, "Node Id 2": node_id_2,
                                "Node Id 1 Port List": node_id_1_port_list, "Node Id 2 Port List": node_id_2_port_list}
                if pa_info_dict not in self.pa_info_dict_list:
                    self.pa_info_dict_list.append(pa_info_dict)
            elif tenant_pa_type == "external":
                pa_info_dict = {"Tenant Name": external_tenant_name, "Pa Name": pa_name, "Fabric": fabric, "Pod": pod,
                                "Pa Type": pa_type, "Interface Profile": interface_profile, "Node Id": node_id,
                                "Node Port List": node_port_list, "Node Id 1": node_id_1, "Node Id 2": node_id_2,
                                "Node Id 1 Port List": node_id_1_port_list, "Node Id 2 Port List": node_id_2_port_list}
                if pa_info_dict not in self.pa_info_dict_list:
                    self.pa_info_dict_list.append(pa_info_dict)
            else:
                raise Exception("!!!Invalid Tenant PA Type!!!")
        self.pa_info_dict_list = helpers.pa_info_dict_list_helper(self.pa_info_dict_list)

        return self.pa_info_dict_list

########################################################################################################################
############################################PORT PA Group Info Dictionary List##########################################

    def __create_pa_portgroups_info_dict_list_with_df(self, df=pd.DataFrame()):
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            pa_name = df.loc[index]["PA NAME"]
            fabric = df.loc[index]["FABRIC"]
            pod = df.loc[index]["POD"]
            pa_type = df.loc[index]["PA TYPE"]
            interface_profile = df.loc[index]["INTERFACE PROFILE"]
            node_id = df.loc[index]["NODE ID"]
            node_port_list = df.loc[index]["NODE PORT LIST"]
            node_id_1 = df.loc[index]["NODE ID 1"]
            node_id_2 = df.loc[index]["NODE ID 2"]
            node_id_1_port_list = df.loc[index]["NODE ID 1 PORT LIST"]
            node_id_2_port_list = df.loc[index]["NODE ID 2 PORT LIST"]
            tenant_pa_type = df.loc[index]["TENANT PA TYPE"]
            external_tenant_name = df.loc[index]["EXTERNAL TENANT NAME"]
            if tenant_pa_type == "internal":
                pa_info_dict = {"Tenant Name": tenant_name, "Pa Name": pa_name, "Fabric": fabric, "Pod": pod,
                                "Pa Type": pa_type, "Interface Profile": interface_profile, "Node Id": node_id,
                                "Node Port List": node_port_list, "Node Id 1": node_id_1, "Node Id 2": node_id_2,
                                "Node Id 1 Port List": node_id_1_port_list, "Node Id 2 Port List": node_id_2_port_list}
                if pa_info_dict not in self.pa_info_dict_list:
                    self.pa_info_dict_list_with_df.append(pa_info_dict)
            elif tenant_pa_type == "external":
                pa_info_dict = {"Tenant Name": external_tenant_name, "Pa Name": pa_name, "Fabric": fabric, "Pod": pod,
                                "Pa Type": pa_type, "Interface Profile": interface_profile, "Node Id": node_id,
                                "Node Port List": node_port_list, "Node Id 1": node_id_1, "Node Id 2": node_id_2,
                                "Node Id 1 Port List": node_id_1_port_list, "Node Id 2 Port List": node_id_2_port_list}
                if pa_info_dict not in self.pa_info_dict_list:
                    self.pa_info_dict_list_with_df.append(pa_info_dict)
            else:
                raise Exception("!!!Invalid Tenant PA Type!!!")
        self.pa_info_dict_list_with_df = helpers.pa_info_dict_list_helper(self.pa_info_dict_list_with_df)

########################################################################################################################
############################################Tenant PA Info Dictionary List##############################################

    def create_tenant_pa_info_dict_list(self):
        df = self.df_pa
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            service_name = df.loc[index]["SERVICE NAME"]
            bd_name = df.loc[index]["BRIDGE DOMAIN NAME"]
            epg_name = df.loc[index]["EPG NAME"]
            encap_id = df.loc[index]["ENCAP ID"]
            tenant_pa_type = df.loc[index]["TENANT PA TYPE"]
            pa_name = df.loc[index]["PA NAME"]
            mode = df.loc[index]["MODE"]
            external_tenant_name = df.loc[index]["EXTERNAL TENANT NAME"]
            tenant_pa_info_dict = {"Tenant Name": tenant_name, "Service Name": service_name, "Bd Name": bd_name,
                                   "Epg Name": epg_name, "Encap Id": encap_id, "Tenant Pa Type": tenant_pa_type,
                                   "External Tenant Name": external_tenant_name, "Pa Name": pa_name, "Mode": mode}
            if tenant_pa_info_dict not in self.tenant_pa_info_dict_list:
                self.tenant_pa_info_dict_list.append(tenant_pa_info_dict)
        self.tenant_pa_info_dict_list = helpers.tenant_pa_info_dict_list_helper(self.tenant_pa_info_dict_list)

        return self.tenant_pa_info_dict_list

########################################################################################################################
############################################TENANT PA Group Info Dictionary List########################################

    def __create_tenant_pa_portgroups_info_dict_list_with_df(self, df=pd.DataFrame()):
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            service_name = df.loc[index]["SERVICE NAME"]
            bd_name = df.loc[index]["BRIDGE DOMAIN NAME"]
            epg_name = df.loc[index]["EPG NAME"]
            encap_id = df.loc[index]["ENCAP ID"]
            tenant_pa_type = df.loc[index]["TENANT PA TYPE"]
            pa_name = df.loc[index]["PA NAME"]
            mode = df.loc[index]["MODE"]
            external_tenant_name = df.loc[index]["EXTERNAL TENANT NAME"]
            tenant_pa_info_dict = {"Tenant Name": tenant_name, "Service Name": service_name, "Bd Name": bd_name,
                                   "Epg Name": epg_name, "Encap Id": encap_id, "Tenant Pa Type": tenant_pa_type,
                                   "External Tenant Name": external_tenant_name, "Pa Name": pa_name, "Mode": mode}
            if tenant_pa_info_dict not in self.tenant_pa_info_dict_list:
                self.tenant_pa_info_dict_list_with_df.append(tenant_pa_info_dict)
        self.tenant_pa_info_dict_list_with_df = helpers.tenant_pa_info_dict_list_helper(self.tenant_pa_info_dict_list_with_df)

########################################################################################################################
############################################Prefix-List Info Dictionary List############################################

    def create_prefix_list_info_dict_list(self):
        df = self.df_prefix_list
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            prefix_list_name = df.loc[index]["PREFIX LIST NAME"]
            prefix = df.loc[index]["PREFIX"]
            eq = df.loc[index]["EQ"]
            ge = df.loc[index]["GE"]
            le = df.loc[index]["LE"]
            prefix_list_info_dict = {"Tenant Name": tenant_name, "Prefix List Name": prefix_list_name,
                                     "IPv4-Prefix": prefix, "Eq": eq, "Ge": ge, "Le": le}
            if prefix_list_info_dict not in self.prefix_list_info_dict_list:
                self.prefix_list_info_dict_list.append(prefix_list_info_dict)
        self.prefix_list_info_dict_list = helpers.prefix_list_info_dict_list_helper(self.prefix_list_info_dict_list)

        return self.prefix_list_info_dict_list

########################################################################################################################
############################################L3 Direct Info Dictionary List##############################################

    def create_l3direct_info_dict_list(self):
        df = self.df_l3direct
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            service_name = df.loc[index]["SERVICE NAME"]
            bd_name = df.loc[index]["BRIDGE DOMAIN NAME"]
            epg_name = df.loc[index]["EPG NAME"]
            encap_id = df.loc[index]["ENCAP ID"]
            l3direct_name = df.loc[index]["L3 DIRECT NAME"]
            ipv4_network = df.loc[index]["IPv4 NETWORK"]
            secondary_ipv4_network_list = df.loc[index]["SECONDARY IPv4 NETWORK LIST"]
            shutdown_status = df.loc[index]["SHUTDOWN"]
            service_policy_status = df.loc[index]["SERVICE POLICY"]
            input_pmap = df.loc[index]["INPUT POLICY MAP"]
            output_pmap = df.loc[index]["OUTPUT POLICY MAP"]
            mtu = df.loc[index]["MTU"]
            l3direct_info_dict = {"Tenant Name": tenant_name, "Service Name": service_name, "Bd Name": bd_name,
                                  "Epg Name": epg_name,
                                  "Encap Id": encap_id, "L3 Direct Name": l3direct_name, "IPv4 Network": ipv4_network,
                                  "Secondary IPv4 Network List": secondary_ipv4_network_list,
                                  "Shutdown": shutdown_status,
                                  "Service Policy": service_policy_status, "Input Policy Map": input_pmap,
                                  "Output Policy Map": output_pmap, "Mtu": mtu}
            if l3direct_info_dict not in self.l3direct_info_dict_list:
                self.l3direct_info_dict_list.append(l3direct_info_dict)
        self.l3direct_info_dict_list = helpers.l3direct_info_dict_list_helper(self.l3direct_info_dict_list)

        return self.l3direct_info_dict_list

########################################################################################################################
############################################Delete L3 Direct Shutdown Info Dictionary List##############################

    def create_delete_l3direct_shutdown_info_dict_list(self, group_name=None):
        df = self.df_delete_l3direct_shutdown
        for index in df.index.values:
            grup = df.loc[index]["GRUP"]
            if group_name == grup:
                tenant_name = df.loc[index]["TENANT NAME"]
                service_name = df.loc[index]["SERVICE NAME"]
                bd_name = df.loc[index]["BRIDGE DOMAIN NAME"]
                epg_name = df.loc[index]["EPG NAME"]
                encap_id = df.loc[index]["ENCAP ID"]
                delete_l3direct_shutdown_info_dict = {"Tenant Name": tenant_name, "Service Name": service_name, "Bd Name": bd_name,
                                                      "Epg Name": epg_name, "Encap Id": encap_id}
                if delete_l3direct_shutdown_info_dict not in self.delete_l3direct_shutdown_info_dict_list:
                    self.delete_l3direct_shutdown_info_dict_list.append(delete_l3direct_shutdown_info_dict)
        self.delete_l3direct_shutdown_info_dict_list = helpers.delete_l3direct_shutdown_info_dict_list_helper(self.delete_l3direct_shutdown_info_dict_list)

        return self.delete_l3direct_shutdown_info_dict_list
########################################################################################################################
############################################L3 Direct Static Info Dictionary List#######################################

    def create_l3direct_static_info_dict_list(self):
        df = self.df_l3direct_static
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            service_name = df.loc[index]["SERVICE NAME"]
            bd_name = df.loc[index]["BRIDGE DOMAIN NAME"]
            epg_name = df.loc[index]["EPG NAME"]
            encap_id = df.loc[index]["ENCAP ID"]
            ipv4_prefix = df.loc[index]["IPv4 PREFIX"]
            nexthop = df.loc[index]["NEXTHOP"]
            administrative_distance = df.loc[index]["ADMINISTRATIVE DISTANCE"]
            tag = df.loc[index]["TAG"]
            l3direct_static_info_dict = {"Tenant Name": tenant_name, "Service Name": service_name, "Bd Name": bd_name,
                                         "Epg Name": epg_name, "Encap Id": encap_id, "IPv4 Prefix": ipv4_prefix,
                                         "Nexthop": nexthop, "Administrative Distance": administrative_distance, "Tag": tag}
            if l3direct_static_info_dict not in self.l3direct_static_info_dict_list:
                self.l3direct_static_info_dict_list.append(l3direct_static_info_dict)
        self.l3direct_static_info_dict_list = helpers.l3direct_static_info_dict_list_helper(self.l3direct_static_info_dict_list)

        return self.l3direct_static_info_dict_list
########################################################################################################################
############################################L3 Direct OSPF Info Dictionary List#########################################

    def create_l3direct_ospf_info_dict_list(self):
        df = self.df_l3direct_ospf
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            service_name = df.loc[index]["SERVICE NAME"]
            bd_name = df.loc[index]["BRIDGE DOMAIN NAME"]
            epg_name = df.loc[index]["EPG NAME"]
            encap_id = df.loc[index]["ENCAP ID"]
            process_id = df.loc[index]["PROCESS ID"]
            default_originate_status = df.loc[index]["DEFAULT ORIGINATE"]
            area = df.loc[index]["AREA"]
            l3direct_ospf_info_dict = {"Tenant Name": tenant_name, "Service Name": service_name, "Bd Name": bd_name,
                                       "Epg Name": epg_name, "Encap Id": encap_id, "Process Id": process_id,
                                       "Default Originate": default_originate_status, "Area": area}
            if l3direct_ospf_info_dict not in self.l3direct_ospf_info_dict_list:
                self.l3direct_ospf_info_dict_list.append(l3direct_ospf_info_dict)
        self.l3direct_ospf_info_dict_list = helpers.l3direct_ospf_info_dict_list_helper(self.l3direct_ospf_info_dict_list)

        return self.l3direct_ospf_info_dict_list

########################################################################################################################
############################################L3 Direct BGP Info Dictionary List##########################################

    def create_l3direct_bgp_info_dict_list(self):
        df = self.df_l3direct_bgp
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            service_name = df.loc[index]["SERVICE NAME"]
            bd_name = df.loc[index]["BRIDGE DOMAIN NAME"]
            epg_name = df.loc[index]["EPG NAME"]
            encap_id = df.loc[index]["ENCAP ID"]
            enable_max_path_status = df.loc[index]["ENABLE MAX PATHS"]
            bfd_status = df.loc[index]["BFD STATUS"]
            bfd_min_interval = df.loc[index]["BFD MIN INTERVAL"]
            bfd_disable_fast_detect_status = df.loc[index]["BFD DISABLE FAST DETECT"]
            bfd_multiplier = df.loc[index]["BFD MULTIPLIER"]
            bgp_peer = df.loc[index]["BGP PEER"]
            remote_as = df.loc[index]["REMOTE AS"]
            nexthopself_status = df.loc[index]["NEXTHOPSELF"]
            remove_private_as_status = df.loc[index]["REMOVE PRIVATE AS"]
            max_prefix = df.loc[index]["MAX PREFIX"]
            action = df.loc[index]["ACTION"]
            default_originate_status = df.loc[index]["DEFAULT ORIGINATE"]
            password = df.loc[index]["PASSWORD"]
            soft_reconfiguration_status = df.loc[index]["SOFT RECONFIGURATION"]
            shutdown_status = df.loc[index]["SHUTDOWN"]
            update_source = df.loc[index]["UPDATE SOURCE"]
            loopback_ip = df.loc[index]["LOOPBACK IP"]
            local_as_status = df.loc[index]["LOCAL AS STATUS"]
            local_as = df.loc[index]["LOCAL AS"]
            local_as_no_prepend_status = df.loc[index]["LOCAL AS NO PREPEND"]
            local_as_replace_as_status = df.loc[index]["LOCAL AS REPLACE AS"]
            customer_timers_status = df.loc[index]["CUSTOM TIMERS STATUS"]
            keepalive = df.loc[index]["KEEPALIVE"]
            hold_time = df.loc[index]["HOLD TIME"]
            in_rpl_name = df.loc[index]["IN RPL NAME"]
            in_rpl_custom_policy_name = df.loc[index]["IN RPL CUSTOM POLICY NAME"]
            in_rpl_prefix_list = df.loc[index]["IN RPL PREFIX LIST"]
            in_rpl_blackhole_prefix_list = df.loc[index]["IN RPL BLACKHOLE PREFIX LIST"]
            in_rpl_local_preference = df.loc[index]["IN RPL LOCAL PREFERENCE"]
            in_rpl_community_name = df.loc[index]["IN RPL COMMUNITY NAME"]
            in_rpl_community_list = df.loc[index]["IN RPL COMMUNITY LIST"]
            in_rpl_as_path = df.loc[index]["IN RPL AS PATH"]
            in_rpl_multiplier = df.loc[index]["IN RPL MULTIPLIER"]
            out_rpl_name = df.loc[index]["OUT RPL NAME"]
            out_rpl_custom_policy_name = df.loc[index]["OUT RPL CUSTOM POLICY NAME"]
            out_rpl_prefix_list = df.loc[index]["OUT RPL PREFIX LIST"]
            out_rpl_as_path = df.loc[index]["OUT RPL AS PATH"]
            out_rpl_multiplier = df.loc[index]["OUT RPL MULTIPLIER"]
            l3direct_bgp_info_dict = {"Tenant Name": tenant_name, "Service Name": service_name, "Bd Name": bd_name,
                                      "Epg Name": epg_name,
                                      "Encap Id": encap_id, "Enable Max Paths": enable_max_path_status,
                                      "Bfd Status": bfd_status, "Bfd Min Interval": bfd_min_interval,
                                      "Bfd Disable Fast Detect": bfd_disable_fast_detect_status,
                                      "Bfd Multiplier": bfd_multiplier, "Bgp Peer": bgp_peer,
                                      "Remote As": remote_as, "Nexthopself": nexthopself_status,
                                      "Remove Private As": remove_private_as_status, "Max Prefix": max_prefix,
                                      "Action": action, "Default Originate": default_originate_status,
                                      "Password": password, "Soft Reconfiguration": soft_reconfiguration_status,
                                      "Shutdown": shutdown_status,
                                      "Update Source": update_source, "Loopback Ip": loopback_ip,
                                      "Local As Status": local_as_status, "Local As": local_as,
                                      "Local As No Prepend": local_as_no_prepend_status,
                                      "Local As Replace As": local_as_replace_as_status,
                                      "Custom Timers": customer_timers_status, "Keepalive": keepalive,
                                      "Hold Time": hold_time, "In Rpl Name": in_rpl_name,
                                      "In Rpl Custom Policy Name": in_rpl_custom_policy_name,
                                      "In Rpl Prefix List": in_rpl_prefix_list,
                                      "In Rpl Blackhole Prefix List": in_rpl_blackhole_prefix_list,
                                      "In Rpl Local Preference": in_rpl_local_preference,
                                      "In Rpl Community Name": in_rpl_community_name,
                                      "In Rpl Community List": in_rpl_community_list,
                                      "In Rpl As Path": in_rpl_as_path, "In Rpl Multiplier": in_rpl_multiplier,
                                      "Out Rpl Name": out_rpl_name,
                                      "Out Rpl Custom Policy Name": out_rpl_custom_policy_name,
                                      "Out Rpl Prefix List": out_rpl_prefix_list, "Out Rpl As Path": out_rpl_as_path,
                                      "Out Rpl Multiplier": out_rpl_multiplier}
            if l3direct_bgp_info_dict not in self.l3direct_bgp_info_dict_list:
                self.l3direct_bgp_info_dict_list.append(l3direct_bgp_info_dict)
            self.l3direct_bgp_info_dict_list = helpers.l3direct_bgp_info_dict_list_helper(self.l3direct_bgp_info_dict_list)

        return self.l3direct_bgp_info_dict_list
########################################################################################################################
############################################L3 Direct Aggreagte Info Dictionary List####################################

    def create_l3direct_aggregate_info_dict_list(self):
        df = self.df_l3direct_aggregate
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            service_name = df.loc[index]["SERVICE NAME"]
            bd_name = df.loc[index]["BRIDGE DOMAIN NAME"]
            epg_name = df.loc[index]["EPG NAME"]
            encap_id = df.loc[index]["ENCAP ID"]
            ipv4_prefix = df.loc[index]["IPv4 PREFIX"]
            summary_only_status = df.loc[index]["SUMMARY ONLY"]
            l3direct_aggregate_info_dict = {"Tenant Name": tenant_name, "Service Name": service_name,
                                            "Bd Name": bd_name,
                                            "Epg Name": epg_name, "Encap Id": encap_id, "IPv4 Prefix": ipv4_prefix,
                                            "Summary Only": summary_only_status}
            if l3direct_aggregate_info_dict not in self.l3direct_aggregate_info_dict_list:
                self.l3direct_aggregate_info_dict_list.append(l3direct_aggregate_info_dict)
            self.l3direct_aggregate_info_dict_list = helpers.l3direct_aggregate_info_dict_list_helper(self.l3direct_aggregate_info_dict_list)

        return self.l3direct_aggregate_info_dict_list

########################################################################################################################
############################################L2 EXTERNAL Info Dictionary List############################################

    def create_l2ext_info_dict_list(self):
        df = self.df_l2ext
        for index in df.index.values:
            tenant_name = df.loc[index]["TENANT NAME"]
            service_name = df.loc[index]["SERVICE NAME"]
            bd_name = df.loc[index]["BRIDGE DOMAIN NAME"]
            epg_name = df.loc[index]["EPG NAME"]
            encap_id = df.loc[index]["ENCAP ID"]
            dci_interface = df.loc[index]['DCI INTERFACE']
            l2ext_type = df.loc[index]['TYPE']
            evi = df.loc[index]['EVI']
            circuit_id = df.loc[index]['CIRCUIT ID']
            neighbor_ip = df.loc[index]['NEIGHBOR IP']
            pw_class = df.loc[index]['PW CLASS']
            mtu = df.loc[index]['MTU']
            l2ext_info_dict = {"Tenant Name": tenant_name, "Service Name": service_name, "Bd Name": bd_name,
                               "Epg Name": epg_name, "Encap Id": encap_id, "Dci Interface": dci_interface,
                               "Type": l2ext_type, "Evi": evi, "Circuit Id": circuit_id, "Neighbor Ip": neighbor_ip,
                               "Pw Class": pw_class, "Mtu": mtu}
            if l2ext_info_dict not in self.l2ext_info_dict_list:
                self.l2ext_info_dict_list.append(l2ext_info_dict)
        self.l2ext_info_dict_list = helpers.l2ext_info_dict_list_helper(self.l2ext_info_dict_list)

        return self.l2ext_info_dict_list

########################################################################################################################
############################################Transit Leaf Tenant Pa Info Dictionary List#################################

    def create_transit_leaf_encap_info_dict_list(self, query_l2ext_encap_id_info_dict_list=[]):
        encap_info_dict_list = self.create_encap_info_dict_list()
        l2ext_info_dict_list = self.create_l2ext_info_dict_list()
        for encap_info_dict in encap_info_dict_list:
            flag = False
            encap_info_dict_tenant_name = encap_info_dict["Tenant Name"]
            encap_info_dict_service_name = encap_info_dict["Service Name"]
            encap_info_dict_bd_name = encap_info_dict["Bd Name"]
            for l2ext_info_dict in l2ext_info_dict_list:
                l2ext_info_dict_tenant_name = l2ext_info_dict["Tenant Name"]
                l2ext_info_dict_service_name = l2ext_info_dict["Service Name"]
                l2ext_info_dict_bd_name = l2ext_info_dict["Bd Name"]
                if encap_info_dict_tenant_name == l2ext_info_dict_tenant_name and encap_info_dict_service_name == l2ext_info_dict_service_name and encap_info_dict_bd_name == l2ext_info_dict_bd_name:
                    self.logger.error(f"Tenant Name:{encap_info_dict_tenant_name} Service Name:{encap_info_dict_service_name} Bd Name:{encap_info_dict_bd_name} | L2EXT EVI Tenant Name:{l2ext_info_dict_tenant_name} Service Name:{l2ext_info_dict_service_name} Bd Name:{l2ext_info_dict_bd_name}")
                    flag = True
            for query_l2ext_encap_id_info_dict in query_l2ext_encap_id_info_dict_list:
                query_l2ext_tenant_name = query_l2ext_encap_id_info_dict["Tenant Name"]
                query_l2ext_service_name = query_l2ext_encap_id_info_dict["Service Name"]
                query_l2ext_bd_name = query_l2ext_encap_id_info_dict["Bd Name"]
                if encap_info_dict_tenant_name == query_l2ext_tenant_name and encap_info_dict_service_name == query_l2ext_service_name and encap_info_dict_bd_name == query_l2ext_bd_name:
                    self.logger.error(f"Tenant Name:{encap_info_dict_tenant_name} Service Name:{encap_info_dict_service_name} Bd Name:{encap_info_dict_bd_name} | Query EVI Tenant Name:{query_l2ext_tenant_name} Service Name:{query_l2ext_service_name} Bd Name:{query_l2ext_bd_name}")
                    flag = True
            if not flag:
                self.transit_leaf_encap_info_dict_list.append(encap_info_dict)
        d = {}; i = 0
        for transit_leaf_encap_info_dict in self.transit_leaf_encap_info_dict_list:
            d.update({i: transit_leaf_encap_info_dict})
            i += 1
        df = pd.DataFrame.from_dict(d, orient="index")
        with pd.ExcelWriter("TRANSIT_LEAF_SERVICES.xlsx") as writer:
            df.to_excel(writer)

        return self.transit_leaf_encap_info_dict_list

########################################################################################################################
############################################Port Pa Group Info Dictionary List##########################################

    def create_pa_portgroups_info_dict_list(self, tenant_name=None, dc_id=None):
        df = self.df_pa.loc[self.df_pa["TENANT NAME"] == tenant_name]
        node_id_list = list(set(df["NODE ID"].tolist()))
        node_id_list = list(map(int, node_id_list))
        for node_id in node_id_list:
            node_port_list = []
            pa_name = f"{tenant_name}_dc{dc_id}_lf{node_id}_portgroup"
            for index in df.index.values:
                if node_id == df.loc[index]["NODE ID"]:
                    node_port_list.append(df.loc[index]["NODE PORT LIST"].strip("Ethernet"))
            df.loc[df["NODE ID"] == node_id, "NODE PORT LIST"] = ",".join(node_port_list)
            df.loc[df["NODE ID"] == node_id, "PA NAME"] = pa_name
        cols = [c for c in df.columns if c.lower()[:3] != "vts"]
        df = df[cols]
        df.drop_duplicates(inplace=True)
        self.__create_pa_portgroups_info_dict_list_with_df(df)

        return self.pa_info_dict_list_with_df

########################################################################################################################
############################################Tenant Pa Group Info Dictionary List########################################

    def create_tenant_pa_portgroups_info_dict_list(self, tenant_name=None, dc_id=None):
        df = self.df_pa.loc[self.df_pa["TENANT NAME"] == tenant_name]
        node_id_list = list(set(df["NODE ID"].tolist()))
        node_id_list = list(map(int, node_id_list))
        for node_id in node_id_list:
            node_port_list = []
            pa_name = f"{tenant_name}_dc{dc_id}_lf{node_id}_portgroup"
            for index in df.index.values:
                if node_id == df.loc[index]["NODE ID"]:
                    node_port_list.append(df.loc[index]["NODE PORT LIST"].strip("Ethernet"))
            df.loc[df["NODE ID"] == node_id, "NODE PORT LIST"] = ",".join(node_port_list)
            df.loc[df["NODE ID"] == node_id, "PA NAME"] = pa_name
        cols = [c for c in df.columns if c.lower()[:3] != "vts"]
        df = df[cols]
        df.drop_duplicates(inplace=True)
        self.__create_tenant_pa_portgroups_info_dict_list_with_df(df)

        return self.tenant_pa_info_dict_list_with_df

########################################################################################################################
############################################LISTING SAME KEY VALUES#####################################################

    @staticmethod
    def set_key(dictionary, key, value):
        if dictionary.get(key):
            if isinstance(dictionary[key], list):
                if value not in dictionary[key]:
                    dictionary[key].append(value)
            else:
                if dictionary[key] != value:
                    dictionary[key] = [dictionary[key], value]
        else:
            dictionary[key] = value

########################################################################################################################
############################################Port Pa Group Info Dictionary List##########################################

    # def create_pa_portgroups_info_dict_list1(self, tenant_name=None, dc_id=None):
        # data_list = self.df_pa.values.tolist()
        # for data in data_list:
        #     if data[8] == "SA":
        #         self.set_key(d,int(data[13]),data[14].strip("Ethernet"))
        # return d
