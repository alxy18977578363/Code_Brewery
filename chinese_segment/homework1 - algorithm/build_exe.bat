@echo off
REM Windows 打包脚本：安装 pyinstaller 并生成单文件 exe
REM 使用前请确保在虚拟环境或系统 Python 环境中运行

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM PyInstaller 的 --add-data 格式在 Windows 上为 "src;dest"
REM 将 data/ 和 model/ 一并打包到 exe 同级的目录下
pyinstaller --noconfirm --onefile --add-data "data;data" --add-data "model;model" --name crf_segmenter src\cli.py

echo 打包完成。可在 dist\crf_segmenter.exe 找到可执行文件。
pause
