# MeowParser 重构实施指南

## 快速开始

### 选项1：自动重构（推荐）
```bash
# 运行重构脚本（待创建）
python scripts/refactor.py
```

### 选项2：手动重构
按照本文档逐步执行

---

## 详细步骤

### 步骤1：创建目录结构

```bash
# 创建主包目录
mkdir meow_parser
mkdir meow_parser/core
mkdir meow_parser/ui
mkdir meow_parser/platform

# 创建 __init__.py 文件
touch meow_parser/__init__.py
touch meow_parser/core/__init__.py
touch meow_parser/ui/__init__.py
touch meow_parser/platform/__init__.py
```

---

### 步骤2：创建 constants.py

**文件：`meow_parser/constants.py`**

从 `meow_parser.py` 提取：
- 第 28-30 行：平台检测
- 添加其他常量

```python
"""常量定义"""
import sys

# 平台检测
IS_WINDOWS = sys.platform == 'win32'
IS_LINUX = sys.platform.startswith('linux')
IS_MACOS = sys.platform == 'darwin'

# 配置路径
CONFIG_DIR = ".kiro/rules"
WINDOW_SETTINGS_FILE = "window_settings.json"
OLD_CONFIG_FILE = "replacement_rules.json"

# 版本信息
VERSION = "2.2.0"
APP_NAME = "MeowParser"
ORG_NAME = "MeowParser"

# 默认配置
DEFAULT_CONFIG_NAME = "default.json"
```

---

### 步骤3：拆分 core/instance_lock.py

**文件：`meow_parser/core/instance_lock.py`**

从 `meow_parser.py` 提取：
- 第 41-74 行：`check_single_instance()` 函数

```python
"""单实例检查模块"""
import os
import ctypes
from pathlib import Path
import psutil
from ..constants import IS_WINDOWS

def check_single_instance():
    """检查是否已有实例运行"""
    if IS_WINDOWS:
        # Windows 实现
        ...
    else:
        # Linux/macOS 实现
        ...
```

---

### 步骤4：拆分 core/config_manager.py

**文件：`meow_parser/core/config_manager.py`**

从 `meow_parser.py` 提取：
- 第 749-951 行：`ConfigFileManager` 类

```python
"""配置文件管理模块"""
import json
from pathlib import Path
from datetime import datetime

class ConfigFileManager:
    """配置文件管理器"""
    
    def __init__(self, config_dir=".kiro/rules"):
        ...
```

---

### 步骤5：拆分 core/text_processor.py

**文件：`meow_parser/core/text_processor.py`**

从 `meow_parser.py` 提取：
- 第 954-985 行：`TextProcessor` 类

```python
"""文本处理引擎"""
import re

class TextProcessor:
    """文本处理引擎"""
    
    def __init__(self, config_manager):
        ...
```

---

### 步骤6：拆分 ui/debug_window.py

**文件：`meow_parser/ui/debug_window.py`**

从 `meow_parser.py` 提取：
- 第 2026-2091 行：`DebugWindow` 类

```python
"""调试窗口模块"""
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QTextEdit, QPushButton, QLineEdit
)

class DebugWindow(QWidget):
    """调试窗口"""
    
    def __init__(self, parent_app):
        ...
```

---

### 步骤7：拆分 ui/floating_window.py

**文件：`meow_parser/ui/floating_window.py`**

从 `meow_parser.py` 提取：
- 第 76-432 行：`FloatingInputWindow` 类

```python
"""悬浮输入窗口模块"""
import time
import threading
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
import keyboard
from ..constants import IS_WINDOWS

if IS_WINDOWS:
    import win32gui
    import win32api
    import win32con

class FloatingInputWindow(QWidget):
    """悬浮输入窗口"""
    
    show_signal = pyqtSignal(int, int, object)
    
    def __init__(self, parent_app):
        ...
```

---

### 步骤8：拆分 ui/window_selector.py

**文件：`meow_parser/ui/window_selector.py`**

从 `meow_parser.py` 提取：
- 第 435-746 行：`WindowSelector` 类

```python
"""窗口管理器模块"""
import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
import psutil
from ..constants import IS_WINDOWS, IS_LINUX

if IS_WINDOWS:
    import win32gui
    import win32process

class WindowSelector(QWidget):
    """窗口管理器（非模态窗口）"""
    
    update_signal = pyqtSignal(dict)
    
    def __init__(self, parent, allowed_windows, save_callback):
        ...
```

---

### 步骤9：拆分 ui/config_editor.py

**文件：`meow_parser/ui/config_editor.py`**

从 `meow_parser.py` 提取：
- 第 988-1071 行：`RuleEditDialog` 类
- 第 1074-1358 行：`ConfigFileEditor` 类

```python
"""配置文件编辑器模块"""
import re
from PyQt6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
    QCheckBox, QMessageBox, QComboBox, QFileDialog, QInputDialog
)
from PyQt6.QtCore import Qt

class RuleEditDialog(QDialog):
    """规则编辑对话框"""
    ...

class ConfigFileEditor(QWidget):
    """配置文件编辑器"""
    ...
```

---

### 步骤10：拆分 ui/rule_editor.py

**文件：`meow_parser/ui/rule_editor.py`**

从 `meow_parser.py` 提取：
- 第 1361-1932 行：`ReplacementRuleEditor` 类
- 第 1935-2023 行：`RuleDialog` 类

```python
"""旧版规则编辑器模块（兼容）"""
import os
import json
import re
from PyQt6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
    QCheckBox, QMessageBox, QFileDialog, QInputDialog
)
from PyQt6.QtCore import Qt

class ReplacementRuleEditor(QWidget):
    """替换规则编辑器（非模态窗口）"""
    ...

class RuleDialog(QDialog):
    """规则编辑对话框"""
    ...
```

---

### 步骤11：拆分 ui/tray_icon.py

**文件：`meow_parser/ui/tray_icon.py`**

从 `meow_parser.py` 提取：
- 第 2155-2168 行：`create_icon()` 方法
- 第 2169-2214 行：`setup_tray()` 方法

```python
"""系统托盘图标管理模块"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QAction
from PyQt6.QtCore import Qt

class TrayIconManager:
    """系统托盘图标管理器"""
    
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.tray_icon = None
        self.toggle_action = None
    
    def create_icon(self, color):
        """创建托盘图标"""
        ...
    
    def setup_tray(self):
        """设置系统托盘"""
        ...
    
    def update_icon(self, enabled):
        """更新图标状态"""
        ...
```

---

### 步骤12：拆分 platform/windows.py

**文件：`meow_parser/platform/windows.py`**

提取 Windows 特定功能：

```python
"""Windows 平台特定功能"""
import win32gui
import win32process
import win32api
import win32con
import psutil

def get_active_window_info():
    """获取当前活动窗口信息"""
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return None
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        title = win32gui.GetWindowText(hwnd)
        if not title:
            return None
        process_name = psutil.Process(pid).name()
        window_key = f"{process_name} - {title}"
        return {'hwnd': hwnd, 'pid': pid, 'title': window_key}
    except Exception as e:
        print(f"获取窗口信息错误: {e}")
        return None

def enumerate_windows(callback):
    """枚举所有窗口"""
    ...

def set_foreground_window(hwnd):
    """设置前台窗口"""
    ...

def get_cursor_pos():
    """获取鼠标位置"""
    ...

def mouse_click(x, y):
    """模拟鼠标点击"""
    ...
```

---

### 步骤13：拆分 platform/linux.py

**文件：`meow_parser/platform/linux.py`**

提取 Linux 特定功能：

```python
"""Linux 平台特定功能"""
import subprocess
import psutil

def get_active_window_info():
    """获取当前活动窗口信息"""
    try:
        # 获取活动窗口 ID
        result = subprocess.run(['xdotool', 'getactivewindow'], 
                              capture_output=True, text=True, timeout=1)
        if result.returncode != 0:
            return None
        
        window_id = result.stdout.strip()
        if not window_id:
            return None
        
        # 获取窗口标题
        result = subprocess.run(['xdotool', 'getwindowname', window_id],
                              capture_output=True, text=True, timeout=1)
        if result.returncode != 0:
            return None
        
        title = result.stdout.strip()
        if not title:
            return None
        
        # 获取窗口 PID
        result = subprocess.run(['xdotool', 'getwindowpid', window_id],
                              capture_output=True, text=True, timeout=1)
        pid = None
        process_name = "Unknown"
        if result.returncode == 0:
            try:
                pid = int(result.stdout.strip())
                process_name = psutil.Process(pid).name()
            except:
                pass
        
        window_key = f"{process_name} - {title}"
        return {'hwnd': window_id, 'pid': pid, 'title': window_key}
    except FileNotFoundError:
        print("错误: 未安装 xdotool")
        return None
    except Exception as e:
        print(f"Linux 窗口信息获取错误: {e}")
        return None

def enumerate_windows():
    """枚举所有窗口"""
    ...

def set_foreground_window(window_id):
    """设置前台窗口"""
    ...

def get_cursor_pos():
    """获取鼠标位置"""
    ...

def mouse_click(x, y):
    """模拟鼠标点击"""
    ...
```

---

### 步骤14：创建 app.py

**文件：`meow_parser/app.py`**

从 `meow_parser.py` 提取：
- 第 2094-2800 行：`MeowParser` 类

```python
"""主应用模块"""
import os
import json
import time
import ctypes
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QMessageBox
import keyboard

from .constants import IS_WINDOWS, IS_LINUX
from .core.instance_lock import check_single_instance
from .core.config_manager import ConfigFileManager
from .core.text_processor import TextProcessor
from .ui.floating_window import FloatingInputWindow
from .ui.window_selector import WindowSelector
from .ui.config_editor import ConfigFileEditor
from .ui.rule_editor import ReplacementRuleEditor
from .ui.debug_window import DebugWindow
from .ui.tray_icon import TrayIconManager

if IS_WINDOWS:
    from .platform import windows as platform
elif IS_LINUX:
    from .platform import linux as platform

class MeowParser(QObject):
    """主应用类"""
    
    log_signal = pyqtSignal(str)
    
    def __init__(self):
        ...
```

---

### 步骤15：创建 __main__.py

**文件：`meow_parser/__main__.py`**

从 `meow_parser.py` 提取：
- 第 2803-2820 行：`main()` 函数

```python
"""程序入口"""
import sys
from PyQt6.QtWidgets import QApplication
import qdarktheme
from .app import MeowParser
from .constants import APP_NAME, ORG_NAME

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # 设置应用信息
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)
    
    # 应用 PyQtDarkTheme 主题（跟随系统）
    qdarktheme.setup_theme("auto")
    
    # 创建主应用
    meow_app = MeowParser()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

---

### 步骤16：更新包的 __init__.py

**文件：`meow_parser/__init__.py`**

```python
"""
MeowParser - 喵语解析器
智能文本处理工具
"""

from .app import MeowParser
from .constants import VERSION, APP_NAME

__version__ = VERSION
__app_name__ = APP_NAME

__all__ = ['MeowParser', '__version__', '__app_name__']
```

---

### 步骤17：创建兼容入口

**文件：`meow_parser.py`（新版本，替换旧文件）**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MeowParser - 兼容入口
为了向后兼容，保留此文件
实际代码已迁移到 meow_parser 包

使用方法：
    python meow_parser.py
    或
    python -m meow_parser
"""

from meow_parser.__main__ import main

if __name__ == "__main__":
    main()
```

---

### 步骤18：更新子包的 __init__.py

**文件：`meow_parser/core/__init__.py`**
```python
"""核心功能模块"""
from .config_manager import ConfigFileManager
from .text_processor import TextProcessor
from .instance_lock import check_single_instance

__all__ = ['ConfigFileManager', 'TextProcessor', 'check_single_instance']
```

**文件：`meow_parser/ui/__init__.py`**
```python
"""UI组件模块"""
from .floating_window import FloatingInputWindow
from .window_selector import WindowSelector
from .config_editor import ConfigFileEditor, RuleEditDialog
from .rule_editor import ReplacementRuleEditor, RuleDialog
from .debug_window import DebugWindow
from .tray_icon import TrayIconManager

__all__ = [
    'FloatingInputWindow',
    'WindowSelector',
    'ConfigFileEditor',
    'RuleEditDialog',
    'ReplacementRuleEditor',
    'RuleDialog',
    'DebugWindow',
    'TrayIconManager'
]
```

**文件：`meow_parser/platform/__init__.py`**
```python
"""平台特定功能模块"""
import sys

IS_WINDOWS = sys.platform == 'win32'
IS_LINUX = sys.platform.startswith('linux')
IS_MACOS = sys.platform == 'darwin'

if IS_WINDOWS:
    from . import windows as current_platform
elif IS_LINUX:
    from . import linux as current_platform
elif IS_MACOS:
    from . import macos as current_platform
else:
    current_platform = None

__all__ = ['current_platform']
```

---

## 测试清单

重构完成后，测试以下功能：

- [ ] 程序启动（`python meow_parser.py`）
- [ ] 程序启动（`python -m meow_parser`）
- [ ] 系统托盘图标显示
- [ ] 启用/禁用功能
- [ ] 悬浮窗弹出
- [ ] 文本替换功能
- [ ] 窗口管理器
- [ ] 配置文件编辑器
- [ ] 调试窗口
- [ ] 快捷键功能
- [ ] 配置导入/导出
- [ ] 单实例检查

---

## 常见问题

### Q: 重构后旧的使用方式还能用吗？
A: 可以。保留了 `meow_parser.py` 作为兼容入口。

### Q: 如何回滚到旧版本？
A: 备份了 `meow_parser.py.backup`，可以恢复。

### Q: 导入路径改变了吗？
A: 对于最终用户，使用方式不变。对于开发者，可以使用新的模块化导入。

---

## 下一步

1. 备份当前代码
2. 按步骤执行重构
3. 逐步测试每个模块
4. 更新文档
5. 发布新版本

---

**重要提示**：重构过程中保持代码可运行，采用渐进式策略！
