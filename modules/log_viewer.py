from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView, QComboBox,
                             QDateEdit, QMessageBox, QFileDialog, QTextEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor

from core.database import db
from datetime import datetime


class LogViewerWidget(QWidget):
    """操作日志查看器"""
    
    LOG_TYPES = {
        'all': '全部类型',
        'import': '文档导入',
        'delete': '文档删除',
        'backup': '数据备份',
        'restore': '数据恢复',
        'rearchive': '重新归档'
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_logs()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("操作日志")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # 筛选栏
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        
        filter_layout.addWidget(QLabel("操作类型:"))
        self.type_filter = QComboBox()
        for key, value in self.LOG_TYPES.items():
            self.type_filter.addItem(value, key)
        self.type_filter.currentIndexChanged.connect(self.load_logs)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addWidget(QLabel("开始日期:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        filter_layout.addWidget(self.start_date)
        
        filter_layout.addWidget(QLabel("结束日期:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date)
        
        self.filter_btn = QPushButton("🔍 筛选")
        self.filter_btn.clicked.connect(self.load_logs)
        filter_layout.addWidget(self.filter_btn)
        
        self.reset_btn = QPushButton("重置")
        self.reset_btn.clicked.connect(self.reset_filters)
        filter_layout.addWidget(self.reset_btn)
        
        filter_layout.addStretch()
        
        self.export_btn = QPushButton("📥 导出日志")
        self.export_btn.clicked.connect(self.export_logs)
        filter_layout.addWidget(self.export_btn)
        
        layout.addWidget(filter_widget)
        
        # 日志表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "时间", "操作类型", "操作对象", "详情", "ID"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(4, 50)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e8e8e8;
            }
            QTableWidget::item:selected {
                background-color: #e6f7ff;
            }
        """)
        
        layout.addWidget(self.table)
        
        # 统计信息
        self.stats_label = QLabel("共 0 条日志")
        self.stats_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.stats_label)
    
    def load_logs(self):
        """加载日志"""
        log_type = self.type_filter.currentData()
        
        # 获取日志
        logs = db.get_logs(limit=500)
        
        # 按类型过滤
        if log_type != 'all':
            logs = [log for log in logs if log['operation_type'] == log_type]
        
        # 按日期过滤
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        
        filtered_logs = []
        for log in logs:
            try:
                time_str = str(log['operation_time'])
                if 'T' in time_str:
                    log_date = datetime.fromisoformat(time_str.replace('Z', '+00:00')).date()
                else:
                    log_date = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S').date()
                if start <= log_date <= end:
                    filtered_logs.append(log)
            except Exception:
                continue
        
        self.display_logs(filtered_logs)
    
    def display_logs(self, logs):
        """显示日志"""
        self.table.setRowCount(len(logs))
        
        # 类型颜色映射
        type_colors = {
            'import': '#52c41a',
            'delete': '#ff4d4f',
            'backup': '#1890ff',
            'restore': '#faad14',
            'rearchive': '#722ed1'
        }
        
        for i, log in enumerate(logs):
            # 时间
            time_str = str(log['operation_time'])[:19]
            time_item = QTableWidgetItem(time_str)
            time_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, time_item)
            
            # 操作类型
            type_text = self.LOG_TYPES.get(log['operation_type'], log['operation_type'])
            type_item = QTableWidgetItem(type_text)
            type_item.setTextAlignment(Qt.AlignCenter)
            
            # 设置颜色
            color = type_colors.get(log['operation_type'], '#666')
            type_item.setForeground(QColor(color))
            type_item.setFont(type_item.font())
            type_item.font().setBold(True)
            self.table.setItem(i, 1, type_item)
            
            # 操作对象
            target_item = QTableWidgetItem(log['operation_target'] or '-')
            self.table.setItem(i, 2, target_item)
            
            # 详情
            detail_item = QTableWidgetItem(log['operation_detail'] or '-')
            detail_item.setToolTip(log['operation_detail'] or '')
            self.table.setItem(i, 3, detail_item)
            
            # ID
            id_item = QTableWidgetItem(str(log['id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 4, id_item)
        
        self.stats_label.setText(f"共 {len(logs)} 条日志")
    
    def reset_filters(self):
        """重置筛选"""
        self.type_filter.setCurrentIndex(0)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.end_date.setDate(QDate.currentDate())
        self.load_logs()
    
    def export_logs(self):
        """导出日志"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出日志",
            f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "文本文件 (*.txt);;CSV文件 (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            logs = db.get_logs(limit=1000)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("操作日志导出\n")
                f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                for log in logs:
                    f.write(f"[{log['operation_time']}] ")
                    f.write(f"{self.LOG_TYPES.get(log['operation_type'], log['operation_type'])} - ")
                    f.write(f"{log['operation_target'] or 'N/A'}\n")
                    if log['operation_detail']:
                        f.write(f"  详情: {log['operation_detail']}\n")
                    f.write("\n")
            
            QMessageBox.information(self, "成功", f"日志已导出到:\n{file_path}")
            
        except Exception as e:
            QMessageBox.warning(self, "失败", f"导出失败: {e}")
