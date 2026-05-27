from datetime import datetime

def log_action(message: str):
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"[{current_time}] {message}")
