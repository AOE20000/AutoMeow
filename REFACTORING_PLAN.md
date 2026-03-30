# MeowParser 代码重构计划

## 当前状态
- 单文件：`meow_parser.py` (2823行)
- 11个类 + 2个函数
- 所有功能耦合在一个文件中

## 目标
将代码拆分为清晰的模块结构，提高可维护性和可测试性

---

## 新的项目结构

```
meow_parser/
├── __init__.py                 # 包初始化
├── __main__.py                 # 程序入口（python -m meow_parser）
├── app.py                      # 主应用类 (MeowParser)
├── constants.py                # 常量定义
├── utils.py                    # 工具函数
│
├── core/                       # 核心功能模块
│   ├── __init__.py
│   ├── config_manager.py       # ConfigFileManager
│   ├── text_processor.py       # TextProcessor
│   └── instance_lock.py        # 单实例检查
│
├── ui/                         # UI组件模块
│   ├── __init__.py
│   ├── floating_window.py      # FloatingInputWindow
│   ├── window_selector.py      # WindowSelector
│   ├── config_editor.py        # ConfigFileEditor + RuleEditDialog
│   ├── rule_editor.py          # ReplacementRuleEditor + RuleDialog (旧版兼容)
│   ├── debug_window.py         # DebugWindow
│   └── tray_icon.py            # 系统托盘相关
│
└── platform/                   # 平台相关模块
    ├── __init__.py
    ├── windows.py              # Windows特定功能
    ├── linux.py                # Linux特定功能
    └── macos.py                # macOS特定功能
```

---

## 拆分步骤

### 阶段1：准备工作
1. ✅ 创建项目目录结构
2. ✅ 创建 `__init__.py` 文件
3. ✅ 创建 `constants.py` - 提取常量

### 阶段2：核心模块拆分
4. ✅ 拆分 `core/instance_lock.py` - 单实例检查
5. ✅ 拆分 `core/config_manager.py` - ConfigFileManager
6. ✅ 拆分 `core/text_processor.py` - TextProcessor

### 阶段3：UI模块拆分
7. ✅ 拆分 `ui/debug_window.py` - DebugWindow
8. ✅ 拆分 `ui/floating_window.py` - FloatingInputWindow
9. ✅ 拆分 `ui/window_selector.py` - WindowSelector
10. ✅ 拆分 `ui/config_editor.py` - ConfigFileEditor + RuleEditDialog
11. ✅ 拆分 `ui/rule_editor.py` - ReplacementRuleEditor + RuleDialog
12. ✅ 拆分 `ui/tray_icon.py` - 托盘图标相关

### 阶段4：平台模块拆分
13. ✅ 拆分 `platform/windows.py` - Windows特定功能
14. ✅ 拆分 `platform/linux.py` - Linux特定功能
15. ✅ 拆分 `platform/macos.py` - macOS特定功能（预留）

### 阶段5：主应用重构
16. ✅ 创建 `app.py` - MeowParser主类
17. ✅ 创建 `__main__.py` - 程序入口
18. ✅ 创建 `utils.py` - 工具函数

### 阶段6：测试和验证
19. ✅ 测试所有功能是否正常
20. ✅ 更新文档和导入说明
21. ✅ 保留旧的 `meow_parser.py` 作为兼容入口

---

## 模块职责说明

### `constants.py`
- 平台检测常量 (IS_WINDOWS, IS_LINUX, IS_MACOS)
- 默认配置路径
- 版本信息
- 其他全局常量

### `utils.py`
- 通用工具函数
- 不依赖特定平台的辅助函数

### `core/instance_lock.py`
```python
def check_single_instance() -> bool | object
```

### `core/config_manager.py`
```python
class ConfigFileManager:
    - 配置文件管理
    - 配置加载/保存
    - 配置迁移
```

### `core/text_processor.py`
```python
class TextProcessor:
    - 文本处理引擎
    - 规则应用逻辑
```

### `ui/floating_window.py`
```python
class FloatingInputWindow(QWidget):
    - 悬浮输入窗口
    - 文本输入和发送
```

### `ui/window_selector.py`
```python
class WindowSelector(QWidget):
    - 窗口管理器
    - 白名单管理
```

### `ui/config_editor.py`
```python
class ConfigFileEditor(QWidget):
    - 配置文件编辑器
class RuleEditDialog(QDialog):
    - 规则编辑对话框
```

### `ui/rule_editor.py`
```python
class ReplacementRuleEditor(QWidget):
    - 旧版规则编辑器（兼容）
class RuleDialog(QDialog):
    - 规则对话框
```

### `ui/debug_window.py`
```python
class DebugWindow(QWidget):
    - 调试窗口
    - 日志显示
```

### `ui/tray_icon.py`
```python
class TrayIconManager:
    - 系统托盘图标管理
    - 菜单创建
    - 图标生成
```

### `platform/windows.py`
```python
def get_active_window_info() -> dict | None
def enumerate_windows(callback) -> list
def set_foreground_window(hwnd) -> bool
# ... 其他Windows特定函数
```

### `platform/linux.py`
```python
def get_active_window_info() -> dict | None
def enumerate_windows() -> list
def set_foreground_window(window_id) -> bool
# ... 其他Linux特定函数
```

### `app.py`
```python
class MeowParser(QObject):
    - 主应用逻辑
    - 协调各个模块
    - 事件处理
```

### `__main__.py`
```python
def main():
    - 程序入口
    - 初始化应用
```

---

## 兼容性处理

### 保留旧入口
创建新的 `meow_parser.py` 作为兼容入口：
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MeowParser - 兼容入口
为了向后兼容，保留此文件
实际代码已迁移到 meow_parser 包
"""

from meow_parser.__main__ import main

if __name__ == "__main__":
    main()
```

### 导入方式
```python
# 旧方式（仍然支持）
python meow_parser.py

# 新方式
python -m meow_parser

# 或者
from meow_parser import MeowParser
```

---

## 依赖关系图

```
app.py (MeowParser)
├── core/
│   ├── instance_lock.py
│   ├── config_manager.py
│   └── text_processor.py
├── ui/
│   ├── floating_window.py
│   ├── window_selector.py
│   ├── config_editor.py
│   ├── rule_editor.py
│   ├── debug_window.py
│   └── tray_icon.py
├── platform/
│   ├── windows.py
│   ├── linux.py
│   └── macos.py
├── constants.py
└── utils.py
```

---

## 优势

### 1. 可维护性
- 每个模块职责单一
- 代码更容易理解和修改
- 减少文件长度

### 2. 可测试性
- 每个模块可以独立测试
- 更容易编写单元测试
- 减少测试复杂度

### 3. 可扩展性
- 新功能可以作为新模块添加
- 平台特定代码隔离
- 更容易添加新平台支持

### 4. 代码复用
- 模块可以在其他项目中复用
- 减少代码重复
- 提高开发效率

### 5. 团队协作
- 多人可以同时开发不同模块
- 减少代码冲突
- 提高开发效率

---

## 注意事项

### 1. 循环导入
- 避免模块之间的循环依赖
- 使用依赖注入
- 必要时使用延迟导入

### 2. 向后兼容
- 保留旧的 `meow_parser.py` 入口
- 确保现有用户无需修改使用方式
- 提供迁移指南

### 3. 测试覆盖
- 每个模块拆分后都要测试
- 确保功能完整性
- 回归测试

### 4. 文档更新
- 更新 README.md
- 更新开发文档
- 添加模块说明

---

## 时间估算

- 阶段1：准备工作 - 30分钟
- 阶段2：核心模块 - 1小时
- 阶段3：UI模块 - 2小时
- 阶段4：平台模块 - 1小时
- 阶段5：主应用 - 1小时
- 阶段6：测试验证 - 1小时

**总计：约6-7小时**

---

## 下一步

1. 确认重构计划
2. 创建新的目录结构
3. 逐步拆分模块
4. 测试验证
5. 更新文档

---

**注意**：重构过程中要保持代码可运行状态，采用渐进式重构策略。
