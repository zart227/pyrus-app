<template>
  <div class="app-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <div class="header-left">
            <h1>Pyrus Tasks</h1>
          </div>
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

.header-left {
  display: flex;
  align-items: center;
  gap: 30px;
}

.main-nav {
  display: flex;
  gap: 20px;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-link.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
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