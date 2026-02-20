#!/usr/bin/env python3
"""启动 FastAPI 后端服务（博客内容 API）。

在项目根目录执行: python3 run_backend.py
服务地址: http://0.0.0.0:8000 ，支持热重载。
"""
import uvicorn
import sys

if __name__ == "__main__":
    # 非 Windows 下设置 locale，便于控制台输出 UTF-8
    if sys.platform != "win32":
        import locale
        try:
            locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
        except Exception:
            pass

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
