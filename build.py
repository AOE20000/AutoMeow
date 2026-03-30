#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MeowParser 跨平台打包脚本
支持 Windows 和 Linux 自动打包
"""

import os
import sys
import shutil
import subprocess
import platform
import io

# 设置 Windows 控制台编码
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass


def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60 + "\n")


def print_step(step, total, text):
    """打印步骤"""
    print(f"[{step}/{total}] {text}...")


def check_python():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"[错误] Python 版本过低: {version.major}.{version.minor}")
        print("需要 Python 3.8 或更高版本")
        return False
    print(f"[OK] Python 版本: {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """检查依赖"""
    required = {
        'PyQt6': 'PyQt6',
        'PyInstaller': 'PyInstaller',
        'keyboard': 'keyboard',
        'psutil': 'psutil'
    }
    missing = []
    
    for display_name, module_name in required.items():
        try:
            __import__(module_name)
            print(f"[OK] {display_name}")
        except ImportError:
            print(f"[X] {display_name} (缺失)")
            missing.append(display_name)
    
    if missing:
        print(f"\n[错误] 缺少依赖: {', '.join(missing)}")
        print("请运行: pip install -r requirements_pyqt6.txt")
        return False
    
    return True


def clean_build():
    """清理构建文件"""
    dirs_to_remove = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            print(f"删除 {dir_name}/")
            shutil.rmtree(dir_name)
    
    # 清理所有 __pycache__
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            shutil.rmtree(pycache_path)


def run_tests():
    """运行测试"""
    try:
        result = subprocess.run(
            [sys.executable, 'test_meow_rules.py'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',  # 忽略编码错误
            timeout=30
        )
        
        if result.returncode == 0:
            print("[OK] 所有测试通过")
            return True
        else:
            print("[X] 测试失败")
            print(result.stdout)
            print(result.stderr)
            
            response = input("\n是否继续打包？ (y/n): ")
            return response.lower() == 'y'
    
    except subprocess.TimeoutExpired:
        print("[X] 测试超时")
        return False
    except Exception as e:
        print(f"[X] 测试出错: {e}")
        return False


def build_package():
    """打包程序"""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'PyInstaller', '--clean', 'meow_parser.spec'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'  # 忽略编码错误
        )
        
        if result.returncode == 0:
            print("[OK] 打包成功")
            return True
        else:
            print("[X] 打包失败")
            print(result.stdout)
            print(result.stderr)
            return False
    
    except Exception as e:
        print(f"[X] 打包出错: {e}")
        return False


def copy_configs():
    """复制配置文件"""
    source_dir = '.meowparser/rules'
    target_dir = 'dist/.meowparser/rules'
    
    try:
        os.makedirs(target_dir, exist_ok=True)
        
        for file in os.listdir(source_dir):
            if file.endswith('.json'):
                source_file = os.path.join(source_dir, file)
                target_file = os.path.join(target_dir, file)
                shutil.copy2(source_file, target_file)
                print(f"复制 {file}")
        
        print("[OK] 配置文件复制完成")
        return True
    
    except Exception as e:
        print(f"[X] 复制配置文件失败: {e}")
        return False


def create_linux_launcher():
    """创建 Linux 启动脚本"""
    if platform.system() != 'Linux':
        return True
    
    launcher_path = 'dist/run_meowparser.sh'
    
    launcher_content = '''#!/bin/bash
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
'''
    
    try:
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        
        os.chmod(launcher_path, 0o755)
        os.chmod('dist/MeowParser', 0o755)
        
        print("[OK] 启动脚本创建完成")
        return True
    
    except Exception as e:
        print(f"[X] 创建启动脚本失败: {e}")
        return False


def print_summary():
    """打印总结"""
    system = platform.system()
    
    print_header("打包完成！")
    
    if system == 'Windows':
        print("可执行文件: dist\\MeowParser.exe")
        print("配置文件: dist\\.meowparser\\rules\\")
        print("\n运行方式:")
        print("  双击 dist\\MeowParser.exe")
        print("  或在命令行中: dist\\MeowParser.exe")
        print("\n注意: 首次运行需要管理员权限")
    
    elif system == 'Linux':
        print("可执行文件: dist/MeowParser")
        print("启动脚本: dist/run_meowparser.sh")
        print("配置文件: dist/.meowparser/rules/")
        print("\n运行方式:")
        print("  sudo ./dist/run_meowparser.sh")
        print("  或: sudo ./dist/MeowParser")
        print("\n注意: 需要 root 权限")
    
    else:
        print(f"可执行文件: dist/MeowParser")
        print(f"配置文件: dist/.meowparser/rules/")
    
    print("\n分发:")
    print("  将整个 dist 文件夹打包分发给用户")
    
    print("\n更多信息:")
    print("  查看 BUILD_GUIDE.md")


def main():
    """主函数"""
    print_header("MeowParser 打包工具")
    
    system = platform.system()
    print(f"操作系统: {system}")
    print(f"架构: {platform.machine()}")
    
    # 步骤 1: 检查 Python
    print_step(1, 6, "检查 Python 版本")
    if not check_python():
        return 1
    
    # 步骤 2: 检查依赖
    print_step(2, 6, "检查依赖")
    if not check_dependencies():
        return 1
    
    # 步骤 3: 清理旧文件
    print_step(3, 6, "清理旧的构建文件")
    clean_build()
    print("[OK] 清理完成")
    
    # 步骤 4: 运行测试
    print_step(4, 6, "运行测试")
    if not run_tests():
        print("\n打包已取消")
        return 1
    
    # 步骤 5: 打包
    print_step(5, 6, "打包程序（这可能需要几分钟）")
    if not build_package():
        return 1
    
    # 步骤 6: 后处理
    print_step(6, 6, "复制配置文件和创建启动脚本")
    if not copy_configs():
        return 1
    
    if system == 'Linux':
        if not create_linux_launcher():
            return 1
    
    # 打印总结
    print_summary()
    
    # 询问是否运行
    print("\n" + "=" * 60)
    response = input("是否立即运行程序？ (y/n): ")
    if response.lower() == 'y':
        print("\n启动程序...")
        
        if system == 'Windows':
            subprocess.Popen(['dist\\MeowParser.exe'])
        elif system == 'Linux':
            print("需要 root 权限，请手动运行:")
            print("  sudo ./dist/run_meowparser.sh")
        else:
            subprocess.Popen(['./dist/MeowParser'])
    
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n打包已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
