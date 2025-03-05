<template>
  <div class="chat-window">
    <div class="messages" ref="messagesContainer">
      <div v-if="historyLoading" class="loading-indicator">
        <div class="loading-spinner"></div>
        <span>加载历史消息...</span>
      </div>
      <div v-if="noMoreHistory && !historyLoading" class="no-more-history">
        没有更多历史消息了
      </div>
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="['message', message.role]"
      >
        <div class="message-content">
          <div 
            class="message-bubble"
            :class="{ 'markdown-body': message.role === 'assistant' }"
          >
            <template v-if="message.role === 'user'">
              {{ message.content }}
            </template>
            <template v-else>
              <div v-if="message.isTyping">
                {{ typingMessage }}
                <span class="typing-cursor"></span>
              </div>
              <template v-else>
                <!-- AI 回复的双部分布局 -->
                <div class="ai-response">
                  <!-- Markdown 部分 -->
                  <div 
                    v-if="message.markdown" 
                    class="markdown-section"
                    v-html="renderMarkdown(message.markdown)"
                  ></div>
                  
                  <!-- 分隔线 -->
                  <div v-if="message.markdown && message.content" class="response-divider"></div>
                  
                  <!-- Content 部分 -->
                  <div 
                    v-if="message.content"
                    class="content-section"
                  >{{ message.content }}</div>
                </div>
              </template>
            </template>
          </div>
          <div class="message-actions">
            <button 
              v-if="message.role === 'assistant'"
              class="action-btn" 
              @click="playAudio(message)"
              title="播放"
            >
              <SpeakerWaveIcon class="icon" />
            </button>
            <button class="action-btn" @click="copyMessage(message.content)" title="复制">
              <DocumentDuplicateIcon class="icon" />
            </button>
            <button class="action-btn" @click="deleteMessage(index)" title="删除">
              <TrashIcon class="icon" />
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="input-area">
      <div class="input-container">
        <textarea
          v-model="inputMessage"
          @keydown.enter.prevent="sendMessage"
          placeholder="向 AI 助手提问..."
          rows="1"
          ref="textarea"
        ></textarea>
        <button
          class="send-button"
          :disabled="isLoading || !inputMessage.trim()"
          @click="sendMessage"
          title="发送消息"
        >
          <PaperAirplaneIcon
            class="icon"
            :class="{ 'animate-pulse': isLoading }"
          />
        </button>
      </div>
      <div class="input-footer">
        <span class="footer-text">ChatGPT 可能会犯错。请考虑验证重要信息。</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { marked } from 'marked'
import {
  DocumentDuplicateIcon,
  TrashIcon,
  PaperAirplaneIcon,
  SpeakerWaveIcon,
} from '@heroicons/vue/24/outline'
import axios from 'axios'

const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref(null)
const textarea = ref(null)
const conversationId = ref('')

const historyLoading = ref(false)
const noMoreHistory = ref(false)
const currentPage = ref(0)
const PAGE_SIZE = 10

const BACKEND_URL = '/api'

// 修改打字效果相关的变量
const typingMessage = ref('')
const isTyping = ref(false)
const baseSpeed = 30 // 基础打字速度（毫秒）

// 添加自动滚动控制
const shouldAutoScroll = ref(true)
const userHasScrolled = ref(false)

// 自动调整文本框高度
const adjustTextareaHeight = () => {
  const el = textarea.value
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

// 获取随机打字延迟
const getTypeDelay = () => {
  // 基础速度上下浮动 20ms
  const randomSpeed = baseSpeed + (Math.random() * 40 - 20)
  
  // 10% 的概率增加较长停顿，模拟思考
  if (Math.random() < 0.1) {
    return randomSpeed + Math.random() * 300
  }
  
  // 在句子结束符号后添加停顿
  if (['.', '!', '?', '。', '！', '？'].includes(typingMessage.value.slice(-1))) {
    return randomSpeed + 200
  }
  
  // 在逗号、分号等后添加短停顿
  if ([',', ';', '，', '；'].includes(typingMessage.value.slice(-1))) {
    return randomSpeed + 100
  }
  
  return randomSpeed
}

// 改进的打字效果函数
const typeMessage = async (message) => {
  isTyping.value = true
  typingMessage.value = ''
  
  for (let i = 0; i < message.length; i++) {
    typingMessage.value += message[i]
    
    const delay = getTypeDelay()
    await new Promise(resolve => setTimeout(resolve, delay))
    
    // 每个字符都尝试滚动到底部
    if (shouldAutoScroll.value) {
      await nextTick()
      scrollToBottom()
    }
  }
  
  isTyping.value = false
}

// 修改 watchInput 函数，移除滚动控制
const watchInput = () => {
  textarea.value.addEventListener('input', adjustTextareaHeight)
}

// 修改发送消息函数
const sendMessage = async () => {
  if (isLoading.value || !inputMessage.value.trim()) return

  const userMessage = inputMessage.value.trim()
  messages.value.push({
    role: 'user',
    content: userMessage,
    markdown: ''
  })

  inputMessage.value = ''
  adjustTextareaHeight()
  isLoading.value = true
  
  // 发送消息时强制滚动到底部
  await nextTick()
  messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight

  try {
    const formData = new FormData()
    formData.append('text', userMessage)

    const response = await axios.post(`${BACKEND_URL}/chat`, formData)
    
    if (response.data.message) {
      const aiMessage = {
        role: 'assistant',
        content: response.data.message[response.data.message.length - 1].content,
        markdown: response.data.message[response.data.message.length - 1].markdown,
        isTyping: true,
        conversationId: response.data.conversation_id
      }
      messages.value.push(aiMessage)
      
      // AI 开始回复前滚动到底部
      await nextTick()
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      
      await typeMessage(aiMessage.content)
      aiMessage.isTyping = false
      
      conversationId.value = response.data.conversation_id
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    messages.value.push({
      role: 'assistant',
      content: '抱歉，发生了一些错误。请稍后重试。',
      markdown: ''
    })
  } finally {
    isLoading.value = false
    await nextTick()
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value && shouldAutoScroll.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 复制消息
const copyMessage = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    alert('已复制到剪贴板')
  } catch (err) {
    console.error('复制失败:', err)
  }
}

// 修改删除消息函数
const deleteMessage = async (index) => {
  // 找到当前消息所属的对话组
  const currentMessage = messages.value[index]
  const isUser = currentMessage.role === 'user'
  
  // 确定对话组的另一条消息的索引
  const pairedIndex = isUser ? index + 1 : index - 1
  
  // 确保配对消息存在且是一组对话
  if (
    pairedIndex < 0 || 
    pairedIndex >= messages.value.length ||
    (isUser && messages.value[pairedIndex].role !== 'assistant') ||
    (!isUser && messages.value[pairedIndex].role !== 'user')
  ) {
    alert('无法删除不完整的对话')
    return
  }

  // 获取对话 ID（从 AI 回复消息中获取）
  const conversationId = isUser 
    ? messages.value[pairedIndex].conversationId 
    : currentMessage.conversationId

  if (!conversationId) {
    console.error('对话 ID 不存在')
    return
  }

  // 弹出确认框
  if (!confirm('确定要删除这组对话记录吗？')) {
    return
  }

  try {
    // 发送删除请求到后端
    const response = await axios.get(`${BACKEND_URL}/delete/${conversationId}`)
    
    if (response.status === 200) {
      // 删除成功后，移除整组对话
      const startIndex = Math.min(index, pairedIndex)
      messages.value.splice(startIndex, 2)
    } else {
      throw new Error('删除失败')
    }
  } catch (error) {
    console.error('删除消息失败:', error)
    alert('删除失败，请稍后重试')
  }
}

// 渲染 Markdown
const renderMarkdown = (content) => {
  if (!content) return ''
  return marked(content)
}

// 添加滚动事件处理
const handleMessagesScroll = (e) => {
  const container = e.target
  const isAtBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 50

  // 处理历史记录加载
  if (container.scrollTop <= 100 && !historyLoading.value && !noMoreHistory.value) {
    loadHistory()
  }

  // 处理自动滚动控制
  if (!isAtBottom && !userHasScrolled.value) {
    userHasScrolled.value = true
    shouldAutoScroll.value = false
  } else if (isAtBottom) {
    userHasScrolled.value = false
    shouldAutoScroll.value = true
  }
}

// 修改加载历史记录函数
const loadHistory = async (isInitial = false) => {
  if (historyLoading.value || (noMoreHistory.value && !isInitial)) return

  historyLoading.value = true
  const oldScrollHeight = messagesContainer.value?.scrollHeight || 0
  const oldScrollTop = messagesContainer.value?.scrollTop || 0

  try {
    const formData = new FormData()
    formData.append('start', currentPage.value * PAGE_SIZE)
    formData.append('limit', PAGE_SIZE)

    const response = await axios.post(`${BACKEND_URL}/conversations`, formData)
    const historyData = response.data

    if (historyData.length < PAGE_SIZE) {
      noMoreHistory.value = true
    }

    if (historyData.length > 0) {
      // 按时间戳升序排序历史数据（最旧的在前）
      const sortedHistory = historyData.sort((a, b) => {
        return new Date(a.timestamp) - new Date(b.timestamp)
      })

      // 解析每组对话，确保用户问题在上，AI回复在下
      const newMessages = []
      for (const item of sortedHistory) {
        const parsedContent = JSON.parse(item.content)
        const conversation = parsedContent.message.map(msg => ({
          ...msg,
          timestamp: item.timestamp,
          content: msg.content || '',
          markdown: msg.markdown || '',
          conversationId: parsedContent.conversation_id
        }))

        // 确保每组对话中用户问题在前，AI回复在后
        const userMsg = conversation.find(msg => msg.role === 'user')
        const aiMsg = conversation.find(msg => msg.role === 'assistant')
        
        if (userMsg) newMessages.push(userMsg)
        if (aiMsg) newMessages.push(aiMsg)
      }

      if (isInitial) {
        // 初始加载时直接使用排序后的消息
        messages.value = newMessages
        await nextTick()
        scrollToBottom()
      } else {
        // 加载更多历史记录时，添加到顶部
        messages.value = [...newMessages, ...messages.value]
        // 保持滚动位置
        await nextTick()
        if (messagesContainer.value) {
          const newScrollHeight = messagesContainer.value.scrollHeight
          messagesContainer.value.scrollTop = newScrollHeight - oldScrollHeight + oldScrollTop
        }
      }

      currentPage.value++
    } else if (isInitial) {
      messages.value = []
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
  } finally {
    historyLoading.value = false
  }
}

// 修改音频播放功能，确保只使用 content
const playAudio = async (message) => {
  try {
    // 确保只使用 content 部分
    const textContent = message.content

    // 创建音频上下文
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    
    // 获取音频数据
    const response = await axios.get(`${BACKEND_URL}/tts`, {
      params: { text: textContent },
      responseType: 'arraybuffer'
    })
    
    // 解码音频数据
    const audioBuffer = await audioContext.decodeAudioData(response.data)
    
    // 创建音频源
    const source = audioContext.createBufferSource()
    source.buffer = audioBuffer
    source.connect(audioContext.destination)
    
    // 播放音频
    source.start(0)
  } catch (error) {
    console.error('播放音频失败:', error)
    alert('播放失败，请稍后重试')
  }
}

onMounted(async () => {
  watchInput()
  // 初始加载历史记录
  await loadHistory(true)
  // 添加滚动事件监听
  messagesContainer.value?.addEventListener('scroll', handleMessagesScroll)
})
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  margin: 0 auto;
  padding-top: 3.5rem;
  overflow: hidden;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 0;
  width: 100%;
  padding-right: 12px;
}

.message {
  padding: 0.5rem 0;
}

.message-content {
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
  padding: 0 1.5rem;
  position: relative;
  display: flex;
  flex-direction: column;
}

.message.user .message-content {
  align-items: flex-end;
}

.message.assistant .message-content {
  align-items: flex-start;
}

.message-bubble {
  max-width: 80%;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  position: relative;
  font-size: 0.9375rem;
  line-height: 1.5;
  background-color: var(--bubble-bg);
  color: var(--bubble-text);
  text-align: justify;
  margin-bottom: 1.5rem;
}

.message.assistant .message-bubble {
  border-radius: 0.75rem;
  margin-right: auto;
}

.message.user .message-bubble {
  border-radius: 0.75rem;
  margin-left: auto;
}

.message-actions {
  position: absolute;
  bottom: -1.75rem;
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.message.assistant .message-actions {
  left: 1.5rem;
  right: auto;
}

.message.user .message-actions {
  right: 1.5rem;
  left: auto;
}

.message:hover .message-actions {
  opacity: 1;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.375rem;
  border-radius: 0.375rem;
  transition: all 0.2s;
  color: #6b7280;
}

.action-btn:hover {
  background-color: var(--hover-color);
  color: var(--primary-color);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.icon {
  width: 1rem;
  height: 1rem;
  color: #6b7280;
}

.input-area {
  background-color: var(--background-color);
  padding: 1.5rem 0 5px;
  position: sticky;
  bottom: 0;
  border-top: 1px solid var(--border-color);
  width: 100%;
}

.input-container {
  width: 100%;
  margin: 0 auto;
  background-color: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 0.75rem;
  box-shadow: 0 0 15px rgba(0,0,0,0.05);
  padding: 0.75rem;
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;
}

textarea {
  flex: 1;
  padding: 0;
  border: none;
  resize: none;
  max-height: 200px;
  min-height: 24px;
  font-family: inherit;
  font-size: 1rem;
  line-height: 1.5;
  outline: none;
  background: transparent;
}

.send-button {
  background-color: transparent;
  color: var(--primary-color);
  border: none;
  border-radius: 0.375rem;
  width: 32px;
  height: 32px;
  padding: 0;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-button:hover:not(:disabled) {
  background-color: var(--hover-color);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-button .icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--primary-color);
}

.input-footer {
  width: 100%;
  margin: 0.5rem auto 0;
  padding: 0 0.75rem;
  text-align: center;
}

.footer-text {
  font-size: 0.75rem;
  color: #6b7280;
}

/* 自定义滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background-color: #e2e8f0;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background-color: #cbd5e1;
}

.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  color: #6b7280;
  font-size: 0.875rem;
  gap: 0.5rem;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid #e5e7eb;
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.no-more-history {
  text-align: center;
  padding: 1rem;
  color: #6b7280;
  font-size: 0.875rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.typing-cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  background-color: currentColor;
  margin-left: 2px;
  animation: blink 1s step-end infinite;
  vertical-align: text-bottom;
}

@keyframes blink {
  from, to {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}

.ai-response {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: 100%;
}

.markdown-section {
  width: 100%;
}

.content-section {
  width: 100%;
  font-size: 0.9375rem;
  line-height: 1.5;
  color: var(--bubble-text);
  text-align: justify;
}

.response-divider {
  width: 100%;
  height: 1px;
  background-color: rgba(0, 0, 0, 0.1);
  margin: 0.5rem 0;
}
</style>

<style>
/* Markdown 样式 */
.markdown-body {
  font-size: 1rem;
  line-height: 1.6;
  text-align: justify;
}

.markdown-body p {
  margin-bottom: 1rem;
}

.markdown-body pre {
  background-color: #f8fafc;
  padding: 1rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 1rem 0;
}

.markdown-body code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
    'Liberation Mono', 'Courier New', monospace;
  font-size: 0.875rem;
  padding: 0.2rem 0.4rem;
  background-color: #f1f5f9;
  border-radius: 0.25rem;
}

.markdown-body pre code {
  padding: 0;
  background-color: transparent;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  font-weight: 600;
}

.markdown-body ul,
.markdown-body ol {
  margin-bottom: 1rem;
  padding-left: 1.5rem;
}

.markdown-body blockquote {
  border-left: 4px solid var(--border-color);
  padding-left: 1rem;
  margin: 1rem 0;
  color: #64748b;
}

/* 添加表格样式 */
.markdown-body table {
  border-collapse: collapse;
  width: 100%;
  margin: 1rem 0;
}

.markdown-body th,
.markdown-body td {
  border: 1px solid var(--border-color);
  padding: 0.5rem;
  text-align: left;
}

.markdown-body th {
  background-color: var(--background-color);
  font-weight: 600;
}

.markdown-body tr:nth-child(even) {
  background-color: var(--message-bg-user);
}

/* 调整代码块在气泡中的样式 */
.message .markdown-body {
  color: var(--bubble-text);
}

.message .markdown-body pre {
  background-color: rgba(255, 255, 255, 0.1);
  border: none;
}

.message .markdown-body code {
  background-color: rgba(255, 255, 255, 0.1);
  color: var(--bubble-text);
}
</style> 