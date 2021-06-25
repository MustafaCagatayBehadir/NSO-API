import paramiko
from time import sleep


class Sso:

    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password
        self.shell = None
        self.buff = ""

    def connect(self):
        conn = paramiko.SSHClient()
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conn.connect(self.ip, port=2222, username=self.username, password=self.password, look_for_keys=False)
        self.shell = conn.invoke_shell()
        self.buff = ""
        while not("Type to search or select one:" in self.buff):
            self.buff += self.shell.recv(65535).decode()
        print(self.buff)

    def connect_dci(self, cmd):
        self.shell.send(cmd + "\r\n")
        self.buff = ""
        while not("#" in self.buff):
            self.buff += self.shell.recv(65535).decode()
        print(self.buff)
