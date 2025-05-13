<template>
  <button 
    class="realtime-button" 
    :class="{ 'active': isRealTimeMode }"
    @click="toggleRealTimeMode"
    :title="isRealTimeMode ? '停止实时对话' : '开始实时对话'"
  >
    <MicrophoneIcon v-if="!isRealTimeMode" class="icon" />
    <StopIcon v-else class="icon" />
  </button>
  
  <!-- 添加临时提示弹窗 -->
  <div 
    v-if="showToast" 
    class="toast-message"
    :class="{ 'fade-out': isToastFading }"
  >
    {{ toastMessage }}
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted, inject } from 'vue'
import { emitter } from './event-bus'
import { 
  MicrophoneIcon,
  StopIcon
} from '@heroicons/vue/24/outline'
import axios from 'axios'

const props = defineProps({
  onMessage: Function,
  disabled: Boolean,
  setInputDisabled: Function,
})

const isRealTimeMode = ref(false)
const recognition = ref(null)
const isListening = ref(false)
let audioContext = null
let mediaStream = null

const showToast = ref(false)
const isToastFading = ref(false)
const toastMessage = ref('')

// 注入设置实时对话模式的方法
const setRealTimeMode = inject('setRealTimeMode')

// 初始化语音识别
const initSpeechRecognition = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) {
    alert('您的浏览器不支持语音识别功能')
    return false
  }

  recognition.value = new SpeechRecognition()
  recognition.value.continuous = true
  recognition.value.interimResults = true
  recognition.value.lang = 'zh-CN'

  recognition.value.onresult = handleSpeechResult
  // 添加识别结束事件，自动重启识别
  recognition.value.onend = () => {
    if (isListening.value) {
      recognition.value.start()
    }
  }
  recognition.value.onerror = (event) => {
    console.error('语音识别错误:', event.error)
  }

  return true
}

// 处理语音识别结果
const handleSpeechResult = async (event) => {
  const last = event.results.length - 1
  const transcript = event.results[last][0].transcript.trim()

  if (transcript.includes('小编小编')) {
    // 停止当前识别以捕获下一句
    recognition.value.stop()
    isListening.value = false

    // 显示临时提示
    showTemporaryToast('小编正在聆听')

    // 等待用户说下一句话
    await startRecording()
    isListening.value = true
    recognition.value.start()
  }
}

// 开始录音
const startRecording = async () => {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const mediaRecorder = new MediaRecorder(mediaStream);
    const audioChunks = [];

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      try {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        await sendAudioToBackend(audioBlob);
        
      } catch (error) {
        console.error('请求失败:', error);
        throw error;
      } finally {
        stopMediaStream();
      }
    };

    // 3秒后自动停止录音
    mediaRecorder.start();
    setTimeout(() => {
      mediaRecorder.stop();
    }, 3000);

  } catch (error) {
    console.error('录音失败:', error);
    alert('无法访问麦克风');
    throw error;
  }
};

// 停止媒体流
const stopMediaStream = () => {
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }
  if (audioContext) {
    audioContext.close()
    audioContext = null
  }
}

import { debounce } from 'lodash' // 或手动实现防抖

const sendAudioToBackend = debounce(async (audioBlob) => {
  try {
    const formData = new FormData()
    formData.append('file', audioBlob)
    const response = await axios.post('/api/stt', formData)
    emitter.emit('send-text', response.data.message)
  } catch (error) {
    console.error('语音识别失败:', error)
  }
}, 1000) // 1秒内只允许发送一次



// 检查麦克风权限和可用性
const checkMicrophoneAvailability = async () => {
  try {
    // 检查是否支持 getUserMedia
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert('您的浏览器不支持麦克风访问')
      return false
    }

    // 检查麦克风设备是否存在
    const devices = await navigator.mediaDevices.enumerateDevices()
    const hasAudioDevice = devices.some(device => device.kind === 'audioinput')
    
    if (!hasAudioDevice) {
      alert('未检测到麦克风设备，请确保麦克风已正确连接')
      return false
    }

    // 尝试获取麦克风权限
    await navigator.mediaDevices.getUserMedia({ audio: true })
    return true
  } catch (error) {
    console.error('麦克风检查失败:', error)
    
    if (error.name === 'NotAllowedError') {
      alert('请允许浏览器访问麦克风')
    } else if (error.name === 'NotFoundError') {
      alert('未检测到麦克风设备，请确保麦克风已正确连接')
    } else {
      alert('麦克风访问失败: ' + error.message)
    }
    
    return false
  }
}

// 切换实时对话模式
const toggleRealTimeMode = async () => {
  if (props.disabled) return

  if (!isRealTimeMode.value) {
    // 开启实时对话模式前检查麦克风
    const hasMicrophoneAccess = await checkMicrophoneAvailability()
    if (!hasMicrophoneAccess) {
      return
    }
    
    // 初始化语音识别
    if (!recognition.value && !initSpeechRecognition()) {
      return
    }
  }

  isRealTimeMode.value = !isRealTimeMode.value
  
  // 设置输入框状态
  props.setInputDisabled(isRealTimeMode.value)
  
  // 设置实时对话模式状态
  setRealTimeMode(isRealTimeMode.value)
  
  // 显示模式切换提示
  if (isRealTimeMode.value) {
    showTemporaryToast('已进入实时对话模式，请说"小编小编"唤醒', 2000)
    try {
      recognition.value.start()
      isListening.value = true
    } catch (error) {
      console.error('语音识别启动失败:', error)
      alert('语音识别启动失败，请重试')
      isRealTimeMode.value = false
      props.setInputDisabled(false)
    }
  } else {
    showTemporaryToast('已退出实时对话模式', 2000)
    if (recognition.value) {
      recognition.value.stop()
    }
    stopMediaStream()
    isListening.value = false
  }
}

// 显示临时提示
const showTemporaryToast = (message, duration = 3000) => {
  toastMessage.value = message
  showToast.value = true
  isToastFading.value = false
  
  // 设定时间后自动隐藏
  setTimeout(hideToast, duration)
}

// 隐藏临时提示
const hideToast = () => {
  isToastFading.value = true
  setTimeout(() => {
    showToast.value = false
    isToastFading.value = false
  }, 300) // 等待淡出动画完成
}

// 组件卸载时清理
onUnmounted(() => {
  if (recognition.value) {
    recognition.value.stop()
  }
  stopMediaStream()
})
</script>

<style scoped>
.realtime-button {
  background-color: transparent;
  color: var(--primary-color);
  border: none;
  border-radius: 0.375rem;
  width: 32px;
  height: 32px;
  padding: 0;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.realtime-button:hover:not(:disabled) {
  background-color: var(--hover-color);
}

.realtime-button.active {
  background-color: #ef4444;
  color: white;
}

.realtime-button.active:hover:not(:disabled) {
  background-color: #dc2626; /* 深一点的红色 */
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
  transition: transform 0.2s ease;
}

.active .icon {
  transform: scale(0.85); /* 让停止图标稍微小一点 */
}

.toast-message {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 1rem 2rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  z-index: 1000;
  opacity: 1;
  transition: opacity 0.3s ease;
}

.toast-message.fade-out {
  opacity: 0;
}
</style> 