import logging
import os
from datetime import datetime

def create_pwa_log(text):
    now = datetime.now()
    log_dir = "/var/log/bot"
    os.makedirs(log_dir, exist_ok=True)  # Ensure the log directory exists
    
    file_path = f"{log_dir}/bot-{now.year}-{now.month:02d}-{now.day:02d}.log"
    
    with open(file_path, "a") as fp:
        fp.write(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - {text}\n")



