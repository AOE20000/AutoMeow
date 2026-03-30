#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
样式管理模块 - BreezeStyleSheets 集成
"""

import json
import os
from PyQt6.QtCore import QFile, QTextStream, QTimer
from PyQt6.QtWidgets import QApplication

from ..constants import IS_WINDOWS, IS_LINUX, IS_MACOS


class ThemeDetector:
    """系统主题检测器"""
    
    # 缓存主题检测结果
    _cached_theme = None
    _cache_time = 0
    _cache_duration = 5  # 缓存 5 秒
    
    @staticmethod
    def get_system_theme():
        """检测系统主题（dark/light）- 带缓存"""
        import time
        current_time = time.time()
        
        # 如果缓存有效，直接返回
        if (ThemeDetector._cached_theme is not None and 
            current_time - ThemeDetector._cache_time < ThemeDetector._cache_duration):
            return ThemeDetector._cached_theme
        
        # 检测主题
        try:
            if IS_WINDOWS:
                theme = ThemeDetector._get_windows_theme()
            elif IS_MACOS:
                theme = ThemeDetector._get_macos_theme()
            elif IS_LINUX:
                theme = ThemeDetector._get_linux_theme()
            else:
                theme = "dark"
        except Exception as e:
            print(f"检测系统主题失败: {e}")
            theme = "dark"
        
        # 更新缓存
        ThemeDetector._cached_theme = theme
        ThemeDetector._cache_time = current_time
        
        return theme
    
    @staticmethod
    def _get_windows_theme():
        """检测 Windows 主题"""
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(
                registry,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return "light" if value == 1 else "dark"
        except:
            return "dark"
    
    @staticmethod
    def _get_macos_theme():
        """检测 macOS 主题（优化版本）"""
        try:
            import subprocess
            result = subprocess.run(
                ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                capture_output=True,
                text=True,
                timeout=0.5  # 减少超时时间到 0.5 秒
            )
            return "dark" if result.returncode == 0 else "light"
        except subprocess.TimeoutExpired:
            print("macOS 主题检测超时，使用默认深色主题")
            return "dark"
        except:
            return "dark"
    
    @staticmethod
    def _get_linux_theme():
        """检测 Linux 主题"""
        try:
            # 尝试读取 GTK 主题设置
            gtk_config = os.path.expanduser("~/.config/gtk-3.0/settings.ini")
            if os.path.exists(gtk_config):
                with open(gtk_config, 'r') as f:
                    content = f.read()
                    if 'dark' in content.lower():
                        return "dark"
                    return "light"
        except:
            pass
        
        return "dark"


class StyleManager:
    """样式管理器"""
    
    # 主题模式
    THEME_AUTO = "auto"
    THEME_DARK = "dark"
    THEME_LIGHT = "light"
    
    # 内置样式定义
    BREEZE_DARK_STYLE = """
/* BreezeStyleSheets inspired dark theme for MeowParser */

/* 全局样式 */
QWidget {
    background-color: #31363b;
    color: #eff0f1;
    font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
    font-size: 9pt;
}

/* 主窗口 */
QMainWindow {
    background-color: #31363b;
}

/* 菜单栏 */
QMenuBar {
    background-color: #31363b;
    color: #eff0f1;
    border-bottom: 1px solid #76797c;
}

QMenuBar::item {
    background-color: transparent;
    padding: 4px 12px;
}

QMenuBar::item:selected {
    background-color: #3daee9;
    color: #ffffff;
}

QMenuBar::item:pressed {
    background-color: #2a79a3;
}

/* 菜单 */
QMenu {
    background-color: #31363b;
    color: #eff0f1;
    border: 1px solid #76797c;
    padding: 4px;
}

QMenu::item {
    padding: 6px 30px 6px 30px;
    border-radius: 3px;
}

QMenu::item:selected {
    background-color: #3daee9;
    color: #ffffff;
}

QMenu::item:disabled {
    color: #76797c;
}

QMenu::separator {
    height: 1px;
    background-color: #76797c;
    margin: 4px 8px;
}

QMenu::indicator {
    width: 16px;
    height: 16px;
    margin-left: 6px;
}

QMenu::indicator:checked {
    image: url(:/icons/check.png);
}

/* 按钮 */
QPushButton {
    background-color: #31363b;
    color: #eff0f1;
    border: 1px solid #76797c;
    border-radius: 4px;
    padding: 6px 16px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #3daee9;
    border-color: #3daee9;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #2a79a3;
    border-color: #2a79a3;
}

QPushButton:disabled {
    background-color: #454545;
    color: #76797c;
    border-color: #76797c;
}

QPushButton:default {
    border: 2px solid #3daee9;
}

/* 输入框 */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #1d2023;
    color: #eff0f1;
    border: 1px solid #76797c;
    border-radius: 4px;
    padding: 4px 8px;
    selection-background-color: #3daee9;
    selection-color: #ffffff;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #3daee9;
}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
    background-color: #2c3034;
    color: #76797c;
}

/* 组合框 */
QComboBox {
    background-color: #31363b;
    color: #eff0f1;
    border: 1px solid #76797c;
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 20px;
}

QComboBox:hover {
    border-color: #3daee9;
}

QComboBox:disabled {
    background-color: #454545;
    color: #76797c;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: url(:/icons/down-arrow.png);
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #31363b;
    color: #eff0f1;
    border: 1px solid #76797c;
    selection-background-color: #3daee9;
    selection-color: #ffffff;
}

/* 复选框 */
QCheckBox {
    color: #eff0f1;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #76797c;
    border-radius: 3px;
    background-color: #1d2023;
}

QCheckBox::indicator:hover {
    border-color: #3daee9;
}

QCheckBox::indicator:checked {
    background-color: #3daee9;
    border-color: #3daee9;
    image: url(:/icons/check-white.png);
}

QCheckBox::indicator:disabled {
    background-color: #454545;
    border-color: #76797c;
}

/* 单选按钮 */
QRadioButton {
    color: #eff0f1;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #76797c;
    border-radius: 9px;
    background-color: #1d2023;
}

QRadioButton::indicator:hover {
    border-color: #3daee9;
}

QRadioButton::indicator:checked {
    background-color: #3daee9;
    border-color: #3daee9;
}

QRadioButton::indicator:checked::after {
    width: 8px;
    height: 8px;
    border-radius: 4px;
    background-color: #ffffff;
}

/* 树形控件 */
QTreeWidget, QTreeView {
    background-color: #1d2023;
    color: #eff0f1;
    border: 1px solid #76797c;
    border-radius: 4px;
    selection-background-color: #3daee9;
    selection-color: #ffffff;
    alternate-background-color: #252a2e;
}

QTreeWidget::item, QTreeView::item {
    padding: 4px;
    border: none;
}

QTreeWidget::item:hover, QTreeView::item:hover {
    background-color: rgba(61, 173, 232, 0.1);
}

QTreeWidget::item:selected, QTreeView::item:selected {
    background-color: #3daee9;
    color: #ffffff;
}

QTreeWidget::branch, QTreeView::branch {
    background-color: transparent;
}

QHeaderView::section {
    background-color: #31363b;
    color: #eff0f1;
    border: none;
    border-right: 1px solid #76797c;
    border-bottom: 1px solid #76797c;
    padding: 6px 8px;
}

QHeaderView::section:hover {
    background-color: #3daee9;
    color: #ffffff;
}

/* 滚动条 */
QScrollBar:vertical {
    background-color: #1d2023;
    width: 14px;
    border-radius: 7px;
}

QScrollBar::handle:vertical {
    background-color: #76797c;
    border-radius: 7px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #3daee9;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #1d2023;
    height: 14px;
    border-radius: 7px;
}

QScrollBar::handle:horizontal {
    background-color: #76797c;
    border-radius: 7px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #3daee9;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* 标签 */
QLabel {
    color: #eff0f1;
    background-color: transparent;
}

/* 分组框 */
QGroupBox {
    color: #eff0f1;
    border: 1px solid #76797c;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 8px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    background-color: #31363b;
}

/* 对话框 */
QDialog {
    background-color: #31363b;
}

/* 消息框 */
QMessageBox {
    background-color: #31363b;
}

QMessageBox QLabel {
    color: #eff0f1;
}

/* 工具提示 */
QToolTip {
    background-color: #31363b;
    color: #eff0f1;
    border: 1px solid #76797c;
    border-radius: 4px;
    padding: 4px 8px;
}

/* 状态栏 */
QStatusBar {
    background-color: #31363b;
    color: #eff0f1;
    border-top: 1px solid #76797c;
}

/* 进度条 */
QProgressBar {
    background-color: #1d2023;
    border: 1px solid #76797c;
    border-radius: 4px;
    text-align: center;
    color: #eff0f1;
}

QProgressBar::chunk {
    background-color: #3daee9;
    border-radius: 3px;
}

/* 标签页 */
QTabWidget::pane {
    background-color: #31363b;
    border: 1px solid #76797c;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #2c3034;
    color: #eff0f1;
    border: 1px solid #76797c;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #31363b;
    border-bottom: 2px solid #3daee9;
}

QTabBar::tab:hover:!selected {
    background-color: #3daee9;
    color: #ffffff;
}

/* 悬浮窗特殊样式 - 现代卡片设计 */
#FloatingInputWindow {
    background-color: #1e1e1e;
    border: 2px solid #3daee9;
    border-radius: 8px;
}

#FloatingInputWindow QLineEdit {
    background-color: #2d2d30;
    color: #cccccc;
    border: none;
    border-radius: 6px;
    padding: 12px 16px;
    font-size: 11pt;
    selection-background-color: #3daee9;
    selection-color: #ffffff;
}

#FloatingInputWindow QLineEdit:focus {
    background-color: #3e3e42;
}
"""
    
    BREEZE_LIGHT_STYLE = """
/* BreezeStyleSheets inspired light theme for MeowParser */

/* 全局样式 */
QWidget {
    background-color: #eff0f1;
    color: #31363b;
    font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
    font-size: 9pt;
}

/* 主窗口 */
QMainWindow {
    background-color: #eff0f1;
}

/* 菜单栏 */
QMenuBar {
    background-color: #eff0f1;
    color: #31363b;
    border-bottom: 1px solid #bdc3c7;
}

QMenuBar::item {
    background-color: transparent;
    padding: 4px 12px;
}

QMenuBar::item:selected {
    background-color: #3daee9;
    color: #ffffff;
}

QMenuBar::item:pressed {
    background-color: #2a79a3;
}

/* 菜单 */
QMenu {
    background-color: #fcfcfc;
    color: #31363b;
    border: 1px solid #bdc3c7;
    padding: 4px;
}

QMenu::item {
    padding: 6px 30px 6px 30px;
    border-radius: 3px;
}

QMenu::item:selected {
    background-color: #3daee9;
    color: #ffffff;
}

QMenu::item:disabled {
    color: #a0a0a0;
}

QMenu::separator {
    height: 1px;
    background-color: #bdc3c7;
    margin: 4px 8px;
}

/* 按钮 */
QPushButton {
    background-color: #fcfcfc;
    color: #31363b;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 6px 16px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #3daee9;
    border-color: #3daee9;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #2a79a3;
    border-color: #2a79a3;
}

QPushButton:disabled {
    background-color: #e0e0e0;
    color: #a0a0a0;
    border-color: #bdc3c7;
}

QPushButton:default {
    border: 2px solid #3daee9;
}

/* 输入框 */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    color: #31363b;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 4px 8px;
    selection-background-color: #3daee9;
    selection-color: #ffffff;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #3daee9;
}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
    background-color: #f0f0f0;
    color: #a0a0a0;
}

/* 组合框 */
QComboBox {
    background-color: #fcfcfc;
    color: #31363b;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 20px;
}

QComboBox:hover {
    border-color: #3daee9;
}

QComboBox:disabled {
    background-color: #e0e0e0;
    color: #a0a0a0;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #31363b;
    border: 1px solid #bdc3c7;
    selection-background-color: #3daee9;
    selection-color: #ffffff;
}

/* 复选框 */
QCheckBox {
    color: #31363b;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #bdc3c7;
    border-radius: 3px;
    background-color: #ffffff;
}

QCheckBox::indicator:hover {
    border-color: #3daee9;
}

QCheckBox::indicator:checked {
    background-color: #3daee9;
    border-color: #3daee9;
}

QCheckBox::indicator:disabled {
    background-color: #e0e0e0;
    border-color: #bdc3c7;
}

/* 单选按钮 */
QRadioButton {
    color: #31363b;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #bdc3c7;
    border-radius: 9px;
    background-color: #ffffff;
}

QRadioButton::indicator:hover {
    border-color: #3daee9;
}

QRadioButton::indicator:checked {
    background-color: #3daee9;
    border-color: #3daee9;
}

/* 树形控件 */
QTreeWidget, QTreeView {
    background-color: #ffffff;
    color: #232629;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    selection-background-color: #3daee9;
    selection-color: #ffffff;
    alternate-background-color: #f8f8f8;
}

QTreeWidget::item, QTreeView::item {
    padding: 4px;
    border: none;
    color: #232629;
}

QTreeWidget::item:hover, QTreeView::item:hover {
    background-color: rgba(61, 173, 232, 0.15);
    color: #232629;
}

QTreeWidget::item:selected, QTreeView::item:selected {
    background-color: #3daee9;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #e8e8e8;
    color: #232629;
    border: none;
    border-right: 1px solid #bdc3c7;
    border-bottom: 1px solid #bdc3c7;
    padding: 6px 8px;
    font-weight: 500;
}

QHeaderView::section:hover {
    background-color: #3daee9;
    color: #ffffff;
}

/* 滚动条 */
QScrollBar:vertical {
    background-color: #f0f0f0;
    width: 14px;
    border-radius: 7px;
}

QScrollBar::handle:vertical {
    background-color: #bdc3c7;
    border-radius: 7px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #3daee9;
}

QScrollBar:horizontal {
    background-color: #f0f0f0;
    height: 14px;
    border-radius: 7px;
}

QScrollBar::handle:horizontal {
    background-color: #bdc3c7;
    border-radius: 7px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #3daee9;
}

/* 标签 */
QLabel {
    color: #31363b;
    background-color: transparent;
}

/* 分组框 */
QGroupBox {
    color: #31363b;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 8px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    background-color: #eff0f1;
}

/* 对话框 */
QDialog {
    background-color: #eff0f1;
}

/* 消息框 */
QMessageBox {
    background-color: #eff0f1;
}

QMessageBox QLabel {
    color: #31363b;
}

/* 工具提示 */
QToolTip {
    background-color: #fcfcfc;
    color: #31363b;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 4px 8px;
}

/* 状态栏 */
QStatusBar {
    background-color: #eff0f1;
    color: #31363b;
    border-top: 1px solid #bdc3c7;
}

/* 进度条 */
QProgressBar {
    background-color: #ffffff;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    text-align: center;
    color: #31363b;
}

QProgressBar::chunk {
    background-color: #3daee9;
    border-radius: 3px;
}

/* 标签页 */
QTabWidget::pane {
    background-color: #eff0f1;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #e0e0e0;
    color: #31363b;
    border: 1px solid #bdc3c7;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #eff0f1;
    border-bottom: 2px solid #3daee9;
}

QTabBar::tab:hover:!selected {
    background-color: #3daee9;
    color: #ffffff;
}

/* 悬浮窗特殊样式 - 现代卡片设计 */
#FloatingInputWindow {
    background-color: #f5f5f5;
    border: 2px solid #3daee9;
    border-radius: 8px;
}

#FloatingInputWindow QLineEdit {
    background-color: #ffffff;
    color: #31363b;
    border: none;
    border-radius: 6px;
    padding: 12px 16px;
    font-size: 11pt;
    selection-background-color: #3daee9;
    selection-color: #ffffff;
}

#FloatingInputWindow QLineEdit:focus {
    background-color: #fafafa;
}
"""
    
    def __init__(self):
        """初始化样式管理器"""
        self.current_theme = self.THEME_AUTO
        self.theme_config_file = ".meowparser/theme_settings.json"
        self.load_theme_preference()
        self.theme_monitor_timer = None
    
    def load_theme_preference(self):
        """加载主题偏好"""
        try:
            if os.path.exists(self.theme_config_file):
                with open(self.theme_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.current_theme = config.get('theme', self.THEME_AUTO)
        except Exception as e:
            print(f"加载主题偏好失败: {e}")
            self.current_theme = self.THEME_AUTO
    
    def save_theme_preference(self):
        """保存主题偏好"""
        try:
            os.makedirs(os.path.dirname(self.theme_config_file), exist_ok=True)
            with open(self.theme_config_file, 'w', encoding='utf-8') as f:
                json.dump({'theme': self.current_theme}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存主题偏好失败: {e}")
    
    def set_theme(self, theme_mode: str, app: QApplication):
        """设置主题模式"""
        self.current_theme = theme_mode
        self.save_theme_preference()
        self.apply_theme(app)
        
        # 如果是自动模式，启动监控
        if theme_mode == self.THEME_AUTO:
            self.start_theme_monitoring(app)
        else:
            self.stop_theme_monitoring()
    
    def apply_theme(self, app: QApplication):
        """应用主题"""
        if self.current_theme == self.THEME_AUTO:
            system_theme = ThemeDetector.get_system_theme()
            if system_theme == "light":
                app.setStyleSheet(self.BREEZE_LIGHT_STYLE)
            else:
                app.setStyleSheet(self.BREEZE_DARK_STYLE)
        elif self.current_theme == self.THEME_LIGHT:
            app.setStyleSheet(self.BREEZE_LIGHT_STYLE)
        else:
            app.setStyleSheet(self.BREEZE_DARK_STYLE)
    
    def start_theme_monitoring(self, app: QApplication):
        """启动主题监控（仅在自动模式下）"""
        if self.theme_monitor_timer is None:
            self.theme_monitor_timer = QTimer()
            self.theme_monitor_timer.timeout.connect(lambda: self._check_theme_change(app))
            self.theme_monitor_timer.start(5000)  # 每5秒检查一次
    
    def stop_theme_monitoring(self):
        """停止主题监控"""
        if self.theme_monitor_timer:
            self.theme_monitor_timer.stop()
            self.theme_monitor_timer = None
    
    def _check_theme_change(self, app: QApplication):
        """检查系统主题是否变化"""
        if self.current_theme == self.THEME_AUTO:
            self.apply_theme(app)
    
    def get_current_effective_theme(self):
        """获取当前实际生效的主题"""
        if self.current_theme == self.THEME_AUTO:
            return ThemeDetector.get_system_theme()
        return self.current_theme
    
    @staticmethod
    def apply_breeze_dark(app: QApplication):
        """应用 Breeze Dark 样式（静态方法，向后兼容）"""
        app.setStyleSheet(StyleManager.BREEZE_DARK_STYLE)
    
    @staticmethod
    def apply_custom_style(app: QApplication, stylesheet_path: str = None):
        """应用自定义样式表"""
        if stylesheet_path:
            try:
                file = QFile(stylesheet_path)
                if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
                    stream = QTextStream(file)
                    app.setStyleSheet(stream.readAll())
                    file.close()
                    return True
            except Exception as e:
                print(f"加载样式表失败: {e}")
        
        # 回退到内置样式
        StyleManager.apply_breeze_dark(app)
        return False
    
    def get_menu_style(self, theme_mode: str = None):
        """获取菜单样式（用于系统托盘菜单）"""
        if theme_mode is None:
            theme_mode = self.get_current_effective_theme()
        
        if theme_mode == "light":
            return """
QMenu {
    background-color: #fcfcfc;
    color: #31363b;
    border: 1px solid #bdc3c7;
    padding: 4px;
}

QMenu::item {
    padding: 8px 32px 8px 32px;
    border-radius: 3px;
}

QMenu::item:selected {
    background-color: #3daee9;
    color: #ffffff;
}

QMenu::item:disabled {
    color: #a0a0a0;
}

QMenu::separator {
    height: 1px;
    background-color: #bdc3c7;
    margin: 6px 10px;
}

QMenu::indicator {
    width: 16px;
    height: 16px;
    margin-left: 6px;
}

QMenu::indicator:checked {
    background-color: #3daee9;
    border: 1px solid #3daee9;
    border-radius: 2px;
}
"""
        else:
            return """
QMenu {
    background-color: #31363b;
    color: #eff0f1;
    border: 1px solid #76797c;
    padding: 4px;
}

QMenu::item {
    padding: 8px 32px 8px 32px;
    border-radius: 3px;
}

QMenu::item:selected {
    background-color: #3daee9;
    color: #ffffff;
}

QMenu::item:disabled {
    color: #76797c;
}

QMenu::separator {
    height: 1px;
    background-color: #76797c;
    margin: 6px 10px;
}

QMenu::indicator {
    width: 16px;
    height: 16px;
    margin-left: 6px;
}

QMenu::indicator:checked {
    background-color: #3daee9;
    border: 1px solid #3daee9;
    border-radius: 2px;
}
"""
