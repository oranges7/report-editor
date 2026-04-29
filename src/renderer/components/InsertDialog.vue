<template>
  <el-dialog
    :title="dialogTitle"
    v-model="visibleDialog"
    width="500px"
    @close="resetForm"
  >
    <el-form :model="form" label-width="100px">
      <!-- 元信息 -->
      <template v-if="type === 'meta'">
        <el-form-item label="Custom">
          <el-input v-model="form.custom" placeholder="名字" />
        </el-form-item>
        <el-form-item label="Contract">
          <el-input v-model="form.contract" placeholder="项目编号" />
        </el-form-item>
        <el-form-item label="Title">
          <el-input v-model="form.title" placeholder="题目" />
        </el-form-item>
      </template>
      
      <!-- 章节 -->
      <template v-else-if="type === 'section'">
        <el-form-item label="英文标题">
          <el-input v-model="form.englishTitle" placeholder="英文题目" />
        </el-form-item>
        <el-form-item label="中文标题">
          <el-input v-model="form.chineseTitle" placeholder="中文标题" />
        </el-form-item>
      </template>
      
      <!-- 图片 -->
      <template v-else-if="type === 'graph'">
        <el-form-item label="标题（可选）">
          <el-input v-model="form.title" placeholder="图片标题（可选）" />
        </el-form-item>
        <el-form-item label="文件路径" required>
          <el-input v-model="form.filePath" placeholder="相对路径">
            <template #append>
              <el-button @click="selectImageFile">选择图片</el-button>
            </template>
          </el-input>
        </el-form-item>
      </template>
      
      <!-- 表格 -->
      <template v-else-if="type === 'table'">
        <el-form-item label="标题（可选）">
          <el-input v-model="form.title" placeholder="表格标题（可选）" />
        </el-form-item>
        <el-form-item label="文件路径" required>
          <el-input v-model="form.filePath" placeholder="相对路径">
            <template #append>
              <el-button @click="selectTableFile">选择表格</el-button>
            </template>
          </el-input>
        </el-form-item>
      </template>
      
      <!-- 链接 -->
      <template v-else-if="type === 'link'">
        <el-form-item label="标题（可选）">
          <el-input v-model="form.title" placeholder="链接标题（可选）" />
        </el-form-item>
        <el-form-item label="文件路径" required>
          <el-input v-model="form.filePath" placeholder="相对路径">
            <template #append>
              <el-button @click="selectAnyFile">选择文件</el-button>
            </template>
          </el-input>
        </el-form-item>
      </template>
      
      <!-- Span -->
      <template v-else-if="type === 'span'">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="标题" />
        </el-form-item>
      </template>
      
      <!-- Paper -->
      <template v-else-if="type === 'paper'">
        <el-form-item label="内容">
          <el-input v-model="form.paper" type="textarea" :rows="4" placeholder="Paper 内容" />
        </el-form-item>
      </template>
      
      <!-- Ann -->
      <template v-else-if="type === 'ann'">
        <el-form-item label="内容">
          <el-input v-model="form.ann" type="textarea" :rows="4" placeholder="Ann 内容" />
        </el-form-item>
      </template>
    </el-form>
    
    <template #footer>
      <el-button @click="visibleDialog = false">取消</el-button>
      <el-button type="primary" @click="handleConfirm">插入</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  visible: boolean
  type: string
  workDir: string | null
}

const props = withDefaults(defineProps<Props>(), {
  workDir: null
})

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'confirm', text: string): void
}>()

const visibleDialog = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

interface FormData {
  custom: string
  contract: string
  title: string
  englishTitle: string
  chineseTitle: string
  filePath: string
  paper: string
  ann: string
}

const form = ref<FormData>({
  custom: '',
  contract: '',
  title: '',
  englishTitle: '',
  chineseTitle: '',
  filePath: '',
  paper: '',
  ann: ''
})

const dialogTitle = computed(() => {
  const titles: Record<string, string> = {
    meta: '插入元信息',
    section: '插入章节',
    graph: '插入图片',
    table: '插入表格',
    link: '插入链接',
    span: '插入 Span',
    paper: '插入 Paper',
    ann: '插入 Ann'
  }
  return titles[props.type] || '插入元素'
})

function resetForm() {
  form.value = {
    custom: '',
    contract: '',
    title: '',
    englishTitle: '',
    chineseTitle: '',
    filePath: '',
    paper: '',
    ann: ''
  }
}

async function selectImageFile() {
  const filePath = await window.electronAPI.selectFile('image')
  if (filePath && props.workDir) {
    const relativePath = await window.electronAPI.relativePath(props.workDir, filePath)
    form.value.filePath = relativePath
  } else if (filePath) {
    form.value.filePath = filePath
  }
}

async function selectTableFile() {
  const filePath = await window.electronAPI.selectFile('table')
  if (filePath && props.workDir) {
    const relativePath = await window.electronAPI.relativePath(props.workDir, filePath)
    form.value.filePath = relativePath
  } else if (filePath) {
    form.value.filePath = filePath
  }
}

async function selectAnyFile() {
  const filePath = await window.electronAPI.selectFile('any')
  if (filePath && props.workDir) {
    const relativePath = await window.electronAPI.relativePath(props.workDir, filePath)
    form.value.filePath = relativePath
  } else if (filePath) {
    form.value.filePath = filePath
  }
}

function handleConfirm() {
  let text = ''
  
  switch (props.type) {
    case 'meta':
      text = `#Custom:${form.value.custom}\n#Contract:${form.value.contract}\n#Title:${form.value.title}\n`
      break
    case 'section':
      text = `#section:${form.value.englishTitle}:${form.value.chineseTitle}#\n`
      break
    case 'graph':
      text = `#graph:${form.value.title}:${form.value.filePath}#\n`
      break
    case 'table':
      text = `#table:${form.value.title}:${form.value.filePath}#\n`
      break
    case 'link':
      text = `#link:${form.value.title}:${form.value.filePath}#\n`
      break
    case 'span':
      text = `#span:${form.value.title}#\n`
      break
    case 'paper':
      text = `#paper:${form.value.paper}#\n`
      break
    case 'ann':
      text = `#ann:${form.value.ann}#\n`
      break
  }
  
  emit('confirm', text)
  visibleDialog.value = false
}
</script>
