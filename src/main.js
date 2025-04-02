import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import 'animate.css'

const app = createApp(App)

// 添加动画指令
app.directive('animate', {
  mounted(el, binding) {
    el.classList.add('animate__animated', `animate__${binding.value}`)
  }
})

app.mount('#app')