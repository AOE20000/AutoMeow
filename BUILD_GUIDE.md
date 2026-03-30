# 打包指南

## 概述

MeowParser 支持打包为独立可执行文件，无需安装 Python 环境即可运行。

---

## 自动检测系统并打包

```bash
python build.py
```

---

## Windows 打包

### 前置要求

- Windows 7 或更高版本
- Python 3.8+ 已安装
- 已安装依赖：`pip install -r requirements_pyqt6.txt`

### 快速打包

双击运行 `build_windows.bat` 或在命令行中执行：

```cmd
build_windows.bat
```

### 手动打包

```cmd
# 1. 安装依赖
pip install -r requirements_pyqt6.txt

# 2. 运行测试（可选）
python test_meow_rules.py

# 3. 清理旧文件
rmdir /s /q build dist

# 4. 打包
pyinstaller --clean meow_parser.spec

# 5. 复制配置文件
mkdir dist\.meowparser\rules
copy .meowparser\rules\*.json dist\.meowparser\rules\
```

### 输出文件

```
dist/
├── MeowParser.exe          # 主程序
└── .meowparser/
    └── rules/
        └── default.json    # 默认规则
```

### 分发

将整个 `dist` 文件夹打包为 ZIP 文件分发给用户。

---

## Linux 打包

### 前置要求

- Linux (Ubuntu 20.04+ / Debian 11+ / Fedora 35+ 等)
- Python 3.8+ 已安装
- 已安装依赖：`pip3 install -r requirements_pyqt6.txt`

### 快速打包

```bash
chmod +x build_linux.sh
./build_linux.sh
```

### 手动打包

```bash
# 1. 安装依赖
pip3 install -r requirements_pyqt6.txt

# 2. 运行测试（可选）
python3 test_meow_rules.py

# 3. 清理旧文件
rm -rf build dist __pycache__

# 4. 打包
pyinstaller --clean meow_parser.spec

# 5. 复制配置文件
mkdir -p dist/.meowparser/rules
cp .meowparser/rules/*.json dist/.meowparser/rules/

# 6. 添加执行权限
chmod +x dist/MeowParser
```

### 输出文件

```
dist/
├── MeowParser              # 主程序
├── run_meowparser.sh       # 启动脚本（自动使用 sudo）
└── .meowparser/
    └── rules/
        └── default.json    # 默认规则
```

### 分发

将整个 `dist` 文件夹打包为 tar.gz 文件：

```bash
cd dist
tar -czf MeowParser-linux-x64.tar.gz *
```

---

## 打包选项

### 修改 meow_parser.spec

#### 添加图标

```python
exe = EXE(
    ...
    icon='path/to/icon.ico',  # Windows: .ico
    # icon='path/to/icon.png',  # Linux: .png
)
```

#### 启用控制台（调试用）

```python
exe = EXE(
    ...
    console=True,  # 显示控制台窗口
)
```

#### 单文件模式（已启用）

当前配置已使用单文件模式（`--onefile`），所有依赖打包在一个可执行文件中。

#### 目录模式

如需目录模式（启动更快，但文件更多）：

```python
exe = EXE(
    pyz,
    a.scripts,
    [],  # 不包含 a.binaries 等
    exclude_binaries=True,
    ...
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    ...
)
```

---

## 常见问题

### Q: 打包后程序无法启动

A: 检查以下几点：
1. 是否以管理员/root 权限运行
2. 是否缺少系统依赖（Linux 需要 X11 库）
3. 查看错误日志（启用 console=True）

### Q: 打包文件太大

A: 可以优化：
1. 在 spec 文件中添加更多 excludes
2. 使用 UPX 压缩（已启用）
3. 移除不需要的依赖

### Q: Linux 下提示权限不足

A: 使用 sudo 运行：
```bash
sudo ./MeowParser
# 或
sudo ./run_meowparser.sh
```

### Q: Windows 下被杀毒软件拦截

A: 这是 PyInstaller 打包程序的常见问题：
1. 添加到杀毒软件白名单
2. 使用代码签名证书签名程序
3. 向杀毒软件厂商报告误报

### Q: 如何减小打包体积？

A: 编辑 `meow_parser.spec`，添加更多排除项：

```python
excludes=[
    'tkinter',
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'IPython',
    'jupyter',
    'test',
    'unittest',
    'distutils',
    'setuptools',
]
```

---

## 高级配置

### 多平台打包

在不同平台上分别打包：

```bash
# Windows
build_windows.bat

# Linux
./build_linux.sh

# macOS (需要在 macOS 上执行)
./build_macos.sh  # 需要创建此脚本
```

### 自动化打包

使用 CI/CD 工具（如 GitHub Actions）自动打包：

```yaml
# .github/workflows/build.yml
name: Build

on: [push, pull_request]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements_pyqt6.txt
      - run: build_windows.bat
      - uses: actions/upload-artifact@v2
        with:
          name: MeowParser-Windows
          path: dist/

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements_pyqt6.txt
      - run: chmod +x build_linux.sh && ./build_linux.sh
      - uses: actions/upload-artifact@v2
        with:
          name: MeowParser-Linux
          path: dist/
```

---

## 版本管理

### 添加版本信息（Windows）

创建 `version_info.txt`：

```
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2, 2, 1, 0),
    prodvers=(2, 2, 1, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'MeowParser'),
        StringStruct(u'FileDescription', u'智能文本处理工具'),
        StringStruct(u'FileVersion', u'2.2.1.0'),
        StringStruct(u'InternalName', u'MeowParser'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2024-2026'),
        StringStruct(u'OriginalFilename', u'MeowParser.exe'),
        StringStruct(u'ProductName', u'MeowParser'),
        StringStruct(u'ProductVersion', u'2.2.1.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
```

在 spec 文件中引用：

```python
exe = EXE(
    ...
    version='version_info.txt',
)
```

---

## 测试打包结果

### Windows

```cmd
# 运行程序
dist\MeowParser.exe

# 查看依赖
dumpbin /dependents dist\MeowParser.exe
```

### Linux

```bash
# 运行程序
sudo dist/MeowParser

# 查看依赖
ldd dist/MeowParser
```

---

## 性能优化

### 启动速度优化

1. 使用目录模式而非单文件模式
2. 减少隐藏导入
3. 使用 lazy imports

### 体积优化

1. 排除不需要的模块
2. 启用 UPX 压缩
3. 移除调试信息

---

## 更多信息

- PyInstaller 文档: https://pyinstaller.org/
- 项目文档: README.md
- 更新日志: docs/CHANGELOG.md
