#!/bin/bash
# MeowParser Linux 打包脚本
# 需要先安装依赖: pip install -r requirements_pyqt6.txt

set -e  # 遇到错误立即退出

echo "========================================"
echo "MeowParser Linux 打包工具"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi

echo "Python 版本: $(python3 --version)"
echo ""

# 检查依赖
echo "[1/5] 检查依赖..."
if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo "[错误] 未找到 PyQt6，正在安装依赖..."
    pip3 install -r requirements_pyqt6.txt
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败"
        exit 1
    fi
fi

# 清理旧的构建文件
echo "[2/5] 清理旧的构建文件..."
rm -rf build dist __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 运行测试
echo "[3/5] 运行测试..."
if ! python3 test_meow_rules.py; then
    echo "[警告] 测试失败，是否继续打包？ (y/n)"
    read -r continue
    if [ "$continue" != "y" ] && [ "$continue" != "Y" ]; then
        echo "打包已取消"
        exit 1
    fi
fi

# 开始打包
echo "[4/5] 开始打包..."
pyinstaller --clean meow_parser.spec
if [ $? -ne 0 ]; then
    echo "[错误] 打包失败"
    exit 1
fi

# 复制配置文件
echo "[5/5] 复制配置文件..."
mkdir -p "dist/.meowparser/rules"
cp .meowparser/rules/*.json "dist/.meowparser/rules/" 2>/dev/null || true

# 创建启动脚本
echo "创建启动脚本..."
cat > dist/run_meowparser.sh << 'EOF'
#!/bin/bash
# MeowParser 启动脚本

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
    echo "MeowParser 需要 root 权限来监听键盘输入"
    echo "正在使用 sudo 重新启动..."
    sudo "$0" "$@"
    exit $?
fi

# 获取脚本所在目录
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 运行程序
cd "$DIR"
./MeowParser
EOF

chmod +x dist/run_meowparser.sh
chmod +x dist/MeowParser

echo ""
echo "========================================"
echo "打包完成！"
echo "========================================"
echo ""
echo "可执行文件位置: dist/MeowParser"
echo "启动脚本: dist/run_meowparser.sh"
echo "配置文件位置: dist/.meowparser/rules/"
echo ""
echo "提示："
echo "1. 运行需要 root 权限: sudo ./run_meowparser.sh"
echo "2. 或直接运行: sudo ./MeowParser"
echo "3. 配置文件会自动创建在用户目录"
echo "4. 可以将整个 dist 文件夹分发给用户"
echo ""

# 询问是否运行
read -p "是否立即运行程序？ (y/n): " run
if [ "$run" = "y" ] || [ "$run" = "Y" ]; then
    echo "启动程序（需要 root 权限）..."
    cd dist
    sudo ./run_meowparser.sh
fi
