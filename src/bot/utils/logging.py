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




except Exception as e:
            error_traceback = traceback.format_exc()
            error_trace=str(error_traceback)
            characters_to_replace = ['"', ',', '/', '\\', '\n', "'","`","'https://huggingface.co/models'"]

            # Replacing each character with an empty string
            for char in characters_to_replace:
                error_trace = error_trace.replace(char, ' ')

            error_mes='GPT Api translation=>'+str(e) +error_trace
            now = datetime.now()
            text='{"@timestamp":"'+str(now)+'","log.level":"ERROR","app_name":"Bot","app_env":"'+str(APP_ENV)+'","Channel":"PWA","lead_id":"'+str(lead_id)+'","message":"'+error_mes+'"}'
            create_PWA_log(text)
