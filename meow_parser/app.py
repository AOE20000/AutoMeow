#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MeowParser 主应用模块
"""

import os
import sys
import json
import time
import ctypes
import threading
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QCursor

import keyboard
import psutil

from .constants import IS_WINDOWS, IS_LINUX, IS_MACOS
from .core import ConfigFileManager, TextProcessor, check_single_instance
from .ui import (
    FloatingInputWindow,
    DebugWindow,
    WindowSelector,
    ConfigFileEditor,
    TrayIconManager
)
from .platform import get_active_window_info

if IS_WINDOWS:
    import win32gui
    import win32process
    import win32api


class MeowParser(QObject):
    """MeowParser 主应用类"""
    
    log_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # 检查单实例
        self.instance_lock = check_single_instance()
        if not self.instance_lock:
            QMessageBox.warning(None, "MeowParser", "程序已在运行中")
            sys.exit(0)
        
        # 基本状态
        self.enabled = False
        
        # 样式管理器（优先初始化，用于托盘菜单）
        from .ui.styles import StyleManager
        self.style_manager = StyleManager()
        
        # 创建系统托盘（最优先，确保立即可见和响应）
        self.tray_manager = TrayIconManager(self)
        self.tray_manager.show()
        
        # 延迟初始化的组件
        self.floating_window = None
        self.debug_window = None
        self.window_manager = None
        self.config_editor = None
        
        # 配置管理（延迟加载）
        self.config_manager = None
        self.text_processor = None
        self.allowed_windows = {}
        
        # 输入监听相关
        self.input_buffer = ""
        self.last_input_time = 0
        self.last_window = None
        self.click_position = None
        self.input_activated = False
        
        # 连接日志信号
        self.log_signal.connect(self._log_to_debug)
        
        # 使用 QTimer 延迟初始化其他组件
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self._delayed_init)
    
    def _delayed_init(self):
        """延迟初始化非关键组件"""
        print("开始延迟初始化...")
        
        # 加载窗口设置
        self.allowed_windows = self.load_window_settings()
        
        # 配置管理
        self.config_manager = ConfigFileManager(".meowparser/rules")
        self.text_processor = TextProcessor(self.config_manager)
        
        # 加载默认配置
        configs = self.config_manager.list_configs()
        if configs:
            self.config_manager.load_config(configs[0]['path'])
        
        # 迁移旧配置（如果存在）
        self._migrate_old_config_if_needed()
        
        # 创建悬浮窗（延迟创建）
        self.floating_window = FloatingInputWindow(self)
        self.floating_window.hide()
        
        print("延迟初始化完成")
    
    def check_admin(self):
        """检查管理员权限（已废弃，保留用于兼容性）"""
        from .core.privilege import is_admin
        return is_admin()
    
    def toggle(self):
        """切换启用/禁用状态"""
        # 确保延迟初始化完成
        if self.floating_window is None:
            print("等待初始化完成...")
            self.tray_manager.show_message(
                "提示",
                "正在初始化，请稍候...",
                QSystemTrayIcon.MessageIcon.Information
            )
            return
        
        self.enabled = not self.enabled
        self.tray_manager.update_icon(self.enabled)
        
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
            keyboard.add_hotkey('ctrl+shift+alt+m', self.toggle_current_window)
            
            self.debug_log("输入监听已启动")
        except Exception as e:
            self.tray_manager.show_message(
                "错误", 
                f"启动失败: {str(e)}", 
                QSystemTrayIcon.MessageIcon.Critical
            )
    
    def stop_input_listener(self):
        """停止输入监听"""
        try:
            # 先移除所有热键
            try:
                keyboard.remove_all_hotkeys()
                print("已移除所有热键")
            except Exception as e:
                print(f"移除热键错误: {e}")
            
            # 等待一小段时间确保事件处理完成
            time.sleep(0.1)
            
            # 清理所有钩子
            keyboard.unhook_all()
            print("已清理键盘钩子")
            
            # 隐藏悬浮窗
            if self.floating_window:
                self.floating_window.hide()
            
            # 重置状态
            self.input_buffer = ""
            self.last_input_time = 0
            self.last_window = None
            self.input_activated = False
            
        except Exception as e:
            print(f"停止监听错误: {e}")
    
    def on_key_event(self, event):
        """键盘事件处理"""
        if not self.enabled:
            return
        
        if event.event_type != 'down':
            return
        
        # 检查当前窗口是否在白名单中
        window = get_active_window_info()
        if not window:
            self.input_buffer = ""
            self.input_activated = False
            if self.floating_window.isVisible():
                self.floating_window.hide()
            return
        
        # 检查窗口是否在白名单中
        window_key = window['title']
        window_config = self.allowed_windows.get(window_key)
        
        # 兼容旧格式和新格式
        if not window_config:
            self.input_buffer = ""
            self.input_activated = False
            if self.floating_window.isVisible():
                self.floating_window.hide()
            return
        
        # 转换为字典格式
        if not isinstance(window_config, dict):
            window_config = {"enabled": window_config}
            self.allowed_windows[window_key] = window_config
        
        # 检查是否启用
        if not window_config.get("enabled", False):
            self.input_buffer = ""
            self.input_activated = False
            if self.floating_window.isVisible():
                self.floating_window.hide()
            return
        
        # 获取窗口配置
        trigger_key = window_config.get("trigger_key", "").lower()
        direct_input = window_config.get("direct_input", False)
        
        # 保存直接输入模式到窗口对象
        window['direct_input'] = direct_input
        
        # 检测窗口切换
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
        
        # 处理空格 - 在输入激活状态下触发悬浮窗
        if key_name == 'space':
            # 检查是否满足触发条件
            should_trigger = False
            
            if trigger_key:
                # 自定义触发器：检查缓冲区是否以触发键结尾
                if self.input_buffer.lower().endswith(trigger_key):
                    should_trigger = True
                    # 移除触发键
                    self.input_buffer = self.input_buffer[:-len(trigger_key)]
            else:
                # 默认触发器：任何输入后按空格
                if self.input_activated:
                    should_trigger = True
            
            if should_trigger and not floating_visible:
                # 获取当前鼠标位置
                try:
                    if IS_WINDOWS:
                        self.click_position = win32api.GetCursorPos()
                    else:
                        pos = QCursor.pos()
                        self.click_position = (pos.x(), pos.y())
                except:
                    self.click_position = (100, 100)
                
                # 显示悬浮窗
                x, y = self.click_position
                self.debug_log(f"显示悬浮窗: 位置({x}, {y}), 触发器: {trigger_key or '空格'}")
                self.floating_window.show_at(x, y, window.get('hwnd'), direct_input)
                
                # 阻止空格键事件传递
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
    
    def process_text(self, text):
        """处理文本"""
        if self.text_processor is None:
            return text
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
            self._add_debug_window_to_whitelist()
        self.debug_window.show()
        self.debug_window.raise_()
        self.debug_window.activateWindow()
    
    def toggle_current_window(self):
        """切换当前窗口的启用状态"""
        try:
            window = get_active_window_info()
            if not window:
                self.tray_manager.show_message(
                    "无法切换",
                    "无法获取当前窗口信息",
                    QSystemTrayIcon.MessageIcon.Critical
                )
                return
            
            window_key = window['title']
            
            # 检查是否是调试窗口
            if "MeowParser 调试窗口" in window_key or "MeowParser调试窗口" in window_key:
                self.tray_manager.show_message(
                    "无法切换",
                    "调试窗口已锁定为启用状态",
                    QSystemTrayIcon.MessageIcon.Information
                )
                return
            
            # 切换状态
            window_config = self.allowed_windows.get(window_key)
            
            # 兼容旧格式
            if window_config and not isinstance(window_config, dict):
                window_config = {"enabled": window_config}
                self.allowed_windows[window_key] = window_config
            
            if window_config and window_config.get("enabled", False):
                # 禁用窗口
                window_config["enabled"] = False
                status = "已禁用"
            else:
                # 启用窗口
                if not window_config:
                    self.allowed_windows[window_key] = {"enabled": True}
                else:
                    window_config["enabled"] = True
                status = "已启用"
            
            self.save_window_settings()
            
            # 显示通知
            parts = window_key.split(" - ", 1)
            display_title = parts[1] if len(parts) > 1 else window_key
            if len(display_title) > 50:
                display_title = display_title[:47] + "..."
            
            self.tray_manager.show_message(
                f"窗口{status}",
                f"{display_title}",
                QSystemTrayIcon.MessageIcon.Information
            )
            
            self.debug_log(f"快捷键切换窗口状态: {window_key} -> {status}")
            
            # 刷新窗口管理器
            if hasattr(self, 'window_manager') and self.window_manager and self.window_manager.isVisible():
                self.window_manager.refresh_windows()
                
        except Exception as e:
            self.debug_log(f"切换窗口状态错误: {e}")
            self.tray_manager.show_message(
                "切换失败",
                f"错误: {str(e)}",
                QSystemTrayIcon.MessageIcon.Critical
            )
    
    def _add_debug_window_to_whitelist(self):
        """自动将调试窗口添加到白名单"""
        try:
            QTimer.singleShot(500, self._do_add_debug_window)
        except Exception as e:
            self.debug_log(f"添加调试窗口到白名单错误: {e}")
    
    def _do_add_debug_window(self):
        """执行添加调试窗口到白名单"""
        try:
            if IS_WINDOWS:
                def find_debug_window(hwnd, _):
                    try:
                        title = win32gui.GetWindowText(hwnd)
                        if "MeowParser 调试窗口" in title or "MeowParser调试窗口" in title:
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            process_name = psutil.Process(pid).name()
                            window_key = f"{process_name} - {title}"
                            self.allowed_windows[window_key] = {"enabled": True}
                            self.save_window_settings()
                            self.debug_log(f"已自动添加调试窗口到白名单: {window_key}")
                    except:
                        pass
                    return True
                
                win32gui.EnumWindows(find_debug_window, None)
            else:
                # Linux 实现
                import subprocess
                result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if "MeowParser 调试窗口" in line or "MeowParser调试窗口" in line:
                            parts = line.split(None, 3)
                            if len(parts) >= 4:
                                title = parts[3]
                                window_key = f"Python - {title}"
                                self.allowed_windows[window_key] = {"enabled": True}
                                self.save_window_settings()
                                self.debug_log(f"已自动添加调试窗口到白名单: {window_key}")
                                break
        except Exception as e:
            self.debug_log(f"自动添加调试窗口错误: {e}")
    
    def show_window_manager(self):
        """显示窗口管理器"""
        # 确保延迟初始化完成
        if self.config_manager is None:
            print("等待初始化完成...")
            self.tray_manager.show_message(
                "提示",
                "正在初始化，请稍候...",
                QSystemTrayIcon.MessageIcon.Information
            )
            return
        
        try:
            if hasattr(self, 'window_manager') and self.window_manager:
                self.window_manager.show()
                self.window_manager.raise_()
                self.window_manager.activateWindow()
                self.window_manager.refresh_windows()
            else:
                self.window_manager = WindowSelector(None, self.allowed_windows, self.save_window_settings)
                self.window_manager.show()
        except Exception as e:
            self.debug_log(f"窗口管理器错误: {e}")
    
    def show_replacement_editor(self):
        """显示配置文件编辑器"""
        # 确保延迟初始化完成
        if self.config_manager is None:
            print("等待初始化完成...")
            self.tray_manager.show_message(
                "提示",
                "正在初始化，请稍候...",
                QSystemTrayIcon.MessageIcon.Information
            )
            return
        
        try:
            if hasattr(self, 'config_editor') and self.config_editor:
                self.config_editor.show()
                self.config_editor.raise_()
                self.config_editor.activateWindow()
                self.config_editor.refresh_config_list()
            else:
                self.config_editor = ConfigFileEditor(None, self.config_manager, self.on_config_changed)
                self.config_editor.show()
        except Exception as e:
            self.debug_log(f"配置编辑器错误: {e}")
    
    def load_window_settings(self):
        """加载窗口设置"""
        from .constants import WINDOW_SETTINGS_FILE, OLD_WINDOW_SETTINGS_FILE
        
        try:
            # 尝试从新位置加载
            if os.path.exists(WINDOW_SETTINGS_FILE):
                with open(WINDOW_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # 如果新位置不存在，尝试从旧位置迁移
            if os.path.exists(OLD_WINDOW_SETTINGS_FILE):
                with open(OLD_WINDOW_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # 保存到新位置
                os.makedirs(os.path.dirname(WINDOW_SETTINGS_FILE), exist_ok=True)
                with open(WINDOW_SETTINGS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)
                
                # 删除旧文件
                try:
                    os.remove(OLD_WINDOW_SETTINGS_FILE)
                    self.debug_log("已迁移窗口设置到 .meowparser 目录")
                except:
                    pass
                
                return settings
        except Exception as e:
            self.debug_log(f"加载窗口设置失败: {e}")
        
        return {}
    
    def save_window_settings(self):
        """保存窗口设置"""
        from .constants import WINDOW_SETTINGS_FILE
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(WINDOW_SETTINGS_FILE), exist_ok=True)
            
            with open(WINDOW_SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.allowed_windows, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.debug_log(f"保存窗口设置失败: {e}")
    
    def _migrate_old_config_if_needed(self):
        """迁移旧配置（如果需要）"""
        old_config_path = Path("replacement_rules.json")
        
        if not old_config_path.exists():
            return
        
        try:
            with open(old_config_path, 'r', encoding='utf-8') as f:
                old_config = json.load(f)
            
            new_config = self.config_manager.migrate_old_config(old_config)
            
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
            
            self.config_manager.load_config(migrated_path)
            
        except Exception as e:
            self.debug_log(f"❌ 配置迁移失败: {e}")
    
    def on_config_changed(self):
        """配置更改回调"""
        if self.config_manager.current_config:
            config_name = self.config_manager.current_config.get('name', '')
            self.debug_log(f"配置已更新: {config_name}")
    
    def change_theme(self, theme_mode: str):
        """切换主题"""
        try:
            app = QApplication.instance()
            self.style_manager.set_theme(theme_mode, app)
            self.tray_manager.update_theme_menu()
            
            # 显示通知
            theme_names = {
                "auto": "自动（跟随系统）",
                "dark": "深色",
                "light": "浅色"
            }
            effective_theme = self.style_manager.get_current_effective_theme()
            effective_name = "深色" if effective_theme == "dark" else "浅色"
            
            if theme_mode == "auto":
                message = f"已切换到自动模式（当前: {effective_name}）"
            else:
                message = f"已切换到{theme_names[theme_mode]}主题"
            
            self.tray_manager.show_message(
                "主题已切换", 
                message, 
                QSystemTrayIcon.MessageIcon.Information
            )
            self.debug_log(f"主题已切换: {theme_mode}")
            
        except Exception as e:
            self.debug_log(f"切换主题错误: {e}")
            self.tray_manager.show_message(
                "切换失败", 
                f"错误: {str(e)}", 
                QSystemTrayIcon.MessageIcon.Critical
            )
    
    def quit_app(self):
        """退出应用"""
        import threading
        
        # 添加超时保护，防止卡死
        def force_quit():
            """3秒后强制退出"""
            time.sleep(3)
            print("⚠️ 超时强制退出")
            os._exit(0)
        
        timeout_thread = threading.Thread(target=force_quit, daemon=True)
        timeout_thread.start()
        
        try:
            print("开始退出程序...")
            
            # 1. 先停止输入监听（最重要）
            self.stop_input_listener()
            time.sleep(0.2)  # 等待清理完成
            
            # 2. 隐藏托盘图标
            if hasattr(self, 'tray_manager') and self.tray_manager:
                try:
                    self.tray_manager.hide()
                    print("已隐藏托盘图标")
                except Exception as e:
                    print(f"隐藏托盘错误: {e}")
            
            # 3. 按顺序关闭窗口
            windows_to_close = [
                ('floating_window', self.floating_window),
                ('debug_window', self.debug_window),
                ('window_manager', self.window_manager),
                ('config_editor', self.config_editor),
            ]
            
            for name, window in windows_to_close:
                if window:
                    try:
                        print(f"关闭 {name}...")
                        window.close()
                        window.deleteLater()  # 标记删除
                    except Exception as e:
                        print(f"关闭 {name} 错误: {e}")
            
            # 4. 保存设置
            try:
                self.save_window_settings()
                print("已保存窗口设置")
            except Exception as e:
                print(f"保存设置错误: {e}")
            
            # 5. 清理单实例锁
            if IS_WINDOWS and self.instance_lock:
                try:
                    ctypes.windll.kernel32.CloseHandle(self.instance_lock)
                    print("已释放单实例锁")
                except Exception as e:
                    print(f"释放锁错误: {e}")
            elif IS_LINUX and self.instance_lock:
                try:
                    self.instance_lock.unlink()
                    print("已删除锁文件")
                except Exception as e:
                    print(f"删除锁文件错误: {e}")
            
            # 6. 处理待处理的事件
            QApplication.processEvents()
            
            # 7. 退出应用
            print("✅ 退出完成")
            QApplication.quit()
            
        except Exception as e:
            print(f"❌ 退出错误: {e}")
            import traceback
            traceback.print_exc()
            # 强制退出
            QApplication.quit()
