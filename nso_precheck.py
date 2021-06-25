from nso import Nso


def nso_precheck():
    nso = Nso(host="10.214.50.233", file_name="29-30Haziran__1-2Temmuz__Gebze DC2 ICT_LAN_FW_LB_services_V4.xlsx")
    nso.cookies()
    nso.start_new_read_transaction()
    nso.precheck_tenant()
    nso.precheck_service()
    nso.precheck_port_pa()
    nso.precheck_vrf()
    nso.precheck_node_id(fabric="gbz-aci-ict-fabric-2")
    nso.precheck_l2ext(fabric="gbz-aci-ict-fabric-2")
    # nso.get_port_pa_with_conditions("HANADATA", "gbz-aci-sol-fabric-5-6")
    # nso.get_l3direct_bgp()
    nso.precheck_to_file()


if __name__ == "__main__":
    nso_precheck()
