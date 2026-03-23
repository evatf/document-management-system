import os
import shutil
from pathlib import Path
from datetime import datetime

from core.database import db
from core.config import config
from core.document_parser import DocumentParser, ArchiveAnalyzer


class DocumentImporter:
    """文档导入器"""
    
    SUPPORTED_EXTENSIONS = ['.docx', '.pdf', '.txt', '.xlsx', '.xls']
    
    def __init__(self):
        self.storage_path = Path(config.get('general.default_storage_path'))
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def import_file(self, file_path, auto_archive=True, category_id=None, tags=None):
        """导入单个文件
        
        Args:
            file_path: 源文件路径
            auto_archive: 是否自动归档
            category_id: 指定分类ID
            tags: 标签列表
            
        Returns:
            dict: 导入结果
        """
        file_path = Path(file_path)
        
        # 检查文件是否存在
        if not file_path.exists():
            return {'success': False, 'error': '文件不存在'}
        
        # 检查文件类型
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return {'success': False, 'error': f'不支持的文件类型: {file_path.suffix}'}
        
        try:
            # 获取文件信息
            file_info = DocumentParser.get_file_info(str(file_path))
            
            # 解析文档内容
            content_text, metadata = DocumentParser.parse(str(file_path))
            
            # 自动归档分析
            archive_info = {}
            if auto_archive:
                archive_info = ArchiveAnalyzer.analyze(str(file_path), content_text)
            
            # 确定存储路径
            target_path = self._get_target_path(file_path, archive_info)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件到存储目录
            if not target_path.exists():
                shutil.copy2(file_path, target_path)
            else:
                # 文件已存在，添加序号
                target_path = self._get_unique_path(target_path)
                shutil.copy2(file_path, target_path)
            
            # 确定分类
            final_category_id = category_id
            if final_category_id is None and auto_archive and archive_info.get('document_type'):
                final_category_id = self._get_category_id_by_name(archive_info['document_type'])
            
            # 添加到数据库
            doc_id = db.add_document(
                title=metadata.get('title') or file_path.stem,
                file_path=str(target_path),
                file_type=file_info['file_type'],
                file_size=file_info['file_size'],
                content_text=content_text,
                create_date=metadata.get('created') or datetime.fromtimestamp(file_path.stat().st_ctime),
                category_id=final_category_id,
                year=archive_info.get('year'),
                author=metadata.get('author'),
                source=str(file_path.parent),
                notes=None
            )
            
            # 添加标签
            if tags:
                for tag_name in tags:
                    tag_id = self._get_or_create_tag(tag_name)
                    db.add_document_tag(doc_id, tag_id)
            
            # 记录日志
            db.add_log('import', str(file_path), f'导入文档: {file_path.name}')
            
            return {
                'success': True,
                'document_id': doc_id,
                'file_path': str(target_path),
                'archive_info': archive_info
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def import_folder(self, folder_path, recursive=True, auto_archive=True, 
                      progress_callback=None):
        """批量导入文件夹
        
        Args:
            folder_path: 文件夹路径
            recursive: 是否递归子文件夹
            auto_archive: 是否自动归档
            progress_callback: 进度回调函数(current, total, file_name)
            
        Returns:
            dict: 导入统计结果
        """
        folder_path = Path(folder_path)
        
        if not folder_path.exists():
            return {'success': False, 'error': '文件夹不存在'}
        
        # 收集所有支持的文件
        files = []
        pattern = '**/*' if recursive else '*'
        for file_path in folder_path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                files.append(file_path)
        
        total = len(files)
        success_count = 0
        failed_count = 0
        failed_files = []
        
        for i, file_path in enumerate(files):
            if progress_callback:
                progress_callback(i + 1, total, file_path.name)
            
            result = self.import_file(file_path, auto_archive=auto_archive)
            if result['success']:
                success_count += 1
            else:
                failed_count += 1
                failed_files.append({
                    'file': str(file_path),
                    'error': result['error']
                })
        
        return {
            'success': True,
            'total': total,
            'success_count': success_count,
            'failed_count': failed_count,
            'failed_files': failed_files
        }
    
    def _get_target_path(self, source_path, archive_info):
        """根据归档信息确定目标路径"""
        year = archive_info.get('year')
        doc_type = archive_info.get('document_type')
        
        # 构建路径: storage/year/type/filename
        target_dir = self.storage_path
        
        if year:
            target_dir = target_dir / str(year)
        
        if doc_type:
            # 清理类型名称，确保可作为文件夹名
            safe_type = ''.join(c for c in doc_type if c.isalnum() or c in '_- ')
            target_dir = target_dir / safe_type
        
        return target_dir / source_path.name
    
    def _get_unique_path(self, path):
        """获取唯一的文件路径（避免覆盖）"""
        if not path.exists():
            return path
        
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1
        
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1
    
    def _get_category_id_by_name(self, name):
        """根据分类名称获取ID"""
        categories = db.get_categories()
        for cat in categories:
            if cat['name'] == name:
                return cat['id']
        return None
    
    def _get_or_create_tag(self, tag_name):
        """获取或创建标签"""
        tags = db.get_tags()
        for tag in tags:
            if tag['name'] == tag_name:
                return tag['id']
        return db.add_tag(tag_name)


class ArchiveManager:
    """归档管理器"""
    
    def __init__(self):
        self.storage_path = Path(config.get('general.default_storage_path'))
    
    def rearchive_document(self, document_id, new_year=None, new_category_id=None):
        """重新归档文档
        
        Args:
            document_id: 文档ID
            new_year: 新年份
            new_category_id: 新分类ID
            
        Returns:
            bool: 是否成功
        """
        doc = db.get_document(document_id)
        if not doc:
            return False
        
        old_path = Path(doc['file_path'])
        
        # 构建新路径
        target_dir = self.storage_path
        
        year = new_year or doc['year']
        if year:
            target_dir = target_dir / str(year)
        
        if new_category_id:
            category = self._get_category_by_id(new_category_id)
            if category:
                safe_name = ''.join(c for c in category['name'] if c.isalnum() or c in '_- ')
                target_dir = target_dir / safe_name
        
        new_path = target_dir / old_path.name
        
        # 确保目标目录存在
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 如果路径相同，无需移动
        if old_path == new_path:
            db.update_document(document_id, year=year, category_id=new_category_id)
            return True
        
        # 处理文件名冲突
        if new_path.exists():
            new_path = self._get_unique_path(new_path)
        
        try:
            # 移动文件
            shutil.move(str(old_path), str(new_path))
            
            # 更新数据库
            db.update_document(document_id, 
                             file_path=str(new_path),
                             year=year,
                             category_id=new_category_id)
            
            db.add_log('rearchive', str(new_path), f'重新归档: {old_path} -> {new_path}')
            return True
            
        except Exception as e:
            print(f"重新归档失败: {e}")
            return False
    
    def batch_rearchive(self, document_ids, new_year=None, new_category_id=None):
        """批量重新归档
        
        Args:
            document_ids: 文档ID列表
            new_year: 新年份
            new_category_id: 新分类ID
            
        Returns:
            dict: 操作结果统计
        """
        success_count = 0
        failed_count = 0
        
        for doc_id in document_ids:
            if self.rearchive_document(doc_id, new_year, new_category_id):
                success_count += 1
            else:
                failed_count += 1
        
        return {
            'success': True,
            'total': len(document_ids),
            'success_count': success_count,
            'failed_count': failed_count
        }
    
    def get_storage_stats(self):
        """获取存储统计信息"""
        stats = {
            'total_size': 0,
            'total_files': 0,
            'type_distribution': {},
            'year_distribution': {}
        }
        
        if not self.storage_path.exists():
            return stats
        
        for file_path in self.storage_path.rglob('*'):
            if file_path.is_file():
                stats['total_files'] += 1
                stats['total_size'] += file_path.stat().st_size
                
                # 文件类型统计
                ext = file_path.suffix.lower()
                stats['type_distribution'][ext] = stats['type_distribution'].get(ext, 0) + 1
        
        # 年份统计从数据库获取
        documents = db.get_all_documents()
        for doc in documents:
            year = doc.get('year')
            if year:
                stats['year_distribution'][year] = stats['year_distribution'].get(year, 0) + 1
        
        return stats
    
    def _get_category_by_id(self, category_id):
        """根据ID获取分类信息"""
        categories = db.get_categories()
        for cat in categories:
            if cat['id'] == category_id:
                return cat
        return None
    
    def _get_unique_path(self, path):
        """获取唯一的文件路径"""
        if not path.exists():
            return path
        
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1
        
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1


class RecycleBinManager:
    """回收站管理器"""
    
    def __init__(self):
        self.storage_path = Path(config.get('general.default_storage_path'))
        self.recycle_path = self.storage_path / '.recycle_bin'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.recycle_path.mkdir(exist_ok=True)
    
    def move_to_recycle(self, document_id, expire_days=30):
        """将文档移入回收站
        
        Args:
            document_id: 文档ID
            expire_days: 过期天数
            
        Returns:
            bool: 是否成功
        """
        doc = db.get_document(document_id)
        if not doc:
            return False
        
        try:
            from datetime import timedelta
            
            old_path = Path(doc['file_path'])
            new_path = self.recycle_path / old_path.name
            
            # 处理文件名冲突
            if new_path.exists():
                new_path = self._get_unique_path(new_path)
            
            # 移动文件
            shutil.move(str(old_path), str(new_path))
            
            # 计算过期日期
            expire_date = datetime.now() + timedelta(days=expire_days)
            
            # 添加到回收站表
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO recycle_bin (document_id, original_category_id, expire_date)
                VALUES (?, ?, ?)
            ''', (document_id, doc['category_id'], expire_date.date()))
            conn.commit()
            conn.close()
            
            # 记录日志
            db.add_log('delete', doc['title'], f'移入回收站: {old_path.name}')
            
            return True
            
        except Exception as e:
            print(f"移入回收站失败: {e}")
            return False
    
    def restore_from_recycle(self, recycle_id):
        """从回收站恢复文档
        
        Args:
            recycle_id: 回收站记录ID
            
        Returns:
            bool: 是否成功
        """
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM recycle_bin WHERE id = ?', (recycle_id,))
        record = cursor.fetchone()
        
        if not record:
            conn.close()
            return False
        
        record = dict(record)
        doc = db.get_document(record['document_id'])
        
        if not doc:
            conn.close()
            return False
        
        try:
            # 查找回收站中的文件
            file_name = Path(doc['file_path']).name
            recycle_file = self.recycle_path / file_name
            
            if not recycle_file.exists():
                conn.close()
                return False
            
            # 恢复到原路径
            original_path = Path(doc['file_path'])
            original_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(recycle_file), str(original_path))
            
            # 删除回收站记录
            cursor.execute('DELETE FROM recycle_bin WHERE id = ?', (recycle_id,))
            conn.commit()
            conn.close()
            
            # 记录日志
            db.add_log('restore', doc['title'], f'从回收站恢复: {file_name}')
            
            return True
            
        except Exception as e:
            print(f"恢复失败: {e}")
            conn.close()
            return False
    
    def permanently_delete(self, recycle_id):
        """永久删除文档
        
        Args:
            recycle_id: 回收站记录ID
            
        Returns:
            bool: 是否成功
        """
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM recycle_bin WHERE id = ?', (recycle_id,))
        record = cursor.fetchone()
        
        if not record:
            conn.close()
            return False
        
        record = dict(record)
        doc = db.get_document(record['document_id'])
        
        try:
            # 删除文件
            if doc:
                file_name = Path(doc['file_path']).name
                recycle_file = self.recycle_path / file_name
                if recycle_file.exists():
                    recycle_file.unlink()
            
            # 删除数据库记录
            cursor.execute('DELETE FROM recycle_bin WHERE id = ?', (recycle_id,))
            cursor.execute('DELETE FROM documents WHERE id = ?', (record['document_id'],))
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"永久删除失败: {e}")
            conn.close()
            return False
    
    def get_recycle_items(self):
        """获取回收站中的所有项目"""
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT rb.*, d.title, d.file_path, d.file_type
            FROM recycle_bin rb
            JOIN documents d ON rb.document_id = d.id
            ORDER BY rb.deleted_date DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def clean_expired(self):
        """清理过期的回收站项目"""
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM recycle_bin WHERE expire_date < date('now')
        ''')
        
        expired = cursor.fetchall()
        
        for record in expired:
            self.permanently_delete(record['id'])
        
        conn.close()
        
        return len(expired)
    
    def _get_unique_path(self, path):
        """获取唯一的文件路径"""
        if not path.exists():
            return path
        
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1
        
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1


# 便捷函数
def import_file(file_path, **kwargs):
    """导入单个文件的便捷函数"""
    importer = DocumentImporter()
    return importer.import_file(file_path, **kwargs)


def import_folder(folder_path, **kwargs):
    """批量导入文件夹的便捷函数"""
    importer = DocumentImporter()
    return importer.import_folder(folder_path, **kwargs)
