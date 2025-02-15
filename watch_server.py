from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time
import subprocess

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command
        self.process = None
        self.start_process()

    def start_process(self):
        if self.process:
            self.process.terminate()
        print("Starting server...")
        self.process = subprocess.Popen(self.command, shell=True)

    def on_any_event(self, event):
        if event.src_path.endswith(('.py', '.html', '.js', '.css')):
            print(f"Detected change in {event.src_path}. Restarting server...")
            self.start_process()

if __name__ == "__main__":
    path = "."  # Monitor current directory
    command = "python inter_ass.py"  # Command to start your server
    event_handler = ChangeHandler(command)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
