from netmiko import Netmiko
from time import sleep
import pandas as pd
import dci_helpers as helpers


class Dci:

    def __init__(self, file, username, password):
        self.file = file
        self.username = username
        self.password = password
        self.output = ""
        self.df = pd.read_excel(file)
        self.device_list = []
        self.bgp_session_status_command_list = []

    def __create_bgp_session_status_command_data_frame(self):
        self.df.loc[:, "DCI IP"] = pd.Series("", index=self.df.index)
        self.df.loc[:, "COMMAND_1"] = pd.Series("", index=self.df.index)
        self.df.loc[:, "COMMAND_2"] = pd.Series("", index=self.df.index)
        self.df.loc[:, "COMMAND_3"] = pd.Series("", index=self.df.index)
        for index in self.df.index.values:
            if self.df.loc[index]["FABRIC"] == "gbz-aci-sol-fabric-1-2":
                self.df.loc[index, "DCI IP"] = "10.214.61.10"
            elif self.df.loc[index]["FABRIC"] == "gbz-aci-sol-fabric-3-4":
                self.df.loc[index, "DCI IP"] = "10.224.61.10" if self.df.loc[index]["L3DIRECT NAME"] == "BLF_801_802_DCI_VPC_INTPOL" else "10.224.62.10"
            elif self.df.loc[index]["FABRIC"] == "gbz-aci-sol-fabric-5-6":
                self.df.loc[index, "DCI IP"] = "10.102.225.10" if self.df.loc[index]["L3DIRECT NAME"] == "BLF_801_802_DCI_VPC_INTPOL" else "10.102.226.10"
            else:
                self.df.loc[index, "DCI IP"] = "10.102.223.10"
            if self.df.loc[index]["VRF TYPE"] == "private":
                self.df.loc[index, "COMMAND_1"] = f"show bgp vrf {self.df.loc[index]['VRF NAME']} ipv4 unicast neighbor {self.df.loc[index]['BGP NEIGHBOR ADDRESS']}"
                self.df.loc[index, "COMMAND_2"] = f"show bgp vrf {self.df.loc[index]['VRF NAME']} ipv4 unicast neighbor {self.df.loc[index]['BGP NEIGHBOR ADDRESS']} advertised-routes"
                self.df.loc[index, "COMMAND_3"] = f"show bgp vrf {self.df.loc[index]['VRF NAME']} ipv4 unicast neighbor {self.df.loc[index]['BGP NEIGHBOR ADDRESS']} received routes"
                self.df.loc[index, "COMMAND_4"] = f"show bgp vrf {self.df.loc[index]['VRF NAME']} ipv4 unicast"
            else:
                self.df.loc[index, "COMMAND_1"] = f"show bgp ipv4 unicast neighbor {self.df.loc[index]['BGP NEIGHBOR ADDRESS']}"
                self.df.loc[index, "COMMAND_2"] = f"show bgp ipv4 unicast neighbor {self.df.loc[index]['BGP NEIGHBOR ADDRESS']} advertised-routes"
                self.df.loc[index, "COMMAND_3"] = f"show bgp ipv4 unicast neighbor {self.df.loc[index]['BGP NEIGHBOR ADDRESS']} received routes"
                self.df.loc[index, "COMMAND_4"] = ""
        [self.device_list.append(self.df.loc[index]["DCI IP"]) for index in self.df.index.values if self.df.loc[index]["DCI IP"] not in self.device_list]

        return self.device_list

    def __open_netmiko_session(self, device):
        try:
            dci = {"device_type": "cisco_xr", "ip": device, "username": "DNSERVICES_RO", "password": "VRTat635"}
            self.net_connect = Netmiko(**dci)
            print(f"{device} ; CONNECTION ESTABLISHED")
        except Exception as err:
            raise Exception(err)

    def create_bgp_check_data_frame(self):
        self.df.loc[:, "BGP SESSION STATE"] = pd.Series("", index=self.df.index)
        self.df.loc[:, "ACCEPTED ROUTES COUNT"] = pd.Series("", index=self.df.index)
        self.df.loc[:, "BESTPATH ROUTES COUNT"] = pd.Series("", index=self.df.index)
        self.df.loc[:, "ADVERTISED ROUTES COUNT"] = pd.Series("", index=self.df.index)
        for device in self.__create_bgp_session_status_command_data_frame():
            self.output += "\n\n" + f"##################################################{device}##################################################"
            self.__open_netmiko_session(device)
            for index in self.df.index.values:
                if self.df.loc[index]["DCI IP"] == device:
                    output_1 = self.net_connect.send_command(self.df.loc[index]["COMMAND_1"])
                    print(self.df.loc[index]["COMMAND_1"])
                    print(output_1)
                    self.output += "\n\n" + self.df.loc[index]["COMMAND_1"]
                    self.output += "\n" + output_1
                    sleep(1)
                    output_2 = self.net_connect.send_command(self.df.loc[index]["COMMAND_2"])
                    print(self.df.loc[index]["COMMAND_2"])
                    print(output_2)
                    self.output += "\n\n" + self.df.loc[index]["COMMAND_2"]
                    self.output += "\n" + output_2
                    sleep(1)
                    output_3 = self.net_connect.send_command(self.df.loc[index]["COMMAND_3"])
                    print(self.df.loc[index]["COMMAND_3"])
                    print(output_3)
                    self.output += "\n\n" + self.df.loc[index]["COMMAND_3"]
                    self.output += "\n" + output_3
                    sleep(1)
                    self.output += self.df.loc[index]["COMMAND_4"] if self.df.loc[index]["COMMAND_4"] is not None else ""
                    output_4 = self.net_connect.send_command(self.df.loc[index]["COMMAND_4"]) if self.df.loc[index]["COMMAND_4"] is not None else ""
                    if output_4 != "":
                        print(self.df.loc[index]["COMMAND_4"])
                        print(output_4)
                        self.output += "\n\n" + self.df.loc[index]["COMMAND_4"]
                        self.output += "\n" + output_4
                    sleep(1)
                    bgp_parser_tuple = helpers.netmiko_bgp_neighbor_session_parser(output_1.splitlines(), output_2.splitlines())
                    self.df.loc[index, "BGP SESSION STATE"] = bgp_parser_tuple[0]
                    self.df.loc[index, "ACCEPTED ROUTES COUNT"] = bgp_parser_tuple[1]
                    self.df.loc[index, "BESTPATH ROUTES COUNT"] = bgp_parser_tuple[2]
                    self.df.loc[index, "ADVERTISED ROUTES COUNT"] = bgp_parser_tuple[3]
            self.net_connect.disconnect()

    def write_files(self, ispre=False):
        file = "{}_Precheck.xlsx".format(self.file.strip(".xlsx")) if ispre else "{}_Postcheck.xlsx".format(self.file.strip(".xlsx"))
        self.df.drop(columns=["DCI IP", "COMMAND_1", "COMMAND_2", "COMMAND_3", "COMMAND_4"], inplace=True)
        with pd.ExcelWriter(file) as writer:
            self.df.to_excel(writer, index=False)
        file = "{}_Command_Outputs_Precheck.txt".format(self.file.strip(".xlsx")) if ispre else "{}_Command_Outputs_Postcheck.txt".format(self.file.strip(".xlsx"))
        with open(file, "w") as f:
            f.write(self.output)


def dci_check():
    dci = Dci(file="DCI_CHECK_gbz-ict-nso-01.xlsx", username="DNSERVICES_RO", password="VRTat635")
    dci.create_bgp_check_data_frame()
    dci.write_files(ispre=False)


if __name__ == "__main__":
    dci_check()
