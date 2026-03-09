import streamlit.web.cli as stcli
import sys
import os
import socket

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def main():
    if hasattr(sys, '_MEIPASS'):
        app_path = os.path.join(sys._MEIPASS, 'app.py')
    else:
        app_path = os.path.join(os.path.dirname(__file__), 'app.py')
        
    port = get_free_port()
    print(f"Starting AudioTranscriber on port {port}...")
    sys.argv = ["streamlit", "run", app_path, "--global.developmentMode=false", f"--server.port={port}"]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()
