<template>
  <AppLayout>

    <!-- Top Navigation & Title -->
    <div class="detail-header-nav">
      <button class="btn-back" @click="router.push('/groups')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        Ortga
      </button>
      <h2 class="page-title-text">{{ group?.name || 'Guruh yuklanmoqda...' }}</h2>
    </div>

    <!-- State containers -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">Guruh tafsilotlari yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchGroupDetail">Qayta urinish</button>
    </div>

    <div v-else-if="group">

      <!-- Group Dashboard Stats Card -->
      <div class="dashboard-stats-card">
        <div class="stat-item">
          <span class="stat-label">Kategoriya</span>
          <span class="stat-val text-green">{{ group.category_name }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Boshlanish sanasi</span>
          <span class="stat-val">{{ formatDate(group.started_at) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Davomiyligi</span>
          <span class="stat-val">{{ group.duration ? group.duration + ' oy' : '-' }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">O'quvchilar soni</span>
          <span class="stat-val highlight">{{ group.student_count }} ta</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Holati</span>
          <span class="status-badge-inline" :class="statusClass(group.status)">
            {{ statusText(group.status) }}
          </span>
        </div>
      </div>

      <div v-if="group.notes" class="group-notes-card">
        <h4 class="notes-title">Guruh bo'yicha eslatma:</h4>
        <p class="notes-content">{{ group.notes }}</p>
      </div>

      <!-- Students Table section -->
      <div class="students-section">
        <div class="section-top">
          <h3 class="section-title">Guruhdagi o'quvchilar</h3>
          
          <!-- Search fields -->
          <div class="search-filters">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Ism yoki Telefon bo'yicha qidirish"
              class="search-input"
            />
            <input
              v-model="searchJshshr"
              type="text"
              placeholder="JSHSHR bo'yicha"
              class="search-input-jshshr"
            />
          </div>
        </div>

        <div class="table-container">
          <table class="students-table">
            <thead>
              <tr>
                <th>F.I.SH.</th>
                <th>Telefon</th>
                <th>JSHSHR</th>
                <th>Eslatma</th>
                <th>Shartnoma summasi</th>
                <th>To'langan</th>
                <th>Qoldiq</th>
                <th style="text-align: center;">Amallar</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="filteredEnrollments.length === 0">
                <td colspan="8" class="td-empty">Hech qanday o'quvchi topilmadi.</td>
              </tr>
              <tr v-for="e in filteredEnrollments" :key="e.id">
                <td class="td-name">{{ e.student_name }}</td>
                <td class="td-phone">
                  <div>{{ formatPhone(e.student_phone) }}</div>
                  <div v-if="e.student_phone2" style="font-size: 11.5px; color: #6B7280; margin-top: 2px;">
                    Qo'shimcha: {{ formatPhone(e.student_phone2) }}
                  </div>
                </td>
                <td class="td-jshshr">{{ e.student_jshshr }}</td>
                <td class="td-notes">{{ e.notes || '-' }}</td>
                <td>
                  <span v-if="e.enrolled_free" class="free-badge">Tekin</span>
                  <span v-else>{{ formatMoney(e.enrolled_amount) }} so'm</span>
                </td>
                <td>
                  <span v-if="e.enrolled_free">-</span>
                  <span v-else class="paid-val">{{ formatMoney(e.paid_amount) }} so'm</span>
                </td>
                <td>
                  <span v-if="e.enrolled_free">-</span>
                  <span v-else :class="{'balance-warning': (e.enrolled_amount - e.paid_amount) > 0}">
                    {{ formatMoney(e.enrolled_amount - e.paid_amount) }} so'm
                  </span>
                </td>
                <td style="text-align: center;">
                  <button
                    v-if="!e.enrolled_free && e.paid_amount < e.enrolled_amount"
                    class="btn-pay"
                    @click="openPayModal(e)"
                  >
                    To'lash
                  </button>
                  <span v-else-if="!e.enrolled_free" class="fully-paid-badge">To'liq to'langan</span>
                  <span v-else>-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- Pay Modal Dialog -->
    <dialog ref="payModal" class="modal-dialog" closedby="any" aria-labelledby="pay-modal-title">
      <form class="modal-form" @submit.prevent="submitPayment">
        <h3 id="pay-modal-title" class="modal-title">To'lov qabul qilish</h3>

        <div v-if="payError" class="modal-error">
          {{ payError }}
        </div>

        <div class="pay-info-summary" v-if="activeEnrollment">
          <p>O'quvchi: <strong>{{ activeEnrollment.student_name }}</strong></p>
          <p>Shartnoma summasi: <strong>{{ formatMoney(activeEnrollment.enrolled_amount) }} so'm</strong></p>
          <p>Qoldiq: <strong class="balance-warning">{{ formatMoney(activeEnrollment.enrolled_amount - activeEnrollment.paid_amount) }} so'm</strong></p>
        </div>

        <div class="form-group">
          <label for="pay-amount" class="form-label">To'lov summasi (so'm)</label>
          <input
            id="pay-amount"
            v-model="formattedInputPrice"
            type="text"
            required
            class="form-input"
            placeholder="Masalan: 1 000 000"
          />
        </div>

        <div class="form-group">
          <label for="pay-method" class="form-label">To'lov turi</label>
          <div class="select-wrap" style="position: relative; display: flex; width: 100%;">
            <select id="pay-method" v-model="paymentForm.method" required class="form-input select-input" style="width: 100%; appearance: none; -webkit-appearance: none;">
              <option value="cash">Naqd</option>
              <option value="card">Plastik karta</option>
              <option value="bank">Bank o'tkazmasi</option>
            </select>
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #6B7280;">
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
            </svg>
          </div>
        </div>

        <div class="form-group">
          <label for="pay-notes" class="form-label">Eslatma</label>
          <textarea
            id="pay-notes"
            v-model="paymentForm.notes"
            placeholder="To'lov bo'yicha izoh"
            class="form-input text-area-input"
            rows="3"
          ></textarea>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closePayModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="paySaving">
            <span v-if="paySaving" class="btn-spinner"></span>
            {{ paySaving ? 'Kiritilmoqda...' : 'Tasdiqlash' }}
          </button>
        </div>
      </form>
    </dialog>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'

const router = useRouter()
const route = useRoute()
const groupId = route.params.id

const group = ref(null)
const loading = ref(false)
const error = ref('')

// Search state
const searchQuery = ref('')
const searchJshshr = ref('')

// Payment state
const payModal = ref(null)
const activeEnrollment = ref(null)
const paySaving = ref(false)
const payError = ref('')
const paymentForm = ref({
  amount: null,
  method: 'cash',
  notes: '',
})

// Two-way space formatting for payment amount
const formattedInputPrice = computed({
  get() {
    if (paymentForm.value.amount === null || paymentForm.value.amount === undefined || isNaN(paymentForm.value.amount)) {
      return ''
    }
    return String(paymentForm.value.amount).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  },
  set(value) {
    const digits = value.replace(/\D/g, '')
    if (digits === '') {
      paymentForm.value.amount = null
    } else {
      paymentForm.value.amount = parseInt(digits, 10)
    }
  }
})

const fetchGroupDetail = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api.get(`/groups/${groupId}/`)
    group.value = response.data
  } catch (err) {
    console.error(err)
    error.value = "Guruh tafsilotlarini yuklashda xatolik yuz berdi."
  } finally {
    loading.value = false
  }
}

const filteredEnrollments = computed(() => {
  if (!group.value?.enrollments) return []
  return group.value.enrollments.filter(e => {
    const q = searchQuery.value.toLowerCase()
    const matchSearch = !searchQuery.value || 
      e.student_name.toLowerCase().includes(q) || 
      e.student_phone.includes(q) ||
      (e.student_phone2 && e.student_phone2.includes(q))
    const matchJshshr = !searchJshshr.value || 
      e.student_jshshr.includes(searchJshshr.value)
    return matchSearch && matchJshshr
  })
})

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('uz-UZ')
}

const formatPhone = (phoneStr) => {
  if (!phoneStr) return '-'
  if (phoneStr.length === 12) {
    return `+${phoneStr.substring(0, 3)} (${phoneStr.substring(3, 5)}) ${phoneStr.substring(5, 8)}-${phoneStr.substring(8, 10)}-${phoneStr.substring(10, 12)}`
  }
  return phoneStr
}

const formatMoney = (amount) => {
  if (amount === null || amount === undefined) return '0'
  return String(amount).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
}

const statusText = (status) => {
  if (status === 'started') return 'Boshlangan'
  if (status === 'finished') return 'Tugatgan'
  if (status === 'canceled') return 'Bekor qilingan'
  return status
}

const statusClass = (status) => {
  return {
    'badge-started': status === 'started',
    'badge-finished': status === 'finished',
    'badge-canceled': status === 'canceled',
  }
}

// Payment modal actions
const openPayModal = (enrollment) => {
  activeEnrollment.value = enrollment
  payError.value = ''
  paymentForm.value = {
    amount: enrollment.enrolled_amount - enrollment.paid_amount,
    method: 'cash',
    notes: '',
  }
  if (payModal.value) {
    payModal.value.showModal()
  }
}

const closePayModal = () => {
  if (payModal.value) {
    payModal.value.close()
  }
  activeEnrollment.value = null
}

const submitPayment = async () => {
  if (paymentForm.value.amount === null || paymentForm.value.amount === undefined || paymentForm.value.amount <= 0) {
    payError.value = "To'g'ri to'lov summasini kiriting."
    return
  }

  paySaving.value = true
  payError.value = ''
  try {
    const payload = {
      enrollment: activeEnrollment.value.id,
      amount: parseInt(paymentForm.value.amount, 10),
      method: paymentForm.value.method,
      notes: paymentForm.value.notes.trim() || null,
      status: 'accepted'
    }
    await api.post('/payments/', payload)
    closePayModal()
    await fetchGroupDetail()
  } catch (err) {
    console.error(err)
    payError.value = "To'lovni saqlashda xatolik yuz berdi. Qayta urinib ko'ring."
  } finally {
    paySaving.value = false
  }
}

onMounted(() => {
  fetchGroupDetail()

  if (payModal.value && !('closedBy' in HTMLDialogElement.prototype)) {
    payModal.value.addEventListener('click', (event) => {
      if (event.target !== payModal.value) return
      const rect = payModal.value.getBoundingClientRect()
      const isInside = (
        rect.top <= event.clientY &&
        event.clientY <= rect.top + rect.height &&
        rect.left <= event.clientX &&
        event.clientX <= rect.left + rect.width
      )
      if (!isInside) {
        closePayModal()
      }
    })
  }
})
</script>

<style scoped>
/* ── Navigation ── */
.detail-header-nav {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}
.btn-back {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  color: #374151;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-back:hover {
  background: #F3F4F6;
  transform: translateX(-2px);
}
.page-title-text {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

/* ── States ── */
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
.btn-retry:hover { background: #245C43; }

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

/* ── Dashboard Card ── */
.dashboard-stats-card {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  background: white;
  border-radius: 14px;
  padding: 22px 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
  margin-bottom: 24px;
}

@media (max-width: 768px) {
  .dashboard-stats-card {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .dashboard-stats-card {
    grid-template-columns: 1fr;
  }
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-label {
  font-size: 12px;
  font-weight: 600;
  color: #6B7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-val {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
}

.stat-val.text-green {
  color: #2D6A4F;
}

.stat-val.highlight {
  color: #2D6A4F;
}

/* Badges */
.status-badge-inline {
  align-self: flex-start;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
}

.badge-started { background: #eff6ff; color: #1d4ed8; }
.badge-finished { background: #f3f4f6; color: #4b5563; }
.badge-canceled { background: #fef2f2; color: #b91c1c; }

/* Group Notes */
.group-notes-card {
  background: #F9FAFB;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.notes-title {
  font-size: 13.5px;
  font-weight: 700;
  color: #374151;
  margin: 0 0 6px 0;
}

.notes-content {
  font-size: 13px;
  color: #4B5563;
  margin: 0;
  line-height: 1.5;
}

/* ── Students List Section ── */
.students-section {
  background: white;
  border-radius: 14px;
  padding: 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
}

.section-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 20px;
}

.section-title {
  font-size: 16.5px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.search-filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.search-input, .search-input-jshshr {
  padding: 8px 14px;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  font-size: 13px;
  width: 250px;
  outline: none;
  transition: border-color 0.15s;
}

.search-input:focus, .search-input-jshshr:focus {
  border-color: #2D6A4F;
}

.search-input-jshshr {
  width: 150px;
}

/* Table */
.table-container {
  overflow-x: auto;
  border: 1px solid #E5E7EB;
  border-radius: 10px;
}

.students-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  text-align: left;
}

.students-table th {
  background: #F9FAFB;
  padding: 12px 16px;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #E5E7EB;
}

.students-table td {
  padding: 14px 16px;
  color: #4B5563;
  border-bottom: 1px solid #E5E7EB;
  vertical-align: middle;
}

.students-table tr:last-child td {
  border-bottom: none;
}

.td-name {
  font-weight: 600;
  color: #111827;
}

.td-phone, .td-jshshr {
  font-family: monospace;
  font-size: 12px;
}

.td-notes {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.td-empty {
  text-align: center;
  padding: 40px;
  color: #9CA3AF;
  font-weight: 500;
}

/* Pay Button */
.btn-pay {
  padding: 6px 14px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 12.5px;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-pay:hover {
  background: #245C43;
}

.fully-paid-badge {
  font-size: 11.5px;
  font-weight: 600;
  color: #047857;
  background: #ecfdf5;
  padding: 4px 10px;
  border-radius: 12px;
  display: inline-block;
}

.free-badge {
  font-size: 11.5px;
  font-weight: 600;
  color: #B45309;
  background: #FFFBEB;
  padding: 4px 10px;
  border-radius: 12px;
  display: inline-block;
}

.balance-warning {
  color: #DC2626;
  font-weight: 700;
}

.paid-val {
  color: #047857;
  font-weight: 600;
}

/* Pay summary info */
.pay-info-summary {
  background: #F3F4F6;
  border-radius: 10px;
  padding: 14px 16px;
  margin-bottom: 18px;
  font-size: 13.5px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.pay-info-summary p {
  margin: 0;
  color: #4B5563;
}
.pay-info-summary strong {
  color: #111827;
}

.text-area-input {
  resize: vertical;
  min-height: 80px;
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
  max-height: 90vh;
  overflow-y: auto;
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
  width: 100%;
  box-sizing: border-box;
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
.btn-save:hover {
  background: #245C43;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
</style>
