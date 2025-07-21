<template>
  <div class="app-container">
    <el-container>
      <el-header>
        <h1>Pyrus Tasks</h1>
      </el-header>
      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ElContainer, ElHeader, ElMain } from 'element-plus'
</script>

<style>
.app-container {
  height: 100vh;
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

.el-main {
  padding: 20px;
}
</style> 