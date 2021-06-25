from nso import Nso


def nso_jsonrpc():
    nso = Nso(host="10.214.50.233", file_name="Gebze DC3 ICT Backup_services.v1.2.xlsx")
    nso.cookies()
    nso.start_new_read_write_transaction()
    # nso.create_tenants()
    # nso.create_services()
    # nso.create_vrfs()
    # nso.create_bds()
    # nso.create_epgs()
    # nso.create_encaps()
    nso.create_pas()
    nso.create_tenant_pas()
    # nso.create_prefix_lists()
    # # nso.create_l3directs()
    # nso.create_l3direct_statics()
    # nso.create_l3direct_ospfs()
    # nso.create_l3direct_bgps()
    # nso.create_l2externals()
    # nso.create_transit_leaf_tenant_pas(tenant_pa_name=None)
    # nso.create_pa_portgroups(tenant="GBZ3B-Backup", dc_id="3B")
    # nso.create_tenant_pa_portgroups(tenant=None, dc_id=None)
    # nso.remove_tenant_pas()
    # nso.remove_port_pas()
    # nso.remove_services()
    nso.validate_commit()
    nso.get_transaction_change(devices_list=[])
    # nso.commit_nonetworking()
    nso.commit()


if __name__ == "__main__":
    nso_jsonrpc()