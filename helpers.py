############################################HELPER MODULE FOR NSO FILE##################################################
############################################VRF HELPER FUNCTION#########################################################


def vrf_info_dict_list_helper(vrf_info_dict_list):
    helper_vrf_info_dict_list = []
    for vrf_info_dict in vrf_info_dict_list:
        if vrf_info_dict["Vpn Id"] == vrf_info_dict["Vpn Id"] and vrf_info_dict["Vpn Id"] is not None:
            vrf_info_dict["Vpn Id"] = str(int(vrf_info_dict["Vpn Id"]))  # Convert float to integer, then integer to string
        if vrf_info_dict["Custom Import RT List"] == vrf_info_dict["Custom Import RT List"] and vrf_info_dict["Custom Import RT List"] is not None:
            vrf_info_dict["Custom Import RT List"] = str(vrf_info_dict["Custom Import RT List"]).split(",")
        if vrf_info_dict["Custom Export RT List"] == vrf_info_dict["Custom Export RT List"] and vrf_info_dict["Custom Export RT List"] is not None:
            vrf_info_dict["Custom Export RT List"] = str(vrf_info_dict["Custom Export RT List"]).split(",")
        if vrf_info_dict["Static"] == vrf_info_dict["Static"] and vrf_info_dict["Static"] is not None:
            vrf_info_dict["Static"] = str(vrf_info_dict["Static"])
        if vrf_info_dict["Connected"] == vrf_info_dict["Connected"] and vrf_info_dict["Connected"] is not None:
            vrf_info_dict["Connected"] = str(vrf_info_dict["Connected"])
        if vrf_info_dict["Vrf Export Policy"] == vrf_info_dict["Vrf Export Policy"] and vrf_info_dict["Vrf Export Policy"] is not None:
            vrf_info_dict["Vrf Export Policy"] = str(vrf_info_dict["Vrf Export Policy"])
        if vrf_info_dict["Vrf Import Policy"] == vrf_info_dict["Vrf Import Policy"] and vrf_info_dict["Vrf Import Policy"] is not None:
            vrf_info_dict["Vrf Import Policy"] = str(vrf_info_dict["Vrf Import Policy"])
        if vrf_info_dict["Vrf Export Policy Prefix List"] == vrf_info_dict["Vrf Export Policy Prefix List"] and vrf_info_dict["Vrf Export Policy Prefix List"] is not None:
            vrf_info_dict["Vrf Export Policy Prefix List"] = str(vrf_info_dict["Vrf Export Policy Prefix List"])
        if vrf_info_dict["Vrf Export Policy Local Preference"] == vrf_info_dict["Vrf Export Policy Local Preference"] and vrf_info_dict["Vrf Export Policy Local Preference"] is not None:
            vrf_info_dict["Vrf Export Policy Local Preference"] = str(int(vrf_info_dict["Vrf Export Policy Local Preference"]))  # Convert float to integer, then integer to string
        if vrf_info_dict["Vrf Import Policy Prefix List"] == vrf_info_dict["Vrf Import Policy Prefix List"] and vrf_info_dict["Vrf Import Policy Prefix List"] is not None:
            vrf_info_dict["Vrf Import Policy Prefix List"] = str(vrf_info_dict["Vrf Import Policy Prefix List"])
        if vrf_info_dict not in helper_vrf_info_dict_list:
            helper_vrf_info_dict_list.append(vrf_info_dict)
    helper_vrf_info_dict_list = sorted(helper_vrf_info_dict_list, key=lambda k: k["Tenant Name"])

    return helper_vrf_info_dict_list
########################################################################################################################
############################################ENCAP HELPER FUNCTION#######################################################


def encap_info_dict_list_helper(encap_info_dict_list):
    helper_encap_info_dict_list = []
    for encap_info_dict in encap_info_dict_list:
        encap_info_dict["Encap Id"] = str(int(encap_info_dict["Encap Id"]))  #Convert float to integer, then integer to string
        if encap_info_dict not in helper_encap_info_dict_list:
            helper_encap_info_dict_list.append(encap_info_dict)
    helper_encap_info_dict_list = sorted(helper_encap_info_dict_list, key=lambda k: k["Tenant Name"])

    return helper_encap_info_dict_list
########################################################################################################################
############################################PORT PA HELPER FUNCTION#####################################################


def pa_info_dict_list_helper(pa_info_dict_list):
    helper_pa_info_dict_list = []
    for pa_info_dict in pa_info_dict_list:
        pa_info_dict["Pod"] = str(int(pa_info_dict["Pod"]))  #Convert float to integer, then integer to string
        if pa_info_dict["Node Id"] == pa_info_dict["Node Id"] and pa_info_dict["Node Id"] is not None:
            pa_info_dict["Node Id"] = str(int(pa_info_dict["Node Id"]))  #Convert float to integer, then integer to string
        if pa_info_dict["Pa Type"] == pa_info_dict["Pa Type"] and pa_info_dict["Pa Type"] is not None:
            pa_info_dict["Pa Type"] = str(pa_info_dict["Pa Type"])
        if pa_info_dict["Interface Profile"] == pa_info_dict["Interface Profile"] and pa_info_dict["Interface Profile"] is not None:
            pa_info_dict["Interface Profile"] = str(pa_info_dict["Interface Profile"])
        if pa_info_dict["Node Port List"] == pa_info_dict["Node Port List"] and pa_info_dict["Node Port List"] is not None:
            if "[" in pa_info_dict["Node Port List"]:
                bad_chars = " '[]Ethernet"
                pa_info_dict["Node Port List"] = "".join(x for x in pa_info_dict["Node Port List"] if x not in bad_chars)
                pa_info_dict["Node Port List"] = pa_info_dict["Node Port List"].split(",")
            else:
                pa_info_dict["Node Port List"] = str(pa_info_dict["Node Port List"]).strip("Ethernet").split(",")  #Convert string to list
        if pa_info_dict["Node Id 1"] == pa_info_dict["Node Id 1"] and pa_info_dict["Node Id 1"] is not None:
            pa_info_dict["Node Id 1"] = str(int(pa_info_dict["Node Id 1"]))  #Convert float to integer, then integer to string
        if pa_info_dict["Node Id 2"] == pa_info_dict["Node Id 2"] and pa_info_dict["Node Id 2"] is not None:
            pa_info_dict["Node Id 2"] = str(int(pa_info_dict["Node Id 2"]))  #Convert float to integer, then integer to string
        if pa_info_dict["Node Id 1 Port List"] == pa_info_dict["Node Id 1 Port List"] and pa_info_dict["Node Id 1 Port List"] is not None:
            if "[" in pa_info_dict["Node Id 1 Port List"]:
                bad_chars = " '[]Ethernet"
                pa_info_dict["Node Id 1 Port List"] = "".join(x for x in pa_info_dict["Node Id 1 Port List"] if x not in bad_chars)
                pa_info_dict["Node Id 1 Port List"] = pa_info_dict["Node Id 1 Port List"].split(",")
            else:
                pa_info_dict["Node Id 1 Port List"] = str(pa_info_dict["Node Id 1 Port List"]).strip("Ethernet").split(",")  #Convert string to list
        if pa_info_dict["Node Id 2 Port List"] == pa_info_dict["Node Id 2 Port List"] and pa_info_dict["Node Id 2 Port List"] is not None:
            if "[" in pa_info_dict["Node Id 2 Port List"]:
                bad_chars = " '[]Ethernet"
                pa_info_dict["Node Id 2 Port List"] = "".join(x for x in pa_info_dict["Node Id 2 Port List"] if x not in bad_chars)
                pa_info_dict["Node Id 2 Port List"] = pa_info_dict["Node Id 2 Port List"].split(",")
            else:
                pa_info_dict["Node Id 2 Port List"] = str(pa_info_dict["Node Id 2 Port List"]).strip("Ethernet").split(",")  #Convert string to list
        if pa_info_dict not in helper_pa_info_dict_list:
            helper_pa_info_dict_list.append(pa_info_dict)
    helper_pa_info_dict_list = sorted(helper_pa_info_dict_list, key=lambda k: k["Tenant Name"])

    return helper_pa_info_dict_list
########################################################################################################################
############################################TENANT PA HELPER FUNCTION###################################################


def tenant_pa_info_dict_list_helper(tenant_pa_info_dict_list):
    helper_tenant_pa_info_dict_list = []
    for tenant_pa_info_dict in tenant_pa_info_dict_list:
        tenant_pa_info_dict["Encap Id"] = str(int(tenant_pa_info_dict["Encap Id"]))  #Convert float to integer, then integer to string
        if tenant_pa_info_dict["Mode"] == tenant_pa_info_dict["Mode"] and tenant_pa_info_dict["Mode"] is not None:
            tenant_pa_info_dict["Mode"] = str(tenant_pa_info_dict["Mode"])
        if tenant_pa_info_dict["External Tenant Name"] == tenant_pa_info_dict["External Tenant Name"] and tenant_pa_info_dict["External Tenant Name"] is not None:
            tenant_pa_info_dict["External Tenant Name"] = str(tenant_pa_info_dict["External Tenant Name"])
        if tenant_pa_info_dict not in helper_tenant_pa_info_dict_list:
            helper_tenant_pa_info_dict_list.append(tenant_pa_info_dict)
    helper_tenant_pa_info_dict_list = sorted(helper_tenant_pa_info_dict_list, key=lambda k: k["Tenant Name"])

    return helper_tenant_pa_info_dict_list
########################################################################################################################
############################################PREFIX-LIST HELPER FUNCTION#################################################


def prefix_list_info_dict_list_helper(prefix_list_info_dict_list):
    helper_prefix_list_info_dict_list = []
    for prefix_list_info_dict in prefix_list_info_dict_list:
        if prefix_list_info_dict["Eq"] == prefix_list_info_dict["Eq"] and prefix_list_info_dict["Eq"] is not None:
            prefix_list_info_dict["Eq"] = str(int(prefix_list_info_dict["Eq"]))  #Convert float to integer, then integer to string
        if prefix_list_info_dict["Ge"] == prefix_list_info_dict["Ge"] and prefix_list_info_dict["Ge"] is not None:
            prefix_list_info_dict["Ge"] = str(int(prefix_list_info_dict["Ge"]))  #Convert float to integer, then integer to string
        if prefix_list_info_dict["Le"] == prefix_list_info_dict["Le"] and prefix_list_info_dict["Le"] is not None:
            prefix_list_info_dict["Le"] = str(int(prefix_list_info_dict["Le"]))  #Convert float to integer, then integer to string
        if prefix_list_info_dict not in helper_prefix_list_info_dict_list:
            helper_prefix_list_info_dict_list.append(prefix_list_info_dict)
    helper_prefix_list_info_dict_list = sorted(helper_prefix_list_info_dict_list, key=lambda k: k["Tenant Name"])

    return helper_prefix_list_info_dict_list
########################################################################################################################
############################################L3 DIRECT HELPER FUNCTION###################################################


def l3direct_info_dict_list_helper(l3direct_info_dict_list):
    helper_l3direct_info_dict_list = []
    for l3direct_info_dict in l3direct_info_dict_list:
        l3direct_info_dict["Encap Id"] = str(int(l3direct_info_dict["Encap Id"]))  #Convert float to integer, then integer to string
        if l3direct_info_dict["Secondary IPv4 Network List"] == l3direct_info_dict["Secondary IPv4 Network List"] and l3direct_info_dict["Secondary IPv4 Network List"] is not None:
            l3direct_info_dict["Secondary IPv4 Network List"] = str(l3direct_info_dict["Secondary IPv4 Network List"]).split(",")  #Convert string to list
        if l3direct_info_dict["Input Policy Map"] == l3direct_info_dict["Input Policy Map"] and l3direct_info_dict["Input Policy Map"] is not None:
            l3direct_info_dict["Input Policy Map"] = str(l3direct_info_dict["Input Policy Map"])
        if l3direct_info_dict["Output Policy Map"] == l3direct_info_dict["Output Policy Map"] and l3direct_info_dict["Output Policy Map"] is not None:
            l3direct_info_dict["Output Policy Map"] = str(l3direct_info_dict["Output Policy Map"])
        if l3direct_info_dict not in helper_l3direct_info_dict_list:
            helper_l3direct_info_dict_list.append(l3direct_info_dict)
    helper_l3direct_info_dict_list = sorted(helper_l3direct_info_dict_list, key=lambda k: k["Tenant Name"])

    return helper_l3direct_info_dict_list

########################################################################################################################
############################################DELETE L3 DIRECT SHUTDOWN HELPER FUNCTION###################################


def delete_l3direct_shutdown_info_dict_list_helper(delete_l3direct_shutdown_info_dict_list):
    helper_delete_l3direct_shutdown_info_dict_list = []
    for delete_l3direct_shutdown_info_dict in delete_l3direct_shutdown_info_dict_list:
        delete_l3direct_shutdown_info_dict["Encap Id"] = str(int(delete_l3direct_shutdown_info_dict["Encap Id"]))  # Convert float to integer, then integer to string
        if delete_l3direct_shutdown_info_dict not in helper_delete_l3direct_shutdown_info_dict_list:
            helper_delete_l3direct_shutdown_info_dict_list.append(delete_l3direct_shutdown_info_dict)
    helper_delete_l3direct_shutdown_info_dict_list = sorted(helper_delete_l3direct_shutdown_info_dict_list, key=lambda k: k["Tenant Name"])

    return helper_delete_l3direct_shutdown_info_dict_list
########################################################################################################################
############################################L3 DIRECT STATIC HELPER FUNCTION############################################


def l3direct_static_info_dict_list_helper(l3direct_static_info_dict_list):
    helper_l3direct_static_info_dict_list = []
    for l3direct_static_info_dict in l3direct_static_info_dict_list:
        l3direct_static_info_dict["Encap Id"] = str(int(l3direct_static_info_dict["Encap Id"]))  #Convert float to integer, then integer to string
        if l3direct_static_info_dict["Administrative Distance"] == l3direct_static_info_dict["Administrative Distance"] and l3direct_static_info_dict["Administrative Distance"] is not None:
            l3direct_static_info_dict["Administrative Distance"] = str(int(l3direct_static_info_dict["Administrative Distance"]))  #Convert float to integer, then integer to string
        if l3direct_static_info_dict["Tag"] == l3direct_static_info_dict["Tag"] and l3direct_static_info_dict["Tag"] is not None:
            l3direct_static_info_dict["Tag"] = str(int(l3direct_static_info_dict["Tag"]))  #Convert float to integer, then integer to string
        if l3direct_static_info_dict not in helper_l3direct_static_info_dict_list:
            helper_l3direct_static_info_dict_list.append(l3direct_static_info_dict)
    helper_l3direct_static_info_dict_list = sorted(helper_l3direct_static_info_dict_list, key=lambda k: k["Tenant Name"])  #Convert float to integer, then integer to string

    return helper_l3direct_static_info_dict_list
########################################################################################################################
############################################L3 DIRECT OSPF HELPER FUNCTION##############################################


def l3direct_ospf_info_dict_list_helper(l3direct_ospf_info_dict_list):
    helper_l3direct_ospf_info_dict_list = []
    for l3direct_ospf_info_dict in l3direct_ospf_info_dict_list:
        l3direct_ospf_info_dict["Encap Id"] = str(int(l3direct_ospf_info_dict["Encap Id"]))  #Convert float to integer, then integer to string
        l3direct_ospf_info_dict["Process Id"] = str(int(l3direct_ospf_info_dict["Process Id"]))  #Convert float to integer, then integer to string
        if l3direct_ospf_info_dict not in helper_l3direct_ospf_info_dict_list:
            helper_l3direct_ospf_info_dict_list.append(l3direct_ospf_info_dict)
    helper_l3direct_ospf_info_dict_list = sorted(helper_l3direct_ospf_info_dict_list, key=lambda k: k["Tenant Name"])

    return helper_l3direct_ospf_info_dict_list
########################################################################################################################
############################################L3 DIRECT BGP HELPER FUNCTION###############################################


def l3direct_bgp_info_dict_list_helper(l3direct_bgp_info_dict_list):
    helper_l3direct_bgp_info_dict_list = []
    for l3direct_bgp_info_dict in l3direct_bgp_info_dict_list:
        l3direct_bgp_info_dict["Encap Id"] = str(int(l3direct_bgp_info_dict["Encap Id"]))  #Convert float to integer, then integer to string
        l3direct_bgp_info_dict["Remote As"] = str(int(l3direct_bgp_info_dict["Remote As"]))  # Convert float to integer, then integer to string
        if l3direct_bgp_info_dict["Bfd Min Interval"] == l3direct_bgp_info_dict["Bfd Min Interval"] and l3direct_bgp_info_dict["Bfd Min Interval"] is not None:
            l3direct_bgp_info_dict["Bfd Min Interval"] = str(int(l3direct_bgp_info_dict["Bfd Min Interval"]))  #Convert float to integer, then integer to string
        if l3direct_bgp_info_dict["Bfd Multiplier"] == l3direct_bgp_info_dict["Bfd Multiplier"] and l3direct_bgp_info_dict["Bfd Multiplier"] is not None:
            l3direct_bgp_info_dict["Bfd Multiplier"] = str(int(l3direct_bgp_info_dict["Bfd Multiplier"]))  #Convert float to integer, then integer to string
        if l3direct_bgp_info_dict["Max Prefix"] == l3direct_bgp_info_dict["Max Prefix"] and l3direct_bgp_info_dict["Max Prefix"] is not None:
            l3direct_bgp_info_dict["Max Prefix"] = str(int(l3direct_bgp_info_dict["Max Prefix"]))  #Convert float to integer, then integer to string
        if l3direct_bgp_info_dict["Local As"] == l3direct_bgp_info_dict["Local As"] and l3direct_bgp_info_dict["Local As"] is not None:
            l3direct_bgp_info_dict["Local As"] = str(int(l3direct_bgp_info_dict["Local As"]))  #Convert float to integer, then integer to string
        if l3direct_bgp_info_dict["Keepalive"] == l3direct_bgp_info_dict["Keepalive"] and l3direct_bgp_info_dict["Keepalive"] is not None:
            l3direct_bgp_info_dict["Keepalive"] = str(int(l3direct_bgp_info_dict["Keepalive"]))  #Convert float to integer, then integer to string
        if l3direct_bgp_info_dict["Hold Time"] == l3direct_bgp_info_dict["Hold Time"] and l3direct_bgp_info_dict["Hold Time"] is not None:
            l3direct_bgp_info_dict["Hold Time"] = str(int(l3direct_bgp_info_dict["Hold Time"]))  #Convert float to integer, then integer to string
        if l3direct_bgp_info_dict["In Rpl Local Preference"] == l3direct_bgp_info_dict["In Rpl Local Preference"] and l3direct_bgp_info_dict["In Rpl Local Preference"] is not None:
            l3direct_bgp_info_dict["In Rpl Local Preference"] = str(int(l3direct_bgp_info_dict["In Rpl Local Preference"]))  #Convert float to integer, then integer to string
        if l3direct_bgp_info_dict["In Rpl As Path"] == l3direct_bgp_info_dict["In Rpl As Path"] and l3direct_bgp_info_dict["In Rpl As Path"] is not None:
            l3direct_bgp_info_dict["In Rpl As Path"] = str(int(l3direct_bgp_info_dict["In Rpl As Path"]))  #Convert float to integer, then integer to string
        if l3direct_bgp_info_dict["In Rpl Multiplier"] == l3direct_bgp_info_dict["In Rpl Multiplier"] and l3direct_bgp_info_dict["In Rpl Multiplier"] is not None:
            l3direct_bgp_info_dict["In Rpl Multiplier"] = str(int(l3direct_bgp_info_dict["In Rpl Multiplier"]))  #Convert float to integer, then integer to string
        if l3direct_bgp_info_dict["In Rpl Community List"] == l3direct_bgp_info_dict["In Rpl Community List"] and l3direct_bgp_info_dict["In Rpl Community List"] is not None:
            l3direct_bgp_info_dict["In Rpl Community List"] = str(l3direct_bgp_info_dict["In Rpl Local Preference"]).split(",")  #Convert string to list
        if l3direct_bgp_info_dict["Out Rpl As Path"] == l3direct_bgp_info_dict["Out Rpl As Path"] and l3direct_bgp_info_dict["Out Rpl As Path"] is not None:
            l3direct_bgp_info_dict["Out Rpl As Path"] = str(int(l3direct_bgp_info_dict["Out Rpl As Path"]))  #Convert float to integer, then integer to string
        if l3direct_bgp_info_dict["Out Rpl Multiplier"] == l3direct_bgp_info_dict["Out Rpl Multiplier"] and l3direct_bgp_info_dict["Out Rpl Multiplier"] is not None:
            l3direct_bgp_info_dict["Out Rpl Multiplier"] = str(int(l3direct_bgp_info_dict["Out Rpl Multiplier"]))  #Convert float to integer, then integer to string
        if l3direct_bgp_info_dict["In Rpl Name"] == l3direct_bgp_info_dict["In Rpl Name"] and l3direct_bgp_info_dict["In Rpl Name"] is not None:
            l3direct_bgp_info_dict["In Rpl Name"] = str(l3direct_bgp_info_dict["In Rpl Name"])
        if l3direct_bgp_info_dict["In Rpl Custom Policy Name"] == l3direct_bgp_info_dict["In Rpl Custom Policy Name"] and l3direct_bgp_info_dict["In Rpl Custom Policy Name"] is not None:
            l3direct_bgp_info_dict["In Rpl Custom Policy Name"] = str(l3direct_bgp_info_dict["In Rpl Custom Policy Name"])
        if l3direct_bgp_info_dict["In Rpl Prefix List"] == l3direct_bgp_info_dict["In Rpl Prefix List"] and l3direct_bgp_info_dict["In Rpl Prefix List"] is not None:
            l3direct_bgp_info_dict["In Rpl Prefix List"] = str(l3direct_bgp_info_dict["In Rpl Prefix List"])
        if l3direct_bgp_info_dict["In Rpl Blackhole Prefix List"] == l3direct_bgp_info_dict["In Rpl Blackhole Prefix List"] and l3direct_bgp_info_dict["In Rpl Blackhole Prefix List"] is not None:
            l3direct_bgp_info_dict["In Rpl Blackhole Prefix List"] = str(l3direct_bgp_info_dict["In Rpl Blackhole Prefix List"])
        if l3direct_bgp_info_dict["In Rpl Community Name"] == l3direct_bgp_info_dict["In Rpl Community Name"] and l3direct_bgp_info_dict["In Rpl Community Name"] is not None:
            l3direct_bgp_info_dict["In Rpl Community Name"] = str(l3direct_bgp_info_dict["In Rpl Community Name"])
        if l3direct_bgp_info_dict["Out Rpl Name"] == l3direct_bgp_info_dict["Out Rpl Name"] and l3direct_bgp_info_dict["Out Rpl Name"] is not None:
            l3direct_bgp_info_dict["Out Rpl Name"] = str(l3direct_bgp_info_dict["Out Rpl Name"])
        if l3direct_bgp_info_dict["Out Rpl Custom Policy Name"] == l3direct_bgp_info_dict["Out Rpl Custom Policy Name"] and l3direct_bgp_info_dict["Out Rpl Custom Policy Name"] is not None:
            l3direct_bgp_info_dict["Out Rpl Custom Policy Name"] = str(l3direct_bgp_info_dict["Out Rpl Custom Policy Name"])
        if l3direct_bgp_info_dict["Out Rpl Prefix List"] == l3direct_bgp_info_dict["Out Rpl Prefix List"] and l3direct_bgp_info_dict["Out Rpl Custom Policy Name"] is not None:
            l3direct_bgp_info_dict["Out Rpl Prefix List"] = str(l3direct_bgp_info_dict["Out Rpl Custom Policy Name"])
        if l3direct_bgp_info_dict not in helper_l3direct_bgp_info_dict_list:
            helper_l3direct_bgp_info_dict_list.append(l3direct_bgp_info_dict)
    helper_l3direct_bgp_info_dict_list = sorted(helper_l3direct_bgp_info_dict_list, key=lambda k: k["Tenant Name"])

    return helper_l3direct_bgp_info_dict_list
########################################################################################################################
############################################L3 DIRECT AGGREGATE HELPER FUNCTION#########################################


def l3direct_aggregate_info_dict_list_helper(l3direct_aggregate_info_dict_list):
    helper_l3direct_aggregate_info_dict_list = []
    for l3direct_aggregate_info_dict in l3direct_aggregate_info_dict_list:
        l3direct_aggregate_info_dict['Encap Id'] = str(int(l3direct_aggregate_info_dict['Encap Id']))  #Convert float to integer, then integer to string
        if l3direct_aggregate_info_dict not in helper_l3direct_aggregate_info_dict_list:
            helper_l3direct_aggregate_info_dict_list.append(l3direct_aggregate_info_dict)
    helper_l3direct_aggregate_info_dict_list = sorted(helper_l3direct_aggregate_info_dict_list, key=lambda k: k["Tenant Name"])

    return helper_l3direct_aggregate_info_dict_list
########################################################################################################################
############################################L2 EXTERNAL HELPER FUNCTION#################################################


def l2ext_info_dict_list_helper(l2ext_info_dict_list):
    helper_l2ext_info_dict_list = []
    for l2ext_info_dict in l2ext_info_dict_list:
        l2ext_info_dict['Encap Id'] = str(int(l2ext_info_dict['Encap Id']))  #Convert float to integer, then integer to string
        if l2ext_info_dict['Evi'] == l2ext_info_dict['Evi'] and l2ext_info_dict['Evi'] is not None:
            l2ext_info_dict['Evi'] = str(int(l2ext_info_dict['Evi']))  #Convert float to integer, then integer to string
        if l2ext_info_dict['Circuit Id'] == l2ext_info_dict['Circuit Id'] and l2ext_info_dict['Circuit Id'] is not None:
            l2ext_info_dict['Circuit Id'] = str(int(l2ext_info_dict['Circuit Id']))  #Convert float to integer, then integer to string
        if l2ext_info_dict['Neighbor Ip'] == l2ext_info_dict['Neighbor Ip'] and l2ext_info_dict['Neighbor Ip'] is not None:
            l2ext_info_dict['Neighbor Ip'] = str(l2ext_info_dict['Neighbor Ip'])
        if l2ext_info_dict['Pw Class'] == l2ext_info_dict['Pw Class'] and l2ext_info_dict['Pw Class'] is not None:
            l2ext_info_dict['Pw Class'] = str(l2ext_info_dict['Pw Class'])
        if l2ext_info_dict['Mtu'] == l2ext_info_dict['Mtu'] and l2ext_info_dict['Mtu'] is not None:
            l2ext_info_dict['Mtu'] = str(int(l2ext_info_dict['Mtu']))  #Convert float to integer, then integer to string
        if l2ext_info_dict not in helper_l2ext_info_dict_list:
            helper_l2ext_info_dict_list.append(l2ext_info_dict)
    helper_l2ext_info_dict_list = sorted(helper_l2ext_info_dict_list, key=lambda k: k["Tenant Name"])

    return helper_l2ext_info_dict_list
########################################################################################################################
############################################MAIN HELPER FUNCTION########################################################


if __name__ == "__main__":
    pass
