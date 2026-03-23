# 材料管理系统 - 统信UOS安装运行指南

## 📋 准备工作

### 1. 确认系统信息
打开终端，输入以下命令查看系统架构：
```bash
uname -m
```

可能的输出：
- `x86_64` - Intel/AMD处理器（最常见）
- `aarch64` - ARM处理器（如华为鲲鹏）
- `mips64` - 龙芯处理器

### 2. 准备文件
将项目文件夹复制到UOS电脑，建议位置：`/home/你的用户名/文档/`

---

## 🚀 方法一：源码运行（推荐开发/测试使用）

### 步骤1：安装系统依赖

打开终端（按 `Ctrl + Alt + T`），依次执行：

```bash
# 更新软件源
sudo apt update

# 安装Python3和pip
sudo apt install -y python3 python3-pip python3-venv

# 安装PyQt5（UOS软件仓库版本）
sudo apt install -y python3-pyqt5 python3-pyqt5.qtwebkit

# 安装编译依赖（某些Python包需要）
sudo apt install -y python3-dev build-essential libffi-dev

# 安装中文字体（重要！避免乱码）
sudo apt install -y fonts-wqy-zenhei fonts-wqy-microhei fonts-noto-cjk

# 刷新字体缓存
fc-cache -fv
```

### 步骤2：进入项目目录

```bash
# 进入项目文件夹（根据实际路径修改）
cd /home/你的用户名/文档/Document\ Management\ System

# 或者如果你放在桌面
cd ~/Desktop/Document\ Management\ System
```

### 步骤3：创建Python虚拟环境（推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 你会看到命令行前面出现 (venv) 字样，表示已激活
```

### 步骤4：安装Python依赖

```bash
# 先升级pip
pip install --upgrade pip

# 安装依赖（使用国内镜像加速）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**如果遇到某个包安装失败**，可以单独安装：
```bash
# 例如PyMuPDF安装失败
pip install PyMuPDF==1.21.0 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或者使用apt安装
sudo apt install python3-fitz  # PyMuPDF在UOS中的包名
```

### 步骤5：修改字体配置（UOS专用）

编辑 `main.py` 文件，修改字体设置：

```bash
# 使用文本编辑器打开
nano main.py
# 或者用图形编辑器
dde-file-manager main.py  # 用文件管理器打开
```

找到第22-29行的 `get_system_font()` 函数，修改为：

```python
def get_system_font():
    """获取跨平台系统字体"""
    if sys.platform == 'win32':
        return "Microsoft YaHei"
    elif sys.platform == 'darwin':
        return "PingFang SC"
    else:
        # UOS/Linux 使用文泉驿字体
        return "WenQuanYi Zen Hei"  # 或者 "Noto Sans CJK SC"
```

保存文件。

### 步骤6：运行程序

```bash
# 确保在虚拟环境中（看到前面的venv字样）
python main.py
```

程序启动后，你会看到：
- 数据目录自动创建在：`~/.document_manager/`
- 配置文件自动生成
- 数据库自动初始化

---

## 📦 方法二：打包为可执行文件（推荐最终用户使用）

### 步骤1：安装PyInstaller

```bash
# 在虚拟环境中
pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步骤2：创建打包脚本

创建文件 `build_uos.sh`：

```bash
#!/bin/bash

# 激活虚拟环境
source venv/bin/activate

# 清理旧构建
rm -rf build dist

# 打包程序
pyinstaller \
    --name="材料管理系统" \
    --onefile \
    --windowed \
    --icon=icon.png \
    --add-data="resources:resources" \
    --hidden-import=PyQt5.sip \
    --hidden-import=sqlite3 \
    main.py

echo "打包完成！可执行文件在 dist/ 目录"
```

### 步骤3：执行打包

```bash
chmod +x build_uos.sh
./build_uos.sh
```

等待几分钟，打包完成后，在 `dist/` 目录下会生成 `材料管理系统` 可执行文件。

### 步骤4：分发和运行

1. **复制文件**：将 `dist/材料管理系统` 复制到目标电脑
2. **设置权限**：
   ```bash
   chmod +x 材料管理系统
   ```
3. **运行**：
   ```bash
   ./材料管理系统
   ```

---

## 🔧 常见问题解决

### 问题1：提示 "ModuleNotFoundError: No module named 'PyQt5'"

**解决方法**：
```bash
# 方法A：使用apt安装
sudo apt install python3-pyqt5

# 方法B：使用pip安装（在虚拟环境中）
pip install PyQt5==5.15.9
```

### 问题2：界面显示乱码或方块字

**解决方法**：
```bash
# 安装中文字体
sudo apt install fonts-wqy-zenhei fonts-wqy-microhei fonts-noto-cjk

# 刷新字体缓存
fc-cache -fv

# 重启程序
```

### 问题3：提示 "Permission denied"

**解决方法**：
```bash
# 给程序添加执行权限
chmod +x main.py

# 或者用Python直接运行
python3 main.py
```

### 问题4：PyMuPDF (fitz) 安装失败

**解决方法**：
```bash
# 方法A：安装系统依赖后再试
sudo apt install libxml2-dev libxslt1-dev
pip install PyMuPDF==1.21.0

# 方法B：使用UOS仓库的版本
sudo apt install python3-fitz
```

### 问题5：wordcloud 安装失败

**解决方法**：
```bash
# 安装编译依赖
sudo apt install gcc g++ python3-dev

# 再安装wordcloud
pip install wordcloud==1.8.1
```

### 问题6：程序启动后闪退

**排查方法**：
```bash
# 终端运行查看错误信息
python main.py 2>&1 | tee error.log

# 查看日志文件
cat ~/.document_manager/logs/*.log
```

常见原因：
- 缺少字体 → 安装中文字体
- 权限问题 → 检查目录权限
- 依赖缺失 → 重新安装requirements

---

## 📁 数据目录说明

程序数据存储在用户主目录下，与程序文件分离：

```
/home/你的用户名/.document_manager/
├── database.db           # SQLite数据库（文档、金句等数据）
├── config/
│   ├── settings.json     # 用户配置
│   └── rules.json        # 归档规则
├── documents/            # 导入的文档文件
│   └── 2024/
│       └── 通知/
│           └── xxx.docx
├── backups/              # 自动备份文件
│   └── backup_20240101_120000/
│       ├── database.db
│       └── config/
└── logs/                 # 运行日志
    └── app_20240101.log
```

**备份数据**：只需复制整个 `.document_manager` 文件夹

**迁移数据**：将旧电脑的 `.document_manager` 文件夹复制到新电脑相同位置

---

## 🎯 快速启动脚本

创建桌面快捷方式：

```bash
# 创建启动脚本
cat > ~/材料管理系统.sh << 'EOF'
#!/bin/bash
cd /home/你的用户名/文档/Document\ Management\ System
source venv/bin/activate
python main.py
EOF

chmod +x ~/材料管理系统.sh

# 创建桌面快捷方式（UOS桌面环境）
cat > ~/Desktop/材料管理系统.desktop << EOF
[Desktop Entry]
Name=材料管理系统
Comment=党政机关材料管理软件
Exec=/home/你的用户名/材料管理系统.sh
Icon=/home/你的用户名/文档/Document\ Management\ System/icon.png
Type=Application
Terminal=false
Categories=Office;
EOF

chmod +x ~/Desktop/材料管理系统.desktop
```

---

## ✅ 安装检查清单

安装完成后，请确认：

- [ ] Python3和pip已安装
- [ ] 虚拟环境创建成功
- [ ] 所有依赖安装完成（pip list查看）
- [ ] 中文字体已安装
- [ ] 程序能正常启动
- [ ] 界面显示正常（无乱码）
- [ ] 能导入文档
- [ ] 能搜索文档
- [ ] 能创建备份

---

## 📞 技术支持

如果遇到问题：

1. **查看日志**：`~/.document_manager/logs/`
2. **检查环境**：
   ```bash
   python3 --version
   pip list | grep -i pyqt
   fc-list :lang=zh  # 查看已安装的中文字体
   ```
3. **重新安装依赖**：
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

---

**祝你使用愉快！** 🎉
