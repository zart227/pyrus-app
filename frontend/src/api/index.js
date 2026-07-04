import axios from 'axios'

// Определяем базовый URL в зависимости от окружения
const getBaseURL = () => {
  const port = window.location.port
  const pathname = window.location.pathname
  
  // Production через Nginx (порт 80 или путь начинается с /pyrus/)
  if (port === '' || pathname.startsWith('/pyrus/')) {
    return '/pyrus/api'
  }
  
  // Прямой доступ к nginx контейнеру (порт 8082)
  if (port === '8082') {
    return '/api'
  }
  
  // Development режим (Vite dev server на порту 5173 или 8081)
  return 'http://localhost:8000/api'
}

// Создаем экземпляр axios с базовой конфигурацией
const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 10000,
  withCredentials: true // Важно для работы с куками
})

// Интерцептор для добавления токена авторизации
api.interceptors.request.use(
  (config) => {
    const token = getTokenFromCookie()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Интерцептор для обработки ошибок авторизации
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Если получили 401, перенаправляем на страницу входа
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

function getTokenFromCookie() {
  const cookies = document.cookie.split(';')
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=')
    if (name === 'access_token') {
      // Убираем кавычки и префикс "Bearer " если есть
      let token = value.replace(/"/g, '')
      if (token.startsWith('Bearer ')) {
        token = token.substring(7)
      }
      return token
    }
  }
  return null
}

export default api
