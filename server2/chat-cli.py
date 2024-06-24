import socket
import json
import base64
import json
import os
from chat import Chat
TARGET_IP = "172.31.83.217" # mesin 1
TARGET_PORT = 8890

class ChatClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP,TARGET_PORT)
        self.sock.connect(self.server_address)
        self.tokenid=""
    def proses(self,cmdline):
        j=cmdline.split(" ")
        try:
            command=j[0].strip()
            if (command=='auth'):
                username=j[1].strip()
                password=j[2].strip()
                return self.login(username,password)
            if (command=='register'):
                username=j[1].strip()
                password=j[2].strip()
                nama=j[3].strip()
                negara=j[4].strip()
                return self.register(username, password, nama, negara)
            elif (command=='addgroup'):
                groupname = j[1].strip()
                return self.add_group(groupname)
            elif (command=='joingroup'):
                groupname = j[1].strip()
                return self.join_group(groupname)
            elif (command=='send'):
                usernameto = j[1].strip()
                message=""
                for w in j[2:]:
                    message="{} {}" . format(message,w)
                return self.send_message(usernameto,message)
            elif (command=='sendfile'):
                usernameto = j[1].strip()
                filepath = j[2].strip()
                return self.send_file(usernameto,filepath)
            elif (command=='sendgroup'):
                groupname = j[1].strip()
                message=""
                for w in j[2:]:
                    message="{} {}" . format(message,w)
                return self.send_group_message(groupname,message)
            elif (command=='sendgroupfile'):
                groupname = j[1].strip()
                filepath = j[2].strip()
                return self.send_group_file(groupname,filepath)
            elif command == "addrealm":
                realmid = j[1].strip()
                realm_address = j[2].strip()
                realm_port = j[3].strip()
                return self.add_realm(realmid, realm_address, realm_port)

            elif command == "sendprivaterealm":
                realmid = j[1].strip()
                username_to = j[2].strip()
                message = ""
                for w in j[3:]:
                    message = "{} {}".format(message, w)
                return self.send_realm_message(realmid, username_to, message)

            elif command == "sendgrouprealm":
                realmid = j[1].strip()
                groupname = j[2].strip()
                message = ""
                for w in j[3:]:
                    message = "{} {}".format(message, w)
                return self.send_group_realm_message(realmid, groupname, message)

            elif command == "getrealminbox":
                realmid = j[1].strip()
                return self.realm_inbox(realmid)
            
            elif (command=='inbox'):
                return self.inbox()
            elif (command=='logout'):
                return self.logout()
            elif (command=='info'):
                return self.info()
            else:
                return "*Maaf, command tidak benar"
        except IndexError:
            return "-Maaf, command tidak benar"

    def sendstring(self,string):
        try:
            self.sock.sendall(string.encode())
            receivemsg = ""
            while True:
                data = self.sock.recv(1024)
                print("diterima dari server",data)
                if (data):
                    receivemsg = "{}{}" . format(receivemsg,data.decode())  #data harus didecode agar dapat di operasikan dalam bentuk string
                    if receivemsg[-4:]=='\r\n\r\n':
                        print("end of string")
                        return json.loads(receivemsg)
        except:
            self.sock.close()
            return { 'status' : 'ERROR', 'message' : 'Gagal'}

    def login(self,username,password):
        string="auth {} {} \r\n" . format(username,password)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=result['tokenid']
            return "username {} logged in, token {} " .format(username,self.tokenid)
        else:
            return "Error, {}" . format(result['message'])
    
    def register(self,username,password, nama, negara):
        string="register {} {} {} {}\r\n" . format(username,password, nama, negara)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=result['tokenid']
            return "username {} register in, token {} " .format(username,self.tokenid)
        else:
            return "Error, {}" . format(result['message'])

    def add_group(self, groupname):
        string="addgroup {} {} \r\n".format(self.tokenid, groupname)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "Group {} added".format(groupname)
    
    def join_group(self, groupname):
        string="joingroup {} {} \r\n".format(self.tokenid, groupname)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "Group {} added".format(groupname)

    def send_message(self,usernameto="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="send {} {} {} \r\n" . format(self.tokenid,usernameto,message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])
        
    def send_group_message(self,groupname="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="sendgroup {} {} {} \r\n" . format(self.tokenid,groupname,message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(groupname)
        else:
            return "Error, {}" . format(result['message'])
        

    def inbox(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inbox {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return "Error, {}" . format(result['message'])
        
    def add_realm(self, realmid, realm_address, realm_port):
        if self.tokenid == "":
            return "Error, not authorized"
        string = "addrealm {} {} {} \r\n".format(realmid, realm_address, realm_port)
        result = self.sendstring(string)
        if result["status"] == "OK":
            return "Realm {} added".format(realmid)
        else:
            return "Error, {}".format(result["message"])
        
    def send_realm_message(self, realmid, username_to, message):
        if self.tokenid == "":
            return "Error, not authorized"
        string = "sendprivaterealm {} {} {} {}\r\n".format(
            self.tokenid, realmid, username_to, message
        )
        result = self.sendstring(string)
        if result["status"] == "OK":
            return "Message sent to realm {}".format(realmid)
        else:
            return "Error, {}".format(result["message"])
        
    
    def send_group_realm_message(self, realmid, usernames_to, message):
        if self.tokenid == "":
            return "Error, not authorized"
        string = "sendgrouprealm {} {} {} {} \r\n".format(
            self.tokenid, realmid, usernames_to, message
        )

        result = self.sendstring(string)
        if result["status"] == "OK":
            return "message sent to group {} in realm {}".format(usernames_to, realmid)
        else:
            return "Error {}".format(result["message"])
        
    def realm_inbox(self, realmid):
        if self.tokenid == "":
            return "Error, not authorized"
        string = "getrealminbox {} {} \r\n".format(self.tokenid, realmid)
        print("Sending: " + string)
        result = self.sendstring(string)
        print("Received: " + str(result))
        if result["status"] == "OK":
            return "Message received from realm {}: {}".format(
                realmid, result["messages"]
            )
        else:
            return "Error, {}".format(result["message"])

    def logout(self):   
        string="logout {}\r\n".format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=""
            return "Logout Berhasil"
        else:
            return "Error, {}" . format(result['message'])

    def info(self):
        string="info \r\n"
        result = self.sendstring(string)
        list_user_aktif="User yang Aktif:\n"
        if result['status']=='OK':
            list_user_aktif += f"{result['message']}"
        return list_user_aktif

if __name__=="__main__":
    cc = ChatClient()
    c = Chat()

    # cc.proses("auth messi surabaya")
    # cc.proses("addrealm realm2 172.31.83.217 8890")
    # cc.proses("sendgrouprealm realm2 group:home halo")

    print("\n")
    print("List User: " + str(c.users.keys()) + " dan Passwordnya: " + str(c.users['messi']['password']) + ", " + str(c.users['henderson']['password']) + ", " + str(c.users['lineker']['password']))
    print("""\n
    Command 1 Server:\n\n
    1. Login: auth [username] [password]\n
    2. Register: register [username] [password] [nama (gunakan "_" untuk seperator) ] [negara]\n
    3. Buat group: addgroup [nama_group]\n
    4. Join group: joingroup [nama_group]\n
    5. Mengirim pesan private: send [username to] [message]\n
    7. Mengirim pesan ke group: sendgroup [nama_group] [message]\n
    9. Melihat pesan: inbox\n
    10. Logout: logout\n
    11. Melihat user yang aktif: info\n

    Command MultiRealm Server:\n\n
    12. Menambah realm: addrealm [nama_realm] [address] [port]\n
    13. Mengirim pesan ke realm: sendprivaterealm [name_realm] [username to] [message]\n
    14. Mengirim pesan ke group realm: sendgrouprealm [name_realm] [usernames to]/[group:][group_name] [message]\n
    15. Melihat pesan realm: getrealminbox [nama_realm]\n
    """)
    while True:
        cmdline = input("Command {}:" . format(cc.tokenid))
        print(cc.proses(cmdline))