import socket
import os
import json
import logging
from tkinter import *
from chat import Chat
from tkinter import filedialog

TARGET_IP = "127.0.0.1"
TARGET_PORT = 8889


class ChatClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP,TARGET_PORT)
        self.sock.connect(self.server_address)
        self.tokenid=""
        # Chat Window
        self.Window = Tk()
        self.Window.withdraw()

        # Login Winodw
        self.loginGUI = Toplevel()
        self.loginGUI.title("Login")
        self.loginGUI.resizable(width=False,
                                height=False)
        self.loginGUI.configure(width=400,
                                height=300)

        # Label Instruksi
        self.instruction = Label(self.loginGUI,
                                 text="Masukkan Username & Password",
                                 justify=CENTER,
                                 font="Helvetica 12 bold")
        self.instruction.place(relheight=0.15,
                               relx=0.15,
                               rely=0.07)

        # Label Username & Password
        self.labelUsername = Label(self.loginGUI,
                                   text="Username: ",
                                   font="Helvetica 12")
        self.labelUsername.place(relheight=0.2,
                                 relx=0.1,
                                 rely=0.25)
        self.labelPassword = Label(self.loginGUI,
                                   text="Password",
                                   font="Helvetica 12")

        self.labelPassword.place(relheight=0.2,
                                 relx=0.1,
                                 rely=0.4)

        # Input Username
        self.inputUsername = Entry(self.loginGUI,
                                   font="Helvetica 14")
        self.inputUsername.place(relwidth=0.5,
                                 relheight=0.1,
                                 relx=0.3,
                                 rely=0.3)
        self.inputPassword = Entry(self.loginGUI,
                                   font="Helvetica 14")
        self.inputPassword.place(relwidth=0.5,
                                 relheight=0.1,
                                 relx=0.3,
                                 rely=0.45)
        self.inputUsername.focus()

        # Button Login
        self.enter = Button(self.loginGUI,
                            text="Login",
                            font="Helvetica 14 bold",
                            command=lambda: self.proses(
                                "auth" + " " + self.inputUsername.get() + " " + self.inputPassword.get())
                            )
        self.enter.place(relx=0.38,
                         rely=0.65)
        self.Window.mainloop()
    def proses(self,cmdline):
        j=cmdline.split(" ")
        try:
            command=j[0].strip()
            if (command=='auth'):
                username=j[1].strip()
                password=j[2].strip()
                return self.login(username,password)
            elif (command=='send'):
                usernameto = j[1].strip()
                message=""
                for w in j[2:]:
                    message="{} {}" . format(message,w)
                return self.sendmessage(usernameto,message)
            elif (command=='inbox'):
                return self.inbox()
            else:
                return "*Maaf, command tidak benar"
        except IndexError:
                return "-Maaf, command tidak benar"
    def sendstring(self,string):
        try:
            self.sock.sendall(string.encode())
            receivemsg = ""
            while True:
                data = self.sock.recv(64)
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
            self.loginGUI.destroy()
            self.layout(username)
            return "username {} logged in, token {} " .format(username,self.tokenid)
        else:
            return "Error, {}" . format(result['message'])
    def sendmessage(self,usernameto="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="send {} {} {} \r\n" . format(self.tokenid,usernameto,message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])
    def inbox(self):
        hasil={}
        pesan={}
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inbox {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':

            for name in result['messages'].keys():
                user = name

                countpesan = len([jmlpesan for jmlpesan in result['messages'][user] if isinstance(jmlpesan, dict)])

                pesan[user]=[]
                for i in range(countpesan):
                    hasil = result['messages'][user][i]['msg']
                    pesan[user].append(hasil)
                
                if not pesan[user]:
                    continue
                else:
                    self.textCons.config(state=NORMAL)
                    for key in pesan[user]:
                        pesan_user = key
                    pesan_user = pesan_user[2:-3]
                    self.textCons.insert(END, user+": "+format(json.dumps(pesan_user))+ "\n")
                    self.textCons.config(state=DISABLED)
                    self.textCons.see(END)    

            return "{}" . format(json.dumps(result['messages']))
        else:            
            return "Error, {}" . format(result['message'])
    def layout(self, name):
        self.name = name
        chatcli = Chat()

        # to show chat window
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=False,
                              height=False)
        self.Window.configure(width=650,
                              height=650,
                              bg="#17202A")
        self.labelHead = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               text=self.name,
                               font="Helvetica 13 bold",
                               pady=5)

        self.labelHead.place(relwidth=1)
        self.line = Label(self.Window,
                          width=450,
                          bg="#ABB2B9")

        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=0.012)

        self.textCons = Text(self.Window,
                             width=20,
                             height=2,
                             bg="#17202A",
                             fg="#EAECEE",
                             font="Helvetica 14",
                             padx=5,
                             pady=5)

        self.textCons.place(relheight=0.745,
                            relwidth=1,
                            relx=0.4,
                            rely=0.08)

        #listbox User
        self.userListbox = Listbox(self.Window,
                                   font="Helvetica 15")
        for key in chatcli.users.keys():
            if self.name==key:
                continue
            else:
                self.userListbox.insert(END, key)

        self.userListbox.place(relwidth=0.4,
                               relheight=0.745,
                               rely=0.08)

        self.userListbox.insert(END,"group")
        #Selecting User with DoubleClick
        def select(event):
            self.sendTo = self.userListbox.get(ANCHOR)

        self.userListbox.bind("<Double-1>",select)

        self.buttonInbox = Button(self.Window,
                                text="Inbox",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.proses("inbox"))

        self.buttonInbox.place(relx=0.08,
                                rely=0.4,
                                relheight=0.06,
                                relwidth=0.22)
        
        def browsefiles():
            self.filename = filedialog.askopenfilename(initialdir = "/",
                                                 title = "Select a File",
                                                filetypes = (("JPG",
                                                        "*.jpg*"),
                                                       ("JPG",
                                                        "*.*")))
            x=self.filename.split("/")
            self.filenamesplit=x[-1].strip()
            self.labelImage.configure(text=self.filenamesplit)

        self.buttonImage = Button(self.Window,
                                text="Image",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=browsefiles)

        self.buttonImage.place(relx=0.08,
                                rely=0.5,
                                relheight=0.06,
                                relwidth=0.22)

        self.buttonSendImage = Button(self.Window,
                                text="Send",
                                font="Helvetica 10 bold",
                                width=10,
                                bg="#ABB2B9",
                                command=lambda: Chat.send_file(self.tokenid,self.name,self.sendTo,self.filenamesplit))
                                                #self.proses("send-image"+" "+self.sendTo+" "+self.filenameSplit))

        self.buttonSendImage.place(relx=0.13,
                                rely=0.6,
                                relheight=0.06,
                                relwidth=0.12)

        self.labelImage = Label(self.userListbox,
                                text="",
                                bg="white",
                                 height=5,
                                 font="Helvetica 13 bold")

        self.labelImage.place(relwidth=1,
                               rely=0.8)

        self.labelBottom = Label(self.Window,
                                 bg="#ABB2B9",
                                 height=80)

        self.labelBottom.place(relwidth=1,
                               rely=0.825)

        self.entryMsg = Entry(self.labelBottom,
                              bg="#2C3E50",
                              fg="#EAECEE",
                              font="Helvetica 13")

        # place the given widget
        # into the gui window
        self.entryMsg.place(relwidth=0.74,
                            relheight=0.06,
                            rely=0.008,
                            relx=0.011)

        self.entryMsg.focus()

        # create a Send Button
        self.buttonMsg = Button(self.labelBottom,
                                text="Send",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.proses("send"+" "+ self.sendTo+" "+self.entryMsg.get()))

        self.buttonMsg.place(relx=0.77,
                             rely=0.008,
                             relheight=0.06,
                             relwidth=0.22)

        self.textCons.config(cursor="arrow")

        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)

        # place the scroll bar
        # into the gui window
        scrollbar.place(relheight=1,
                        relx=0.974)

        scrollbar.config(command=self.textCons.yview)


if __name__=="__main__":
    cc = ChatClient()
    #while True:
    #    cmdline = input("Command {}:" . format(cc.tokenid))
    #    print(cc.proses(cmdline))

