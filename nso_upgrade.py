from xml.etree import ElementTree as Et
import requests
import urllib3
import json
import nso_helpers as helpers


def create_service_xpath_info_dict_list(filename):
    tree = Et.parse(filename)
    root = tree.getroot()
    service_xpath_list = []
    for sect3 in root.iter("{http://docbook.org/ns/docbook}sect3"):
        title = sect3.find("{http://docbook.org/ns/docbook}title")
        if "/" in title.text and "Details" not in title.text:
            if title.text not in service_xpath_list:
                service_xpath_list.append(title.text)

    return service_xpath_list


class Nso:

    def __init__(self, protocol="https", host="127.0.0.1", port="8888", username="admin", password="Tellcom123!", disable_warnings=True, cert_verify=False, file_name=None):
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
        self.delete_tenant_list = []
        if disable_warnings:
            urllib3.disable_warnings()

    def cookies(self):
        auth = {"jsonrpc": "2.0", "id": 1, "method": "login", "params": {"user": self.username, "passwd": self.password}}
        authenticate = requests.post(self.url, json=auth, verify=self.verify)
        self.cookies_string = authenticate.cookies
        print(self.cookies_string)

    def start_new_read_write_transaction(self):
        payload = {"jsonrpc": "2.0", "id": 1, "method": "new_trans", "params": {"db": "running", "mode": "read_write"}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        self.th_id = json.loads(response)["result"]["th"]
        print(f"New Read WriteTransaction:{response}")

    def __create_tenant_info_list(self):
        xpath = "/acidc/tenants"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "query", "params": {"context_node": "/acidc", "xpath_expr": xpath,
                   "selection": ["tenant"], "result_as": "keypath-value", "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        response_dict = json.loads(response)
        print(response_dict)
        self.delete_tenant_list = helpers.query_tenant_helper(response_dict)

        return self.delete_tenant_list

    def __delete_tenant(self, tenant_name):
        xpath = f"/acidc/tenants{{{tenant_name}}}"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "delete", "params": {"th": self.th_id, "path": xpath}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        print(f"Delete Tenant {tenant_name}:{response}")

    def delete_tenant_with_commit(self):
        for tenant_name in self.__create_tenant_info_list():
            nso.start_new_read_write_transaction()
            nso.__delete_tenant(tenant_name)
            nso.validate_commit()
            nso.commit()

    def __run_action_touch(self, path):
        xpath = f"{path}/touch"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "run_action", "params": {"params": {}, "path": xpath, "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        print(f"Touch {path}:{response}")

    def run_action_touch(self):
        [self.__run_action_touch(xpath) for xpath in create_service_xpath_info_dict_list(self.file_name)]

    def __create_bgp_info_dict_list(self):
        bgp_info_dict_list = []
        xpath = "/acidc/tenants/service/dclan/bd/epg/encap/l3direct/bgp/neighbor"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "query", "params": {"context_node": "/acidc", "xpath_expr": xpath,
                   "selection": ["../../../../../../../../tenant", "../../../../../../name", "../../../../../../fabric", "../../../../../vrf", "../../../../../name", "../../../../name", "../../../dot1q", "../../name", "ipv4_addr"], "result_as": "keypath-value", "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        response_dict = json.loads(response)
        bgp_info_dict_list.extend(helpers.query_l3direct_bgp_neighbor_helper(response_dict))
        i = 0
        for bgp_info_dict in bgp_info_dict_list:
            xpath = f"/acidc/tenants[tenant='{bgp_info_dict['TENANT NAME']}']/vrf[name='{bgp_info_dict['VRF NAME']}']/vrf-type"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "query", "params": {"context_node": "/acidc", "xpath_expr": xpath,
                       "selection": ["current()"], "result_as": "keypath-value", "th": self.th_id}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            response_dict = json.loads(response)
            bgp_info_dict["VRF TYPE"] = helpers.query_l3direct_bgp_neighbor_vrf_helper(response_dict)
            xpath = f"/acidc/tenants{{{bgp_info_dict['TENANT NAME']}}}/service/dclan{{{bgp_info_dict['SERVICE NAME']}}}/bd{{{bgp_info_dict['BD NAME']}}}/epg{{{bgp_info_dict['EPG NAME']}}}/encap{{{bgp_info_dict['ENCAP ID']}}}/l3direct/bgp/neighbor{{{bgp_info_dict['BGP NEIGHBOR ADDRESS']}}}"
            payload = {"jsonrpc": "2.0", "id": 1, "method": "show_config", "params": {"th": self.th_id, "path": xpath, "result_as": "json2", "with_oper": True}}
            req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
            response = req.text
            response_dict = json.loads(response)
            bgp_policy = helpers.query_l3direct_bgp_neighbor_policy_helper(response_dict)
            bgp_info_dict["INBOUND POLICY"] = bgp_policy[0]
            bgp_info_dict["OUTBOUND POLICY"] = bgp_policy[1]
            bgp_info_dict_list[i] = bgp_info_dict
            i += 1

        return bgp_info_dict_list

    def create_bgp_dci_check_file(self, nso_name):
        helpers.dci_check_to_file_helper(self.__create_bgp_info_dict_list(), nso_name)

    def validate_commit(self):
        payload = {"jsonrpc": "2.0", "id": 1, "method": "validate_commit", "params": {"th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        print(f"Validate Commit:{response}")

    def commit_dryrun(self):
        payload = {"jsonrpc": "2.0", "id": 1, "method": "commit", "params": {"th": self.th_id, "flags": ["dry-run=cli"]}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        print(f"Commit Dry-Run:{response}")
        response_dict = json.loads(response)
        output = helpers.commit_dryrun_helper(response_dict)
        file_name = "NSO_POSTCHECK_{}.txt".format(self.file_name.strip(".xlsx"))
        with open(file_name, "w") as f:
            f.write(output)

    def commit(self):
        payload = {"jsonrpc": "2.0", "id": 1, "method": "commit", "params": {"th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        print(f"Commit:{response}")


if __name__ == "__main__":
    nso = Nso(host="10.211.101.212")
    nso.cookies()
    nso.start_new_read_write_transaction()
    nso.delete_tenant_with_commit()
    # nso.create_bgp_dci_check_file(nso_name="gbz-ict-nso-01")
    # nso.run_action_touch()
    # nso.validate_commit()
    # nso.commit_dryrun()
    # nso.commit()
