import pandas as pd
import logging

############################################HELPER MODULE FOR NSO#######################################################
########################################################################################################################
############################################TENANT HELPER FUNCTION######################################################


def query_tenant_helper(response_dict={}):
    tenant_list = []
    for d_list in response_dict["result"]["results"]:
        tenant_name = d_list[0]["value"]
        tenant_list.append({"Tenant Name": tenant_name})

    return tenant_list

########################################################################################################################
############################################TENANT PRECHECK HELPER FUNCTION#############################################


def precheck_tenant_helper(tenant_info_dict_list=[], query_tenant_info_dict_list=[]):
    tenant_problems = []
    for tenant_info_dict in tenant_info_dict_list:
        tenant_name = tenant_info_dict["Tenant Name"]
        for query_tenant_info_dict in query_tenant_info_dict_list:
            query_tenant_name = query_tenant_info_dict["Tenant Name"]
            if tenant_name != query_tenant_name:
                if tenant_name.lower() == query_tenant_name.lower():
                    tenant_problems.append({"MOP TENANT NAME": tenant_name, "QUERY TENANT NAME": query_tenant_name, "PROBLEM": "tenant name needs to be unique without case sensitivity"})

    return tenant_problems

########################################################################################################################
############################################TENANT PRECHECK DF HELPER FUNCTION##########################################


def precheck_tenant_df(tenant_list=[]):
    d = {}
    i = 0
    for tenant_dict in tenant_list:
        d.update({i: tenant_dict})
        i += 1
    if not d:
        d = {0: {"MOP TENANT NAME": "", "QUERY TENANT NAME": "", "PROBLEM": ""}}
    df = pd.DataFrame.from_dict(d, orient="index")

    return df

########################################################################################################################
############################################SERVICE HELPER FUNCTION#####################################################


def query_service_helper(response_dict={}):
    service_list = []
    for d_list in response_dict["result"]["results"]:
        tenant_name = d_list[0]["value"]
        service_name = d_list[1]["value"]
        fabric = d_list[2]["value"]
        service_list.append({"Tenant Name": tenant_name, "Service Name": service_name, "Fabric": fabric})

    return service_list

########################################################################################################################
############################################SERVICE PRECHECK HELPER FUNCTION############################################


def precheck_service_helper(service_info_dict_list=[], query_service_info_dict_list=[]):
    service_problems = []
    for service_info_dict in service_info_dict_list:
        tenant_name = service_info_dict["Tenant Name"]
        service_name = service_info_dict["Service Name"]
        fabric = service_info_dict["Fabric"]
        for query_service_info_dict in query_service_info_dict_list:
            query_tenant_name = query_service_info_dict["Tenant Name"]
            query_service_name = query_service_info_dict["Service Name"]
            query_fabric = query_service_info_dict["Fabric"]
            if tenant_name == query_tenant_name and service_name == query_service_name:
                if fabric != query_fabric:
                    service_problems.append({"MOP TENANT NAME": tenant_name, "MOP SERVICE NAME": service_name, "MOP FABRIC": fabric, "QUERY FABRIC": query_fabric, "PROBLEM": "Same Service Dclan with Different Fabric"})

    return service_problems

########################################################################################################################
############################################SERVICE PRECHECK DF HELPER FUNCTION#########################################


def precheck_service_df(service_list=[]):
    d = {}
    i = 0
    for service_dict in service_list:
        d.update({i: service_dict})
        i += 1
    if not d:
        d = {0: {"MOP TENANT NAME": "", "MOP SERVICE NAME": "", "MOP FABRIC": "", "QUERY FABRIC": "", "PROBLEM": ""}}
    df = pd.DataFrame.from_dict(d, orient="index")

    return df

############################################TRANSIT LEAF TENANT PA HELPER FUNCTION######################################


def query_transit_leaf_tenant_pa_helper(response_dict={}):
    external_tenant_pa_list = []
    for d_list in response_dict["result"]["results"]:
        tenant_name = d_list[0]["value"]
        service_name = d_list[1]["value"]
        bd_name = d_list[2]["value"]
        epg_name = d_list[3]["value"]
        encap_id = d_list[4]["value"]
        tenant_pa = d_list[5]["value"]
        external_tenant_pa_list.append({"Tenant Name": tenant_name, "Service Name": service_name, "Bd Name": bd_name, "Epg Name": epg_name, "Encap Id": encap_id, "Tenant Pa Name": tenant_pa})

    return external_tenant_pa_list

########################################################################################################################
############################################PORT PA HELPER FUNCTION#####################################################


def query_port_pa_helper(response_dict={}):
    port_pa_list = []
    for d_list in response_dict["result"]["results"]:
        pa_name = d_list[0]["value"]
        fabric = d_list[1]["value"]
        pa_type = d_list[2]["value"]
        node_id = d_list[3]["value"]
        node_port = d_list[4]["value"]
        node_id_1 = d_list[5]["value"]
        node_id_1_port = d_list[6]["value"]
        node_id_2 = d_list[7]["value"]
        node_id_2_port = d_list[8]["value"]
        if pa_type == "VPC":
            node_id = None
            node_port = None
        else:
            node_id_1 = None
            node_id_1_port = None
            node_id_2 = None
            node_id_2_port = None
        port_pa_list.append({"Pa Name": pa_name, "Fabric": fabric, "Pa Type": pa_type, "Node Id": node_id, "Node Port": node_port, "Node Id 1": node_id_1, "Node Id 1 Port": node_id_1_port, "Node Id 2": node_id_2, "Node Id 2 Port": node_id_2_port})

    return port_pa_list

########################################################################################################################
############################################PORT PA SA PRECHECK HELPER FUNCTION#########################################


def precheck_port_pa_sa_helper(fabric=None, tenant_name=None, pa_name=None, interface_profile=None, node_id=None, node_port_list=[], query_port_pa_info_dict_list=[]):
    pa_problems = []
    for query_port_pa_info_dict in query_port_pa_info_dict_list:
        if fabric == query_port_pa_info_dict["Fabric"]:
            if node_id == query_port_pa_info_dict["Node Id"]:
                query_node_port_list = query_port_pa_info_dict["Node Port"].split(",")
                intersection_node_port_list = list(set(node_port_list) & set(query_node_port_list))
                if len(intersection_node_port_list) != 0:
                    pa_problems.append({"MOP PA NAME": pa_name, "QUERY PA NAME": query_port_pa_info_dict["Pa Name"], "PROBLEM": "PORT ALREADY USED"})
            if node_id == query_port_pa_info_dict["Node Id 1"]:
                query_node_1_port_list = query_port_pa_info_dict["Node Id 1 Port"].split(",")
                intersection_node_port_list = list(set(node_port_list) & set(query_node_1_port_list))
                if len(intersection_node_port_list) != 0:
                    pa_problems.append({"MOP PA NAME": pa_name, "QUERY PA NAME": query_port_pa_info_dict["Pa Name"], "PROBLEM": "PORT ALREADY USED"})
            if node_id == query_port_pa_info_dict["Node Id 2"]:
                query_node_2_port_list = query_port_pa_info_dict["Node Id 2 Port"].split(",")
                intersection_node_port_list = list(set(node_port_list) & set(query_node_2_port_list))
                if len(intersection_node_port_list) != 0:
                    pa_problems.append({"MOP PA NAME": pa_name, "QUERY PA NAME": query_port_pa_info_dict["Pa Name"], "PROBLEM": "PORT ALREADY USED"})
    int_pol_group_name = f"LF_SA_{tenant_name}_{interface_profile}"
    # INTERFACE SELECTOR ADDS 4 or 5 characters:LF_VPC_GBZ3B-Backup_407-408_G3B_BSCSPRIMARY_lf407-408_VPC2_1_47
    if len(int_pol_group_name) > 59:
        pa_problems.append({"MOP PA NAME": pa_name, "QUERY PA NAME": "", "INTERFACE POLICY GROUP": int_pol_group_name, "PROBLEM": "INTERFACE POLICY GROUP OR INTERFACE SELECTOR NAMES ARE MORE THAN 64 CHARACTER"})

    return pa_problems

########################################################################################################################
############################################PORT PA PC PRECHECK HELPER FUNCTION#########################################


def precheck_port_pa_pc_helper(fabric=None, tenant_name=None, pa_name=None, node_id=None, node_port_list=[], query_port_pa_info_dict_list=[]):
    pa_problems = []
    for query_port_pa_info_dict in query_port_pa_info_dict_list:
        if fabric == query_port_pa_info_dict["Fabric"]:
            if node_id == query_port_pa_info_dict["Node Id"]:
                query_node_port_list = query_port_pa_info_dict["Node Port"].split(",")
                intersection_node_port_list = list(set(node_port_list) & set(query_node_port_list))
                if len(intersection_node_port_list) != 0:
                    pa_problems.append({"MOP PA NAME": pa_name, "QUERY PA NAME": query_port_pa_info_dict["Pa Name"], "PROBLEM": "PORT ALREADY USED"})
            if node_id == query_port_pa_info_dict["Node Id 1"]:
                query_node_1_port_list = query_port_pa_info_dict["Node Id 1 Port"].split(",")
                intersection_node_port_list = list(set(node_port_list) & set(query_node_1_port_list))
                if len(intersection_node_port_list) != 0:
                    pa_problems.append({"MOP PA NAME": pa_name, "QUERY PA NAME": query_port_pa_info_dict["Pa Name"], "PROBLEM": "PORT ALREADY USED"})
            if node_id == query_port_pa_info_dict["Node Id 2"]:
                query_node_2_port_list = query_port_pa_info_dict["Node Id 2 Port"].split(",")
                intersection_node_port_list = list(set(node_port_list) & set(query_node_2_port_list))
                if len(intersection_node_port_list) != 0:
                    pa_problems.append({"MOP PA NAME": pa_name, "QUERY PA NAME": query_port_pa_info_dict["Pa Name"], "PROBLEM": "PORT ALREADY USED"})
    int_pol_group_name = f"LF_PC_{tenant_name}_{node_id}_{pa_name}"
    # INTERFACE SELECTOR ADDS 4 or 5 characters:LF_VPC_GBZ3B-Backup_407-408_G3B_BSCSPRIMARY_lf407-408_VPC2_1_47
    if len(int_pol_group_name) > 59:
        pa_problems.append({"MOP PA NAME": pa_name, "QUERY PA NAME": "", "INTERFACE POLICY GROUP": int_pol_group_name, "PROBLEM": "INTERFACE POLICY GROUP OR INTERFACE SELECTOR NAMES ARE MORE THAN 64 CHARACTER"})

    return pa_problems

########################################################################################################################
############################################PORT PA VPC PRECHECK HELPER FUNCTION########################################


def precheck_port_pa_vpc_helper(fabric=None, tenant_name=None, pa_name=None, node_id_1=None, node_id_1_port_list=[], node_id_2=None, node_id_2_port_list=[], query_port_pa_info_dict_list=[]):
    pa_problems = []
    for query_port_pa_info_dict in query_port_pa_info_dict_list:
        if fabric == query_port_pa_info_dict["Fabric"]:
            if node_id_1 == query_port_pa_info_dict["Node Id"]:
                query_node_port_list = query_port_pa_info_dict["Node Port"].split(",")
                intersection_node_port_list = list(set(node_id_1_port_list) & set(query_node_port_list))
                if len(intersection_node_port_list) != 0:
                    pa_problems.append({"MOP PA NAME": pa_name, "QUERY PA NAME": query_port_pa_info_dict["Pa Name"], "PROBLEM": "PORT ALREADY USED"})
            if node_id_1 == query_port_pa_info_dict["Node Id 1"]:
                query_node_1_port_list = query_port_pa_info_dict["Node Id 1 Port"].split(",")
                intersection_node_port_list = list(set(node_id_1_port_list) & set(query_node_1_port_list))
                if len(intersection_node_port_list) != 0:
                    pa_problems.append({"MOP PA NAME": pa_name, "QUERY PA NAME": query_port_pa_info_dict["Pa Name"], "PROBLEM": "PORT ALREADY USED"})
            if node_id_2 == query_port_pa_info_dict["Node Id"]:
                query_node_port_list = query_port_pa_info_dict["Node Port"].split(",")
                intersection_node_port_list = list(set(node_id_2_port_list) & set(query_node_port_list))
                if len(intersection_node_port_list) != 0:
                    pa_problems.append({"MOP PA NAME": pa_name, "QUERY PA NAME": query_port_pa_info_dict["Pa Name"], "PROBLEM": "PORT ALREADY USED"})
            if node_id_2 == query_port_pa_info_dict["Node Id 2"]:
                query_node_2_port_list = query_port_pa_info_dict["Node Id 2 Port"].split(",")
                intersection_node_port_list = list(set(node_id_2_port_list) & set(query_node_2_port_list))
                if len(intersection_node_port_list) != 0:
                    pa_problems.append({"MOP PA NAME": pa_name, "QUERY PA NAME": query_port_pa_info_dict["Pa Name"], "PROBLEM": "PORT ALREADY USED"})
    int_pol_group_name = f"LF_VPC_{tenant_name}_{node_id_1}-{node_id_2}_{pa_name}"
    # INTERFACE SELECTOR ADDS 4 or 5 characters:LF_VPC_GBZ3B-Backup_407-408_G3B_BSCSPRIMARY_lf407-408_VPC2_1_47
    if len(int_pol_group_name) > 59:
        pa_problems.append({"MOP PA NAME": pa_name, "QUERY PA NAME": "", "INTERFACE POLICY GROUP": int_pol_group_name, "PROBLEM": "INTERFACE POLICY GROUP OR INTERFACE SELECTOR NAMES ARE MORE THAN 64 CHARACTER"})

    return pa_problems

########################################################################################################################
############################################PORT PA PRECHECK DF HELPER FUNCTION#########################################


def precheck_port_pa_df(pa_list=[]):
    d = {}
    i = 0
    for pa_dict in pa_list:
        d.update({i: pa_dict})
        i += 1
    if not d:
        d = {0: {"MOP PA NAME": "", "QUERY PA NAME": "", "INTERFACE POLICY GROUP": "", "PROBLEM": ""}}
    df = pd.DataFrame.from_dict(d, orient="index")

    return df


########################################################################################################################
############################################VRF HELPER FUNCTION#########################################################


def query_vrf_helper(response_dict={}):
    vrf_list = []
    for d_list in response_dict["result"]["results"]:
        tenant_name = d_list[0]["value"]
        vrf_name = d_list[1]["value"]
        vpn_id = d_list[2]["value"]
        vrf_list.append({"Tenant Name": tenant_name, "Vrf Name": vrf_name, "Vpn Id": vpn_id})

    return vrf_list

########################################################################################################################
############################################VRF VPN-ID PRECHECK HELPER FUNCTION#########################################


def precheck_vpn_id_helper(vrf_info_dict_list=[], query_vrf_info_dict_list=[]):
    vrf_problems = []
    for vrf_info_dict in vrf_info_dict_list:
        vrf_name = vrf_info_dict["Vrf Name"]
        vrf_type = vrf_info_dict["Vrf Type"]
        vpn_id = vrf_info_dict["Vpn Id"]
        if vrf_type == "private" and vpn_id is None:
            vrf_problems.append({"MOP VRF NAME": vrf_name, "QUERY VRF NAME": "", "PROBLEM": "VPN-ID MISSING"})
        for query_vrf_info_dict in query_vrf_info_dict_list:
            if vpn_id == query_vrf_info_dict["Vpn Id"]:
                vrf_problems.append({"MOP VRF NAME": vrf_name, "QUERY VRF NAME": query_vrf_info_dict["Vrf Name"], "PROBLEM": "VPN-ID ALREADY USED"})

    return vrf_problems

########################################################################################################################
############################################VRF PRECHECK DF HELPER FUNCTION#############################################


def precheck_vrf_df(vrf_list=[]):
    d = {}
    i = 0
    for vrf_dict in vrf_list:
        d.update({i: vrf_dict})
        i += 1
    if not d:
        d = {0: {"MOP VRF NAME": "", "QUERY VRF NAME": "", "PROBLEM": ""}}
    df = pd.DataFrame.from_dict(d, orient="index")

    return df

########################################################################################################################
############################################NODE ID HELPER FUNCTION#####################################################


def query_node_id_helper(response_dict):
    node_id_list = []
    for d_list in response_dict["result"]["results"]:
        fabric = d_list[0]["value"]
        pod = d_list[1]["value"]
        node_id = d_list[2]["value"]
        node_id_list.append({"Fabric": fabric, "Pod": pod, "Node Id": node_id})

    return node_id_list

########################################################################################################################
############################################NODE ID PRECHECK HELPER FUNCTION############################################


def precheck_node_id_helper(port_pa_info_dict_list=[], query_node_id_info_dict_list=[]):
    node_id_list = []
    query_node_id_list = []
    node_id_problems = []
    for port_pa_info_dict in port_pa_info_dict_list:
        pa_type = port_pa_info_dict["Pa Type"]
        if pa_type == "VPC":
            node_1_id = port_pa_info_dict["Node Id 1"]
            node_2_id = port_pa_info_dict["Node Id 2"]
            if node_1_id not in node_id_list:
                node_id_list.append(node_1_id)
            if node_2_id not in node_id_list:
                node_id_list.append(node_2_id)
        else:
            node_id = port_pa_info_dict["Node Id"]
            if node_id not in node_id_list:
                node_id_list.append(node_id)
    for query_node_id_info_dict in query_node_id_info_dict_list:
        query_node_id = query_node_id_info_dict["Node Id"]
        query_node_id_list.append(query_node_id)
    node_id_list.sort(key=int)
    for node_id in node_id_list:
        if node_id not in query_node_id_list:
            node_id_problems.append({"NODE ID": node_id, "PROBLEM": "NODE ID IS NOT DEFINED IN ACI FABRIC"})

    return node_id_problems

########################################################################################################################
############################################NODE ID PRECHECK DF HELPER FUNCTION#########################################


def precheck_node_id_df(node_id_list=[]):
    d = {}
    i = 0
    for node_id_dict in node_id_list:
        d.update({i: node_id_dict})
        i += 1
    if not d:
        d = {0: {"NODE ID": "", "PROBLEM": ""}}
    df = pd.DataFrame.from_dict(d, orient="index")

    return df
########################################################################################################################
############################################PRECHECK FILE HELPER FUNCTION###############################################


def precheck_file(df_tenant=pd.DataFrame(), df_service=pd.DataFrame(), df_pa=pd.DataFrame(), df_vrf=pd.DataFrame(), df_node_id=pd.DataFrame(), df_l2ext=pd.DataFrame(), file_name=None):
    file = "NSO_PRECHECK_{}.xlsx".format(file_name.strip("xlsx"))
    with pd.ExcelWriter(file) as writer:
        df_tenant.to_excel(writer, sheet_name="TENANT")
        df_service.to_excel(writer, sheet_name="SERVICE")
        df_pa.to_excel(writer, sheet_name="PA")
        df_vrf.to_excel(writer, sheet_name="VRF")
        df_node_id.to_excel(writer, sheet_name="NODE ID")
        df_l2ext.to_excel(writer, sheet_name="L2 EXTERNAL")

########################################################################################################################
############################################GET TRANSACTION CHANGE HELPER FUNCTION######################################


def get_transaction_change_helper(response=None, devices_list=[]):
    flag = False
    for device in devices_list:
        if device in response:
            flag = True
            break

    return flag

########################################################################################################################
############################################COMMIT DRY-RUN HELPER FUNCTION##############################################


def commit_dryrun_helper(response_dict={}):
    logging.basicConfig(level=logging.DEBUG)
    output = response_dict["result"]["dry_run_result"]["cli"]["local_node"]["data"]
    logging.info(output)
    # output_list = output.splitlines()
    # for line in output_list:
    #     if line[0] == "-":
    #         raise Exception("Configuration Will Be Deleted On NSO or Devices")

    return output

########################################################################################################################
############################################QUERY PORT PA CONDITIONAL HELPER############################################


def query_port_pa_conditional_helper(response_dict={}):
    port_pa_list = []
    for d_list in response_dict["result"]["results"]:
        tenant_name = d_list[0]["value"]
        pa_name = d_list[1]["value"]
        fabric = d_list[2]["value"]
        d = {"Tenant Name": tenant_name, "Pa Name": pa_name, "Fabric": fabric}
        if d not in port_pa_list:
            port_pa_list.append(d)

    return port_pa_list

########################################################################################################################
############################################QUERY PORT PA EXTERNALLY USED BY HELPER FUNCTION############################


def query_port_pa_externally_used_by_helper(pa_name=None, response_dict={}):
    externally_used_by_list = []
    for d_list in response_dict["result"]["results"]:
        tenant_name = d_list[0]["value"]
        service_name = d_list[1]["value"]
        d = {"PA NAME": pa_name, "TENANT NAME": tenant_name, "SERVICE NAME": service_name}
        if d not in externally_used_by_list:
            externally_used_by_list.append(d)

    return externally_used_by_list

########################################################################################################################
############################################QUERY PORT PA EXTERNALLY USED BY DF HELPER FUNCTION#########################


def query_port_pa_externally_used_by_df_helper(externally_used_by_dict_list=[]):
    d = {}
    i = 0
    for externally_used_by_dict in externally_used_by_dict_list:
        d.update({i: externally_used_by_dict})
        i += 1
    if not d:
        d = {0: {"PA NAME": "", "TENANT NAME": "", "SERVICE NAME": ""}}
    df = pd.DataFrame.from_dict(d, orient="index")

    return df

########################################################################################################################
############################################QUERY L2EXT ENCAP ID HELPER FUNCTION########################################


def query_l2ext_encap_id_helper(response_dict={}):
    encap_id_info_dict_list = []
    for d_list in response_dict["result"]["results"]:
        evi_id = d_list[0]["value"]
        encap_id = d_list[1]["value"]
        bd_name = d_list[2]["value"]
        service_name = d_list[3]["value"]
        tenant_name = d_list[4]["value"]
        encap_id_info_dict = {"Tenant Name": tenant_name, "Service Name": service_name, "Bd Name": bd_name, "Encap Id": encap_id, "Evi": evi_id}
        if encap_id_info_dict not in encap_id_info_dict_list:
            encap_id_info_dict_list.append(encap_id_info_dict)

    return encap_id_info_dict_list


########################################################################################################################
############################################L2EXT PRECHECK HELPER FUNCTION##############################################


def precheck_l2ext_helper(l2ext_info_dict_list=[], query_transit_leaf_tenant_pa_info_dict_list=[], query_l2ext_info_dict_list=[]):
    l2ext_list = []
    for l2ext_info_dict in l2ext_info_dict_list:
        service_name = l2ext_info_dict["Service Name"]
        encap_id = l2ext_info_dict["Encap Id"]
        for query_transit_leaf_tenant_pa_info_dict in query_transit_leaf_tenant_pa_info_dict_list:
            if encap_id == query_transit_leaf_tenant_pa_info_dict["Encap Id"] and service_name == query_transit_leaf_tenant_pa_info_dict["Service Name"]:
                evi_id = l2ext_info_dict["Evi"]
                d = {"EVI ID": evi_id, "PROBLEM": "ENCAP ID IS TAGGED AT TRANSIT LEAF"}
                if d not in l2ext_list:
                    l2ext_list.append(d)
        for query_l2ext_info_dict in query_l2ext_info_dict_list:
            if encap_id == query_l2ext_info_dict["Encap Id"]:
                evi_id = query_l2ext_info_dict["Evi"]
                d = {"EVI ID": evi_id, "PROBLEM": "ENCAP ID IS ALREADY USED AT DCI"}
                if d not in l2ext_list:
                    l2ext_list.append(d)

    return l2ext_list

########################################################################################################################
############################################L2EXT PRECHECK DF HELPER FUNCTION###########################################


def precheck_l2ext_df_helper(l2ext_problems_list=[]):
    d = {}
    i = 0
    for l2ext_problem_dict in l2ext_problems_list:
        d.update({i: l2ext_problem_dict})
        i += 1
    if not d:
        d = {0: {"EVI ID": "", "PROBLEM": ""}}
    df = pd.DataFrame.from_dict(d, orient="index")

    return df

########################################################################################################################
############################################L3DIRECT BGP HELPER FUNCTION################################################


def query_l3direct_bgp_helper(response_dict={}):
    d = {}
    i = 0
    for d_list in response_dict["result"]["results"]:
        tenant_name = d_list[0]["value"]
        service_name = d_list[1]["value"]
        d.update({i: {"TENANT NAME": tenant_name, "SERVICE NAME": service_name}})
        i += 1
    if not d:
        d = {"TENANT NAME": "", "SERVICE NAME": ""}

    return d

########################################################################################################################
############################################QUERY FILE HELPER FUNCTION##################################################


def query_file(df=pd.DataFrame(), query_name=None):
    file = "NSO_QUERY_{}.xlsx".format(query_name)
    with pd.ExcelWriter(file) as writer:
        df.to_excel(writer, sheet_name=query_name)

########################################################################################################################
############################################DCI BGP CHECK HELPER########################################################


def query_l3direct_bgp_neighbor_helper(response_dict={}):
    d_list = []
    for response_list in response_dict["result"]["results"]:
        tenant_name = response_list[0]["value"]
        service_name = response_list[1]["value"]
        fabric = response_list[2]["value"]
        vrf_name = response_list[3]["value"]
        bd_name = response_list[4]["value"]
        epg_name = response_list[5]["value"]
        encap_id = response_list[6]["value"]
        l3direct_name = response_list[7]["value"]
        bgp_neighbor_address = response_list[8]["value"]

        d_list.append({"FABRIC": fabric, "TENANT NAME": tenant_name, "SERVICE NAME": service_name, "VRF NAME": vrf_name, "BD NAME": bd_name, "EPG NAME": epg_name, "ENCAP ID": encap_id, "L3DIRECT NAME": l3direct_name, "BGP NEIGHBOR ADDRESS": bgp_neighbor_address})

    return d_list

########################################################################################################################
############################################DCI BGP CHECK HELPER########################################################


def query_l3direct_bgp_neighbor_policy_helper(response_dict={}):
    inbound_policy = [*response_dict["result"]["acidc-services:neighbor"]["inbound-policy"]][0]
    outbound_policy = [*response_dict["result"]["acidc-services:neighbor"]["outbound-policy"]][0]

    return inbound_policy, outbound_policy

########################################################################################################################
############################################DCI VRF TYPE CHECK HELPER###################################################


def query_l3direct_bgp_neighbor_vrf_helper(response_dict={}):
    for d_list in response_dict["result"]["results"]:

        return d_list[0]["value"]

########################################################################################################################
############################################DCI CHECK TO FILE  HELPER###################################################


def dci_check_to_file_helper(d_list=[], nso_name=""):
    d = {}
    i = 0
    for d_list_d in d_list:
        d.update({i: d_list_d})
        i += 1
    df = pd.DataFrame.from_dict(d, orient="index")
    file = "DCI_CHECK_{}.xlsx".format(nso_name)
    with pd.ExcelWriter(file) as writer:
        df.to_excel(writer, index=False)

########################################################################################################################
############################################QUERY SERVICE DCLAN CONDITIONAL HELPER######################################


def query_service_dclan_fabric_conditional_helper(response_dict={}):
    service_dclan_list = []
    for d_list in response_dict["result"]["results"]:
        xpath = f"/acidc/tenants{{{d_list[0]['value']}}}/service/dclan{{{d_list[1]['value']}}}"
        service_dclan_list.append(xpath)

    return service_dclan_list

########################################################################################################################
############################################QUERY PORT PA CONDITIONAL HELPER############################################


def query_port_pa_fabric_conditional_helper(response_dict={}):
    port_pa_list = []
    for d_list in response_dict["result"]["results"]:
        xpath = f"/acidc/tenants{{{d_list[0]['value']}}}/port/pa{{{d_list[1]['value']}}}"
        port_pa_list.append(xpath)

    return port_pa_list
