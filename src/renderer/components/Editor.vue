<template>
  <div ref="editorContainer" class="editor-container" @contextmenu.prevent="onContextMenu">
    <div
      v-if="contextMenu.visible"
      class="ctx-menu"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      @mousedown.stop
    >
      <button class="ctx-item" :class="{ disabled: !canCopy }" @click="ctxCopy">
        <span class="ctx-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
        </span>
        复制<span class="ctx-shortcut">Ctrl+C</span>
      </button>
      <button class="ctx-item" :class="{ disabled: !canCopy }" @click="ctxCut">
        <span class="ctx-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><line x1="20" y1="4" x2="8.12" y2="15.88"/><line x1="14.47" y1="14.48" x2="20" y2="20"/><line x1="8.12" y1="8.12" x2="12" y2="12"/></svg>
        </span>
        剪切<span class="ctx-shortcut">Ctrl+X</span>
      </button>
      <button class="ctx-item" @click="ctxPaste">
        <span class="ctx-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/></svg>
        </span>
        粘贴<span class="ctx-shortcut">Ctrl+V</span>
      </button>
      <div class="ctx-divider" />
      <button class="ctx-item" @click="ctxSelectAll">
        <span class="ctx-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
        </span>
        全选<span class="ctx-shortcut">Ctrl+A</span>
      </button>
      <button class="ctx-item" @click="ctxFind">
        <span class="ctx-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        </span>
        查找替换<span class="ctx-shortcut">Ctrl+F</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { EditorView, keymap, Panel, showPanel } from '@codemirror/view'
import { EditorState, StateEffect, StateField, Compartment } from '@codemirror/state'
import { defaultKeymap, history, historyKeymap, indentWithTab } from '@codemirror/commands'
import { highlightSelectionMatches } from '@codemirror/search'
import { lineNumbers, highlightActiveLine, highlightActiveLineGutter } from '@codemirror/view'
import { syntaxHighlighting, defaultHighlightStyle } from '@codemirror/language'
import { StreamLanguage } from '@codemirror/language'

const props = defineProps<{
  content: string
}>()

const emit = defineEmits<{
  (e: 'update:content', value: string): void
  (e: 'change'): void
  (e: 'toggle-wrap', enabled: boolean): void
}>()

const editorContainer = ref<HTMLElement>()
let editorView: EditorView | null = null
const themeCompartment = new Compartment()
const wrapCompartment = new Compartment()

const WORD_WRAP_KEY = 'report-editor-word-wrap'
const wordWrap = ref(localStorage.getItem(WORD_WRAP_KEY) !== 'false')

const reportLanguage = StreamLanguage.define({
  name: 'report',
  startState: () => ({}),
  token: (stream) => {
    if (stream.match('#Custom:')) return 'keyword'
    if (stream.match('#Contract:')) return 'keyword'
    if (stream.match('#Title:')) return 'keyword'
    if (stream.match('#section:')) return 'keyword'
    if (stream.match('#subsection#')) return 'keyword'
    if (stream.match('#h5#')) return 'keyword'
    if (stream.match('#h6#')) return 'keyword'
    if (stream.match('#graph:')) return 'string'
    if (stream.match('#table:')) return 'string'
    if (stream.match('#link:')) return 'string'
    if (stream.match('#span:')) return 'comment'
    if (stream.match('#paper:')) return 'comment'
    if (stream.match('#ann:')) return 'comment'
    if (stream.match(/#.*?#/)) return 'string'
    stream.next()
    return null
  }
})

const togglePanel = StateEffect.define<boolean>()

const panelState = StateField.define<boolean>({
  create: () => false,
  update: (value, tr) => {
    for (const effect of tr.effects) {
      if (effect.is(togglePanel)) return effect.value
    }
    return value
  }
})

function createSearchPanel(view: EditorView): Panel {
  const dom = document.createElement('div')
  dom.className = 'cm-search-panel'
  dom.innerHTML = `
    <div class="cm-search-row">
      <label>搜索:</label>
      <input type="text" class="cm-search-input" placeholder="输入搜索内容..." />
      <button class="cm-search-btn" data-action="prev" title="上一处">↑</button>
      <button class="cm-search-btn" data-action="next" title="下一处">↓</button>
      <span class="cm-search-count"></span>
    </div>
    <div class="cm-search-row">
      <label>替换:</label>
      <input type="text" class="cm-replace-input" placeholder="输入替换内容..." />
      <button class="cm-search-btn" data-action="replace">替换</button>
      <button class="cm-search-btn" data-action="replace-all">全部替换</button>
      <button class="cm-search-btn cm-search-close" data-action="close">关闭</button>
    </div>
  `

  const searchInput = dom.querySelector('.cm-search-input') as HTMLInputElement
  const replaceInput = dom.querySelector('.cm-replace-input') as HTMLInputElement
  const countSpan = dom.querySelector('.cm-search-count') as HTMLSpanElement

  function findAll(text: string): { from: number; to: number }[] {
    if (!text) return []
    const results: { from: number; to: number }[] = []
    const doc = view.state.doc
    const docText = doc.toString()
    let pos = 0
    while (true) {
      const idx = docText.indexOf(text, pos)
      if (idx === -1) break
      results.push({ from: idx, to: idx + text.length })
      pos = idx + 1
    }
    return results
  }

  let currentMatchIndex = -1
  let matches: { from: number; to: number }[] = []

  function updateMatches() {
    const query = searchInput.value
    matches = findAll(query)
    currentMatchIndex = -1
    countSpan.textContent = query ? `共 ${matches.length} 处` : ''
  }

  function goToMatch(index: number) {
    if (matches.length === 0) return
    currentMatchIndex = ((index % matches.length) + matches.length) % matches.length
    const match = matches[currentMatchIndex]
    view.dispatch({
      selection: { anchor: match.from, head: match.to },
      effects: EditorView.scrollIntoView(match.from)
    })
  }

  searchInput.addEventListener('input', () => {
    updateMatches()
  })

  searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      if (matches.length > 0) {
        if (e.shiftKey) {
          goToMatch(currentMatchIndex - 1)
        } else {
          goToMatch(currentMatchIndex + 1)
        }
      }
    }
    if (e.key === 'Escape') {
      view.dispatch({ effects: togglePanel.of(false) })
    }
  })

  dom.addEventListener('click', (e) => {
    const target = e.target as HTMLElement
    if (!target.classList.contains('cm-search-btn')) return

    const action = target.dataset.action
    const query = searchInput.value

    switch (action) {
      case 'prev':
        if (matches.length > 0) {
          goToMatch(currentMatchIndex - 1)
        }
        break
      case 'next':
        if (matches.length > 0) {
          goToMatch(currentMatchIndex + 1)
        }
        break
      case 'replace':
        if (query && replaceInput.value && matches.length > 0) {
          const match = matches[0]
          view.dispatch({
            changes: { from: match.from, to: match.to, insert: replaceInput.value }
          })
          updateMatches()
        }
        break
      case 'replace-all':
        if (query && replaceInput.value && matches.length > 0) {
          const changes = matches.map(m => ({ from: m.from, to: m.to, insert: replaceInput.value }))
          view.dispatch({ changes })
          updateMatches()
        }
        break
      case 'close':
        view.dispatch({ effects: togglePanel.of(false) })
        break
    }
  })

  setTimeout(() => searchInput.focus(), 0)

  return { dom, top: true }
}

function getDarkTheme() {
  return EditorView.theme({
    '&': {
      height: '100%',
      fontSize: '14px',
      backgroundColor: '#151825',
      color: '#cdd6f4'
    },
    '.cm-scroller': {
      height: '100%',
      fontFamily: '"JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", monospace',
      lineHeight: '1.7'
    },
    '.cm-content': {
      minHeight: '100%',
      fontFamily: '"JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", monospace',
      caretColor: '#89b4fa',
      padding: '16px 0'
    },
    '.cm-content ::selection': {
      backgroundColor: 'rgba(137, 180, 250, 0.25)'
    },
    '.cm-cursor, .cm-dropCursor': {
      borderLeftColor: '#89b4fa',
      borderLeftWidth: '2px'
    },
    '.cm-activeLine': {
      backgroundColor: 'rgba(137, 180, 250, 0.05)'
    },
    '.cm-activeLineGutter': {
      backgroundColor: 'rgba(137, 180, 250, 0.07)'
    },
    '.cm-gutters': {
      backgroundColor: '#151825',
      borderRight: '1px solid rgba(205, 214, 244, 0.06)',
      color: '#6c7086',
      fontFamily: '"JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", monospace'
    },
    '.cm-lineNumbers .cm-gutterElement': {
      padding: '0 10px 0 16px',
      fontSize: '12px'
    },
    '.cm-foldPlaceholder': {
      backgroundColor: 'rgba(137, 180, 250, 0.08)',
      border: '1px solid rgba(137, 180, 250, 0.15)',
      color: '#89b4fa',
      borderRadius: '4px'
    },
    '.cm-selectionBackground, ::selection': {
      backgroundColor: 'rgba(137, 180, 250, 0.18) !important'
    },
    '.cm-selectionMatch': {
      backgroundColor: 'rgba(249, 226, 175, 0.12)'
    },
    '.cm-matchingBracket, .cm-nonmatchingBracket': {
      backgroundColor: 'rgba(137, 180, 250, 0.12)',
      outline: '1px solid rgba(137, 180, 250, 0.3)'
    },
    '.cm-tooltip': {
      backgroundColor: '#1a1e2e',
      border: '1px solid rgba(205, 214, 244, 0.06)',
      color: '#cdd6f4',
      borderRadius: '8px',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)'
    },
    '.cm-panels': {
      backgroundColor: '#1a1e2e',
      borderBottom: '1px solid rgba(205, 214, 244, 0.06)'
    },
    '.cm-panels.cm-panels-top': {
      borderBottom: '1px solid rgba(205, 214, 244, 0.06)'
    },
    '.cm-search-panel': {
      padding: '10px 16px',
      background: '#1a1e2e',
      borderBottom: '1px solid rgba(205, 214, 244, 0.06)'
    },
    '.cm-search-row': {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      marginBottom: '6px'
    },
    '.cm-search-row:last-child': {
      marginBottom: '0'
    },
    '.cm-search-row label': {
      fontSize: '12px',
      color: '#a6adc8',
      width: '40px',
      fontWeight: '500'
    },
    '.cm-search-input, .cm-replace-input': {
      padding: '5px 10px',
      border: '1px solid rgba(205, 214, 244, 0.06)',
      borderRadius: '6px',
      fontSize: '12.5px',
      width: '200px',
      backgroundColor: '#151825',
      color: '#cdd6f4',
      fontFamily: '"JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", monospace',
      transition: 'border-color 120ms ease, box-shadow 120ms ease'
    },
    '.cm-search-input:focus, .cm-replace-input:focus': {
      outline: 'none',
      borderColor: '#89b4fa',
      boxShadow: '0 0 0 2px rgba(137, 180, 250, 0.10), 0 0 16px rgba(137, 180, 250, 0.08)'
    },
    '.cm-search-input::placeholder, .cm-replace-input::placeholder': {
      color: '#6c7086'
    },
    '.cm-search-btn': {
      padding: '5px 10px',
      border: '1px solid rgba(205, 214, 244, 0.06)',
      background: '#1f2437',
      borderRadius: '6px',
      cursor: 'pointer',
      fontSize: '12px',
      color: '#a6adc8',
      fontWeight: '500',
      transition: 'all 120ms ease'
    },
    '.cm-search-btn:hover': {
      background: 'rgba(137, 180, 250, 0.10)',
      borderColor: '#89b4fa',
      color: '#89b4fa'
    },
    '.cm-search-close': {
      marginLeft: 'auto'
    },
    '.cm-search-count': {
      fontSize: '11px',
      color: '#6c7086'
    },
    '.ͼb': { color: '#cba6f7' },
    '.ͼc': { color: '#f38ba8' },
    '.ͼd': { color: '#fab387' },
    '.ͼe': { color: '#f9e2af' },
    '.ͼf': { color: '#a6e3a1' },
    '.ͼg': { color: '#94e2d5' },
    '.ͼh': { color: '#89b4fa' },
    '.ͼi': { color: '#f5c2e7' }
  })
}

function getLightTheme() {
  return EditorView.theme({
    '&': {
      height: '100%',
      fontSize: '14px',
      backgroundColor: '#e6e9ef',
      color: '#4c4f69'
    },
    '.cm-scroller': {
      height: '100%',
      fontFamily: '"JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", monospace',
      lineHeight: '1.7'
    },
    '.cm-content': {
      minHeight: '100%',
      fontFamily: '"JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", monospace',
      caretColor: '#1e66f5',
      padding: '16px 0'
    },
    '.cm-content ::selection': {
      backgroundColor: 'rgba(30, 102, 245, 0.18)'
    },
    '.cm-cursor, .cm-dropCursor': {
      borderLeftColor: '#1e66f5',
      borderLeftWidth: '2px'
    },
    '.cm-activeLine': {
      backgroundColor: 'rgba(30, 102, 245, 0.05)'
    },
    '.cm-activeLineGutter': {
      backgroundColor: 'rgba(30, 102, 245, 0.06)'
    },
    '.cm-gutters': {
      backgroundColor: '#e6e9ef',
      borderRight: '1px solid rgba(76, 79, 105, 0.08)',
      color: '#9ca0b0',
      fontFamily: '"JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", monospace'
    },
    '.cm-lineNumbers .cm-gutterElement': {
      padding: '0 10px 0 16px',
      fontSize: '12px'
    },
    '.cm-foldPlaceholder': {
      backgroundColor: 'rgba(30, 102, 245, 0.06)',
      border: '1px solid rgba(30, 102, 245, 0.12)',
      color: '#1e66f5',
      borderRadius: '4px'
    },
    '.cm-selectionBackground, ::selection': {
      backgroundColor: 'rgba(30, 102, 245, 0.14) !important'
    },
    '.cm-selectionMatch': {
      backgroundColor: 'rgba(223, 142, 29, 0.12)'
    },
    '.cm-matchingBracket, .cm-nonmatchingBracket': {
      backgroundColor: 'rgba(30, 102, 245, 0.10)',
      outline: '1px solid rgba(30, 102, 245, 0.25)'
    },
    '.cm-tooltip': {
      backgroundColor: '#eff1f5',
      border: '1px solid rgba(76, 79, 105, 0.10)',
      color: '#4c4f69',
      borderRadius: '8px',
      boxShadow: '0 8px 32px rgba(76, 79, 105, 0.12)'
    },
    '.cm-panels': {
      backgroundColor: '#e6e9ef',
      borderBottom: '1px solid rgba(76, 79, 105, 0.10)'
    },
    '.cm-panels.cm-panels-top': {
      borderBottom: '1px solid rgba(76, 79, 105, 0.10)'
    },
    '.cm-search-panel': {
      padding: '10px 16px',
      background: '#e6e9ef',
      borderBottom: '1px solid rgba(76, 79, 105, 0.10)'
    },
    '.cm-search-row': {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      marginBottom: '6px'
    },
    '.cm-search-row:last-child': {
      marginBottom: '0'
    },
    '.cm-search-row label': {
      fontSize: '12px',
      color: '#5c5f77',
      width: '40px',
      fontWeight: '500'
    },
    '.cm-search-input, .cm-replace-input': {
      padding: '5px 10px',
      border: '1px solid rgba(76, 79, 105, 0.12)',
      borderRadius: '6px',
      fontSize: '12.5px',
      width: '200px',
      backgroundColor: '#eff1f5',
      color: '#4c4f69',
      fontFamily: '"JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", monospace',
      transition: 'border-color 120ms ease, box-shadow 120ms ease'
    },
    '.cm-search-input:focus, .cm-replace-input:focus': {
      outline: 'none',
      borderColor: '#1e66f5',
      boxShadow: '0 0 0 2px rgba(30, 102, 245, 0.10), 0 0 16px rgba(30, 102, 245, 0.06)'
    },
    '.cm-search-input::placeholder, .cm-replace-input::placeholder': {
      color: '#9ca0b0'
    },
    '.cm-search-btn': {
      padding: '5px 10px',
      border: '1px solid rgba(76, 79, 105, 0.12)',
      background: '#ccd0da',
      borderRadius: '6px',
      cursor: 'pointer',
      fontSize: '12px',
      color: '#5c5f77',
      fontWeight: '500',
      transition: 'all 120ms ease'
    },
    '.cm-search-btn:hover': {
      background: 'rgba(30, 102, 245, 0.08)',
      borderColor: '#1e66f5',
      color: '#1e66f5'
    },
    '.cm-search-close': {
      marginLeft: 'auto'
    },
    '.cm-search-count': {
      fontSize: '11px',
      color: '#9ca0b0'
    },
    '.ͼb': { color: '#8839ef' },
    '.ͼc': { color: '#d20f39' },
    '.ͼd': { color: '#fe640b' },
    '.ͼe': { color: '#df8e1d' },
    '.ͼf': { color: '#40a02b' },
    '.ͼg': { color: '#179299' },
    '.ͼh': { color: '#1e66f5' },
    '.ͼi': { color: '#ea76cb' }
  })
}

function getCurrentTheme(): 'light' | 'dark' {
  return (document.documentElement.getAttribute('data-theme') as 'light' | 'dark') || 'dark'
}

function createEditorState(content: string) {
  const theme = getCurrentTheme()
  return EditorState.create({
    doc: content,
    extensions: [
      lineNumbers(),
      highlightActiveLine(),
      highlightActiveLineGutter(),
      history(),
      highlightSelectionMatches(),
      syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
      reportLanguage,
      panelState,
      showPanel.from(panelState, (on) => on ? createSearchPanel : null),
      keymap.of([
        ...defaultKeymap,
        ...historyKeymap,
        indentWithTab,
        { key: 'Mod-f', run: (view) => {
          view.dispatch({ effects: togglePanel.of(true) })
          return true
        }},
        { key: 'Mod-h', run: (view) => {
          view.dispatch({ effects: togglePanel.of(true) })
          return true
        }},
        { key: 'Escape', run: (view) => {
          if (view.state.field(panelState)) {
            view.dispatch({ effects: togglePanel.of(false) })
            return true
          }
          return false
        }}
      ]),
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          emit('update:content', update.state.doc.toString())
          emit('change')
        }
      }),
      themeCompartment.of(theme === 'dark' ? getDarkTheme() : getLightTheme()),
      wrapCompartment.of(wordWrap.value ? [EditorView.lineWrapping] : []),
    ]
  })
}

function applyTheme(theme: 'light' | 'dark') {
  if (!editorView) return
  editorView.dispatch({
    effects: themeCompartment.reconfigure(theme === 'dark' ? getDarkTheme() : getLightTheme())
  })
}

function setWordWrap(enabled: boolean) {
  wordWrap.value = enabled
  localStorage.setItem(WORD_WRAP_KEY, String(enabled))
  if (!editorView) return
  editorView.dispatch({
    effects: wrapCompartment.reconfigure(enabled ? [EditorView.lineWrapping] : [])
  })
  emit('toggle-wrap', enabled)
}

const contextMenu = ref({ visible: false, x: 0, y: 0 })
const canCopy = ref(false)

function onContextMenu(e: MouseEvent) {
  if (!editorView) return
  const sel = editorView.state.selection.main
  canCopy.value = sel.from !== sel.to

  const container = editorContainer.value!
  const rect = container.getBoundingClientRect()
  let x = e.clientX - rect.left
  let y = e.clientY - rect.top
  if (x + 200 > rect.width) x = rect.width - 200
  if (y + 200 > rect.height) y = rect.height - 200
  if (x < 0) x = 0
  if (y < 0) y = 0

  contextMenu.value = { visible: true, x, y }
}

function closeContextMenu() {
  contextMenu.value.visible = false
}

function ctxCopy() {
  closeContextMenu()
  if (!editorView) return
  const sel = editorView.state.selection.main
  if (sel.from === sel.to) return
  const text = editorView.state.doc.sliceString(sel.from, sel.to)
  navigator.clipboard.writeText(text)
}

function ctxCut() {
  closeContextMenu()
  if (!editorView) return
  const sel = editorView.state.selection.main
  if (sel.from === sel.to) return
  const text = editorView.state.doc.sliceString(sel.from, sel.to)
  navigator.clipboard.writeText(text)
  editorView.dispatch({
    changes: { from: sel.from, to: sel.to, insert: '' },
    selection: { anchor: sel.from }
  })
}

async function ctxPaste() {
  closeContextMenu()
  if (!editorView) return
  try {
    const text = await navigator.clipboard.readText()
    const sel = editorView.state.selection.main
    editorView.dispatch({
      changes: { from: sel.from, to: sel.to, insert: text },
      selection: { anchor: sel.from + text.length }
    })
  } catch { /* clipboard access denied */ }
}

function ctxSelectAll() {
  closeContextMenu()
  if (!editorView) return
  editorView.dispatch({
    selection: { anchor: 0, head: editorView.state.doc.length }
  })
  editorView.focus()
}

function ctxFind() {
  closeContextMenu()
  if (!editorView) return
  editorView.dispatch({ effects: togglePanel.of(true) })
}

let themeObserver: MutationObserver | null = null

onMounted(() => {
  if (editorContainer.value) {
    editorView = new EditorView({
      state: createEditorState(props.content),
      parent: editorContainer.value
    })
  }

  themeObserver = new MutationObserver(() => {
    const theme = getCurrentTheme()
    applyTheme(theme)
  })
  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme']
  })

  document.addEventListener('mousedown', onDocMouseDown)
})

onUnmounted(() => {
  themeObserver?.disconnect()
  document.removeEventListener('mousedown', onDocMouseDown)
})

function onDocMouseDown(e: MouseEvent) {
  if (contextMenu.value.visible) {
    const target = e.target as HTMLElement
    if (!target.closest('.ctx-menu')) {
      closeContextMenu()
    }
  }
}

watch(() => props.content, (newContent) => {
  if (editorView && editorView.state.doc.toString() !== newContent) {
    editorView.dispatch({
      changes: {
        from: 0,
        to: editorView.state.doc.length,
        insert: newContent
      }
    })
  }
})

function insertText(text: string) {
  if (editorView) {
    const state = editorView.state
    const from = state.selection.main.from
    const to = state.selection.main.to
    editorView.dispatch({
      changes: { from, to, insert: text },
      selection: { anchor: from + text.length }
    })
  }
}

function getSelectedText(): string {
  if (editorView) {
    const state = editorView.state
    const from = state.selection.main.from
    const to = state.selection.main.to
    return state.doc.sliceString(from, to)
  }
  return ''
}

defineExpose({
  insertText,
  getSelectedText,
  setWordWrap,
  wordWrap
})
</script>

<style scoped>
.editor-container {
  height: 100%;
  width: 100%;
  position: relative;
}

.ctx-menu {
  position: absolute;
  z-index: 300;
  min-width: 200px;
  background: var(--bg-surface0);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.55), 0 0 0 1px rgba(255, 255, 255, 0.03) inset;
  padding: 4px;
  backdrop-filter: blur(12px);
  animation: ctx-in 120ms cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes ctx-in {
  from { opacity: 0; transform: scale(0.96) translateY(-4px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.ctx-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 7px 12px;
  border: none;
  border-radius: var(--radius-xs);
  background: transparent;
  color: var(--text-subtext0);
  font-family: var(--font-sans);
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
  transition: all 100ms ease;
  text-align: left;
}

.ctx-item:hover:not(.disabled) {
  background: var(--accent-blue-soft);
  color: var(--accent-blue);
}

.ctx-item:active:not(.disabled) {
  transform: scale(0.98);
}

.ctx-item.disabled {
  opacity: 0.35;
  cursor: default;
}

.ctx-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.ctx-icon svg {
  width: 14px;
  height: 14px;
}

.ctx-shortcut {
  margin-left: auto;
  font-size: 10.5px;
  color: var(--text-overlay0);
  font-family: var(--font-mono);
  letter-spacing: -0.2px;
}

.ctx-item:hover:not(.disabled) .ctx-shortcut {
  color: var(--accent-blue);
  opacity: 0.7;
}

.ctx-divider {
  height: 1px;
  background: var(--border-subtle);
  margin: 4px 6px;
}
</style>
