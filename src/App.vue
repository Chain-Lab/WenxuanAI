<script setup>
import ChatWindow from './components/ChatWindow.vue'
</script>

<template>
  <div class="app-container">
    <div class="chat-container">
      <div class="chat-header">
        <h1>AI 助手</h1>
      </div>
      <ChatWindow />
    </div>
  </div>
</template>

<style>
:root {
  --primary-color: #2563eb;
  --secondary-color: #3b82f6;
  --background-color: #ffffff;
  --text-color: #374151;
  --border-color: #e5e7eb;
  --hover-color: #f9fafb;
  --message-bg-user: #f7f7f8;
  --message-bg-assistant: #ffffff;
  --content-width: 70%;
  --bubble-bg: #f1f5f9;
  --bubble-text: #1f2937;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Söhne, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Ubuntu, Cantarell, "Noto Sans", sans-serif, "Helvetica Neue";
  background-color: var(--background-color);
  color: var(--text-color);
  line-height: 1.6;
  height: 100vh;
  overflow: hidden;
}

.app-container {
  height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  background-color: var(--background-color);
  overflow: hidden;
}

.chat-container {
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--background-color);
  position: relative;
}

.chat-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  background-color: rgba(255,255,255,0.95);
  backdrop-filter: blur(8px);
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
}

.chat-header h1 {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-color);
  text-align: center;
}

@media (max-width: 768px) {
  .chat-container {
    width: 100%;
  }
}

#app {
  padding-bottom: 5px;
}
</style>
