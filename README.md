# 报告编辑器

一款专业的报告模板桌面编辑器，基于 Electron 41 + Vue 3 + CodeMirror 6 构建，支持自定义标记语法高亮、快捷元素插入、文件浏览器、双主题切换和文本片段管理。

![版本](https://img.shields.io/badge/version-1.2.0-blue)
![Electron](https://img.shields.io/badge/Electron-41-47848f)
![Vue](https://img.shields.io/badge/Vue-3.4-42b883)
![CodeMirror](https://img.shields.io/badge/CodeMirror-6-d92a2a)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 功能特性

### 编辑器

- **语法高亮** — 自定义报告标记语言的语法着色（关键字、字符串、注释分色显示）
- **行号显示** — 带行号的代码编辑区
- **查找替换** — 支持 Ctrl+F / Ctrl+H 快捷键，搜索计数与逐条跳转
- **撤销/重做** — 完整的编辑历史记录
- **活动行高亮** — 当前行背景高亮

### 文件操作

- **新建文件** — 创建包含默认模板的新文件
- **打开文件** — 打开 .txt 报告模板文件
- **保存 / 另存为** — 保存编辑内容，未保存时显示脉动提示
- **工作目录** — 设置工作目录后自动显示文件浏览器

### 快捷插入

| 元素 | 语法 | 说明 |
|------|------|------|
| 元信息 | `#Custom:` `#Contract:` `#Title:` | 报告基本信息 |
| 章节 | `#section:英文:中文#` | 一级章节标题 |
| 子标题 | `#subsection#` | 章节副标题 |
| H5 / H6 | `#h5#` `#h6#` | 五级/六级标题 |
| 图片 | `#graph:标题:路径#` | 插入图片（支持多图） |
| 表格 | `#table:标题:路径#` | 插入表格 |
| 链接 | `#link:标题:路径#` | 链接文件（不展示为图表） |
| Span | `#span:` | 行内标注 |
| Paper | `#paper:` | 文献引用 |
| Ann | `#ann:` | 注释标记 |

### 文件浏览器

- 设置工作目录后自动显示侧栏文件树
- 文件类型自动识别（图片 / 表格 / 其他）
- 单击文件自动插入对应语法到编辑器（相对路径自动转换）

### 双主题系统

- **暗色主题** — Catppuccin Mocha 配色，深蓝灰基调
- **亮色主题** — Catppuccin Latte 配色，清爽明亮
- 一键切换，主题偏好自动保存至 localStorage
- 窗口标题栏颜色同步切换

### 文本片段

- **保存片段** — 选中编辑器文本保存为可复用片段
- **插入片段** — 从已保存的片段库中快速插入

---

## 报告模板语法

报告模板使用 `#` 标记的自定义语法，配合 Python 脚本 `html_auto_report_nologo.py` 生成最终报告文档。

### 基本格式

```
#Custom:名字
#Contract:项目编号
#Title:题目
```

### 章节结构

```
#section:English Title:中文标题#
#subsection# -- 用于副标题
#h5# -- 五级标题
#h6# -- 六级标题
```

### 媒体元素

```
#graph:图1,图2:img1.png,img2.png#    -- 插入图片（多图并排）
#table:表名:data.xlsx#               -- 插入表格
#link:附件1:file.pdf#                -- 链接文件
```

### 注释元素

```
#span:标注内容#
#paper:文献引用#
#ann:注释说明#
```

---

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Electron | 41.3 | 跨平台桌面应用框架 |
| Vue | 3.4 | 响应式前端框架 |
| TypeScript | 5.6 | 类型安全 |
| Vite | 5.4 | 构建工具 |
| CodeMirror | 6 | 代码编辑器引擎 |
| Element Plus | 2.5 | UI 组件库 |

---

## 项目结构

```
报告编辑器/
├── src/
│   ├── main/                    # Electron 主进程
│   │   ├── main.ts              # 窗口创建、IPC 通信、文件操作
│   │   └── preload.ts           # 预加载脚本、API 桥接
│   └── renderer/                # 渲染进程（Vue 应用）
│       ├── App.vue              # 根组件、全局样式、主题变量
│       ├── main.ts              # Vue 入口
│       └── components/
│           ├── Editor.vue       # CodeMirror 编辑器、双主题、搜索替换
│           ├── Toolbar.vue      # 自定义标题栏、操作按钮、下拉菜单
│           ├── FileBrowser.vue  # 文件浏览器侧栏
│           ├── InsertDialog.vue # 元素插入对话框
│           └── TemplateDialog.vue # 文本片段管理对话框
├── index.html                   # 入口 HTML
├── vite.config.ts               # Vite 构建配置
├── tsconfig.json                # TypeScript 配置
├── tsconfig.electron.json       # Electron 端 TS 配置
├── package.json                 # 项目依赖与脚本
└── html_auto_report_nologo.py   # 配套 Python 报告生成脚本
```

---

## 快速开始

### 环境要求

- Node.js >= 18
- npm >= 9
- Windows 10/11（当前仅构建 Windows 版本）

### 安装依赖

```bash
npm install
```

> 国内用户建议使用镜像源加速 Electron 下载：
> ```bash
> $env:ELECTRON_MIRROR="https://npmmirror.com/mirrors/electron/"
> npm install
> ```

### 开发运行

```bash
npm run electron:dev
```

启动后自动打开开发工具，支持热重载。

### 构建打包

```bash
npm run electron:build
```

构建产物输出至 `release-{version}/` 目录，包含：
- `报告编辑器 Setup {version}.exe` — NSIS 安装包
- `win-unpacked/报告编辑器.exe` — 绿色免安装版

---

## 开发指南

### 可用脚本

| 命令 | 说明 |
|------|------|
| `npm run dev` | 启动 Vite 开发服务器（仅前端） |
| `npm run build` | TypeScript 检查 + Vite 构建 |
| `npm run build:electron` | 编译 Electron 主进程 TypeScript |
| `npm run electron:dev` | 完整开发模式（前端 + Electron） |
| `npm run electron:build` | 完整构建 + 打包安装程序 |

### 架构说明

- **主进程** (`src/main/`) — 负责窗口管理、原生对话框、文件系统操作
- **渲染进程** (`src/renderer/`) — Vue 3 SPA，负责全部 UI 逻辑
- **预加载脚本** (`src/main/preload.ts`) — 通过 `contextBridge` 安全暴露文件操作 API
- **IPC 通信** — 渲染进程通过 `window.electronAPI` 调用主进程能力

### 主题系统

主题通过 `data-theme` 属性切换，CSS 变量驱动全局配色：

- 暗色：Catppuccin Mocha 调色板
- 亮色：Catppuccin Latte 调色板
- CodeMirror 编辑器通过 `Compartment` + `MutationObserver` 实现动态主题切换
- 窗口标题栏通过 IPC 同步颜色

---

## 版本历史

### v1.2.0

- 升级 Electron 至 v41（Chromium 146 + Node 24）
- 全新 Studio Luxe 设计系统（Catppuccin Mocha / Latte 双主题）
- 无边框窗口 + 原生 titleBarOverlay
- 主题切换按钮（☀️/🌙），偏好自动保存
- 编辑器动态主题切换（Compartment）
- 窗口标题栏颜色同步
- 工具栏按钮与窗口控件间距修复

### v1.1.1

- 暗色主题 UI 现代化
- 自定义下拉菜单替代 Element Plus Dropdown
- 内联 SVG 图标替代 Element Plus Icons
- 文件类型色彩编码徽章
- 渐变光线装饰效果

### v1.0.0

- 初始版本
- 基础报告模板编辑功能
- CodeMirror 6 语法高亮
- 文件浏览器
- 元素插入对话框
- 文本片段管理

---

## 许可证

[MIT License](https://opensource.org/licenses/MIT)
