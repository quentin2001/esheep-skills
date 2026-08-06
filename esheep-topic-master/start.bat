@echo off
echo ========================================================
echo   esheep-topic-master 选题掌管者 - 本地看板启动器
echo ========================================================
echo.
echo 正在打开浏览器: http://localhost:18922 ...
start "" "http://localhost:18922"
echo 正在启动 Python 后端服务 (端口 18922)...
python scripts/server.py --port 18922
