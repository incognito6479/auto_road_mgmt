<template>
  <AppLayout>

    <!-- Top Action Bar -->
    <div class="page-top">
      <div class="top-left">
        <button class="btn-back" @click="goBack" title="Orqaga">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          Avtomobillar ro'yxatiga qarash
        </button>
        <h2 class="page-main-title">{{ car?.car_name || 'Avtomobil Ma\'lumotlari' }}</h2>
      </div>

      <div v-if="authStore.isAdminOrSuperuser && car" class="header-actions">
        <button class="btn-edit-profile" @click="openEditModal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" style="margin-right: 6px;">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
            <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
          </svg>
          Tahrirlash
        </button>
      </div>
    </div>

    <!-- Loading / Error States -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">Avtomobil ma'lumotlari yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchCarDetail">Qayta urinish</button>
    </div>

    <div v-else-if="car" class="detail-container">

      <!-- Car Header Overview Card -->
      <div class="car-overview-card">
        <div class="car-header-row">
          <div class="car-photo-box" @click="openImageModal(car.image || '/default_car_photo.png')" title="Rasmni kattalashtirish">
            <img :src="car.image || '/default_car_photo.png'" alt="Car" class="car-photo-img" />
          </div>

          <div class="car-header-info">
            <div class="title-status-line">
              <h3 class="car-title-name">{{ car.car_name }}</h3>
              <span class="status-badge" :class="car.status">
                {{ statusText(car.status) }}
              </span>
            </div>
            <div class="plate-number-badge">
              🚘 {{ car.plate_number }}
            </div>
            <p v-if="car.notes" class="car-notes-sub">{{ car.notes }}</p>
          </div>
        </div>
      </div>

      <!-- Detail Grid Section -->
      <div class="detail-grid">
        
        <!-- Left: Technical Information -->
        <div class="info-card">
          <div class="card-header">
            <div class="icon-circle">
              <svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="2" width="20" height="20">
                <rect x="1" y="3" width="15" height="13"></rect>
                <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
                <circle cx="5.5" cy="18.5" r="2.5"></circle>
                <circle cx="18.5" cy="18.5" r="2.5"></circle>
              </svg>
            </div>
            <h4>Texnik Ma'lumotlar</h4>
          </div>

          <div class="info-list">
            <div class="info-item">
              <span class="item-label">Avtomobil nomi:</span>
              <span class="item-value font-bold">{{ car.car_name }}</span>
            </div>

            <div class="info-item">
              <span class="item-label">Davlat raqami:</span>
              <span class="item-value font-mono font-bold">{{ car.plate_number }}</span>
            </div>

            <div class="info-item">
              <span class="item-label">Ishlab chiqarilgan yili:</span>
              <span class="item-value">{{ car.manufact_year || '-' }}</span>
            </div>

            <div class="info-item">
              <span class="item-label">Filial (Branch):</span>
              <span class="item-value">{{ car.branch_name || car.branch?.name || '-' }}</span>
            </div>

            <div class="info-item">
              <span class="item-label">Status:</span>
              <span class="item-value"><span class="status-chip" :class="car.status">{{ statusText(car.status) }}</span></span>
            </div>
          </div>
        </div>

        <!-- Right: Insurance Policy & Inspection Cards -->
        <div class="status-cards-col">

          <!-- Sug'urta Card -->
          <div class="info-card">
            <div class="card-header">
              <div class="icon-circle icon-blue">
                <svg viewBox="0 0 24 24" fill="none" stroke="#0284C7" stroke-width="2" width="20" height="20">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                </svg>
              </div>
              <h4>Sug'urta Polis Muddati</h4>
            </div>

            <div class="policy-body">
              <div class="date-row">
                <span>Amal qilish muddati:</span>
                <span class="font-bold">{{ formatDate(car.policy_date) }}</span>
              </div>
              <div v-if="policyDaysRemaining !== null" class="days-remaining" :class="daysClass(policyDaysRemaining)">
                {{ daysRemainingText(policyDaysRemaining) }}
              </div>
            </div>
          </div>

          <!-- Texnik Ko'rik Card -->
          <div class="info-card">
            <div class="card-header">
              <div class="icon-circle icon-amber">
                <svg viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2" width="20" height="20">
                  <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
                </svg>
              </div>
              <h4>Texnik Ko'rik Muddati</h4>
            </div>

            <div class="policy-body">
              <div class="date-row">
                <span>Amal qilish muddati:</span>
                <span class="font-bold">{{ formatDate(car.tech_inspection_date) }}</span>
              </div>
              <div v-if="techDaysRemaining !== null" class="days-remaining" :class="daysClass(techDaysRemaining)">
                {{ daysRemainingText(techDaysRemaining) }}
              </div>
            </div>
          </div>

        </div>

      </div>

    </div>

    <!-- Edit Car Modal -->
    <dialog ref="carModal" class="modal-dialog">
      <div class="car-modal-header">
        <div class="header-badge-wrap">
          <div class="header-badge-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="2" width="22" height="22">
              <rect x="1" y="3" width="15" height="13"></rect>
              <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
              <circle cx="5.5" cy="18.5" r="2.5"></circle>
              <circle cx="18.5" cy="18.5" r="2.5"></circle>
            </svg>
          </div>
          <div>
            <h3 class="car-modal-title">Avtomobilni Tahrirlash</h3>
            <p class="car-modal-sub">Ma'lumotlarni va rasmni yangilang</p>
          </div>
        </div>
        <button class="car-btn-close" @click="closeModal" title="Yopish">✕</button>
      </div>

      <form @submit.prevent="saveCar" class="car-modal-form">
        <div v-if="modalError" class="modal-alert modal-alert-error">
          <span>{{ modalError }}</span>
        </div>

        <div class="form-group">
          <label class="form-label required">Avtomobil nomi va davlat raqami *</label>
          <input v-model="editForm.car_name" type="text" class="form-input" required placeholder="Masalan: Cobalt 01 A 777 AA" />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Ishlab chiqarilgan yili</label>
            <input v-model="editForm.manufact_year" type="number" class="form-input" placeholder="2022" />
          </div>

          <div class="form-group">
            <label class="form-label">Status</label>
            <select v-model="editForm.status" class="form-input">
              <option value="available">Mavjud (Bo'sh)</option>
              <option value="repairing">Ta'mirlashda</option>
              <option value="not_available">Mavjud emas</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Sug'urta muddati</label>
            <input v-model="editForm.policy_date" type="date" class="form-input" />
          </div>

          <div class="form-group">
            <label class="form-label">Texnik ko'rik muddati</label>
            <input v-model="editForm.tech_inspection_date" type="date" class="form-input" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Avtomobil Rasmi (Foto)</label>
          <div style="display: flex; align-items: center; gap: 12px; width: 100%;">
            <img v-if="editForm.existingImage" :src="editForm.existingImage" alt="Current Photo" style="width: 44px; height: 44px; border-radius: 8px; object-fit: cover; border: 1px solid #E5E7EB; flex-shrink: 0;" />
            <input type="file" accept="image/*" class="form-input" style="width: 100%;" @change="onCarFileChange" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Qo'shimcha izoh</label>
          <textarea v-model="editForm.notes" rows="3" class="form-input form-textarea"></textarea>
        </div>

        <div class="car-modal-footer">
          <button type="button" class="btn-cancel" @click="closeModal">Bekor qilish</button>
          <button type="submit" class="btn-submit" :disabled="saving">
            {{ saving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Image Zoom Modal -->
    <dialog ref="imageZoomModal" class="image-zoom-dialog" @click="imageZoomModal?.close()">
      <div class="image-zoom-content" @click.stop>
        <button type="button" class="image-zoom-close" @click="imageZoomModal?.close()">✕</button>
        <img :src="zoomedImageUrl" alt="Enlarged Photo" class="zoomed-img" />
      </div>
    </dialog>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { formatDate } from '@/utils/formatters'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const car = ref(null)
const loading = ref(true)
const error = ref(null)

const carModal = ref(null)
const saving = ref(false)
const modalError = ref(null)
const selectedCarFile = ref(null)

const editForm = ref({
  car_name: '',
  plate_number: '',
  manufact_year: '',
  status: 'available',
  policy_date: '',
  tech_inspection_date: '',
  notes: '',
  existingImage: null
})

const imageZoomModal = ref(null)
const zoomedImageUrl = ref('')

function openImageModal(url) {
  if (!url) return
  zoomedImageUrl.value = url
  imageZoomModal.value?.showModal()
}

function onCarFileChange(e) {
  selectedCarFile.value = e.target.files?.[0] || null
}

const policyDaysRemaining = computed(() => {
  if (!car.value?.policy_date) return null
  const target = new Date(car.value.policy_date)
  const today = new Date()
  today.setHours(0,0,0,0)
  const diffTime = target - today
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
})

const techDaysRemaining = computed(() => {
  if (!car.value?.tech_inspection_date) return null
  const target = new Date(car.value.tech_inspection_date)
  const today = new Date()
  today.setHours(0,0,0,0)
  const diffTime = target - today
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
})

function daysRemainingText(days) {
  if (days < 0) return `${Math.abs(days)} kun oldin muddati o'tgan`
  if (days === 0) return "Bugun muddati tugaydi!"
  return `${days} kun qoldi`
}

function daysClass(days) {
  if (days < 0) return 'days-expired'
  if (days <= 15) return 'days-warning'
  return 'days-good'
}

function statusText(st) {
  switch (st) {
    case 'available': return 'Mavjud'
    case 'repairing': return "Ta'mirlashda"
    case 'not_available': return 'Mavjud emas'
    default: return st || '-'
  }
}

async function fetchCarDetail() {
  loading.value = true
  error.value = null
  try {
    const res = await api.get(`/cars/${route.params.id}/`)
    car.value = res.data
  } catch (err) {
    console.error(err)
    error.value = "Avtomobil ma'lumotlarini yuklashda xatolik"
  } finally {
    loading.value = false
  }
}

function openEditModal() {
  modalError.value = null
  selectedCarFile.value = null
  editForm.value = {
    car_name: car.value.car_name || '',
    manufact_year: car.value.manufact_year || '',
    status: car.value.status || 'available',
    policy_date: car.value.policy_date || '',
    tech_inspection_date: car.value.tech_inspection_date || '',
    notes: car.value.notes || '',
    existingImage: car.value.image || null,
  }
  carModal.value?.showModal()
}

function closeModal() {
  carModal.value?.close()
}

async function saveCar() {
  if (!editForm.value.car_name || !editForm.value.car_name.trim()) {
    modalError.value = "Avtomobil nomini kiriting."
    return
  }
  saving.value = true
  modalError.value = null
  try {
    const payload = {
      car_name: editForm.value.car_name.trim(),
      status: editForm.value.status || 'available',
      manufact_year: editForm.value.manufact_year ? parseInt(editForm.value.manufact_year, 10) : null,
      policy_date: editForm.value.policy_date || null,
      tech_inspection_date: editForm.value.tech_inspection_date || null,
      notes: editForm.value.notes ? editForm.value.notes.trim() : '',
    }

    let res
    if (selectedCarFile.value) {
      const formData = new FormData()
      Object.keys(payload).forEach(k => {
        if (payload[k] !== null && payload[k] !== undefined) {
          formData.append(k, payload[k])
        }
      })
      formData.append('image', selectedCarFile.value)
      res = await api.patch(`/cars/${car.value.id}/`, formData)
    } else {
      res = await api.patch(`/cars/${car.value.id}/`, payload)
    }

    car.value = res.data
    closeModal()
  } catch (err) {
    console.error(err)
    if (err.response?.data) {
      const data = err.response.data
      if (typeof data === 'object') {
        const msgs = Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
        modalError.value = msgs.join(' | ')
      } else {
        modalError.value = String(data)
      }
    } else {
      modalError.value = "Saqlashda xatolik yuz berdi"
    }
  } finally {
    saving.value = false
  }
}

function goBack() {
  router.push('/vehicles')
}

onMounted(() => {
  fetchCarDetail()
})
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; }
.page-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.top-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 16px;
  border-radius: 10px;
  background: white;
  border: 1px solid #E5E7EB;
  font-size: 13.5px;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-back:hover {
  background: #F9FAFB;
  border-color: #D1D5DB;
}
.page-main-title {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
}

.btn-edit-profile {
  display: inline-flex;
  align-items: center;
  padding: 10px 18px;
  border-radius: 10px;
  background: #2D6A4F;
  color: white;
  font-size: 13.5px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: background 0.15s ease;
  box-shadow: 0 4px 12px rgba(45, 106, 79, 0.2);
}
.btn-edit-profile:hover {
  background: #1B4332;
}

.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
}
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #E5E7EB;
  border-top-color: #2D6A4F;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.state-text {
  margin-top: 12px;
  font-size: 14px;
  color: #6B7280;
}

.car-overview-card {
  background: white;
  border-radius: 16px;
  border: 1px solid #E5E7EB;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.03);
}
.car-header-row {
  display: flex;
  align-items: center;
  gap: 24px;
}
.car-photo-box {
  width: 120px;
  height: 90px;
  border-radius: 12px;
  overflow: hidden;
  background: #F3F4F6;
  border: 1px solid #E5E7EB;
  flex-shrink: 0;
  cursor: pointer;
  transition: transform 0.15s ease;
}
.car-photo-box:hover {
  transform: scale(1.03);
}
.car-photo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.car-header-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.title-status-line {
  display: flex;
  align-items: center;
  gap: 12px;
}
.car-title-name {
  font-size: 22px;
  font-weight: 800;
  color: #111827;
}
.status-badge {
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 20px;
  text-transform: capitalize;
}
.status-badge.available { background: #DCFCE7; color: #15803D; }
.status-badge.in_use { background: #FEF3C7; color: #B45309; }
.status-badge.maintenance { background: #FEE2E2; color: #B91C1C; }

.plate-number-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  background: #F3F4F6;
  border-radius: 8px;
  font-family: monospace;
  font-weight: 700;
  font-size: 15px;
  color: #1F2937;
}
.car-notes-sub {
  font-size: 13px;
  color: #6B7280;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.info-card {
  background: white;
  border-radius: 16px;
  border: 1px solid #E5E7EB;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.03);
}
.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.card-header h4 {
  font-size: 16px;
  font-weight: 700;
  color: #111827;
}
.icon-circle {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: #ECFDF5;
  display: flex;
  align-items: center;
  justify-content: center;
}
.icon-blue { background: #E0F2FE; }
.icon-amber { background: #FEF3C7; }

.info-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 12px;
  border-bottom: 1px dashed #F3F4F6;
}
.item-label { font-size: 13.5px; color: #6B7280; }
.item-value { font-size: 14px; color: #111827; }
.font-bold { font-weight: 700; }
.font-mono { font-family: monospace; }

.status-cards-col {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.policy-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.date-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
}
.days-remaining {
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.days-good { background: #ECFDF5; color: #047857; }
.days-warning { background: #FFFBEB; color: #B45309; }
.days-expired { background: #FEF2F2; color: #B91C1C; }

/* Modal Styles */
.modal-dialog {
  border: none;
  border-radius: 20px;
  padding: 0;
  width: 90%;
  max-width: 580px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  background: white;
  margin: auto;
}
.modal-dialog::backdrop {
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}
.car-modal-header {
  padding: 20px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #F3F4F6;
}
.header-badge-wrap { display: flex; align-items: center; gap: 12px; }
.header-badge-icon {
  width: 40px; height: 40px; border-radius: 12px; background: #ECFDF5;
  display: flex; align-items: center; justify-content: center;
}
.car-modal-title { font-size: 17px; font-weight: 700; color: #111827; }
.car-modal-sub { font-size: 12px; color: #6B7280; margin-top: 2px; }
.car-btn-close { background: none; border: none; font-size: 18px; color: #9CA3AF; cursor: pointer; }
.car-modal-form { padding: 24px; }
.form-group { margin-bottom: 16px; width: 100%; box-sizing: border-box; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; width: 100%; box-sizing: border-box; }
.form-label { display: block; font-size: 12.5px; font-weight: 600; color: #374151; margin-bottom: 6px; }
.form-input {
  width: 100%; box-sizing: border-box; padding: 10px 14px; border: 1.5px solid #E5E7EB;
  border-radius: 10px; font-size: 14px; background: #FAFAFA; color: #111827; outline: none;
}
.form-input:focus { border-color: #2D6A4F; background: white; box-shadow: 0 0 0 3.5px rgba(45,106,79,0.12); }
.car-modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.btn-cancel { padding: 10px 18px; border: 1px solid #D1D5DB; background: white; border-radius: 10px; font-weight: 600; font-size: 13px; color: #374151; cursor: pointer; }
.btn-submit { padding: 10px 22px; background: #2D6A4F; color: white; border-radius: 10px; font-weight: 600; font-size: 13.5px; border: none; cursor: pointer; }

/* Image Zoom Modal */
.image-zoom-dialog { border: none; background: transparent; padding: 0; max-width: 90vw; max-height: 90vh; margin: auto; overflow: visible; }
.image-zoom-dialog::backdrop { background: rgba(0, 0, 0, 0.75); backdrop-filter: blur(5px); }
.image-zoom-content { position: relative; display: flex; align-items: center; justify-content: center; }
.image-zoom-close { position: absolute; top: -16px; right: -16px; width: 32px; height: 32px; border-radius: 50%; background: white; color: #111827; font-weight: 700; font-size: 14px; border: none; box-shadow: 0 4px 12px rgba(0,0,0,0.3); cursor: pointer; z-index: 10; display: flex; align-items: center; justify-content: center; }
.zoomed-img { max-width: 85vw; max-height: 85vh; border-radius: 14px; object-fit: contain; box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
</style>
