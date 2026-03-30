# MeowParser - 喵语解析器

智能文本处理工具，通过输入焦点劫持和悬浮窗中转实现即时文本处理

---

## 快速开始

### 安装依赖

```bash
pip install -r requirements_pyqt6.txt
```

### 运行程序

```bash
# Windows
run.bat

# Linux/macOS
./run.sh

# 或直接运行
python meow_parser.py
```

---

## 功能特点

- 🎯 系统托盘运行，占用资源少
- 🚦 红/绿图标显示启用状态
- 🎨 现代化深色主题界面（BreezeStyleSheets 风格）
- � 自动主题切换（支持深色/浅色/自动跟随系统）
- �🎨 智能输入监听，自动弹出悬浮窗
- 💬 悬浮输入窗口，不干扰原有输入框
- 📁 多配置文件系统，快速切换不同场景
- 🔄 智能文本替换（支持文本匹配和正则表达式）
- 📋 规则组管理，灵活组织替换规则
- 🔒 单实例运行保护
- 🪟 窗口白名单管理
- 💾 配置导入/导出
- ⚙️ 自定义触发器和直接输入模式

---

## 工作原理

启用后，当你在白名单窗口中开始输入时：

1. 程序监听你的键盘输入
2. 激活输入框后，按空格键自动弹出悬浮窗
3. 悬浮窗强制获取焦点，阻止输入进入原输入框
4. 在悬浮窗中输入你要发送的文本
5. **回车**：应用替换规则，自动输入到原位置并回车
6. **Ctrl+回车**：直接发送原始内容，不做替换
7. **ESC**：取消输入，关闭悬浮窗

---

## 使用方法

### 基本操作

1. 运行程序后会在系统托盘显示"喵"字图标
2. 图标颜色：🔴 红色=禁用，🟢 绿色=启用
3. 右键图标菜单：
   - 启用/禁用功能
   - 窗口管理
   - 配置管理
   - 调试窗口
   - 退出程序

### 窗口管理

- 搜索窗口
- 双击切换启用状态
- 右键配置窗口
  - 设置自定义触发器
  - 启用直接输入模式
- 刷新窗口列表

**自定义触发器：**
- 默认：任何输入后按空格触发
- 自定义：设置特定字符（如 `u`），输入该字符后按空格触发
- 示例：设置触发器为 `u`，输入 `u` + 空格触发悬浮窗

**直接输入模式：**
- 标准模式：点击输入框 → 输入文本 → 回车
- 直接模式：直接输入文本 → 回车（跳过点击）
- 适用于聊天窗口、终端等始终保持焦点的应用

详见 [自定义触发器指南](docs/CUSTOM_TRIGGER_GUIDE.md)

### 配置管理

- 创建多个配置文件
- 快速切换配置
- 添加/编辑/删除规则
- 规则组管理（上下移动）
- 导入/导出配置
- 配置存储在 `.meowparser/rules/`
- 正则表达式规则橙色高亮显示

### 主题切换

- 🌓 自动模式：跟随系统主题自动切换
- 🌙 深色主题：经典的 Breeze Dark 风格
- ☀️ 浅色主题：清新的 Breeze Light 风格
- 右键托盘图标 → 主题 → 选择模式
- 详见 [主题切换指南](docs/THEME_GUIDE.md)

### 快捷键

- **回车**：应用规则并发送
- **Ctrl+回车**：发送原始内容
- **ESC**：取消输入
- **Ctrl+Shift+Alt+M**：切换当前窗口启用状态

---

## 文本替换

### 配置系统

- 支持多个配置文件
- 快速切换场景
- 自动迁移旧配置

### 规则组

- 规则按顺序执行
- 支持文本和正则匹配
- 灵活组织管理

### 默认配置

**喵语转换**
- 标点符号前添加"喵"
- 换行符前添加"喵"
- 句尾添加"喵"

### 示例

**普通文本：**
- 输入："为什么？"
- 输出："为什么喵？"

**正则表达式：**
- 规则："\\d+" → "很多"
- 输入："我有123个苹果"
- 输出："我有很多个苹果喵"

---

## 系统要求

- Windows / Linux / macOS
- Python 3.8+
- PyQt6 >= 6.6.0

**注意：** MeowParser 需要管理员/root 权限才能运行。程序会在启动时自动请求权限提升。

---

## 配置文件

所有配置文件统一存储在 `.meowparser` 目录：

- **规则配置**：`.meowparser/rules/*.json`
- **窗口白名单**：`.meowparser/window_settings.json`
- **实例锁文件**：`.meowparser/instance.lock`（Linux）
- **旧配置**：`replacement_rules.json`（自动迁移）

首次运行时，程序会自动创建默认配置并迁移旧配置文件。

---

## 文档

- [QUICKSTART.md](docs/QUICKSTART.md) - 快速开始
- [CUSTOM_TRIGGER_GUIDE.md](docs/CUSTOM_TRIGGER_GUIDE.md) - 自定义触发器指南
- [THEME_GUIDE.md](docs/THEME_GUIDE.md) - 主题切换指南
- [CHANGELOG.md](docs/CHANGELOG.md) - 更新日志
- [RULE_GROUPS_GUIDE.md](docs/RULE_GROUPS_GUIDE.md) - 规则指南
- [LICENSE](LICENSE) - 开源协议

---

## 开发

```bash
# 安装依赖
pip install -r requirements_pyqt6.txt

# 运行完整测试套件
python test_meow_rules.py

# 测试单个文本
python test_single_text.py "你好，世界"

# 交互式测试
python test_single_text.py

# 运行 UI 模块测试
python test_ui_modules.py
```

---

## 打包

### 跨平台打包（推荐）

```bash
# 自动检测系统并打包
python build.py
```

### Windows 打包

```cmd
# 使用批处理脚本
build_windows.bat

# 或手动打包
pyinstaller --clean meow_parser.spec
```

### Linux 打包

```bash
# 使用 shell 脚本
chmod +x build_linux.sh
./build_linux.sh

# 或手动打包
pyinstaller --clean meow_parser.spec
```

详细打包说明请查看 [BUILD_GUIDE.md](BUILD_GUIDE.md)

---

## 项目结构

```
MeowParser/
├── meow_parser/           # 主代码包
│   ├── core/              # 核心模块
│   ├── ui/                # UI 模块
│   ├── platform/          # 平台模块
│   └── app.py             # 主应用
├── docs/                  # 文档
├── .meowparser/           # 配置目录
├── README.md              # 本文档
├── LICENSE                # 许可证
├── meow_parser.py         # 程序入口
├── build.py               # 打包脚本
└── test_meow_rules.py     # 测试套件
```

详细结构请查看 [PROJECT_LAYOUT.md](PROJECT_LAYOUT.md)

---

## 致谢

本项目灵感源自并基于 AutoMeow 开发。

特别感谢 afoim 提供的初期基础工作。虽然当前版本已进行了大规模重构，且核心功能定位已全面转向即时文本处理，但原项目最初的概念与架构思路为 MeowParser 提供了宝贵的起点。

---

## Keep Android Open

> **保持安卓开放**

https://keepandroidopen.org
