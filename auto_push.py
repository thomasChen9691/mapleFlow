import subprocess
from datetime import datetime

def auto_push():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"update: {now}"
    subprocess.run(["git", "add", "."], check=True)
    # 若无变更，git commit 会失败并导致 check=True 抛错，脚本在此退出，不会执行 push
    r = subprocess.run(["git", "commit", "-m", msg])
    if r.returncode != 0:
        print("没有可提交的变更，跳过 push。若有未推送的提交，可手动执行: git push origin main")
        return
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("已提交并推送完成。")

auto_push()