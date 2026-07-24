<template>
  <AppLayout>

    <!-- Top Info bar -->
    <div class="payments-title-bar">
      <h2 class="page-title-text">To'lovlar Tarixi</h2>
    </div>

    <!-- State containers -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">To'lovlar yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchPayments">Qayta urinish</button>
    </div>

    <div v-else>

      <!-- Filters Card -->
      <div class="filter-card" style="grid-template-columns: repeat(4, 1fr);">
        <div class="filter-field">
          <label class="filter-label">O'quvchi ismi</label>
          <input
            v-model="filterStudentName"
            type="text"
            placeholder="Qidirish..."
            class="filter-input"
          />
        </div>

        <div class="filter-field">
          <label class="filter-label">JSHSHR</label>
          <input
            v-model="filterJshshr"
            type="text"
            placeholder="JSHSHR bo'yicha..."
            class="filter-input"
          />
        </div>

        <div class="filter-field">
          <label class="filter-label">Kategoriya</label>
          <div class="select-wrap">
            <select v-model="filterCategory" class="filter-select">
              <option value="">Barchasi</option>
              <option v-for="c in categories" :key="c.id" :value="c.name">
                {{ c.name }}
              </option>
            </select>
            <svg class="select-arrow" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
            </svg>
          </div>
        </div>

        <div class="filter-field">
          <label class="filter-label">Holati</label>
          <div class="select-wrap">
            <select v-model="filterStatus" class="filter-select">
              <option value="">Barchasi</option>
              <option value="accepted">Qabul qilingan</option>
              <option value="returned">Qaytarilgan</option>
              <option value="paid">To'langan</option>
              <option value="bonus">Bonus</option>
              <option value="bank">Bank</option>
            </select>
            <svg class="select-arrow" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
            </svg>
          </div>
        </div>

        <div class="filter-field">
          <label class="filter-label">Sana (Dan)</label>
          <input
            v-model="filterDateFrom"
            type="date"
            class="filter-input"
          />
        </div>

        <div class="filter-field">
          <label class="filter-label">Sana (Gacha)</label>
          <input
            v-model="filterDateTo"
            type="date"
            class="filter-input"
          />
        </div>

        <div class="filter-field">
          <label class="filter-label">To'lov turi</label>
          <div class="select-wrap">
            <select v-model="filterMethod" class="filter-select">
              <option value="">Barchasi</option>
              <option value="cash">Naqd</option>
              <option value="card">Plastik karta</option>
              <option value="qr_code">QR kod</option>
              <option value="transfer">Bank o'tkazmasi</option>
            </select>
            <svg class="select-arrow" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
            </svg>
          </div>
        </div>
        <div class="filter-field">
          <label class="filter-label">Agent bo'yicha</label>
          <div class="select-wrap">
            <select v-model="filterAgent" class="filter-select">
              <option value="">Barcha agentlar</option>
              <option v-for="a in agents" :key="a.id" :value="a.id">
                {{ a.full_name }}
              </option>
            </select>
            <svg class="select-arrow" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
            </svg>
          </div>
        </div>
      </div>

      <!-- Payments Table Card -->
      <div class="table-card">
        <div class="table-container">
          <table class="payments-table">
            <thead>
              <tr>
                <th style="width: 60px;">ID</th>
                <th>O'quvchi</th>
                <th>JSHSHR</th>
                <th>Kategoriya</th>
                <th>Agent</th>
                <th>Sana</th>
                <th class="th-cashier">Kassir (Tel)</th>
                <th>Summa</th>
                <th>To'lov turi</th>
                <th>Holati</th>
                <th>Izoh</th>
                <th v-if="authStore.isSuperuser" style="text-align: center; width: 80px;">Amallar</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="payments.length === 0">
                <td :colspan="authStore.isSuperuser ? 12 : 11" class="td-empty">To'lovlar topilmadi.</td>
              </tr>
              <tr v-for="p in payments" :key="p.id">
                <td class="td-id">#{{ p.id }}</td>
                <td class="td-student">{{ p.student_name || '-' }}</td>
                <td class="td-jshshr" style="font-family: monospace; font-size: 12px;">{{ p.student_jshshr || '-' }}</td>
                <td class="td-cat">{{ p.category_name || '-' }}</td>
                <td class="td-agent">{{ p.agent_name || '-' }}</td>
                <td class="td-date">{{ formatDateTime(p.created_at) }}</td>
                <td class="td-cashier">{{ formatPhone(p.cashier_name) }}</td>
                <td class="td-amount">{{ formatMoney(p.amount) }} so'm</td>
                <td class="td-method">{{ formatMethodText(p.method) }}</td>
                <td>
                  <span class="status-badge" :class="statusClass(p.status)">
                    {{ statusText(p.status) }}
                  </span>
                </td>
                <td class="td-notes" :title="p.notes">{{ p.notes || '-' }}</td>
                <td v-if="authStore.isSuperuser" style="text-align: center;">
                  <button class="btn-edit" @click="openEditModal(p)" title="Tahrirlash">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15" style="vertical-align: middle;">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Pagination controls -->
          <div class="pagination-bar" style="display: flex; justify-content: space-between; align-items: center; margin-top: 20px; padding: 12px 16px; background: #F9FAFB; border-top: 1px solid #E5E7EB; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;">
            <span class="pagination-info" style="font-size: 13.5px; color: #6B7280; font-weight: 500;">
              Jami: <strong>{{ totalCount }}</strong> tadan <strong>{{ totalCount > 0 ? (currentPage - 1) * pageSize + 1 : 0 }} - {{ Math.min(currentPage * pageSize, totalCount) }}</strong> ko'rsatilmoqda
            </span>
            <div class="pagination-actions" style="display: flex; gap: 8px;">
              <button class="btn-page" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">
                Oldingi
              </button>
              <span class="page-num" style="display: inline-flex; align-items: center; padding: 0 12px; font-weight: 600; color: #374151; font-size: 14px;">
                Sahifa {{ currentPage }} / {{ totalPages }}
              </span>
              <button class="btn-page" :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">
                Keyingi
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Edit Payment Modal Dialog -->
    <dialog ref="editPaymentModal" class="modal-dialog" closedby="any" aria-labelledby="edit-modal-title">
      <form class="modal-form" @submit.prevent="updatePayment">
        <h3 id="edit-modal-title" class="modal-title">To'lovni tahrirlash</h3>

        <div v-if="editError" class="modal-error">
          {{ editError }}
        </div>

        <div class="form-group">
          <label for="edit-amount" class="form-label">To'lov summasi (so'm)</label>
          <input
            id="edit-amount"
            v-model="formattedEditPrice"
            type="text"
            required
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="edit-method" class="form-label">To'lov turi</label>
          <div class="select-wrap" style="position: relative; display: flex; width: 100%;">
            <select id="edit-method" v-model="editingPayment.method" required class="form-input select-input" style="width: 100%; appearance: none; -webkit-appearance: none;">
              <option value="cash">Naqd</option>
              <option value="card">Plastik karta</option>
              <option value="qr_code">QR kod</option>
              <option value="transfer">Bank o'tkazmasi</option>
            </select>
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #6B7280;">
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
            </svg>
          </div>
        </div>

        <div class="form-group">
          <label for="edit-status" class="form-label">Holati</label>
          <div class="select-wrap" style="position: relative; display: flex; width: 100%;">
            <select id="edit-status" v-model="editingPayment.status" required class="form-input select-input" style="width: 100%; appearance: none; -webkit-appearance: none;">
              <option value="accepted">Qabul qilingan</option>
              <option value="returned">Qaytarilgan</option>
              <option value="paid">To'langan</option>
              <option value="bonus">Bonus</option>
              <option value="bank">Bank</option>
            </select>
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #6B7280;">
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
            </svg>
          </div>
        </div>

        <div class="form-group">
          <label for="edit-notes" class="form-label">Eslatma</label>
          <textarea
            id="edit-notes"
            v-model="editingPayment.notes"
            placeholder="To'lov bo'yicha izoh"
            class="form-input text-area-input"
            rows="3"
          ></textarea>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closeEditModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="editSaving">
            <span v-if="editSaving" class="btn-spinner"></span>
            {{ editSaving ? 'Saqlanmoqda...' : 'Saqlash' }}
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
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const payments = ref([])
const loading = ref(false)
const error = ref('')

// Filter states
const filterDateFrom = ref('')
const filterDateTo = ref('')
const filterMethod = ref('')
const filterStatus = ref('')

// New category/student search/Jshshr/agent filters
const categories = ref([])
const agents = ref([])
const filterCategory = ref('')
const filterStudentName = ref('')
const filterJshshr = ref('')
const filterAgent = ref('')

// Pagination state
const currentPage = ref(1)
const totalCount = ref(0)
const pageSize = 50
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize) || 1)

// Edit state
const editPaymentModal = ref(null)
const editSaving = ref(false)
const editError = ref('')
const editingPayment = ref({
  id: null,
  amount: null,
  method: 'cash',
  status: 'accepted',
  notes: '',
})

// Two-way space formatting for edit amount
const formattedEditPrice = computed({
  get() {
    if (editingPayment.value.amount === null || editingPayment.value.amount === undefined || isNaN(editingPayment.value.amount)) {
      return ''
    }
    return String(editingPayment.value.amount).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  },
  set(value) {
    const digits = value.replace(/\D/g, '')
    if (digits === '') {
      editingPayment.value.amount = null
    } else {
      editingPayment.value.amount = parseInt(digits, 10)
    }
  }
})

const fetchPayments = async () => {
  loading.value = true
  error.value = ''
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize
    }
    if (filterDateFrom.value) params.date_from = filterDateFrom.value
    if (filterDateTo.value) params.date_to = filterDateTo.value
    if (filterMethod.value) params.method = filterMethod.value
    if (filterCategory.value) params.category = filterCategory.value
    if (filterStudentName.value) params.student_name = filterStudentName.value.trim()
    if (filterJshshr.value) params.jshshr = filterJshshr.value.trim()

    if (filterAgent.value) {
      params.agent = filterAgent.value
      params.status = 'bonus'
    } else if (filterStatus.value) {
      params.status = filterStatus.value
    }

    const response = await api.get('/payments/', { params })
    payments.value = response.data.results || response.data
    totalCount.value = response.data.count || payments.value.length
  } catch (err) {
    console.error(err)
    error.value = "To'lovlar ro'yxatini yuklashda xatolik yuz berdi."
  } finally {
    loading.value = false
  }
}

watch(filterAgent, (newVal) => {
  if (newVal) {
    filterStatus.value = 'bonus'
  }
})

watch(
  [filterDateFrom, filterDateTo, filterMethod, filterStatus, filterCategory, filterStudentName, filterJshshr, filterAgent],
  () => {
    currentPage.value = 1
    fetchPayments()
  }
)

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchPayments()
}

const fetchCategories = async () => {
  try {
    const [cRes, aRes] = await Promise.all([
      api.get('/categories/?page_size=100'),
      api.get('/agents/?page_size=100')
    ])
    categories.value = cRes.data.results ? cRes.data.results : cRes.data
    agents.value = aRes.data.results ? aRes.data.results : aRes.data
  } catch (err) {
    console.error('Error fetching categories and agents:', err)
  }
}

const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return '-'
  const d = new Date(dateTimeStr)
  return `${d.toLocaleDateString('uz-UZ')} ${d.toLocaleTimeString('uz-UZ', {hour: '2-digit', minute:'2-digit'})}`
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

const formatMethodText = (method) => {
  if (method === 'cash') return 'Naqd'
  if (method === 'card') return 'Plastik karta'
  if (method === 'qr_code') return 'QR kod'
  if (method === 'transfer') return "O'tkazma"
  return method
}

const statusText = (status) => {
  if (status === 'accepted') return 'Qabul qilingan'
  if (status === 'returned') return 'Qaytarilgan'
  if (status === 'paid') return "To'langan"
  if (status === 'bonus') return 'Bonus'
  if (status === 'bank') return 'Bank'
  return status
}

const statusClass = (status) => {
  return {
    'badge-accepted': status === 'accepted',
    'badge-returned': status === 'returned',
    'badge-paid': status === 'paid',
    'badge-bonus': status === 'bonus',
    'badge-bank': status === 'bank',
  }
}

// Edit Payment modals
const openEditModal = (p) => {
  if (!authStore.isSuperuser) {
    alert("Faqat superuser to'lov ma'lumotlarini tahrirlashi mumkin.")
    return
  }
  editingPayment.value = {
    id: p.id,
    amount: p.amount,
    method: p.method,
    status: p.status,
    notes: p.notes || '',
  }
  editError.value = ''
  if (editPaymentModal.value) {
    editPaymentModal.value.showModal()
  }
}

const closeEditModal = () => {
  if (editPaymentModal.value) {
    editPaymentModal.value.close()
  }
}

const updatePayment = async () => {
  if (!authStore.isSuperuser) {
    editError.value = "Faqat superuser to'lov ma'lumotlarini tahrirlashi mumkin."
    return
  }

  if (editingPayment.value.amount === null || editingPayment.value.amount === undefined || editingPayment.value.amount <= 0) {
    editError.value = "To'g'ri to'lov summasini kiriting."
    return
  }

  editSaving.value = true
  editError.value = ''
  try {
    const payload = {
      amount: parseInt(editingPayment.value.amount, 10),
      method: editingPayment.value.method,
      status: editingPayment.value.status,
      notes: editingPayment.value.notes.trim() || null,
    }
    await api.patch(`/payments/${editingPayment.value.id}/`, payload)
    closeEditModal()
    await fetchPayments()
  } catch (err) {
    console.error(err)
    editError.value = "Saqlashda xatolik yuz berdi. Qayta urinib ko'ring."
  } finally {
    editSaving.value = false
  }
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchCurrentUser()
  }
  fetchPayments()
  fetchCategories()

  if (editPaymentModal.value && !('closedBy' in HTMLDialogElement.prototype)) {
    editPaymentModal.value.addEventListener('click', (event) => {
      if (event.target !== editPaymentModal.value) return
      const rect = editPaymentModal.value.getBoundingClientRect()
      const isInside = (
        rect.top <= event.clientY &&
        event.clientY <= rect.top + rect.height &&
        rect.left <= event.clientX &&
        event.clientX <= rect.left + rect.width
      )
      if (!isInside) {
        closeEditModal()
      }
    })
  }
})
</script>

<style scoped>
.payments-title-bar {
  margin-bottom: 24px;
}
.page-title-text {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

/* ── Filter Card ── */
.filter-card {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .filter-card {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .filter-card {
    grid-template-columns: 1fr;
  }
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

.filter-input {
  padding: 8px 12px;
  border: 1.5px solid #D1D5DB;
  border-radius: 8px;
  font-size: 13.5px;
  outline: none;
  transition: border-color 0.15s;
  background: white;
}
.filter-input:focus {
  border-color: #2D6A4F;
}

/* Select wrapper */
.select-wrap {
  position: relative;
  display: flex;
}

.filter-select {
  width: 100%;
  padding: 8px 12px;
  padding-right: 32px;
  border: 1.5px solid #D1D5DB;
  border-radius: 8px;
  font-size: 13.5px;
  outline: none;
  transition: border-color 0.15s;
  background: white;
  appearance: none;
  -webkit-appearance: none;
  cursor: pointer;
}
.filter-select:focus {
  border-color: #2D6A4F;
}

.select-arrow {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9CA3AF;
  pointer-events: none;
}

/* ── Table Card ── */
.table-card {
  background: white;
  border-radius: 14px;
  padding: 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
}

.table-container {
  overflow-x: auto;
  border: 1px solid #E5E7EB;
  border-radius: 10px;
}

.payments-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  text-align: left;
}

.payments-table th {
  background: #F9FAFB;
  padding: 12px 16px;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #E5E7EB;
}

.payments-table td {
  padding: 14px 16px;
  color: #4B5563;
  border-bottom: 1px solid #E5E7EB;
  vertical-align: middle;
}

.payments-table tr:last-child td {
  border-bottom: none;
}

.td-id {
  font-weight: 600;
  color: #6B7280;
}

.td-student {
  font-weight: 600;
  color: #111827;
}

.td-cat {
  font-weight: 500;
  color: #374151;
}

.td-date, .td-cashier {
  font-family: monospace;
  font-size: 12px;
}

.td-amount {
  font-weight: 700;
  color: #2D6A4F;
}

.td-notes {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Strict phone column width */
.th-cashier, .td-cashier {
  width: 175px !important;
  min-width: 175px !important;
  max-width: 175px !important;
  white-space: nowrap !important;
}

.td-empty {
  text-align: center;
  padding: 40px;
  color: #9CA3AF;
  font-weight: 500;
}

/* Edit action button */
.btn-edit {
  color: #4B5563;
  padding: 6px;
  border-radius: 8px;
  background: #F3F4F6;
  border: 1px solid #E5E7EB;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  cursor: pointer;
}
.btn-edit:hover {
  background: #E5E7EB;
  color: #111827;
  transform: scale(1.05);
}

/* Status Badges */
.status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
  display: inline-block;
}

.badge-accepted {
  background: #E8F5E9;
  color: #2E7D32;
  border: 1px solid #C8E6C9;
}

.badge-returned {
  background: #FFEBEE;
  color: #C62828;
  border: 1px solid #FFCDD2;
}

.badge-paid {
  background: #E3F2FD;
  color: #1565C0;
  border: 1px solid #BBDEFB;
}

.badge-bonus {
  background: #F3E8FF;
  color: #7E22CE;
  border: 1px solid #E9D5FF;
}

.badge-bank {
  background: #E0F2FE;
  color: #0369A1;
  border: 1px solid #BAE6FD;
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

/* ── Modal Dialog ── */
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

.text-area-input {
  resize: vertical;
  min-height: 80px;
}

/* Pagination styles */
.btn-page {
  padding: 6px 14px;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-page:hover:not(:disabled) {
  background: #F3F4F6;
  border-color: #D1D5DB;
}
.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
