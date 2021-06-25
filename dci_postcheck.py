from dci import Dci


def postcheck():
    tenant_list = input("Tenant Listesini Giriniz:").split(",")
    dci = Dci(file_name="Extranet_FW_26.05.2021_V3.xlsx", host="10.214.61.10", tenant_list=tenant_list)
    dci.netmiko_dci()
    dci.create_arp_postcheck()
    dci.create_route_postcheck()
    dci.create_static_route_postcheck()
    dci.create_bgp_route_postcheck()
    dci.create_mac_address_postcheck()
    dci.create_interface_statistics_postcheck()
    dci.write_excel()
    dci.disconnect()


if __name__ == "__main__":
    postcheck()
