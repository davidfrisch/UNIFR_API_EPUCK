import tkinter as tk
from tkinter.constants import BOTTOM
from PIL import Image, ImageTk
import os, shutil

"""
Inspiration:
    * https://stackoverflow.com/questions/45445163/python-tkinter-opening-bmp-file-as-canvas
"""


class MonitorCamera(tk.Frame):
    """
        Frame tkinter Object to display the stream of the Epuck camera
    """

    def __init__(self, folder_directory, epuck_ip, master=None):
        tk.Frame.__init__(self, master)

        self.epuck_id = epuck_ip.replace('.','_')
        self.folder_directory = folder_directory
        self.counter_img = 0

        # begin of frame for refresh rate parameter
        refresh_frame = tk.Frame(self)
        self.refresh_rate_val = tk.IntVar()
        self.refresh_rate_val.set(200)
        tk.Label(refresh_frame, text='Refresh (ms):').pack(side='left')
        self.refresh_rate_scale = tk.Scale(
            refresh_frame, variable=self.refresh_rate_val, from_=10, to=500, orient=tk.HORIZONTAL)
        self.refresh_rate_scale.pack()
        refresh_frame.pack()

        # begin of Canvas for display bmp image
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.image = None  # none yet
        
        found_type_robot = False
        #check if is real robot
        try:
            self.image_directory = folder_directory+'/'+self.epuck_id+'_image_video.bmp'
            load = Image.open(self.image_directory)
            load = load.resize((320, 240), Image.ADAPTIVE)
        except:
            #check if it is simulation
            try:
                self.image_directory = folder_directory+'/'+ self.epuck_id +'_image_video.png'
                load = Image.open(self.image_directory)
                load = load.resize((320, 240), Image.ADAPTIVE)
            except:
                load = None

                 #for pipuck test 
                try:
                    self.image_directory = folder_directory+'/'+ self.epuck_id +'_image_video.jpg'
                    load = Image.open(self.image_directory)
                    load = load.resize((320, 240), Image.ADAPTIVE)
                except:
                    load = None


        # begin of text to display directory of where the image is load
        footer_frame = tk.Frame(self)
        data_string = tk.StringVar()
        data_string.set('\''+folder_directory+'\'')
        text_dir = tk.Entry(footer_frame, width=40, textvariable=data_string,
                            fg="black", bg="white", bd=0, state="readonly")
        
        confirm_picture = tk.Label(footer_frame,text= 'Message saved !', fg='white')
        confirm_picture.pack()
        tk.Button(footer_frame, text='Take Picture', command=self.take_picture).pack()
        text_dir.pack(pady=30)
        self.confirm_message_label = [confirm_picture, 0]

        footer_frame.pack(side=BOTTOM)

    def update(self):
        """
            Refresh the window every self.refresh_val time
        """
        # check if image exists

        if self.confirm_message_label[1] > 0:
            self.confirm_message_label[1] = self.confirm_message_label[1] +1
            if self.confirm_message_label[1] > 15:
                self.confirm_message_label[1] = 0
                self.confirm_message_label[0].config(bg="white")
      
        try:
            load = Image.open(self.image_directory)
            
            #resize image considering window size
            width = self.master.winfo_width()
            height = self.master.winfo_height()

            if width < height:
                load = load.resize((width-10, height-200), Image.ADAPTIVE)
            else:
                load = load.resize((height-200, height-200), Image.ADAPTIVE)
        except:
            load = None

            

        if load:
            w, h = load.size

            # must keep a reference to this
            self.render = ImageTk.PhotoImage(load)

            if self.image is not None:  # if an image was already loaded
                self.canvas.delete(self.image)  # remove the previous image

            #add new image
            self.image = self.canvas.create_image(
                (w/2, h/2), image=self.render)

        self.after(self.refresh_rate_val.get(), self.update)

    def take_picture(self):
        """
        if necessary creates a new folder and saves the taken picture
        """
        src_dir = self.folder_directory

        try:
            dest_dir = os.mkdir(self.folder_directory+'/picture_taken_from_'+ self.epuck_id)
            os.listdir()
        except:
            pass

        
        dest_dir = src_dir+'/picture_taken_from_'+ self.epuck_id
        src_file = os.path.join(src_dir, self.image_directory)
        shutil.copy(src_file, dest_dir) #copy the file to destination dir

        dst_file = os.path.join(dest_dir, self.image_directory)
        counter = '{:04d}'.format(self.counter_img)
        new_dst_file_name = os.path.join(dest_dir, 'btn_image'+ counter +'.bmp')

        os.rename(dst_file, new_dst_file_name)#rename
        os.chdir(dest_dir)

        self.confirm_message_label[0].config(bg="green")
        self.confirm_message_label[1] = 1
        self.counter_img+=1

def open_new_window_camera(master, folder_directory, epuck_ip):
    root = tk.Toplevel(master)
    root.geometry("%dx%d" % (325, 330))
    root.title('Camera of ' +  epuck_ip)

    # define the window
    app = MonitorCamera(folder_directory, epuck_ip, root)
    app.pack(fill=tk.BOTH, expand=1)

    # refresh after 1sec
    root.after(1000, app.update)
    root.mainloop()
