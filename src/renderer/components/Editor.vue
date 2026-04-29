<template>
  <div ref="editorContainer" class="editor-container"></div>
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
})

onUnmounted(() => {
  themeObserver?.disconnect()
})

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
}
</style>
