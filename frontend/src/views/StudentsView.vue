<template>
  <AppLayout>

    <!-- Top action -->
    <div class="page-top">
      <button class="btn-add" @click="openModal">Yangi O'quvchi Qo'shish</button>
    </div>

    <!-- Filter card -->
    <div class="filter-card">
      <div class="filter-field">
        <label class="filter-label">Holat bo'yicha saralash</label>
        <div class="select-wrap">
          <select v-model="filterStatus" class="filter-select">
            <option value="">Barchasi</option>
            <option value="Yangi">Yangi</option>
            <option value="Qabul qilingan">Qabul qilingan</option>
            <option value="Tugatgan">Tugatgan</option>
          </select>
          <svg class="select-arrow" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
            <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
          </svg>
        </div>
      </div>

      <div class="filter-field">
        <label class="filter-label">Ism yoki Telefon raqami bo'yicha qidirish</label>
        <input
          v-model="filterSearch"
          class="filter-input"
          type="text"
          placeholder="Ism yoki Telefon raqami bo'yicha qidirish"
        />
      </div>

      <div class="filter-field">
        <label class="filter-label">JSHSHR bo'yicha qidirish (faqat raqam)</label>
        <input
          v-model="filterJshshr"
          class="filter-input"
          type="text"
          placeholder="JSHSHR"
        />
      </div>
    </div>

    <!-- Loading / error states -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">O'quvchilar yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchStudents">Qayta urinish</button>
    </div>

    <!-- Table -->
    <div v-else class="table-wrap">
      <table class="stbl">
        <thead>
          <tr>
            <th>To'liq Ismi</th>
            <th>Kategoriya</th>
            <th>Telefon Raqami</th>
            <th>JSHSHR</th>
            <th>Passport Ma'lumotlari</th>
            <th>Ro'yxatdan o'tgan sana</th>
            <th>Holat</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredStudents.length === 0">
            <td colspan="7" class="no-data">Ma'lumot topilmadi</td>
          </tr>
          <tr v-for="s in filteredStudents" :key="s.id" class="stbl-row">
            <td class="td-name">{{ s.name }}</td>
            <td class="td-cat">{{ s.category }}</td>
            <td class="td-muted">{{ s.phone }}</td>
            <td class="td-muted">{{ s.jshshr }}</td>
            <td class="td-muted">{{ s.passport }}</td>
            <td class="td-muted">{{ s.date }}</td>
            <td>
              <span class="status-badge" :class="statusClass(s.status)">{{ s.status }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- New Student Modal Dialog -->
    <dialog ref="studentModal" class="modal-dialog" closedby="any" aria-labelledby="modal-title">
      <form class="modal-form" @submit.prevent="saveStudent">
        <h3 id="modal-title" class="modal-title">Yangi o'quvchi qo'shish</h3>

        <div v-if="modalError" class="modal-error">
          {{ modalError }}
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label for="std-name" class="form-label">F.I.SH. (To'liq ism)</label>
            <input
              id="std-name"
              v-model="newStudent.full_name"
              type="text"
              placeholder="Masalan: Abdullayev Ali"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="std-phone" class="form-label">Telefon raqami</label>
            <input
              id="std-phone"
              v-model="newStudent.phone"
              type="tel"
              placeholder="+998 90 123 45 67"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="std-jshshr" class="form-label">JSHSHR (14 xonali raqam)</label>
            <input
              id="std-jshshr"
              v-model="newStudent.jshshr"
              type="text"
              placeholder="Masalan: 30101990001014"
              required
              maxlength="14"
              class="form-input"
            />
          </div>

          <div class="form-row-group">
            <div class="form-group half-width">
              <label for="std-pass-serie" class="form-label">Pass. Seriya</label>
              <input
                id="std-pass-serie"
                v-model="newStudent.passport_serie"
                type="text"
                placeholder="AA"
                required
                maxlength="2"
                class="form-input text-uppercase"
              />
            </div>
            <div class="form-group half-width">
              <label for="std-pass-num" class="form-label">Pass. Raqam</label>
              <input
                id="std-pass-num"
                v-model="newStudent.passport_number"
                type="text"
                placeholder="1234567"
                required
                maxlength="7"
                class="form-input"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="std-cat" class="form-label">Kategoriya</label>
            <div class="select-wrap">
              <select id="std-cat" v-model="newStudent.category" required class="form-input select-input">
                <option value="" disabled>Kategoriyani tanlang</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }} ({{ Number(cat.price).toLocaleString('uz-UZ') }} so'm)
                </option>
              </select>
              <svg class="select-arrow-modal" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
              </svg>
            </div>
          </div>

          <div class="form-group">
            <label for="std-payment" class="form-label">Boshlang'ich to'lov (so'm)</label>
            <input
              id="std-payment"
              v-model="formattedMinPayment"
              type="text"
              placeholder="Masalan: 1 000 000"
              required
              class="form-input"
            />
          </div>
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
import { ref, computed, onMounted, watch } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'

// ── Filter state ─────────────────────────────────────────────
const filterStatus = ref('')
const filterSearch = ref('')
const filterJshshr = ref('')

// ── Loading & state ──────────────────────────────────────────
const students = ref([])
const categories = ref([])
const loading = ref(false)
const error = ref('')

// ── Modal state ──────────────────────────────────────────────
const studentModal = ref(null)
const newStudent = ref({
  full_name: '',
  phone: '',
  jshshr: '',
  passport_serie: '',
  passport_number: '',
  category: '',
  min_payment: null,
})
const saving = ref(false)
const modalError = ref('')

// Watch phone for formatting: +998 90 900 90 90
watch(() => newStudent.value.phone, (newValue) => {
  if (!newValue) return
  let digits = newValue.replace(/\D/g, '')

  if (digits.length > 0 && !digits.startsWith('998')) {
    digits = '998' + digits
  }

  // Enforce max 12 digits (998 + 9 digits)
  digits = digits.substring(0, 12)

  let formatted = ''
  if (digits.length > 0) {
    formatted += '+' + digits.substring(0, 3)
  }
  if (digits.length > 3) {
    formatted += ' ' + digits.substring(3, 5)
  }
  if (digits.length > 5) {
    formatted += ' ' + digits.substring(5, 8)
  }
  if (digits.length > 8) {
    formatted += ' ' + digits.substring(8, 10)
  }
  if (digits.length > 10) {
    formatted += ' ' + digits.substring(10, 12)
  }

  if (newValue !== formatted) {
    newStudent.value.phone = formatted
  }
})

// Two-way formatting for min_payment
const formattedMinPayment = computed({
  get() {
    if (newStudent.value.min_payment === null || newStudent.value.min_payment === undefined || isNaN(newStudent.value.min_payment)) {
      return ''
    }
    return String(newStudent.value.min_payment).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  },
  set(value) {
    const digits = value.replace(/\D/g, '')
    if (digits === '') {
      newStudent.value.min_payment = null
    } else {
      newStudent.value.min_payment = parseInt(digits, 10)
    }
  }
})

// ── Fetch data ───────────────────────────────────────────────
const fetchStudents = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api.get('/students/')
    students.value = response.data.map(mapStudent)
  } catch (err) {
    console.error(err)
    error.value = "O'quvchilarni yuklashda xatolik yuz berdi."
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const response = await api.get('/categories/')
    categories.value = response.data
  } catch (err) {
    console.error('Error fetching categories:', err)
  }
}

const mapStudent = (s) => {
  let statusText = 'Yangi'
  if (s.status === 'enrolled') statusText = "Qabul qilingan"
  else if (s.status === 'finished') statusText = 'Tugatgan'
  
  const dateStr = s.created_at ? new Date(s.created_at).toLocaleDateString('uz-UZ') : ''
  
  return {
    id: s.id,
    name: s.full_name,
    category: s.category || '-',
    phone: formatPhoneDisplay(s.phone),
    jshshr: String(s.jshshr),
    passport: `${s.passport_serie} ${s.passport_number}`,
    date: dateStr,
    status: statusText,
  }
}

const formatPhoneDisplay = (p) => {
  if (!p) return ''
  if (p.includes(' ')) return p
  const digits = p.replace(/\D/g, '')
  if (digits.length === 12) {
    return `+${digits.substring(0, 3)} ${digits.substring(3, 5)} ${digits.substring(5, 8)} ${digits.substring(8, 10)} ${digits.substring(10, 12)}`
  }
  return p
}

onMounted(() => {
  fetchStudents()
  fetchCategories()
  
  // Light dismiss fallback
  if (studentModal.value && !('closedBy' in HTMLDialogElement.prototype)) {
    studentModal.value.addEventListener('click', (event) => {
      if (event.target !== studentModal.value) return
      const rect = studentModal.value.getBoundingClientRect()
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

// ── Filtered computed ────────────────────────────────────────
const filteredStudents = computed(() => {
  return students.value.filter(s => {
    const matchStatus = !filterStatus.value || s.status === filterStatus.value
    const q = filterSearch.value.toLowerCase()
    const matchSearch = !q || s.name.toLowerCase().includes(q) || s.phone.includes(q)
    const matchJshshr = !filterJshshr.value || s.jshshr.includes(filterJshshr.value)
    return matchStatus && matchSearch && matchJshshr
  })
})

// ── Status badge class ───────────────────────────────────────
function statusClass(status) {
  if (status === 'Yangi') return 'badge-new'
  if (status === "Qabul qilingan" || status === "Ro'yxatdan o'tgan") return 'badge-registered'
  if (status === 'Tugatgan') return 'badge-done'
  return ''
}

// ── Modal Actions ────────────────────────────────────────────
const openModal = () => {
  newStudent.value = {
    full_name: '',
    phone: '',
    jshshr: '',
    passport_serie: '',
    passport_number: '',
    category: '',
    min_payment: null,
  }
  modalError.value = ''
  if (studentModal.value) {
    studentModal.value.showModal()
  }
}

const closeModal = () => {
  if (studentModal.value) {
    studentModal.value.close()
  }
}

const saveStudent = async () => {
  const s = newStudent.value
  const phoneCleaned = s.phone.replace(/\D/g, '')
  
  if (!s.full_name.trim() || !phoneCleaned || !s.jshshr || !s.passport_serie.trim() || !s.passport_number || !s.category || s.min_payment === null) {
    modalError.value = "Barcha maydonlarni to'ldiring."
    return
  }
  
  if (phoneCleaned.length < 12) {
    modalError.value = "Telefon raqami noto'g'ri kiritilgan."
    return
  }
  
  if (String(s.jshshr).length !== 14) {
    modalError.value = "JSHSHR 14 ta raqam bo'lishi shart."
    return
  }
  
  saving.value = true
  modalError.value = ''
  
  try {
    const payload = {
      full_name: s.full_name.trim(),
      phone: phoneCleaned,
      jshshr: parseInt(s.jshshr, 10),
      passport_serie: s.passport_serie.trim().toUpperCase(),
      passport_number: parseInt(s.passport_number, 10),
      category: parseInt(s.category, 10),
      min_payment: parseInt(s.min_payment, 10)
    }
    
    await api.post('/students/', payload)
    closeModal()
    await fetchStudents()
  } catch (err) {
    console.error(err)
    if (err.response?.data?.phone) {
      modalError.value = "Ushbu telefon raqamli o'quvchi allaqachon mavjud."
    } else if (err.response?.data?.jshshr) {
      modalError.value = "Ushbu JSHSHR egasi bo'lgan o'quvchi allaqachon mavjud."
    } else if (err.response?.data?.passport_number) {
      modalError.value = "Ushbu passport raqamli o'quvchi allaqachon mavjud."
    } else {
      modalError.value = "Saqlashda xatolik yuz berdi. Ma'lumotlarni tekshirib qayta urinib ko'ring."
    }
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
/* ── Top action ─────────────────────────────────────────── */
.page-top {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.btn-add {
  padding: 10px 20px;
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
.btn-add:hover { background: #245C43; transform: translateY(-1px); }

/* ── Filter card ─────────────────────────────────────────── */
.filter-card {
  display: grid;
  grid-template-columns: 1fr 1.4fr 1fr;
  gap: 16px;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 20px;
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-label {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
}

/* Select wrapper */
.select-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.filter-select {
  width: 100%;
  appearance: none;
  -webkit-appearance: none;
  padding: 9px 34px 9px 12px;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  font-size: 13px;
  color: #374151;
  background: white;
  outline: none;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  transition: border-color 0.15s;
}
.filter-select:focus { border-color: #2D6A4F; }

.select-arrow {
  position: absolute;
  right: 10px;
  color: #9CA3AF;
  pointer-events: none;
  flex-shrink: 0;
}

/* Text inputs */
.filter-input {
  padding: 9px 12px;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  font-size: 13px;
  color: #374151;
  outline: none;
  font-family: 'Inter', sans-serif;
  transition: border-color 0.15s;
}
.filter-input:focus { border-color: #2D6A4F; }
.filter-input::placeholder { color: #9CA3AF; }

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

/* ── Table ─────────────────────────────────────────────────── */
.table-wrap {
  background: white;
  border-radius: 12px;
  border: 1px solid #E5E7EB;
  overflow: hidden;
}

.stbl {
  width: 100%;
  border-collapse: collapse;
  font-size: 13.5px;
}

.stbl thead th {
  padding: 13px 16px;
  text-align: left;
  font-size: 13px;
  font-weight: 700;
  color: #111827;
  border-bottom: 2px solid #F3F4F6;
  white-space: nowrap;
  background: white;
}

.stbl tbody .stbl-row td {
  padding: 13px 16px;
  border-bottom: 1px solid #F9FAFB;
  vertical-align: middle;
}

.stbl tbody .stbl-row:last-child td { border-bottom: none; }
.stbl tbody .stbl-row:hover td { background: #FAFAFA; }

.td-name {
  font-weight: 600;
  color: #111827;
  white-space: nowrap;
}

.td-cat {
  font-size: 20px;
  font-weight: 900;
  color: #2D6A4F;
  letter-spacing: -0.01em;
}

.td-muted { color: #6B7280; }

/* No data row */
.no-data {
  text-align: center;
  padding: 40px;
  color: #9CA3AF;
  font-size: 14px;
}

/* ── Status badges ──────────────────────────────────────────── */
.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.badge-new {
  background: white;
  color: #374151;
  border: 1.5px solid #D1D5DB;
}

.badge-registered {
  background: #2D6A4F;
  color: white;
}

.badge-done {
  background: #1B2430;
  color: white;
}

/* ── Modal Dialog ───────────────────────────────────── */
.modal-dialog {
  border: none;
  border-radius: 16px;
  padding: 0;
  max-width: 500px;
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

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row-group {
  display: flex;
  gap: 16px;
}

.half-width {
  flex: 1;
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
  width: 100%;
  box-sizing: border-box;
}
.form-input:focus {
  border-color: #2D6A4F;
}

.text-uppercase {
  text-transform: uppercase;
}

.select-input {
  appearance: none;
  -webkit-appearance: none;
  cursor: pointer;
  padding-right: 32px;
}

.select-arrow-modal {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9CA3AF;
  pointer-events: none;
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

/* ── Responsive ─────────────────────────────────────────────── */
@media (max-width: 900px) {
  .filter-card { grid-template-columns: 1fr; }
  .table-wrap  { overflow-x: auto; }
}
</style>
