<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AudioRecorder from '@/components/AudioRecorder.vue'
import { TranscriptionWebSocket } from '@/utils/websocket'
import type { TranscriptSegment } from '@/types/realtime'

const router = useRouter()

const meetingTitle = ref('')
const language = ref('zh')
const isConnected = ref(false)
const isRecording = ref(false)
const transcripts = ref<TranscriptSegment[]>([])
const wsClient = ref<TranscriptionWebSocket | null>(null)
const meetingId = ref('')
const errorMessage = ref('')

async function startSession() {
  if (!meetingTitle.value) {
    errorMessage.value = '请输入会议标题'
    return
  }

  errorMessage.value = ''

  wsClient.value = new TranscriptionWebSocket(import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000')

  try {
    await wsClient.value.connect(
      {
        title: meetingTitle.value,
        language: language.value
      },
      {
        onConnected: (id) => {
          meetingId.value = id
          isConnected.value = true
        },
        onTranscript: (segment) => {
          transcripts.value.push(segment)
          // Auto scroll to bottom
          setTimeout(() => {
            const content = document.querySelector('.transcript-content')
            if (content) content.scrollTop = content.scrollHeight
          }, 100)
        },
        onError: (error) => {
          errorMessage.value = `错误: ${error}`
        },
        onDisconnected: () => {
          isConnected.value = false
        }
      }
    )
  } catch (error) {
    errorMessage.value = '连接失败，请检查服务是否启动'
    console.error(error)
  }
}

function handleAudioData(data: ArrayBuffer) {
  if (wsClient.value && isConnected.value) {
    wsClient.value.sendAudio(data)
  }
}

function handleRecordingState(recording: boolean) {
  isRecording.value = recording
}

function clearTranscript() {
  transcripts.value = []
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function goBack() {
  if (isConnected.value) {
    wsClient.value?.stop()
  }
  router.push('/meetings')
}

function stopSession() {
  if (wsClient.value) {
    wsClient.value.stop()
  }
  isConnected.value = false
  isRecording.value = false

  // 等待一小段时间后跳转到会议详情页
  if (meetingId.value) {
    setTimeout(() => {
      router.push(`/meetings/${meetingId.value}`)
    }, 500)
  } else {
    router.push('/meetings')
  }
}
</script>

<template>
  <div class="max-w-5xl mx-auto px-6 py-12">
    <!-- Page Header -->
    <div class="mb-10 animate-fade-up flex items-center gap-4">
      <button @click="goBack" class="p-2 text-espresso-400 hover:text-espresso-700 transition-colors">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <div>
        <p class="subhead mb-1">Real-time Transcription</p>
        <h2 class="masthead">实时会议转录</h2>
      </div>
    </div>

    <!-- Setup Form -->
    <div v-if="!isConnected" class="card-paper p-8 animate-fade-up delay-100 max-w-xl mx-auto">
      <div class="mb-6">
        <label class="block text-sm font-sans font-medium text-espresso-600 mb-2">
          会议标题
        </label>
        <input
          v-model="meetingTitle"
          type="text"
          placeholder="例如：产品评审会"
          class="input-editorial"
          maxlength="255"
        />
      </div>

      <div class="mb-6">
        <label class="block text-sm font-sans font-medium text-espresso-600 mb-2">
          语言
        </label>
        <select v-model="language" class="input-editorial">
          <option value="zh">中文</option>
          <option value="en">English</option>
        </select>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="mb-6 p-4 bg-accent-terracotta/10 border border-accent-terracotta/30 rounded-lg">
        <p class="text-sm text-accent-terracotta font-sans">{{ errorMessage }}</p>
      </div>

      <button @click="startSession" class="btn-primary w-full">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
        开始会议
      </button>
    </div>

    <!-- Transcription Area -->
    <div v-else class="space-y-6">
      <!-- Controls Card -->
      <div class="card-paper p-6 animate-fade-up">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h3 class="font-display text-xl text-espresso-700">{{ meetingTitle }}</h3>
            <p class="text-sm text-espresso-400 font-sans mt-1">
              会议 ID: {{ meetingId.slice(0, 8) }}
            </p>
          </div>
          <div class="flex items-center gap-3">
            <span class="px-3 py-1 text-sm font-sans rounded-full"
                  :class="{
                    'bg-accent-sage/20 text-accent-sage': isRecording,
                    'bg-espresso-100 text-espresso-500': !isRecording
                  }">
              {{ isRecording ? '录音中' : '已暂停' }}
            </span>
            <span class="px-3 py-1 text-sm font-sans rounded-full bg-accent-sage/20 text-accent-sage">
              已连接
            </span>
          </div>
        </div>

        <AudioRecorder
          @audioData="handleAudioData"
          @recordingState="handleRecordingState"
        />

        <div class="mt-6 flex justify-end">
          <button @click="stopSession" class="btn-ghost text-accent-terracotta hover:bg-accent-terracotta/10">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M9 10h6v4H9z" />
            </svg>
            结束会议
          </button>
        </div>
      </div>

      <!-- Transcript Card -->
      <div class="card-paper p-6 animate-fade-up delay-100">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-display text-lg text-espresso-700">转录内容</h3>
          <button
            v-if="transcripts.length > 0"
            @click="clearTranscript"
            class="text-sm text-espresso-400 hover:text-espresso-600 transition-colors"
          >
            清空
          </button>
        </div>

        <div class="transcript-content bg-cream-50 rounded-lg p-4 min-h-[300px] max-h-[500px] overflow-y-auto">
          <div
            v-for="segment in transcripts"
            :key="segment.segment_id"
            class="transcript-segment bg-white rounded-lg p-4 mb-3 shadow-sm"
          >
            <div class="flex items-start gap-3">
              <span class="speaker-label font-medium text-accent-blue whitespace-nowrap">
                {{ segment.speaker }}:
              </span>
              <p class="transcript-text flex-1 text-espresso-700 leading-relaxed">
                {{ segment.text }}
              </p>
              <span class="time-stamp text-xs text-espresso-400 whitespace-nowrap">
                {{ formatTime(segment.start_time) }}
              </span>
            </div>
          </div>

          <div v-if="transcripts.length === 0" class="flex flex-col items-center justify-center py-12">
            <svg class="w-16 h-16 text-espresso-200 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
            <p class="text-espresso-400 font-sans">暂无转录内容</p>
            <p class="text-sm text-espresso-300 font-sans mt-1">点击"开始录音"开始实时转录</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.transcript-content {
  scrollbar-width: thin;
  scrollbar-color: #d1d5db #f9fafb;
}

.transcript-content::-webkit-scrollbar {
  width: 6px;
}

.transcript-content::-webkit-scrollbar-track {
  background: #f9fafb;
  border-radius: 3px;
}

.transcript-content::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.transcript-content::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
