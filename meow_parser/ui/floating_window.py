#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
悬浮输入窗口模块
"""

import time
import threading
from PyQt6.QtWidgets import QWidget, QLineEdit, QApplication
from PyQt6.QtCore import Qt, pyqtSignal
import keyboard
from ..constants import IS_WINDOWS

if IS_WINDOWS:
    import win32gui
    import win32api
    import win32con


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
        self.direct_input_mode = False  # 直接输入模式
        
        # 连接信号到槽
        self.show_signal.connect(self._do_show_at)
        
        self.init_ui()
        
    def init_ui(self):
        """初始化UI - 极简设计"""
        # 设置窗口标志
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # 设置对象名称
        self.setObjectName("FloatingInputWindow")
        
        # 确保窗口不透明
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        
        # 设置固定大小（紧凑设计）
        self.setFixedSize(500, 60)
        
        # 创建输入框（居中放置，留出边距）
        self.entry = QLineEdit(self)
        self.entry.setGeometry(5, 5, 490, 50)
        self.entry.setPlaceholderText("输入内容 (回车发送 | Ctrl+回车原始 | ESC取消)")
        self.entry.returnPressed.connect(self.on_enter)
        
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
    
    def show_at(self, x, y, target_window=None, direct_input=False):
        """在指定位置显示悬浮窗（线程安全）"""
        # 使用信号发送到主线程
        print(f"show_at 被调用: ({x}, {y}), 直接输入模式: {direct_input}")
        self.direct_input_mode = direct_input
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
        window_height = 60
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
            self.parent_app.debug_log(f"直接输入模式: {self.direct_input_mode}")
            
            # 等待悬浮窗完全隐藏
            time.sleep(0.15)
            
            # 恢复焦点（改进：添加验证和重试机制）
            focus_restored = False
            
            if self.direct_input_mode:
                # 直接输入模式：跳过点击，直接输入
                self.parent_app.debug_log("使用直接输入模式，跳过点击流程")
                
                if self.target_window:
                    if IS_WINDOWS:
                        try:
                            # 只恢复窗口焦点，不点击
                            for attempt in range(3):
                                win32gui.SetForegroundWindow(self.target_window)
                                time.sleep(0.05)
                                
                                current_hwnd = win32gui.GetForegroundWindow()
                                if current_hwnd == self.target_window:
                                    focus_restored = True
                                    break
                                time.sleep(0.05)
                        except Exception as e:
                            self.parent_app.debug_log(f"焦点恢复错误: {e}")
                    else:
                        # Linux
                        try:
                            import subprocess
                            subprocess.run(['xdotool', 'windowactivate', str(self.target_window)],
                                         timeout=1, check=False)
                            time.sleep(0.1)
                            focus_restored = True
                        except Exception as e:
                            self.parent_app.debug_log(f"Linux 焦点恢复错误: {e}")
                
                # 直接输入模式下，稍微延长等待时间
                time.sleep(0.1)
                
            else:
                # 标准模式：点击后输入
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
