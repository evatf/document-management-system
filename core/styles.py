# -*- coding: utf-8 -*-
"""
全局样式定义 - 确保整个应用风格统一
"""

GLOBAL_STYLE = """
/* ==================== 全局基础样式 ==================== */
QWidget {
    font-family: "Microsoft YaHei", "Noto Sans CJK SC", "PingFang SC", "WenQuanYi Micro Hei", sans-serif;
    font-size: 14px;
    color: #333;
}

QMainWindow {
    background-color: #f5f7fa;
}

/* ==================== 滚动条样式 ==================== */
QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 10px;
    border-radius: 5px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #c0c0c0;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a0a0a0;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::horizontal {
    background-color: #f5f5f5;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #c0c0c0;
    border-radius: 5px;
    min-width: 30px;
}

/* ==================== 按钮样式 ==================== */
QPushButton {
    background-color: white;
    color: #333;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 14px;
    min-height: 32px;
}

QPushButton:hover {
    color: #1890ff;
    border-color: #1890ff;
}

QPushButton:pressed {
    color: #096dd9;
    border-color: #096dd9;
}

QPushButton:disabled {
    color: #bfbfbf;
    background-color: #f5f5f5;
    border-color: #d9d9d9;
}

/* 主要按钮 */
QPushButton#primary {
    background-color: #1890ff;
    color: white;
    border: none;
}

QPushButton#primary:hover {
    background-color: #40a9ff;
}

QPushButton#primary:pressed {
    background-color: #096dd9;
}

/* 危险按钮 */
QPushButton#danger {
    color: #ff4d4f;
    border-color: #ff4d4f;
}

QPushButton#danger:hover {
    background-color: #fff1f0;
}

/* ==================== 输入框样式 ==================== */
QLineEdit {
    background-color: white;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 14px;
    min-height: 32px;
}

QLineEdit:focus {
    border-color: #1890ff;
    outline: none;
}

QLineEdit:disabled {
    background-color: #f5f5f5;
    color: #bfbfbf;
}

QLineEdit::placeholder {
    color: #bfbfbf;
}

/* ==================== 下拉框样式 ==================== */
QComboBox {
    background-color: white;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 14px;
    min-height: 32px;
    min-width: 100px;
}

QComboBox:focus {
    border-color: #1890ff;
}

QComboBox:disabled {
    background-color: #f5f5f5;
    color: #bfbfbf;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #666;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: white;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    selection-background-color: #e6f7ff;
    selection-color: #1890ff;
    outline: none;
}

/* ==================== 表格样式 ==================== */
QTableWidget {
    background-color: white;
    border: 1px solid #e8e8e8;
    border-radius: 4px;
    gridline-color: #f0f0f0;
    font-size: 13px;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #f0f0f0;
}

QTableWidget::item:selected {
    background-color: #e6f7ff;
    color: #1890ff;
}

QTableWidget::item:hover {
    background-color: #f5f5f5;
}

QHeaderView::section {
    background-color: #fafafa;
    color: #333;
    padding: 10px 8px;
    border: none;
    border-bottom: 1px solid #e8e8e8;
    font-weight: bold;
    font-size: 13px;
}

QHeaderView::section:hover {
    background-color: #f0f0f0;
}

/* ==================== 列表样式 ==================== */
QListWidget {
    background-color: white;
    border: 1px solid #e8e8e8;
    border-radius: 4px;
    font-size: 14px;
    outline: none;
}

QListWidget::item {
    padding: 10px 15px;
    border-bottom: 1px solid #f0f0f0;
    color: #333;
}

QListWidget::item:selected {
    background-color: #e6f7ff;
    color: #1890ff;
}

QListWidget::item:hover {
    background-color: #f5f5f5;
}

/* ==================== 树形控件样式 ==================== */
QTreeWidget {
    background-color: white;
    border: 1px solid #e8e8e8;
    border-radius: 4px;
    font-size: 13px;
    outline: none;
}

QTreeWidget::item {
    padding: 6px 8px;
    border-radius: 4px;
}

QTreeWidget::item:selected {
    background-color: #e6f7ff;
    color: #1890ff;
}

QTreeWidget::item:hover {
    background-color: #f5f5f5;
}

QTreeWidget::branch {
    background-color: transparent;
}

/* ==================== 文本编辑框样式 ==================== */
QTextEdit {
    background-color: white;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    padding: 10px;
    font-size: 14px;
}

QTextEdit:focus {
    border-color: #1890ff;
}

QTextEdit:disabled {
    background-color: #f5f5f5;
    color: #bfbfbf;
}

/* ==================== 分组框样式 ==================== */
QGroupBox {
    background-color: white;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 20px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 10px;
    color: #333;
}

/* ==================== 标签页样式 ==================== */
QTabWidget::pane {
    border: 1px solid #e8e8e8;
    border-radius: 4px;
    background-color: white;
}

QTabBar::tab {
    background-color: #f5f5f5;
    color: #666;
    padding: 10px 20px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: white;
    color: #1890ff;
    border-bottom: 2px solid #1890ff;
}

QTabBar::tab:hover:!selected {
    background-color: #e6f7ff;
    color: #1890ff;
}

/* ==================== 菜单样式 ==================== */
QMenu {
    background-color: white;
    border: 1px solid #e8e8e8;
    border-radius: 4px;
    padding: 5px;
}

QMenu::item {
    padding: 8px 25px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #e6f7ff;
    color: #1890ff;
}

QMenu::separator {
    height: 1px;
    background-color: #e8e8e8;
    margin: 5px 10px;
}

/* ==================== 对话框样式 ==================== */
QDialog {
    background-color: white;
}

/* ==================== 工具提示样式 ==================== */
QToolTip {
    background-color: rgba(0, 0, 0, 0.8);
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}

/* ==================== 进度条样式 ==================== */
QProgressBar {
    background-color: #f5f5f5;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #1890ff;
    border-radius: 4px;
}

/* ==================== 复选框样式 ==================== */
QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #d9d9d9;
    border-radius: 3px;
    background-color: white;
}

QCheckBox::indicator:checked {
    background-color: #1890ff;
    border-color: #1890ff;
}

QCheckBox::indicator:hover {
    border-color: #1890ff;
}

/* ==================== 单选框样式 ==================== */
QRadioButton {
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #d9d9d9;
    border-radius: 9px;
    background-color: white;
}

QRadioButton::indicator:checked {
    background-color: #1890ff;
    border-color: #1890ff;
}

QRadioButton::indicator:hover {
    border-color: #1890ff;
}

/* ==================== 分割器样式 ==================== */
QSplitter::handle {
    background-color: #e8e8e8;
}

QSplitter::handle:horizontal {
    width: 1px;
}

QSplitter::handle:vertical {
    height: 1px;
}

/* ==================== 消息框样式 ==================== */
QMessageBox {
    background-color: white;
}

QMessageBox QLabel {
    color: #333;
    font-size: 14px;
}
"""

CARD_STYLE = """
background-color: white;
border: 1px solid #e8e8e8;
border-radius: 8px;
padding: 20px;
"""

STAT_CARD_STYLE = """
background-color: white;
border: 1px solid #e8e8e8;
border-radius: 8px;
padding: 15px;
"""

TITLE_STYLE = """
font-size: 24px;
font-weight: bold;
color: #333;
"""

SUBTITLE_STYLE = """
font-size: 16px;
font-weight: bold;
color: #333;
"""

LABEL_STYLE = """
font-size: 14px;
color: #666;
"""

PRIMARY_BTN_STYLE = """
QPushButton {
    background-color: #1890ff;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: bold;
    min-height: 36px;
}
QPushButton:hover {
    background-color: #40a9ff;
}
QPushButton:pressed {
    background-color: #096dd9;
}
"""

DEFAULT_BTN_STYLE = """
QPushButton {
    background-color: white;
    color: #666;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    padding: 10px 20px;
    font-size: 14px;
    min-height: 36px;
}
QPushButton:hover {
    color: #1890ff;
    border-color: #1890ff;
}
"""

DANGER_BTN_STYLE = """
QPushButton {
    background-color: white;
    color: #ff4d4f;
    border: 1px solid #ff4d4f;
    border-radius: 4px;
    padding: 10px 20px;
    font-size: 14px;
    min-height: 36px;
}
QPushButton:hover {
    background-color: #fff1f0;
}
"""

SMALL_BTN_STYLE = """
QPushButton {
    background-color: white;
    color: #666;
    border: 1px solid #d9d9d9;
    border-radius: 3px;
    padding: 5px 12px;
    font-size: 12px;
    min-height: 24px;
}
QPushButton:hover {
    color: #1890ff;
    border-color: #1890ff;
}
"""

SEARCH_INPUT_STYLE = """
QLineEdit {
    padding: 10px 15px;
    border: 2px solid #d9d9d9;
    border-radius: 8px;
    font-size: 14px;
    background-color: white;
}
QLineEdit:focus {
    border-color: #1890ff;
}
"""

TABLE_STYLE = """
QTableWidget {
    background-color: white;
    border: 1px solid #e8e8e8;
    border-radius: 4px;
    gridline-color: #f0f0f0;
    font-size: 13px;
}
QTableWidget::item {
    padding: 10px 8px;
    border-bottom: 1px solid #f0f0f0;
}
QTableWidget::item:selected {
    background-color: #e6f7ff;
    color: #1890ff;
}
QHeaderView::section {
    background-color: #fafafa;
    color: #333;
    padding: 12px 8px;
    border: none;
    border-bottom: 1px solid #e8e8e8;
    font-weight: bold;
    font-size: 13px;
}
"""

PAGINATION_BTN_STYLE = """
QPushButton {
    background-color: white;
    color: #666;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 14px;
    min-width: 40px;
    min-height: 32px;
}
QPushButton:hover {
    color: #1890ff;
    border-color: #1890ff;
}
QPushButton:disabled {
    color: #bfbfbf;
    background-color: #f5f5f5;
    border-color: #e8e8e8;
}
"""

PAGINATION_INFO_STYLE = """
font-size: 14px;
color: #666;
padding: 0 10px;
"""

PAGINATION_COMBO_STYLE = """
QComboBox {
    background-color: white;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 14px;
    min-width: 80px;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox QAbstractItemView {
    background-color: white;
    border: 1px solid #d9d9d9;
    selection-background-color: #e6f7ff;
}
"""

TABLE_ACTION_BTN_PRIMARY = """
QPushButton {
    background-color: #1890ff;
    color: white;
    border: none;
    border-radius: 3px;
    padding: 5px 12px;
    font-size: 12px;
    min-width: 50px;
    max-width: 60px;
    min-height: 26px;
}
QPushButton:hover {
    background-color: #40a9ff;
}
"""

TABLE_ACTION_BTN_DEFAULT = """
QPushButton {
    background-color: white;
    color: #1890ff;
    border: 1px solid #1890ff;
    border-radius: 3px;
    padding: 5px 12px;
    font-size: 12px;
    min-width: 50px;
    max-width: 60px;
    min-height: 26px;
}
QPushButton:hover {
    background-color: #e6f7ff;
}
"""

TABLE_ACTION_BTN_DANGER = """
QPushButton {
    background-color: white;
    color: #ff4d4f;
    border: 1px solid #ff4d4f;
    border-radius: 3px;
    padding: 5px 12px;
    font-size: 12px;
    min-width: 50px;
    max-width: 60px;
    min-height: 26px;
}
QPushButton:hover {
    background-color: #fff1f0;
}
"""

LIST_ITEM_ENHANCED_STYLE = """
QListWidget {
    background-color: white;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    font-size: 14px;
    outline: none;
}
QListWidget::item {
    padding: 12px 15px;
    border-bottom: 1px solid #e8e8e8;
    color: #333;
    background-color: white;
}
QListWidget::item:selected {
    background-color: #e6f7ff;
    color: #1890ff;
    border-left: 3px solid #1890ff;
    padding-left: 12px;
}
QListWidget::item:hover {
    background-color: #f5f5f5;
    border-left: 3px solid #1890ff;
    padding-left: 12px;
}
"""

STAT_CARD_ENHANCED_STYLE = """
QWidget {
    background-color: white;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
}
"""

TAG_WIDGET_STYLE = """
QPushButton {
    background-color: #e6f7ff;
    color: #1890ff;
    border: 1px solid #91d5ff;
    border-radius: 12px;
    padding: 4px 10px;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #bae7ff;
}
"""

TAG_REMOVE_BTN_STYLE = """
QPushButton {
    background-color: transparent;
    color: #1890ff;
    border: none;
    border-radius: 10px;
    padding: 0 6px;
    font-size: 12px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #ff4d4f;
    color: white;
}
"""

TOOLBAR_PRIMARY_BTN = """
QPushButton {
    background-color: #1890ff;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 12px;
    min-height: 28px;
}
QPushButton:hover {
    background-color: #40a9ff;
}
"""

TOOLBAR_DEFAULT_BTN = """
QPushButton {
    background-color: white;
    color: #666;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 12px;
    min-height: 28px;
}
QPushButton:hover {
    color: #1890ff;
    border-color: #1890ff;
}
"""

TOOLBAR_DANGER_BTN = """
QPushButton {
    background-color: white;
    color: #ff4d4f;
    border: 1px solid #ff4d4f;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 12px;
    min-height: 28px;
}
QPushButton:hover {
    background-color: #fff1f0;
}
"""

TOOLBAR_SUCCESS_BTN = """
QPushButton {
    background-color: white;
    color: #52c41a;
    border: 1px solid #52c41a;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 12px;
    min-height: 28px;
}
QPushButton:hover {
    background-color: #f6ffed;
}
"""

SEARCH_BOX_STYLE = """
QLineEdit {
    padding: 8px 12px;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    font-size: 13px;
    background-color: white;
}
QLineEdit:focus {
    border-color: #1890ff;
}
"""

FILTER_COMBO_STYLE = """
QComboBox {
    background-color: white;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 13px;
    min-width: 80px;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox QAbstractItemView {
    background-color: white;
    border: 1px solid #d9d9d9;
    selection-background-color: #e6f7ff;
}
"""

DIALOG_BTN_PRIMARY = """
QPushButton {
    background-color: #1890ff;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 20px;
    font-size: 13px;
    min-width: 80px;
}
QPushButton:hover {
    background-color: #40a9ff;
}
"""

DIALOG_BTN_DEFAULT = """
QPushButton {
    background-color: white;
    color: #666;
    border: 1px solid #d9d9d9;
    border-radius: 4px;
    padding: 8px 20px;
    font-size: 13px;
    min-width: 80px;
}
QPushButton:hover {
    color: #1890ff;
    border-color: #1890ff;
}
"""

STAT_NUMBER_STYLE = """
font-size: 28px;
font-weight: bold;
color: #1890ff;
"""

STAT_LABEL_STYLE = """
font-size: 12px;
color: #666;
"""

SIMILARITY_NUMBER_STYLE = """
font-size: 72px;
font-weight: bold;
color: #1890ff;
"""

SECTION_TITLE_STYLE = """
font-size: 14px;
font-weight: bold;
color: #333;
margin-bottom: 10px;
"""

HINT_LABEL_STYLE = """
font-size: 12px;
color: #999;
"""

INFO_BAR_STYLE = """
background-color: #fafafa;
border-bottom: 1px solid #e8e8e8;
padding: 10px 15px;
"""
