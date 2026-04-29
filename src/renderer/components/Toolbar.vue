<template>
  <header class="titlebar" :data-theme="theme">
    <div class="titlebar-drag">
      <div class="toolbar-left">
        <div class="brand">
          <div class="brand-mark">
            <svg viewBox="0 0 32 32" fill="none">
              <rect x="2" y="2" width="28" height="28" rx="8" fill="url(#brand-grad)" />
              <path d="M10 11h12M10 16h8M10 21h10" stroke="white" stroke-width="1.8" stroke-linecap="round" />
              <defs>
                <linearGradient id="brand-grad" x1="2" y1="2" x2="30" y2="30">
                  <stop stop-color="#89b4fa" />
                  <stop offset="1" stop-color="#cba6f7" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <span class="brand-name">报告编辑器</span>
          <span class="brand-version">v1.2</span>
        </div>

        <div class="sep" />

        <div class="action-group">
          <button class="act-btn" @click="$emit('new-file')" title="新建 (Ctrl+N)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/></svg>
          </button>
          <button class="act-btn" @click="$emit('open-file')" title="打开 (Ctrl+O)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
          </button>
          <button class="act-btn save" :class="{ 'has-changes': isModified }" @click="$emit('save-file')" title="保存 (Ctrl+S)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
            <span v-if="isModified" class="unsaved-dot" />
          </button>
          <button class="act-btn" @click="$emit('save-as')" title="另存为">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          </button>
        </div>

        <div class="sep" />

        <button class="act-btn ghost" @click="$emit('set-work-dir')" title="设置工作目录">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
          <span class="act-label">工作目录</span>
        </button>

        <Transition name="fade">
          <span v-if="filePath" class="file-path-pill">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" class="pill-icon"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            {{ shortPath }}
          </span>
        </Transition>
      </div>

      <div class="toolbar-right">
        <button class="act-btn theme-toggle" @click="toggleTheme" :title="theme === 'dark' ? '切换到浅色主题' : '切换到深色主题'">
          <svg v-if="theme === 'dark'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        </button>

        <div class="dropdown-wrap" ref="insertRef">
          <button class="act-btn primary" @click="toggleInsert">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            <span class="act-label">插入</span>
            <svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
          </button>
          <Transition name="dropdown">
            <div class="menu-panel" v-if="insertOpen">
              <div class="menu-section">
                <div class="menu-heading">文本结构</div>
                <button class="menu-item" @click="fire('insert-meta')">
                  <span class="mi-badge blue">M</span> 插入元信息
                </button>
                <button class="menu-item" @click="fire('insert-section')">
                  <span class="mi-badge green">§</span> 插入章节
                </button>
                <button class="menu-item" @click="fire('insert-subsection')">
                  <span class="mi-badge teal">¶</span> 插入子标题
                </button>
                <button class="menu-item" @click="fire('insert-h5')">
                  <span class="mi-badge surface">H5</span> 插入 H5
                </button>
                <button class="menu-item" @click="fire('insert-h6')">
                  <span class="mi-badge surface">H6</span> 插入 H6
                </button>
              </div>
              <div class="menu-divider" />
              <div class="menu-section">
                <div class="menu-heading">媒体元素</div>
                <button class="menu-item" @click="fire('insert-graph')">
                  <span class="mi-badge green">◆</span> 插入图片
                </button>
                <button class="menu-item" @click="fire('insert-table')">
                  <span class="mi-badge yellow">⊞</span> 插入表格
                </button>
                <button class="menu-item" @click="fire('insert-link')">
                  <span class="mi-badge sapphire">⬡</span> 插入链接
                </button>
              </div>
              <div class="menu-divider" />
              <div class="menu-section">
                <div class="menu-heading">注释元素</div>
                <button class="menu-item" @click="fire('insert-span')">
                  <span class="mi-badge mauve">◈</span> 插入 Span
                </button>
                <button class="menu-item" @click="fire('insert-paper')">
                  <span class="mi-badge peach">◉</span> 插入 Paper
                </button>
                <button class="menu-item" @click="fire('insert-ann')">
                  <span class="mi-badge pink">◉</span> 插入 Ann
                </button>
              </div>
            </div>
          </Transition>
        </div>

        <div class="dropdown-wrap" ref="templateRef">
          <button class="act-btn mauve" @click="toggleTemplate">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="3" x2="9" y2="21"/></svg>
            <span class="act-label">片段</span>
            <svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
          </button>
          <Transition name="dropdown">
            <div class="menu-panel compact" v-if="templateOpen">
              <button class="menu-item" @click="fire('load-template')">
                <span class="mi-badge mauve">⟳</span> 插入文本片段
              </button>
              <button class="menu-item" @click="fire('save-template')">
                <span class="mi-badge mauve">↧</span> 保存为片段
              </button>
            </div>
          </Transition>
        </div>

        <div class="window-controls-spacer" />
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  filePath: string | null
  isModified: boolean
}>()

const emit = defineEmits<{
  (e: 'new-file'): void
  (e: 'open-file'): void
  (e: 'save-file'): void
  (e: 'save-as'): void
  (e: 'set-work-dir'): void
  (e: 'insert-meta'): void
  (e: 'insert-section'): void
  (e: 'insert-subsection'): void
  (e: 'insert-h5'): void
  (e: 'insert-h6'): void
  (e: 'insert-graph'): void
  (e: 'insert-table'): void
  (e: 'insert-link'): void
  (e: 'insert-span'): void
  (e: 'insert-paper'): void
  (e: 'insert-ann'): void
  (e: 'load-template'): void
  (e: 'save-template'): void
  (e: 'theme-change', theme: 'light' | 'dark'): void
}>()

const insertOpen = ref(false)
const templateOpen = ref(false)
const insertRef = ref<HTMLElement>()
const templateRef = ref<HTMLElement>()
const theme = ref<'light' | 'dark'>('dark')

const shortPath = computed(() => {
  if (!props.filePath) return ''
  const parts = props.filePath.split(/[/\\]/)
  return parts.length > 2 ? '...' + '/' + parts.slice(-2).join('/') : props.filePath
})

function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  document.documentElement.setAttribute('data-theme', theme.value)
  localStorage.setItem('report-editor-theme', theme.value)
  emit('theme-change', theme.value)
}

function toggleInsert() {
  insertOpen.value = !insertOpen.value
  templateOpen.value = false
}

function toggleTemplate() {
  templateOpen.value = !templateOpen.value
  insertOpen.value = false
}

function fire(event: string) {
  emit(event as any)
  insertOpen.value = false
  templateOpen.value = false
}

function onClickOutside(e: MouseEvent) {
  const t = e.target as HTMLElement
  if (insertRef.value && !insertRef.value.contains(t)) insertOpen.value = false
  if (templateRef.value && !templateRef.value.contains(t)) templateOpen.value = false
}

onMounted(() => {
  document.addEventListener('click', onClickOutside)
  const saved = localStorage.getItem('report-editor-theme') as 'light' | 'dark' | null
  if (saved) {
    theme.value = saved
    document.documentElement.setAttribute('data-theme', saved)
  }
})

onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>

<style scoped>
.titlebar {
  height: 40px;
  background: var(--bg-crust);
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
  position: relative;
  z-index: 100;
  user-select: none;
}

.titlebar::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(to right, var(--accent-blue-med), transparent 25%, transparent 75%, var(--accent-mauve-soft));
  pointer-events: none;
}

.titlebar-drag {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 0 0 8px;
  -webkit-app-region: drag;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 2px;
  -webkit-app-region: no-drag;
}

.window-controls-spacer {
  width: 138px;
  flex-shrink: 0;
  -webkit-app-region: no-drag;
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 6px;
  margin-right: 2px;
}

.brand-mark {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
}

.brand-mark svg {
  width: 100%;
  height: 100%;
}

.brand-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-base);
  letter-spacing: -0.4px;
}

.brand-version {
  font-size: 10px;
  font-weight: 600;
  color: var(--accent-mauve);
  background: var(--accent-mauve-soft);
  padding: 1px 6px;
  border-radius: 99px;
  letter-spacing: 0.3px;
}

.sep {
  width: 1px;
  height: 16px;
  background: var(--border);
  margin: 0 4px;
  border-radius: 1px;
}

.action-group {
  display: flex;
  align-items: center;
  gap: 1px;
}

.act-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  height: 28px;
  padding: 0 8px;
  border: none;
  border-radius: var(--radius-xs);
  background: transparent;
  color: var(--text-subtext1);
  font-family: var(--font-sans);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
  white-space: nowrap;
  position: relative;
}

.act-btn svg {
  width: 15px;
  height: 15px;
  flex-shrink: 0;
}

.act-btn:hover {
  background: var(--bg-surface1);
  color: var(--text-base);
}

.act-btn:active {
  transform: scale(0.96);
}

.act-btn.save:hover {
  background: var(--accent-blue-soft);
  color: var(--accent-blue);
}

.act-btn.save.has-changes {
  color: var(--accent-yellow);
}

.unsaved-dot {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 6px;
  height: 6px;
  background: var(--accent-peach);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--accent-peach);
  animation: dot-pulse 2.5s ease-in-out infinite;
}

@keyframes dot-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.3; transform: scale(0.7); }
}

.act-btn.ghost {
  color: var(--text-overlay0);
}

.act-btn.ghost:hover {
  color: var(--text-subtext0);
  background: var(--bg-surface0);
}

.act-btn.primary {
  background: var(--accent-blue-soft);
  color: var(--accent-blue);
  font-weight: 600;
}

.act-btn.primary:hover {
  background: var(--accent-blue-med);
}

.act-btn.mauve {
  background: var(--accent-mauve-soft);
  color: var(--accent-mauve);
}

.act-btn.mauve:hover {
  background: rgba(203, 166, 247, 0.18);
}

.act-btn.theme-toggle {
  color: var(--accent-yellow);
  padding: 0 6px;
}

.act-btn.theme-toggle:hover {
  background: var(--accent-yellow-soft);
  color: var(--accent-yellow);
}

.act-label {
  font-size: 12px;
}

.chev {
  width: 11px !important;
  height: 11px !important;
  opacity: 0.5;
}

.file-path-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: var(--text-overlay0);
  background: var(--bg-surface0);
  padding: 3px 10px;
  border-radius: 99px;
  border: 1px solid var(--border-subtle);
  max-width: 240px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: var(--font-mono);
  margin-left: 4px;
}

.pill-icon {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
}

.dropdown-wrap {
  position: relative;
}

.menu-panel {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  min-width: 200px;
  background: var(--bg-surface0);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.55), 0 0 0 1px rgba(255, 255, 255, 0.03) inset;
  padding: 6px;
  z-index: 200;
  backdrop-filter: blur(12px);
}

.menu-panel.compact {
  min-width: 170px;
}

.menu-section {
  padding: 2px 0;
}

.menu-heading {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-overlay0);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  padding: 6px 8px 4px;
}

.menu-divider {
  height: 1px;
  background: var(--border-subtle);
  margin: 4px 6px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 6px 8px;
  border: none;
  border-radius: var(--radius-xs);
  background: transparent;
  color: var(--text-subtext0);
  font-family: var(--font-sans);
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
  text-align: left;
}

.menu-item:hover {
  background: var(--accent-blue-soft);
  color: var(--accent-blue);
}

.menu-item:active {
  transform: scale(0.98);
}

.mi-badge {
  width: 22px;
  height: 22px;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  flex-shrink: 0;
  background: var(--bg-surface2);
  color: var(--text-overlay0);
}

.mi-badge.blue { background: var(--accent-blue-soft); color: var(--accent-blue); }
.mi-badge.green { background: var(--accent-green-soft); color: var(--accent-green); }
.mi-badge.teal { background: rgba(148, 226, 213, 0.10); color: var(--accent-teal); }
.mi-badge.yellow { background: var(--accent-yellow-soft); color: var(--accent-yellow); }
.mi-badge.sapphire { background: rgba(116, 199, 236, 0.10); color: var(--accent-sapphire); }
.mi-badge.mauve { background: var(--accent-mauve-soft); color: var(--accent-mauve); }
.mi-badge.peach { background: rgba(250, 179, 135, 0.10); color: var(--accent-peach); }
.mi-badge.pink { background: rgba(245, 194, 231, 0.10); color: var(--accent-pink); }
.mi-badge.surface { background: var(--bg-surface1); color: var(--text-subtext1); }

.dropdown-enter-active { transition: all 180ms var(--ease-out); }
.dropdown-leave-active { transition: all 120ms ease-in; }
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-6px) scale(0.97);
}

.fade-enter-active,
.fade-leave-active { transition: opacity var(--duration-base) ease; }
.fade-enter-from,
.fade-leave-to { opacity: 0; }
</style>
