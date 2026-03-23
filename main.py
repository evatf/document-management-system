#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

project_root = str(Path(__file__).parent.resolve())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from widgets.main_window import MainWindow
from core.config import config
from core.database import db
from core.scheduler import start_schedulers, stop_schedulers
from core.styles import GLOBAL_STYLE


def get_system_font():
    """获取跨平台系统字体"""
    if sys.platform == 'win32':
        return "Microsoft YaHei"
    elif sys.platform == 'darwin':
        return "PingFang SC"
    else:
        # Linux/UOS - 尝试多个字体，返回第一个可用的
        from PyQt5.QtGui import QFontDatabase
        font_db = QFontDatabase()
        available_fonts = font_db.families()
        
        # 优先尝试的字体列表（按优先级排序）
        preferred_fonts = [
            "WenQuanYi Zen Hei",      # 文泉驿正黑（UOS默认）
            "WenQuanYi Micro Hei",    # 文泉驿微米黑
            "Noto Sans CJK SC",       # Google Noto字体
            "Source Han Sans SC",     # Adobe思源黑体
            "Droid Sans Fallback",    # Android备用字体
            "DejaVu Sans",            # 通用字体
        ]
        
        for font in preferred_fonts:
            if font in available_fonts:
                return font
        
        # 如果都没有，返回通用字体
        return "DejaVu Sans"


def main():
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("材料管理系统")
    app.setApplicationVersion("1.0.0")
    
    app.setStyle('Fusion')
    
    font = QFont(get_system_font(), 10)
    app.setFont(font)
    
    app.setStyleSheet(GLOBAL_STYLE)
    
    start_schedulers()
    
    window = MainWindow()
    window.show()
    
    try:
        sys.exit(app.exec_())
    finally:
        stop_schedulers()


if __name__ == '__main__':
    main()
