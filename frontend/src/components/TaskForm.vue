<template>
  <div class="task-form-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ formTitle }}</span>
          <div class="header-buttons">
            <el-button @click="cancelForm">Отмена</el-button>
            <el-button type="primary" @click="saveForm" :loading="saving">
              {{ isEditMode ? 'Сохранить' : 'Создать' }}
            </el-button>
          </div>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="200px"
        v-loading="loading">
        
        <!-- Основные поля -->
        <el-form-item label="Тема" prop="subject">
          <el-input v-model="formData.subject" placeholder="Введите тему задачи" />
        </el-form-item>

        <el-form-item label="Описание" prop="text">
          <el-input
            v-model="formData.text"
            type="textarea"
            :rows="4"
            placeholder="Введите описание задачи" />
        </el-form-item>

        <!-- Динамические поля из формы -->
        <template v-for="field in taskForm.fields" :key="field.id">
          <el-form-item
            :label="field.name"
            :prop="`field_${field.id}`"
            :required="field.required">
            
            <!-- Поле типа catalog (выпадающий список) -->
            <el-select
              v-if="field.type === 'catalog'"
              v-model="formData[`field_${field.id}`]"
              :placeholder="`Выберите ${field.name.toLowerCase()}`"
              style="width: 100%">
              <el-option
                v-for="item in field.catalog_items"
                :key="item.item_id"
                :label="getCatalogItemLabel(item)"
                :value="item.item_id" />
            </el-select>

            <!-- Поле типа status (выпадающий список с одним выбором) -->
            <el-select
              v-else-if="field.type === 'status'"
              v-model="formData[`field_${field.id}`]"
              :placeholder="`Выберите ${field.name.toLowerCase()}`"
              style="width: 100%">
              <el-option
                v-for="item in field.catalog_items"
                :key="item.item_id"
                :label="getCatalogItemLabel(item)"
                :value="item.item_id" />
            </el-select>

            <!-- Поле типа checkmark/multiple_choice (множественный выбор) -->
            <el-select
              v-else-if="field.type === 'checkmark' || field.type === 'multiple_choice'"
              v-model="formData[`field_${field.id}`]"
              :placeholder="`Выберите ${field.name.toLowerCase()}`"
              multiple
              style="width: 100%">
              <el-option
                v-for="item in field.catalog_items"
                :key="item.item_id"
                :label="getCatalogItemLabel(item)"
                :value="item.item_id" />
            </el-select>

            <!-- Поле типа text -->
            <el-input
              v-else-if="field.type === 'text'"
              v-model="formData[`field_${field.id}`]"
              :placeholder="`Введите ${field.name.toLowerCase()}`" />

            <!-- Поле типа textarea -->
            <el-input
              v-else-if="field.type === 'textarea'"
              v-model="formData[`field_${field.id}`]"
              type="textarea"
              :rows="3"
              :placeholder="`Введите ${field.name.toLowerCase()}`" />

            <!-- Поле типа date -->
            <el-date-picker
              v-else-if="field.type === 'date'"
              v-model="formData[`field_${field.id}`]"
              type="date"
              :placeholder="`Выберите ${field.name.toLowerCase()}`"
              format="DD.MM.YYYY"
              value-format="YYYY-MM-DD" />

            <!-- Поле типа datetime -->
            <el-date-picker
              v-else-if="field.type === 'datetime' || field.type === 'due_date_time'"
              v-model="formData[`field_${field.id}`]"
              type="datetime"
              :placeholder="`Выберите ${field.name.toLowerCase()}`"
              format="DD.MM.YYYY HH:mm"
              value-format="YYYY-MM-DDTHH:mm:ssZ" />

            <!-- Поле типа number -->
            <el-input-number
              v-else-if="field.type === 'number'"
              v-model="formData[`field_${field.id}`]"
              :placeholder="`Введите ${field.name.toLowerCase()}`"
              style="width: 100%" />

            <!-- Поле типа email -->
            <el-input
              v-else-if="field.type === 'email'"
              v-model="formData[`field_${field.id}`]"
              type="email"
              :placeholder="`Введите ${field.name.toLowerCase()}`" />

            <!-- Поле типа phone -->
            <el-input
              v-else-if="field.type === 'phone'"
              v-model="formData[`field_${field.id}`]"
              :placeholder="`Введите ${field.name.toLowerCase()}`" />

            <!-- Поле типа checkbox -->
            <el-checkbox
              v-else-if="field.type === 'checkbox'"
              v-model="formData[`field_${field.id}`]">
              {{ field.name }}
            </el-checkbox>

            <!-- Поле типа radio -->
            <el-radio-group
              v-else-if="field.type === 'radio'"
              v-model="formData[`field_${field.id}`]">
              <el-radio
                v-for="option in getRadioOptions(field)"
                :key="option.value"
                :label="option.value">
                {{ option.label }}
              </el-radio>
            </el-radio-group>

            <!-- Поле типа select (не каталог) -->
            <el-select
              v-else-if="field.type === 'select'"
              v-model="formData[`field_${field.id}`]"
              :placeholder="`Выберите ${field.name.toLowerCase()}`"
              style="width: 100%">
              <el-option
                v-for="option in getSelectOptions(field)"
                :key="option.value"
                :label="option.label"
                :value="option.value" />
            </el-select>

            <!-- Неизвестный тип поля -->
            <el-input
              v-else
              v-model="formData[`field_${field.id}`]"
              :placeholder="`Введите ${field.name.toLowerCase()}`" />
          </el-form-item>
        </template>
      </el-form>

      <!-- Вложения -->
      <el-divider v-if="attachments.length > 0">Вложения</el-divider>
      <div v-if="attachments.length > 0" class="attachments-section">
        <el-tag
          v-for="att in attachments"
          :key="att.id"
          class="attachment-tag"
          type="info">
          <a :href="att.url" target="_blank" class="attachment-link">
            {{ att.name }} ({{ formatFileSize(att.size) }})
          </a>
        </el-tag>
      </div>

      <!-- Комментарии -->
      <el-divider v-if="isEditMode">Комментарии</el-divider>
      <div v-if="isEditMode && comments.length > 0" class="comments-section">
        <el-card v-for="(comment, idx) in comments" :key="idx" class="comment-card" shadow="never">
          <div class="comment-header">
            <span class="comment-author">{{ comment.author }}</span>
            <span class="comment-date">{{ formatDate(comment.create_date) }}</span>
          </div>
          <div class="comment-text">{{ comment.text }}</div>
          <div v-if="comment.attachments && comment.attachments.length > 0" class="comment-attachments">
            <el-tag
              v-for="att in comment.attachments"
              :key="att.id"
              size="small"
              type="info">
              <a :href="att.url" target="_blank">{{ att.name }}</a>
            </el-tag>
          </div>
        </el-card>
      </div>

      <!-- Форма добавления комментария -->
      <el-divider v-if="isEditMode">Добавить комментарий</el-divider>
      <div v-if="isEditMode" class="comment-form">
        <el-form :model="commentForm" label-width="150px">
          <el-form-item label="Тип комментария">
            <el-radio-group v-model="commentForm.type">
              <el-radio value="internal">Внутренняя переписка</el-radio>
              <el-radio value="email">Эл. почта</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="Текст комментария">
            <el-input
              v-model="commentForm.text"
              type="textarea"
              :rows="4"
              placeholder="Введите текст комментария" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="addComment" :loading="commenting">
              Отправить комментарий
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const props = defineProps({
  formId: {
    type: Number,
    required: true
  },
  taskId: {
    type: Number,
    default: null
  },
  currentValues: {
    type: Object,
    default: () => ({})
  },
  taskComments: {
    type: Array,
    default: () => []
  },
  taskAttachments: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'saved'])

// Реактивные данные
const loading = ref(false)
const saving = ref(false)
const commenting = ref(false)
const taskForm = ref({ fields: [] })
const formRef = ref(null)
const attachments = ref([])
const comments = ref([])

// Данные формы
const formData = reactive({
  subject: '',
  text: '',
  // Динамические поля будут добавляться автоматически
})

// Форма комментария
const commentForm = reactive({
  type: 'internal',
  text: ''
})

// Правила валидации
const formRules = reactive({
  subject: [
    { required: true, message: 'Пожалуйста, введите тему задачи', trigger: 'blur' }
  ],
  text: [
    { required: true, message: 'Пожалуйста, введите описание задачи', trigger: 'blur' }
  ]
})

// Вычисляемые свойства
const formTitle = computed(() => {
  if (props.taskId) {
    return `Редактирование задачи #${props.taskId}`
  }
  return `Создание новой задачи - ${taskForm.value.form_name || 'Форма'}`
})

const isEditMode = computed(() => !!props.taskId)

// Методы
const getCatalogItemLabel = (item) => {
  if (item.values && item.values.length > 0) {
    return item.values[0]
  }
  if (item.headers && item.headers.length > 0) {
    return item.headers[0]
  }
  return `Элемент ${item.item_id}`
}

const getRadioOptions = (field) => {
  // Для radio полей нужно получить опции из поля
  // Пока возвращаем пустой массив, можно расширить при необходимости
  return []
}

const getSelectOptions = (field) => {
  // Для select полей нужно получить опции из поля
  // Пока возвращаем пустой массив, можно расширить при необходимости
  return []
}

const loadTaskForm = async () => {
  loading.value = true
  try {
    const response = await api.get(`/forms/${props.formId}/task-form`)
    taskForm.value = response.data.form
    
    // Добавляем правила валидации для обязательных полей
    taskForm.value.fields.forEach(field => {
      if (field.required) {
        formRules[`field_${field.id}`] = [
          { required: true, message: `Пожалуйста, заполните поле "${field.name}"`, trigger: 'blur' }
        ]
      }
    })
    
    // Инициализируем значения полей
    initializeFormData()
    
  } catch (error) {
    ElMessage.error('Ошибка при загрузке формы задачи')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const initializeFormData = () => {
  // Инициализируем значения полей из текущих значений задачи (для редактирования)
  if (props.currentValues) {
    Object.keys(props.currentValues).forEach(key => {
      // Специальные поля subject и text не имеют префикса field_
      if (key === 'subject' || key === 'text') {
        formData[key] = props.currentValues[key]
      } else {
        // Остальные поля - это ID полей формы, добавляем префикс field_
        formData[`field_${key}`] = props.currentValues[key]
      }
    })
  }
  
  // Инициализируем пустые значения для всех полей формы
  taskForm.value.fields.forEach(field => {
    if (!formData.hasOwnProperty(`field_${field.id}`)) {
      formData[`field_${field.id}`] = getDefaultValueForFieldType(field.type)
    }
  })
}

const getDefaultValueForFieldType = (type) => {
  switch (type) {
    case 'checkbox':
      return false
    case 'number':
      return null
    case 'date':
    case 'datetime':
    case 'due_date_time':
      return null
    default:
      return ''
  }
}

const saveForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch (error) {
    ElMessage.warning('Пожалуйста, заполните все обязательные поля')
    return
  }
  
  saving.value = true
  try {
    // Подготавливаем данные для отправки
    const fieldValues = {}
    
    // Собираем значения полей формы
    Object.keys(formData).forEach(key => {
      if (key.startsWith('field_')) {
        const fieldId = key.replace('field_', '')
        const value = formData[key]
        
        if (value !== null && value !== undefined && value !== '') {
          fieldValues[fieldId] = value
        }
      }
    })
    
    if (isEditMode.value) {
      // Редактирование существующей задачи
      const fieldUpdates = Object.keys(fieldValues).map(fieldId => {
        const field = taskForm.value.fields.find(f => f.id == fieldId)
        return {
          id: parseInt(fieldId),
          type: field.type,
          name: field.name,
          value: fieldValues[fieldId]
        }
      })
      
      const commentData = {
        text: formData.text || 'Обновление задачи',
        field_updates: fieldUpdates
      }
      
      await api.post(`/tasks/${props.taskId}/comment`, commentData)
      ElMessage.success('Задача успешно обновлена')
    } else {
      // Создание новой задачи
      const taskData = {
        form_id: props.formId,
        subject: formData.subject,
        text: formData.text,
        field_values: fieldValues
      }
      
      await api.post('/tasks/create', taskData)
      ElMessage.success('Задача успешно создана')
    }
    
    emit('saved')
    emit('close')
    
  } catch (error) {
    ElMessage.error('Ошибка при сохранении задачи')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const cancelForm = () => {
  emit('close')
}

// Добавление комментария
const addComment = async () => {
  if (!commentForm.text.trim()) {
    ElMessage.warning('Пожалуйста, введите текст комментария')
    return
  }

  commenting.value = true
  try {
    const commentData = {
      text: commentForm.text,
      action: commentForm.type === 'email' ? 'replied' : null,
      field_updates: []
    }

    await api.post(`/tasks/${props.taskId}/comment`, commentData)
    ElMessage.success('Комментарий добавлен')
    
    // Очищаем форму
    commentForm.text = ''
    
    // Перезагружаем данные задачи
    // TODO: можно оптимизировать, загружая только комментарии
    emit('saved')
    emit('close')
  } catch (error) {
    ElMessage.error('Ошибка при добавлении комментария')
    console.error(error)
  } finally {
    commenting.value = false
  }
}

// Вспомогательные функции
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('ru-RU')
}

// Инициализация
onMounted(() => {
  loadTaskForm()
  
  // Загружаем комментарии и вложения из props
  if (props.taskComments) {
    comments.value = props.taskComments
  }
  if (props.taskAttachments) {
    attachments.value = props.taskAttachments
  }
})
</script>

<style scoped>
.task-form-container {
  max-width: 800px;
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

.el-form-item {
  margin-bottom: 20px;
}

.attachments-section {
  margin: 20px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.attachment-tag {
  max-width: 300px;
}

.attachment-link {
  color: inherit;
  text-decoration: none;
}

.attachment-link:hover {
  text-decoration: underline;
}

.comments-section {
  margin: 20px 0;
}

.comment-card {
  margin-bottom: 15px;
  border: 1px solid #ebeef5;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.comment-author {
  font-weight: bold;
  color: #409EFF;
}

.comment-date {
  color: #909399;
  font-size: 12px;
}

.comment-text {
  margin: 10px 0;
  line-height: 1.6;
  white-space: pre-wrap;
}

.comment-attachments {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.comment-form {
  margin: 20px 0;
}
</style>
