from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView, QMessageBox, QMenu,
                             QAction, QDialog, QTextEdit, QFormLayout, QComboBox,
                             QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from core.database import db
from core.styles import (PAGINATION_BTN_STYLE, PAGINATION_INFO_STYLE, PAGINATION_COMBO_STYLE,
                          LIST_ITEM_ENHANCED_STYLE, TOOLBAR_DEFAULT_BTN, TOOLBAR_DANGER_BTN,
                          SEARCH_BOX_STYLE, FILTER_COMBO_STYLE)


class FavoritesWidget(QWidget):
    """星标收藏模块 - 带分页功能"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 1
        self.page_size = 20
        self.total_pages = 1
        self.all_favorites = []
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("星标收藏")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("全部分类", None)
        # 从数据库加载分类
        categories = db.get_categories()
        for cat in categories:
            self.category_filter.addItem(cat['name'], cat['id'])
        self.category_filter.setStyleSheet(FILTER_COMBO_STYLE)
        toolbar.addWidget(self.category_filter)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索收藏的文档...")
        self.search_edit.setStyleSheet(SEARCH_BOX_STYLE)
        toolbar.addWidget(self.search_edit, 1)
        
        self.search_btn = QPushButton("🔍 搜索")
        self.search_btn.setStyleSheet(TOOLBAR_DEFAULT_BTN)
        self.search_btn.clicked.connect(self.load_data)
        toolbar.addWidget(self.search_btn)
        
        toolbar.addStretch()
        
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.setStyleSheet(TOOLBAR_DEFAULT_BTN)
        self.refresh_btn.clicked.connect(self.load_data)
        toolbar.addWidget(self.refresh_btn)
        
        layout.addLayout(toolbar)
        
        self.favorites_list = QListWidget()
        self.favorites_list.setStyleSheet(LIST_ITEM_ENHANCED_STYLE)
        self.favorites_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.favorites_list.customContextMenuRequested.connect(self.on_context_menu)
        self.favorites_list.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.favorites_list)
        
        # 分页栏
        self.setup_pagination(layout)
    
    def setup_pagination(self, parent_layout):
        """设置分页组件"""
        pagination_widget = QWidget()
        pagination_widget.setStyleSheet("background-color: white; border: 1px solid #e8e8e8; border-radius: 8px; padding: 10px;")
        pagination_layout = QHBoxLayout(pagination_widget)
        pagination_layout.setContentsMargins(10, 5, 10, 5)
        pagination_layout.setSpacing(10)
        
        # 统计信息
        self.pagination_info = QLabel("共 0 条")
        self.pagination_info.setStyleSheet(PAGINATION_INFO_STYLE)
        pagination_layout.addWidget(self.pagination_info)
        
        pagination_layout.addStretch()
        
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
        
        parent_layout.addWidget(pagination_widget)
    
    def load_data(self):
        """加载收藏数据"""
        category_id = self.category_filter.currentData()
        keyword = self.search_edit.text().strip() or None
        
        favorites = db.get_favorites()
        
        # 筛选数据
        filtered_favorites = []
        
        for fav in favorites:
            doc = db.get_document(fav['document_id'])
            if not doc:
                continue
            
            # 检查筛选
            matches = True
            if keyword and keyword.lower() not in (doc['title'] or '').lower():
                matches = False
            
            if category_id is not None and doc['category_id'] != category_id:
                matches = False
            
            if matches:
                filtered_favorites.append((fav, doc))
        
        self.all_favorites = filtered_favorites
        self.total_pages = max(1, (len(self.all_favorites) + self.page_size - 1) // self.page_size)
        self.current_page = min(self.current_page, self.total_pages)
        
        self.display_current_page()
    
    def display_current_page(self):
        """显示当前页数据"""
        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        page_data = self.all_favorites[start:end]
        
        # 更新统计
        self.pagination_info.setText(f"共 {len(self.all_favorites)} 条")
        self.page_label.setText(f"{self.current_page} / {self.total_pages}")
        
        # 更新按钮状态
        self.first_page_btn.setEnabled(self.current_page > 1)
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < self.total_pages)
        self.last_page_btn.setEnabled(self.current_page < self.total_pages)
        
        # 填充列表
        self.favorites_list.clear()
        for fav, doc in page_data:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, {'fav_id': fav['id'], 'doc_id': fav['document_id']})
            
            # 格式化显示
            title = doc['title'] or '未命名'
            file_type = (doc['file_type'] or '未知').upper()
            word_count = len(doc['content_text'] or '')
            added_date = str(fav['added_date'])[:10] if fav['added_date'] else '-'
            
            item.setText(f"⭐ {title}\n{file_type}   {word_count}字   收藏于 {added_date}")
            item.setToolTip(title)
            
            self.favorites_list.addItem(item)
    
    def on_page_size_changed(self, text):
        """每页条数改变"""
        self.page_size = int(text)
        self.current_page = 1
        self.load_data()
    
    def go_first_page(self):
        """首页"""
        self.current_page = 1
        self.display_current_page()
    
    def go_prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.display_current_page()
    
    def go_next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_current_page()
    
    def go_last_page(self):
        """末页"""
        self.current_page = self.total_pages
        self.display_current_page()
    
    def on_item_clicked(self, item):
        """点击收藏项 - 预览文档"""
        data = item.data(Qt.UserRole)
        if data:
            self.preview_document(data['doc_id'])
    
    def preview_document(self, doc_id):
        """预览文档"""
        from modules.material_library import DocumentPreviewDialog
        dialog = DocumentPreviewDialog(doc_id, self)
        dialog.exec_()
        # 预览关闭后刷新列表（可能取消了收藏）
        self.load_data()
    
    def remove_favorite(self, fav_id):
        """取消收藏"""
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要取消收藏吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 删除收藏记录
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM favorites WHERE id = ?', (fav_id,))
            conn.commit()
            conn.close()
            
            self.load_data()
            QMessageBox.information(self, "成功", "已取消收藏")
    
    def on_context_menu(self, position):
        """右键菜单"""
        menu = QMenu(self)
        
        item = self.favorites_list.itemAt(position)
        if item:
            data = item.data(Qt.UserRole)
            
            preview_action = QAction("预览文档", self)
            preview_action.triggered.connect(lambda: self.preview_document(data['doc_id']))
            menu.addAction(preview_action)
            
            menu.addSeparator()
            
            remove_action = QAction("取消收藏", self)
            remove_action.triggered.connect(lambda: self.remove_favorite(data['fav_id']))
            menu.addAction(remove_action)
        
        menu.exec_(self.favorites_list.viewport().mapToGlobal(position))


class QuoteEditDialog(QDialog):
    """金句编辑对话框"""
    
    def __init__(self, quote_id=None, parent=None):
        super().__init__(parent)
        self.quote_id = quote_id
        self.setWindowTitle("编辑金句" if quote_id else "添加金句")
        # 去掉问号按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(500)
        self.setup_ui()
        
        if quote_id:
            self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.content_edit = QTextEdit()
        self.content_edit.setMaximumHeight(150)
        form_layout.addRow("金句内容:", self.content_edit)
        
        # 分类下拉框（可编辑）
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItem("其他", "")
        self.category_combo.addItem("开头句", "开头句")
        self.category_combo.addItem("结尾句", "结尾句")
        self.category_combo.addItem("过渡句", "过渡句")
        self.category_combo.addItem("排比句", "排比句")
        self.category_combo.addItem("固定搭配", "固定搭配")
        self.category_combo.addItem("强调句", "强调句")
        self.category_combo.addItem("总结句", "总结句")
        self.category_combo.addItem("对策句", "对策句")
        self.category_combo.addItem("成效句", "成效句")
        form_layout.addRow("分类:", self.category_combo)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        form_layout.addRow("备注:", self.notes_edit)
        
        layout.addLayout(form_layout)
        
        buttons = QPushButton("保存")
        buttons.clicked.connect(self.accept)
        layout.addWidget(buttons)
    
    def load_data(self):
        """加载金句数据"""
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM quotes WHERE id = ?', (self.quote_id,))
        quote = cursor.fetchone()
        conn.close()
        
        if quote:
            quote = dict(quote)
            self.content_edit.setText(quote['content'] or '')
            # 设置分类
            category = quote['category'] or ''
            index = self.category_combo.findText(category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            else:
                self.category_combo.setCurrentText(category)
            self.notes_edit.setText(quote['notes'] or '')
    
    def get_data(self):
        return {
            'content': self.content_edit.toPlainText(),
            'category': self.category_combo.currentText(),
            'notes': self.notes_edit.toPlainText()
        }


class QuotesWidget(QWidget):
    """金句库模块 - 带分页功能"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 1
        self.page_size = 20
        self.total_pages = 1
        self.all_quotes = []
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("金句库")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        toolbar = QHBoxLayout()
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("全部分类", None)
        preset_categories = ["其他", "开头句", "结尾句", "过渡句", "排比句", "固定搭配", "强调句", "总结句", "对策句", "成效句"]
        for cat in preset_categories:
            self.category_filter.addItem(cat, cat)
        self.category_filter.setStyleSheet(FILTER_COMBO_STYLE)
        toolbar.addWidget(self.category_filter)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索金句...")
        self.search_edit.setStyleSheet(SEARCH_BOX_STYLE)
        toolbar.addWidget(self.search_edit, 1)
        
        self.search_btn = QPushButton("🔍 搜索")
        self.search_btn.setStyleSheet(TOOLBAR_DEFAULT_BTN)
        self.search_btn.clicked.connect(self.load_data)
        toolbar.addWidget(self.search_btn)
        
        toolbar.addStretch()
        
        self.add_btn = QPushButton("➕ 添加金句")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
        """)
        self.add_btn.clicked.connect(self.add_quote)
        toolbar.addWidget(self.add_btn)
        
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.setStyleSheet(TOOLBAR_DEFAULT_BTN)
        self.refresh_btn.clicked.connect(self.load_data)
        toolbar.addWidget(self.refresh_btn)
        
        layout.addLayout(toolbar)
        
        self.quotes_list = QListWidget()
        self.quotes_list.setStyleSheet(LIST_ITEM_ENHANCED_STYLE)
        self.quotes_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.quotes_list.customContextMenuRequested.connect(self.on_context_menu)
        layout.addWidget(self.quotes_list)
        
        # 分页栏
        self.setup_pagination(layout)
    
    def setup_pagination(self, parent_layout):
        """设置分页组件"""
        pagination_widget = QWidget()
        pagination_widget.setStyleSheet("background-color: white; border: 1px solid #e8e8e8; border-radius: 8px; padding: 10px;")
        pagination_layout = QHBoxLayout(pagination_widget)
        pagination_layout.setContentsMargins(10, 5, 10, 5)
        pagination_layout.setSpacing(10)
        
        # 统计信息
        self.pagination_info = QLabel("共 0 条")
        self.pagination_info.setStyleSheet(PAGINATION_INFO_STYLE)
        pagination_layout.addWidget(self.pagination_info)
        
        pagination_layout.addStretch()
        
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
        
        parent_layout.addWidget(pagination_widget)
    
    def load_data(self):
        """加载金句数据"""
        category = self.category_filter.currentData()
        keyword = self.search_edit.text().strip() or None
        
        quotes = db.get_quotes(category=category, search_keyword=keyword)
        
        self.all_quotes = quotes
        self.total_pages = max(1, (len(self.all_quotes) + self.page_size - 1) // self.page_size)
        self.current_page = min(self.current_page, self.total_pages)
        
        # 更新分类下拉框（保留预设分类）
        current_category = self.category_filter.currentData()
        self.category_filter.clear()
        self.category_filter.addItem("全部分类", None)
        # 预设分类
        preset_categories = ["其他", "开头句", "结尾句", "过渡句", "排比句", "固定搭配", "强调句", "总结句", "对策句", "成效句"]
        for cat in preset_categories:
            self.category_filter.addItem(cat, cat)
        
        # 恢复选择
        if current_category:
            index = self.category_filter.findData(current_category)
            if index >= 0:
                self.category_filter.setCurrentIndex(index)
        
        self.display_current_page()
    
    def display_current_page(self):
        """显示当前页数据"""
        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        page_data = self.all_quotes[start:end]
        
        # 更新统计
        self.pagination_info.setText(f"共 {len(self.all_quotes)} 条")
        self.page_label.setText(f"{self.current_page} / {self.total_pages}")
        
        # 更新按钮状态
        self.first_page_btn.setEnabled(self.current_page > 1)
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < self.total_pages)
        self.last_page_btn.setEnabled(self.current_page < self.total_pages)
        
        # 填充列表
        self.quotes_list.clear()
        for quote in page_data:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, quote['id'])
            
            # 格式化显示
            content = quote['content'] or ''
            if len(content) > 100:
                content = content[:100] + "..."
            
            category_text = f" [{quote['category']}]" if quote['category'] else ""
            tags_text = f" ({quote['tags']})" if quote['tags'] else ""
            
            item.setText(f"{content}{category_text}{tags_text}")
            item.setToolTip(quote['content'])
            
            self.quotes_list.addItem(item)
    
    def on_page_size_changed(self, text):
        """每页条数改变"""
        self.page_size = int(text)
        self.current_page = 1
        self.load_data()
    
    def go_first_page(self):
        """首页"""
        self.current_page = 1
        self.display_current_page()
    
    def go_prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.display_current_page()
    
    def go_next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_current_page()
    
    def go_last_page(self):
        """末页"""
        self.current_page = self.total_pages
        self.display_current_page()
    
    def add_quote(self):
        """添加金句"""
        dialog = QuoteEditDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data['content'].strip():
                db.add_quote(
                    content=data['content'],
                    category=data['category'] or None,
                    tags=data['tags'] or None,
                    notes=data['notes'] or None
                )
                self.load_data()
                QMessageBox.information(self, "成功", "金句已添加")
    
    def edit_quote(self):
        """编辑金句"""
        item = self.quotes_list.currentItem()
        if not item:
            return
        
        quote_id = item.data(Qt.UserRole)
        dialog = QuoteEditDialog(quote_id, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE quotes SET content=?, category=?, tags=?, notes=?
                WHERE id=?
            ''', (data['content'], data['category'], data['tags'], data['notes'], quote_id))
            conn.commit()
            conn.close()
            self.load_data()
    
    def delete_quote(self):
        """删除金句"""
        item = self.quotes_list.currentItem()
        if not item:
            return
        
        quote_id = item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这条金句吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM quotes WHERE id = ?', (quote_id,))
            conn.commit()
            conn.close()
            self.load_data()
    
    def on_context_menu(self, position):
        """右键菜单"""
        menu = QMenu(self)
        
        copy_action = QAction("复制", self)
        copy_action.triggered.connect(self.copy_quote)
        menu.addAction(copy_action)
        
        menu.addSeparator()
        
        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(self.edit_quote)
        menu.addAction(edit_action)
        
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(self.delete_quote)
        menu.addAction(delete_action)
        
        menu.exec_(self.quotes_list.viewport().mapToGlobal(position))
    
    def copy_quote(self):
        """复制金句到剪贴板"""
        item = self.quotes_list.currentItem()
        if item:
            quote_id = item.data(Qt.UserRole)
            quote = db.get_quote(quote_id)
            if quote:
                from PyQt5.QtWidgets import QApplication
                clipboard = QApplication.clipboard()
                clipboard.setText(quote['content'])


# 导入QFormLayout
from PyQt5.QtWidgets import QFormLayout
