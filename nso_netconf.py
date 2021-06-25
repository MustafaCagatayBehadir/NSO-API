from ncclient import manager
from xml.etree import ElementTree as ET


class Nso_Netconf:

    def __init__(self, host, port="2022", username="admin", password="Tellcom123!"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.tenant_list = []

    def capabilities(self):
        with manager.connect(host=self.host, port=self.port, username=self.username, password=self.password, hostkey_verify=False, look_for_keys=False) as m:
            print("Here are the NETCONF capabilities")
            for capability in m.server_capabilities:
                print(capability)

    def get_config(self):
        with manager.connect(host=self.host, port=self.port, username=self.username, password=self.password, timeout=180, hostkey_verify=False, look_for_keys=False) as m:
            rpc_reply = m.get_config(source="running", filter=("xpath", "/acidc/tenants")).data_xml
            print(rpc_reply)

    def get_tenants(self):
        with manager.connect(host=self.host, port=self.port, username=self.username, password=self.password, timeout=180, hostkey_verify=False, look_for_keys=False) as m:
            rpc_reply = m.get(filter=("xpath", "/acidc/tenants/tenant")).data_xml
            root = ET.fromstring(rpc_reply)
            for tenant in root.iter("{http://tr/com/turkcell/acidc/acidc-core}tenant"):
                self.tenant_list.append(tenant.text)

        return self.tenant_list

    def __delete_tenant(self, tenant):
        payload = f"""<?xml version='1.0' encoding='UTF-8'?>
        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
          <acidc xmlns="http://tr/com/turkcell/acidc/acidc-core">
            <tenants nc:operation="delete">
              <tenant>{tenant}</tenant>
            </tenants>
          </acidc>
        </config>"""
        with manager.connect(host=self.host, port=self.port, username=self.username, password=self.password, timeout=180, hostkey_verify=False, look_for_keys=False) as m:
            try:
                response = m.edit_config(target='running', config=payload).xml
                print(f"Delete Tenant {tenant}: {response}")
            except Exception as e:
                print(f"Error: {e}")

    def delete_tenants(self):
        [self.__delete_tenant(tenant) for tenant in self.get_tenants()]


if __name__ == "__main__":
    netconf = Nso_Netconf(host="10.211.101.213")
    # netconf.capabilities()
    # netconf.get_config()
    # print(netconf.get_tenants())
    netconf.delete_tenants()
