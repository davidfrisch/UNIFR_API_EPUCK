import tkinter as tk
from tkinter import ttk, StringVar, BOTH, filedialog as fd
from multiprocessing import Process
from unifr_api_epuck import gui_epuck_communication as gui_communication
from unifr_api_epuck import gui_epuck_camera as gui_camera
import json
import webbrowser


class MainWindow(tk.Frame):
    """
        Main tkinter Frame Object to display the menu of the program
    """

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        # init variables
        self.host_ips = []
        self.epuck_ips = []
        self.folder_dir = StringVar()
        self.folder_dir.set('Select location folder images')
        self.has_set_directory = False

        # load data from json file
        try:
            with open('unifr_api_epuck.json', 'r') as openfile:
                dict_data = json.load(openfile)
                self.host_ips = dict_data['host_ips']
                self.epuck_ips = dict_data['epuck_ips']
                self.folder_dir.set(dict_data['last_folder_dir'])
        except:
            pass

        # GUI start
        menu = tk.Menu(self.master)
        master.config(menu=menu)
        master.geometry("%dx%d" % (400, 600))

        # top bar menu
        file_menu = tk.Menu(menu)
        file_menu.add_command(label='Go to Github source',
                              command=self.open_github)
        #file_menu.add_command(label='Go to Readthedocs', command=self.open_communication_monitor)
        file_menu.add_command(label='Exit', command=self.quit)
        menu.add_cascade(label="Window", menu=file_menu)

        # communication
        com_frame = tk.Frame(self)
        tk.Label(com_frame, text='Enter Host IP address (default:localhost)').pack()
        self.cmb_host_ips = ttk.Combobox(com_frame, values=self.host_ips)

        # put first value as initial
        if self.host_ips:
            self.cmb_host_ips.current(0)
        self.cmb_host_ips.pack()

        comm_btn = tk.Button(com_frame, text='Open Communication Monitor',
                             command=self.open_communication_monitor, fg='blue', bg='grey')
        comm_btn.pack(side=tk.TOP, pady=10, padx=10)
        com_frame.pack(pady=40)

        # camera tools positioning
        cam_frame = tk.Frame(self)

        tk.Label(cam_frame, text='Enter IP address or Webots Epuck ID').pack()
        self.cmb_epuck_ips = ttk.Combobox(cam_frame, values=self.epuck_ips)

        # put first value as initial in the combobox
        if self.epuck_ips:
            self.cmb_epuck_ips.current(0)

        self.cmb_epuck_ips.pack(pady=10)
        if self.folder_dir.get() != 'Select location folder images':
            self.has_set_directory = True

        tk.Entry(cam_frame, textvariable=self.folder_dir,
                 state="readonly", width=40, bd=0, bg='white').pack(pady=10)

        file_btn = tk.Button(cam_frame, text='Locate folder...',
                             command=self.open_folder, fg='blue', bg='grey')
        file_btn.pack(side=tk.TOP, pady=10, padx=20)

        cam_btn = tk.Button(cam_frame, text='Open Camera Monitor',
                            command=self.open_camera_monitor, fg='blue', bg='grey')
        cam_btn.pack(side=tk.TOP, pady=10, padx=10)

        cam_frame.pack(pady=40)

        # unifr credential
        author_label = tk.Label(text='UNIFR - 2020 \n Author : David Frischer \n Supervisor : Julien Nembrini',
                                anchor="e")
        author_label.pack(side=tk.BOTTOM)

        self.pack(fill=BOTH)

    def open_camera_monitor(self):
        current_epuck_ip = self.cmb_epuck_ips.get().replace(' ', '')
        if self.has_set_directory and current_epuck_ip != '':
            if current_epuck_ip in self.epuck_ips:
                self.epuck_ips.remove(current_epuck_ip)
            # put it in first position
            self.epuck_ips.insert(0, current_epuck_ip)
            self.insert_data_json()
            Process(target=gui_camera.main, args=(
                self.folder_dir.get(), current_epuck_ip, )).start()

    def open_communication_monitor(self):
        # default value
        current_host_ip = self.cmb_host_ips.get().replace(' ', '')
        if current_host_ip == '':
            current_host_ip = 'localhost'

        if current_host_ip in self.host_ips:
            self.host_ips.remove(current_host_ip)

        # put it in first position
        self.host_ips.insert(0, current_host_ip)

        self.insert_data_json()
        # launch gui host communication process
        Process(target=gui_communication.main,
                args=(current_host_ip,)).start()

    def insert_data_json(self):
        json_object = json.dumps(
            # [:5] --> will only keep the last 5 records
            {'host_ips': self.host_ips[:5], 'epuck_ips': self.epuck_ips[:5], 'last_folder_dir': self.folder_dir.get()}, indent=4)
        with open('unifr_api_epuck.json', 'w') as outfile:
            outfile.write(json_object)

    # Where I open my file
    def open_folder(self):
        output = fd.askdirectory()

        if not output and not self.has_set_directory:
            self.has_set_directory = False
            self.folder_dir.set('No directory selected')
            return  # user cancelled; stop this method
        elif output:
            self.has_set_directory = True
            self.folder_dir.set(output)

    def open_github(self):
        webbrowser.open(
            'https://github.com/davidfrisch/TravailBachelor', new=2)


def main():
    root = tk.Tk()
    root.title("Main E-PUCK GUI")
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
