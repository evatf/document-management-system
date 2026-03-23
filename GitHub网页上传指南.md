# GitHub网页上传操作指南（小白专用，无需安装Git）

## 第一步：注册GitHub账号（2分钟）

1. 打开浏览器，访问：https://github.com/signup
2. 填写信息：
   - Email（邮箱）
   - Password（密码）
   - Username（用户名，例如：jf-doc-manager）
3. 点击 "Create account"
4. 验证邮箱（查收邮件，点击验证链接）
5. 完成！

---

## 第二步：创建仓库（1分钟）

1. 登录GitHub后，点击右上角的 **"+"** 按钮
2. 选择 **"New repository"**
3. 填写仓库信息：
   - **Repository name**: `document-management-system`
   - **Description**（可选）: `材料管理系统 - 党政机关文档管理软件`
   - 选择 **"Public"**（公开）
   - ⚠️ **不要**勾选 "Add a README file"（我们稍后上传）
4. 点击 **"Create repository"**

---

## 第三步：上传文件（5分钟）

### 方法：拖拽上传（最简单）

1. 在刚创建的仓库页面，找到并点击：
   ```
   uploading an existing file
   ```
   或者在页面底部点击：
   ```
   Add file → Upload files
   ```

2. **重要：一次性上传所有文件**

   打开你的项目文件夹：
   ```
   C:\Users\J.F\Desktop\Document Management System
   ```

   **按 Ctrl+A 全选所有文件**，然后拖拽到网页的虚线框区域

3. **必须上传的关键文件清单**

   确保以下文件都已上传（如果缺失请检查）：

   ```
   ✅ 必须上传的文件：
   ├── main.py
   ├── requirements.txt
   ├── icon.png
   ├── build_deb.sh
   ├── DEB构建说明.md
   ├── GitHub Actions自动构建DEB包说明.md
   ├── 部署架构对比与DEB方案总结.md
   ├── core/（整个文件夹）
   │   ├── __init__.py
   │   ├── database.py
   │   ├── config.py
   │   └── ...
   ├── modules/（整个文件夹）
   │   ├── __init__.py
   │   ├── material_library.py
   │   └── ...
   ├── widgets/（整个文件夹）
   │   ├── __init__.py
   │   └── main_window.py
   ├── resources/（整个文件夹，如果有）
   └── .github/
       └── workflows/
           └── build-deb.yml
   ```

4. **提交文件**

   在页面底部的 "Commit changes" 区域：
   - 填写：`Initial commit`
   - 选择：**"Commit directly to the main branch"**（默认选项）
   - 点击 **"Commit changes"** 按钮

5. 等待上传完成（根据网络速度，可能需要1-5分钟）

---

## 第四步：触发自动构建（自动或手动）

### 自动构建（推荐）

上传完成后，GitHub会**自动**开始构建DEB包（大约3-5分钟）

### 手动触发（如果自动构建没开始）

1. 点击仓库顶部的 **"Actions"** 标签
2. 在左侧找到 **"构建DEB安装包"** 工作流
3. 点击 **"Run workflow"** → **"Run workflow"** 按钮
4. 等待构建完成（3-5分钟）

---

## 第五步：下载DEB包（1分钟）

### 方法1：从Actions下载（推荐）

1. 点击仓库顶部的 **"Actions"** 标签
2. 点击最新的构建记录（绿色✓标记）
3. 滚动到页面最底部
4. 找到 **"Artifacts"** 部分
5. 点击 **`deb-package`** 下载
6. 下载完成后，解压zip文件
7. 得到：`材料管理系统_1.0.0_amd64.deb`

### 方法2：从Releases下载

1. 点击仓库右侧的 **"Releases"**
2. 点击 **"材料管理系统 v1.0.0"**
3. 点击 **`材料管理系统_1.0.0_amd64.deb`** 直接下载

---

## 第六步：在UOS上安装（1分钟）

### 方法1：双击安装（最简单）

1. 将 `材料管理系统_1.0.0_amd64.deb` 复制到UOS电脑
2. 双击该文件
3. 点击 **"安装"** 按钮
4. 输入密码确认
5. 等待安装完成

### 方法2：命令行安装

```bash
sudo dpkg -i 材料管理系统_1.0.0_amd64.deb
```

---

## 第七步：启动应用

安装完成后：

1. 在UOS应用菜单中找到 **"材料管理系统"**
2. 或者在桌面双击快捷方式
3. 点击启动即可使用

---

## 常见问题

### Q1: 上传文件时提示错误怎么办？

**A:**
- 检查文件名中是否包含特殊字符
- 文件名不要包含中文（GitHub支持中文但可能有问题）
- 确保没有正在使用的文件（如数据库.db文件）

### Q2: 构建失败怎么办？

**A:**
1. 点击 **"Actions"** 标签
2. 点击失败的构建记录（红色✗）
3. 查看详细的错误日志
4. 常见错误：
   - 缺少文件（检查是否所有文件都上传了）
   - 文件名错误（检查main.py、requirements.txt等）

### Q3: 上传太慢怎么办？

**A:**
- 检查网络连接
- 分批上传（第一次上传核心文件，第二次上传资源文件）
- 压缩后再上传（不推荐，会增加复杂度）

### Q4: 如何验证文件是否全部上传？

**A:**
在GitHub仓库页面，点击文件列表，确保以下文件夹都存在：
- `core/`
- `modules/`
- `widgets/`
- `.github/workflows/`

### Q5: 构建需要多长时间？

**A:**
- 首次构建：约5-10分钟
- 后续构建：约3-5分钟

---

## 成功标志

当看到以下情况，说明成功：

✅ GitHub Actions显示绿色✓
✅ Artifacts区域可以下载 `deb-package`
✅ 下载的DEB包约50-100MB
✅ 在UOS上双击能正常安装
✅ 安装后能在应用菜单找到"材料管理系统"

---

## 下一步

安装成功后，你可以：

1. 测试所有功能（导入文件、搜索、智能分析等）
2. 如果发现bug，修改代码后重新上传，会自动构建新版本
3. 需要更新版本号时，修改 `.github/workflows/build-deb.yml` 中的版本号

---

## 需要帮助？

如果遇到问题：

1. 查看 Actions 页面的构建日志（详细错误信息）
2. 检查文件是否全部上传（特别是 .github/workflows/build-deb.yml）
3. 确保文件名正确（main.py、requirements.txt等）

祝你使用顺利！🎉
