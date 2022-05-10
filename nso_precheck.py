from nso import Nso


def nso_precheck():
    nso = Nso(host="10.169.86.237", file_name="Dataset.xlsx")
    nso.cookies()
    nso.start_new_read_transaction()
    nso.precheck_tenant()
    nso.precheck_service()
    nso.precheck_port_pa()
    nso.precheck_vrf()
    nso.precheck_node_id(fabric="mnd-aci-sol-fabric-1")
    nso.precheck_l2ext(fabric="mnd-aci-sol-fabric-1")
    # nso.get_port_pa_with_conditions("HANADATA", "gbz-aci-sol-fabric-5-6")
    # nso.get_l3direct_bgp()
    nso.precheck_to_file()


if __name__ == "__main__":
    nso_precheck()
