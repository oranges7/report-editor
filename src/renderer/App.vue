<template>
  <div class="app">
    <Toolbar
      :file-path="filePath"
      :is-modified="isModified"
      @new-file="handleNewFile"
      @open-file="handleOpenFile"
      @save-file="handleSaveFile"
      @save-as="handleSaveAs"
      @set-work-dir="handleSetWorkDir"
      @insert-meta="handleInsertMeta"
      @insert-section="handleInsertSection"
      @insert-subsection="handleInsertSubsection"
      @insert-h5="handleInsertH5"
      @insert-h6="handleInsertH6"
      @insert-graph="handleInsertGraph"
      @insert-table="handleInsertTable"
      @insert-link="handleInsertLink"
      @insert-span="handleInsertSpan"
      @insert-paper="handleInsertPaper"
      @insert-ann="handleInsertAnn"
      @load-template="handleLoadTemplate"
      @save-template="handleSaveTemplate"
      @theme-change="handleThemeChange"
      @toggle-wrap="handleToggleWrap"
    />

    <div class="main-body">
      <transition name="slide-sidebar">
        <aside class="sidebar" v-if="workDir" :style="{ width: sidebarWidth + 'px' }">
          <FileBrowser
            :work-dir="workDir"
            @select-file="handleFileSelect"
          />
        </aside>
      </transition>

      <div
        v-if="workDir"
        class="resize-handle"
        @mousedown="startResize"
      />

      <main class="editor-area">
        <div class="editor-shell">
          <Editor
            ref="editorRef"
            v-model:content="content"
            @change="handleContentChange"
          />
        </div>
      </main>
    </div>

    <InsertDialog
      v-model:visible="insertDialogVisible"
      :type="insertDialogType"
      :work-dir="workDir"
      @confirm="handleInsertConfirm"
    />

    <TemplateDialog
      v-model:visible="templateDialogVisible"
      :mode="templateDialogMode"
      :current-content="selectedText"
      @load-template-content="handleLoadTemplateContent"
      @save-template="handleSaveTemplateConfirm"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import Toolbar from './components/Toolbar.vue'
import Editor from './components/Editor.vue'
import FileBrowser from './components/FileBrowser.vue'
import InsertDialog from './components/InsertDialog.vue'
import TemplateDialog from './components/TemplateDialog.vue'

const editorRef = ref()
const filePath = ref<string | null>(null)
const content = ref('')
const isModified = ref(false)
const workDir = ref<string | null>(null)

const SIDEBAR_MIN = 180
const SIDEBAR_MAX = 600
const SIDEBAR_DEFAULT = 300
const SIDEBAR_STORAGE_KEY = 'report-editor-sidebar-width'

const sidebarWidth = ref(SIDEBAR_DEFAULT)

const insertDialogVisible = ref(false)
const insertDialogType = ref('')
const templateDialogVisible = ref(false)
const templateDialogMode = ref<'load' | 'save'>('load')
const selectedText = ref('')

function startResize(e: MouseEvent) {
  e.preventDefault()
  const startX = e.clientX
  const startWidth = sidebarWidth.value

  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'

  const overlay = document.createElement('div')
  overlay.className = 'resize-overlay'
  document.body.appendChild(overlay)

  function onMouseMove(ev: MouseEvent) {
    const delta = ev.clientX - startX
    const newWidth = Math.min(SIDEBAR_MAX, Math.max(SIDEBAR_MIN, startWidth + delta))
    sidebarWidth.value = newWidth
  }

  function onMouseUp() {
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
    if (overlay.parentNode) overlay.parentNode.removeChild(overlay)
    localStorage.setItem(SIDEBAR_STORAGE_KEY, String(sidebarWidth.value))
  }

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}

const defaultContent = `#Custom:名字
#Contract:项目编号
#Title:题目
#section:英文题目:中文标题#
#subsection# -- 用于副标题
#table:表名:表文件名# -- 用于表格
#graph:S1,S2,..:file1,file2,..# -- 用于图片
#link:S1,S2,..:file1,file2,..# -- 用于链接文件，但不做图或表展示
`

onMounted(() => {
  content.value = defaultContent
  const savedWidth = localStorage.getItem(SIDEBAR_STORAGE_KEY)
  if (savedWidth) {
    const w = parseInt(savedWidth, 10)
    if (!isNaN(w) && w >= SIDEBAR_MIN && w <= SIDEBAR_MAX) {
      sidebarWidth.value = w
    }
  }
})

function handleNewFile() {
  if (isModified.value) {
    ElMessageBox.confirm('当前文件有未保存的内容，是否继续？', '提示', {
      confirmButtonText: '继续',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      createNewFile()
    }).catch(() => {})
  } else {
    createNewFile()
  }
}

function createNewFile() {
  filePath.value = null
  content.value = defaultContent
  isModified.value = false
  ElMessage.success('已创建新文件')
}

async function handleOpenFile() {
  const result = await window.electronAPI.openFile()
  if (result) {
    filePath.value = result.filePath
    content.value = result.content
    isModified.value = false
    ElMessage.success('文件已打开')
  }
}

async function handleSaveFile() {
  if (filePath.value) {
    await window.electronAPI.writeFile(filePath.value, content.value)
    isModified.value = false
    ElMessage.success('文件已保存')
  } else {
    handleSaveAs()
  }
}

async function handleSaveAs() {
  const path = await window.electronAPI.saveFile(content.value)
  if (path) {
    filePath.value = path
    isModified.value = false
    ElMessage.success('文件已保存')
  }
}

async function handleSetWorkDir() {
  const dir = await window.electronAPI.openDirectory()
  if (dir) {
    workDir.value = dir
    ElMessage.success('工作目录已设置')
  }
}

function handleContentChange() {
  isModified.value = true
}

function handleInsertMeta() {
  insertDialogType.value = 'meta'
  insertDialogVisible.value = true
}

function handleInsertSection() {
  insertDialogType.value = 'section'
  insertDialogVisible.value = true
}

function handleInsertSubsection() {
  insertText('#subsection#\n')
}

function handleInsertH5() {
  insertText('#h5#\n')
}

function handleInsertH6() {
  insertText('#h6#\n')
}

function handleInsertGraph() {
  insertDialogType.value = 'graph'
  insertDialogVisible.value = true
}

function handleInsertTable() {
  insertDialogType.value = 'table'
  insertDialogVisible.value = true
}

function handleInsertLink() {
  insertDialogType.value = 'link'
  insertDialogVisible.value = true
}

function handleInsertSpan() {
  insertDialogType.value = 'span'
  insertDialogVisible.value = true
}

function handleInsertPaper() {
  insertDialogType.value = 'paper'
  insertDialogVisible.value = true
}

function handleInsertAnn() {
  insertDialogType.value = 'ann'
  insertDialogVisible.value = true
}

function handleInsertConfirm(text: string) {
  insertText(text)
  insertDialogVisible.value = false
}

function insertText(text: string) {
  editorRef.value?.insertText(text)
  isModified.value = true
}

async function handleFileSelect(selectedFilePath: string, type: 'graph' | 'table' | 'link') {
  if (!workDir.value) return

  const relativePath = await window.electronAPI.relativePath(workDir.value, selectedFilePath)
  const fileName = selectedFilePath.split(/[/\\]/).pop() || ''
  const baseName = fileName.substring(0, fileName.lastIndexOf('.')) || fileName

  let text = ''
  switch (type) {
    case 'graph':
      text = `#graph:${baseName}:${relativePath}#\n`
      break
    case 'table':
      text = `#table:${baseName}:${relativePath}#\n`
      break
    case 'link':
      text = `#link:${baseName}:${relativePath}#\n`
      break
  }

  insertText(text)
  ElMessage.success(`已插入${type === 'graph' ? '图片' : type === 'table' ? '表格' : '链接'}: ${fileName}`)
}

function handleLoadTemplate() {
  templateDialogMode.value = 'load'
  selectedText.value = ''
  templateDialogVisible.value = true
}

function handleSaveTemplate() {
  templateDialogMode.value = 'save'
  selectedText.value = editorRef.value?.getSelectedText() || ''
  templateDialogVisible.value = true
}

function handleLoadTemplateContent(templateContent: string) {
  insertText(templateContent)
  templateDialogVisible.value = false
}

function handleSaveTemplateConfirm(name: string) {
  ElMessage.success(`文本片段 "${name}" 已保存`)
  templateDialogVisible.value = false
}

function handleThemeChange(theme: 'light' | 'dark') {
  if (window.electronAPI?.setTitleBarTheme) {
    window.electronAPI.setTitleBarTheme(theme)
  }
}

function handleToggleWrap() {
  const current = editorRef.value?.wordWrap ?? true
  editorRef.value?.setWordWrap(!current)
}
</script>

<style>
:root {
  --bg-base: #0d0f14;
  --bg-crust: #111320;
  --bg-mantle: #151825;
  --bg-surface0: #1a1e2e;
  --bg-surface1: #1f2437;
  --bg-surface2: #252b3f;
  --bg-overlay: rgba(13, 15, 20, 0.8);

  --text-base: #cdd6f4;
  --text-subtext0: #a6adc8;
  --text-subtext1: #7f849c;
  --text-overlay0: #6c7086;

  --accent-blue: #89b4fa;
  --accent-blue-soft: rgba(137, 180, 250, 0.10);
  --accent-blue-med: rgba(137, 180, 250, 0.18);
  --accent-lavender: #b4befe;
  --accent-sapphire: #74c7ec;
  --accent-teal: #94e2d5;
  --accent-green: #a6e3a1;
  --accent-green-soft: rgba(166, 227, 161, 0.10);
  --accent-yellow: #f9e2af;
  --accent-yellow-soft: rgba(249, 226, 175, 0.10);
  --accent-peach: #fab387;
  --accent-red: #f38ba8;
  --accent-red-soft: rgba(243, 139, 168, 0.10);
  --accent-mauve: #cba6f7;
  --accent-mauve-soft: rgba(203, 166, 247, 0.10);
  --accent-pink: #f5c2e7;
  --accent-sky: #89dceb;

  --border: #2a2f45;
  --border-subtle: rgba(205, 214, 244, 0.06);

  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.4);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.5);
  --shadow-lg: 0 12px 48px rgba(0, 0, 0, 0.6);
  --shadow-glow: 0 0 32px rgba(137, 180, 250, 0.12);

  --radius-xs: 4px;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-xl: 20px;

  --font-sans: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace;

  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  --duration-fast: 120ms;
  --duration-base: 200ms;
  --duration-slow: 350ms;
}

[data-theme="light"] {
  --bg-base: #eff1f5;
  --bg-crust: #e6e9ef;
  --bg-mantle: #e6e9ef;
  --bg-surface0: #ccd0da;
  --bg-surface1: #bcc0cc;
  --bg-surface2: #acb0be;
  --bg-overlay: rgba(239, 241, 245, 0.85);

  --text-base: #4c4f69;
  --text-subtext0: #5c5f77;
  --text-subtext1: #7c7f93;
  --text-overlay0: #9ca0b0;

  --accent-blue: #1e66f5;
  --accent-blue-soft: rgba(30, 102, 245, 0.08);
  --accent-blue-med: rgba(30, 102, 245, 0.15);
  --accent-lavender: #7287fd;
  --accent-sapphire: #209fb5;
  --accent-teal: #179299;
  --accent-green: #40a02b;
  --accent-green-soft: rgba(64, 160, 43, 0.08);
  --accent-yellow: #df8e1d;
  --accent-yellow-soft: rgba(223, 142, 29, 0.08);
  --accent-peach: #fe640b;
  --accent-red: #d20f39;
  --accent-red-soft: rgba(210, 15, 57, 0.08);
  --accent-mauve: #8839ef;
  --accent-mauve-soft: rgba(136, 57, 239, 0.08);
  --accent-pink: #ea76cb;
  --accent-sky: #04a5e5;

  --border: #ccd0da;
  --border-subtle: rgba(76, 79, 105, 0.10);

  --shadow-sm: 0 1px 3px rgba(76, 79, 105, 0.08);
  --shadow-md: 0 4px 16px rgba(76, 79, 105, 0.10);
  --shadow-lg: 0 12px 48px rgba(76, 79, 105, 0.14);
  --shadow-glow: 0 0 32px rgba(30, 102, 245, 0.08);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  width: 100%;
  overflow: hidden;
  background: var(--bg-base);
  color: var(--text-base);
  font-family: var(--font-sans);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--bg-surface2);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-overlay0);
}

.app {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-base);
}

.main-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

.slide-sidebar-enter-active,
.slide-sidebar-leave-active {
  transition: opacity var(--duration-slow) var(--ease-out), transform var(--duration-slow) var(--ease-out);
}

.slide-sidebar-enter-from,
.slide-sidebar-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.sidebar {
  flex-shrink: 0;
  border-right: 1px solid var(--border-subtle);
  background: var(--bg-crust);
  overflow: hidden;
  position: relative;
}

.resize-handle {
  width: 5px;
  cursor: col-resize;
  background: transparent;
  flex-shrink: 0;
  position: relative;
  z-index: 10;
  transition: background var(--duration-fast) ease;
}

.resize-handle:hover {
  background: var(--accent-blue-med);
}

.resize-handle:active {
  background: var(--accent-blue);
}

.resize-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  cursor: col-resize;
}

.sidebar::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 1px;
  background: linear-gradient(to bottom, var(--accent-blue-med), transparent 30%, transparent 70%, var(--accent-mauve-soft));
  pointer-events: none;
}

.editor-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
  background: var(--bg-base);
  position: relative;
}

.editor-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 120px;
  background: radial-gradient(ellipse at 50% -20%, rgba(137, 180, 250, 0.04) 0%, transparent 70%);
  pointer-events: none;
  z-index: 0;
}

.editor-shell {
  flex: 1;
  overflow: hidden;
  margin: 6px;
  border-radius: var(--radius-lg);
  background: var(--bg-mantle);
  border: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255, 255, 255, 0.02);
  position: relative;
  z-index: 1;
}

.el-message-box {
  background: var(--bg-surface0) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-lg) !important;
}

.el-message-box__title {
  color: var(--text-base) !important;
  font-family: var(--font-sans) !important;
}

.el-message-box__message {
  color: var(--text-subtext0) !important;
  font-family: var(--font-sans) !important;
}

.el-message-box__btns .el-button--primary {
  background: var(--accent-blue) !important;
  border-color: var(--accent-blue) !important;
  color: var(--bg-base) !important;
  font-weight: 600 !important;
}

.el-message-box__btns .el-button--primary:hover {
  background: var(--accent-lavender) !important;
  border-color: var(--accent-lavender) !important;
}

.el-message {
  background: var(--bg-surface0) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-lg) !important;
}

.el-message .el-message__content {
  color: var(--text-base) !important;
}

.el-message--success { border-color: var(--accent-green) !important; }
.el-message--warning { border-color: var(--accent-yellow) !important; }
.el-message--error { border-color: var(--accent-red) !important; }

.el-dialog {
  background: var(--bg-surface0) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-xl) !important;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.7) !important;
  overflow: hidden;
}

.el-dialog__header {
  padding: 20px 28px 16px !important;
  border-bottom: 1px solid var(--border-subtle) !important;
  background: var(--bg-crust) !important;
}

.el-dialog__title {
  color: var(--text-base) !important;
  font-weight: 700 !important;
  font-size: 15px !important;
  font-family: var(--font-sans) !important;
  letter-spacing: -0.3px;
}

.el-dialog__headerbtn .el-dialog__close {
  color: var(--text-subtext1) !important;
}

.el-dialog__body {
  padding: 24px 28px !important;
  color: var(--text-subtext0) !important;
}

.el-dialog__footer {
  padding: 12px 28px 24px !important;
  border-top: 1px solid var(--border-subtle) !important;
}

.el-form-item__label {
  color: var(--text-subtext0) !important;
  font-family: var(--font-sans) !important;
  font-weight: 500 !important;
}

.el-input__wrapper {
  background: var(--bg-mantle) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  box-shadow: none !important;
  transition: all var(--duration-fast) ease !important;
}

.el-input__wrapper:hover {
  border-color: var(--bg-surface2) !important;
}

.el-input__wrapper.is-focus,
.el-textarea__inner:focus {
  border-color: var(--accent-blue) !important;
  box-shadow: 0 0 0 2px var(--accent-blue-soft), 0 0 16px var(--accent-blue-soft) !important;
}

.el-input__inner {
  color: var(--text-base) !important;
  font-family: var(--font-sans) !important;
}

.el-input__inner::placeholder {
  color: var(--text-overlay0) !important;
}

.el-textarea__inner {
  background: var(--bg-mantle) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-base) !important;
  font-family: var(--font-mono) !important;
  font-size: 13px !important;
  line-height: 1.7 !important;
  box-shadow: none !important;
  transition: all var(--duration-fast) ease !important;
}

.el-textarea__inner:hover {
  border-color: var(--bg-surface2) !important;
}

.el-textarea__inner::placeholder {
  color: var(--text-overlay0) !important;
}

.el-button--default {
  background: var(--bg-surface1) !important;
  border: 1px solid var(--border) !important;
  color: var(--text-subtext0) !important;
  border-radius: var(--radius-sm) !important;
  font-family: var(--font-sans) !important;
  font-weight: 500 !important;
  transition: all var(--duration-fast) ease !important;
}

.el-button--default:hover {
  background: var(--bg-surface2) !important;
  border-color: var(--text-overlay0) !important;
  color: var(--text-base) !important;
}

.el-button--primary {
  background: var(--accent-blue) !important;
  border-color: var(--accent-blue) !important;
  color: var(--bg-base) !important;
  border-radius: var(--radius-sm) !important;
  font-family: var(--font-sans) !important;
  font-weight: 600 !important;
  transition: all var(--duration-fast) ease !important;
}

.el-button--primary:hover {
  background: var(--accent-lavender) !important;
  border-color: var(--accent-lavender) !important;
  box-shadow: 0 0 24px rgba(137, 180, 250, 0.25) !important;
}

.el-button--danger {
  background: transparent !important;
  border: 1px solid rgba(243, 139, 168, 0.25) !important;
  color: var(--accent-red) !important;
  border-radius: var(--radius-sm) !important;
  font-family: var(--font-sans) !important;
  transition: all var(--duration-fast) ease !important;
}

.el-button--danger:hover {
  background: var(--accent-red-soft) !important;
  border-color: var(--accent-red) !important;
}

.el-table {
  background: transparent !important;
  --el-table-tr-bg-color: transparent !important;
  --el-table-header-bg-color: transparent !important;
  --el-table-row-hover-bg-color: var(--bg-surface1) !important;
  --el-table-border-color: var(--border-subtle) !important;
  font-family: var(--font-sans) !important;
}

.el-table th.el-table__cell {
  background: var(--bg-surface0) !important;
  color: var(--text-subtext1) !important;
  font-weight: 600 !important;
  font-size: 12px !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
  border-bottom: 1px solid var(--border) !important;
}

.el-table td.el-table__cell {
  color: var(--text-base) !important;
  border-bottom: 1px solid var(--border-subtle) !important;
}

.el-alert {
  background: var(--accent-blue-soft) !important;
  border: 1px solid rgba(137, 180, 250, 0.15) !important;
  border-radius: var(--radius-sm) !important;
}

.el-alert__title {
  color: var(--accent-blue) !important;
  font-family: var(--font-sans) !important;
}

.el-tree {
  background: transparent !important;
  --el-tree-node-hover-bg-color: var(--bg-surface1) !important;
  color: var(--text-subtext0) !important;
  font-family: var(--font-sans) !important;
}

.el-tree-node__content:hover {
  background: var(--bg-surface1) !important;
}

.el-overlay {
  background: rgba(0, 0, 0, 0.65) !important;
  backdrop-filter: blur(8px) saturate(1.2);
}

.el-popper.is-dark {
  background: var(--bg-surface1) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-lg) !important;
}

.el-dropdown-menu {
  background: var(--bg-surface0) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.6) !important;
  padding: 6px !important;
}

.el-dropdown-menu__item {
  color: var(--text-subtext0) !important;
  border-radius: var(--radius-sm) !important;
  margin: 1px 0 !important;
  font-family: var(--font-sans) !important;
  font-size: 13px !important;
  transition: all var(--duration-fast) ease !important;
}

.el-dropdown-menu__item:hover {
  background: var(--accent-blue-soft) !important;
  color: var(--accent-blue) !important;
}

.el-divider--horizontal {
  border-top-color: var(--border-subtle) !important;
  margin: 6px 0 !important;
}
</style>
