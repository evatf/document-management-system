import sqlite3
from datetime import datetime
from pathlib import Path
import os


def get_data_dir():
    """获取数据目录（兼容打包后的环境）"""
    # 优先使用环境变量
    if 'DOCUMENT_MANAGER_DATA' in os.environ:
        return Path(os.environ['DOCUMENT_MANAGER_DATA'])
    
    # 用户目录下的应用数据目录
    if os.name == 'nt':  # Windows
        data_dir = Path(os.environ.get('APPDATA', Path.home())) / 'document_manager'
    else:  # Linux/Mac
        data_dir = Path.home() / '.document_manager'
    
    return data_dir


class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            data_dir = get_data_dir()
            db_path = data_dir / "database.db"
        self.db_path = str(db_path)
        self._ensure_data_dir()
        self.init_database()
    
    def _ensure_data_dir(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 文档表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT,
                file_size INTEGER,
                content_text TEXT,
                create_date DATE,
                import_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                category_id INTEGER,
                year INTEGER,
                author TEXT,
                source TEXT,
                notes TEXT,
                is_starred INTEGER DEFAULT 0,
                folder_path TEXT DEFAULT '未分类',
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        
        # 分类表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_id INTEGER,
                type TEXT DEFAULT 'custom',
                sort_order INTEGER DEFAULT 0,
                FOREIGN KEY (parent_id) REFERENCES categories(id)
            )
        ''')
        
        # 标签表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                color TEXT DEFAULT '#3498db'
            )
        ''')
        
        # 文档-标签关联表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_tags (
                document_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (document_id, tag_id),
                FOREIGN KEY (document_id) REFERENCES documents(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id)
            )
        ''')
        
        # 收藏表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                folder TEXT DEFAULT 'default',
                added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        ''')
        
        # 金句表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                source_document_id INTEGER,
                source_text TEXT,
                category TEXT,
                tags TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (source_document_id) REFERENCES documents(id)
            )
        ''')
        
        # 回收站表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recycle_bin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                original_category_id INTEGER,
                deleted_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                expire_date DATE,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        ''')
        
        # 备份记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_path TEXT NOT NULL,
                backup_size INTEGER,
                backup_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                backup_type TEXT DEFAULT 'manual',
                note TEXT
            )
        ''')
        
        # 文件夹表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_id INTEGER,
                sort_order INTEGER DEFAULT 0,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES folders(id)
            )
        ''')
        
        # 自定义词典表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_dictionary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                frequency INTEGER DEFAULT 10,
                pos_tag TEXT,
                category TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 操作日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,
                operation_target TEXT,
                operation_detail TEXT,
                operation_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 插入默认分类
        cursor.execute('''
            INSERT OR IGNORE INTO categories (id, name, type, sort_order) VALUES 
            (1, '通知', 'system', 1),
            (2, '决定', 'system', 2),
            (3, '报告', 'system', 3),
            (4, '请示', 'system', 4),
            (5, '批复', 'system', 5),
            (6, '函', 'system', 6),
            (7, '会议纪要', 'system', 7),
            (8, '其他', 'system', 99)
        ''')
        
        # 数据库迁移：检查并添加缺失的列
        self._migrate_database(cursor)
        
        conn.commit()
        conn.close()
    
    def _migrate_database(self, cursor):
        """数据库迁移：添加缺失的列"""
        # 检查 documents 表是否有 folder_path 列
        cursor.execute("PRAGMA table_info(documents)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'folder_path' not in columns:
            cursor.execute("ALTER TABLE documents ADD COLUMN folder_path TEXT DEFAULT '未分类'")
    
    # 文档相关操作
    def add_document(self, title, file_path, file_type=None, file_size=None, 
                     content_text=None, create_date=None, category_id=None, 
                     year=None, author=None, source=None, notes=None, folder_path=None):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO documents (title, file_path, file_type, file_size, content_text,
                                       create_date, category_id, year, author, source, notes, folder_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, file_path, file_type, file_size, content_text, 
                  create_date, category_id, year, author, source, notes, folder_path))
            doc_id = cursor.lastrowid
            conn.commit()
            return doc_id
        finally:
            conn.close()
    
    def get_document(self, doc_id):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        finally:
            conn.close()
    
    def get_all_documents(self, limit=None, offset=None):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            sql = 'SELECT * FROM documents ORDER BY import_date DESC'
            if limit is not None:
                if not isinstance(limit, int) or limit < 0:
                    raise ValueError("limit must be a non-negative integer")
                sql += f' LIMIT {limit}'
            if offset is not None:
                if not isinstance(offset, int) or offset < 0:
                    raise ValueError("offset must be a non-negative integer")
                sql += f' OFFSET {offset}'
            cursor.execute(sql)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        finally:
            conn.close()
    
    def update_document(self, doc_id, **kwargs):
        if not kwargs:
            return
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            fields = []
            values = []
            for key, value in kwargs.items():
                fields.append(f'{key} = ?')
                values.append(value)
            values.append(doc_id)
            cursor.execute(f"UPDATE documents SET {', '.join(fields)} WHERE id = ?", values)
            conn.commit()
        finally:
            conn.close()
    
    def delete_document(self, doc_id):
        """删除文档（包括物理文件）"""
        import os
        
        # 先获取文档信息
        doc = self.get_document(doc_id)
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            # 删除关联的标签
            cursor.execute('DELETE FROM document_tags WHERE document_id = ?', (doc_id,))
            # 删除关联的收藏
            cursor.execute('DELETE FROM favorites WHERE document_id = ?', (doc_id,))
            # 删除文档记录
            cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
            conn.commit()
        finally:
            conn.close()
        
        # 删除物理文件
        if doc and doc.get('file_path'):
            try:
                file_path = doc['file_path']
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"删除物理文件失败: {e}")
    
    def search_documents(self, keyword=None, category_id=None, year=None, 
                        author=None, tag_ids=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        if keyword:
            conditions.append('(title LIKE ? OR content_text LIKE ?)')
            params.extend([f'%{keyword}%', f'%{keyword}%'])
        if category_id:
            conditions.append('category_id = ?')
            params.append(category_id)
        if year:
            conditions.append('year = ?')
            params.append(year)
        if author:
            conditions.append('author LIKE ?')
            params.append(f'%{author}%')
        
        sql = 'SELECT * FROM documents'
        if conditions:
            sql += ' WHERE ' + ' AND '.join(conditions)
        sql += ' ORDER BY import_date DESC'
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    # 分类相关操作
    def get_categories(self, parent_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if parent_id is None:
            cursor.execute('SELECT * FROM categories WHERE parent_id IS NULL ORDER BY sort_order')
        else:
            cursor.execute('SELECT * FROM categories WHERE parent_id = ? ORDER BY sort_order', (parent_id,))
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    def add_category(self, name, parent_id=None, type='custom', sort_order=0):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO categories (name, parent_id, type, sort_order)
            VALUES (?, ?, ?, ?)
        ''', (name, parent_id, type, sort_order))
        cat_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return cat_id
    
    # 标签相关操作
    def get_tags(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tags ORDER BY name')
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    def add_tag(self, name, color='#3498db'):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tags (name, color) VALUES (?, ?)', (name, color))
        tag_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return tag_id
    
    def get_document_tags(self, document_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.* FROM tags t
            JOIN document_tags dt ON t.id = dt.tag_id
            WHERE dt.document_id = ?
        ''', (document_id,))
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    def add_document_tag(self, document_id, tag_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO document_tags (document_id, tag_id)
            VALUES (?, ?)
        ''', (document_id, tag_id))
        conn.commit()
        conn.close()
    
    # 收藏相关操作
    def add_favorite(self, document_id, folder='default', notes=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO favorites (document_id, folder, notes)
            VALUES (?, ?, ?)
        ''', (document_id, folder, notes))
        conn.commit()
        conn.close()
    
    def get_favorites(self, folder=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if folder:
            cursor.execute('SELECT * FROM favorites WHERE folder = ? ORDER BY added_date DESC', (folder,))
        else:
            cursor.execute('SELECT * FROM favorites ORDER BY added_date DESC')
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    # 金句相关操作
    def add_quote(self, content, source_document_id=None, source_text=None, 
                  category=None, tags=None, notes=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO quotes (content, source_document_id, source_text, category, tags, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (content, source_document_id, source_text, category, tags, notes))
        quote_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return quote_id
    
    def get_quotes(self, category=None, search_keyword=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        conditions = []
        params = []
        
        if category:
            conditions.append('category = ?')
            params.append(category)
        if search_keyword:
            conditions.append('content LIKE ?')
            params.append(f'%{search_keyword}%')
        
        sql = 'SELECT * FROM quotes'
        if conditions:
            sql += ' WHERE ' + ' AND '.join(conditions)
        sql += ' ORDER BY created_date DESC'
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    def get_quote(self, quote_id):
        """获取单个金句"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM quotes WHERE id = ?', (quote_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    
    # 日志操作
    def add_log(self, operation_type, operation_target=None, operation_detail=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO operation_logs (operation_type, operation_target, operation_detail)
            VALUES (?, ?, ?)
        ''', (operation_type, operation_target, operation_detail))
        conn.commit()
        conn.close()
    
    def get_logs(self, limit=100):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM operation_logs 
            ORDER BY operation_time DESC 
            LIMIT ?
        ''', (limit,))
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    # 文件夹操作
    def get_folders(self, parent_id=None):
        """获取文件夹列表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if parent_id is None:
            cursor.execute('SELECT * FROM folders WHERE parent_id IS NULL ORDER BY sort_order')
        else:
            cursor.execute('SELECT * FROM folders WHERE parent_id = ? ORDER BY sort_order', (parent_id,))
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    def add_folder(self, name, parent_id=None, sort_order=0):
        """添加文件夹"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO folders (name, parent_id, sort_order)
            VALUES (?, ?, ?)
        ''', (name, parent_id, sort_order))
        folder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return folder_id
    
    def delete_folder(self, folder_id):
        """删除文件夹"""
        conn = self.get_connection()
        cursor = conn.cursor()
        # 先删除子文件夹
        cursor.execute('DELETE FROM folders WHERE parent_id = ?', (folder_id,))
        # 再删除自身
        cursor.execute('DELETE FROM folders WHERE id = ?', (folder_id,))
        conn.commit()
        conn.close()
    
    def update_folder(self, folder_id, **kwargs):
        """更新文件夹"""
        if not kwargs:
            return
        conn = self.get_connection()
        cursor = conn.cursor()
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f'{key} = ?')
            values.append(value)
        values.append(folder_id)
        cursor.execute(f"UPDATE folders SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
        conn.close()
    
    # 备份相关操作
    def get_backups(self):
        """获取备份列表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM backups ORDER BY backup_date DESC')
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    def delete_backup(self, backup_id):
        """删除备份记录"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM backups WHERE id = ?', (backup_id,))
        conn.commit()
        conn.close()


# 全局数据库实例
db = Database()
