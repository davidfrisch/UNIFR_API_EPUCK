import tkinter as tk
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
        self.refresh_rate_val.set(500)
        tk.Label(refresh_frame, text='Refresh (ms):').pack(side='left')
        self.refresh_rate_scale = tk.Scale(
            refresh_frame, variable=self.refresh_rate_val, from_=10, to=1000, orient=tk.HORIZONTAL)
        self.refresh_rate_scale.pack()
        refresh_frame.pack()

        # begin of Canvas for display bmp image
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.image = None  # none yet
        

        #check if is real robot
        try:
            self.image_directory = folder_directory+'/'+self.epuck_id+'_image_video.bmp'
            load = Image.open(self.image_directory)
            load = load.resize((320, 240), Image.ADAPTIVE)
        except:
            #check if it is simulation
            try:
                self.image_directory = folder_directory+'/'+ self.epuck_id +'_image_video.jpg'
                load = Image.open(self.image_directory)
                load = load.resize((320, 240), Image.ADAPTIVE)
            except:
                load = None

        tk.Button(self, text='Take Picture', command=self.take_picture).pack()

        # begin of text to display directory of where the image is load
        data_string = tk.StringVar()
        data_string.set('\''+folder_directory+'\'')
        text_dir = tk.Entry(self, width=40, textvariable=data_string,
                            fg="black", bg="white", bd=0, state="readonly")
        text_dir.pack(side='bottom')

    def update(self):
        """
            Refresh the window every self.refresh_val time
        """
        # check if image exists
        try:
            load = Image.open(self.image_directory)
            load = load.resize((320, 240), Image.ADAPTIVE)
        except:
            load = None

            

        if load:
            w, h = load.size

            # must keep a reference to this
            self.render = ImageTk.PhotoImage(load)

            if self.image is not None:  # if an image was already loaded
                self.canvas.delete(self.image)  # remove the previous image

            self.image = self.canvas.create_image(
                (w/2, h/2), image=self.render)

        self.after(self.refresh_rate_val.get(), self.update)

    def take_picture(self):
        src_dir = self.folder_directory
        # create a dir where we want to copy and rename

        try:
            dest_dir = os.mkdir(self.folder_directory+'/picture_taken_from_'+ self.epuck_id)
            os.listdir()
        except:
            pass

        
        dest_dir = src_dir+'/picture_taken_from_'+ self.epuck_id
        src_file = os.path.join(src_dir, self.image_directory)
        shutil.copy(src_file, dest_dir) #copy the file to destination dir

        dst_file = os.path.join(dest_dir, self.image_directory)
        new_dst_file_name = os.path.join(dest_dir, 'btn_image'+ f"{self.counter_img:0>4}" +'.bmp')

        os.rename(dst_file, new_dst_file_name)#rename
        os.chdir(dest_dir)

        self.counter_img+=1



def main(folder_directory, epuck_ip):
    """
    Main function for GUI Epuck Camera

    :param folder_directory: In which folder the image is loaded
    :param epuck_ip: IP address of the epuck for unicity image load purpose.
    """
    # creating the window
    root = tk.Tk()
    root.geometry("%dx%d" % (325, 330))
    root.title(f'Camera of {epuck_ip}')

    # define the window
    app = MonitorCamera(folder_directory, epuck_ip, root)
    app.pack(fill=tk.BOTH, expand=1)

    # refresh after 1sec
    root.after(1000, app.update)
    root.mainloop()
