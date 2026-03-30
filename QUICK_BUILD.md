# 快速打包指南

## 一键打包

### Windows

```cmd
# 1. 安装依赖（首次）
install_build_deps.bat

# 2. 打包
python build.py
```

或使用批处理脚本：

```cmd
build_windows.bat
```

### Linux

```bash
# 1. 安装依赖（首次）
chmod +x install_build_deps.sh
./install_build_deps.sh

# 2. 打包
python3 build.py
```

或使用 shell 脚本：

```bash
chmod +x build_linux.sh
./build_linux.sh
```

---

## 输出文件

### Windows

```
dist/
├── MeowParser.exe          # 可执行文件
└── .meowparser/
    └── rules/
        └── default.json    # 默认规则
```

运行：双击 `dist\MeowParser.exe`（需要管理员权限）

### Linux

```
dist/
├── MeowParser              # 可执行文件
├── run_meowparser.sh       # 启动脚本
└── .meowparser/
    └── rules/
        └── default.json    # 默认规则
```

运行：`sudo ./dist/run_meowparser.sh`

---

## 分发

### Windows

```cmd
# 打包为 ZIP
cd dist
tar -a -c -f MeowParser-Windows-x64.zip *
```

或使用 Windows 资源管理器：
1. 右键点击 `dist` 文件夹
2. 选择"发送到" → "压缩(zipped)文件夹"

### Linux

```bash
# 打包为 tar.gz
cd dist
tar -czf MeowParser-Linux-x64.tar.gz *
```

---

## 常见问题

### Q: 提示缺少依赖

A: 运行安装脚本：
- Windows: `install_build_deps.bat`
- Linux: `./install_build_deps.sh`

### Q: 打包失败

A: 检查：
1. Python 版本是否 >= 3.8
2. 是否安装了所有依赖
3. 查看错误信息

### Q: 打包后文件很大

A: 这是正常的，因为包含了 Python 运行时和所有依赖。
可以通过编辑 `meow_parser.spec` 优化体积。

### Q: 测试失败但想继续打包

A: 在提示时输入 `y` 继续。

---

## 更多信息

详细打包指南：[BUILD_GUIDE.md](BUILD_GUIDE.md)
