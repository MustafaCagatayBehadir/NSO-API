from nso_config import NsoConfig
from nso_file import NsoFile


def nso_config(file_name=None):
    output = ""
    nsofile = NsoFile(file_name)
    nsoconfig = NsoConfig()
    tenant_info_dict_list = nsofile.create_tenant_info_dict_list()
    port_pa_info_dict_list = nsofile.create_pa_info_dict_list()
    vrf_info_dict_list = nsofile.create_vrf_info_dict_list()
    prefix_list_info_dict_list = nsofile.create_prefix_list_info_dict_list()
    service_info_dict_list = nsofile.create_service_info_dict_list()
    bd_info_dict_list = nsofile.create_bd_info_dict_list()
    epg_info_dict_list = nsofile.create_epg_info_dict_list()
    encap_info_dict_list = nsofile.create_encap_info_dict_list()
    tenant_pa_info_dict_list = nsofile.create_tenant_pa_info_dict_list()
    l3direct_info_dict_list = nsofile.create_l3direct_info_dict_list()
    l3direct_static_info_dict_list = nsofile.create_l3direct_static_info_dict_list()
    l3direct_bgp_info_dict_list = nsofile.create_l3direct_bgp_info_dict_list()
    l2ext_info_dict_list = nsofile.create_l2ext_info_dict_list()
    for tenant_info_dict in tenant_info_dict_list:
        output += nsoconfig.create_tenant_config(tenant_info_dict)
        for port_pa_info_dict in port_pa_info_dict_list:
            if port_pa_info_dict["Tenant Name"] == tenant_info_dict["Tenant Name"]:
                output += nsoconfig.create_pa_config(port_pa_info_dict)
        for vrf_info_dict in vrf_info_dict_list:
            if vrf_info_dict["Tenant Name"] == tenant_info_dict["Tenant Name"]:
                output += nsoconfig.create_vrf_config(vrf_info_dict)
        for prefix_list_info_dict in prefix_list_info_dict_list:
            if prefix_list_info_dict["Tenant Name"] == tenant_info_dict["Tenant Name"]:
                output += nsoconfig.create_prefix_list_config(prefix_list_info_dict)
        for service_info_dict in service_info_dict_list:
            if service_info_dict["Tenant Name"] == tenant_info_dict["Tenant Name"]:
                output += nsoconfig.create_service_config(service_info_dict)
                for bd_info_dict in bd_info_dict_list:
                    if bd_info_dict["Service Name"] == service_info_dict["Service Name"]:
                        output += nsoconfig.create_bd_config(bd_info_dict)
                        for epg_info_dict in epg_info_dict_list:
                            if epg_info_dict["Service Name"] == bd_info_dict["Service Name"] and epg_info_dict["Bd Name"] == bd_info_dict["Bd Name"]:
                                output += nsoconfig.create_epg_config(epg_info_dict)
                                for encap_info_dict in encap_info_dict_list:
                                    if encap_info_dict["Service Name"] == epg_info_dict["Service Name"] and encap_info_dict["Epg Name"] == epg_info_dict["Epg Name"]:
                                        output += nsoconfig.create_encap_config(encap_info_dict)
                                        for tenant_pa_info_dict in tenant_pa_info_dict_list:
                                            if tenant_pa_info_dict["Service Name"] == encap_info_dict["Service Name"] and tenant_pa_info_dict["Encap Id"] == encap_info_dict["Encap Id"]:
                                                output += nsoconfig.create_tenant_pa_config(tenant_pa_info_dict)
                                        for l3direct_info_dict in l3direct_info_dict_list:
                                            if l3direct_info_dict["Service Name"] == encap_info_dict["Service Name"] and l3direct_info_dict["Encap Id"] == encap_info_dict["Encap Id"]:
                                                output += nsoconfig.create_l3direct_config(l3direct_info_dict)
                                        for l3direct_static_info_dict in l3direct_static_info_dict_list:
                                            if l3direct_static_info_dict["Service Name"] == encap_info_dict["Service Name"] and l3direct_static_info_dict["Encap Id"] == encap_info_dict["Encap Id"]:
                                                output += nsoconfig.create_l3direct_static_config(l3direct_static_info_dict)
                                        for l3direct_bgp_info_dict in l3direct_bgp_info_dict_list:
                                            if l3direct_bgp_info_dict["Service Name"] == encap_info_dict["Service Name"] and l3direct_bgp_info_dict["Encap Id"] == encap_info_dict["Encap Id"]:
                                                output += nsoconfig.create_l3direct_bgp_config(l3direct_bgp_info_dict)
                                        for l2ext_info_dict in l2ext_info_dict_list:
                                            if l2ext_info_dict["Service Name"] == encap_info_dict["Service Name"] and l2ext_info_dict["Encap Id"] == encap_info_dict["Encap Id"]:
                                                output += nsoconfig.create_l2ext_config(l2ext_info_dict)

    config_file = "NSO_CONFIG_{}.txt".format(file_name.strip("xlsx"))
    with open(config_file, "w") as f:
        f.write(output)


if __name__ == "__main__":
    nso_config(file_name="29 Nisan Anadolu_Ajansi ve Adalet_kalkinma Gebze SOL1_services_limited.xlsx")
