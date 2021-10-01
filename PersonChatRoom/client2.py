import datetime

from threading import Thread
from tkinter import *
import socket

window = Tk()
window.geometry("600x400")
window.title("WeChat")
socket_TCP = None

lists_conversation = []
userlists = []

textip = None
textport = None
textusername = None
show_left = None
user_list_area = None
show_right = None
kill = True

def button_clickedd():
    global socket_TCP, userlists, kill
    host = textip.get()
    port = int(textport.get())
    socket_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_TCP.connect((host, port))
    socket_TCP.send(str("@@"+textusername.get()).encode())
    kill = True
    disbutton = Button(show_left, width=11, text="Dissconnect", background="tomato", command=button_clickedc)
    disbutton.place(x=75, y=280)

def button_clickedc():
    global socket_TCP, userlists, kill
    kill = False
    del userlists[:]
    removewindow()
    socket_TCP.close()
    user_list_area.place(x=0, y=0)
    disbutton = Button(show_left, width=11, text="Connection", background="cyan", command=button_clickedd)
    disbutton.place(x=75, y=280)

def tr():
    try:
        clint_speak = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + \
                      " " + textusername.get() + ": " + text.get()
        if clint_speak != "":
            socket_TCP.send(clint_speak.encode())
            showdialog()
    except:
        pass

def re():
    global lists_conversation, userlists, textusername, kill
    print("command is start!")
    while True:
        try:
            server_speak = socket_TCP.recv(32768)
            # print(str(server_speak, encoding='UTF-8'))
            for i in userlists:
                if i + "kill" == str(server_speak, encoding='UTF-8'):
                    userlists.remove(i)
                    refresh()
                    server_speak = None
                    continue
            # print(str(server_speak, encoding='UTF-8'))
            if str(server_speak, encoding='UTF-8') == "kill you!":
                button_clickedc()

            if "@@" in str(server_speak, encoding='UTF-8') and len(str(server_speak, encoding='UTF-8')) > 5:
                # print(str(server_speak, encoding='UTF-8'))
                if "leave the room" in str(server_speak, encoding='UTF-8'):
                    server_speak = str(server_speak, encoding='UTF-8')[2:]
                    lists_conversation.append(server_speak[:-3])
                    showdialog()
                    continue
                lists_conversation.append(str(server_speak, encoding='UTF-8')[3:])
                showdialog()
                continue

            if "@@" in str(server_speak, encoding='UTF-8') and str(server_speak, encoding='UTF-8')\
                    not in userlists and len(str(server_speak, encoding='UTF-8')) < 5 and kill == True:
                # print(str(server_speak, encoding='UTF-8'))
                userlists.append(str(server_speak, encoding='UTF-8'))
                deluserlists()
                refresh()
                # server_speak = None
                continue

            # print(str(server_speak, encoding='UTF-8'))

            if str(server_speak, encoding='UTF-8') != "" and "@@" not in str(server_speak, encoding='UTF-8') \
                    and server_speak != None:
                # print(kill)
                lists_conversation.append(str(server_speak, encoding='UTF-8'))
                showdialog()
                continue
        except:
            continue


def showdialog():
    global text
    conversation_list_area = Listbox(show_right, width=400, height=21, bd=3, background="gainsboro")
    for item in lists_conversation:
        conversation_list_area.insert(END, item)
    conversation_list_area.place(x=0, y=0)
    try:
        user_text_input = Entry(show_right, width=50, textvariable=text, bd=3, background="gainsboro")
        user_text_input.place(x=0, y=378)
        sendbutton = Button(show_right, width=6, text="send", command=tr)
        sendbutton.place(x=350, y=375)
        if text.get() != "":
            text.set("")
    except:
        print("showdialog except!")

def refresh():
    user_list_area = Listbox(show_left, width=200, height=10, background="gainsboro")
    for item in userlists:
        user_list_area.insert(END, item[2:])
    user_list_area.place(x=0, y=0)
    # print(userlists, kill)

def deluserlists():
    global kill
    if kill == False:
        del userlists[:]

#刷新初始界面
def removewindow():
    global textip, textport, textusername, show_left, show_right, user_list_area,\
        lists_conversation, userlists, socket_TCP

    socket_TCP = None
    lists_conversation = []
    userlists = []
    textip = None
    textport = None
    textusername = None
    show_left = None
    user_list_area = None
    show_right = None

    # left
    show_left = Frame(width=200, height=400, background="gainsboro")
    show_left.place(x=0, y=0)
    user_list_area = Listbox(show_left, width=200, height=10, bd=3, background="gainsboro")
    user_list_area.place(x=0, y=0)

    # ip input
    textip = StringVar()
    ip_text = Label(show_left, width=10, text='Server_IP', background="gainsboro")
    ip_text.place(x=-5, y=190)
    ip_text_input = Entry(show_left, width=17, textvariable=textip, background="gainsboro")
    ip_text_input.place(x=75, y=191)

    # port input
    textport = StringVar()
    port_text = Label(show_left, width=10, text='Server_Port', background="gainsboro")
    port_text.place(x=-5, y=220)
    port_text_input = Entry(show_left, width=17, textvariable=textport, background="gainsboro")
    port_text_input.place(x=75, y=221)

    # username input
    textusername = StringVar()
    username_text = Label(show_left, width=10, text='Username', background="gainsboro")
    username_text.place(x=-5, y=250)
    username_text_input = Entry(show_left, width=17, textvariable=textusername, background="gainsboro")
    username_text_input.place(x=75, y=251)

    # button
    disbutton = Button(show_left, width=11, text="Connection", background="cyan", command=button_clickedd)
    disbutton.place(x=75, y=280)

    # right
    show_right = Frame(width=400, height=400)
    show_right.place(x=200, y=0)
    showdialog()

text = StringVar()

#初始界面
removewindow()

# showdialog
showdialog()

if __name__ == "__main__":
    receive = Thread(target=re)
    receive.start()

window.mainloop()

