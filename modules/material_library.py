import os
from pathlib import Path

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QComboBox, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView,
                             QMenu, QAction, QMessageBox, QFileDialog,
                             QProgressDialog, QDialog, QFormLayout, QTextEdit,
                             QDialogButtonBox, QGroupBox, QListWidget, QListWidgetItem,
                             QSplitter, QFrame, QCheckBox, QSpinBox, QTreeWidget,
                             QTreeWidgetItem, QAbstractItemView, QToolButton)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt5.QtGui import QColor, QFont


class TagWidget(QWidget):
    """带删除按钮的标签组件"""
    
    remove_clicked = pyqtSignal(int)  # 删除信号，传递tag_id
    
    def __init__(self, tag_id, tag_name, parent=None):
        super().__init__(parent)
        self.tag_id = tag_id
        self.tag_name = tag_name
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标签名称按钮
        self.tag_btn = QPushButton(self.tag_name)
        self.tag_btn.setStyleSheet(TAG_WIDGET_STYLE)
        layout.addWidget(self.tag_btn)
        
        # 删除按钮（×）
        self.remove_btn = QPushButton("×")
        self.remove_btn.setFixedSize(20, 24)
        self.remove_btn.setStyleSheet(TAG_REMOVE_BTN_STYLE)
        self.remove_btn.setToolTip("删除此标签")
        self.remove_btn.clicked.connect(self.on_remove_clicked)
        layout.addWidget(self.remove_btn)
        
        self.setFixedHeight(26)
    
    def on_remove_clicked(self):
        """删除按钮点击"""
        self.remove_clicked.emit(self.tag_id)

from core.database import db
from core.archiver import DocumentImporter, ArchiveManager
from core.styles import (PAGINATION_BTN_STYLE, PAGINATION_INFO_STYLE, PAGINATION_COMBO_STYLE,
                          TABLE_ACTION_BTN_PRIMARY, TABLE_ACTION_BTN_DEFAULT, 
                          TABLE_ACTION_BTN_DANGER, TOOLBAR_PRIMARY_BTN, 
                          TOOLBAR_DEFAULT_BTN, TOOLBAR_DANGER_BTN, TOOLBAR_SUCCESS_BTN,
                          SEARCH_BOX_STYLE, FILTER_COMBO_STYLE, DIALOG_BTN_PRIMARY,
                          DIALOG_BTN_DEFAULT, TAG_WIDGET_STYLE, TAG_REMOVE_BTN_STYLE)


class ImportThread(QThread):
    """导入线程"""
    progress = pyqtSignal(int, int, str)
    finished_signal = pyqtSignal(dict)
    
    def __init__(self, folder_path, recursive=True, auto_archive=True):
        super().__init__()
        self.folder_path = folder_path
        self.recursive = recursive
        self.auto_archive = auto_archive
        self.importer = DocumentImporter()
    
    def run(self):
        result = self.importer.import_folder(
            self.folder_path,
            recursive=self.recursive,
            auto_archive=self.auto_archive,
            progress_callback=lambda c, t, n: self.progress.emit(c, t, n)
        )
        self.finished_signal.emit(result)


class DocumentPreviewDialog(QDialog):
    """文档预览对话框"""
    
    def __init__(self, doc_id, parent=None):
        super().__init__(parent)
        self.doc_id = doc_id
        self.doc = db.get_document(doc_id)
        self.setWindowTitle(self.doc['title'] or '文档预览')
        self.setMinimumSize(1000, 800)
        # 去掉问号按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setup_ui()
        self.check_favorite_status()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 顶部工具栏
        toolbar = QWidget()
        toolbar.setStyleSheet("background-color: #f5f5f5; border-bottom: 1px solid #e8e8e8;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(15, 10, 15, 10)
        
        # 标题（去掉返回按钮后居中）
        title_label = QLabel(self.doc['title'] or '未命名')
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        title_label.setAlignment(Qt.AlignCenter)
        toolbar_layout.addWidget(title_label, 1)
        
        # 右侧按钮
        right_layout = QHBoxLayout()
        
        # 收藏按钮
        self.star_btn = QPushButton("☆ 收藏")
        self.star_btn.setCheckable(True)
        self.star_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 6px 16px;
            }
            QPushButton:checked {
                background-color: #fff7e6;
                border-color: #ffa940;
                color: #ffa940;
            }
        """)
        self.star_btn.clicked.connect(self.toggle_favorite)
        right_layout.addWidget(self.star_btn)
        
        # 复制全文按钮
        copy_btn = QPushButton("📋 复制全文")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 6px 16px;
            }
        """)
        copy_btn.clicked.connect(self.copy_full_text)
        right_layout.addWidget(copy_btn)
        
        toolbar_layout.addLayout(right_layout)
        layout.addWidget(toolbar)
        
        # 文档信息栏
        info_bar = QWidget()
        info_bar.setStyleSheet("background-color: #fafafa; border-bottom: 1px solid #e8e8e8; padding: 10px 15px;")
        info_layout = QHBoxLayout(info_bar)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        info_text = f"文件名: {Path(self.doc['file_path']).name}    类型: {self.doc['file_type'] or '-'}    字数: {len(self.doc['content_text'] or '')}"
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #666; font-size: 13px;")
        info_layout.addWidget(info_label)
        
        info_layout.addStretch()
        
        hint_label = QLabel("选中文字可添加到金句库")
        hint_label.setStyleSheet("color: #999; font-size: 12px;")
        info_layout.addWidget(hint_label)
        
        layout.addWidget(info_bar)
        
        # 文档内容
        self.content_edit = QTextEdit()
        self.content_edit.setReadOnly(True)
        self.content_edit.setText(self.doc['content_text'] or '无内容')
        self.content_edit.setStyleSheet("""
            QTextEdit {
                border: none;
                padding: 20px;
                font-size: 14px;
                line-height: 1.8;
            }
        """)
        self.content_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.content_edit.customContextMenuRequested.connect(self.on_text_context_menu)
        layout.addWidget(self.content_edit)
    
    def check_favorite_status(self):
        """检查收藏状态"""
        favorites = db.get_favorites()
        for fav in favorites:
            if fav['document_id'] == self.doc_id:
                self.star_btn.setChecked(True)
                self.star_btn.setText("★ 已收藏")
                break
    
    def toggle_favorite(self):
        """切换收藏状态"""
        if self.star_btn.isChecked():
            db.add_favorite(self.doc_id)
            self.star_btn.setText("★ 已收藏")
            QMessageBox.information(self, "成功", "已添加到收藏")
        else:
            # 取消收藏
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM favorites WHERE document_id = ?', (self.doc_id,))
            conn.commit()
            conn.close()
            self.star_btn.setText("☆ 收藏")
            QMessageBox.information(self, "成功", "已取消收藏")
    
    def copy_full_text(self):
        """复制全文"""
        from PyQt5.QtWidgets import QApplication
        QApplication.clipboard().setText(self.doc['content_text'] or '')
        QMessageBox.information(self, "成功", "全文已复制到剪贴板")
    
    def on_text_context_menu(self, position):
        """文本右键菜单"""
        menu = QMenu(self)
        
        # 获取选中的文本
        cursor = self.content_edit.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            add_quote_action = QAction("收录金句", self)
            add_quote_action.triggered.connect(lambda: self.add_to_quotes(selected_text))
            menu.addAction(add_quote_action)
            menu.addSeparator()
        
        copy_action = QAction("复制", self)
        copy_action.triggered.connect(self.content_edit.copy)
        menu.addAction(copy_action)
        
        select_all_action = QAction("全选", self)
        select_all_action.triggered.connect(self.content_edit.selectAll)
        menu.addAction(select_all_action)
        
        menu.exec_(self.content_edit.viewport().mapToGlobal(position))
    
    def add_to_quotes(self, text):
        """添加到金句库"""
        from modules.favorites import QuoteEditDialog
        
        dialog = QuoteEditDialog(parent=self)
        dialog.content_edit.setText(text)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data['content'].strip():
                db.add_quote(
                    content=data['content'],
                    source_document_id=self.doc_id,
                    category=data['category'] or None,
                    notes=data['notes'] or None
                )
                QMessageBox.information(self, "成功", "已添加到金句库")


class DocumentEditDialog(QDialog):
    """文档编辑对话框"""
    
    def __init__(self, document_id=None, parent=None):
        super().__init__(parent)
        self.document_id = document_id
        self.selected_tag_ids = set()
        self.setWindowTitle("编辑文档信息" if document_id else "新建文档")
        self.setMinimumWidth(500)
        self.setup_ui()
        
        if document_id:
            self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        from PyQt5.QtWidgets import QFormLayout
        form_layout = QFormLayout()
        
        self.title_edit = QLineEdit()
        form_layout.addRow("标题:", self.title_edit)
        
        self.author_edit = QLineEdit()
        form_layout.addRow("作者:", self.author_edit)
        
        self.year_spin = QSpinBox()
        self.year_spin.setRange(1990, 2030)
        self.year_spin.setValue(2024)
        form_layout.addRow("年份:", self.year_spin)
        
        self.category_combo = QComboBox()
        self.load_categories()
        form_layout.addRow("分类:", self.category_combo)
        
        # 标签选择 - 使用流式布局
        self.tags_group = QGroupBox("标签")
        tags_main_layout = QVBoxLayout(self.tags_group)
        tags_main_layout.setSpacing(10)
        tags_main_layout.setContentsMargins(15, 20, 15, 15)
        
        # 已选标签显示区域 - 使用流式布局
        tags_container = QWidget()
        tags_container.setMinimumHeight(60)
        self.tags_flow_layout = QHBoxLayout(tags_container)
        self.tags_flow_layout.setContentsMargins(0, 0, 0, 0)
        self.tags_flow_layout.setSpacing(6)
        self.tags_flow_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        self.selected_tags_widget = QWidget()
        self.selected_tags_layout = QHBoxLayout(self.selected_tags_widget)
        self.selected_tags_layout.setContentsMargins(0, 0, 0, 0)
        self.selected_tags_layout.setSpacing(6)
        self.selected_tags_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.selected_tags_layout.addStretch()
        
        self.tags_flow_layout.addWidget(self.selected_tags_widget)
        self.tags_flow_layout.addStretch()
        
        tags_main_layout.addWidget(tags_container)
        
        # 添加标签按钮 - 独立一行
        self.add_tag_btn = QPushButton("➕ 添加标签")
        self.add_tag_btn.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 12px;
                min-height: 28px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
        """)
        self.add_tag_btn.clicked.connect(self.add_new_tag)
        
        add_tag_layout = QHBoxLayout()
        add_tag_layout.addWidget(self.add_tag_btn)
        add_tag_layout.addStretch()
        tags_main_layout.addLayout(add_tag_layout)
        
        form_layout.addRow(self.tags_group)
        
        self.source_edit = QLineEdit()
        form_layout.addRow("来源:", self.source_edit)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        form_layout.addRow("备注:", self.notes_edit)
        
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.all_tags = []
        self.load_tags()
    
    def load_categories(self):
        categories = db.get_categories()
        for cat in categories:
            self.category_combo.addItem(cat['name'], cat['id'])
    
    def load_tags(self):
        """加载标签列表"""
        self.all_tags = db.get_tags()
        self.update_selected_tags_display()
    
    def update_selected_tags_display(self):
        """更新已选标签显示"""
        # 清空现有显示
        while self.selected_tags_layout.count() > 1:  # 保留stretch
            item = self.selected_tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加已选标签组件
        for tag_id in self.selected_tag_ids:
            tag = next((t for t in self.all_tags if t['id'] == tag_id), None)
            if tag:
                tag_widget = TagWidget(tag_id, tag['name'], self)
                tag_widget.remove_clicked.connect(self.remove_tag)
                self.selected_tags_layout.insertWidget(self.selected_tags_layout.count() - 1, tag_widget)
        
        # 如果没有标签，显示提示
        if not self.selected_tag_ids:
            label = QLabel("暂无标签，点击'添加标签'按钮添加")
            label.setStyleSheet("color: #999; font-size: 12px;")
            self.selected_tags_layout.insertWidget(0, label)
    
    def add_new_tag(self):
        """添加新标签"""
        from PyQt5.QtWidgets import QInputDialog
        
        # 获取所有现有标签名称
        existing_tags = [tag['name'] for tag in self.all_tags]
        
        tag_name, ok = QInputDialog.getText(self, "添加标签", "请输入标签名称:")
        if ok and tag_name:
            # 检查是否已存在
            if tag_name in existing_tags:
                # 如果已存在，直接选中
                existing_tag = next((t for t in self.all_tags if t['name'] == tag_name), None)
                if existing_tag:
                    self.selected_tag_ids.add(existing_tag['id'])
                    self.update_selected_tags_display()
            else:
                # 创建新标签
                tag_id = db.add_tag(tag_name)
                self.load_tags()
                self.selected_tag_ids.add(tag_id)
                self.update_selected_tags_display()
            QMessageBox.information(self, "成功", "标签添加成功")
    
    def delete_tag(self):
        """删除标签"""
        if not self.all_tags:
            QMessageBox.information(self, "提示", "暂无标签可删除")
            return
        
        from PyQt5.QtWidgets import QInputDialog
        
        # 获取所有标签名称
        tag_names = [tag['name'] for tag in self.all_tags]
        
        tag_name, ok = QInputDialog.getItem(
            self, 
            "删除标签", 
            "选择要删除的标签:", 
            tag_names,
            editable=False
        )
        
        if ok and tag_name:
            reply = QMessageBox.question(
                self,
                "确认删除",
                f"确定要删除标签 \"{tag_name}\" 吗？\n此操作将从所有文档中移除该标签。",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                tag = next((t for t in self.all_tags if t['name'] == tag_name), None)
                if tag:
                    try:
                        conn = db.get_connection()
                        cursor = conn.cursor()
                        # 删除文档标签关联
                        cursor.execute('DELETE FROM document_tags WHERE tag_id = ?', (tag['id'],))
                        # 删除标签
                        cursor.execute('DELETE FROM tags WHERE id = ?', (tag['id'],))
                        conn.commit()
                        conn.close()
                        
                        # 从已选标签中移除
                        self.selected_tag_ids.discard(tag['id'])
                        self.load_tags()
                        QMessageBox.information(self, "成功", "标签已删除")
                    except Exception as e:
                        QMessageBox.warning(self, "失败", f"删除失败: {e}")
    
    def remove_tag(self, tag_id):
        """从当前文档移除标签"""
        self.selected_tag_ids.discard(tag_id)
        self.update_selected_tags_display()
    
    def load_data(self):
        doc = db.get_document(self.document_id)
        if doc:
            self.title_edit.setText(doc['title'] or '')
            self.author_edit.setText(doc['author'] or '')
            if doc['year']:
                self.year_spin.setValue(doc['year'])
            
            index = self.category_combo.findData(doc['category_id'])
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            
            self.source_edit.setText(doc['source'] or '')
            self.notes_edit.setText(doc['notes'] or '')
            
            # 加载已选标签
            doc_tags = db.get_document_tags(self.document_id)
            self.selected_tag_ids = {tag['id'] for tag in doc_tags}
            
            # 更新标签显示
            self.update_selected_tags_display()
    
    def get_data(self):
        return {
            'title': self.title_edit.text(),
            'author': self.author_edit.text(),
            'year': self.year_spin.value(),
            'category_id': self.category_combo.currentData(),
            'source': self.source_edit.text(),
            'notes': self.notes_edit.toPlainText()
        }
    
    def get_selected_tags(self):
        """获取选中的标签ID"""
        return list(self.selected_tag_ids)


class MaterialLibraryWidget(QWidget):
    """材料库主界面 - 带文件夹树"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.archive_manager = ArchiveManager()
        self.current_folder = None
        self.selected_docs = set()
        self.all_docs = []
        self.setup_ui()
        self.load_data()
        self.load_column_widths()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background-color: #e8e8e8; }")
        
        # 左侧文件夹树 - 宽度更窄，减小右边距
        left_panel = QWidget()
        left_panel.setFixedWidth(150)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 10, 0, 10)
        left_layout.setSpacing(10)
        
        # 文件夹标题
        folder_title = QLabel("📁 文件夹")
        folder_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #333;")
        left_layout.addWidget(folder_title)
        
        # 文件夹树
        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderHidden(True)
        self.folder_tree.setStyleSheet("""
            QTreeWidget {
                background-color: white;
                border: 1px solid #e8e8e8;
                border-radius: 4px;
            }
            QTreeWidget::item {
                padding: 4px;
                border-radius: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #e6f7ff;
                color: #1890ff;
            }
            QTreeWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        self.folder_tree.itemClicked.connect(self.on_folder_selected)
        self.folder_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.folder_tree.customContextMenuRequested.connect(self.on_folder_context_menu)
        left_layout.addWidget(self.folder_tree)
        
        # 文件夹操作按钮
        folder_btn_layout = QHBoxLayout()
        
        self.add_folder_btn = QPushButton("➕ 新建")
        self.add_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 8px;
                font-size: 11px;
            }
        """)
        self.add_folder_btn.clicked.connect(self.add_folder)
        folder_btn_layout.addWidget(self.add_folder_btn)
        
        self.del_folder_btn = QPushButton("🗑️ 删除")
        self.del_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #ff4d4f;
                border: 1px solid #ff4d4f;
                border-radius: 4px;
                padding: 5px 8px;
                font-size: 11px;
            }
        """)
        self.del_folder_btn.clicked.connect(self.delete_folder)
        folder_btn_layout.addWidget(self.del_folder_btn)
        
        left_layout.addLayout(folder_btn_layout)
        
        splitter.addWidget(left_panel)
        
        # 右侧内容区 - 减小左边距，让左右区域更紧凑
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 10, 10, 10)
        right_layout.setSpacing(10)
        
        # 标题
        title = QLabel("材料库")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #333;
        """)
        right_layout.addWidget(title)
        
        # 搜索和筛选栏
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(8)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索文件名...")
        self.search_edit.setStyleSheet(SEARCH_BOX_STYLE)
        self.search_edit.returnPressed.connect(self.on_search)
        filter_layout.addWidget(self.search_edit, 1)
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("全部分类", None)
        self.category_filter.setStyleSheet(FILTER_COMBO_STYLE)
        filter_layout.addWidget(self.category_filter, 1)
        
        self.year_filter = QComboBox()
        self.year_filter.addItem("全部年份", None)
        for year in range(2024, 1989, -1):
            self.year_filter.addItem(str(year), year)
        self.year_filter.setStyleSheet(FILTER_COMBO_STYLE)
        filter_layout.addWidget(self.year_filter, 1)
        
        self.search_btn = QPushButton("🔍 搜索")
        self.search_btn.setStyleSheet(TOOLBAR_PRIMARY_BTN)
        self.search_btn.clicked.connect(self.on_search)
        filter_layout.addWidget(self.search_btn)
        
        self.reset_btn = QPushButton("重置")
        self.reset_btn.setStyleSheet(TOOLBAR_DEFAULT_BTN)
        self.reset_btn.clicked.connect(self.on_reset)
        filter_layout.addWidget(self.reset_btn)
        
        right_layout.addWidget(filter_widget)
        
        # 工具栏
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.import_btn = QPushButton("📥 导入文件")
        self.import_btn.setStyleSheet(TOOLBAR_PRIMARY_BTN)
        self.import_btn.clicked.connect(self.on_import_file)
        toolbar_layout.addWidget(self.import_btn)
        
        self.import_folder_btn = QPushButton("📁 导入文件夹")
        self.import_folder_btn.setStyleSheet(TOOLBAR_DEFAULT_BTN)
        self.import_folder_btn.clicked.connect(self.on_import_folder)
        toolbar_layout.addWidget(self.import_folder_btn)
        
        self.move_btn = QPushButton("📂 移动到")
        self.move_btn.setStyleSheet(TOOLBAR_DEFAULT_BTN)
        self.move_btn.clicked.connect(self.on_move_selected)
        toolbar_layout.addWidget(self.move_btn)
        
        self.delete_btn = QPushButton("🗑️ 删除选中")
        self.delete_btn.setStyleSheet(TOOLBAR_DANGER_BTN)
        self.delete_btn.clicked.connect(self.on_delete_selected)
        toolbar_layout.addWidget(self.delete_btn)
        
        toolbar_layout.addStretch()
        
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.setStyleSheet(TOOLBAR_SUCCESS_BTN)
        self.refresh_btn.clicked.connect(self.on_refresh)
        toolbar_layout.addWidget(self.refresh_btn)
        
        right_layout.addWidget(toolbar)
        
        # 文档表格 - 增加标签列
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "", "标题", "类型", "年份", "作者", "分类", "标签", "编辑", "移动", "删除"
        ])
        
        # 隐藏行号
        self.table.verticalHeader().setVisible(False)
        
        # 设置列宽模式 - 所有列都可以调整
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(9, QHeaderView.Fixed)
        
        # 设置初始列宽 - 复选框列缩小
        self.table.setColumnWidth(0, 35)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 60)
        self.table.setColumnWidth(3, 60)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 120)
        self.table.setColumnWidth(7, 60)
        self.table.setColumnWidth(8, 60)
        self.table.setColumnWidth(9, 60)
        
        # 在表头第一列添加全选复选框
        self.header_checkbox = QCheckBox()
        self.header_checkbox.stateChanged.connect(self.on_header_checkbox_changed)
        self.table.horizontalHeader().setMinimumHeight(30)
        
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #fafafa;
                border: 1px solid #e8e8e8;
                padding: 6px;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setAlternatingRowColors(True)
        self.table.cellClicked.connect(self.on_cell_clicked)
        self.table.horizontalHeader().sectionResized.connect(self.save_column_widths)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e8e8e8;
            }
            QTableWidget::item:selected {
                background-color: #e6f7ff;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        
        # 设置行高
        self.table.verticalHeader().setDefaultSectionSize(40)
        
        right_layout.addWidget(self.table)
        
        # 分页组件
        pagination_widget = QWidget()
        pagination_layout = QHBoxLayout(pagination_widget)
        pagination_layout.setContentsMargins(0, 5, 0, 0)
        pagination_layout.setSpacing(10)
        
        # 共X条
        self.pagination_info = QLabel("共 0 条")
        self.pagination_info.setStyleSheet(PAGINATION_INFO_STYLE)
        pagination_layout.addWidget(self.pagination_info)
        
        pagination_layout.addStretch()
        
        # 每页条数选择
        page_size_label = QLabel("每页")
        page_size_label.setStyleSheet(PAGINATION_INFO_STYLE)
        pagination_layout.addWidget(page_size_label)
        
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["10", "20", "50", "100"])
        self.page_size_combo.setCurrentText("20")
        self.page_size_combo.setFixedWidth(70)
        self.page_size_combo.setStyleSheet(PAGINATION_COMBO_STYLE)
        self.page_size_combo.currentTextChanged.connect(self.on_page_size_changed)
        pagination_layout.addWidget(self.page_size_combo)
        
        page_size_suffix = QLabel("条")
        page_size_suffix.setStyleSheet(PAGINATION_INFO_STYLE)
        pagination_layout.addWidget(page_size_suffix)
        
        # 分页按钮
        self.first_page_btn = QPushButton("<<")
        self.first_page_btn.setFixedWidth(40)
        self.first_page_btn.setStyleSheet(PAGINATION_BTN_STYLE)
        self.first_page_btn.clicked.connect(self.go_first_page)
        pagination_layout.addWidget(self.first_page_btn)
        
        self.prev_page_btn = QPushButton("<")
        self.prev_page_btn.setFixedWidth(35)
        self.prev_page_btn.setStyleSheet(PAGINATION_BTN_STYLE)
        self.prev_page_btn.clicked.connect(self.go_prev_page)
        pagination_layout.addWidget(self.prev_page_btn)
        
        # 页码显示
        self.page_label = QLabel("1 / 1")
        self.page_label.setStyleSheet(PAGINATION_INFO_STYLE)
        pagination_layout.addWidget(self.page_label)
        
        self.next_page_btn = QPushButton(">")
        self.next_page_btn.setFixedWidth(35)
        self.next_page_btn.setStyleSheet(PAGINATION_BTN_STYLE)
        self.next_page_btn.clicked.connect(self.go_next_page)
        pagination_layout.addWidget(self.next_page_btn)
        
        self.last_page_btn = QPushButton(">>")
        self.last_page_btn.setFixedWidth(40)
        self.last_page_btn.setStyleSheet(PAGINATION_BTN_STYLE)
        self.last_page_btn.clicked.connect(self.go_last_page)
        pagination_layout.addWidget(self.last_page_btn)
        
        right_layout.addWidget(pagination_widget)
        
        # 初始化分页参数
        self.current_page = 1
        self.page_size = 20
        self.total_pages = 1
        
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([150, 850])
        
        layout.addWidget(splitter)
        
        # 将全选复选框放置到表头第一列（缩小并居中）
        self.header_checkbox.setParent(self.table)
        self.header_checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
        """)
        self.header_checkbox.move(10, 8)
        self.header_checkbox.show()
    
    def resizeEvent(self, event):
        """窗口大小改变时调整全选复选框位置"""
        super().resizeEvent(event)
        if hasattr(self, 'header_checkbox'):
            self.header_checkbox.move(10, 8)
    
    def on_header_checkbox_changed(self, state):
        """全选复选框状态变化"""
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(state == Qt.Checked)
    
    def on_page_size_changed(self, text):
        """每页条数改变"""
        self.page_size = int(text)
        self.current_page = 1
        self.load_documents(self.all_docs)
    
    def go_first_page(self):
        """首页"""
        self.current_page = 1
        self.load_documents(self.all_docs)
    
    def go_prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_documents(self.all_docs)
    
    def go_next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_documents(self.all_docs)
    
    def go_last_page(self):
        """末页"""
        self.current_page = self.total_pages
        self.load_documents(self.all_docs)
    
    def update_pagination(self):
        """更新分页显示"""
        total = len(self.all_docs)
        self.total_pages = max(1, (total + self.page_size - 1) // self.page_size)
        
        # 确保当前页在有效范围内
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        
        # 更新显示
        self.pagination_info.setText(f"共 {total} 条")
        self.page_label.setText(f"{self.current_page} / {self.total_pages}")
        
        # 更新按钮状态
        self.first_page_btn.setEnabled(self.current_page > 1)
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < self.total_pages)
        self.last_page_btn.setEnabled(self.current_page < self.total_pages)
    
    def load_column_widths(self):
        """加载列宽设置"""
        settings = QSettings('DocumentManager', 'MaterialLibrary')
        for col in range(self.table.columnCount()):
            width = settings.value(f'column_width_{col}', None)
            if width:
                self.table.setColumnWidth(col, int(width))
    
    def save_column_widths(self):
        """保存列宽设置"""
        settings = QSettings('DocumentManager', 'MaterialLibrary')
        for col in range(self.table.columnCount()):
            settings.setValue(f'column_width_{col}', self.table.columnWidth(col))
    
    def load_data(self):
        """加载数据"""
        self.load_folder_tree()
        
        self.category_filter.clear()
        self.category_filter.addItem("全部分类", None)
        categories = db.get_categories()
        for cat in categories:
            self.category_filter.addItem(cat['name'], cat['id'])
        
        self.on_search()
    
    def load_folder_tree(self):
        """加载文件夹树 - 从数据库加载，首次加载时初始化默认文件夹"""
        self.folder_tree.clear()
        
        # 默认文件夹列表
        default_folders = [
            "领导文稿",
            "政策法规", 
            "按文种",
            "按年度",
            "通知",
            "方案",
            "报告",
            "讲话稿",
            "工作总结",
            "交流研讨",
            "未分类"
        ]
        
        # 检查数据库中是否有文件夹
        folders = db.get_folders()
        
        if not folders:
            # 首次运行，初始化默认文件夹
            for i, folder_name in enumerate(default_folders):
                db.add_folder(folder_name, sort_order=i)
            folders = db.get_folders()
        
        # 构建文件夹树
        for folder in folders:
            item = QTreeWidgetItem(self.folder_tree)
            # 获取该文件夹下的文档数量
            doc_count = self.get_folder_document_count(folder['name'])
            item.setText(0, f"{folder['name']} ({doc_count})")
            item.setData(0, Qt.UserRole, {'id': folder['id'], 'name': folder['name'], 'level': 1})
            item.setFlags(item.flags() | Qt.ItemIsDropEnabled)
            
            # 加载子文件夹
            self._load_sub_folders(item, folder['id'])
        
        self.folder_tree.expandAll()
    
    def get_folder_document_count(self, folder_path):
        """获取文件夹下的文档数量"""
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM documents WHERE folder_path = ?', (folder_path,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def _load_sub_folders(self, parent_item, parent_id):
        """递归加载子文件夹"""
        sub_folders = db.get_folders(parent_id)
        for folder in sub_folders:
            item = QTreeWidgetItem(parent_item)
            parent_path = parent_item.data(0, Qt.UserRole)['name']
            full_path = f"{parent_path}/{folder['name']}"
            # 获取该文件夹下的文档数量
            doc_count = self.get_folder_document_count(full_path)
            item.setText(0, f"{folder['name']} ({doc_count})")
            item.setData(0, Qt.UserRole, {'id': folder['id'], 'name': full_path, 'level': 2})
            item.setFlags(item.flags() | Qt.ItemIsDropEnabled)
            
            # 递归加载更深层子文件夹
            self._load_sub_folders(item, folder['id'])
    
    def on_folder_selected(self, item):
        """文件夹选中"""
        folder_data = item.data(0, Qt.UserRole)
        if folder_data:
            self.current_folder = folder_data['name']
            self.on_search()
    
    def on_folder_context_menu(self, position):
        """文件夹右键菜单"""
        item = self.folder_tree.itemAt(position)
        menu = QMenu(self)
        
        add_action = QAction("新建子文件夹", self)
        add_action.triggered.connect(lambda: self.add_sub_folder(item))
        menu.addAction(add_action)
        
        if item:
            delete_action = QAction("删除文件夹", self)
            delete_action.triggered.connect(self.delete_folder)
            menu.addAction(delete_action)
        
        menu.exec_(self.folder_tree.viewport().mapToGlobal(position))
    
    def add_folder(self):
        """添加一级文件夹"""
        from PyQt5.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "新建文件夹", "请输入文件夹名称:")
        if ok and name:
            # 保存到数据库
            folder_id = db.add_folder(name)
            # 添加到树
            item = QTreeWidgetItem(self.folder_tree)
            item.setText(0, name)
            item.setData(0, Qt.UserRole, {'id': folder_id, 'name': name, 'level': 1})
            item.setFlags(item.flags() | Qt.ItemIsDropEnabled)
    
    def add_sub_folder(self, parent_item):
        """添加子文件夹"""
        if not parent_item:
            return
        
        from PyQt5.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "新建子文件夹", "请输入子文件夹名称:")
        if ok and name:
            parent_data = parent_item.data(0, Qt.UserRole)
            parent_id = parent_data.get('id')
            parent_path = parent_data['name']
            
            # 保存到数据库
            folder_id = db.add_folder(name, parent_id=parent_id)
            
            # 添加到树
            sub_item = QTreeWidgetItem(parent_item)
            sub_item.setText(0, name)
            sub_item.setData(0, Qt.UserRole, {'id': folder_id, 'name': f"{parent_path}/{name}", 'level': 2})
            sub_item.setFlags(sub_item.flags() | Qt.ItemIsDropEnabled)
            parent_item.setExpanded(True)
    
    def delete_folder(self):
        """删除文件夹"""
        item = self.folder_tree.currentItem()
        if not item:
            QMessageBox.warning(self, "提示", "请先选择要删除的文件夹")
            return
        
        folder_data = item.data(0, Qt.UserRole)
        folder_name = item.text(0)
        
        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除文件夹 \"{folder_name}\" 吗？\n子文件夹也会被删除。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 从数据库删除
            folder_id = folder_data.get('id')
            if folder_id:
                db.delete_folder(folder_id)
            
            # 从树中移除
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                index = self.folder_tree.indexOfTopLevelItem(item)
                self.folder_tree.takeTopLevelItem(index)
    
    def load_documents(self, documents):
        """加载文档到表格（支持分页）"""
        self.all_docs = documents
        self.selected_docs.clear()
        
        if hasattr(self, 'header_checkbox'):
            self.header_checkbox.setChecked(False)
        
        # 更新分页信息
        self.update_pagination()
        
        # 计算当前页的数据
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        page_docs = documents[start_idx:end_idx]
        
        self.table.setRowCount(len(page_docs))
        
        categories = {cat['id']: cat['name'] for cat in db.get_categories()}
        
        for i, doc in enumerate(page_docs):
            # 复选框（缩小）
            checkbox = QCheckBox()
            checkbox.setChecked(doc['id'] in self.selected_docs)
            checkbox.stateChanged.connect(lambda state, did=doc['id']: self.on_checkbox_changed(did, state))
            checkbox.setStyleSheet("""
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
            """)
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(i, 0, checkbox_widget)
            
            # 标题
            title_item = QTableWidgetItem(doc['title'] or '未命名')
            title_item.setData(Qt.UserRole, doc['id'])
            title_item.setForeground(QColor("#1890ff"))
            self.table.setItem(i, 1, title_item)
            
            # 类型
            file_type = (doc['file_type'] or '未知').upper()
            type_item = QTableWidgetItem(file_type)
            type_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 2, type_item)
            
            # 年份
            year_text = str(doc['year']) if doc['year'] else '-'
            year_item = QTableWidgetItem(year_text)
            year_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 3, year_item)
            
            # 作者
            author_item = QTableWidgetItem(doc['author'] or '-')
            self.table.setItem(i, 4, author_item)
            
            # 分类
            category_name = categories.get(doc['category_id'], '未分类')
            category_item = QTableWidgetItem(category_name)
            category_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 5, category_item)
            
            # 标签
            doc_tags = db.get_document_tags(doc['id'])
            tag_names = ', '.join([tag['name'] for tag in doc_tags])
            tag_item = QTableWidgetItem(tag_names)
            self.table.setItem(i, 6, tag_item)
            
            # 编辑按钮
            edit_btn = QPushButton("编辑")
            edit_btn.setStyleSheet(TABLE_ACTION_BTN_PRIMARY)
            edit_btn.clicked.connect(lambda checked, did=doc['id']: self.edit_document(did))
            self.table.setCellWidget(i, 7, edit_btn)
            
            # 移动按钮
            move_btn = QPushButton("移动")
            move_btn.setStyleSheet(TABLE_ACTION_BTN_DEFAULT)
            move_btn.clicked.connect(lambda checked, did=doc['id']: self.move_document(did))
            self.table.setCellWidget(i, 8, move_btn)
            
            # 删除按钮
            delete_btn = QPushButton("删除")
            delete_btn.setStyleSheet(TABLE_ACTION_BTN_DANGER)
            delete_btn.clicked.connect(lambda checked, did=doc['id']: self.delete_document(did))
            self.table.setCellWidget(i, 9, delete_btn)
    
    def on_checkbox_changed(self, doc_id, state):
        """复选框状态变化"""
        if state == Qt.Checked:
            self.selected_docs.add(doc_id)
        else:
            self.selected_docs.discard(doc_id)
            if hasattr(self, 'header_checkbox') and self.header_checkbox.isChecked():
                self.header_checkbox.setChecked(False)
    
    def on_cell_clicked(self, row, column):
        """单元格点击"""
        if column == 1:
            doc_id = self.table.item(row, 1).data(Qt.UserRole)
            self.preview_document(doc_id)
    
    def preview_document(self, doc_id):
        """预览文档"""
        dialog = DocumentPreviewDialog(doc_id, self)
        dialog.exec_()
    
    def edit_document(self, doc_id):
        """编辑文档"""
        dialog = DocumentEditDialog(doc_id, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            db.update_document(doc_id, **data)
            
            # 更新标签 - 使用同一个连接
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM document_tags WHERE document_id = ?', (doc_id,))
            selected_tags = dialog.get_selected_tags()
            for tag_id in selected_tags:
                cursor.execute('INSERT INTO document_tags (document_id, tag_id) VALUES (?, ?)', (doc_id, tag_id))
            conn.commit()
            conn.close()
            
            self.load_data()
            QMessageBox.information(self, "成功", "文档信息已更新")
    
    def move_document(self, doc_id):
        """移动单个文档"""
        self.selected_docs = {doc_id}
        self.on_move_selected()
    
    def delete_document(self, doc_id):
        """删除单个文档"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除此文档吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            db.delete_document(doc_id)
            QMessageBox.information(self, "成功", "文档已删除")
            self.load_data()
    
    def on_search(self):
        """搜索文档 - 支持按文件夹、标题、分类、年份筛选"""
        keyword = self.search_edit.text().strip() or None
        category_id = self.category_filter.currentData()
        year = self.year_filter.currentData()
        
        documents = self.search_documents(
            keyword=keyword,
            category_id=category_id,
            year=year,
            folder_path=self.current_folder
        )
        
        self.load_documents(documents)
    
    def search_documents(self, keyword=None, category_id=None, year=None, folder_path=None):
        """搜索文档"""
        conn = db.get_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        if keyword:
            conditions.append('title LIKE ?')
            params.append(f'%{keyword}%')
        if category_id:
            conditions.append('category_id = ?')
            params.append(category_id)
        if year:
            conditions.append('year = ?')
            params.append(year)
        if folder_path:
            conditions.append('folder_path = ?')
            params.append(folder_path)
        
        sql = 'SELECT * FROM documents'
        if conditions:
            sql += ' WHERE ' + ' AND '.join(conditions)
        sql += ' ORDER BY import_date DESC'
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    def on_reset(self):
        """重置筛选"""
        self.search_edit.clear()
        self.category_filter.setCurrentIndex(0)
        self.year_filter.setCurrentIndex(0)
        self.current_folder = None
        self.load_folder_tree()
        self.on_search()
    
    def on_refresh(self):
        """刷新文件库"""
        self.load_folder_tree()
        self.on_search()
        QMessageBox.information(self, "提示", "文件库已刷新")
    
    def on_import_file(self):
        """导入文件（支持多选）"""
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
            self.load_data()
    
    def on_import_folder(self):
        """导入文件夹"""
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        
        if folder_path:
            folder_name = Path(folder_path).name
            item = QTreeWidgetItem(self.folder_tree)
            item.setText(0, folder_name)
            item.setData(0, Qt.UserRole, {'name': folder_name, 'level': 1})
            
            progress = QProgressDialog("准备导入...", "取消", 0, 100, self)
            progress.setWindowTitle("批量导入")
            progress.setWindowModality(Qt.WindowModal)
            
            self.import_thread = ImportThread(folder_path)
            self.import_thread.progress.connect(
                lambda c, t, n: progress.setLabelText(f"正在导入 ({c}/{t}): {n}")
            )
            self.import_thread.progress.connect(
                lambda c, t, n: progress.setValue(int(c / t * 100))
            )
            self.import_thread.finished_signal.connect(
                lambda result: self.on_import_finished(result, progress)
            )
            
            self.import_thread.start()
    
    def on_import_finished(self, result, progress):
        """导入完成处理"""
        progress.close()
        
        if result['success']:
            msg = f"导入完成！\n\n总计: {result['total']}\n成功: {result['success_count']}\n失败: {result['failed_count']}"
            QMessageBox.information(self, "导入完成", msg)
            self.load_data()
        else:
            QMessageBox.warning(self, "导入失败", result['error'])
    
    def on_move_selected(self):
        """移动选中的文档到文件夹"""
        if not self.selected_docs:
            QMessageBox.warning(self, "提示", "请先选择要移动的文档")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("选择目标文件夹")
        dialog.setMinimumSize(300, 400)
        # 去掉问号按钮
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout(dialog)
        
        # 提示标签
        hint_label = QLabel("请选择目标文件夹：")
        hint_label.setStyleSheet("font-size: 13px; color: #333;")
        layout.addWidget(hint_label)
        
        # 文件夹树（从数据库加载）
        tree = QTreeWidget()
        tree.setHeaderHidden(True)
        tree.setStyleSheet("""
            QTreeWidget {
                background-color: white;
                border: 1px solid #e8e8e8;
                border-radius: 4px;
            }
            QTreeWidget::item {
                padding: 6px;
                border-radius: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #e6f7ff;
                color: #1890ff;
            }
            QTreeWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        
        # 从数据库加载文件夹
        folders = db.get_folders()
        
        def add_folder_items(parent, folder_list):
            for folder in folder_list:
                item = QTreeWidgetItem(parent)
                item.setText(0, f"📁 {folder['name']}")
                item.setData(0, Qt.UserRole, folder['name'])
                # 加载子文件夹
                sub_folders = db.get_folders(folder['id'])
                if sub_folders:
                    add_folder_items(item, sub_folders)
        
        add_folder_items(tree, folders)
        
        tree.expandAll()
        layout.addWidget(tree)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #666;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                border-color: #1890ff;
                color: #1890ff;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("确定")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
        """)
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            item = tree.currentItem()
            if item:
                folder_name = item.data(0, Qt.UserRole)
                
                # 更新文档的文件夹路径
                try:
                    for doc_id in self.selected_docs:
                        db.update_document(doc_id, folder_path=folder_name)
                    
                    QMessageBox.information(self, "成功", f"已移动 {len(self.selected_docs)} 个文档到 \"{folder_name}\"")
                    self.selected_docs.clear()
                    self.load_data()
                except Exception as e:
                    QMessageBox.warning(self, "失败", f"移动失败: {e}")
            else:
                QMessageBox.warning(self, "提示", "请先选择一个目标文件夹")
    
    def copy_tree_items(self, source_item, target_item):
        """复制树形结构"""
        for i in range(source_item.childCount()):
            child = source_item.child(i)
            new_child = QTreeWidgetItem(target_item)
            new_child.setText(0, child.text(0))
            new_child.setData(0, Qt.UserRole, child.data(0, Qt.UserRole))
            self.copy_tree_items(child, new_child)
    
    def on_delete_selected(self):
        """删除选中的文档"""
        if not self.selected_docs:
            QMessageBox.warning(self, "提示", "请先选择要删除的文档")
            return
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除选中的 {len(self.selected_docs)} 个文档吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for doc_id in self.selected_docs:
                db.delete_document(doc_id)
            
            QMessageBox.information(self, "成功", "文档已删除")
            self.selected_docs.clear()
            self.load_data()


# 导入QFormLayout
from PyQt5.QtWidgets import QFormLayout
