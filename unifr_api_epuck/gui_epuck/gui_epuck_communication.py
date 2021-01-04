from tkinter import Label, Frame, Tk, Menu, BOTH
from unifr_api_epuck import host_epuck_communication as hec
from threading import Thread
from multiprocessing.managers import SyncManager
import socket
import os
import time
import sys

SyncManager.register("syncdict")
SyncManager.register("lock")

#############
#   GUI     #
#############


class MonitorCommunication(Frame):
    """
        Frame tkinter Object to display the pending messages of each epuck
    """

    def __init__(self, master, ip_addr, pid_name, **kwargs):
        Frame.__init__(self, master, **kwargs)

        menu = Menu(self.master)
        master.config(menu=menu)

        self.pack(fill=BOTH)
        Label(self, text=f"Hosting on network : {ip_addr}").pack()
        Label(self, text=f"running on Process ID {pid_name}").pack()

        self.list_labels = []
        self.is_alive = True
        # communication
        self.manager = None
        self.label_online = Label(self, text="OFFLINE", fg='red')
        self.label_online.pack()

    def open_camera_monitor(self):
        Thread(target=os.system, args=("python3 gui_epuck_camera.py",)).start()

    def init_communication(self, host_ip='localhost'):
        """
        .. attention:: Requires host_epuck_communication.py

        Initiate the communication between host and Monitor.

        Firstly it creates host server if does not exists yet.
        Secondly Monitor connects to host
        """
        is_online = 1

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            is_online = sock.connect_ex((host_ip, 50000))
        except Exception as e:
            Label(text=e, fg='red').pack()
            print(e)

        if not is_online == 0:
            try:
                print('    starting server', end=" "),
                self.host = Thread(
                    target=hec.start_manager_gui, args=(host_ip,))
                self.host.start()
                animation = "|/-\\"
                for i in range(25):
                    time.sleep(0.1)
                    sys.stdout.write("\r" + animation[i % len(animation)])
                    sys.stdout.flush()
                    # do something

            except Exception as e:
                Label(text=e, fg='red').pack()
                print(e)

        # connecting to host manager
        try:
            # connect to host ip
            self.manager = SyncManager((host_ip, 50000), authkey=b"abc")
            self.manager.connect()
            print('Monitor CONNECTED to host IP!')
            self.label_online.destroy()
            self.label_online = Label(self, text="ONLINE", fg='green', pady=20)
            self.label_online.pack()

            # get shared proxy instance of host manager
            self.lock = self.manager.lock()
            self.syncdict = self.manager.syncdict()

        except Exception as e:
            Label(text=e, fg='red').pack()
            print(e)

    def update_monitor_communication(self):
        try:
            if self.is_alive:
                self.lock.acquire()
                tmp_dict = self.syncdict.copy()

                for label in self.list_labels:
                    label.destroy()

                for an_epuck in tmp_dict:
                    text = an_epuck + " has " + \
                        str(len(tmp_dict[an_epuck])) + " messages pending."
                    a_label = Label(self, text=f"{text}")
                    a_label.pack()
                    self.list_labels.append(a_label)

                self.lock.release()
                self.after(1000, self.update_monitor_communication)

        except Exception as e:
            self.is_alive = False
            Label(text=e, fg='red').pack()
            print(e)


def open_window_communication(ip_addr, pid_name):
    """
        Parameter of the window app 
    """
    root = Tk()
    root.title("Monitor Host Communication")
    root.geometry("500x400")
    monitor = MonitorCommunication(root, ip_addr, pid_name)
    monitor.init_communication(ip_addr)
    monitor.after(1000, monitor.update_monitor_communication)
    monitor.mainloop()


def main(ip_addr, pid_name=None):
    #check if ip_addr exist and remove spaces
    if not ip_addr or ip_addr == '':
        ip_addr = 'localhost'
    if not pid_name:
        pid_name = os.getpid()

    open_window_communication(ip_addr, pid_name)


if __name__ == "__main__":
    ip_addr = 'localhost'
    pid_name = None
    """
    if arguments in the command line --> IRL
    leave empy if using Webots
    """

    if len(sys.argv) == 2:
        ip_addr = sys.argv[1]

    if len(sys.argv) == 3:
        pid_name = sys.argv[2]

    main(ip_addr, pid_name)
