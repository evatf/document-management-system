# DEB包构建说明

## 快速开始

### 前提条件
- Windows 10/11 专业版/企业版/教育版
- 已安装WSL（Windows Subsystem for Linux）

### 第一步：安装WSL

如果还没有安装WSL，在PowerShell（管理员）中运行：

```powershell
wsl --install
```

选择 **Ubuntu 22.04 LTS**，安装完成后重启电脑。

### 第二步：准备构建环境

1. 打开 **Ubuntu**（在开始菜单搜索"Ubuntu"）
2. 安装必要工具：

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv build-essential dpkg-dev debhelper
```

3. 进入项目目录：

```bash
cd /mnt/c/Users/J.F/Desktop/Document\ Management\ System
```

### 第三步：执行构建

```bash
chmod +x build_deb.sh
./build_deb.sh
```

### 第四步：获取deb包

构建完成后，deb包会在项目根目录：

```
材料管理系统_1.0.0_amd64.deb
```

这个文件就是最终可以拷贝到UOS电脑安装的安装包！

## 在UOS上使用

### 安装

**方法1：双击安装**
1. 将 `材料管理系统_1.0.0_amd64.deb` 复制到UOS电脑
2. 双击文件，点击"安装"
3. 输入密码确认

**方法2：命令行安装**
```bash
sudo dpkg -i 材料管理系统_1.0.0_amd64.deb
```

### 启动应用

- 在应用菜单中找到"材料管理系统"
- 或在桌面双击快捷方式

### 卸载

**方法1：图形界面**
- 打开软件中心，找到"材料管理系统"，点击卸载

**方法2：命令行**
```bash
sudo dpkg -r material-manager
```

## 完全卸载（包括配置）

```bash
sudo dpkg -P material-manager
```

## 常见问题

### Q1: WSL安装失败？

**A:** 确保Windows版本支持WSL，需要Windows 10版本19044或更高。

### Q2: 构建失败提示缺少依赖？

**A:** 在Ubuntu中运行：
```bash
sudo apt update
sudo apt install -f
```

### Q3: deb包太大？

**A:** 正常大小约50-100MB，包含了所有依赖。

### Q4: 在UOS上安装失败？

**A:** 尝试修复依赖：
```bash
sudo apt --fix-broken install
sudo dpkg -i 材料管理系统_1.0.0_amd64.deb
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `build_deb.sh` | 自动构建脚本 |
| `材料管理系统_1.0.0_amd64.deb` | 最终的安装包（构建后生成） |
| `.trae/documents/deb打包方案.md` | 详细技术文档 |

## 下一步

如果WSL不可用，可以考虑：

1. **使用在线构建服务**（GitHub Actions）
2. **购买UOS虚拟机**（最保险）
3. **继续使用Shell脚本方案**（已经准备好的）

需要我帮你设置GitHub Actions自动构建吗？
