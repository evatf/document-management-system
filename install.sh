#!/bin/bash
# 材料管理系统 - 离线安装脚本（统信UOS专用）
# 使用方法：./install.sh

set -e

echo "========================================"
echo "  材料管理系统 - 离线安装"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否在正确目录
if [ ! -f "source/main.py" ]; then
    echo -e "${RED}[错误] 找不到 source/main.py${NC}"
    echo "请确保在部署包根目录中运行此脚本"
    echo "正确路径示例：/home/用户名/材料管理系统部署包/"
    exit 1
fi

# 检查packages目录
if [ ! -d "packages" ]; then
    echo -e "${RED}[错误] 找不到 packages 目录${NC}"
    echo "请确保依赖包已复制到 packages/ 目录"
    exit 1
fi

# 检查系统
if [ ! -f /etc/os-release ]; then
    echo -e "${RED}[错误] 无法识别操作系统${NC}"
    exit 1
fi

source /etc/os-release
echo -e "${GREEN}[信息] 检测到系统：$NAME $VERSION${NC}"

# 检查Python3
echo ""
echo "[1/6] 检查Python3..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[错误] 未找到Python3${NC}"
    echo "正在尝试安装..."
    sudo apt update
    sudo apt install -y python3
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}[成功] Python版本: $PYTHON_VERSION${NC}"

# 安装系统依赖
echo ""
echo "[2/6] 安装系统依赖..."
sudo apt update
sudo apt install -y python3-venv python3-pip fonts-wqy-zenhei fonts-wqy-microhei fontconfig

# 刷新字体缓存
echo "[信息] 刷新字体缓存..."
fc-cache -fv > /dev/null 2>&1

# 创建安装目录
INSTALL_DIR="$HOME/材料管理系统"
echo ""
echo "[3/6] 创建安装目录: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# 复制源码
echo "[信息] 复制项目文件..."
cp -r source/* "$INSTALL_DIR/"

# 进入安装目录
cd "$INSTALL_DIR"

# 创建虚拟环境
echo ""
echo "[4/6] 创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 升级pip
echo "[信息] 升级pip..."
pip install --upgrade pip --quiet

# 离线安装依赖
echo ""
echo "[5/6] 安装Python依赖（离线模式）..."
echo "这可能需要几分钟，请耐心等待..."

PACKAGES_DIR="$(dirname "$INSTALL_DIR")/packages"
if [ ! -d "$PACKAGES_DIR" ]; then
    # 如果packages在上一级目录（部署包结构）
    PACKAGES_DIR="$(dirname "$(dirname "$INSTALL_DIR")")/packages"
fi

# 尝试找到packages目录
if [ -d "../packages" ]; then
    PACKAGES_DIR="$(realpath ../packages)"
elif [ -d "../../packages" ]; then
    PACKAGES_DIR="$(realpath ../../packages)"
fi

echo "[信息] 依赖包路径: $PACKAGES_DIR"

# 安装依赖
if pip install --no-index --find-links="$PACKAGES_DIR" -r requirements.txt; then
    echo -e "${GREEN}[成功] 依赖安装完成${NC}"
else
    echo -e "${YELLOW}[警告] 部分依赖安装失败，尝试逐个安装...${NC}"
    for whl in "$PACKAGES_DIR"/*.whl; do
        if [ -f "$whl" ]; then
            echo "[信息] 安装: $(basename "$whl")"
            pip install --no-index "$whl" || true
        fi
    done
fi

# 创建启动脚本
echo ""
echo "[6/6] 创建启动器..."

cat > "$HOME/材料管理系统.sh" << 'EOF'
#!/bin/bash
# 材料管理系统启动脚本

cd "$HOME/材料管理系统"
source venv/bin/activate
python main.py "$@"
EOF

chmod +x "$HOME/材料管理系统.sh"

# 创建桌面快捷方式
DESKTOP_FILE="$HOME/Desktop/材料管理系统.desktop"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=材料管理系统
Name[zh_CN]=材料管理系统
Comment=党政机关材料管理软件
Comment[zh_CN]=党政机关材料管理软件
Exec=$HOME/材料管理系统.sh
Icon=$INSTALL_DIR/icon.png
Terminal=false
Type=Application
Categories=Office;Database;Qt;
StartupNotify=true
EOF

chmod +x "$DESKTOP_FILE"

# 设置权限
echo "[信息] 设置文件权限..."
chmod +x "$INSTALL_DIR/main.py"

echo ""
echo "========================================"
echo -e "${GREEN}  安装完成！${NC}"
echo "========================================"
echo ""
echo "启动方式："
echo "  1. 双击桌面图标 '材料管理系统'"
echo "  2. 终端运行：$HOME/材料管理系统.sh"
echo "  3. 进入目录运行：cd $INSTALL_DIR && ./start.sh"
echo ""
echo "重要信息："
echo "  - 安装目录: $INSTALL_DIR"
echo "  - 数据目录: $HOME/.document_manager/"
echo "  - 桌面快捷方式: $DESKTOP_FILE"
echo ""
echo -e "${YELLOW}提示：首次启动可能需要10-20秒，请耐心等待${NC}"
echo ""

# 询问是否立即运行
read -p "是否立即运行程序？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "正在启动..."
    "$HOME/材料管理系统.sh"
fi
