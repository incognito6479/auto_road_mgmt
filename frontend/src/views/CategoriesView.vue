<template>
  <AppLayout>

    <!-- Top action row -->
    <div class="page-top">
      <button class="btn-new" @click="openModal">Yangi Kategoriya</button>
    </div>

    <!-- Loading, error, or empty states -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">Kategoriyalar yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchCategories">Qayta urinish</button>
    </div>

    <div v-else-if="categories.length === 0" class="state-container">
      <p class="state-text">Hech qanday kategoriya topilmadi. Yangi kategoriya qo'shing.</p>
    </div>

    <!-- Category cards grid -->
    <div v-else class="cards-grid">
      <div class="cat-card" v-for="cat in enrichedCategories" :key="cat.id">

        <!-- Icon + title -->
        <div class="cat-header">
          <div class="cat-icon-wrap">
            <span v-html="cat.icon"></span>
          </div>
          <h3 class="cat-title">{{ cat.name }}</h3>
        </div>

        <!-- Stats: registered + price -->
        <div class="cat-stats">
          <div class="reg-block">
            <span class="reg-num">{{ cat.registered }}</span>
            <span class="reg-label"> Ro'yxatda</span>
          </div>
          <div class="price-block">
            <span class="price-label">Narxi: </span>
            <span class="price-val">{{ cat.formattedPrice }}</span>
          </div>
        </div>

        <!-- Progress bar -->
        <div class="progress-track">
          <div class="progress-fill" :style="{ width: cat.pct + '%' }"></div>
        </div>

        <!-- View details button -->
        <button class="btn-view">Ko'rish</button>

      </div>
    </div>

    <!-- New Category Dialog -->
    <dialog ref="categoryModal" class="modal-dialog" closedby="any" aria-labelledby="modal-title">
      <form class="modal-form" @submit.prevent="saveCategory">
        <h3 id="modal-title" class="modal-title">Yangi kategoriya qo'shish</h3>
        
        <div v-if="modalError" class="modal-error">
          {{ modalError }}
        </div>
        
        <div class="form-group">
          <label for="cat-name" class="form-label">Kategoriya nomi</label>
          <input
            id="cat-name"
            v-model="newCategory.name"
            type="text"
            placeholder="Masalan: B, A, BC"
            required
            class="form-input"
            maxlength="10"
          />
        </div>
        
        <div class="form-group">
          <label for="cat-price" class="form-label">Narxi (so'm)</label>
          <input
            id="cat-price"
            v-model="formattedInputPrice"
            type="text"
            placeholder="Masalan: 4 500 000"
            required
            class="form-input"
          />
        </div>
        
        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closeModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="saving">
            <span v-if="saving" class="btn-spinner"></span>
            {{ saving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'

// ── State ───────────────────────────────────────────
const categories = ref([])
const loading = ref(false)
const error = ref('')

const categoryModal = ref(null)
const newCategory = ref({
  name: '',
  price: null,
})
const saving = ref(false)
const modalError = ref('')

const formattedInputPrice = computed({
  get() {
    if (newCategory.value.price === null || newCategory.value.price === undefined || isNaN(newCategory.value.price)) {
      return ''
    }
    return String(newCategory.value.price).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  },
  set(value) {
    const digits = value.replace(/\D/g, '')
    if (digits === '') {
      newCategory.value.price = null
    } else {
      newCategory.value.price = parseInt(digits, 10)
    }
  }
})

// ── Icons & pricing helpers ──────────────────────────
const getCategoryIcon = (name) => {
  const norm = name.toUpperCase()
  if (norm.includes('B') && !norm.includes('C')) {
    return `<svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="1.6" width="36" height="36">
      <circle cx="12" cy="12" r="9.5"/>
      <circle cx="12" cy="12" r="3.5"/>
      <line x1="12" y1="8.5" x2="12" y2="2.5"/>
      <line x1="6.3" y1="15.5" x2="9.3" y2="13.4"/>
      <line x1="17.7" y1="15.5" x2="14.7" y2="13.4"/>
    </svg>`
  } else if (norm.includes('A')) {
    return `<svg viewBox="0 0 32 24" fill="none" stroke="#2D6A4F" stroke-width="1.6" width="36" height="36">
      <circle cx="6" cy="18" r="4"/>
      <circle cx="26" cy="18" r="4"/>
      <path d="M6 18h5l3-7h5l4 7"/>
      <path d="M14 11l1.5-4h3"/>
      <circle cx="20" cy="6" r="1.5"/>
    </svg>`
  } else if (norm.includes('BC') || norm.includes('C')) {
    return `<svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="1.6" width="36" height="36">
      <rect x="1" y="7" width="14" height="11" rx="1"/>
      <path d="M15 10h5l3 4v3h-8V10z"/>
      <circle cx="5.5" cy="18.5" r="1.5"/>
      <circle cx="18.5" cy="18.5" r="1.5"/>
    </svg>`
  } else if (norm.includes('D')) {
    return `<svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="1.6" width="36" height="36">
      <rect x="2" y="4" width="20" height="14" rx="2"/>
      <line x1="2" y1="9" x2="22" y2="9"/>
      <line x1="12" y1="4" x2="12" y2="18"/>
      <circle cx="6" cy="20" r="1.5"/>
      <circle cx="18" cy="20" r="1.5"/>
      <line x1="6" y1="18" x2="6" y2="21"/>
      <line x1="18" y1="18" x2="18" y2="21"/>
    </svg>`
  } else {
    return `<svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="1.6" width="36" height="36">
      <circle cx="12" cy="12" r="9.5"/>
      <path d="M12 8v8M8 12h8" stroke="#2D6A4F" stroke-width="1.6" stroke-linecap="round"/>
    </svg>`
  }
}

const formatPrice = (price) => {
  if (!price) return "0 so'm"
  return Number(price).toLocaleString('uz-UZ') + " so'm"
}

// ── Computed Enriched Categories ───────────────────
const enrichedCategories = computed(() => {
  return categories.value.map(cat => {
    const normName = cat.name.trim().toUpperCase()
    let registered = 0
    let pct = 0
    
    // Maintain mock numbers if using matching name to make UI populate beautifully
    if (normName.startsWith('B') && !normName.includes('C')) {
      registered = 78
      pct = 78
    } else if (normName.startsWith('A')) {
      registered = 34
      pct = 34
    } else if (normName.startsWith('BC')) {
      registered = 19
      pct = 19
    } else if (normName.startsWith('D')) {
      registered = 11
      pct = 11
    } else if (normName.startsWith('C')) {
      registered = 7
      pct = 7
    } else {
      registered = 0
      pct = 0
    }
    
    return {
      ...cat,
      registered,
      pct,
      icon: getCategoryIcon(cat.name),
      formattedPrice: formatPrice(cat.price)
    }
  })
})

// ── Fetch Categories ───────────────────────────────
const fetchCategories = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api.get('/categories/')
    categories.value = response.data
  } catch (err) {
    console.error(err)
    error.value = 'Kategoriyalarni yuklashda xatolik yuz berdi.'
  } finally {
    loading.value = false
  }
}

// ── Modal Actions ──────────────────────────────────
const openModal = () => {
  newCategory.value = { name: '', price: null }
  modalError.value = ''
  if (categoryModal.value) {
    categoryModal.value.showModal()
  }
}

const closeModal = () => {
  if (categoryModal.value) {
    categoryModal.value.close()
  }
}

const saveCategory = async () => {
  const nameTrimmed = newCategory.value.name.trim()
  if (!nameTrimmed || newCategory.value.price === null || newCategory.value.price === undefined) {
    modalError.value = 'Barcha maydonlarni to\'ldiring.'
    return
  }
  
  saving.value = true
  modalError.value = ''
  try {
    const payload = {
      name: nameTrimmed,
      price: parseInt(newCategory.value.price)
    }
    await api.post('/categories/', payload)
    closeModal()
    await fetchCategories()
  } catch (err) {
    console.error(err)
    if (err.response?.data?.name) {
      modalError.value = 'Kategoriya nomi band yoki xato kiritilgan.'
    } else if (err.response?.data?.price) {
      modalError.value = 'Kategoriya narxi noto\'g\'ri kiritilgan.'
    } else {
      modalError.value = 'Saqlashda xatolik yuz berdi.'
    }
  } finally {
    saving.value = false
  }
}

// ── Lifecycle & Listeners ──────────────────────────
onMounted(() => {
  fetchCategories()
  
  // Light dismiss fallback
  if (categoryModal.value && !('closedBy' in HTMLDialogElement.prototype)) {
    categoryModal.value.addEventListener('click', (event) => {
      if (event.target !== categoryModal.value) return
      const rect = categoryModal.value.getBoundingClientRect()
      const isInside = (
        rect.top <= event.clientY &&
        event.clientY <= rect.top + rect.height &&
        rect.left <= event.clientX &&
        event.clientX <= rect.left + rect.width
      )
      if (!isInside) {
        closeModal()
      }
    })
  }
})
</script>

<style scoped>
/* ── Top action bar ──────────────────────────────────── */
.page-top {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 24px;
}

.btn-new {
  padding: 9px 20px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: background 0.15s, transform 0.1s;
}
.btn-new:hover { background: #245C43; transform: translateY(-1px); }

/* ── States ─────────────────────────────────────────── */
.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: white;
  border-radius: 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
}
.state-text {
  font-size: 15px;
  color: #6B7280;
  font-weight: 500;
  margin: 12px 0 0 0;
}
.state-error .state-text {
  color: #DC2626;
}
.btn-retry {
  margin-top: 16px;
  padding: 8px 16px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}
.btn-retry:hover {
  background: #245C43;
}

/* Spinner */
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(45, 106, 79, 0.2);
  border-top-color: #2D6A4F;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── Cards grid ─────────────────────────────────────── */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px;
}

/* ── Card ───────────────────────────────────────────── */
.cat-card {
  background: white;
  border-radius: 14px;
  padding: 24px 22px 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: box-shadow 0.2s, transform 0.2s;
}
.cat-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.10), 0 8px 32px rgba(0,0,0,0.06);
  transform: translateY(-2px);
}

/* Header: icon + title */
.cat-header {
  display: flex;
  align-items: center;
  gap: 14px;
}

.cat-icon-wrap {
  width: 58px;
  height: 58px;
  background: #d1fae5;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.cat-title {
  font-size: 16.5px;
  font-weight: 700;
  color: #111827;
  margin: 0;
  line-height: 1.3;
}

/* Stats row: registered + price */
.cat-stats {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}

.reg-block {
  display: flex;
  align-items: baseline;
  gap: 0;
}

.reg-num {
  font-size: 32px;
  font-weight: 800;
  color: #111827;
  line-height: 1;
}

.reg-label {
  font-size: 14px;
  color: #6B7280;
  font-weight: 500;
  margin-left: 4px;
}

.price-block {
  text-align: right;
}

.price-label {
  font-size: 13px;
  color: #6B7280;
  font-weight: 500;
}

.price-val {
  font-size: 14px;
  font-weight: 700;
  color: #111827;
}

/* Progress bar */
.progress-track {
  height: 5px;
  background: #E5E7EB;
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #2D6A4F;
  border-radius: 6px;
}

/* View button */
.btn-view {
  width: 100%;
  padding: 11px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: background 0.15s;
}
.btn-view:hover { background: #245C43; }

/* ── Modal Dialog ───────────────────────────────────── */
.modal-dialog {
  border: none;
  border-radius: 16px;
  padding: 0;
  max-width: 420px;
  width: 90%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  background: white;
  overflow: visible;
}
.modal-dialog::backdrop {
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
}

.modal-form {
  padding: 28px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  border-bottom: 1px solid #E5E7EB;
  padding-bottom: 12px;
}

.modal-error {
  padding: 10px 12px;
  background: #FEE2E2;
  border-left: 4px solid #EF4444;
  color: #991B1B;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  text-align: left;
}

.form-label {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}

.form-input {
  padding: 10px 12px;
  border: 1.5px solid #D1D5DB;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s;
  font-family: inherit;
}
.form-input:focus {
  border-color: #2D6A4F;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

.btn-cancel {
  padding: 9px 16px;
  background: #F3F4F6;
  color: #374151;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-cancel:hover {
  background: #E5E7EB;
}

.btn-save {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 9px 20px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-save:hover:not(:disabled) {
  background: #245C43;
}
.btn-save:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Responsive */
@media (max-width: 1100px) { .cards-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px)  { .cards-grid { grid-template-columns: 1fr; } }
</style>
