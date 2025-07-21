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
        <el-table-column prop="id" label="ID" width="100" />
        <el-table-column prop="text" label="Текст" show-overflow-tooltip min-width="300">
          <template #default="scope">
            {{ scope.row.text || 'Нет текста' }}
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
        <!-- <el-table-column label="Заморожена" width="120">
          <template #default="scope">
            <span v-if="scope.row.is_frozen" class="frozen-label">Да</span>
            <span v-else>Нет</span>
          </template>
        </el-table-column> -->
        <!-- <el-table-column label="Действия" width="120" fixed="right">
          <template #default="scope">
            <el-button @click="openTaskDialog(scope.row)" type="primary" size="small">
              Редактировать
            </el-button>
          </template>
        </el-table-column> -->
      </el-table>
    </el-card>

    <!-- Диалог редактирования задачи -->
    <el-dialog
      v-model="dialogVisible"
      title="Редактирование задачи"
      width="50%">
      <el-form :model="currentTask" label-width="120px">
        <el-form-item label="Площадка">
          <el-select v-model="currentTask.platform" placeholder="Выберите площадку">
            <el-option label="Nano" value="81073933" />
          </el-select>
        </el-form-item>
        <el-form-item label="Решение">
          <el-input v-model="currentTask.solution" type="textarea" rows="3" />
        </el-form-item>
        <el-form-item label="Срок">
          <el-date-picker
            v-model="currentTask.due_date"
            type="datetime"
            placeholder="Выберите срок"
            format="DD.MM.YYYY HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ssZ"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Отмена</el-button>
          <el-button type="primary" @click="saveTaskChanges">
            Сохранить
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

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

const fetchTasks = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/inbox_full')
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

const openTaskDialog = (task) => {
  currentTask.value = {
    id: task.id,
    platform: '',
    solution: '',
    due_date: task.due ? new Date(task.due) : null
  }
  dialogVisible.value = true
}

const saveTaskChanges = async () => {
  try {
    const fieldUpdates = []
    
    // Добавляем площадку только если она выбрана
    if (currentTask.value.platform) {
      fieldUpdates.push({
        id: 41,
        type: "catalog",
        name: "Площадка/Place",
        value: {
          item_id: parseInt(currentTask.value.platform),
          item_ids: [parseInt(currentTask.value.platform)],
          headers: ["Площадки"],
          values: ["Nano"],
          rows: [["Nano"]]
        }
      })
    }

    // Добавляем решение только если оно заполнено
    if (currentTask.value.solution) {
      fieldUpdates.push({
        id: 27,
        type: "text",
        name: "Решение/Solution",
        value: currentTask.value.solution
      })
    }

    // Добавляем срок только если он выбран
    if (currentTask.value.due_date) {
      fieldUpdates.push({
        id: 42,
        type: "due_date_time",
        name: "Срок/Term",
        value: currentTask.value.due_date
      })
    }

    const commentData = {
      text: currentTask.value.solution ? `Решение: ${currentTask.value.solution}` : 'Обновление задачи',
      action: "reopened",
      field_updates: fieldUpdates
    }

    await axios.post(`/api/tasks/${currentTask.value.id}/comment`, commentData)
    ElMessage.success('Задача успешно обновлена')
    dialogVisible.value = false
    fetchTasks()
  } catch (error) {
    ElMessage.error('Ошибка при сохранении изменений')
    console.error(error)
  }
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
      await axios.post(`/api/tasks/${task.id}/comment`, commentData)
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
      await axios.post(`/api/tasks/${task.id}/comment`, commentData)
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
</style> 