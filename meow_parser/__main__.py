#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序入口模块
"""

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from .core.privilege import ensure_admin


def main():
    """主函数"""
    # 在创建 QApplication 之前检查权限
    if not ensure_admin():
        # 权限提升失败，显示错误消息
        app = QApplication(sys.argv)
        QMessageBox.critical(
            None,
            "MeowParser - 权限不足",
            "MeowParser 需要管理员/root 权限才能运行。\n\n"
            "权限提升失败或被拒绝。\n\n"
            "Windows: 请右键程序，选择\"以管理员身份运行\"\n"
            "Linux/macOS: 请使用 sudo 运行程序"
        )
        sys.exit(1)
    
    # 已有管理员权限，继续启动
    from .app import MeowParser
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # 创建应用实例
    parser = MeowParser()
    
    # 延迟应用主题，不阻塞启动
    from PyQt6.QtCore import QTimer
    QTimer.singleShot(0, lambda: _apply_theme(parser, app))
    
    sys.exit(app.exec())


def _apply_theme(parser, app):
    """延迟应用主题"""
    parser.style_manager.apply_theme(app)
    
    # 如果是自动模式，启动主题监控
    if parser.style_manager.current_theme == parser.style_manager.THEME_AUTO:
        parser.style_manager.start_theme_monitoring(app)


if __name__ == "__main__":
    main()
