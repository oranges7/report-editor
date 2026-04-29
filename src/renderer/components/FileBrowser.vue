<template>
  <div class="file-browser">
    <div class="browser-head">
      <div class="head-label">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" class="head-icon"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
        <span>资源管理器</span>
      </div>
      <button class="refresh-btn" @click="refresh" title="刷新目录">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
      </button>
    </div>
    <div class="browser-tree">
      <el-tree
        ref="treeRef"
        :data="fileTree"
        node-key="path"
        :props="treeProps"
        :expand-on-click-node="false"
        @node-click="handleNodeClick"
        class="ftree"
      >
        <template #default="{ data }">
          <span class="tnode" :class="nodeTypeClass(data)">
            <span class="tnode-icon" :class="iconClass(data)">
              <svg v-if="data.isDirectory" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" class="isvg"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
              <svg v-else-if="isImage(data.name)" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" class="isvg"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
              <svg v-else-if="isTable(data.name)" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" class="isvg"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><line x1="9" y1="3" x2="9" y2="21"/></svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" class="isvg"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            </span>
            <span class="tnode-name">{{ data.name }}</span>
            <span v-if="!data.isDirectory" class="tnode-tag">{{ tagLabel(data.name) }}</span>
          </span>
        </template>
      </el-tree>
    </div>
    <div class="browser-foot">
      <span>单击文件自动插入到编辑器</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import type { TreeInstance } from 'element-plus'

interface FileNode {
  name: string
  path: string
  isDirectory: boolean
  children?: FileNode[]
}

const props = defineProps<{
  workDir: string
}>()

const emit = defineEmits<{
  (e: 'select-file', filePath: string, type: 'graph' | 'table' | 'link'): void
}>()

const treeRef = ref<TreeInstance>()
const fileTree = ref<FileNode[]>([])
const treeProps = {
  children: 'children',
  label: 'name',
  isLeaf: (data: FileNode) => !data.isDirectory
}

const imgExts = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp', '.tiff', '.tif']
const tblExts = ['.xlsx', '.xls', '.csv', '.tsv', '.txt']

function isImage(f: string) { return imgExts.includes(f.toLowerCase().substring(f.lastIndexOf('.'))) }
function isTable(f: string) { return tblExts.includes(f.toLowerCase().substring(f.lastIndexOf('.'))) }
function fileType(f: string): 'graph' | 'table' | 'link' { return isImage(f) ? 'graph' : isTable(f) ? 'table' : 'link' }
function tagLabel(f: string) { return isImage(f) ? 'IMG' : isTable(f) ? 'TBL' : 'FILE' }
function nodeTypeClass(d: FileNode) { return d.isDirectory ? '' : isImage(d.name) ? 'nt-img' : isTable(d.name) ? 'nt-tbl' : 'nt-file' }
function iconClass(d: FileNode) { return d.isDirectory ? 'ic-dir' : isImage(d.name) ? 'ic-img' : isTable(d.name) ? 'ic-tbl' : 'ic-file' }

async function loadDir(dirPath: string): Promise<FileNode[]> {
  const files = await window.electronAPI.readdir(dirPath)
  return files
    .filter((f: any) => !f.name.startsWith('.'))
    .sort((a: any, b: any) => {
      if (a.isDirectory && !b.isDirectory) return -1
      if (!a.isDirectory && b.isDirectory) return 1
      return a.name.localeCompare(b.name)
    })
    .map((f: any) => ({
      name: f.name,
      path: f.path,
      isDirectory: f.isDirectory,
      ...(f.isDirectory ? { children: [] } : {})
    }))
}

async function refresh() {
  const root: FileNode = { name: '工作目录', path: props.workDir, isDirectory: true }
  root.children = await loadDir(props.workDir)
  fileTree.value = [root]
}

watch(() => props.workDir, refresh)
onMounted(refresh)

async function handleNodeClick(data: FileNode) {
  if (!data.isDirectory) {
    emit('select-file', data.path, fileType(data.name))
  } else {
    data.children = await loadDir(data.path)
  }
}
</script>

<style scoped>
.file-browser {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.browser-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px 10px;
}

.head-label {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 11.5px;
  font-weight: 700;
  color: var(--text-subtext1);
  text-transform: uppercase;
  letter-spacing: 0.6px;
}

.head-icon {
  width: 14px;
  height: 14px;
  color: var(--accent-blue);
}

.refresh-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: var(--radius-xs);
  background: transparent;
  color: var(--text-overlay0);
  cursor: pointer;
  transition: all var(--duration-fast) ease;
}

.refresh-btn svg { width: 13px; height: 13px; }

.refresh-btn:hover {
  background: var(--bg-surface1);
  color: var(--text-base);
}

.browser-tree {
  flex: 1;
  overflow: auto;
  padding: 0 6px;
}

.ftree {
  background: transparent;
}

.ftree :deep(.el-tree-node__content) {
  height: 30px;
  border-radius: var(--radius-xs);
  padding-right: 4px;
  transition: background var(--duration-fast) ease;
}

.ftree :deep(.el-tree-node__content:hover) {
  background: var(--bg-surface1);
}

.ftree :deep(.el-tree-node.is-current > .el-tree-node__content) {
  background: var(--accent-blue-soft);
}

.ftree :deep(.el-tree-node__expand-icon) {
  color: var(--text-overlay0);
  font-size: 11px;
  padding: 3px;
}

.ftree :deep(.el-tree-node__expand-icon.is-leaf) {
  color: transparent;
}

.tnode {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  width: 100%;
  overflow: hidden;
  font-weight: 500;
}

.tnode-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 5px;
  flex-shrink: 0;
  background: var(--bg-surface1);
  transition: transform var(--duration-fast) ease;
}

.isvg { width: 12px; height: 12px; }

.ic-dir { background: var(--accent-yellow-soft); }
.ic-dir .isvg { color: var(--accent-yellow); }
.ic-img { background: var(--accent-green-soft); }
.ic-img .isvg { color: var(--accent-green); }
.ic-tbl { background: var(--accent-blue-soft); }
.ic-tbl .isvg { color: var(--accent-blue); }
.ic-file { background: var(--bg-surface1); }
.ic-file .isvg { color: var(--text-overlay0); }

.tnode:hover .tnode-icon { transform: scale(1.08); }

.tnode-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-subtext0);
}

.tnode-tag {
  font-size: 8.5px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 3px;
  background: var(--bg-surface1);
  color: var(--text-overlay0);
  letter-spacing: 0.4px;
  flex-shrink: 0;
}

.nt-img .tnode-tag { background: var(--accent-green-soft); color: var(--accent-green); }
.nt-tbl .tnode-tag { background: var(--accent-blue-soft); color: var(--accent-blue); }

.browser-foot {
  padding: 8px 14px;
  border-top: 1px solid var(--border-subtle);
}

.browser-foot span {
  font-size: 10px;
  color: var(--text-overlay0);
  font-style: italic;
}
</style>
