# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 14:01:23 2024

@author: anggi
"""

# main.py

from threading import Thread
from app.handler import process_existing_files
from app.server import start_server, run_flask, start_monitor
from app.config import FOLDER_PATH

if __name__ == "__main__":
    process_existing_files(FOLDER_PATH)

    server_thread = Thread(target=start_server)
    server_thread.start()

    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    start_monitor()
