<template>
  <div class="tasks-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Входящие задачи ({{ tasks.length }})</span>
          <div class="header-buttons">
            <el-button type="danger" @click="closeSelectedTasksWithEmailRemoval" :disabled="!selectedTasks.length">
              Закрыть и удалить почту
            </el-button>
            <el-button type="primary" @click="closeSelectedTasks" :disabled="!selectedTasks.length">
              Закрыть выбранные
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="sortedTasks"
        :row-style="rowStyle"
        @selection-change="handleSelectionChange"
        style="width: 100%">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="100">
          <template #default="scope">
            <span class="clickable-cell" @click="openTaskFormDialog(scope.row)">
              {{ scope.row.id }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="text" label="Текст" show-overflow-tooltip min-width="300">
          <template #default="scope">
            <span class="clickable-cell" @click="openTaskFormDialog(scope.row)">
              {{ scope.row.text || 'Нет текста' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="step" label="Этап" width="140">
          <template #default="scope">
            <span v-if="scope.row.step">{{ scope.row.step + '/3' }}</span>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column prop="due" label="Дедлайн" width="180">
          <template #default="scope">
            <span>{{ deadlineText(scope.row) }}</span>
          </template>
        </el-table-column>

      </el-table>
    </el-card>

    <!-- Диалог редактирования задачи -->
    <el-dialog
      v-model="taskFormDialogVisible"
      title="Редактирование задачи"
      width="80%"
      :close-on-click-modal="false">
      <TaskForm
        v-if="taskFormDialogVisible"
        :form-id="selectedFormId"
        :task-id="selectedTaskId"
        :current-values="selectedTaskValues"
        :task-comments="selectedTaskComments"
        :task-attachments="selectedTaskAttachments"
        @close="closeTaskFormDialog"
        @saved="handleTaskSaved" />
    </el-dialog>


  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import TaskForm from '../components/TaskForm.vue'
import api from '../api'

const tasks = ref([])
const loading = ref(false)
const selectedTasks = ref([])
const dialogVisible = ref(false)
const currentTask = ref({
  id: null,
  platform: '',
  solution: '',
  due_date: null
})

// Новые переменные для формы задачи
const taskFormDialogVisible = ref(false)
const selectedFormId = ref(null)
const selectedTaskId = ref(null)
const selectedTaskValues = ref({})
const selectedTaskComments = ref([])
const selectedTaskAttachments = ref([])

const fetchTasks = async () => {
  loading.value = true
  try {
    const response = await api.get('/inbox_full')
    tasks.value = response.data
  } catch (error) {
    ElMessage.error('Ошибка при загрузке задач')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const sortedTasks = computed(() => {
  // сортировка по last_modified_date по убыванию, если есть, иначе по due
  return [...tasks.value].sort((a, b) => {
    const aDate = a.last_modified_date ? new Date(a.last_modified_date).getTime() : (a.due ? new Date(a.due).getTime() : 0)
    const bDate = b.last_modified_date ? new Date(b.last_modified_date).getTime() : (b.due ? new Date(b.due).getTime() : 0)
    return bDate - aDate
  })
})

const handleSelectionChange = (selection) => {
  selectedTasks.value = selection
}

const closeSelectedTasks = async () => {
  try {
    for (const task of selectedTasks.value) {
      const commentData = {
        text: "Задача закрыта",
        action: "finished",
        field_updates: [
          {
            id: 41,
            type: "catalog",
            name: "Площадка/Place",
            value: {
              item_id: 81073933,
              item_ids: [81073933],
              headers: ["Площадки"],
              values: ["Nano"],
              rows: [["Nano"]]
            }
          },
          {
            id: 27,
            type: "text",
            name: "Решение/Solution",
            value: "Задача автоматически закрыта"
          }
        ]
      }
      await api.post(`/tasks/${task.id}/comment`, commentData)
    }
    ElMessage.success('Выбранные задачи успешно закрыты')
    fetchTasks()
  } catch (error) {
    ElMessage.error('Ошибка при закрытии задач')
    console.error(error)
  }
}

const closeSelectedTasksWithEmailRemoval = async () => {
  try {
    for (const task of selectedTasks.value) {
      const commentData = {
        text: "",
        action: "finished",
        field_updates: [
          {
            id: 41,
            type: "catalog",
            name: "Площадка/Place",
            value: {
              item_id: 81073933,
              item_ids: [81073933],
              headers: ["Площадки"],
              values: ["Nano"],
              rows: [["Nano"]]
            }
          },
          {
            id: 27,
            type: "text",
            name: "Решение/Solution",
            value: "Задача автоматически закрыта"
          },
          {
            id: 7,
            type: "email",
            name: "Эл. почта/E-mail",
            value: ""
          }
        ]
      }
      await api.post(`/tasks/${task.id}/comment`, commentData)
    }
    ElMessage.success('Выбранные задачи успешно закрыты с удалением почты')
    fetchTasks()
  } catch (error) {
    ElMessage.error('Ошибка при закрытии задач')
    console.error(error)
  }
}

function deadlineText(row) {
  if (row.is_frozen) return 'SLA заморожен'
  if (!row.due) return '—'
  const dueTime = new Date(row.due).getTime()
  const diff = dueTime - Date.now()
  if (diff < 0) return 'Просрочено'
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days > 0) return `${days} д`
  const hours = Math.floor(diff / 1000 / 60 / 60)
  const minutes = Math.floor((diff / 1000 / 60) % 60)
  if (hours > 0) return `${hours} ч ${minutes} мин`
  return `${minutes} мин`
}

function rowStyle({ row }) {
  if (row.is_frozen) return { background: '#e6f0ff', color: '#2366a8' }
  if (row.color === 'red') return { background: '#ffeaea' }
  if (row.color === 'yellow') return { background: '#fffbe6' }
  return {}
}

// Методы для работы с формой задачи
const openTaskFormDialog = async (task) => {
  try {
    // Получаем данные формы для задачи
    const response = await api.get(`/tasks/${task.id}/form`)
    selectedFormId.value = response.data.form.form_id
    selectedTaskId.value = task.id
    selectedTaskValues.value = response.data.current_values
    selectedTaskComments.value = response.data.comments || []
    selectedTaskAttachments.value = response.data.attachments || []
    taskFormDialogVisible.value = true
  } catch (error) {
    ElMessage.error('Ошибка при загрузке формы задачи')
    console.error(error)
  }
}

const closeTaskFormDialog = () => {
  taskFormDialogVisible.value = false
  selectedFormId.value = null
  selectedTaskId.value = null
  selectedTaskValues.value = {}
  selectedTaskComments.value = []
  selectedTaskAttachments.value = []
}

const handleTaskSaved = () => {
  // Обновляем список задач после сохранения
  fetchTasks()
}

onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>
.tasks-container {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.frozen-label {
  color: #2366a8;
  font-weight: bold;
}

.clickable-cell {
  cursor: pointer;
  color: #409EFF;
  transition: color 0.3s;
}

.clickable-cell:hover {
  color: #66b1ff;
  text-decoration: underline;
}
</style> 