@echo off
REM 安装打包依赖

echo ========================================
echo 安装 MeowParser 打包依赖
echo ========================================
echo.

echo 正在安装依赖...
pip install -r requirements_pyqt6.txt

if errorlevel 1 (
    echo.
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 依赖安装完成！
echo ========================================
echo.
echo 现在可以运行打包脚本：
echo   python build.py
echo   或
echo   build_windows.bat
echo.

pause
