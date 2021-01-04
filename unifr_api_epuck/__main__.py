from unifr_api_epuck import gui_epuck_main as gem
from unifr_api_epuck import gui_epuck_communication as gec
import sys, os

if __name__ == "__main__":
    """
    if arguments in the command line --> IRL
    leave empy if using Webots
    """
    #take arguments
    argc = sys.argv[1:]

    if len(argc) == 1:
        ip_addr = sys.argv[1]
        pid_name = os.getpid()
        gec.main(ip_addr, pid_name)
    
    gem.main()
    