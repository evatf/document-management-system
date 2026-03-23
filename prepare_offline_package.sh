#!/bin/bash
# 材料管理系统 - 离线部署包制作脚本
# 在联网的UOS/Debian/Ubuntu电脑上运行

set -e

echo "========================================"
echo "  材料管理系统 - 离线部署包制作"
echo "========================================"
echo ""

# 配置
PACKAGE_NAME="材料管理系统部署包"
PACKAGE_DIR="$HOME/$PACKAGE_NAME"
SOURCE_DIR="$(dirname "$(readlink -f "$0")")"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}[信息] 项目路径: $SOURCE_DIR${NC}"
echo -e "${GREEN}[信息] 输出路径: $PACKAGE_DIR${NC}"
echo ""

# 检查项目文件
if [ ! -f "$SOURCE_DIR/main.py" ]; then
    echo "[错误] 找不到 main.py，请确保在项目根目录运行此脚本"
    exit 1
fi

if [ ! -f "$SOURCE_DIR/requirements.txt" ]; then
    echo "[错误] 找不到 requirements.txt"
    exit 1
fi

# 清理旧文件
echo "[1/5] 清理旧文件..."
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# 创建目录结构
echo "[2/5] 创建目录结构..."
mkdir -p "$PACKAGE_DIR/source"
mkdir -p "$PACKAGE_DIR/packages"
mkdir -p "$PACKAGE_DIR/tools"

# 复制项目源码
echo "[3/5] 复制项目源码..."
cp -r "$SOURCE_DIR"/* "$PACKAGE_DIR/source/"

# 清理不需要的文件
cd "$PACKAGE_DIR/source"
rm -rf __pycache__ */__pycache__ .trae build dist
rm -f *.spec *.toc *.pkg *.pyz
rm -rf data/*.db data/*.bak

echo -e "${GREEN}[成功] 源码已复制${NC}"

# 下载依赖包
echo ""
echo "[4/5] 下载Python依赖包..."
echo "这可能需要几分钟，请耐心等待..."
echo ""

cd "$PACKAGE_DIR/packages"

# 使用pip download下载所有依赖
pip3 download -r "$SOURCE_DIR/requirements.txt" -i https://pypi.tuna.tsinghua.edu.cn/simple || {
    echo -e "${YELLOW}[警告] 使用清华镜像失败，尝试官方源...${NC}"
    pip3 download -r "$SOURCE_DIR/requirements.txt"
}

# 统计下载的包数量
PACKAGE_COUNT=$(ls -1 *.whl *.tar.gz 2>/dev/null | wc -l)
echo -e "${GREEN}[成功] 已下载 $PACKAGE_COUNT 个依赖包${NC}"

# 复制安装脚本
echo ""
echo "[5/5] 复制安装脚本..."
cd "$PACKAGE_DIR"

# 复制install.sh
if [ -f "$SOURCE_DIR/install.sh" ]; then
    cp "$SOURCE_DIR/install.sh" ./
    chmod +x install.sh
fi

# 创建README
cat > README.txt << 'EOF'
材料管理系统 - 离线部署包
==========================

适用系统：
  - 统信UOS（推荐）
  - 麒麟OS
  - Deepin
  - 其他Debian/Ubuntu-based Linux

目录说明：
  source/     - 项目源代码
  packages/   - Python依赖包（.whl文件）
  install.sh  - 一键安装脚本
  README.txt  - 本说明文件

安装步骤：
==========

1. 复制部署包到目标电脑
   - 使用U盘或内网文件传输
   - 复制整个文件夹到任意位置（如：/home/用户名/文档/）

2. 运行安装脚本
   - 打开终端（Ctrl + Alt + T）
   - 进入部署包目录：
     cd /path/to/材料管理系统部署包
   - 执行安装：
     ./install.sh

3. 等待安装完成
   - 安装过程约需5-10分钟
   - 需要管理员权限（sudo）
   - 会自动安装中文字体

4. 启动程序
   - 方式1：双击桌面图标
   - 方式2：终端运行：~/材料管理系统.sh

注意事项：
==========

1. 系统要求
   - Python 3.7+（UOS自带）
   - 管理员权限（sudo）
   - 至少500MB磁盘空间

2. 数据存储
   - 程序数据保存在：~/.document_manager/
   - 与程序文件分离，便于备份

3. 卸载方法
   - 删除安装目录：rm -rf ~/材料管理系统
   - 删除数据目录：rm -rf ~/.document_manager/
   - 删除桌面快捷方式：rm ~/Desktop/材料管理系统.desktop
   - 删除启动脚本：rm ~/材料管理系统.sh

4. 重新安装
   - 直接再次运行 ./install.sh 即可
   - 数据不会丢失（除非删除 ~/.document_manager/）

常见问题：
==========

Q: 提示权限不足？
A: 确保有sudo权限，或联系管理员

Q: 安装失败？
A: 查看错误信息，常见问题：
   - packages目录为空 → 重新下载依赖包
   - Python版本过低 → 升级Python3
   - 缺少系统库 → 运行 sudo apt update && sudo apt upgrade

Q: 如何更新程序？
A: 1. 备份数据（复制 ~/.document_manager/）
   2. 删除旧版本
   3. 重新安装新版本
   4. 恢复数据

技术支持：
==========

如有问题，请检查：
1. 系统日志：~/.document_manager/logs/
2. Python版本：python3 --version
3. 已安装包：pip3 list

EOF

# 创建快速启动脚本（用于部署后）
cat > "$PACKAGE_DIR/source/start.sh" << 'EOF'
#!/bin/bash
# 材料管理系统 - 快速启动脚本

cd "$(dirname "$0")"
source venv/bin/activate
python main.py "$@"
EOF

chmod +x "$PACKAGE_DIR/source/start.sh"

# 创建打包脚本（用于制作压缩包）
cat > "$PACKAGE_DIR/打包.bat" << 'EOF'
@echo off
chcp 65001 >nul
echo 正在创建压缩包...

:: 使用PowerShell压缩
powershell -Command "Compress-Archive -Path '%~dp0*' -DestinationPath '%USERPROFILE%\Desktop\材料管理系统部署包.zip' -Force"

echo.
echo 压缩包已创建在桌面：材料管理系统部署包.zip
echo.
pause
EOF

cat > "$PACKAGE_DIR/打包.sh" << 'EOF'
#!/bin/bash
# 创建压缩包

echo "正在创建压缩包..."

cd "$(dirname "$0")"
cd ..

tar czvf "$HOME/材料管理系统部署包.tar.gz" "$(basename "$PACKAGE_DIR")"

echo ""
echo "压缩包已创建: $HOME/材料管理系统部署包.tar.gz"
echo ""
EOF

chmod +x "$PACKAGE_DIR/打包.sh"

# 统计信息
echo ""
echo "========================================"
echo -e "${GREEN}  离线部署包制作完成！${NC}"
echo "========================================"
echo ""
echo "包信息："
echo "  位置: $PACKAGE_DIR"
echo "  大小: $(du -sh "$PACKAGE_DIR" | cut -f1)"
echo "  依赖包: $PACKAGE_COUNT 个"
echo ""
echo "部署包结构："
tree -L 2 "$PACKAGE_DIR" 2>/dev/null || find "$PACKAGE_DIR" -maxdepth 2 -type d

echo ""
echo "使用步骤："
echo "  1. 将整个文件夹复制到U盘"
echo "  2. 插入目标UOS电脑"
echo "  3. 复制到电脑任意位置"
echo "  4. 运行 ./install.sh"
echo ""
echo "可选操作："
echo "  - 创建zip压缩包（Windows）: 双击 打包.bat"
echo "  - 创建tar.gz压缩包（Linux）: ./打包.sh"
echo ""

# 询问是否创建压缩包
read -p "是否立即创建压缩包？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "正在创建压缩包..."
    cd "$(dirname "$PACKAGE_DIR")"
    tar czvf "$HOME/材料管理系统部署包.tar.gz" "$PACKAGE_NAME"
    echo -e "${GREEN}[成功] 压缩包已创建: $HOME/材料管理系统部署包.tar.gz${NC}"
    ls -lh "$HOME/材料管理系统部署包.tar.gz"
fi

echo ""
echo -e "${GREEN}完成！${NC}"
