import requests
import urllib3
import json
import nso_helpers as helpers


class Nso:

    def __init__(self, protocol="https", host="127.0.0.1", port="8888", username="admin", password="xVGS6vNHJPx4ngzu", fabric_condition="", disable_warnings=True, cert_verify=False):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.verify = cert_verify
        self.fabric_condition = fabric_condition
        self.url = f"{protocol}://{host}:{port}/jsonrpc"
        self.cookies_string = None
        self.th_id = None
        self.service_dclan_xpath_list = []
        self.port_pa_xpath_list = []
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

    def __create_port_pa_xpath_info_dict_list(self, fabric_condition):
        xpath_dclan = f"/acidc-core:acidc/acidc-core:tenants/acidc-pa:port/acidc-pa:pa[fabric='{fabric_condition}']"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "query", "params": {"context_node": "/acidc", "xpath_expr": xpath_dclan, "selection": ["../../tenant", "name"], "result_as": "keypath-value", "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        response_dict = json.loads(response)
        self.port_pa_xpath_list = helpers.query_port_pa_fabric_conditional_helper(response_dict)

        return self.port_pa_xpath_list

    def __create_service_xpath_info_dict_list(self, fabric_condition):
        xpath_dclan = f"/acidc-core:acidc/acidc-core:tenants/acidc-services:service/acidc-services:dclan[fabric='{fabric_condition}']"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "query", "params": {"context_node": "/acidc", "xpath_expr": xpath_dclan, "selection": ["../../tenant", "name"], "result_as": "keypath-value", "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        response_dict = json.loads(response)
        self.service_dclan_xpath_list = helpers.query_service_dclan_fabric_conditional_helper(response_dict)

        return self.service_dclan_xpath_list

    def __run_action_touch(self, path):
        xpath = f"{path}/touch"
        payload = {"jsonrpc": "2.0", "id": 1, "method": "run_action", "params": {"params": {}, "path": xpath, "th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        print(f"Touch {path}:{response}")

    def run_action_touch(self):
        [self.__run_action_touch(xpath) for xpath in self.__create_service_xpath_info_dict_list(self.fabric_condition)]
        [self.__run_action_touch(xpath) for xpath in self.__create_port_pa_xpath_info_dict_list(self.fabric_condition)]

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
        file_name = "NSO_POSTCHECK_{}.txt".format(self.fabric_condition)
        with open(file_name, "w") as f:
            f.write(output)

    def commit_nonetworking(self):
        payload = {"jsonrpc": "2.0", "id": 1, "method": "commit", "params": {"th": self.th_id, "flags": ["no-networking"]}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        print(f"Commit No-Networking:{response}")

    def commit(self):
        payload = {"jsonrpc": "2.0", "id": 1, "method": "commit", "params": {"th": self.th_id}}
        req = requests.post(self.url, cookies=self.cookies_string, json=payload, verify=self.verify)
        response = req.text
        print(f"Commit:{response}")


if __name__ == "__main__":
    nso = Nso(host="10.220.2.234", fabric_condition="ank-aci-ict-fabric-1")
    nso.cookies()
    nso.start_new_read_write_transaction()
    nso.run_action_touch()
    nso.validate_commit()
    nso.commit_nonetworking()
