
from pathlib import Path
import subprocess
import sys
from threading import Event
import time

ROOT_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_PATH))

from src.config import load_config

CONFIG = load_config(str(ROOT_PATH / 'src/config/config.yml'))

class QueryServers():
    def __init__(self):
        self.processes = []


    def start_processes(self):
        print("Starting query servers...")

        for number in range(len(CONFIG['query_servers'])):
            number = number + 1
            server = subprocess.Popen(f"flask -e test/query_server_config/.env_server{number} --app test.query_server run")
            self.processes.append(server)
        time.sleep(1)

    def stop_processes(self):
        for server in self.processes:
            server.terminate()
    
        print("Finished terminating")

if __name__ == '__main__':
    servers = QueryServers()
    servers.start_processes()
    print("Query servers started.")
    
    stop_event = Event()
    while not stop_event.is_set():
        try:
            stop_event.wait(1)
        except KeyboardInterrupt as e:
            print("Terminating query servers...")
            stop_event.set()
    
    servers.stop_processes()

