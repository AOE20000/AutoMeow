#!/bin/bash
# 安装打包依赖

echo "========================================"
echo "安装 MeowParser 打包依赖"
echo "========================================"
echo ""

echo "正在安装依赖..."
pip3 install -r requirements_pyqt6.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 依赖安装失败"
    exit 1
fi

echo ""
echo "========================================"
echo "依赖安装完成！"
echo "========================================"
echo ""
echo "现在可以运行打包脚本："
echo "  python3 build.py"
echo "  或"
echo "  ./build_linux.sh"
echo ""
