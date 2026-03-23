# 统信UOS兼容性检查清单

## 开发环境
- **目标平台**: 统信UOS (Debian/Ubuntu-based Linux发行版)
- **Python版本**: 3.7.3 (UOS默认版本)
- **架构**: x86_64 / aarch64 (龙芯/飞腾)

## 已完成的兼容性措施

### 1. 路径处理
- ✅ 使用 `pathlib.Path` 替代字符串路径操作
- ✅ 使用 `/` 作为路径分隔符（pathlib自动处理）
- ✅ 配置文件路径使用 `Path.home()` 相对路径

### 2. 文件编码
- ✅ 所有文件操作使用 `UTF-8` 编码
- ✅ 文本文件打开时显式指定 `encoding='utf-8'`

### 3. 依赖库选择
- ✅ PyQt5 5.15.9 - UOS软件仓库可用
- ✅ python-docx - 纯Python，跨平台
- ✅ PyMuPDF - 支持Linux
- ✅ openpyxl - 纯Python，跨平台
- ✅ jieba - 纯Python，跨平台
- ✅ snownlp - 纯Python，跨平台

### 4. 数据库
- ✅ SQLite3 - Python内置，无需额外安装
- ✅ 单文件数据库，便于备份和迁移

### 5. 字体处理
- ✅ 默认使用 "Microsoft YaHei"（Windows）
- ✅ 备选字体 "SimHei" / "Noto Sans CJK SC"（Linux）
- ✅ 代码中字体设置支持回退机制

## UOS部署注意事项

### 安装依赖
```bash
# 更新软件源
sudo apt update

# 安装Python3和pip
sudo apt install python3 python3-pip

# 安装PyQt5（UOS软件仓库）
sudo apt install python3-pyqt5

# 安装其他系统依赖
sudo apt install python3-dev build-essential
```

### 字体配置
如果UOS上没有微软雅黑字体，建议：
1. 安装文泉驿字体：`sudo apt install fonts-wqy-zenhei`
2. 修改 `main.py` 中的字体设置：
   ```python
   font = QFont("WenQuanYi Zen Hei", 10)  # UOS可用
   ```

### 文件权限
- 数据目录需要读写权限
- 建议将数据存储在用户主目录下：`~/.document_manager/`

### 打包发布
使用 `PyInstaller` 打包为独立可执行文件：
```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

## 测试检查项

- [ ] 文档导入功能正常
- [ ] 全文搜索功能正常
- [ ] 词频分析功能正常
- [ ] 数据备份/恢复功能正常
- [ ] 界面显示正常（无乱码）
- [ ] 文件路径处理正确
- [ ] 自动备份调度器运行正常

## 已知限制

1. **词云生成**: wordcloud库在UOS上可能需要额外字体配置
2. **PDF解析**: 某些PDF可能需要额外的编码支持
3. **打印功能**: 需要系统配置正确的打印机

## 推荐配置

### 最小系统要求
- CPU: 双核 2.0GHz
- 内存: 4GB RAM
- 硬盘: 10GB 可用空间
- 显示器: 1280x720 分辨率

### 推荐系统要求
- CPU: 四核 2.5GHz
- 内存: 8GB RAM
- 硬盘: 50GB SSD
- 显示器: 1920x1080 分辨率
