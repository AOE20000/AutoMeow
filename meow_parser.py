#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MeowParser - PyQt6 版本
喵语解析器 - 跨平台版本
"""

import sys
import os
import json
import time
import re
import threading
import ctypes
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QWidget, QVBoxLayout, 
    QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel,
    QTreeWidget, QTreeWidgetItem, QDialog, QCheckBox, QMessageBox,
    QFrame, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QAction

import keyboard
import psutil
import qdarktheme

# 平台检测
IS_WINDOWS = sys.platform == 'win32'
IS_LINUX = sys.platform.startswith('linux')

if IS_WINDOWS:
    import win32gui
    import win32process
    import win32api
    import win32con


def check_single_instance():
    """检查是否已有实例运行"""
    if IS_WINDOWS:
        event_name = r"Global\MeowParser_SingleInstance_Event"
        try:
            event = ctypes.windll.kernel32.CreateEventW(None, True, False, event_name)
            if event == 0:
                return False
            if ctypes.get_last_error() == 183:
                ctypes.windll.kernel32.CloseHandle(event)
                return False
            return event
        except:
            return False
    else:
        # Linux: 使用文件锁
        lock_file = Path.home() / '.meowparser.lock'
        try:
            if lock_file.exists():
                # 检查进程是否还在运行
                try:
                    with open(lock_file, 'r') as f:
                        pid = int(f.read().strip())
                    if psutil.pid_exists(pid):
                        return False
                except:
                    pass
            # 写入当前进程 PID
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))
            return lock_file
        except:
            return False


class FloatingInputWindow(QWidget):
    """悬浮输入窗口"""
    
    # 添加信号用于线程安全的显示
    show_signal = pyqtSignal(int, int, object)
    
    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app
        self.target_window = None
        self.click_pos = None
        self.is_processing = False
        self.send_lock = threading.Lock()  # 添加线程锁
        
        # 连接信号到槽
        self.show_signal.connect(self._do_show_at)
        
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 设置窗口标志（移除 WindowDoesNotAcceptFocus）
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # 确保窗口不透明
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        
        # 设置固定大小，避免大小为0
        self.setFixedSize(500, 80)
        
        # 使用内联样式，完全覆盖主题
        self.setStyleSheet("""
            FloatingInputWindow {
                background-color: #1e1e1e;
                border: 3px solid #0078d4;
                border-radius: 6px;
            }
        """)
        
        # 创建布局
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)
        
        # 创建输入框
        self.entry = QLineEdit()
        self.entry.setFixedHeight(50)
        self.entry.setPlaceholderText("输入内容 (回车发送 | Ctrl+回车原始 | ESC取消)")
        
        # 输入框样式 - 使用内联样式
        self.entry.setStyleSheet("""
            QLineEdit {
                background-color: #252526;
                color: #cccccc;
                border: 2px solid #3e3e42;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14pt;
                font-family: 'Microsoft YaHei UI', 'Segoe UI', 'Arial';
                selection-background-color: #0078d4;
                selection-color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
                background-color: #1e1e1e;
            }
        """)
        
        self.entry.returnPressed.connect(self.on_enter)
        layout.addWidget(self.entry)
        
        self.setLayout(layout)
        
        # 安装事件过滤器
        self.entry.installEventFilter(self)
        
        print("悬浮窗 UI 初始化完成")
        
    def eventFilter(self, obj, event):
        """事件过滤器"""
        if obj == self.entry:
            # 处理 Escape 键
            if event.type() == event.Type.KeyPress:
                if event.key() == Qt.Key.Key_Escape:
                    self.on_escape()
                    return True
                # 处理 Ctrl+Enter
                elif event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    self.on_ctrl_enter()
                    return True
        return super().eventFilter(obj, event)
    
    def show_at(self, x, y, target_window=None):
        """在指定位置显示悬浮窗（线程安全）"""
        # 使用信号发送到主线程
        print(f"show_at 被调用: ({x}, {y})")
        self.show_signal.emit(x, y, target_window)
    
    def _do_show_at(self, x, y, target_window=None):
        """实际显示悬浮窗（在主线程中执行）"""
        if self.is_processing:
            print("悬浮窗正在处理中，跳过显示")
            return
        
        print(f"\n=== 显示悬浮窗（主线程） ===")
        print(f"目标位置: ({x}, {y})")
        
        self.target_window = target_window
        self.click_pos = (x, y)
        
        # 暂停键盘监听，避免卡死
        try:
            keyboard.unhook_all()
            print("已暂停键盘监听")
        except Exception as e:
            print(f"暂停键盘监听错误: {e}")
        
        # 获取屏幕信息
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        print(f"屏幕大小: {screen_geometry.width()}x{screen_geometry.height()}")
        
        # 确保窗口大小正确
        window_width = 500
        window_height = 80
        print(f"窗口大小: {window_width}x{window_height}")
        
        # 计算位置，避免超出屏幕
        final_x = min(x + 10, screen_geometry.width() - window_width - 10)
        final_y = min(y + 10, screen_geometry.height() - window_height - 10)
        final_x = max(10, final_x)
        final_y = max(10, final_y)
        
        print(f"最终位置: ({final_x}, {final_y})")
        
        # 先隐藏窗口（如果已显示）
        if self.isVisible():
            self.hide()
            QApplication.processEvents()
        
        # 设置位置和大小
        self.setGeometry(final_x, final_y, window_width, window_height)
        
        # 清空输入框
        self.entry.clear()
        
        # 显示窗口 - 使用 showNormal 而不是 show
        self.showNormal()
        
        # 强制创建窗口句柄
        if not self.windowHandle():
            self.create()
        
        # 请求暴露窗口
        if self.windowHandle():
            self.windowHandle().requestActivate()
        
        # 强制刷新多次
        for i in range(10):
            self.update()
            self.repaint()
            QApplication.processEvents()
        
        # 提升窗口层级
        self.raise_()
        self.activateWindow()
        
        # 使用 Windows API 强制置顶（如果是 Windows）
        if IS_WINDOWS:
            try:
                import win32gui
                import win32con
                hwnd = int(self.winId())
                # 强制置顶并显示
                win32gui.SetWindowPos(
                    hwnd,
                    win32con.HWND_TOPMOST,
                    final_x, final_y, window_width, window_height,
                    win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE
                )
                # 再次激活
                win32gui.SetForegroundWindow(hwnd)
                print("使用 Windows API 强制置顶")
            except Exception as e:
                print(f"Windows API 错误: {e}")
        
        # 设置焦点到输入框
        self.entry.setFocus(Qt.FocusReason.OtherFocusReason)
        
        # 再次强制刷新
        QApplication.processEvents()
        
        # 验证状态
        print(f"窗口状态:")
        print(f"  - isVisible: {self.isVisible()}")
        print(f"  - isActiveWindow: {self.isActiveWindow()}")
        print(f"  - geometry: {self.geometry()}")
        print(f"  - windowHandle.isExposed: {self.windowHandle().isExposed() if self.windowHandle() else 'None'}")
        print(f"===================\n")
        
    def on_enter(self):
        """回车键 - 应用替换规则"""
        # 使用线程锁防止重复处理
        if not self.send_lock.acquire(blocking=False):
            return
        
        if self.is_processing:
            self.send_lock.release()
            return
        
        self.is_processing = True
        text = self.entry.text()
        self.hide()
        
        # 恢复键盘监听
        self._resume_keyboard_listener()
        
        # 在后台线程处理
        threading.Thread(target=self._send_text, args=(text, True), daemon=True).start()
    
    def on_ctrl_enter(self):
        """Ctrl+回车 - 发送原始内容"""
        # 使用线程锁防止重复处理
        if not self.send_lock.acquire(blocking=False):
            return
        
        if self.is_processing:
            self.send_lock.release()
            return
        
        self.is_processing = True
        text = self.entry.text()
        self.hide()
        
        # 恢复键盘监听
        self._resume_keyboard_listener()
        
        threading.Thread(target=self._send_text, args=(text, False), daemon=True).start()
    
    def on_escape(self):
        """ESC键 - 取消输入"""
        print("ESC 键按下，关闭悬浮窗")
        self.hide()
        
        # 恢复键盘监听
        self._resume_keyboard_listener()
        
        if self.target_window and IS_WINDOWS:
            try:
                win32gui.SetForegroundWindow(self.target_window)
            except:
                pass
    
    def _resume_keyboard_listener(self):
        """恢复键盘监听"""
        try:
            if self.parent_app.enabled:
                print("恢复键盘监听...")
                keyboard.hook(self.parent_app.on_key_event)
                keyboard.add_hotkey('ctrl+shift+alt+m', self.parent_app.toggle_current_window)
                print("键盘监听已恢复")
        except Exception as e:
            print(f"恢复键盘监听错误: {e}")
    
    def _send_text(self, text, apply_rules):
        """发送文本到目标位置"""
        try:
            # 应用替换规则
            if apply_rules:
                final_text = self.parent_app.process_text(text)
            else:
                final_text = text
            
            self.parent_app.debug_log(f"原文本: {text}")
            self.parent_app.debug_log(f"处理后: {final_text}")
            
            # 等待悬浮窗完全隐藏
            time.sleep(0.15)
            
            # 恢复焦点（改进：添加验证和重试机制）
            focus_restored = False
            if self.click_pos and self.target_window:
                if IS_WINDOWS:
                    try:
                        # 尝试恢复焦点（最多重试3次）
                        for attempt in range(3):
                            win32gui.SetForegroundWindow(self.target_window)
                            time.sleep(0.05)
                            
                            # 验证焦点是否恢复
                            current_hwnd = win32gui.GetForegroundWindow()
                            if current_hwnd == self.target_window:
                                focus_restored = True
                                break
                            time.sleep(0.05)
                        
                        if focus_restored:
                            # 点击原位置
                            x, y = self.click_pos
                            win32api.SetCursorPos((x, y))
                            time.sleep(0.05)
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                            time.sleep(0.03)
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                            time.sleep(0.1)
                        else:
                            self.parent_app.debug_log("警告: 焦点恢复失败")
                    except Exception as e:
                        self.parent_app.debug_log(f"焦点恢复错误: {e}")
                else:
                    # Linux: 使用 xdotool 恢复焦点
                    try:
                        import subprocess
                        # 激活窗口
                        subprocess.run(['xdotool', 'windowactivate', str(self.target_window)],
                                     timeout=1, check=False)
                        time.sleep(0.1)
                        
                        # 点击位置
                        x, y = self.click_pos
                        subprocess.run(['xdotool', 'mousemove', str(x), str(y)],
                                     timeout=1, check=False)
                        time.sleep(0.05)
                        subprocess.run(['xdotool', 'click', '1'],
                                     timeout=1, check=False)
                        time.sleep(0.1)
                        focus_restored = True
                    except Exception as e:
                        self.parent_app.debug_log(f"Linux 焦点恢复错误: {e}")
            
            # 输入文本
            if final_text:
                try:
                    keyboard.write(final_text)
                    time.sleep(0.05)
                except Exception as e:
                    self.parent_app.debug_log(f"输入失败: {e}")
            
            # 发送回车
            time.sleep(0.05)
            keyboard.press_and_release('enter')
            
        except Exception as e:
            self.parent_app.debug_log(f"发送文本错误: {e}")
        finally:
            self.is_processing = False
            # 释放线程锁
            try:
                self.send_lock.release()
            except:
                pass


class WindowSelector(QWidget):
    """窗口管理器（非模态窗口）"""
    
    # 添加信号用于线程间通信
    update_signal = pyqtSignal(dict)
    
    def __init__(self, parent, allowed_windows, save_callback):
        super().__init__(parent)
        self.allowed_windows = allowed_windows
        self.save_callback = save_callback
        self.window_list = {}
        self._refreshing = False
        
        # 连接信号
        self.update_signal.connect(self.update_tree)
        
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("窗口管理")
        self.setGeometry(100, 100, 800, 600)
        
        # 设置窗口标志（独立窗口）
        self.setWindowFlags(Qt.WindowType.Window)
        
        layout = QVBoxLayout()
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索窗口：")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.filter_windows)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # 窗口列表
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['进程名', '窗口标题', '状态'])
        self.tree.setColumnWidth(0, 150)
        self.tree.setColumnWidth(1, 500)
        self.tree.setColumnWidth(2, 100)
        self.tree.itemDoubleClicked.connect(self.toggle_window)
        
        # 启用排序功能
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(2, Qt.SortOrder.DescendingOrder)  # 默认按状态降序排序（已启用在前）
        
        layout.addWidget(self.tree)
        
        # 提示标签
        hint_label = QLabel("双击窗口项目可切换启用状态 | 点击列标题可排序")
        hint_label.setStyleSheet("color: gray;")
        layout.addWidget(hint_label)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("刷新窗口列表")
        self.refresh_btn.clicked.connect(self.refresh_windows)
        button_layout.addWidget(self.refresh_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 延迟刷新，确保窗口已显示
        QTimer.singleShot(100, self.refresh_windows)
    
    def closeEvent(self, event):
        """关闭事件 - 保存设置"""
        if self.save_callback:
            self.save_callback()
        event.accept()
    
    def get_process_name(self, pid):
        """获取进程名"""
        try:
            return psutil.Process(pid).name()
        except:
            return "未知进程"
    
    def toggle_window(self, item, column):
        """切换窗口启用状态"""
        try:
            process_name = item.text(0)
            title = item.text(1)
            window_key = f"{process_name} - {title}"
            
            # 检查是否是调试窗口（改进：更精确的匹配）
            if title.strip() in ["MeowParser 调试窗口", "MeowParser调试窗口"]:
                # 调试窗口保持启用，不允许禁用
                if window_key not in self.allowed_windows:
                    self.allowed_windows[window_key] = True
                    self.refresh_windows()
                return
            
            # 切换状态
            if window_key in self.allowed_windows:
                del self.allowed_windows[window_key]
            else:
                self.allowed_windows[window_key] = True
            
            self.refresh_windows()
        except Exception as e:
            print(f"切换窗口状态错误: {e}")
    
    def refresh_windows(self):
        """刷新窗口列表"""
        # 防止重复刷新
        if self._refreshing:
            print("已在刷新中，跳过")
            return
        
        print("开始刷新窗口列表...")
        self._refreshing = True
        
        # 禁用刷新按钮，防止重复点击
        if hasattr(self, 'refresh_btn'):
            self.refresh_btn.setEnabled(False)
        
        self.tree.clear()
        self.window_list.clear()
        
        # 添加加载提示
        loading_item = QTreeWidgetItem(self.tree)
        loading_item.setText(1, "正在加载窗口列表...")
        
        # 在后台线程中枚举窗口
        def do_refresh():
            temp_list = {}
            
            try:
                if IS_WINDOWS:
                    print("Windows 平台，开始枚举窗口...")
                    
                    # 获取当前窗口管理器的 hwnd，避免枚举自己导致死锁
                    try:
                        from PyQt6.QtGui import QWindow
                        window_handle = self.windowHandle()
                        if window_handle:
                            self_hwnd = int(window_handle.winId())
                        else:
                            self_hwnd = None
                    except:
                        self_hwnd = None
                    
                    print(f"窗口管理器 hwnd: {self_hwnd}")
                    
                    def enum_windows_callback(hwnd, _):
                        try:
                            # 跳过窗口管理器自己
                            if self_hwnd and hwnd == self_hwnd:
                                return True
                            
                            if win32gui.IsWindowVisible(hwnd):
                                title = win32gui.GetWindowText(hwnd)
                                if title and len(title.strip()) > 0:
                                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                                    process_name = self.get_process_name(pid)
                                    window_key = f"{process_name} - {title}"
                                    temp_list[window_key] = hwnd
                        except Exception as e:
                            print(f"枚举窗口错误: {e}")
                        return True
                    
                    try:
                        win32gui.EnumWindows(enum_windows_callback, None)
                        print(f"枚举完成，找到 {len(temp_list)} 个窗口")
                    except Exception as e:
                        print(f"EnumWindows 错误: {e}")
                else:
                    print("Linux 平台，开始枚举窗口...")
                    # Linux: 使用 wmctrl 或 xdotool
                    try:
                        import subprocess
                        result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True, timeout=2)
                        if result.returncode == 0:
                            for line in result.stdout.strip().split('\n'):
                                parts = line.split(None, 3)
                                if len(parts) >= 4:
                                    window_id = parts[0]
                                    title = parts[3]
                                    # 尝试获取进程名
                                    try:
                                        pid_result = subprocess.run(['xdotool', 'getwindowpid', window_id],
                                                                  capture_output=True, text=True, timeout=1)
                                        if pid_result.returncode == 0:
                                            pid = int(pid_result.stdout.strip())
                                            process_name = self.get_process_name(pid)
                                        else:
                                            process_name = "Unknown"
                                    except:
                                        process_name = "Unknown"
                                    
                                    window_key = f"{process_name} - {title}"
                                    temp_list[window_key] = window_id
                            print(f"枚举完成，找到 {len(temp_list)} 个窗口")
                    except FileNotFoundError:
                        print("wmctrl 未安装")
                    except Exception as e:
                        print(f"Linux 窗口枚举错误: {e}")
            except Exception as e:
                print(f"刷新窗口列表错误: {e}")
            finally:
                # 使用信号发送结果到主线程
                print(f"发送信号更新 UI，窗口数: {len(temp_list)}")
                try:
                    self.update_signal.emit(temp_list)
                except Exception as e:
                    print(f"发送信号错误: {e}")
        
        # 启动后台线程
        thread = threading.Thread(target=do_refresh, daemon=True)
        thread.start()
        print("后台线程已启动")
    
    def update_tree(self, temp_list):
        """更新树形控件"""
        print(f"update_tree 被调用，窗口数: {len(temp_list)}")
        try:
            # 临时禁用排序以提高性能
            self.tree.setSortingEnabled(False)
            self.tree.clear()
            self.window_list = temp_list
            
            if not temp_list:
                # 没有找到窗口
                no_window_item = QTreeWidgetItem(self.tree)
                no_window_item.setText(1, "未找到窗口")
                print("未找到任何窗口")
                return
            
            added_count = 0
            for window_key, hwnd in self.window_list.items():
                try:
                    parts = window_key.split(" - ", 1)
                    if len(parts) != 2:
                        continue
                    
                    process_name, title = parts
                    
                    # 检查是否是调试窗口（改进：更精确的匹配）
                    is_debug_window = title.strip() in ["MeowParser 调试窗口", "MeowParser调试窗口"]
                    
                    if is_debug_window:
                        self.allowed_windows[window_key] = True
                        enabled = "✓ 已启用（锁定）"
                        sort_key = "0"  # 用于排序，确保锁定项在最前
                    else:
                        if window_key in self.allowed_windows:
                            enabled = "✓ 已启用"
                            sort_key = "1"  # 已启用排第二
                        else:
                            enabled = "✗ 未启用"
                            sort_key = "2"  # 未启用排最后
                    
                    item = QTreeWidgetItem(self.tree)
                    item.setText(0, process_name)
                    item.setText(1, title)
                    item.setText(2, enabled)
                    
                    # 设置隐藏的排序键（用于正确排序）
                    item.setData(2, Qt.ItemDataRole.UserRole, sort_key)
                    
                    added_count += 1
                except Exception as e:
                    print(f"添加窗口项错误: {e}")
            
            print(f"成功添加 {added_count} 个窗口到列表")
            
            # 重新启用排序
            self.tree.setSortingEnabled(True)
            # 按状态列降序排序（已启用在前）
            self.tree.sortByColumn(2, Qt.SortOrder.DescendingOrder)
            
        except Exception as e:
            print(f"更新树形控件错误: {e}")
        finally:
            self._refreshing = False
            # 重新启用刷新按钮
            if hasattr(self, 'refresh_btn'):
                self.refresh_btn.setEnabled(True)
            print("刷新完成")
    
    def filter_windows(self, search_text):
        """过滤窗口列表"""
        search_text = search_text.lower()
        
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            process_name = item.text(0).lower()
            title = item.text(1).lower()
            
            # 显示或隐藏项目
            if search_text in process_name or search_text in title:
                item.setHidden(False)
            else:
                item.setHidden(True)


# ============================================================================
# 配置文件管理系统（新方案）
# ============================================================================

class ConfigFileManager:
    """配置文件管理器"""
    
    def __init__(self, config_dir=".kiro/rules"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.current_config = None
        self.current_config_path = None
        
        # 确保有默认配置
        self._ensure_default_config()
    
    def _ensure_default_config(self):
        """确保存在默认配置"""
        default_path = self.config_dir / "default.json"
        if not default_path.exists():
            from datetime import datetime
            default_config = {
                "name": "喵语转换（默认）",
                "version": "1.0.0",
                "description": "将文本转换为可爱的喵语",
                "author": "MeowParser",
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "groups": [
                    {
                        "name": "喵语转换",
                        "description": "在标点前添加喵",
                        "collapsed": False,
                        "rules": [
                            {
                                "enabled": True,
                                "pattern": "([^喵])([。，！？；、）（：])",
                                "replacement": "\\1喵\\2",
                                "is_regex": True,
                                "description": "标点前添加喵"
                            },
                            {
                                "enabled": True,
                                "pattern": "([^喵。，！？；、）（：\\n])(\\n)",
                                "replacement": "\\1喵\\2",
                                "is_regex": True,
                                "description": "换行前添加喵"
                            },
                            {
                                "enabled": True,
                                "pattern": "([^。，！？；、）（：\\n])$",
                                "replacement": "\\1喵",
                                "is_regex": True,
                                "description": "句尾添加喵"
                            }
                        ]
                    }
                ]
            }
            
            with open(default_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
    
    def list_configs(self):
        """列出所有配置文件"""
        configs = []
        for file_path in sorted(self.config_dir.glob("*.json")):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    configs.append({
                        "path": file_path,
                        "name": config.get("name", file_path.stem),
                        "description": config.get("description", ""),
                        "version": config.get("version", "1.0.0"),
                        "updated": config.get("updated", ""),
                        "rule_count": sum(len(g.get("rules", [])) for g in config.get("groups", []))
                    })
            except Exception as e:
                print(f"加载配置文件失败 {file_path}: {e}")
        return configs
    
    def load_config(self, config_path):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.current_config = json.load(f)
                self.current_config_path = Path(config_path)
                return True
        except Exception as e:
            print(f"加载配置失败: {e}")
            return False
    
    def save_config(self, config_path=None):
        """保存配置文件"""
        if config_path is None:
            config_path = self.current_config_path
        
        if config_path is None:
            raise ValueError("未指定配置文件路径")
        
        try:
            from datetime import datetime
            # 更新时间戳
            self.current_config["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def create_config(self, name, description=""):
        """创建新配置文件"""
        from datetime import datetime
        config = {
            "name": name,
            "version": "1.0.0",
            "description": description,
            "author": "",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "groups": []
        }
        
        # 生成文件名
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        config_path = self.config_dir / f"{safe_name}.json"
        
        # 避免重名
        counter = 1
        while config_path.exists():
            config_path = self.config_dir / f"{safe_name}_{counter}.json"
            counter += 1
        
        self.current_config = config
        self.current_config_path = config_path
        self.save_config()
        
        return config_path
    
    def delete_config(self, config_path):
        """删除配置文件"""
        try:
            # 不允许删除默认配置
            if Path(config_path).name == "default.json":
                return False, "不能删除默认配置"
            
            Path(config_path).unlink()
            return True, "删除成功"
        except Exception as e:
            return False, f"删除失败: {e}"
    
    def get_all_rules(self):
        """获取当前配置的所有启用规则（扁平化，按顺序）"""
        if not self.current_config:
            return []
        
        all_rules = []
        for group in self.current_config.get("groups", []):
            for rule in group.get("rules", []):
                if rule.get("enabled", True):
                    all_rules.append(rule)
        
        return all_rules
    
    def migrate_old_config(self, old_config):
        """迁移旧配置格式"""
        from datetime import datetime
        new_config = {
            "name": "迁移的配置",
            "version": "1.0.0",
            "description": "从旧版本迁移",
            "author": "",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "groups": []
        }
        
        old_groups = old_config.get("groups", {})
        
        for group_name, group_data in old_groups.items():
            # 只迁移启用的规则组
            if not group_data.get("enabled", True):
                continue
            
            new_group = {
                "name": group_name,
                "description": "",
                "collapsed": False,
                "rules": []
            }
            
            for rule in group_data.get("rules", []):
                new_rule = {
                    "enabled": True,
                    "pattern": rule.get("pattern", ""),
                    "replacement": rule.get("replacement", ""),
                    "is_regex": rule.get("is_regex", False),
                    "description": f"{rule.get('pattern', '')} → {rule.get('replacement', '')}"
                }
                new_group["rules"].append(new_rule)
            
            new_config["groups"].append(new_group)
        
        return new_config


class TextProcessor:
    """文本处理引擎"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
    
    def process(self, text):
        """处理文本 - 按规则顺序依次应用"""
        if not text or len(text.strip()) == 0:
            return text
        
        result = text
        rules = self.config_manager.get_all_rules()
        
        for rule in rules:
            pattern = rule.get("pattern", "")
            replacement = rule.get("replacement", "")
            is_regex = rule.get("is_regex", False)
            
            if not pattern:
                continue
            
            try:
                if is_regex:
                    result = re.sub(pattern, replacement, result)
                else:
                    result = result.replace(pattern, replacement)
            except re.error as e:
                print(f"正则表达式错误 '{pattern}': {e}")
                continue
        
        return result


class RuleEditDialog(QDialog):
    """规则编辑对话框"""
    
    def __init__(self, parent, rule=None):
        super().__init__(parent)
        self.rule = rule or {}
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("编辑规则" if self.rule else "添加规则")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # 描述
        layout.addWidget(QLabel("描述:"))
        self.desc_input = QLineEdit()
        self.desc_input.setText(self.rule.get("description", ""))
        layout.addWidget(self.desc_input)
        
        # 匹配文本
        layout.addWidget(QLabel("匹配文本:"))
        self.pattern_input = QLineEdit()
        self.pattern_input.setText(self.rule.get("pattern", ""))
        layout.addWidget(self.pattern_input)
        
        # 替换为
        layout.addWidget(QLabel("替换为:"))
        self.replacement_input = QLineEdit()
        self.replacement_input.setText(self.rule.get("replacement", ""))
        layout.addWidget(self.replacement_input)
        
        # 正则表达式
        self.regex_checkbox = QCheckBox("使用正则表达式")
        self.regex_checkbox.setChecked(self.rule.get("is_regex", False))
        layout.addWidget(self.regex_checkbox)
        
        # 启用
        self.enabled_checkbox = QCheckBox("启用此规则")
        self.enabled_checkbox.setChecked(self.rule.get("enabled", True))
        layout.addWidget(self.enabled_checkbox)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def accept(self):
        """验证并接受"""
        pattern = self.pattern_input.text()
        is_regex = self.regex_checkbox.isChecked()
        
        if not pattern:
            QMessageBox.warning(self, "错误", "匹配文本不能为空")
            return
        
        # 验证正则表达式
        if is_regex:
            try:
                re.compile(pattern)
            except re.error as e:
                QMessageBox.warning(self, "正则表达式错误", f"无效的正则表达式:\n{str(e)}")
                return
        
        super().accept()
    
    def get_result(self):
        """获取结果"""
        return {
            "enabled": self.enabled_checkbox.isChecked(),
            "pattern": self.pattern_input.text(),
            "replacement": self.replacement_input.text(),
            "is_regex": self.regex_checkbox.isChecked(),
            "description": self.desc_input.text() or f"{self.pattern_input.text()} → {self.replacement_input.text()}"
        }


class ConfigFileEditor(QWidget):
    """配置文件编辑器"""
    
    def __init__(self, parent, config_manager, save_callback):
        super().__init__(parent)
        self.config_manager = config_manager
        self.save_callback = save_callback
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("替换规则管理")
        self.setGeometry(100, 100, 900, 600)
        self.setWindowFlags(Qt.WindowType.Window)
        
        layout = QVBoxLayout()
        
        # 配置文件选择器
        config_layout = QHBoxLayout()
        config_layout.addWidget(QLabel("当前配置:"))
        
        self.config_combo = QComboBox()
        self.config_combo.setMinimumWidth(300)
        self.config_combo.currentIndexChanged.connect(self.on_config_changed)
        config_layout.addWidget(self.config_combo)
        
        new_btn = QPushButton("新建")
        new_btn.clicked.connect(self.create_config)
        config_layout.addWidget(new_btn)
        
        import_btn = QPushButton("导入")
        import_btn.clicked.connect(self.import_config)
        config_layout.addWidget(import_btn)
        
        export_btn = QPushButton("导出")
        export_btn.clicked.connect(self.export_config)
        config_layout.addWidget(export_btn)
        
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_config)
        config_layout.addWidget(delete_btn)
        
        config_layout.addStretch()
        layout.addLayout(config_layout)
        
        # 规则树
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['规则', '操作'])
        self.tree.setColumnWidth(0, 600)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.tree)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        add_group_btn = QPushButton("添加规则组")
        add_group_btn.clicked.connect(self.add_group)
        button_layout.addWidget(add_group_btn)
        
        button_layout.addStretch()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save)
        button_layout.addWidget(save_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 加载配置列表
        self.refresh_config_list()
    
    def refresh_config_list(self):
        """刷新配置列表"""
        self.config_combo.blockSignals(True)
        self.config_combo.clear()
        
        configs = self.config_manager.list_configs()
        
        for config in configs:
            display_text = f"{config['name']} ({config['rule_count']}条规则)"
            if config['description']:
                display_text += f" - {config['description'][:30]}"
            
            self.config_combo.addItem(display_text, config['path'])
        
        self.config_combo.blockSignals(False)
        
        # 加载第一个配置
        if self.config_combo.count() > 0:
            self.on_config_changed(0)
    
    def on_config_changed(self, index):
        """配置文件切换"""
        if index < 0:
            return
        
        config_path = self.config_combo.itemData(index)
        if config_path:
            self.config_manager.load_config(config_path)
            self.refresh_tree()
            
            # 通知主应用配置已更改
            if self.save_callback:
                self.save_callback()
    
    def refresh_tree(self):
        """刷新规则树"""
        self.tree.clear()
        
        if not self.config_manager.current_config:
            return
        
        groups = self.config_manager.current_config.get("groups", [])
        
        for group_index, group in enumerate(groups):
            # 创建规则组节点
            group_item = QTreeWidgetItem(self.tree)
            group_name = group.get("name", f"规则组 {group_index + 1}")
            rules = group.get("rules", [])
            rule_count = len(rules)
            enabled_count = sum(1 for r in rules if r.get("enabled", True))
            
            collapsed = group.get("collapsed", False)
            icon = "▶" if collapsed else "▼"
            
            group_item.setText(0, f"{icon} {group_name} ({enabled_count}/{rule_count}条规则)")
            group_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "group", "index": group_index})
            group_item.setExpanded(not collapsed)
            
            # 添加规则
            for rule_index, rule in enumerate(rules):
                rule_item = QTreeWidgetItem(group_item)
                
                enabled = "☑" if rule.get("enabled", True) else "☐"
                description = rule.get("description", "")
                
                rule_item.setText(0, f"  {enabled} {description}")
                rule_item.setData(0, Qt.ItemDataRole.UserRole, {
                    "type": "rule",
                    "group_index": group_index,
                    "rule_index": rule_index
                })
    
    def on_item_double_clicked(self, item, column):
        """双击项目"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        if data["type"] == "group":
            # 切换折叠状态
            group_index = data["index"]
            groups = self.config_manager.current_config.get("groups", [])
            if group_index < len(groups):
                groups[group_index]["collapsed"] = not groups[group_index].get("collapsed", False)
                self.refresh_tree()
        
        elif data["type"] == "rule":
            # 编辑规则
            self.edit_rule(data["group_index"], data["rule_index"])
    
    def add_group(self):
        """添加规则组"""
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "新建规则组", "规则组名称:")
        if ok and name:
            if not self.config_manager.current_config:
                QMessageBox.warning(self, "错误", "请先选择或创建配置文件")
                return
            
            groups = self.config_manager.current_config.setdefault("groups", [])
            groups.append({
                "name": name,
                "description": "",
                "collapsed": False,
                "rules": []
            })
            
            self.refresh_tree()
            self.save()
    
    def edit_rule(self, group_index, rule_index):
        """编辑规则"""
        groups = self.config_manager.current_config.get("groups", [])
        if group_index >= len(groups):
            return
        
        rules = groups[group_index].get("rules", [])
        if rule_index >= len(rules):
            return
        
        rule = rules[rule_index]
        dialog = RuleEditDialog(self, rule)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            rules[rule_index] = dialog.get_result()
            self.refresh_tree()
            self.save()
    
    def create_config(self):
        """创建新配置"""
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "新建配置", "配置名称:")
        if ok and name:
            description, ok2 = QInputDialog.getText(self, "新建配置", "配置描述:")
            if ok2:
                self.config_manager.create_config(name, description)
                self.refresh_config_list()
    
    def import_config(self):
        """导入配置"""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入配置", "", "JSON 文件 (*.json)"
        )
        
        if file_path:
            try:
                import shutil
                dest_path = self.config_manager.config_dir / Path(file_path).name
                shutil.copy(file_path, dest_path)
                self.refresh_config_list()
                QMessageBox.information(self, "成功", "配置已导入")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入失败: {e}")
    
    def export_config(self):
        """导出配置"""
        from PyQt6.QtWidgets import QFileDialog
        if not self.config_manager.current_config_path:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出配置", "", "JSON 文件 (*.json)"
        )
        
        if file_path:
            try:
                import shutil
                shutil.copy(self.config_manager.current_config_path, file_path)
                QMessageBox.information(self, "成功", "配置已导出")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {e}")
    
    def delete_config(self):
        """删除配置"""
        if not self.config_manager.current_config_path:
            return
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除配置 '{self.config_manager.current_config['name']}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.config_manager.delete_config(
                self.config_manager.current_config_path
            )
            
            if success:
                self.refresh_config_list()
                QMessageBox.information(self, "成功", message)
            else:
                QMessageBox.warning(self, "错误", message)
    
    def save(self):
        """保存配置"""
        if self.config_manager.save_config():
            if self.save_callback:
                self.save_callback()
    
    def closeEvent(self, event):
        """关闭事件"""
        self.save()
        event.accept()


# ============================================================================
# 旧的替换规则编辑器（保留用于兼容）
# ============================================================================

class ReplacementRuleEditor(QWidget):
    """替换规则编辑器（非模态窗口）"""
    
    def __init__(self, parent, replacement_rules, save_callback):
        super().__init__(parent)
        self.replacement_rules = replacement_rules
        self.save_callback = save_callback
        self.current_group = None
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("替换规则管理")
        self.setGeometry(100, 100, 900, 600)
        
        # 设置窗口标志（独立窗口）
        self.setWindowFlags(Qt.WindowType.Window)
        
        main_layout = QHBoxLayout()
        
        # 左侧：规则组列表
        left_panel = QVBoxLayout()
        
        group_label = QLabel("规则组（双击切换启用/禁用）：")
        left_panel.addWidget(group_label)
        
        self.group_list = QTreeWidget()
        self.group_list.setHeaderLabels(['规则组', '状态'])
        self.group_list.setColumnWidth(0, 150)
        self.group_list.setColumnWidth(1, 50)
        self.group_list.itemClicked.connect(self.on_group_selected)
        self.group_list.itemDoubleClicked.connect(self.toggle_group)
        left_panel.addWidget(self.group_list)
        
        # 规则组按钮
        group_btn_layout = QHBoxLayout()
        add_group_btn = QPushButton("新建组")
        add_group_btn.clicked.connect(self.add_group)
        group_btn_layout.addWidget(add_group_btn)
        
        rename_group_btn = QPushButton("重命名")
        rename_group_btn.clicked.connect(self.rename_group)
        group_btn_layout.addWidget(rename_group_btn)
        
        delete_group_btn = QPushButton("删除组")
        delete_group_btn.clicked.connect(self.delete_group)
        group_btn_layout.addWidget(delete_group_btn)
        
        left_panel.addLayout(group_btn_layout)
        
        # 导入导出按钮
        import_export_layout = QHBoxLayout()
        import_btn = QPushButton("导入规则组")
        import_btn.clicked.connect(self.import_group)
        import_export_layout.addWidget(import_btn)
        
        export_btn = QPushButton("导出规则组")
        export_btn.clicked.connect(self.export_group)
        import_export_layout.addWidget(export_btn)
        
        left_panel.addLayout(import_export_layout)
        
        # 右侧：规则列表
        right_panel = QVBoxLayout()
        
        # 当前规则组标签
        self.current_group_label = QLabel("请选择规则组")
        self.current_group_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        right_panel.addWidget(self.current_group_label)
        
        # 规则列表
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['优先级', '匹配文本', '替换为', '类型'])
        self.tree.setColumnWidth(0, 60)
        self.tree.setColumnWidth(1, 180)
        self.tree.setColumnWidth(2, 180)
        self.tree.setColumnWidth(3, 80)
        right_panel.addWidget(self.tree)
        
        # 规则按钮
        rule_btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("添加规则")
        add_btn.clicked.connect(self.add_rule)
        rule_btn_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("编辑规则")
        edit_btn.clicked.connect(self.edit_rule)
        rule_btn_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("删除规则")
        delete_btn.clicked.connect(self.delete_rule)
        rule_btn_layout.addWidget(delete_btn)
        
        up_btn = QPushButton("上移")
        up_btn.clicked.connect(self.move_up)
        rule_btn_layout.addWidget(up_btn)
        
        down_btn = QPushButton("下移")
        down_btn.clicked.connect(self.move_down)
        rule_btn_layout.addWidget(down_btn)
        
        right_panel.addLayout(rule_btn_layout)
        
        # 说明文本
        info_text = ("说明：规则按顺序依次应用，每个规则会替换文本中所有匹配的位置。\n"
                    "文本示例：\"我\" → \"喵\"，则\"我的\"会变成\"喵的\"。\n"
                    "正则示例：\"\\d+\" → \"数字\"，则\"123\"会变成\"数字\"。")
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; padding: 10px;")
        right_panel.addWidget(info_label)
        
        # 关闭按钮
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        close_layout.addWidget(close_btn)
        right_panel.addLayout(close_layout)
        
        # 组合布局
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMaximumWidth(250)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        
        self.setLayout(main_layout)
        
        # 刷新规则组列表
        self.refresh_groups()
    
    def closeEvent(self, event):
        """关闭事件 - 保存设置"""
        if self.save_callback:
            self.save_callback()
        event.accept()
    
    def refresh_groups(self):
        """刷新规则组列表"""
        self.group_list.clear()
        
        # 确保有 groups 结构
        if "groups" not in self.replacement_rules:
            # 自动迁移旧格式 - 修复：使用 clear() 和更新，保持引用
            old_rules = self.replacement_rules.get("rules", [])
            
            # 清空原字典并更新，而不是重新赋值
            self.replacement_rules.clear()
            self.replacement_rules["groups"] = {
                "默认规则组": {
                    "enabled": True,
                    "rules": old_rules
                },
                "喵语转换": {
                    "enabled": True,
                    "rules": [
                        {
                            "pattern": "([^喵])([。，！？；、）（：])",
                            "replacement": "\\1喵\\2",
                            "is_regex": True
                        },
                        {
                            "pattern": "([^喵。，！？；、）（：\\n])(\\n)",
                            "replacement": "\\1喵\\2",
                            "is_regex": True
                        },
                        {
                            "pattern": "([^。，！？；、）（：\\n])$",
                            "replacement": "\\1喵",
                            "is_regex": True
                        }
                    ]
                }
            }
            # 保存迁移后的配置
            if self.save_callback:
                self.save_callback()
        
        groups = self.replacement_rules.get("groups", {})
        for group_name, group_data in groups.items():
            item = QTreeWidgetItem(self.group_list)
            item.setText(0, group_name)
            item.setText(1, "✓" if group_data.get("enabled", True) else "✗")
            item.setData(0, Qt.ItemDataRole.UserRole, group_name)
        
        # 选择第一个组
        if self.group_list.topLevelItemCount() > 0:
            self.group_list.setCurrentItem(self.group_list.topLevelItem(0))
            self.on_group_selected(self.group_list.topLevelItem(0), 0)
    
    def on_group_selected(self, item, column):
        """选择规则组"""
        if not item:
            return
        
        group_name = item.data(0, Qt.ItemDataRole.UserRole)
        self.current_group = group_name
        self.current_group_label.setText(f"规则组：{group_name}")
        self.refresh_rules()
    
    def toggle_group(self, item, column):
        """切换规则组启用状态"""
        if not item:
            return
        
        group_name = item.data(0, Qt.ItemDataRole.UserRole)
        groups = self.replacement_rules.get("groups", {})
        
        if group_name in groups:
            current_state = groups[group_name].get("enabled", True)
            groups[group_name]["enabled"] = not current_state
            item.setText(1, "✓" if not current_state else "✗")
            self.save_callback()
    
    def refresh_rules(self):
        """刷新规则列表"""
        self.tree.clear()
        
        if not self.current_group:
            return
        
        groups = self.replacement_rules.get("groups", {})
        if self.current_group not in groups:
            return
        
        rules = groups[self.current_group].get("rules", [])
        for index, rule in enumerate(rules, 1):
            rule_type = "正则" if rule.get("is_regex", False) else "文本"
            item = QTreeWidgetItem(self.tree)
            item.setText(0, str(index))
            item.setText(1, rule.get("pattern", ""))
            item.setText(2, rule.get("replacement", ""))
            item.setText(3, rule_type)
    
    def add_group(self):
        """添加规则组"""
        from PyQt6.QtWidgets import QInputDialog
        
        group_name, ok = QInputDialog.getText(self, "新建规则组", "规则组名称：")
        if ok and group_name:
            groups = self.replacement_rules.setdefault("groups", {})
            if group_name in groups:
                QMessageBox.warning(self, "错误", "规则组已存在")
                return
            
            groups[group_name] = {
                "enabled": True,
                "rules": []
            }
            self.refresh_groups()
            self.save_callback()
    
    def rename_group(self):
        """重命名规则组"""
        from PyQt6.QtWidgets import QInputDialog
        
        current_item = self.group_list.currentItem()
        if not current_item:
            return
        
        old_name = current_item.data(0, Qt.ItemDataRole.UserRole)
        new_name, ok = QInputDialog.getText(self, "重命名规则组", "新名称：", text=old_name)
        
        if ok and new_name and new_name != old_name:
            groups = self.replacement_rules.get("groups", {})
            if new_name in groups:
                QMessageBox.warning(self, "错误", "规则组已存在")
                return
            
            groups[new_name] = groups.pop(old_name)
            if self.current_group == old_name:
                self.current_group = new_name
            
            self.refresh_groups()
            
            # 重新选中重命名后的组
            for i in range(self.group_list.topLevelItemCount()):
                item = self.group_list.topLevelItem(i)
                if item.data(0, Qt.ItemDataRole.UserRole) == new_name:
                    self.group_list.setCurrentItem(item)
                    self.on_group_selected(item, 0)
                    break
            
            self.save_callback()
    
    def delete_group(self):
        """删除规则组"""
        current_item = self.group_list.currentItem()
        if not current_item:
            return
        
        group_name = current_item.data(0, Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除规则组 '{group_name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            groups = self.replacement_rules.get("groups", {})
            if group_name in groups:
                del groups[group_name]
                
                # 先清空当前组和右侧面板
                self.current_group = None
                self.current_group_label.setText("请选择规则组")
                self.tree.clear()
                
                # 再刷新列表（会自动选择第一个组，如果有的话）
                self.refresh_groups()
                self.save_callback()
    
    def add_rule(self):
        """添加规则"""
        if not self.current_group:
            QMessageBox.warning(self, "错误", "请先选择规则组")
            return
        
        dialog = RuleDialog(self, "添加规则")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            pattern, replacement, is_regex = dialog.get_result()
            
            # 检查 pattern 是否为空
            if not pattern:
                QMessageBox.warning(self, "错误", "匹配文本不能为空")
                return
            
            # 可选：警告空替换
            if not replacement:
                reply = QMessageBox.question(
                    self,
                    "确认",
                    "替换文本为空，这将删除匹配的内容。是否继续？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            groups = self.replacement_rules.get("groups", {})
            groups[self.current_group].setdefault("rules", []).append({
                "pattern": pattern,
                "replacement": replacement,
                "is_regex": is_regex
            })
            self.refresh_rules()
            self.save_callback()
    
    def edit_rule(self):
        """编辑规则"""
        if not self.current_group:
            return
        
        current_item = self.tree.currentItem()
        if not current_item:
            return
        
        index = self.tree.indexOfTopLevelItem(current_item)
        groups = self.replacement_rules.get("groups", {})
        rule = groups[self.current_group]["rules"][index]
        
        dialog = RuleDialog(
            self, 
            "编辑规则",
            rule.get("pattern", ""),
            rule.get("replacement", ""),
            rule.get("is_regex", False)
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            pattern, replacement, is_regex = dialog.get_result()
            
            # 检查 pattern 是否为空
            if not pattern:
                QMessageBox.warning(self, "错误", "匹配文本不能为空")
                return
            
            # 可选：警告空替换
            if not replacement:
                reply = QMessageBox.question(
                    self,
                    "确认",
                    "替换文本为空，这将删除匹配的内容。是否继续？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            groups[self.current_group]["rules"][index] = {
                "pattern": pattern,
                "replacement": replacement,
                "is_regex": is_regex
            }
            self.refresh_rules()
            self.save_callback()
    
    def delete_rule(self):
        """删除规则"""
        if not self.current_group:
            return
        
        current_item = self.tree.currentItem()
        if not current_item:
            return
        
        # 添加确认对话框
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这条规则吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            index = self.tree.indexOfTopLevelItem(current_item)
            groups = self.replacement_rules.get("groups", {})
            del groups[self.current_group]["rules"][index]
            self.refresh_rules()
            self.save_callback()
    
    def move_up(self):
        """上移规则"""
        if not self.current_group:
            return
        
        current_item = self.tree.currentItem()
        if not current_item:
            return
        
        index = self.tree.indexOfTopLevelItem(current_item)
        if index > 0:
            groups = self.replacement_rules.get("groups", {})
            rules = groups[self.current_group]["rules"]
            rules[index], rules[index-1] = rules[index-1], rules[index]
            self.refresh_rules()
            self.save_callback()
            self.tree.setCurrentItem(self.tree.topLevelItem(index-1))
    
    def move_down(self):
        """下移规则"""
        if not self.current_group:
            return
        
        current_item = self.tree.currentItem()
        if not current_item:
            return
        
        index = self.tree.indexOfTopLevelItem(current_item)
        groups = self.replacement_rules.get("groups", {})
        rules = groups[self.current_group]["rules"]
        if index < len(rules) - 1:
            rules[index], rules[index+1] = rules[index+1], rules[index]
            self.refresh_rules()
            self.save_callback()
            self.tree.setCurrentItem(self.tree.topLevelItem(index+1))
    
    def import_group(self):
        """导入规则组"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "导入规则组",
            "",
            "JSON 文件 (*.json);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            # 检查是否是单个规则组
            if "enabled" in imported_data and "rules" in imported_data:
                # 单个规则组格式
                group_name = os.path.splitext(os.path.basename(file_path))[0]
                
                # 检查是否已存在
                groups = self.replacement_rules.get("groups", {})
                if group_name in groups:
                    from PyQt6.QtWidgets import QInputDialog
                    # 修复：使用新变量名避免重用
                    new_group_name, ok = QInputDialog.getText(
                        self,
                        "规则组已存在",
                        f"规则组 '{group_name}' 已存在，请输入新名称：",
                        text=f"{group_name}_导入"
                    )
                    if not ok or not new_group_name:
                        return
                    group_name = new_group_name
                
                groups[group_name] = imported_data
                QMessageBox.information(self, "成功", f"已导入规则组：{group_name}")
            
            elif "groups" in imported_data:
                # 多个规则组格式
                groups = self.replacement_rules.get("groups", {})
                imported_count = 0
                
                for group_name, group_data in imported_data["groups"].items():
                    original_name = group_name
                    if group_name in groups:
                        # 重命名冲突的规则组
                        counter = 1
                        while group_name in groups:
                            group_name = f"{original_name}_{counter}"
                            counter += 1
                    
                    groups[group_name] = group_data
                    imported_count += 1
                
                QMessageBox.information(self, "成功", f"已导入 {imported_count} 个规则组")
            
            else:
                QMessageBox.warning(self, "错误", "无效的规则组文件格式")
                return
            
            self.refresh_groups()
            self.save_callback()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入失败：{str(e)}")
    
    def export_group(self):
        """导出规则组"""
        from PyQt6.QtWidgets import QFileDialog
        
        current_item = self.group_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "提示", "请先选择要导出的规则组")
            return
        
        group_name = current_item.data(0, Qt.ItemDataRole.UserRole)
        groups = self.replacement_rules.get("groups", {})
        
        if group_name not in groups:
            return
        
        # 默认文件名
        default_filename = f"{group_name}.json"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出规则组",
            default_filename,
            "JSON 文件 (*.json);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            # 导出单个规则组
            export_data = groups[group_name]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "成功", f"规则组已导出到：\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败：{str(e)}")


class RuleDialog(QDialog):
    """规则编辑对话框"""
    
    def __init__(self, parent, title, pattern="", replacement="", is_regex=False):
        super().__init__(parent)
        self.result = None
        self.init_ui(title, pattern, replacement, is_regex)
        
    def init_ui(self, title, pattern, replacement, is_regex):
        """初始化UI"""
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # 匹配文本
        pattern_label = QLabel("匹配文本：")
        layout.addWidget(pattern_label)
        
        self.pattern_input = QLineEdit()
        self.pattern_input.setText(pattern)
        layout.addWidget(self.pattern_input)
        
        # 替换为
        replacement_label = QLabel("替换为：")
        layout.addWidget(replacement_label)
        
        self.replacement_input = QLineEdit()
        self.replacement_input.setText(replacement)
        layout.addWidget(self.replacement_input)
        
        # 正则表达式选项
        self.regex_checkbox = QCheckBox("使用正则表达式")
        self.regex_checkbox.setChecked(is_regex)
        layout.addWidget(self.regex_checkbox)
        
        # 提示
        hint_label = QLabel("提示：正则表达式示例 - \\d+ 匹配数字，[a-z]+ 匹配小写字母")
        hint_label.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(hint_label)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 设置焦点
        self.pattern_input.setFocus()
    
    def accept(self):
        """重写 accept 方法，添加验证"""
        pattern = self.pattern_input.text()
        is_regex = self.regex_checkbox.isChecked()
        
        if not pattern:
            QMessageBox.warning(self, "错误", "匹配文本不能为空")
            return
        
        # 验证正则表达式
        if is_regex:
            try:
                re.compile(pattern)
            except re.error as e:
                QMessageBox.warning(
                    self,
                    "正则表达式错误",
                    f"无效的正则表达式：\n{str(e)}"
                )
                return
        
        super().accept()
    
    def get_result(self):
        """获取结果"""
        return (
            self.pattern_input.text(),
            self.replacement_input.text(),
            self.regex_checkbox.isChecked()
        )


class DebugWindow(QWidget):
    """调试窗口"""
    
    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("MeowParser 调试窗口")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        
        # 日志区域
        log_label = QLabel("日志输出：")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        clear_btn = QPushButton("清空日志")
        clear_btn.clicked.connect(self.clear_log)
        button_layout.addWidget(clear_btn)
        
        copy_btn = QPushButton("复制日志")
        copy_btn.clicked.connect(self.copy_log)
        button_layout.addWidget(copy_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 测试输入区域
        test_label = QLabel("测试输入：")
        layout.addWidget(test_label)
        
        self.test_entry = QLineEdit()
        layout.addWidget(self.test_entry)
        
        hint_label = QLabel("提示：开始输入时会自动弹出悬浮窗")
        hint_label.setStyleSheet("color: gray;")
        layout.addWidget(hint_label)
        
        self.setLayout(layout)
        
    def log(self, message):
        """添加日志"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
        
    def copy_log(self):
        """复制日志"""
        try:
            import pyperclip
            pyperclip.copy(self.log_text.toPlainText())
            self.log("日志已复制到剪贴板")
        except:
            self.log("复制失败：未安装 pyperclip")


class MeowParser(QObject):
    """主应用类"""
    
    log_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # 检查单实例
        self.instance_lock = check_single_instance()
        if not self.instance_lock:
            QMessageBox.warning(None, "MeowParser", "程序已在运行中")
            sys.exit(0)
        
        self.enabled = False
        self.is_admin = self.check_admin()
        self.allowed_windows = self.load_window_settings()
        
        # 使用新的配置管理器
        self.config_manager = ConfigFileManager(".kiro/rules")
        self.text_processor = TextProcessor(self.config_manager)
        
        # 加载默认配置
        configs = self.config_manager.list_configs()
        if configs:
            self.config_manager.load_config(configs[0]['path'])
        
        # 迁移旧配置（如果存在）
        self._migrate_old_config_if_needed()
        
        # 输入监听相关
        self.input_buffer = ""
        self.last_input_time = 0
        self.last_window = None
        self.click_position = None
        self.input_activated = False
        
        # 创建UI组件（悬浮窗无父窗口，独立显示）
        self.floating_window = FloatingInputWindow(self)
        # 强制显示一次然后隐藏，确保窗口正确初始化
        self.floating_window.hide()
        self.debug_window = None
        self.window_manager = None
        self.config_editor = None  # 使用新的编辑器
        
        # 创建系统托盘
        self.setup_tray()
        
        # 连接日志信号
        self.log_signal.connect(self._log_to_debug)
        
    def check_admin(self):
        """检查管理员权限"""
        if IS_WINDOWS:
            try:
                return ctypes.windll.shell32.IsUserAnAdmin()
            except:
                return False
        else:
            return os.geteuid() == 0
    
    def create_icon(self, color):
        """创建托盘图标"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(color))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor('white'))
        font = QFont('SimHei', 20)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "喵")
        painter.end()
        
        return QIcon(pixmap)
    
    def setup_tray(self):
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon(self.create_icon('red'))
        self.tray_icon.setToolTip("MeowParser (禁用)")
        
        # 创建菜单
        menu = QMenu()
        
        self.toggle_action = QAction("启用/禁用", menu)
        self.toggle_action.triggered.connect(self.toggle)
        menu.addAction(self.toggle_action)
        
        menu.addSeparator()
        
        window_action = QAction("窗口管理", menu)
        window_action.triggered.connect(self.show_window_manager)
        menu.addAction(window_action)
        
        rules_action = QAction("替换规则", menu)
        rules_action.triggered.connect(self.show_replacement_editor)
        menu.addAction(rules_action)
        
        debug_action = QAction("调试窗口", menu)
        debug_action.triggered.connect(self.show_debug_window)
        menu.addAction(debug_action)
        
        menu.addSeparator()
        
        status_text = f"权限状态: {'✓ 管理员' if self.is_admin else '✗ 普通用户'}"
        status_action = QAction(status_text, menu)
        status_action.setEnabled(False)
        menu.addAction(status_action)
        
        # 快捷键提示
        hotkey_text = "快捷键: Ctrl+Shift+Alt+M 切换当前窗口"
        hotkey_action = QAction(hotkey_text, menu)
        hotkey_action.setEnabled(False)
        menu.addAction(hotkey_action)
        
        menu.addSeparator()
        
        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
    
    def toggle(self):
        """切换启用/禁用状态"""
        if not self.is_admin:
            self.tray_icon.showMessage(
                "权限不足",
                "需要管理员权限才能使用此功能",
                QSystemTrayIcon.MessageIcon.Warning
            )
            return
        
        self.enabled = not self.enabled
        color = 'green' if self.enabled else 'red'
        self.tray_icon.setIcon(self.create_icon(color))
        self.tray_icon.setToolTip(f"MeowParser ({'启用' if self.enabled else '禁用'})")
        
        if self.enabled:
            self.start_input_listener()
        else:
            self.stop_input_listener()
    
    def start_input_listener(self):
        """启动输入监听"""
        try:
            self.input_buffer = ""
            self.last_input_time = 0
            self.last_window = None
            self.input_activated = False
            
            keyboard.hook(self.on_key_event)
            # 添加快捷键：Ctrl+Shift+Alt+M 切换当前窗口启用状态
            keyboard.add_hotkey('ctrl+shift+alt+m', self.toggle_current_window)
            
            self.debug_log("输入监听已启动")
        except Exception as e:
            self.tray_icon.showMessage("错误", f"启动失败: {str(e)}", QSystemTrayIcon.MessageIcon.Critical)
    
    def stop_input_listener(self):
        """停止输入监听"""
        try:
            keyboard.unhook_all()
            self.floating_window.hide()
            
            self.input_buffer = ""
            self.last_input_time = 0
            self.last_window = None
            self.input_activated = False
        except:
            pass
    
    def on_key_event(self, event):
        """键盘事件处理"""
        if not self.enabled:
            return
        
        if event.event_type != 'down':
            return
        
        # 检查当前窗口是否在白名单中
        window = self.get_active_window_info()
        if not window:
            self.input_buffer = ""
            self.input_activated = False
            if self.floating_window.isVisible():
                self.floating_window.hide()
            return
        
        # 检查窗口是否在白名单中（修复：正确检查字典键）
        window_key = window['title']
        if window_key not in self.allowed_windows or not self.allowed_windows[window_key]:
            self.input_buffer = ""
            self.input_activated = False
            if self.floating_window.isVisible():
                self.floating_window.hide()
            return
        
        # 检测窗口切换（修复：添加 None 检查并立即返回）
        if self.last_window != window_key:
            self.input_buffer = ""
            self.last_window = window_key
            self.input_activated = False
            if self.floating_window.isVisible():
                self.floating_window.hide()
            return
        
        key_name = event.name
        current_time = time.time()
        
        # 检查悬浮窗是否已显示
        floating_visible = self.floating_window.isVisible()
        
        # 处理回车键
        if key_name == 'enter':
            if floating_visible:
                return
            self.input_buffer = ""
            self.input_activated = False
            return
        
        # 如果悬浮窗已显示，不再处理输入
        if floating_visible:
            return
        
        # 处理退格键
        if key_name == 'backspace':
            if len(self.input_buffer) > 0:
                self.input_buffer = self.input_buffer[:-1]
                self.last_input_time = current_time
            return
        
        # 处理空格 - 在输入激活状态下触发悬浮窗（修复：添加防重复检查）
        if key_name == 'space':
            if self.input_activated and not floating_visible:
                self.input_buffer = ""
                
                # 获取当前鼠标位置
                try:
                    if IS_WINDOWS:
                        self.click_position = win32api.GetCursorPos()
                    else:
                        # Linux: 使用 PyQt6 获取鼠标位置
                        from PyQt6.QtGui import QCursor
                        pos = QCursor.pos()
                        self.click_position = (pos.x(), pos.y())
                except:
                    self.click_position = (100, 100)
                
                # 显示悬浮窗
                x, y = self.click_position
                self.debug_log(f"显示悬浮窗: 位置({x}, {y})")
                self.floating_window.show_at(x, y, window.get('hwnd'))
                
                # 阻止空格键事件传递（修复：只在成功显示后阻止）
                try:
                    keyboard.block_key('space')
                    def unblock_space():
                        try:
                            keyboard.unblock_key('space')
                        except:
                            pass
                    threading.Timer(0.2, unblock_space).start()
                except:
                    pass
            else:
                self.input_buffer += ' '
                self.last_input_time = current_time
                self.input_activated = True
            return
        
        # 处理Tab
        if key_name == 'tab':
            self.input_buffer += '\t'
            self.last_input_time = current_time
            return
        
        # 处理单字符按键
        if len(key_name) == 1:
            self.input_buffer += key_name
            self.last_input_time = current_time
            self.input_activated = True
            return
        
        # 处理光标移动键
        if key_name in ['left', 'right', 'up', 'down', 'home', 'end', 'page up', 'page down']:
            self.input_buffer = ""
            self.input_activated = False
            if self.floating_window.isVisible():
                self.floating_window.hide()
            return
        
        # 处理ESC键
        if key_name in ['esc', 'escape']:
            self.input_buffer = ""
            self.input_activated = False
            if self.floating_window.isVisible():
                self.floating_window.hide()
            return
    
    def get_active_window_info(self):
        """获取当前活动窗口信息"""
        try:
            if IS_WINDOWS:
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
            else:
                # Linux: 使用 xdotool 获取活动窗口信息
                try:
                    import subprocess
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
                    self.debug_log("错误: 未安装 xdotool，Linux 平台需要安装: sudo apt-get install xdotool")
                    return None
                except subprocess.TimeoutExpired:
                    return None
                except Exception as e:
                    self.debug_log(f"Linux 窗口信息获取错误: {e}")
                    return None
        except Exception as e:
            self.debug_log(f"获取窗口信息错误: {e}")
            return None
    
    def process_text(self, text):
        """处理文本 - 使用新的文本处理器"""
        return self.text_processor.process(text)
    
    def debug_log(self, message):
        """记录调试日志"""
        print(message)
        self.log_signal.emit(message)
    
    def _log_to_debug(self, message):
        """将日志输出到调试窗口"""
        if self.debug_window:
            self.debug_window.log(message)
    
    def show_debug_window(self):
        """显示调试窗口"""
        if self.debug_window is None:
            self.debug_window = DebugWindow(self)
            # 自动将调试窗口添加到白名单
            self._add_debug_window_to_whitelist()
        self.debug_window.show()
        self.debug_window.raise_()
        self.debug_window.activateWindow()
    
    def toggle_current_window(self):
        """切换当前窗口的启用状态（快捷键：Ctrl+Shift+Alt+M）"""
        try:
            # 获取当前活动窗口
            window = self.get_active_window_info()
            if not window:
                self.tray_icon.showMessage(
                    "无法切换",
                    "无法获取当前窗口信息",
                    QSystemTrayIcon.MessageIcon.Warning,
                    2000
                )
                return
            
            window_key = window['title']
            
            # 检查是否是调试窗口（不允许切换）
            if "MeowParser 调试窗口" in window_key or "MeowParser调试窗口" in window_key:
                self.tray_icon.showMessage(
                    "无法切换",
                    "调试窗口已锁定为启用状态",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
                return
            
            # 切换状态
            if window_key in self.allowed_windows and self.allowed_windows[window_key]:
                # 当前已启用，切换为禁用
                del self.allowed_windows[window_key]
                status = "已禁用"
                icon = QSystemTrayIcon.MessageIcon.Information
            else:
                # 当前未启用，切换为启用
                self.allowed_windows[window_key] = True
                status = "已启用"
                icon = QSystemTrayIcon.MessageIcon.Information
            
            # 保存设置
            self.save_window_settings()
            
            # 显示通知
            # 提取窗口标题（去掉进程名）
            parts = window_key.split(" - ", 1)
            display_title = parts[1] if len(parts) > 1 else window_key
            if len(display_title) > 50:
                display_title = display_title[:47] + "..."
            
            self.tray_icon.showMessage(
                f"窗口{status}",
                f"{display_title}",
                icon,
                2000
            )
            
            self.debug_log(f"快捷键切换窗口状态: {window_key} -> {status}")
            
            # 如果窗口管理器打开，刷新列表
            if hasattr(self, 'window_manager') and self.window_manager and self.window_manager.isVisible():
                self.window_manager.refresh_windows()
                
        except Exception as e:
            self.debug_log(f"切换窗口状态错误: {e}")
            self.tray_icon.showMessage(
                "切换失败",
                f"错误: {str(e)}",
                QSystemTrayIcon.MessageIcon.Critical,
                2000
            )
    
    def _add_debug_window_to_whitelist(self):
        """自动将调试窗口添加到白名单"""
        try:
            # 等待窗口创建
            QTimer.singleShot(500, self._do_add_debug_window)
        except Exception as e:
            self.debug_log(f"添加调试窗口到白名单错误: {e}")
    
    def _do_add_debug_window(self):
        """执行添加调试窗口到白名单"""
        try:
            if IS_WINDOWS:
                # 查找调试窗口
                def find_debug_window(hwnd, _):
                    try:
                        title = win32gui.GetWindowText(hwnd)
                        if "MeowParser 调试窗口" in title or "MeowParser调试窗口" in title:
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            process_name = psutil.Process(pid).name()
                            window_key = f"{process_name} - {title}"
                            self.allowed_windows[window_key] = True
                            self.save_window_settings()
                            self.debug_log(f"已自动添加调试窗口到白名单: {window_key}")
                    except:
                        pass
                    return True
                
                win32gui.EnumWindows(find_debug_window, None)
            else:
                # Linux: 使用 xdotool 查找
                import subprocess
                result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if "MeowParser 调试窗口" in line or "MeowParser调试窗口" in line:
                            parts = line.split(None, 3)
                            if len(parts) >= 4:
                                title = parts[3]
                                window_key = f"Python - {title}"
                                self.allowed_windows[window_key] = True
                                self.save_window_settings()
                                self.debug_log(f"已自动添加调试窗口到白名单: {window_key}")
                                break
        except Exception as e:
            self.debug_log(f"自动添加调试窗口错误: {e}")
    
    def show_window_manager(self):
        """显示窗口管理器"""
        try:
            # 如果窗口管理器已存在，直接显示
            if hasattr(self, 'window_manager') and self.window_manager:
                self.window_manager.show()
                self.window_manager.raise_()
                self.window_manager.activateWindow()
                self.window_manager.refresh_windows()
            else:
                # 创建新的窗口管理器（非模态）
                self.window_manager = WindowSelector(None, self.allowed_windows, self.save_window_settings)
                self.window_manager.show()
        except Exception as e:
            self.debug_log(f"窗口管理器错误: {e}")
    
    def show_replacement_editor(self):
        """显示配置文件编辑器"""
        try:
            # 如果编辑器已存在，直接显示
            if hasattr(self, 'config_editor') and self.config_editor:
                self.config_editor.show()
                self.config_editor.raise_()
                self.config_editor.activateWindow()
                self.config_editor.refresh_config_list()
            else:
                # 创建新的编辑器（非模态）
                self.config_editor = ConfigFileEditor(None, self.config_manager, self.on_config_changed)
                self.config_editor.show()
        except Exception as e:
            self.debug_log(f"配置编辑器错误: {e}")
    
    def load_window_settings(self):
        """加载窗口设置"""
        try:
            if os.path.exists('window_settings.json'):
                with open('window_settings.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_window_settings(self):
        """保存窗口设置"""
        try:
            with open('window_settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.allowed_windows, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def _migrate_old_config_if_needed(self):
        """迁移旧配置（如果需要）"""
        old_config_path = Path("replacement_rules.json")
        
        if not old_config_path.exists():
            return
        
        try:
            # 读取旧配置
            with open(old_config_path, 'r', encoding='utf-8') as f:
                old_config = json.load(f)
            
            # 迁移配置
            new_config = self.config_manager.migrate_old_config(old_config)
            
            # 保存为新配置文件
            migrated_path = self.config_manager.config_dir / "migrated_from_old.json"
            self.config_manager.current_config = new_config
            self.config_manager.current_config_path = migrated_path
            self.config_manager.save_config()
            
            self.debug_log(f"✅ 配置已迁移到: {migrated_path}")
            
            # 备份旧配置
            backup_path = old_config_path.with_suffix('.json.old')
            import shutil
            shutil.copy(old_config_path, backup_path)
            self.debug_log(f"✅ 旧配置已备份到: {backup_path}")
            
            # 加载迁移后的配置
            self.config_manager.load_config(migrated_path)
            
        except Exception as e:
            self.debug_log(f"❌ 配置迁移失败: {e}")
    
    def on_config_changed(self):
        """配置更改回调"""
        if self.config_manager.current_config:
            config_name = self.config_manager.current_config.get('name', '')
            self.debug_log(f"配置已更新: {config_name}")
    
    def load_replacement_rules(self):
        """加载替换规则"""
        try:
            if os.path.exists('replacement_rules.json'):
                with open('replacement_rules.json', 'r', encoding='utf-8') as f:
                    rules = json.load(f)
                    
                    # 自动迁移旧格式到新格式
                    if "groups" not in rules:
                        # 旧格式：{"enabled": true, "rules": [...]}
                        old_rules = rules.get("rules", [])
                        rules = {
                            "groups": {
                                "默认规则组": {
                                    "enabled": True,
                                    "rules": old_rules
                                },
                                "喵语转换": {
                                    "enabled": True,
                                    "rules": [
                                        {
                                            "pattern": "([^喵])([。，！？；、）（：])",
                                            "replacement": "\\1喵\\2",
                                            "is_regex": True
                                        },
                                        {
                                            "pattern": "([^喵。，！？；、）（：\\n])(\\n)",
                                            "replacement": "\\1喵\\2",
                                            "is_regex": True
                                        },
                                        {
                                            "pattern": "([^。，！？；、）（：\\n])$",
                                            "replacement": "\\1喵",
                                            "is_regex": True
                                        }
                                    ]
                                }
                            }
                        }
                        # 保存迁移后的配置
                        self.replacement_rules = rules
                        self.save_replacement_rules()
                    
                    return rules
        except Exception as e:
            print(f"加载替换规则错误: {e}")
        
        # 返回默认配置（新格式）
        return {
            "groups": {
                "喵语转换": {
                    "enabled": True,
                    "rules": [
                        {
                            "pattern": "([^喵])([。，！？；、）（：])",
                            "replacement": "\\1喵\\2",
                            "is_regex": True
                        },
                        {
                            "pattern": "([^喵。，！？；、）（：\\n])(\\n)",
                            "replacement": "\\1喵\\2",
                            "is_regex": True
                        },
                        {
                            "pattern": "([^。，！？；、）（：\\n])$",
                            "replacement": "\\1喵",
                            "is_regex": True
                        }
                    ]
                }
            }
        }
    
    def save_replacement_rules(self):
        """保存替换规则"""
        try:
            with open('replacement_rules.json', 'w', encoding='utf-8') as f:
                json.dump(self.replacement_rules, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def quit_app(self):
        """退出应用"""
        try:
            self.stop_input_listener()
            
            # 关闭所有窗口
            if self.debug_window:
                self.debug_window.close()
            
            if self.window_manager:
                self.window_manager.close()
            
            if self.replacement_editor:
                self.replacement_editor.close()
            
            self.floating_window.close()
            self.save_window_settings()
            
            # 清理单实例锁
            if IS_WINDOWS and self.instance_lock:
                ctypes.windll.kernel32.CloseHandle(self.instance_lock)
            elif IS_LINUX and self.instance_lock:
                try:
                    self.instance_lock.unlink()
                except:
                    pass
            
            QApplication.quit()
        except Exception as e:
            print(f"退出错误: {e}")
            QApplication.quit()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # 设置应用信息
    app.setApplicationName("MeowParser")
    app.setOrganizationName("MeowParser")
    
    # 应用 PyQtDarkTheme 主题（跟随系统）
    qdarktheme.setup_theme("auto")
    
    # 创建主应用
    meow_app = MeowParser()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
