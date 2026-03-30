#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统托盘图标管理模块
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QAction
from PyQt6.QtCore import Qt


class TrayIconManager:
    """系统托盘图标管理器"""
    
    def __init__(self, parent_app):
        """
        初始化托盘图标管理器
        
        Args:
            parent_app: 父应用实例，需要提供以下方法：
                - toggle(): 切换启用/禁用
                - show_window_manager(): 显示窗口管理器
                - show_replacement_editor(): 显示规则编辑器
                - show_debug_window(): 显示调试窗口
                - quit_app(): 退出应用
                - is_admin: 是否管理员权限（属性）
        """
        self.parent_app = parent_app
        self.tray_icon = None
        self.toggle_action = None
        self.setup_tray()
    
    def create_icon(self, color):
        """
        创建托盘图标（优化版本）
        
        Args:
            color: 图标颜色 ('red' 或 'green')
            
        Returns:
            QIcon: 创建的图标
        """
        # 使用更小的尺寸提升性能
        pixmap = QPixmap(24, 24)
        pixmap.fill(QColor(color))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor('white'))
        # 使用系统字体，避免字体查找延迟
        font = QFont()
        font.setPixelSize(16)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "喵")
        painter.end()
        
        return QIcon(pixmap)
    
    def setup_tray(self):
        """设置系统托盘（优化版本 - 快速启动）"""
        self.tray_icon = QSystemTrayIcon(self.create_icon('red'))
        self.tray_icon.setToolTip("MeowParser (禁用)")
        
        # 创建菜单
        self.menu = QMenu()
        
        # 延迟应用菜单样式（不阻塞启动）
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(50, self.update_menu_style)
        
        self.toggle_action = QAction("启用/禁用", self.menu)
        self.toggle_action.triggered.connect(self.parent_app.toggle)
        self.menu.addAction(self.toggle_action)
        
        self.menu.addSeparator()
        
        window_action = QAction("窗口管理", self.menu)
        window_action.triggered.connect(self.parent_app.show_window_manager)
        self.menu.addAction(window_action)
        
        rules_action = QAction("替换规则", self.menu)
        rules_action.triggered.connect(self.parent_app.show_replacement_editor)
        self.menu.addAction(rules_action)
        
        debug_action = QAction("调试窗口", self.menu)
        debug_action.triggered.connect(self.parent_app.show_debug_window)
        self.menu.addAction(debug_action)
        
        self.menu.addSeparator()
        
        # 主题切换菜单（延迟创建子菜单项）
        self.theme_menu = QMenu("主题", self.menu)
        self.theme_auto_action = None
        self.theme_dark_action = None
        self.theme_light_action = None
        
        # 连接菜单显示信号，延迟创建主题菜单项
        self.theme_menu.aboutToShow.connect(self._ensure_theme_menu_items)
        
        self.menu.addMenu(self.theme_menu)
        self.menu.addSeparator()
        
        quit_action = QAction("退出", self.menu)
        quit_action.triggered.connect(self.parent_app.quit_app)
        self.menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(self.menu)
    
    def _ensure_theme_menu_items(self):
        """确保主题菜单项已创建（延迟创建）"""
        if self.theme_auto_action is not None:
            # 已创建，只更新状态
            self.update_theme_menu()
            return
        
        # 首次创建主题菜单项
        self.theme_auto_action = QAction("🌓 自动（跟随系统）", self.theme_menu)
        self.theme_auto_action.setCheckable(True)
        self.theme_auto_action.triggered.connect(lambda: self.parent_app.change_theme("auto"))
        self.theme_menu.addAction(self.theme_auto_action)
        
        self.theme_dark_action = QAction("🌙 深色", self.theme_menu)
        self.theme_dark_action.setCheckable(True)
        self.theme_dark_action.triggered.connect(lambda: self.parent_app.change_theme("dark"))
        self.theme_menu.addAction(self.theme_dark_action)
        
        self.theme_light_action = QAction("☀️ 浅色", self.theme_menu)
        self.theme_light_action.setCheckable(True)
        self.theme_light_action.triggered.connect(lambda: self.parent_app.change_theme("light"))
        self.theme_menu.addAction(self.theme_light_action)
        
        # 应用样式
        self.update_menu_style()
        
        # 更新选中状态
        self.update_theme_menu()
    
    def update_menu_style(self):
        """更新菜单样式"""
        if hasattr(self.parent_app, 'style_manager'):
            style = self.parent_app.style_manager.get_menu_style()
            if hasattr(self, 'menu') and self.menu:
                self.menu.setStyleSheet(style)
            if hasattr(self, 'theme_menu') and self.theme_menu:
                self.theme_menu.setStyleSheet(style)
    
    def update_theme_menu(self):
        """更新主题菜单选中状态"""
        # 如果主题菜单项还未创建，跳过
        if self.theme_auto_action is None:
            return
        
        if hasattr(self.parent_app, 'style_manager'):
            current_theme = self.parent_app.style_manager.current_theme
            self.theme_auto_action.setChecked(current_theme == "auto")
            self.theme_dark_action.setChecked(current_theme == "dark")
            self.theme_light_action.setChecked(current_theme == "light")
        
        # 同时更新菜单样式
        self.update_menu_style()
    
    def show(self):
        """显示托盘图标"""
        if self.tray_icon:
            self.tray_icon.show()
    
    def hide(self):
        """隐藏托盘图标"""
        if self.tray_icon:
            self.tray_icon.hide()
    
    def update_icon(self, enabled):
        """
        更新图标状态
        
        Args:
            enabled: 是否启用状态
        """
        if self.tray_icon:
            color = 'green' if enabled else 'red'
            status = "启用" if enabled else "禁用"
            self.tray_icon.setIcon(self.create_icon(color))
            self.tray_icon.setToolTip(f"MeowParser ({status})")
    
    def show_message(self, title, message, icon=QSystemTrayIcon.MessageIcon.Information, duration=2000):
        """
        显示托盘消息
        
        Args:
            title: 消息标题
            message: 消息内容
            icon: 消息图标类型
            duration: 显示时长（毫秒）
        """
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, icon, duration)
