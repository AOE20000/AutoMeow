# MeowParser - 喵语解析器

即时文本处理工具，通过输入焦点劫持和悬浮窗中转实现量产猫娘

---

## 功能特点

- 悬浮输入窗口，不干扰原有输入框
- 多配置文件系统，快速切换不同场景
- 智能文本替换（支持文本匹配和正则表达式）
- 规则组管理，灵活组织替换规则
- 配置导入/导出
- 自定义触发器和直接输入模式

---

## 快捷键与工作原理

启用后，当你在白名单窗口中开始输入时：

1. 程序监听你的键盘输入
2. 激活输入框后，按空格键自动弹出悬浮窗
3. 悬浮窗强制获取焦点，阻止输入进入原输入框
4. 在悬浮窗中输入你要发送的文本
5. **回车**：应用替换规则，自动输入到原位置并回车
6. **Ctrl+回车**：直接发送原始内容，不做替换
7. **ESC**：取消输入，关闭悬浮窗
8. **Ctrl+Shift+Alt+M**：切换当前窗口启用状态

---

## 即时文本处理

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
- 标点符号前添加“喵”
- 换行符前添加“喵”
- 句尾添加“喵”
- “我”→“喵”

### 示例
- 输入：“需要管理员权限运行（因为需要键盘监听）启用状态下会监听键盘输入，建议在聊天软件等适当场合使用”

- 输出：“需要管理员权限运行喵（因为需要键盘监听喵）启用状态下会监听键盘输入喵，建议在聊天软件等适当场合使用喵”

- 输入：“其实我也不知道（其实我知道）”
- 规则：“我”→“喵”

- 输出：“其实喵也不知道喵（其实喵知道喵）” 

- 输入：“我有123个苹果和456个橙子”
- 规则：“\d+” “很多”（正则）

- 输出：“我有很多个苹果和很多个橙子喵”

- 输入：“hello world”
- 规则：“[a-z]+” “喵”（正则）

- 输出：“喵 喵喵”

---

## 系统要求

- Windows / Linux（未测试）
- 管理员/ root 权限

---

## 配置文件

所有配置文件统一存储在 `.meowparser` 目录：

- **规则配置文件**：`.meowparser/rules/`
- **窗口白名单**：`.meowparser/window_settings.json`
- **实例锁文件**：`.meowparser/instance.lock`（Linux）

---

## 文档

- [QUICKSTART.md](docs/QUICKSTART.md) - 快速开始
- [CHANGELOG.md](docs/CHANGELOG.md) - 更新日志
- [RULE_GROUPS_GUIDE.md](docs/RULE_GROUPS_GUIDE.md) - 规则配置文件指南
- [CUSTOM_TRIGGER_GUIDE.md](docs/CUSTOM_TRIGGER_GUIDE.md) - 自定义触发器指南
- [THEME_GUIDE.md](docs/THEME_GUIDE.md) - 主题切换指南
- [PROJECT_LAYOUT.md](PROJECT_LAYOUT.md) - 项目结构
- [BUILD_GUIDE.md](BUILD_GUIDE.md) - 打包说明
- [LICENSE](LICENSE) - 开源协议

---

## 开发

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

## 致谢与许可

本项目基于 AutoMeow 开发，特别感谢 afoim 的初期基础工作。

虽然当前版本已进行了大规模重构，且重点已转移至即时文本处理，但最初的概念为我们提供了宝贵的起点。

根据 AGPL-3.0 协议的要求，本项目保持开源。欢迎开发者在此基础上继续改进并遵循相同的协议分发。

---

## Keep Android Open

> **保持安卓开放**

https://keepandroidopen.org
