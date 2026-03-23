import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QStackedWidget, QSplitter,
                             QApplication, QFrame, QSizePolicy, QGridLayout,
                             QScrollArea)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from core.config import config
from core.scheduler import start_schedulers, stop_schedulers
from core.database import db
from modules.material_library import MaterialLibraryWidget
from modules.document_search import DocumentSearchWidget
from modules.smart_analysis import SmartAnalysisWidget
from modules.favorites import FavoritesWidget, QuotesWidget
from modules.settings import SettingsWidget


class NavButton(QPushButton):
    def __init__(self, text, icon_text, parent=None):
        super().__init__(parent)
        self.setText(f"  {icon_text}  {text}")
        self.setCheckable(True)
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            NavButton {
                background-color: transparent;
                color: rgba(255, 255, 255, 0.85);
                border: none;
                padding: 12px 20px;
                text-align: left;
                font-size: 14px;
                border-radius: 4px;
                margin: 2px 8px;
            }
            NavButton:hover {
                background-color: #34495e;
            }
            NavButton:checked {
                background-color: #1890ff;
                color: white;
            }
        """)


class SidebarWidget(QFrame):
    nav_clicked = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setStyleSheet("""
            SidebarWidget {
                background-color: #2c3e50;
                border: none;
            }
        """)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(0)
        
        # Logo区域
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setAlignment(Qt.AlignCenter)
        
        logo_label = QLabel("📚 材料管理系统")
        logo_label.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
        """)
        logo_layout.addWidget(logo_label)
        
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.6);
            font-size: 12px;
        """)
        version_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(version_label)
        
        layout.addWidget(logo_container)
        layout.addSpacing(30)
        
        # 导航按钮组
        self.nav_buttons = []
        nav_items = [
            ("工作台", "🏠", 0),
            ("材料库", "📁", 1),
            ("文档检索", "🔍", 2),
            ("智能分析", "📊", 3),
            ("星标收藏", "⭐", 4),
            ("金句库", "💎", 5),
            ("系统设置", "⚙️", 6),
        ]
        
        for text, icon, index in nav_items:
            btn = NavButton(text, icon)
            btn.clicked.connect(lambda checked, idx=index: self.on_nav_clicked(idx))
            self.nav_buttons.append(btn)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # 底部信息
        footer = QLabel("© 2026 党政机关")
        footer.setStyleSheet("""
            color: rgba(255, 255, 255, 0.5);
            font-size: 11px;
            padding: 10px;
        """)
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
    
    def on_nav_clicked(self, index):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        self.nav_clicked.emit(index)
    
    def set_active_index(self, index):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)


class ShortcutCard(QFrame):
    clicked = pyqtSignal()
    
    def __init__(self, icon, title, desc, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            ShortcutCard {
                background-color: white;
                border: 1px solid #e8e8e8;
                border-radius: 8px;
            }
            ShortcutCard:hover {
                border-color: #1890ff;
                background-color: #f0f7ff;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(120)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 36px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        desc_label = QLabel(desc)
        desc_label.setStyleSheet("font-size: 12px; color: #999;")
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
    
    def mousePressEvent(self, event):
        self.clicked.emit()


class StatCard(QFrame):
    def __init__(self, icon, label, value="0", parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            StatCard {
                background-color: white;
                border: 1px solid #e8e8e8;
                border-radius: 8px;
            }
        """)
        self.setMinimumHeight(100)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(15)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 40px;")
        layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #1890ff;")
        text_layout.addWidget(self.value_label)
        
        label_label = QLabel(label)
        label_label.setStyleSheet("font-size: 14px; color: #666;")
        text_layout.addWidget(label_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
    
    def set_value(self, value):
        self.value_label.setText(str(value))


class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_stats()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # 标题
        title = QLabel("工作台")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #333;
        """)
        layout.addWidget(title)
        
        # 快捷入口
        shortcut_label = QLabel("快捷入口")
        shortcut_label.setStyleSheet("font-size: 16px; color: #666;")
        layout.addWidget(shortcut_label)
        
        shortcuts_widget = QWidget()
        shortcuts_layout = QGridLayout(shortcuts_widget)
        shortcuts_layout.setSpacing(20)
        
        shortcuts = [
            ("📁", "材料库", "查看和管理文档"),
            ("🔍", "文档搜索", "快速查找文档"),
            ("📊", "分析工具", "智能分析文档"),
            ("📥", "导入文档", "批量导入文件"),
        ]
        
        for i, (icon, title_text, desc) in enumerate(shortcuts):
            card = ShortcutCard(icon, title_text, desc)
            card.clicked.connect(lambda idx=i: self.on_shortcut_click(idx))
            shortcuts_layout.addWidget(card, 0, i)
        
        layout.addWidget(shortcuts_widget)
        
        # 统计概览
        stats_label = QLabel("统计概览")
        stats_label.setStyleSheet("font-size: 16px; color: #666; margin-top: 10px;")
        layout.addWidget(stats_label)
        
        stats_widget = QWidget()
        stats_layout = QGridLayout(stats_widget)
        stats_layout.setSpacing(20)
        
        self.stat_cards = [
            StatCard("📄", "文档总数", "0"),
            StatCard("📈", "本月新增", "0"),
            StatCard("📝", "总字数", "0"),
            StatCard("🏷️", "标签数量", "0"),
        ]
        
        for i, card in enumerate(self.stat_cards):
            stats_layout.addWidget(card, 0, i)
        
        layout.addWidget(stats_widget)
        layout.addStretch()
    
    def load_stats(self):
        """加载统计数据"""
        try:
            # 文档总数
            documents = db.get_all_documents()
            self.stat_cards[0].set_value(len(documents))
            
            # 本月新增
            from datetime import datetime
            current_month = datetime.now().month
            current_year = datetime.now().year
            month_count = 0
            for d in documents:
                if d['import_date']:
                    try:
                        import_date_str = str(d['import_date'])
                        # 处理各种日期格式
                        if 'T' in import_date_str:
                            # ISO格式: 2024-01-01T12:00:00
                            import_date = datetime.fromisoformat(import_date_str.replace('Z', '+00:00'))
                        else:
                            # 普通格式: 2024-01-01 12:00:00
                            import_date = datetime.strptime(import_date_str, '%Y-%m-%d %H:%M:%S')
                        
                        if import_date.month == current_month and import_date.year == current_year:
                            month_count += 1
                    except Exception:
                        continue
            self.stat_cards[1].set_value(month_count)
            
            # 总字数
            total_chars = sum(len(d['content_text'] or '') for d in documents)
            self.stat_cards[2].set_value(f"{total_chars // 10000}万" if total_chars > 10000 else str(total_chars))
            
            # 标签数量
            tags = db.get_tags()
            self.stat_cards[3].set_value(len(tags))
            
        except Exception as e:
            print(f"加载统计失败: {e}")
    
    def on_shortcut_click(self, index):
        """快捷入口点击"""
        main_window = self.window()
        if hasattr(main_window, 'switch_page'):
            if index == 0:  # 材料库
                main_window.switch_page(1)
            elif index == 1:  # 文档搜索
                main_window.switch_page(2)
            elif index == 2:  # 分析工具
                main_window.switch_page(3)
            elif index == 3:  # 导入文档 - 直接弹出导入对话框
                main_window.show_import_dialog()


class PlaceholderWidget(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        label = QLabel(f"{self.title}\n\n模块开发中...")
        label.setStyleSheet("""
            font-size: 20px;
            color: #999;
            text-align: center;
        """)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("材料管理系统")
        self.setMinimumSize(1200, 800)
        
        # 加载窗口大小配置
        width = config.get('general.window_width', 1400)
        height = config.get('general.window_height', 900)
        self.resize(width, height)
        
        self.setup_ui()
    
    def setup_ui(self):
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 侧边栏
        self.sidebar = SidebarWidget()
        self.sidebar.nav_clicked.connect(self.switch_page)
        splitter.addWidget(self.sidebar)
        
        # 内容区域
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                background-color: #f5f7fa;
            }
        """)
        
        # 添加各个页面
        self.dashboard = DashboardWidget()
        self.content_stack.addWidget(self.dashboard)
        
        self.material_lib = MaterialLibraryWidget()
        self.content_stack.addWidget(self.material_lib)
        
        self.search_page = DocumentSearchWidget()
        self.content_stack.addWidget(self.search_page)
        
        self.analysis_page = SmartAnalysisWidget()
        self.content_stack.addWidget(self.analysis_page)
        
        self.favorites_page = FavoritesWidget()
        self.content_stack.addWidget(self.favorites_page)
        
        self.quotes_page = QuotesWidget()
        self.content_stack.addWidget(self.quotes_page)
        
        self.settings_page = SettingsWidget()
        self.content_stack.addWidget(self.settings_page)
        
        splitter.addWidget(self.content_stack)
        splitter.setSizes([200, 1200])
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # 默认选中工作台
        self.sidebar.set_active_index(0)
    
    def switch_page(self, index):
        self.content_stack.setCurrentIndex(index)
        self.sidebar.set_active_index(index)
    
    def show_import_dialog(self):
        """显示导入文档对话框"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        from core.archiver import DocumentImporter
        from pathlib import Path
        
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择文档",
            "",
            "文档文件 (*.docx *.pdf *.txt *.xlsx *.xls);;所有文件 (*.*)"
        )
        
        if file_paths:
            success_count = 0
            failed_count = 0
            failed_files = []
            
            for file_path in file_paths:
                importer = DocumentImporter()
                result = importer.import_file(file_path)
                
                if result['success']:
                    success_count += 1
                else:
                    failed_count += 1
                    failed_files.append(f"{Path(file_path).name}: {result['error']}")
            
            msg = f"导入完成！\n\n成功: {success_count}\n失败: {failed_count}"
            if failed_files:
                msg += "\n\n失败文件:\n" + "\n".join(failed_files[:5])
                if len(failed_files) > 5:
                    msg += f"\n...还有 {len(failed_files) - 5} 个文件"
            
            QMessageBox.information(self, "导入结果", msg)
            # 刷新材料库数据
            self.material_lib.load_data()
    
    def closeEvent(self, event):
        # 保存窗口大小
        if config.get('general.remember_window_size', True):
            config.set('general.window_width', self.width())
            config.set('general.window_height', self.height())
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    # 启用高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
