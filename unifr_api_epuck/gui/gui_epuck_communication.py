from tkinter import Label, Frame, Tk, Menu, Entry, Button, Toplevel, ttk
from tkinter.constants import BOTTOM, BOTH, LEFT
from threading import Thread
from multiprocessing.managers import SyncManager
import socket
import os
import time
import sys
from ..communication.host_communication import start_manager_gui, get_available_clients

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
        Label(self, text="Hosting on network " + ip_addr).pack()

        self.list_labels = []
        self.is_alive = True

        # communication
        self.manager = None
        self.label_online = Label(self, text="OFFLINE", fg='red')
        self.label_online.pack()
        self.timelock = 4

        #reset buttons
        # top bar menu
        menu = Menu(self.master)
        master.config(menu=menu)
        file_menu = Menu(menu)
        file_menu.add_command(label='Reset Messages', command=self.reset_host)
        file_menu.add_command(label='Reset Locker', command=self.reset_lock)

        menu.add_cascade(label="Reset", menu=file_menu)



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
            sock.settimeout(5)
            is_online = sock.connect_ex((host_ip, 50000))
            
        except Exception as e:
            self.is_alive = False
            Label(text=e, fg='red').pack()
            print(e)


        if self.is_alive:
            if not is_online == 0:
                
                try:
                    print('    starting server', end=" "),
                    self.host = Thread(
                        target=start_manager_gui, args=(host_ip,))
                    self.host.start()
                    animation = "|/-\\"
                    for i in range(25):
                        time.sleep(0.1)
                        sys.stdout.write("\r" + animation[i % len(animation)])
                        sys.stdout.flush()

                except Exception as e:
                    Label(text=e, fg='red').pack()
                    print(e)
            

            # connecting to host manager
            try:

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                is_online = sock.connect_ex((host_ip, 50000))

                if is_online == 0:
                    # connect to host ip
                    self.is_alive = True
                    self.manager = SyncManager((host_ip, 50000), authkey=b"abc")
                    self.manager.connect()
                    print('Monitor CONNECTED to host IP!')
                    self.label_online.destroy()
                    self.label_online = Label(self, text="ONLINE", fg='green', pady=20)
                    self.label_online.pack()

                    # get shared proxy instance of host manager
                    self.lock = self.manager.lock()
                    self.syncdict = self.manager.syncdict()
                else:
                    self.is_alive = False

            except Exception as e:
                self.is_alive = False
                Label(text=e, fg='red').pack()


            sock.settimeout(None)

        
        #add input text to send message
        self.message_frame = Frame(self)

        #list of available Epucks to send messages
        if self.is_alive:
            is_locked = self.lock.acquire(timeout=self.timelock)
            if is_locked:
                tmp_dict = self.syncdict.copy()
            
                self.available_epucks = get_available_clients(tmp_dict['connected'])
                self.cmb_available_epucks = ttk.Combobox(self.message_frame, values=self.available_epucks, postcommand=self.refresh_combo_list_epucks, state="readonly" )
                self.cmb_available_epucks.pack(side=LEFT)
                
                self.syncdict.update(tmp_dict)
                self.lock.release()

            #input message from user
            self.message = Entry(self.message_frame)
            self.message.pack(side=LEFT)

            #send button
            #Button(self.message_frame, text='Send', padx=5, command=self.send_msg).pack(side=LEFT)

            #pack
            self.message_frame.pack(side=BOTTOM)


    def reset_lock(self):
        try:
            self.lock.release()
        except Exception:
            pass


    def reset_host(self):
        is_locked = self.lock.acquire(timeout=self.timelock)

        if is_locked:
            current_dict = self.syncdict.copy()
            for epuck in current_dict['connected']:
                current_dict[epuck] = []
            self.syncdict.update(current_dict)
            self.lock.release()


    def send_msg(self, event):
        if self.message.get() != '' and  self.cmb_available_epucks.get() != '':
            if self.cmb_available_epucks.get() == 'All':
                #send msg to all Epucks
                current_dict = self.syncdict.copy()
                for epuck in current_dict['connected']:
                    self.send_msg_to(epuck, self.message.get())
            else:
                #send msg to epuck from selected combobox
                self.send_msg_to(self.cmb_available_epucks.get(), self.message.get())
            
            #clear input area
            self.message.delete(0, 'end')

        
    def send_msg_to(self, epuck, msg):
        if self.is_alive:
            try:
                is_locked = self.lock.acquire(timeout=self.timelock)
                if is_locked:
                    #send msg
                    current_dict = self.syncdict.copy()
                    epuck_inbox = current_dict[epuck]
                    epuck_inbox.append(msg)
                    current_dict.update({epuck: epuck_inbox})

                    self.syncdict.update(current_dict)
                    self.lock.release()

            except Exception as e:
                self.is_alive = False
                print('GUI lost communication with host communication')
                print(e)


    def refresh_combo_list_epucks(self):
        #list of available Epucks to send messages
        try:
            is_locked = self.lock.acquire(timeout=self.timelock)
            if is_locked:
                tmp_dict = self.syncdict.copy()
                available_epucks = get_available_clients(tmp_dict['connected'])
                number_available_epucks = len(available_epucks)

                if number_available_epucks > 1:
                    self.available_epucks = ['All']
                else:
                    self.available_epucks = []
                    
                self.available_epucks += available_epucks
                self.cmb_available_epucks['values']= self.available_epucks

                if number_available_epucks > 0:
                    self.cmb_available_epucks.current(0)
                else:
                    self.cmb_available_epucks.set('')

                self.lock.release()
        except Exception as e:
                    print(e)
        
   
    def update_label_connected(self, connected_dict):
        number_epucks_alive = len(get_available_clients(connected_dict))
        if number_epucks_alive > 0:
            if number_epucks_alive == 1:
                text = "There is " + str(number_epucks_alive) + " client connected."

            else:
                text = "There are "+  str(number_epucks_alive) + " clients connected."

            a_label = Label(self, text=text, bd=5, fg='blue')
        
            a_label.pack()
            self.list_labels.append(a_label)



    def update_epuck(self, tmp_dict, epuck):
        epuck_mailbox = tmp_dict[epuck]
        epuck_is_alive = tmp_dict['connected'][epuck]
        if epuck_is_alive:
            text = epuck + " has " + \
                str(len(epuck_mailbox)) + " messages pending."
            a_label = Label(self, text=text)

                 
            a_label = Label(self, text=text)
            a_label.pack()
            self.list_labels.append(a_label)
    

    def update_monitor_communication(self):
        try:
            if self.is_alive:
                try:
                    is_locked = self.lock.acquire(timeout=self.timelock)
                    if is_locked:
                        tmp_dict = self.syncdict.copy()
                        for label in self.list_labels:
                                label.destroy()

                        
                            #update pending messages
                        for key in tmp_dict:
                            if key == 'connected':
                                self.update_label_connected(tmp_dict[key])
                            elif key !='connected':
                                #key is an epuck 
                                self.update_epuck(tmp_dict, key)
                    

                            
                        self.lock.release()
                except Exception as e:
                    print(e)

            else:
                self.label_online.destroy()
                self.label_online = Label(self, text="OFFLINE", fg='red', pady=20)
                self.is_alive = False
                #print(self.host.is_alive())
                self.label_online.pack()
            
            self.after(1000, self.update_monitor_communication)


        except Exception as e:
            self.is_alive = False
            Label(text=e, fg='red').pack()
            print(e)



def open_new_window_communication(master, ip_addr):
    #check if ip_addr exist and remove spaces
    if not ip_addr or ip_addr == '':
        ip_addr = 'localhost'
    
    pid_name = os.getpid()
    
    root = Toplevel(master)
    root.title("Monitor Host Communication")
    root.geometry("500x400")
    monitor = MonitorCommunication(root, ip_addr, pid_name)
    root.bind('<Return>', monitor.send_msg)
    monitor.init_communication(ip_addr)
    monitor.after(1000, monitor.update_monitor_communication)
    monitor.mainloop()
