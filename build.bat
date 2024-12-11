@echo off
echo 正在构建可执行文件...
pyinstaller --clean FileShare.spec
echo.
echo 构建完成！
echo 可执行文件位于 dist 目录中
pause
