<template>
  <div class="app-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>Pyrus Tasks</h1>
          <UserInfo v-if="authStore.isLoggedIn" />
        </div>
      </el-header>
      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { ElContainer, ElHeader, ElMain } from 'element-plus'
import { useAuthStore } from './stores/auth'
import UserInfo from './components/UserInfo.vue'

const authStore = useAuthStore()

onMounted(async () => {
  // Проверяем авторизацию при загрузке приложения
  await authStore.checkAuth()
})
</script>

<style>
.app-container {
  height: 100vh;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.el-header {
  background-color: #409EFF;
  color: white;
  line-height: 60px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.el-header h1 {
  margin: 0;
}

.el-main {
  padding: 20px;
}
</style> 