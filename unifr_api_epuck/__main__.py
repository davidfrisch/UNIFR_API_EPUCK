from .gui import gui_epuck_main 
from .epuck import host_epuck_communication
import sys


def main():
    has_arg = False
    if any(i in sys.argv[1:] for i in ['h','host','-host','--host','-h']):
        host_epuck_communication.start_manager('localhost')
        has_arg = True

    if any(i in sys.argv[1:] for i in ['g','gui','-gui','--gui','-g']):
        gui_epuck_main.main()
        has_arg = True

    if not has_arg:
        print('possible arguments : -h to activate host or -g to activate gui')

    
    


if __name__ == "__main__":
    main()
    