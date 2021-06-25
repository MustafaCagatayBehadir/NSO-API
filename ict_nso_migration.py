from nso import Nso


def nso_jsonrpc():
    nso = Nso(host="10.214.50.233", file_name="Gebze DC3 ICT Backup_services.v1.2.xlsx")
    nso.create_ict_pa_portgroups_info_dict_list()


if __name__ == "__main__":
    nso_jsonrpc()