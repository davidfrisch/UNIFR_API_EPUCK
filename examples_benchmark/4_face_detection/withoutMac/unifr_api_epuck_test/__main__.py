from .gui import gui_epuck_main 
import sys


def main():
    has_arg = False

    if any(i in sys.argv[1:] for i in ['g','gui','-gui','--gui','-g']):
        gui_epuck_main.main()
        has_arg = True

    if not has_arg:
        gui_epuck_main.main()

    
    


if __name__ == "__main__":
    main()
    