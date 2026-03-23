import shutil
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QComboBox, QCheckBox,
                             QSpinBox, QGroupBox, QFormLayout, QFileDialog,
                             QMessageBox, QTabWidget, QTextEdit, QListWidget,
                             QListWidgetItem, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt

from core.config import config
from core.database import db
from core.styles import (TOOLBAR_PRIMARY_BTN, TOOLBAR_DEFAULT_BTN, TOOLBAR_DANGER_BTN,
                          DIALOG_BTN_PRIMARY, DIALOG_BTN_DEFAULT, SEARCH_BOX_STYLE)


class BackupManager:
    """备份管理器"""
    
    def __init__(self):
        self.backup_path = Path(config.get('backup.backup_path'))
        self.backup_path.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, note=None, backup_type='manual'):
        """创建备份
        
        Args:
            note: 备份备注
            backup_type: 备份类型 ('manual' 或 'auto')
        """
        try:
            from core.config import get_data_dir
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}"
            backup_dir = self.backup_path / backup_name
            backup_dir.mkdir(exist_ok=True)
            
            # 备份数据库 - 使用正确的数据目录
            data_dir = get_data_dir()
            db_path = data_dir / "database.db"
            if db_path.exists():
                shutil.copy2(db_path, backup_dir / 'database.db')
            
            # 备份配置文件 - 从用户数据目录
            config_dir = data_dir / "config"
            if config_dir.exists():
                shutil.copytree(config_dir, backup_dir / 'config', dirs_exist_ok=True)
            
            # 计算备份大小
            backup_size = sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file())
            
            # 记录备份信息到数据库
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO backups (backup_path, backup_size, backup_type, note)
                VALUES (?, ?, ?, ?)
            ''', (str(backup_dir), backup_size, backup_type, note))
            conn.commit()
            conn.close()
            
            db.add_log('backup', str(backup_dir), f'创建备份: {backup_name}')
            
            return {
                'success': True,
                'backup_path': str(backup_dir),
                'backup_size': backup_size,
                'backup_name': backup_name
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_backup_list(self):
        """获取备份列表"""
        backups = []
        if self.backup_path.exists():
            for item in self.backup_path.iterdir():
                if item.is_dir() and item.name.startswith('backup_'):
                    stat = item.stat()
                    size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                    backups.append({
                        'name': item.name,
                        'path': str(item),
                        'size': size,
                        'time': datetime.fromtimestamp(stat.st_mtime)
                    })
        return sorted(backups, key=lambda x: x['time'], reverse=True)
    
    def restore_backup(self, backup_path):
        """恢复备份"""
        try:
            from core.config import get_data_dir
            
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                return {'success': False, 'error': '备份不存在'}
            
            # 恢复数据库
            db_backup = backup_dir / 'database.db'
            if db_backup.exists():
                data_dir = get_data_dir()
                db_path = data_dir / 'database.db'
                # 先备份当前数据库
                if db_path.exists():
                    shutil.copy2(db_path, str(db_path) + '.bak')
                shutil.copy2(db_backup, db_path)
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


class SettingsWidget(QWidget):
    """系统设置模块"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.backup_manager = BackupManager()
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("系统设置")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # 创建标签页
        tabs = QTabWidget()
        
        # 数据管理
        data_tab = self.create_data_tab()
        tabs.addTab(data_tab, "数据管理")
        
        # 备份设置
        backup_tab = self.create_backup_tab()
        tabs.addTab(backup_tab, "数据备份")
        
        # 关于
        about_tab = self.create_about_tab()
        tabs.addTab(about_tab, "关于")
        
        layout.addWidget(tabs)
    
    def create_data_tab(self):
        """创建数据管理标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 数据库统计
        stats_group = QGroupBox("数据库统计")
        stats_layout = QFormLayout(stats_group)
        
        self.doc_count_label = QLabel("0")
        stats_layout.addRow("文档数量:", self.doc_count_label)
        
        self.category_count_label = QLabel("0")
        stats_layout.addRow("分类数量:", self.category_count_label)
        
        self.quote_count_label = QLabel("0")
        stats_layout.addRow("金句数量:", self.quote_count_label)
        
        self.favorite_count_label = QLabel("0")
        stats_layout.addRow("收藏数量:", self.favorite_count_label)
        
        layout.addWidget(stats_group)
        
        # 数据清理
        clean_group = QGroupBox("数据清理")
        clean_layout = QVBoxLayout(clean_group)
        
        clean_info = QLabel("清除数据库将删除所有文档、分类、金句和收藏数据，此操作不可恢复！")
        clean_info.setStyleSheet("color: #ff4d4f; font-size: 13px;")
        clean_info.setWordWrap(True)
        clean_layout.addWidget(clean_info)
        
        clean_btn_layout = QHBoxLayout()
        clean_btn_layout.setSpacing(10)
        
        self.clear_docs_btn = QPushButton("清除所有文档")
        self.clear_docs_btn.setStyleSheet(TOOLBAR_DANGER_BTN)
        self.clear_docs_btn.setMinimumWidth(120)
        self.clear_docs_btn.clicked.connect(self.clear_documents)
        clean_btn_layout.addWidget(self.clear_docs_btn)
        
        self.clear_quotes_btn = QPushButton("清除所有金句")
        self.clear_quotes_btn.setStyleSheet(TOOLBAR_DANGER_BTN)
        self.clear_quotes_btn.setMinimumWidth(120)
        self.clear_quotes_btn.clicked.connect(self.clear_quotes)
        clean_btn_layout.addWidget(self.clear_quotes_btn)
        
        self.clear_all_btn = QPushButton("清除全部数据")
        self.clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4d4f;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #ff7875;
            }
        """)
        self.clear_all_btn.clicked.connect(self.clear_all_data)
        clean_btn_layout.addWidget(self.clear_all_btn)
        
        clean_btn_layout.addStretch()
        clean_layout.addLayout(clean_btn_layout)
        
        layout.addWidget(clean_group)
        layout.addStretch()
        
        # 加载统计数据
        self.load_data_stats()
        
        return widget
    
    def create_backup_tab(self):
        """创建备份设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 自动备份设置
        settings_group = QGroupBox("自动备份设置")
        settings_form = QFormLayout(settings_group)
        
        self.auto_backup_check = QCheckBox("启用自动备份")
        settings_form.addRow(self.auto_backup_check)
        
        self.backup_freq_combo = QComboBox()
        self.backup_freq_combo.addItem("每天", "daily")
        self.backup_freq_combo.addItem("每周", "weekly")
        self.backup_freq_combo.addItem("每月", "monthly")
        settings_form.addRow("备份频率:", self.backup_freq_combo)
        
        self.backup_keep_spin = QSpinBox()
        self.backup_keep_spin.setRange(1, 100)
        self.backup_keep_spin.setValue(10)
        settings_form.addRow("保留备份数量:", self.backup_keep_spin)
        
        layout.addWidget(settings_group)
        
        # 手动备份
        manual_group = QGroupBox("手动备份")
        manual_layout = QHBoxLayout(manual_group)
        
        self.backup_now_btn = QPushButton("立即备份")
        self.backup_now_btn.setStyleSheet(TOOLBAR_PRIMARY_BTN)
        self.backup_now_btn.clicked.connect(self.create_backup)
        manual_layout.addWidget(self.backup_now_btn)
        
        manual_layout.addStretch()
        layout.addWidget(manual_group)
        
        # 备份列表
        list_group = QGroupBox("备份列表")
        list_layout = QVBoxLayout(list_group)
        
        self.backup_list = QListWidget()
        self.backup_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #e8e8e8;
                border-radius: 8px;
            }
        """)
        list_layout.addWidget(self.backup_list)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.restore_btn = QPushButton("恢复选中备份")
        self.restore_btn.setStyleSheet(TOOLBAR_PRIMARY_BTN)
        self.restore_btn.clicked.connect(self.restore_backup)
        btn_layout.addWidget(self.restore_btn)
        
        self.delete_backup_btn = QPushButton("删除选中备份")
        self.delete_backup_btn.setStyleSheet(TOOLBAR_DANGER_BTN)
        self.delete_backup_btn.clicked.connect(self.delete_backup)
        btn_layout.addWidget(self.delete_backup_btn)
        
        btn_layout.addStretch()
        list_layout.addLayout(btn_layout)
        
        layout.addWidget(list_group)
        
        # 保存设置按钮
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        self.save_settings_btn = QPushButton("保存设置")
        self.save_settings_btn.setStyleSheet(DIALOG_BTN_PRIMARY)
        self.save_settings_btn.clicked.connect(self.save_settings)
        save_layout.addWidget(self.save_settings_btn)
        layout.addLayout(save_layout)
        
        # 加载备份列表
        self.load_backup_list()
        
        return widget
    
    def create_about_tab(self):
        """创建关于标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setHtml("""
        <h2>材料管理系统</h2>
        <p><b>版本:</b> 1.0.0</p>
        <p><b>开发目标:</b> 面向党政机关的材料管理软件</p>
        <p><b>支持系统:</b> 统信UOS / Windows</p>
        <p><b>Python版本:</b> 3.7.3+</p>
        <hr>
        <h3>功能特性</h3>
        <ul>
            <li>文档归档与管理</li>
            <li>智能全文检索</li>
            <li>词频分析与文稿比对</li>
            <li>金句库管理</li>
            <li>数据备份与恢复</li>
        </ul>
        <hr>
        <p><b>© 2026 党政机关</b></p>
        """)
        layout.addWidget(about_text)
        
        return widget
    
    def load_settings(self):
        """加载设置"""
        # 备份设置
        self.auto_backup_check.setChecked(config.get('backup.auto_backup', True))
        
        freq = config.get('backup.backup_frequency', 'daily')
        index = self.backup_freq_combo.findData(freq)
        if index >= 0:
            self.backup_freq_combo.setCurrentIndex(index)
        
        self.backup_keep_spin.setValue(config.get('backup.backup_keep_count', 10))
    
    def save_settings(self):
        """保存设置"""
        try:
            # 保存备份设置
            config.set('backup.auto_backup', self.auto_backup_check.isChecked())
            config.set('backup.backup_frequency', self.backup_freq_combo.currentData())
            config.set('backup.backup_keep_count', self.backup_keep_spin.value())
            
            # 重新调度自动备份
            from core.scheduler import restart_auto_backup
            restart_auto_backup()
            
            QMessageBox.information(self, "成功", "设置已保存")
        except Exception as e:
            QMessageBox.warning(self, "失败", f"保存设置失败: {e}")
    
    def load_data_stats(self):
        """加载数据库统计"""
        docs = db.get_all_documents()
        self.doc_count_label.setText(str(len(docs)))
        
        categories = db.get_categories()
        self.category_count_label.setText(str(len(categories)))
        
        quotes = db.get_quotes()
        self.quote_count_label.setText(str(len(quotes)))
        
        favorites = db.get_favorites()
        self.favorite_count_label.setText(str(len(favorites)))
    
    def load_backup_list(self):
        """加载备份列表"""
        self.backup_list.clear()
        backups = self.backup_manager.get_backup_list()
        
        for backup in backups:
            size_mb = backup['size'] / (1024 * 1024)
            item_text = f"{backup['name']} - {backup['time'].strftime('%Y-%m-%d %H:%M:%S')} ({size_mb:.2f} MB)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, backup['path'])
            self.backup_list.addItem(item)
    
    def create_backup(self):
        """创建备份"""
        result = self.backup_manager.create_backup()
        if result['success']:
            self.load_backup_list()
            QMessageBox.information(self, "成功", f"备份创建成功！\n位置: {result['backup_name']}")
        else:
            QMessageBox.warning(self, "失败", f"备份创建失败: {result['error']}")
    
    def restore_backup(self):
        """恢复备份"""
        item = self.backup_list.currentItem()
        if not item:
            QMessageBox.warning(self, "提示", "请先选择要恢复的备份")
            return
        
        backup_path = item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self,
            "确认恢复",
            "恢复备份将覆盖当前数据，确定要继续吗？\n建议先创建当前数据的备份。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            result = self.backup_manager.restore_backup(backup_path)
            if result['success']:
                QMessageBox.information(self, "成功", "备份恢复成功！请重启应用程序。")
            else:
                QMessageBox.warning(self, "失败", f"恢复失败: {result['error']}")
    
    def delete_backup(self):
        """删除备份"""
        item = self.backup_list.currentItem()
        if not item:
            return
        
        backup_path = item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这个备份吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                shutil.rmtree(backup_path)
                self.load_backup_list()
            except Exception as e:
                QMessageBox.warning(self, "失败", f"删除失败: {e}")
    
    def clear_documents(self):
        """清除所有文档"""
        reply = QMessageBox.question(
            self,
            "确认清除",
            "确定要清除所有文档吗？\n此操作将删除所有文档及其关联的标签和收藏，且不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute('DELETE FROM document_tags')
                cursor.execute('DELETE FROM favorites')
                cursor.execute('DELETE FROM documents')
                conn.commit()
                conn.close()
                self.load_data_stats()
                QMessageBox.information(self, "成功", "所有文档已清除")
            except Exception as e:
                QMessageBox.warning(self, "失败", f"清除失败: {e}")
    
    def clear_quotes(self):
        """清除所有金句"""
        reply = QMessageBox.question(
            self,
            "确认清除",
            "确定要清除所有金句吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute('DELETE FROM quotes')
                conn.commit()
                conn.close()
                self.load_data_stats()
                QMessageBox.information(self, "成功", "所有金句已清除")
            except Exception as e:
                QMessageBox.warning(self, "失败", f"清除失败: {e}")
    
    def clear_all_data(self):
        """清除全部数据（包括物理文件）"""
        reply = QMessageBox.question(
            self,
            "⚠️ 危险操作",
            "确定要清除全部数据吗？\n\n此操作将删除：\n- 所有文档（包括物理文件）\n- 所有分类\n- 所有金句\n- 所有收藏\n- 所有标签\n\n此操作不可恢复！\n建议先创建备份。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 二次确认
            reply2 = QMessageBox.question(
                self,
                "最终确认",
                "真的要清除全部数据吗？\n这将同时删除所有物理文件！\n这是最后一次确认机会！",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply2 == QMessageBox.Yes:
                try:
                    import shutil
                    from pathlib import Path
                    
                    # 获取所有文档的文件路径
                    documents = db.get_all_documents()
                    deleted_files = 0
                    failed_files = []
                    
                    # 删除物理文件
                    for doc in documents:
                        if doc.get('file_path'):
                            try:
                                file_path = Path(doc['file_path'])
                                if file_path.exists():
                                    file_path.unlink()
                                    deleted_files += 1
                            except Exception as e:
                                failed_files.append(f"{doc['title']}: {e}")
                    
                    # 清理空目录
                    storage_path = Path(config.get('general.default_storage_path'))
                    if storage_path.exists():
                        for folder in storage_path.iterdir():
                            if folder.is_dir():
                                try:
                                    # 只删除空目录
                                    if not any(folder.iterdir()):
                                        folder.rmdir()
                                except:
                                    pass
                    
                    # 清空数据库表
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM document_tags')
                    cursor.execute('DELETE FROM favorites')
                    cursor.execute('DELETE FROM quotes')
                    cursor.execute('DELETE FROM tags')
                    cursor.execute('DELETE FROM documents')
                    cursor.execute('DELETE FROM categories WHERE type = "custom"')
                    conn.commit()
                    conn.close()
                    
                    self.load_data_stats()
                    
                    msg = f"全部数据已清除！\n\n删除了 {deleted_files} 个物理文件"
                    if failed_files:
                        msg += f"\n\n{len(failed_files)} 个文件删除失败"
                    QMessageBox.information(self, "成功", msg)
                except Exception as e:
                    QMessageBox.warning(self, "失败", f"清除失败: {e}")
