import json
from pathlib import Path
import os


def get_data_dir():
    """获取数据目录（兼容打包后的环境）"""
    if 'DOCUMENT_MANAGER_DATA' in os.environ:
        return Path(os.environ['DOCUMENT_MANAGER_DATA'])
    
    if os.name == 'nt':  # Windows
        appdata = os.environ.get('APPDATA', str(Path.home()))
        data_dir = Path(appdata) / 'document_manager'
    else:  # Linux/Mac
        data_dir = Path.home() / '.document_manager'
    
    return data_dir


class Config:
    def __init__(self):
        data_dir = get_data_dir()
        self.config_dir = data_dir / "config"
        self.config_file = self.config_dir / "settings.json"
        self.rules_file = self.config_dir / "rules.json"
        self._ensure_config_dir()
        self.settings = self._load_settings()
        self.rules = self._load_rules()
    
    def _ensure_config_dir(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_settings(self):
        data_dir = get_data_dir()
        default_settings = {
            "general": {
                "default_storage_path": str(data_dir / "documents"),
                "check_update_on_startup": False,
                "remember_window_size": True,
                "window_width": 1200,
                "window_height": 800,
                "sidebar_width": 200
            },
            "appearance": {
                "theme": "light",
                "font_size": "medium",
                "sidebar_width": 200
            },
            "backup": {
                "auto_backup": True,
                "backup_frequency": "daily",
                "backup_keep_count": 10,
                "backup_path": str(data_dir / "backups")
            },
            "archive": {
                "auto_recognize_year": True,
                "default_category_id": 8
            },
            "search": {
                "highlight_color": "#1890ff",
                "page_size": 50
            },
            "nlp": {
                "custom_dict_path": "",
                "stopwords_path": ""
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self._merge_config(default_settings, loaded)
                    return default_settings
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return default_settings
        return default_settings
    
    def _load_rules(self):
        default_rules = {
            "year_patterns": [
                r"(\d{4})年",
                r"(\d{4})[-/]",
                r"\[(\d{4})\]",
                r"\((\d{4})\)"
            ],
            "document_types": {
                "通知": ["通知", "通告", "通报"],
                "决定": ["决定", "决议"],
                "报告": ["报告", "汇报"],
                "请示": ["请示", "申请"],
                "批复": ["批复", "批示"],
                "函": ["函", "信函"],
                "会议纪要": ["纪要", "会议", "记录"]
            },
            "auto_archive_rules": [
                {
                    "name": "按年份归档",
                    "enabled": True,
                    "condition": "year_detected",
                    "action": "move_to_year_folder"
                },
                {
                    "name": "按类型归档",
                    "enabled": True,
                    "condition": "type_detected",
                    "action": "set_category"
                }
            ]
        }
        
        if self.rules_file.exists():
            try:
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self._merge_config(default_rules, loaded)
                    return default_rules
            except Exception as e:
                print(f"加载规则文件失败: {e}")
                return default_rules
        return default_rules
    
    def _merge_config(self, default, loaded):
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
    
    def save_settings(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def save_rules(self):
        try:
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(self.rules, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存规则失败: {e}")
            return False
    
    def get(self, key_path, default=None):
        keys = key_path.split('.')
        value = self.settings
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, key_path, value):
        keys = key_path.split('.')
        target = self.settings
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value
        return self.save_settings()
    
    def get_rule(self, key_path, default=None):
        keys = key_path.split('.')
        value = self.rules
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set_rule(self, key_path, value):
        keys = key_path.split('.')
        target = self.rules
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value
        return self.save_rules()


config = Config()
