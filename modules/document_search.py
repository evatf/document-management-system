from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QComboBox, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView,
                             QTextEdit, QSplitter, QListWidget, QListWidgetItem,
                             QMessageBox, QDialog, QMenu, QAction)
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt5.QtGui import QColor, QBrush, QFont

from core.database import db
from core.styles import (PAGINATION_BTN_STYLE, PAGINATION_INFO_STYLE, PAGINATION_COMBO_STYLE,
                          TOOLBAR_PRIMARY_BTN, TOOLBAR_DEFAULT_BTN, SEARCH_BOX_STYLE, 
                          FILTER_COMBO_STYLE, LIST_ITEM_ENHANCED_STYLE)


class SearchResultWidget(QWidget):
    """搜索结果项Widget - 支持富文本，点击标题预览"""
    
    clicked = pyqtSignal(int)  # 点击信号，传递doc_id
    
    def __init__(self, doc, keywords, parent=None):
        super().__init__(parent)
        self.doc_id = doc['id']
        self.setup_ui(doc, keywords)
    
    def setup_ui(self, doc, keywords):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(8)
        
        title = doc['title'] or '未命名'
        content = doc['content_text'] or ''
        
        first_pos = -1
        text_lower = content.lower()
        for keyword in keywords:
            if keyword.strip():
                pos = text_lower.find(keyword.lower())
                if pos != -1 and (first_pos == -1 or pos < first_pos):
                    first_pos = pos
        
        if first_pos != -1:
            start = max(0, first_pos - 50)
            end = min(len(content), first_pos + 150)
            excerpt = content[start:end]
            prefix = "..." if start > 0 else ""
            suffix = "..." if end < len(content) else ""
            excerpt = prefix + excerpt + suffix
        else:
            excerpt = content[:150] + "..." if len(content) > 150 else content
        
        if keywords:
            title_html = self.highlight_with_html(title, keywords)
            excerpt_html = self.highlight_with_html(excerpt, keywords)
        else:
            title_html = title
            excerpt_html = excerpt
        
        # 可点击的标题按钮
        title_btn = QPushButton(f"📄 {title_html}")
        title_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                border: none;
                background: transparent;
                font-size: 15px;
                font-weight: bold;
                color: #1890ff;
                padding: 0;
            }
            QPushButton:hover {
                color: #40a9ff;
                text-decoration: underline;
            }
        """)
        title_btn.clicked.connect(self.on_title_clicked)
        layout.addWidget(title_btn)
        
        excerpt_label = QLabel()
        excerpt_label.setTextFormat(Qt.RichText)
        excerpt_label.setWordWrap(True)
        excerpt_label.setText(f'<span style="font-size: 13px; color: #333;">{excerpt_html}</span>')
        layout.addWidget(excerpt_label)
        
        categories = {cat['id']: cat['name'] for cat in db.get_categories()}
        category = categories.get(doc['category_id'], '未分类')
        year = str(doc['year']) if doc['year'] else '-'
        file_type = (doc['file_type'] or '未知').upper()
        word_count = len(content)
        
        meta_label = QLabel(f'📁 {category}   📅 {year}   📝 {file_type}   🔤 {word_count}字')
        meta_label.setStyleSheet('font-size: 12px; color: #999;')
        layout.addWidget(meta_label)
    
    def on_title_clicked(self):
        """标题被点击"""
        self.clicked.emit(self.doc_id)
    
    def highlight_with_html(self, text, keywords):
        """用HTML span标签高亮关键词"""
        if not text:
            return ""
        
        import re
        # 先转义HTML特殊字符
        text = (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))
        
        # 高亮关键词
        result = text
        for keyword in sorted(keywords, key=len, reverse=True):
            if keyword.strip():
                # 对关键词也进行转义
                escaped_keyword = re.escape(keyword)
                pattern = re.compile(escaped_keyword, re.IGNORECASE)
                result = pattern.sub(f'<span style="background-color: #fff2cc; color: #d4380d; font-weight: bold;">\\g<0></span>', result)
        
        return result


class DocumentSearchWidget(QWidget):
    """文档检索模块 - 支持分页和富文本高亮"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_keywords = []
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.all_docs = []
        self.current_page = 1
        self.page_size = 20
        self.total_pages = 1
        self.search_history = []
        self.max_history = 10
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title = QLabel("文档检索")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        search_widget = QWidget()
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(10)
        
        self.keyword_edit = QLineEdit()
        self.keyword_edit.setPlaceholderText("输入关键词搜索，多个关键词用空格分隔...")
        self.keyword_edit.setFixedHeight(40)
        self.keyword_edit.setStyleSheet(SEARCH_BOX_STYLE)
        self.keyword_edit.textChanged.connect(self.on_keyword_changed)
        search_layout.addWidget(self.keyword_edit, 3)
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("全部分类", None)
        self.category_filter.setFixedHeight(40)
        self.category_filter.setStyleSheet(FILTER_COMBO_STYLE)
        search_layout.addWidget(self.category_filter, 1)
        
        self.year_filter = QComboBox()
        self.year_filter.addItem("全部年份", None)
        for year in range(2024, 1989, -1):
            self.year_filter.addItem(str(year), year)
        self.year_filter.setFixedHeight(40)
        self.year_filter.setStyleSheet(FILTER_COMBO_STYLE)
        search_layout.addWidget(self.year_filter, 1)
        
        self.tag_filter = QComboBox()
        self.tag_filter.addItem("全部标签", None)
        self.tag_filter.setFixedHeight(40)
        self.tag_filter.setStyleSheet(FILTER_COMBO_STYLE)
        search_layout.addWidget(self.tag_filter, 1)
        
        self.search_btn = QPushButton("🔍 搜索")
        self.search_btn.setFixedHeight(40)
        self.search_btn.setStyleSheet(TOOLBAR_PRIMARY_BTN)
        self.search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_btn)
        
        self.history_btn = QPushButton("📋 历史")
        self.history_btn.setFixedHeight(40)
        self.history_btn.setStyleSheet(TOOLBAR_DEFAULT_BTN)
        self.history_btn.clicked.connect(self.show_search_history)
        search_layout.addWidget(self.history_btn)
        
        self.reset_btn = QPushButton("重置")
        self.reset_btn.setFixedHeight(40)
        self.reset_btn.setStyleSheet(TOOLBAR_DEFAULT_BTN)
        self.reset_btn.clicked.connect(self.reset_filters)
        search_layout.addWidget(self.reset_btn)
        
        layout.addWidget(search_widget)
        
        # 加载分类和标签
        self.load_categories()
        
        self.result_label = QLabel("请输入关键词开始搜索")
        self.result_label.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(self.result_label)
        
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #e8e8e8;
                border-radius: 8px;
            }
            QListWidget::item {
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e6f7ff;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        # 不再使用列表点击，改为点击标题预览
        # self.results_list.itemClicked.connect(self.on_result_clicked)
        layout.addWidget(self.results_list, 1)
        
        self.setup_pagination(layout)
    
    def setup_pagination(self, parent_layout):
        """设置分页组件"""
        pagination_widget = QWidget()
        pagination_layout = QHBoxLayout(pagination_widget)
        pagination_layout.setContentsMargins(0, 10, 0, 0)
        pagination_layout.setSpacing(10)
        
        self.pagination_info = QLabel("共 0 条")
        self.pagination_info.setStyleSheet(PAGINATION_INFO_STYLE)
        pagination_layout.addWidget(self.pagination_info)
        
        pagination_layout.addStretch()
        
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
        
        parent_layout.addWidget(pagination_widget)
    
    def load_categories(self):
        """加载分类数据"""
        categories = db.get_categories()
        for cat in categories:
            self.category_filter.addItem(cat['name'], cat['id'])
        
        # 加载标签
        self.load_tags()
    
    def load_tags(self):
        """加载标签数据"""
        self.tag_filter.clear()
        self.tag_filter.addItem("全部标签", None)
        tags = db.get_tags()
        for tag in tags:
            self.tag_filter.addItem(tag['name'], tag['id'])
    
    def on_keyword_changed(self):
        """关键词变化时延迟搜索"""
        self.search_timer.stop()
        self.search_timer.start(600)
    
    def parse_keywords(self, keyword_text):
        """解析关键词（空格分隔）"""
        if not keyword_text:
            return []
        keywords = [k.strip() for k in keyword_text.split() if k.strip()]
        return keywords
    
    def perform_search(self):
        """执行搜索 - 支持多关键词和标签筛选"""
        keyword_text = self.keyword_edit.text().strip()
        self.current_keywords = self.parse_keywords(keyword_text)
        
        if keyword_text:
            self.save_to_history(keyword_text)
        
        category_id = self.category_filter.currentData()
        year = self.year_filter.currentData()
        tag_id = self.tag_filter.currentData()
        
        self.all_docs = self.search_documents_multi_keywords(
            keywords=self.current_keywords,
            category_id=category_id,
            year=year,
            tag_id=tag_id
        )
        
        self.current_page = 1
        self.display_current_page()
    
    def search_documents_multi_keywords(self, keywords, category_id=None, year=None, tag_id=None):
        """多关键词搜索文档 - 支持标签筛选"""
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # 如果选择了标签，先获取该标签下的文档ID
        doc_ids_with_tag = None
        if tag_id:
            cursor.execute('SELECT document_id FROM document_tags WHERE tag_id = ?', (tag_id,))
            doc_ids_with_tag = {row[0] for row in cursor.fetchall()}
            if not doc_ids_with_tag:
                conn.close()
                return []
        
        conditions = []
        params = []
        
        if keywords:
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append('(title LIKE ? OR content_text LIKE ?)')
                params.extend([f'%{keyword}%', f'%{keyword}%'])
            conditions.append('(' + ' OR '.join(keyword_conditions) + ')')
        
        if category_id:
            conditions.append('category_id = ?')
            params.append(category_id)
        
        if year:
            conditions.append('year = ?')
            params.append(year)
        
        if doc_ids_with_tag:
            placeholders = ','.join('?' * len(doc_ids_with_tag))
            conditions.append(f'id IN ({placeholders})')
            params.extend(list(doc_ids_with_tag))
        
        sql = 'SELECT * FROM documents'
        if conditions:
            sql += ' WHERE ' + ' AND '.join(conditions)
        sql += ' ORDER BY import_date DESC'
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    def display_current_page(self):
        """显示当前页"""
        self.results_list.clear()
        
        total = len(self.all_docs)
        self.total_pages = max(1, (total + self.page_size - 1) // self.page_size)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        
        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        page_docs = self.all_docs[start:end]
        
        for doc in page_docs:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, doc['id'])
            
            widget = SearchResultWidget(doc, self.current_keywords)
            widget.clicked.connect(self.preview_document)  # 连接点击信号
            # 增加行高以显示完整两句话
            item.setSizeHint(QSize(self.results_list.width(), 140))
            
            self.results_list.addItem(item)
            self.results_list.setItemWidget(item, widget)
        
        if self.current_keywords:
            keyword_str = '"' + '" "'.join(self.current_keywords) + '"'
            self.result_label.setText(f"关键词 {keyword_str} 找到 {len(self.all_docs)} 个结果")
        else:
            self.result_label.setText(f"共 {len(self.all_docs)} 个文档")
        
        self.update_pagination()
    
    def update_pagination(self):
        """更新分页显示"""
        total = len(self.all_docs)
        self.total_pages = max(1, (total + self.page_size - 1) // self.page_size)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        
        self.pagination_info.setText(f"共 {total} 条")
        self.page_label.setText(f"{self.current_page} / {self.total_pages}")
        
        self.first_page_btn.setEnabled(self.current_page > 1)
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < self.total_pages)
        self.last_page_btn.setEnabled(self.current_page < self.total_pages)
    
    def on_page_size_changed(self, text):
        """每页条数改变"""
        self.page_size = int(text)
        self.current_page = 1
        self.display_current_page()
    
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
    
    def on_result_clicked(self, item):
        """点击结果项 - 预览文档"""
        doc_id = item.data(Qt.UserRole)
        self.preview_document(doc_id)
    
    def preview_document(self, doc_id):
        """预览文档"""
        from modules.material_library import DocumentPreviewDialog
        dialog = DocumentPreviewDialog(doc_id, self)
        dialog.exec_()
    
    def reset_filters(self):
        """重置筛选"""
        self.keyword_edit.clear()
        self.category_filter.setCurrentIndex(0)
        self.year_filter.setCurrentIndex(0)
        self.current_keywords = []
        self.all_docs = []
        self.current_page = 1
        self.results_list.clear()
        self.result_label.setText("请输入关键词开始搜索")
        self.update_pagination()
    
    def show_search_history(self):
        """显示搜索历史"""
        menu = QMenu(self)
        
        if self.search_history:
            for keywords in self.search_history:
                action = QAction(keywords, self)
                action.triggered.connect(lambda checked, k=keywords: self.apply_history(k))
                menu.addAction(action)
            
            menu.addSeparator()
            clear_action = QAction("清除历史", self)
            clear_action.triggered.connect(self.clear_history)
            menu.addAction(clear_action)
        else:
            no_history = QAction("暂无搜索历史", self)
            no_history.setEnabled(False)
            menu.addAction(no_history)
        
        menu.exec_(self.history_btn.mapToGlobal(self.history_btn.rect().bottomLeft()))
    
    def apply_history(self, keywords):
        """应用搜索历史"""
        self.keyword_edit.setText(keywords)
        self.perform_search()
    
    def clear_history(self):
        """清除搜索历史"""
        self.search_history = []
        QMessageBox.information(self, "成功", "搜索历史已清除")
    
    def save_to_history(self, keyword_text):
        """保存到搜索历史"""
        if not keyword_text or keyword_text in self.search_history:
            return
        
        self.search_history.insert(0, keyword_text)
        if len(self.search_history) > self.max_history:
            self.search_history.pop()
