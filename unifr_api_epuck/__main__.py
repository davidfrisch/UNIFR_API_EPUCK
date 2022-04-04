from .flask_server_gui_communication.app import start_flask_server
import sys
import webbrowser


def main():
    webbrowser.open('http://127.0.0.1:8000/', new=1)
    start_flask_server()

if __name__ == "__main__":
    main()
    