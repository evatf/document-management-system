
from datetime import datetime
from PyQt5.QtCore import QTimer
from core.database import db
from core.config import config


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self):
        self.stats = {
            'start_time': datetime.now(),
            'import_count': 0,
            'search_count': 0,
            'backup_count': 0
        }
    
    def record_import(self, count=1):
        """记录导入数量"""
        self.stats['import_count'] += count
    
    def record_search(self):
        """记录搜索次数"""
        self.stats['search_count'] += 1
    
    def record_backup(self):
        """记录备份次数"""
        self.stats['backup_count'] += 1
    
    def get_stats(self):
        """获取统计信息"""
        uptime = datetime.now() - self.stats['start_time']
        
        return {
            'uptime': str(uptime).split('.')[0],
            'import_count': self.stats['import_count'],
            'search_count': self.stats['search_count'],
            'backup_count': self.stats['backup_count']
        }


# 全局调度器实例
system_monitor = SystemMonitor()
backup_timer = None


def start_schedulers():
    """启动所有调度器"""
    global backup_timer
    start_auto_backup()


def stop_schedulers():
    """停止所有调度器"""
    global backup_timer
    if backup_timer:
        backup_timer.stop()
        backup_timer = None


def start_auto_backup():
    """启动自动备份"""
    global backup_timer
    
    if not config.get('backup.auto_backup', True):
        return
    
    # 计算备份间隔（毫秒）
    frequency = config.get('backup.backup_frequency', 'daily')
    
    if frequency == 'daily':
        interval = 24 * 60 * 60 * 1000  # 24小时
    elif frequency == 'weekly':
        interval = 7 * 24 * 60 * 60 * 1000  # 7天
    elif frequency == 'monthly':
        interval = 30 * 24 * 60 * 60 * 1000  # 30天
    else:
        interval = 24 * 60 * 60 * 1000  # 默认24小时
    
    # 创建定时器
    if backup_timer is None:
        backup_timer = QTimer()
        backup_timer.timeout.connect(do_auto_backup)
    
    backup_timer.start(interval)
    print(f"自动备份已启动，间隔: {frequency}")


def restart_auto_backup():
    """重启自动备份"""
    stop_schedulers()
    start_schedulers()


def do_auto_backup():
    """执行自动备份"""
    try:
        from modules.settings import BackupManager
        backup_manager = BackupManager()
        result = backup_manager.create_backup(backup_type='auto')
        
        if result['success']:
            system_monitor.record_backup()
            print(f"自动备份成功: {result['backup_name']}")
            
            # 清理旧备份
            keep_count = config.get('backup.backup_keep_count', 10)
            clean_old_backups(keep_count)
        else:
            print(f"自动备份失败: {result.get('error', '未知错误')}")
    except Exception as e:
        print(f"自动备份异常: {e}")


def clean_old_backups(keep_count):
    """清理旧备份"""
    try:
        backups = db.get_backups()
        auto_backups = [b for b in backups if b.get('backup_type') == 'auto']
        
        if len(auto_backups) > keep_count:
            # 按日期排序，删除最旧的
            auto_backups.sort(key=lambda x: x['backup_date'], reverse=True)
            
            import os
            import shutil
            for backup in auto_backups[keep_count:]:
                try:
                    backup_path = backup.get('backup_path')
                    if backup_path and os.path.exists(backup_path):
                        shutil.rmtree(backup_path)
                    db.delete_backup(backup['id'])
                    print(f"已删除旧备份: {backup_path}")
                except Exception as e:
                    print(f"删除旧备份失败: {e}")
    except Exception as e:
        print(f"清理旧备份异常: {e}")
