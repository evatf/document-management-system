# 使用GitHub Actions自动构建DEB包（小白专用）

## 一、为什么选择这个方案？

✅ **完全免费** - GitHub免费提供  
✅ **零配置** - 不需要安装WSL或Linux环境  
✅ **全自动** - 一键构建，自动下载  
✅ **最简单** - 你只需要点击几个按钮  

## 二、操作步骤（5分钟搞定）

### 步骤1：创建GitHub仓库（如果还没有）

1. 打开 https://github.com
2. 点击右上角 "+" → "New repository"
3. 填写仓库信息：
   - Repository name: `document-management-system`（或其他名字）
   - 选择 "Public"（公开）
   - 勾选 "Add a README file"
4. 点击 "Create repository"

### 步骤2：上传项目代码到GitHub

**方法A：使用GitHub网页上传（最简单）**

1. 打开刚创建的仓库页面
2. 点击 "uploading an existing file" 链接
3. 将项目文件夹中的所有文件拖拽上传
   - 特别注意：不要只上传某些文件，要全部上传！
4. 在页面底部填写提交信息：
   - "Create a new branch for this commit and start a pull request" → 选择 **"直接提交到main分支"**
5. 点击 "Commit changes"

**方法B：使用Git命令行（如果你会用）**

```bash
# 在项目目录下
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/你的用户名/document-management-system.git
git push -u origin main
```

### 步骤3：触发自动构建

上传完成后，GitHub会自动开始构建（大概需要3-5分钟）

**或者手动触发：**

1. 打开仓库页面
2. 点击顶部的 "Actions" 标签
3. 在左侧找到 "构建DEB安装包" 工作流
4. 点击 "Run workflow" → "Run workflow" 按钮

### 步骤4：下载DEB包

**构建完成后，有两种下载方式：**

**方式1：从Actions下载（推荐）**

1. 点击仓库顶部的 "Actions" 标签
2. 点击最近的构建记录（绿色✓）
3. 滚动到页面底部，找到 "Artifacts" 部分
4. 点击 `deb-package` 下载
5. 下载后解压，得到 `材料管理系统_1.0.0_amd64.deb`

**方式2：从Releases下载**

1. 点击仓库右侧的 "Releases"
2. 点击 "材料管理系统 v1.0.0"
3. 点击 `材料管理系统_1.0.0_amd64.deb` 下载

## 三、在UOS上安装

### 安装

**双击安装（最简单）**
1. 将 `材料管理系统_1.0.0_amd64.deb` 复制到UOS电脑
2. 双击文件
3. 点击"安装"按钮
4. 输入密码

**命令行安装**
```bash
sudo dpkg -i 材料管理系统_1.0.0_amd64.deb
```

### 启动应用

- 在应用菜单中找到"材料管理系统"
- 或在桌面双击快捷方式

### 卸载

```bash
sudo dpkg -r material-manager
```

## 四、常见问题

### Q1: GitHub Actions构建失败怎么办？

**A:** 检查以下几点：
1. 确认所有代码文件都已上传到GitHub
2. 查看 "Actions" 页面中的详细错误日志
3. 检查 `requirements.txt` 和 `main.py` 是否存在

### Q2: 构建需要多长时间？

**A:** 通常3-5分钟，首次可能稍长（约10分钟）

### Q3: DEB包多大？

**A:** 约50-100MB，包含所有依赖

### Q4: 我没有GitHub账号怎么办？

**A:** 免费注册一个，只需要邮箱即可，全程免费

### Q5: 仓库必须是公开的吗？

**A:** 也可以是私有仓库，Actions仍然可以免费使用（有每月2000分钟的限额）

## 五、文件清单

确保以下文件都已上传到GitHub：

```
document-management-system/
├── main.py                          # 主程序
├── requirements.txt                 # Python依赖
├── icon.png                         # 图标
├── resources/                       # 资源文件
├── core/                            # 核心模块
│   ├── __init__.py
│   ├── database.py
│   ├── config.py
│   └── ...
├── modules/                         # 功能模块
│   ├── __init__.py
│   ├── material_library.py
│   └── ...
├── widgets/                         # UI组件
│   ├── __init__.py
│   └── main_window.py
└── .github/
    └── workflows/
        └── build-deb.yml            # 自动构建脚本
```

## 六、如何重新构建？

如果修改了代码，需要重新构建DEB包：

**方法1：推送代码自动构建**
```bash
git add .
git commit -m "Update code"
git push
```
推送后会自动触发构建

**方法2：手动触发**
1. 打开仓库 → Actions
2. 点击 "Run workflow"

## 七、版本管理

每次构建都会生成新的版本，建议：

1. 修改 `build-deb.yml` 中的版本号
2. 推送代码
3. 新的DEB包会自动生成

## 八、对比其他方案

| 方案 | 难度 | 耗时 | 是否需要额外安装 |
|------|------|------|----------------|
| **GitHub Actions** | ⭐ 最简单 | 5分钟 | ❌ 不需要 |
| WSL + 手动构建 | ⭐⭐⭐ 中等 | 30分钟+ | ✅ 需要WSL |
| 购买UOS虚拟机 | ⭐⭐⭐⭐ 困难 | 1小时+ | ✅ 需要购买 |

## 九、推荐流程总结

```
1. 创建GitHub仓库
   ↓
2. 上传所有代码文件
   ↓
3. 等待自动构建完成（3-5分钟）
   ↓
4. 下载DEB包
   ↓
5. 在UOS上双击安装
   ↓
6. 完成！
```

## 十、需要帮助？

如果遇到问题，可以：
1. 查看 "Actions" 页面的构建日志
2. 检查代码是否全部上传
3. 确认 `build-deb.yml` 文件存在且正确

祝你使用顺利！🎉
