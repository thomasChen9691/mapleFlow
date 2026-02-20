# -*- coding: utf-8 -*-
"""
自动 add / commit / push。在项目根目录运行: python auto_push.py 或 .\auto_push.py
"""
import os
import sys
import subprocess
from datetime import datetime

def _repo_root():
    return os.path.dirname(os.path.abspath(__file__))

def _run_git(args, cwd=None):
    cwd = cwd or _repo_root()
    return subprocess.run(["git"] + list(args), cwd=cwd)

def auto_push():
    root = _repo_root()
    # 使用纯 ASCII 的 commit message，避免 Windows 控制台编码导致乱码或脚本异常
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = "update: " + now

    try:
        r = _run_git(["add", "."], cwd=root)
        if r.returncode != 0:
            print("git add failed, exit code:", r.returncode, flush=True)
            sys.exit(1)

        r = _run_git(["commit", "-m", msg], cwd=root)
        if r.returncode != 0:
            print("No changes to commit, skip push. To push existing commits run: git push origin main", flush=True)
            return

        r = _run_git(["push", "origin", "main"], cwd=root)
        if r.returncode != 0:
            print("git push failed, exit code:", r.returncode, flush=True)
            sys.exit(1)
        print("Committed and pushed.", flush=True)
    except Exception as e:
        print("Error:", e, flush=True)
        sys.exit(1)

if __name__ == "__main__":
    auto_push()
