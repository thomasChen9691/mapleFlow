import subprocess
from datetime import datetime

def auto_push():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"update: {now}"
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", msg], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)

auto_push()