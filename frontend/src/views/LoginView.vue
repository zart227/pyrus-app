<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>Авторизация в Pyrus</h2>
        </div>
      </template>
      
      <el-form 
        :model="loginForm" 
        :rules="rules" 
        ref="loginFormRef"
        @submit.prevent="handleLogin"
        label-width="120px"
      >
        <el-form-item label="Логин" prop="login">
          <el-input 
            v-model="loginForm.login" 
            placeholder="Введите ваш email"
            :prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item label="Ключ безопасности" prop="securityKey">
          <el-input 
            v-model="loginForm.securityKey" 
            type="password"
            placeholder="Введите ключ безопасности"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleLogin"
            :loading="loading"
            style="width: 100%"
          >
            Войти
          </el-button>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="default" 
            @click="showRegister = true"
            style="width: 100%"
          >
            Регистрация
          </el-button>
        </el-form-item>
      </el-form>
      
      <el-alert
        v-if="error"
        :title="error"
        type="error"
        :closable="false"
        style="margin-top: 20px"
      />
    </el-card>

    <!-- Диалог регистрации -->
    <el-dialog 
      v-model="showRegister" 
      title="Регистрация нового пользователя"
      width="500px"
    >
      <el-form 
        :model="registerForm" 
        :rules="registerRules" 
        ref="registerFormRef"
        label-width="120px"
      >
        <el-form-item label="Логин" prop="login">
          <el-input 
            v-model="registerForm.login" 
            placeholder="Введите ваш email"
            :prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item label="Ключ безопасности" prop="securityKey">
          <el-input 
            v-model="registerForm.securityKey" 
            type="password"
            placeholder="Введите ключ безопасности"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showRegister = false">Отмена</el-button>
        <el-button 
          type="primary" 
          @click="handleRegister"
          :loading="registerLoading"
        >
          Зарегистрироваться
        </el-button>
      </template>
      
      <el-alert
        v-if="registerError"
        :title="registerError"
        type="error"
        :closable="false"
        style="margin-top: 20px"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Состояние формы входа
const loginForm = reactive({
  login: '',
  securityKey: ''
})

const loginFormRef = ref()
const loading = ref(false)
const error = ref('')

// Состояние формы регистрации
const registerForm = reactive({
  login: '',
  securityKey: ''
})

const registerFormRef = ref()
const showRegister = ref(false)
const registerLoading = ref(false)
const registerError = ref('')

// Правила валидации для входа
const rules = {
  login: [
    { required: true, message: 'Пожалуйста, введите логин', trigger: 'blur' },
    { type: 'email', message: 'Пожалуйста, введите корректный email', trigger: 'blur' }
  ],
  securityKey: [
    { required: true, message: 'Пожалуйста, введите ключ безопасности', trigger: 'blur' }
  ]
}

// Правила валидации для регистрации
const registerRules = {
  login: [
    { required: true, message: 'Пожалуйста, введите логин', trigger: 'blur' },
    { type: 'email', message: 'Пожалуйста, введите корректный email', trigger: 'blur' }
  ],
  securityKey: [
    { required: true, message: 'Пожалуйста, введите ключ безопасности', trigger: 'blur' }
  ]
}

// Обработка входа
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      error.value = ''
      
      const result = await authStore.login(loginForm.login, loginForm.securityKey)
      
      if (result.success) {
        ElMessage.success('Успешный вход!')
        router.push('/')
      } else {
        error.value = result.error
      }
      
      loading.value = false
    }
  })
}

// Обработка регистрации
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      registerLoading.value = true
      registerError.value = ''
      
      const result = await authStore.register(registerForm.login, registerForm.securityKey)
      
      if (result.success) {
        ElMessage.success('Регистрация успешна! Теперь вы можете войти.')
        showRegister.value = false
        // Очищаем форму регистрации
        registerForm.login = ''
        registerForm.securityKey = ''
      } else {
        registerError.value = result.error
      }
      
      registerLoading.value = false
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #333;
}
</style>
