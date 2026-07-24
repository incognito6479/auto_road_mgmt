<template>
  <AppLayout>

    <!-- Top Action Bar -->
    <div class="page-top">
      <div class="top-title-wrap">
        <h2 class="page-main-title">Bayramlar va Dam Olish Kunlari</h2>
        <p class="page-sub-title">Tizimdagi dam olish kunlari va rasmiy bayramlar boshqaruvi</p>
      </div>
      <button v-if="!authStore.isMechanic" class="btn-add" @click="openCreateModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="16" height="16">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        <span>Yangi Bayram Qo'shish</span>
      </button>
    </div>

    <!-- Filter & Search Bar -->
    <div class="filter-card">
      <div class="filter-field">
        <label class="filter-label">Bayram nomi bo'yicha qidirish</label>
        <div class="search-input-wrap">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Bayram nomini kiriting..."
            class="filter-input"
            @input="handleSearch"
          />
          <svg class="search-ico" viewBox="0 0 20 20" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
            <circle cx="8.5" cy="8.5" r="5.5"/>
            <line x1="12.5" y1="12.5" x2="16" y2="16"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- Loading / Error States -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">Bayramlar yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchHolidays">Qayta urinish</button>
    </div>

    <!-- Card Grid Layout -->
    <div v-else class="cards-grid">
      <div v-if="holidays.length === 0" class="empty-state">
        <div class="empty-icon-wrap">
          <svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="1.5" width="36" height="36">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
        </div>
        <p class="empty-title">Bayramlar topilmadi</p>
        <p class="empty-sub">Yangi dam olish kunini qo'shish uchun "+ Yangi Bayram Qo'shish" tugmasini bosing</p>
      </div>

      <div
        v-for="h in holidays"
        :key="h.id"
        class="holiday-card"
        :class="getHolidayStatus(h.start_date, h.end_date).statusClass"
      >
        <div class="card-header">
          <div class="holiday-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
          </div>
          <div class="card-title-wrap">
            <h3 class="holiday-name">{{ h.holiday_name }}</h3>
            <span class="status-badge" :class="getHolidayStatus(h.start_date, h.end_date).badgeClass">
              {{ getHolidayStatus(h.start_date, h.end_date).text }}
            </span>
          </div>
        </div>

        <div class="card-body">
          <div class="date-row">
            <span class="date-label">Sana oralig'i:</span>
            <span class="date-value">{{ formatDate(h.start_date) }} — {{ formatDate(h.end_date) }}</span>
          </div>
          <div class="days-count">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 16 14"></polyline>
            </svg>
            <span>{{ calculateDays(h.start_date, h.end_date) }} kun dam olish</span>
          </div>
          <p v-if="h.note" class="holiday-note">{{ h.note }}</p>
        </div>

        <div v-if="!authStore.isMechanic" class="card-footer">
          <button class="btn-card-action edit" @click="openEditModal(h)" title="Tahrirlash">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            <span>Tahrirlash</span>
          </button>
          <button class="btn-card-action delete" @click="openDeleteModal(h)" title="O'chirish">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
            <span>O'chirish</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Beautiful Create / Edit Modal Overlay -->
    <Transition name="modal">
      <div v-if="showHolidayModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card">

          <!-- Header -->
          <div class="modal-header-banner">
            <div class="modal-header-left">
              <div class="header-icon-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="16" y1="2" x2="16" y2="6"></line>
                  <line x1="8" y1="2" x2="8" y2="6"></line>
                  <line x1="3" y1="10" x2="21" y2="10"></line>
                </svg>
              </div>
              <div class="header-text-block">
                <h3 class="modal-title-text">{{ isEditing ? 'Bayramni Tahrirlash' : 'Yangi Bayram Qo\'shish' }}</h3>
                <p class="modal-subtitle-text">Tizimdagi dam olish kunlari va rasmiy ta'tillarni kiriting</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closeModal" title="Yopish">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>

          <!-- Form Body -->
          <form @submit.prevent="saveHoliday" class="modal-form-body">
            
            <div v-if="modalError" class="modal-error-alert">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
              <span>{{ modalError }}</span>
            </div>

            <!-- Field 1: Holiday Name -->
            <div class="form-field-group">
              <label class="field-label required">Bayram / Dam olish kuni nomi</label>
              <div class="field-input-icon-wrap">
                <input
                  v-model="form.holiday_name"
                  type="text"
                  class="field-input"
                  placeholder="Masalan: Navro'z bayrami"
                  required
                />
                <svg class="field-icon" viewBox="0 0 24 24" fill="none" stroke="#6B7280" stroke-width="1.8" width="18" height="18">
                  <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                  <line x1="7" y1="7" x2="7.01" y2="7"></line>
                </svg>
              </div>
            </div>

            <!-- Field 2: Date Range Row -->
            <div class="form-two-cols">
              <div class="form-field-group">
                <label class="field-label required">Boshlanish sanasi</label>
                <div class="field-input-icon-wrap">
                  <input
                    v-model="form.start_date"
                    type="date"
                    class="field-input date-input"
                    required
                  />
                </div>
              </div>

              <div class="form-field-group">
                <label class="field-label required">Tugash sanasi</label>
                <div class="field-input-icon-wrap">
                  <input
                    v-model="form.end_date"
                    type="date"
                    class="field-input date-input"
                    required
                  />
                </div>
              </div>
            </div>

            <!-- Calculated Live Days Pill -->
            <div v-if="liveDaysCount > 0" class="live-days-pill">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              <span>Ushbu bayram <strong>{{ liveDaysCount }} kun</strong> davom etadi</span>
            </div>

            <!-- Field 3: Note -->
            <div class="form-field-group">
              <label class="field-label">Qo'shimcha izoh / Ma'lumot</label>
              <textarea
                v-model="form.note"
                rows="3"
                class="field-input field-textarea"
                placeholder="Bayram va dam olish kunlari bo'yicha izoh (ixtiyoriy)..."
              ></textarea>
            </div>

            <!-- Footer Actions -->
            <div class="modal-footer-actions">
              <button type="button" class="btn-modal-cancel" @click="closeModal">
                Bekor qilish
              </button>
              <button type="submit" class="btn-modal-submit" :disabled="saving">
                <div v-if="saving" class="btn-spinner"></div>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <span>{{ saving ? 'Saqlanmoqda...' : (isEditing ? 'Saqlash' : 'Bayram Qo\'shish') }}</span>
              </button>
            </div>

          </form>
        </div>
      </div>
    </Transition>

    <!-- Beautiful Delete Confirmation Modal Overlay -->
    <Transition name="modal">
      <div v-if="showDeleteModal" class="modal-overlay" @click.self="closeDeleteModal">
        <div class="modal-card modal-card-sm">
          <div class="delete-card-content">
            <div class="delete-avatar-ring">
              <svg viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2" width="28" height="28">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
            </div>
            <h3 class="delete-heading">Bayramni o'chirish</h3>
            <p class="delete-description">
              Haqiqatan ham <strong>"{{ targetHoliday?.holiday_name }}"</strong> bayramini tizimdan o'chirmoqchimisiz?
            </p>

            <div class="delete-footer-actions">
              <button class="btn-modal-cancel" @click="closeDeleteModal">Bekor qilish</button>
              <button class="btn-delete-action" @click="confirmDelete" :disabled="deleting">
                <div v-if="deleting" class="btn-spinner"></div>
                <span>{{ deleting ? 'O\'chirilmoqda...' : 'O\'chirish' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { formatDate } from '@/utils/formatters'

const authStore = useAuthStore()

const holidays = ref([])
const loading = ref(true)
const error = ref(null)
const searchQuery = ref('')

const showHolidayModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const deleting = ref(false)
const modalError = ref(null)
const targetHoliday = ref(null)

const form = ref({
  id: null,
  holiday_name: '',
  start_date: '',
  end_date: '',
  note: ''
})

const liveDaysCount = computed(() => {
  if (!form.value.start_date || !form.value.end_date) return 0
  return calculateDays(form.value.start_date, form.value.end_date)
})

async function fetchHolidays() {
  loading.value = true
  error.value = null
  try {
    const res = await api.get('/holidays/', {
      params: { search: searchQuery.value || undefined, page_size: 100 }
    })
    holidays.value = res.data.results ? res.data.results : res.data
  } catch (err) {
    error.value = "Bayramlarni yuklashda xatolik yuz berdi"
  } finally {
    loading.value = false
  }
}

let searchTimeout = null
function handleSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchHolidays()
  }, 300)
}

function calculateDays(startStr, endStr) {
  if (!startStr || !endStr) return 0
  const s = new Date(startStr)
  const e = new Date(endStr)
  const diffTime = Math.abs(e - s)
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
}

function getHolidayStatus(startStr, endStr) {
  const today = new Date().toISOString().split('T')[0]
  if (today >= startStr && today <= endStr) {
    return { text: "Amaldagi", badgeClass: "badge-active", statusClass: "status-active" }
  } else if (today < startStr) {
    return { text: "Kutilayotgan", badgeClass: "badge-upcoming", statusClass: "status-upcoming" }
  } else {
    return { text: "O'tib ketgan", badgeClass: "badge-past", statusClass: "status-past" }
  }
}

function openCreateModal() {
  isEditing.value = false
  modalError.value = null
  form.value = { id: null, holiday_name: '', start_date: '', end_date: '', note: '' }
  showHolidayModal.value = true
}

function openEditModal(h) {
  isEditing.value = true
  modalError.value = null
  form.value = {
    id: h.id,
    holiday_name: h.holiday_name,
    start_date: h.start_date,
    end_date: h.end_date,
    note: h.note || ''
  }
  showHolidayModal.value = true
}

function closeModal() {
  showHolidayModal.value = false
}

async function saveHoliday() {
  if (!form.value.holiday_name.trim() || !form.value.start_date || !form.value.end_date) {
    modalError.value = "Barcha majburiy maydonlarni to'ldiring."
    return
  }

  saving.value = true
  modalError.value = null
  try {
    const payload = {
      holiday_name: form.value.holiday_name.trim(),
      start_date: form.value.start_date,
      end_date: form.value.end_date,
      note: form.value.note ? form.value.note.trim() : ''
    }

    if (isEditing.value) {
      await api.patch(`/holidays/${form.value.id}/`, payload)
    } else {
      await api.post('/holidays/', payload)
    }
    closeModal()
    fetchHolidays()
  } catch (err) {
    modalError.value = err.response?.data?.detail || "Saqlashda xatolik yuz berdi"
  } finally {
    saving.value = false
  }
}

function openDeleteModal(h) {
  targetHoliday.value = h
  showDeleteModal.value = true
}

function closeDeleteModal() {
  showDeleteModal.value = false
}

async function confirmDelete() {
  if (!targetHoliday.value) return
  deleting.value = true
  try {
    await api.delete(`/holidays/${targetHoliday.value.id}/`)
    closeDeleteModal()
    fetchHolidays()
  } catch (err) {
    alert("O'chirishda xatolik yuz berdi")
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchCurrentUser()
  }
  fetchHolidays()
})
</script>

<style scoped>
.page-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.page-main-title {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
}

.page-sub-title {
  font-size: 13px;
  color: #6B7280;
  margin-top: 4px;
}

.btn-add {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13.5px;
  box-shadow: 0 4px 12px rgba(45, 106, 79, 0.25);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(45, 106, 79, 0.35);
  }

  &:active {
    transform: translateY(0);
  }
}

.filter-card {
  background: white;
  padding: 18px 22px;
  border-radius: 14px;
  border: 1px solid #E5E7EB;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  margin-bottom: 24px;
}

.filter-label {
  font-size: 12.5px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  display: block;
}

.search-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.filter-input {
  width: 100%;
  padding: 11px 16px 11px 40px;
  border: 1px solid #D1D5DB;
  border-radius: 10px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s ease;

  &:focus {
    border-color: #2D6A4F;
    box-shadow: 0 0 0 4px rgba(45, 106, 79, 0.12);
  }
}

.search-ico {
  position: absolute;
  left: 14px;
  pointer-events: none;
}

.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 0;
}

.spinner {
  width: 38px;
  height: 38px;
  border: 3px solid #E5E7EB;
  border-top-color: #2D6A4F;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 48px 24px;
  background: white;
  border-radius: 16px;
  border: 1px dashed #D1D5DB;
}

.empty-icon-wrap {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: #F0FDF4;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.empty-title {
  font-size: 16px;
  font-weight: 700;
  color: #111827;
}

.empty-sub {
  font-size: 13px;
  color: #6B7280;
  margin-top: 4px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.holiday-card {
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 14px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: all 0.25s ease;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.07);
    border-color: #D1D5DB;
  }
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 16px;
}

.holiday-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: #F0FDF4;
  color: #2D6A4F;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.holiday-name {
  font-size: 16px;
  font-weight: 700;
  color: #111827;
}

.status-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  margin-top: 4px;
}

.badge-active { background: #DCFCE7; color: #166534; }
.badge-upcoming { background: #FEF3C7; color: #92400E; }
.badge-past { background: #F3F4F6; color: #6B7280; }

.card-body {
  margin-bottom: 16px;
}

.date-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  margin-bottom: 8px;
}

.date-label { color: #6B7280; }
.date-value { font-weight: 600; color: #1F2937; }

.days-count {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #2D6A4F;
  font-weight: 600;
  margin-bottom: 10px;
}

.holiday-note {
  font-size: 13px;
  color: #4B5563;
  background: #F9FAFB;
  padding: 10px 12px;
  border-radius: 8px;
  border-left: 3px solid #2D6A4F;
}

.card-footer {
  display: flex;
  gap: 10px;
  border-top: 1px solid #F3F4F6;
  padding-top: 14px;
}

.btn-card-action {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px;
  border-radius: 8px;
  font-size: 12.5px;
  font-weight: 600;
  border: 1px solid #E5E7EB;
  background: #F9FAFB;
  cursor: pointer;
  transition: all 0.2s ease;

  &.edit:hover { background: #EFF6FF; color: #2563EB; border-color: #BFDBFE; }
  &.delete:hover { background: #FEF2F2; color: #DC2626; border-color: #FECACA; }
}

/* ==========================================================
   ULTRA-BEAUTIFUL MODAL DESIGN SYSTEM
   ========================================================== */

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow-y: auto;
}

.modal-card {
  background: white;
  border-radius: 20px;
  width: 100%;
  max-width: 520px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.1);
  overflow: hidden;
  position: relative;
  transform-origin: center;

  &.modal-card-sm {
    max-width: 420px;
  }
}

/* Vue Modal Transition */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(10px);
}

/* Header Banner */
.modal-header-banner {
  padding: 24px 28px 20px;
  background: linear-gradient(180deg, #F0FDF4 0%, #FFFFFF 100%);
  border-bottom: 1px solid #F3F4F6;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.modal-header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon-box {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 18px -4px rgba(45, 106, 79, 0.35);
  flex-shrink: 0;
}

.modal-title-text {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  letter-spacing: -0.01em;
}

.modal-subtitle-text {
  font-size: 12.5px;
  color: #6B7280;
  margin-top: 3px;
}

.btn-modal-close {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid #E5E7EB;
  background: white;
  color: #6B7280;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #F3F4F6;
    color: #111827;
    transform: rotate(90deg);
  }
}

/* Form Body */
.modal-form-body {
  padding: 24px 28px 28px;
}

.modal-error-alert {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #FEF2F2;
  border: 1px solid #FCA5A5;
  border-radius: 10px;
  color: #991B1B;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 20px;
}

.form-field-group {
  margin-bottom: 20px;
}

.form-two-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.field-label {
  display: block;
  font-size: 12.5px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 7px;

  &.required::after {
    content: " *";
    color: #EF4444;
  }
}

.field-input-icon-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.field-input {
  width: 100%;
  padding: 11px 14px;
  padding-right: 40px;
  border: 1px solid #D1D5DB;
  border-radius: 10px;
  font-size: 14px;
  color: #111827;
  background: #FAFAFA;
  transition: all 0.2s ease;

  &.date-input {
    padding-right: 14px;
  }

  &:focus {
    background: white;
    border-color: #2D6A4F;
    outline: none;
    box-shadow: 0 0 0 4px rgba(45, 106, 79, 0.12);
  }

  &::placeholder {
    color: #9CA3AF;
  }
}

.field-textarea {
  padding-right: 14px;
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.field-icon {
  position: absolute;
  right: 14px;
  pointer-events: none;
}

.live-days-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: #F0FDF4;
  border: 1px solid #BBF7D0;
  border-radius: 8px;
  color: #166534;
  font-size: 12.5px;
  font-weight: 500;
  margin-bottom: 20px;
  width: 100%;
}

/* Footer Actions */
.modal-footer-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid #F3F4F6;
}

.btn-modal-cancel {
  padding: 11px 20px;
  border: 1px solid #D1D5DB;
  background: white;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13.5px;
  color: #4B5563;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #F9FAFB;
    color: #111827;
    border-color: #9CA3AF;
  }
}

.btn-modal-submit {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 11px 24px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13.5px;
  box-shadow: 0 4px 14px rgba(45, 106, 79, 0.35);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(45, 106, 79, 0.45);
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Delete Modal Styling */
.delete-card-content {
  padding: 32px 28px 28px;
  text-align: center;
}

.delete-avatar-ring {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #FEE2E2;
  border: 4px solid #FEF2F2;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 18px;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.15);
}

.delete-heading {
  font-size: 19px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
}

.delete-description {
  font-size: 13.5px;
  color: #4B5563;
  line-height: 1.5;
  margin-bottom: 24px;
}

.delete-footer-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn-delete-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 11px 24px;
  background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13.5px;
  box-shadow: 0 4px 14px rgba(220, 38, 38, 0.35);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(220, 38, 38, 0.45);
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
}
</style>
