# MeowParser - 喵语解析器

智能文本处理工具，通过输入监听和悬浮窗实现实时文本转换

基于 PyQt6 构建，支持跨平台运行（Windows/Linux/macOS）

**当前版本：2.2.0**

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
- 🎨 智能输入监听，自动弹出悬浮窗
- 💬 悬浮输入窗口，不干扰原有输入框
- 📁 多配置文件系统，快速切换不同场景
- 🔄 智能文本替换（支持文本匹配和正则表达式）
- 📋 规则组管理，灵活组织替换规则
- 🔒 单实例运行保护
- 🪟 窗口白名单管理
- 💾 配置导入/导出

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
- 刷新窗口列表

### 配置管理

- 创建多个配置文件
- 快速切换配置
- 添加/编辑/删除规则
- 导入/导出配置
- 配置存储在 `.meowparser/rules/`

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
- 管理员/root 权限
- Python 3.8+
- PyQt6 >= 6.6.0

---

## 配置文件

- **窗口白名单**：`window_settings.json`
- **配置文件**：`.meowparser/rules/*.json`
- **旧配置**：`replacement_rules.json`（自动迁移）

---

## 文档

- [QUICKSTART.md](docs/QUICKSTART.md) - 快速开始
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

详细结构请查看 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

---

## 许可证

本项目采用开源协议，详见 [LICENSE](LICENSE)

---

# Keep Android Open
https://keepandroidopen.org
