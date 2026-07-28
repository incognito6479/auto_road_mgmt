<template>
  <AppLayout>

    <!-- Page Header -->
    <div class="page-top">
      <div>
        <h2 class="page-main-title">Bildirishnomalar (Notifications)</h2>
        <p class="page-sub-title">Tizimdagi amaliy darslar, to'lovlar va hujjatlar bo'yicha so'nggi xabarlar</p>
      </div>

      <button
        v-if="unreadCount > 0"
        class="btn-primary-action"
        @click="markAllAsRead"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="18" height="18">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
        <span>Barchasini O'qilgan deb belgilash</span>
      </button>
    </div>

    <!-- Metrics Bar -->
    <div class="metrics-cards-grid">
      <div class="card-metric card-blue">
        <div class="card-metric-icon">🔔</div>
        <div>
          <span class="metric-lbl">Jami Bildirishnomalar</span>
          <h4 class="metric-val text-blue">{{ notifications.length }} ta</h4>
        </div>
      </div>

      <div class="card-metric card-orange">
        <div class="card-metric-icon">⚡</div>
        <div>
          <span class="metric-lbl">O'qilmagan Xabarlar</span>
          <h4 class="metric-val text-orange">{{ unreadCount }} ta xabar</h4>
        </div>
      </div>
    </div>

    <!-- Filter Toolbar -->
    <div class="table-section-card margin-top">
      <div class="toolbar-bar">
        <div class="filter-controls">
          <button
            class="filter-tab-btn"
            :class="{ active: activeStatusFilter === '' }"
            @click="activeStatusFilter = ''"
          >
            Barchasi
          </button>
          <button
            class="filter-tab-btn"
            :class="{ active: activeStatusFilter === 'driving_lesson' }"
            @click="activeStatusFilter = 'driving_lesson'"
          >
            🏎️ Amaliy Haydash
          </button>
          <button
            class="filter-tab-btn"
            :class="{ active: activeStatusFilter === 'certificate_upload' }"
            @click="activeStatusFilter = 'certificate_upload'"
          >
            📄 Sertifikat
          </button>
          <button
            class="filter-tab-btn"
            :class="{ active: activeStatusFilter === 'payment' }"
            @click="activeStatusFilter = 'payment'"
          >
            💵 To'lov
          </button>
          <button
            class="filter-tab-btn"
            :class="{ active: activeStatusFilter === 'agent_payment' }"
            @click="activeStatusFilter = 'agent_payment'"
          >
            💼 Agent To'lovi
          </button>
        </div>
      </div>

      <!-- Notifications List -->
      <div class="notifications-container">
        <div v-if="loading" class="state-box">
          <div class="spinner"></div>
          <span>Bildirishnomalar yuklanmoqda...</span>
        </div>

        <div v-else-if="filteredNotifications.length === 0" class="empty-state">
          <p>Bildirishnomalar mavjud emas</p>
        </div>

        <div v-else class="notif-cards-list">
          <div
            v-for="item in filteredNotifications"
            :key="item.id"
            class="notif-card-item"
            :class="{ 'unread-card': !item.is_read }"
          >
            <div class="notif-card-left">
              <div class="status-avatar-box" :class="statusAvatarClass(item.status)">
                {{ statusIcon(item.status) }}
              </div>

              <div class="notif-content-area">
                <div class="notif-top-line">
                  <span class="status-chip-pill" :class="item.status">
                    {{ statusText(item.status) }}
                  </span>
                  <span class="notif-time font-mono">🕒 {{ formatDateTime(item.date) }}</span>
                </div>

                <h4 class="notif-title">{{ item.title }}</h4>
                <p v-if="item.note" class="notif-note-text">{{ item.note }}</p>
              </div>
            </div>

            <div class="notif-card-right">
              <span v-if="item.is_read" class="read-indicator">✓ O'qilgan</span>
              <button
                v-else
                class="btn-mark-read"
                @click="markSingleAsRead(item.id)"
              >
                O'qilgan deb belgilash
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useBranchStore } from '@/stores/branch'

const branchStore = useBranchStore()
const notifications = ref([])
const loading = ref(true)
const activeStatusFilter = ref('')

const unreadCount = computed(() => notifications.value.filter(n => !n.is_read && branchStore.isBranchMatch(n)).length)

const filteredNotifications = computed(() => {
  return notifications.value.filter(n => {
    if (!branchStore.isBranchMatch(n)) return false
    if (!activeStatusFilter.value) return true
    return n.status === activeStatusFilter.value
  })
})

async function fetchNotifications() {
  loading.value = true
  try {
    const res = await api.get('/notifications/', { params: { page_size: 100 } })
    notifications.value = res.data.results || res.data || []
  } catch (err) {
    console.error("Bildirishnomalarni yuklashda xatolik:", err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchNotifications()
})

async function markSingleAsRead(id) {
  try {
    await api.post(`/notifications/${id}/mark_as_read/`)
    const item = notifications.value.find(n => n.id === id)
    if (item) item.is_read = true
  } catch (err) {
    console.error("O'qilgan deb belgilashda xatolik:", err)
  }
}

async function markAllAsRead() {
  try {
    await api.post('/notifications/mark_all_read/')
    notifications.value.forEach(n => { n.is_read = true })
  } catch (err) {
    console.error("Barchasini o'qilgan deb belgilashda xatolik:", err)
  }
}

function statusIcon(st) {
  switch (st) {
    case 'driving_lesson': return '🏎️'
    case 'certificate_upload': return '📄'
    case 'payment': return '💵'
    case 'agent_payment': return '💼'
    default: return '🔔'
  }
}

function statusText(st) {
  switch (st) {
    case 'driving_lesson': return 'Amaliy Haydash Darsi'
    case 'certificate_upload': return 'Sertifikat'
    case 'payment': return 'To\'lov'
    case 'agent_payment': return 'Agent To\'lovi'
    default: return st || 'Bildirishnoma'
  }
}

function statusAvatarClass(st) {
  switch (st) {
    case 'driving_lesson': return 'bg-purple'
    case 'certificate_upload': return 'bg-blue'
    case 'payment': return 'bg-green'
    case 'agent_payment': return 'bg-amber'
    default: return 'bg-gray'
  }
}

function formatDateTime(dtStr) {
  if (!dtStr) return '-'
  const dt = new Date(dtStr)
  if (isNaN(dt.getTime())) return dtStr
  const day = String(dt.getDate()).padStart(2, '0')
  const month = String(dt.getMonth() + 1).padStart(2, '0')
  const year = dt.getFullYear()
  const hours = String(dt.getHours()).padStart(2, '0')
  const minutes = String(dt.getMinutes()).padStart(2, '0')
  return `${day}.${month}.${year} ${hours}:${minutes}`
}
</script>

<style scoped>
.page-top { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.page-main-title { font-size: 22px; font-weight: 800; color: #111827; }
.page-sub-title { font-size: 13px; color: #6B7280; margin-top: 2px; }

.btn-primary-action { display: flex; align-items: center; gap: 8px; background: linear-gradient(135deg, #10B981, #059669); color: white; border: none; padding: 10px 18px; border-radius: 12px; font-weight: 600; font-size: 13.5px; cursor: pointer; transition: all 0.2s ease; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25); }
.btn-primary-action:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(16, 185, 129, 0.35); }

.metrics-cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; }
.card-metric { background: white; border: 1.5px solid #E5E7EB; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); }
.card-metric-icon { font-size: 30px; }
.metric-lbl { font-size: 12.5px; color: #6B7280; font-weight: 600; }
.metric-val { font-size: 18px; font-weight: 800; color: #111827; margin-top: 4px; }
.text-blue { color: #2563EB; font-weight: 800; }
.text-orange { color: #EA580C; font-weight: 800; }

.margin-top { margin-top: 24px; }
.table-section-card { background: white; border: 1px solid #E5E7EB; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.toolbar-bar { display: flex; align-items: center; justify-content: space-between; padding: 14px 20px; border-bottom: 1px solid #E5E7EB; gap: 12px; flex-wrap: wrap; }
.filter-controls { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.filter-tab-btn { padding: 8px 16px; border-radius: 10px; font-size: 13px; font-weight: 600; border: 1.5px solid #E5E7EB; background: #F9FAFB; color: #4B5563; cursor: pointer; transition: all 0.15s ease; }
.filter-tab-btn:hover { background: #F3F4F6; }
.filter-tab-btn.active { background: #4F46E5; color: white; border-color: #4F46E5; }

.notifications-container { padding: 20px; }
.notif-cards-list { display: flex; flex-direction: column; gap: 14px; }
.notif-card-item { background: white; border: 1.5px solid #E5E7EB; border-radius: 14px; padding: 18px 22px; display: flex; align-items: center; justify-content: space-between; gap: 18px; transition: all 0.2s ease; }
.notif-card-item:hover { border-color: #CBD5E1; box-shadow: 0 4px 12px rgba(0,0,0,0.04); }
.notif-card-item.unread-card { border-left: 5px solid #4F46E5; background: #F8FAFC; }

.notif-card-left { display: flex; align-items: flex-start; gap: 16px; }
.status-avatar-box { font-size: 22px; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.bg-purple { background: #F3E8FF; }
.bg-blue { background: #DBEAFE; }
.bg-green { background: #DCFCE7; }
.bg-amber { background: #FEF3C7; }
.bg-gray { background: #F1F5F9; }

.notif-content-area { display: flex; flex-direction: column; gap: 4px; }
.notif-top-line { display: flex; align-items: center; gap: 10px; }
.status-chip-pill { font-size: 11.5px; font-weight: 700; padding: 2px 10px; border-radius: 12px; }
.status-chip-pill.driving_lesson { background: #F3E8FF; color: #7E22CE; }
.status-chip-pill.certificate_upload { background: #DBEAFE; color: #1D4ED8; }
.status-chip-pill.payment { background: #DCFCE7; color: #15803D; }
.status-chip-pill.agent_payment { background: #FEF3C7; color: #B45309; }

.notif-time { font-size: 12px; color: #94A3B8; }
.notif-title { font-size: 15px; font-weight: 700; color: #0F172A; margin-top: 2px; }
.notif-note-text { font-size: 13px; color: #475569; margin-top: 2px; }

.notif-card-right { flex-shrink: 0; }
.read-indicator { font-size: 12.5px; font-weight: 600; color: #94A3B8; }
.btn-mark-read { padding: 7px 14px; background: #EEF2FF; color: #4F46E5; border: 1px solid #C7D2FE; border-radius: 8px; font-size: 12.5px; font-weight: 600; cursor: pointer; transition: all 0.15s ease; }
.btn-mark-read:hover { background: #4F46E5; color: white; }

.state-box, .empty-state { text-align: center; padding: 40px 0; color: #6B7280; }
.spinner { width: 28px; height: 28px; border: 3px solid #E5E7EB; border-top-color: #4F46E5; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
