@echo off
REM MeowParser Windows 打包脚本
REM 需要先安装依赖: pip install -r requirements_pyqt6.txt

echo ========================================
echo MeowParser Windows 打包工具
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/5] 检查依赖...
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 PyQt6，正在安装依赖...
    pip install -r requirements_pyqt6.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [2/5] 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

echo [3/5] 运行测试...
python test_meow_rules.py
if errorlevel 1 (
    echo [警告] 测试失败，是否继续打包？ (Y/N)
    set /p continue=
    if /i not "%continue%"=="Y" (
        echo 打包已取消
        pause
        exit /b 1
    )
)

echo [4/5] 开始打包...
pyinstaller --clean meow_parser.spec
if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo [5/5] 复制配置文件...
if not exist "dist\.meowparser\rules" mkdir "dist\.meowparser\rules"
copy ".meowparser\rules\*.json" "dist\.meowparser\rules\" >nul 2>&1

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 可执行文件位置: dist\MeowParser.exe
echo 配置文件位置: dist\.meowparser\rules\
echo.
echo 提示：
echo 1. 首次运行需要管理员权限
echo 2. 配置文件会自动创建在用户目录
echo 3. 可以将整个 dist 文件夹分发给用户
echo.

REM 询问是否运行
set /p run="是否立即运行程序？ (Y/N): "
if /i "%run%"=="Y" (
    echo 启动程序...
    start "" "dist\MeowParser.exe"
)

pause
