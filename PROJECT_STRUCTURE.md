# MeowParser 项目结构

## 目录说明

```
MeowParser/
├── meow_parser/              # 核心代码包
│   ├── core/                 # 核心功能模块
│   │   ├── config_manager.py    # 配置管理
│   │   ├── text_processor.py    # 文本处理
│   │   └── instance_lock.py     # 单实例锁
│   ├── ui/                   # 用户界面模块
│   │   ├── tray_icon.py         # 系统托盘图标
│   │   ├── floating_window.py   # 悬浮输入窗口
│   │   ├── window_selector.py   # 窗口选择器
│   │   ├── rule_editor.py       # 规则编辑器
│   │   ├── config_editor.py     # 配置编辑器
│   │   └── debug_window.py      # 调试窗口
│   ├── platform/             # 平台特定功能
│   │   ├── windows.py           # Windows 平台
│   │   ├── linux.py             # Linux 平台
│   │   └── macos.py             # macOS 平台
│   └── app.py                # 主应用逻辑
│
├── .meowparser/              # 配置目录
│   └── rules/                # 规则配置文件
│       └── default.json      # 默认规则（已优化）
│
├── docs/                     # 文档目录
│   ├── CHANGELOG.md          # 更新日志
│   ├── QUICKSTART.md         # 快速开始指南
│   ├── RULE_GROUPS_GUIDE.md  # 规则组使用指南
│   └── RULES_OPTIMIZATION.md # 规则优化说明
│
├── meow_parser.py            # 程序入口
├── requirements_pyqt6.txt    # Python 依赖列表
├── LICENSE                   # 开源协议
├── README.md                 # 项目主文档
│
├── run.bat                   # Windows 运行脚本
├── run.sh                    # Linux/macOS 运行脚本
│
├── build.py                  # 跨平台打包脚本
├── build_windows.bat         # Windows 打包脚本
├── build_linux.sh            # Linux 打包脚本
├── meow_parser.spec          # PyInstaller 配置
├── install_build_deps.bat    # Windows 依赖安装
├── install_build_deps.sh     # Linux 依赖安装
│
├── test_meow_rules.py        # 规则测试套件
├── test_single_text.py       # 单文本测试工具
│
├── BUILD_GUIDE.md            # 打包详细指南
├── QUICK_BUILD.md            # 快速打包指南
├── TEST_GUIDE.md             # 测试指南
└── .gitignore                # Git 忽略配置
```

---

## 文件分类

### 核心文件（必需）

**程序运行：**
- `meow_parser/` - 核心代码包
- `meow_parser.py` - 程序入口
- `.meowparser/rules/default.json` - 默认规则配置
- `requirements_pyqt6.txt` - 依赖列表

**运行脚本：**
- `run.bat` - Windows 运行
- `run.sh` - Linux/macOS 运行

### 打包文件（开发用）

**打包脚本：**
- `build.py` - 跨平台自动打包（推荐）
- `build_windows.bat` - Windows 批处理
- `build_linux.sh` - Linux Shell
- `meow_parser.spec` - PyInstaller 配置

**依赖安装：**
- `install_build_deps.bat` - Windows
- `install_build_deps.sh` - Linux

### 测试文件（开发用）

- `test_meow_rules.py` - 完整测试套件（30+ 用例）
- `test_single_text.py` - 单文本测试工具

### 文档文件

**用户文档：**
- `README.md` - 项目主文档（必读）
- `docs/QUICKSTART.md` - 快速开始
- `docs/CHANGELOG.md` - 更新日志
- `LICENSE` - 开源协议

**开发文档：**
- `BUILD_GUIDE.md` - 打包详细指南
- `QUICK_BUILD.md` - 快速打包指南
- `TEST_GUIDE.md` - 测试指南
- `docs/RULE_GROUPS_GUIDE.md` - 规则组指南
- `docs/RULES_OPTIMIZATION.md` - 规则优化说明

### 配置文件

- `.gitignore` - Git 忽略配置

---

## 使用场景

### 普通用户

**需要的文件：**
- 下载打包版本（`dist/MeowParser.exe`）
- 或查看 `README.md` 和 `docs/QUICKSTART.md`

### 开发者

**需要的文件：**
- 所有核心文件
- 测试文件
- 开发文档

**工作流程：**
1. 克隆仓库
2. 安装依赖：`pip install -r requirements_pyqt6.txt`
3. 运行程序：`python meow_parser.py`
4. 运行测试：`python test_meow_rules.py`
5. 打包：`python build.py`

### 贡献者

**需要的文件：**
- 所有文件
- 特别关注测试文件和文档

---

## 目录大小

- **核心代码：** ~50 KB
- **配置文件：** ~2 KB
- **文档：** ~100 KB
- **测试：** ~20 KB
- **打包脚本：** ~30 KB

**总计：** ~200 KB（不含依赖和构建输出）

---

## 清理命令

### 清理构建文件

```bash
# Windows
rmdir /s /q build dist
del /q *.pyc

# Linux/macOS
rm -rf build dist __pycache__
find . -name "*.pyc" -delete
```

### 清理测试缓存

```bash
# Windows
del /q *.log

# Linux/macOS
rm -f *.log
```

---

## 最小化部署

如果只需要运行程序，最小文件集：

```
meow_parser/          # 核心代码
meow_parser.py        # 入口
.meowparser/          # 配置
requirements_pyqt6.txt # 依赖
run.bat / run.sh      # 运行脚本
```

---

## 更新日志

### v2.2.1 (2026-03-30)
- 整理项目结构
- 移除冗余文档
- 保留核心功能和必要文档
