<template>
  <div class="user-info">
    <el-dropdown @command="handleCommand">
      <span class="user-dropdown">
        <el-icon><User /></el-icon>
        {{ user?.login }}
        <el-icon class="el-icon--right"><arrow-down /></el-icon>
      </span>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="profile">Профиль</el-dropdown-item>
          <el-dropdown-item command="logout" divided>Выйти</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { User, ArrowDown } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const user = authStore.user

const handleCommand = async (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('Функция профиля в разработке')
      break
    case 'logout':
      await authStore.logout()
      ElMessage.success('Вы вышли из системы')
      router.push('/login')
      break
  }
}
</script>

<style scoped>
.user-info {
  margin-left: auto;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-dropdown:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.user-dropdown .el-icon {
  margin-right: 8px;
}

.user-dropdown .el-icon--right {
  margin-left: 8px;
  margin-right: 0;
}
</style>
