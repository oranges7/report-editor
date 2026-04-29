<template>
  <el-dialog
    :title="mode === 'load' ? '插入文本片段' : '保存文本片段'"
    v-model="visibleDialog"
    width="600px"
  >
    <!-- 加载模板模式 -->
    <template v-if="mode === 'load'">
      <el-alert title="选择要插入的文本片段" type="info" show-icon style="margin-bottom: 16px;" />
      <el-table :data="templateList" style="width: 100%" highlight-current-row @current-change="handleCurrentChange">
        <el-table-column prop="name" label="片段名称" width="150" />
        <el-table-column prop="preview" label="内容预览" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click.stop="deleteTemplate(row.name)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </template>
    
    <!-- 保存模板模式 -->
    <template v-else>
      <el-form label-width="100px">
        <el-form-item label="片段名称">
          <el-input v-model="templateName" placeholder="请输入片段名称" />
        </el-form-item>
        <el-form-item label="片段内容">
          <el-input 
            v-model="templateContent" 
            type="textarea" 
            :rows="8" 
            placeholder="输入要保存的文本片段内容"
          />
        </el-form-item>
      </el-form>
    </template>
    
    <template #footer>
      <el-button @click="visibleDialog = false">取消</el-button>
      <el-button 
        type="primary" 
        @click="handleConfirm"
        :disabled="mode === 'load' && !selectedTemplate"
      >
        {{ mode === 'load' ? '插入' : '保存' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'

interface Props {
  visible: boolean
  mode: 'load' | 'save'
  currentContent: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'load-template-content', content: string): void
  (e: 'save-template', name: string): void
}>()

const visibleDialog = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

interface TemplateItem {
  name: string
  content: string
  preview: string
}

const templates = ref<Record<string, string>>({})
const templateList = ref<TemplateItem[]>([])
const selectedTemplate = ref<TemplateItem | null>(null)
const templateName = ref('')
const templateContent = ref('')

const defaultTemplates: Record<string, string> = {
  '差异基因分析': `#section:Differential Expression Analysis:差异基因分析#
#subsection#差异基因筛选标准
本分析使用DESeq2进行差异表达基因分析。差异基因筛选标准为：|log2FoldChange| > 1 且 padj < 0.05。
#graph:差异基因火山图:result/volcano.png#
#graph:差异基因热图:result/heatmap.png#
`,
  'GO富集分析': `#section:GO Enrichment Analysis:GO富集分析#
#subsection#GO富集分析结果
GO（Gene Ontology）富集分析用于研究差异基因在生物学过程（BP）、细胞组分（CC）和分子功能（MF）三个层面的功能注释。
#graph:GO富集柱状图:result/go_bar.png#
#graph:GO富集气泡图:result/go_bubble.png#
`,
  'KEGG通路分析': `#section:KEGG Pathway Analysis:KEGG通路分析#
#subsection#KEGG通路富集结果
KEGG（Kyoto Encyclopedia of Genes and Genomes）是一个整合基因组、化学和系统功能信息的数据库。
#graph:KEGG通路富集分析:result/kegg.png#
`,
  'PCA分析': `#section:PCA Analysis:PCA分析#
#subsection#主成分分析结果
主成分分析（Principal Component Analysis，PCA）是一种降维分析方法，用于可视化样本之间的整体差异。
#graph:PCA分析图:result/pca.png#
`,
  '相关性分析': `#section:Correlation Analysis:相关性分析#
#subsection#样本相关性分析
样本间相关性分析可以评估样本之间的相似程度，通常使用Pearson相关系数进行计算。
#graph:样本相关性热图:result/correlation.png#
`
}

function loadTemplates() {
  const saved = localStorage.getItem('reportTextSnippets')
  if (saved) {
    try {
      templates.value = { ...defaultTemplates, ...JSON.parse(saved) }
    } catch {
      templates.value = defaultTemplates
    }
  } else {
    templates.value = defaultTemplates
  }
  
  templateList.value = Object.entries(templates.value).map(([name, content]) => ({
    name,
    content,
    preview: content.substring(0, 100) + (content.length > 100 ? '...' : '')
  }))
}

function handleCurrentChange(row: TemplateItem | null) {
  selectedTemplate.value = row
}

function deleteTemplate(name: string) {
  const saved = localStorage.getItem('reportTextSnippets')
  let savedTemplates: Record<string, string> = {}
  if (saved) {
    try {
      savedTemplates = JSON.parse(saved)
    } catch {
      savedTemplates = {}
    }
  }
  delete savedTemplates[name]
  localStorage.setItem('reportTextSnippets', JSON.stringify(savedTemplates))
  loadTemplates()
}

onMounted(() => {
  loadTemplates()
})

watch(() => props.visible, (val) => {
  if (val) {
    loadTemplates()
    selectedTemplate.value = null
    templateName.value = ''
    templateContent.value = props.currentContent
  }
})

function handleConfirm() {
  if (props.mode === 'load') {
    if (selectedTemplate.value) {
      emit('load-template-content', selectedTemplate.value.content)
    }
  } else {
    if (templateName.value.trim() && templateContent.value.trim()) {
      const saved = localStorage.getItem('reportTextSnippets')
      let savedTemplates: Record<string, string> = {}
      if (saved) {
        try {
          savedTemplates = JSON.parse(saved)
        } catch {
          savedTemplates = {}
        }
      }
      savedTemplates[templateName.value.trim()] = templateContent.value
      localStorage.setItem('reportTextSnippets', JSON.stringify(savedTemplates))
      emit('save-template', templateName.value.trim())
    }
  }
  visibleDialog.value = false
}
</script>
