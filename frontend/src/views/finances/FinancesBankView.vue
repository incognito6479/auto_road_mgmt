<template>
  <AppLayout>

    <div class="page-top">
      <div>
        <h2 class="page-main-title">Bank uchun (Status: Bank)</h2>
        <p class="page-sub-title">Bank orqali o'tkazilgan va rasmiylashtiriladigan to'lovlar</p>
      </div>

      <button class="btn-primary-action btn-blue" @click="openCreateModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="18" height="18">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        <span>Yangi bank to'lovini kiritish</span>
      </button>
    </div>

    <!-- Metrics Cards -->
    <div class="metrics-cards-grid">
      <div class="card-metric card-blue">
        <div class="card-metric-icon">🏦</div>
        <div>
          <span class="metric-lbl">Jami Bank Operatsiyalari</span>
          <h4 class="metric-val text-blue">{{ payments.length }} ta to'lov</h4>
        </div>
      </div>

      <div class="card-metric card-purple font-hero">
        <div class="card-metric-icon">📊</div>
        <div>
          <span class="metric-lbl">Jami Bank Summasi</span>
          <h4 class="metric-val text-purple">{{ formatMoney(metrics.total) }}</h4>
        </div>
      </div>
    </div>

    <!-- Table Section -->
    <div class="table-section-card margin-top">
      <div class="toolbar-bar">
        <div class="search-box">
          <svg viewBox="0 0 20 20" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
            <circle cx="8.5" cy="8.5" r="5.5"/>
            <line x1="13" y1="13" x2="18" y2="18"/>
          </svg>
          <input
            v-model="filterStudentName"
            type="text"
            placeholder="Izoh yoki sana bo'yicha qidirish..."
            class="search-input"
          />
        </div>

        <div class="filter-controls">
          <div class="filter-item">
            <label class="flabel">Dan:</label>
            <input v-model="filterDateFrom" type="date" class="finput-date" />
          </div>

          <div class="filter-item">
            <label class="flabel">Gacha:</label>
            <input v-model="filterDateTo" type="date" class="finput-date" />
          </div>
        </div>

        <div class="total-count">
          Jami: <strong>{{ totalCount }}</strong> ta bank to'lovi
        </div>
      </div>

      <div class="table-container">
        <div v-if="loading" class="state-box">
          <div class="spinner"></div>
          <span>Bank to'lovlari yuklanmoqda...</span>
        </div>

        <div v-else-if="payments.length === 0" class="empty-state">
          <p>Bank statusidagi to'lovlar topilmadi</p>
        </div>

        <table v-else class="data-table">
          <thead>
            <tr>
              <th>To'lov Tafsiloti / Izoh</th>
              <th>Bank Summasi</th>
              <th>Usul</th>
              <th>Sana & Vaqt</th>
              <th style="width: 110px; text-align: right;">Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in payments" :key="p.id" class="table-row">
              <td class="td-name">
                <div v-if="p.student" class="student-name link-value" @click="goStudent(p.student)">{{ p.notes || p.student_name || 'Bank Operatsiyasi' }}</div>
                <div v-else class="student-name">{{ p.notes || p.student_name || 'Bank Operatsiyasi' }}</div>
                <div v-if="p.group_name" class="group-sub">{{ p.group_name }}</div>
              </td>
              <td class="td-amount">
                <span class="amount-val text-blue">{{ formatMoney(p.amount) }}</span>
              </td>
              <td><span class="method-chip">{{ methodText(p.method) }}</span></td>
              <td class="td-date">{{ formatDateTime(p.created_at) }}</td>
              <td style="text-align: right;">
                <div class="row-actions">
                  <template v-if="authStore.isSuperuser">
                    <button class="btn-action-edit" @click="openEditModal(p)" title="Tahrirlash">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                        <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                      </svg>
                    </button>
                    <button class="btn-action-delete" @click="openDeleteModal(p)" title="O'chirish">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                      </svg>
                    </button>
                  </template>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- CREATE / EDIT MODAL (STUDENT SELECT REMOVED AS REQUESTED) -->
    <Transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card">
          <div class="modal-header-banner blue-banner">
            <div class="header-left-info">
              <div class="header-icon-box blue-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <path d="M3 21h18M3 10h18M5 6l7-3 7 3M4 10v11M20 10v11M8 14v3M12 14v3M16 14v3"></path>
                </svg>
              </div>
              <div>
                <h3>{{ isEditing ? "Bank To'lovini Tahrirlash" : "Yangi Bank To'lovi" }}</h3>
                <p>Status: Bank</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closeModal">✕</button>
          </div>

          <form @submit.prevent="savePayment" class="modal-body">
            <div v-if="modalError" class="alert-error">{{ modalError }}</div>

            <!-- Amount Input -->
            <div class="form-group">
              <label class="flabel required">Bank Summasi *</label>
              <input
                v-model="form.amountFormatted"
                type="text"
                class="finput amount-input blue-text"
                placeholder="0"
                required
                @input="onAmountInput"
              />
            </div>

            <!-- Method Select -->
            <div class="form-group">
              <label class="flabel required">To'lov Usuli *</label>
              <div class="select-wrap-relative">
                <select v-model="form.method" class="fselect-field">
                  <option value="cash">Naqd</option>
                  <option value="card">Karta</option>
                  <option value="qr_code">QR code</option>
                  <option value="click">Click</option>
                  <option value="transfer">O'tkazma</option>
                </select>
                <div class="select-chevron-icon">▼</div>
              </div>
            </div>

            <!-- Notes -->
            <div class="form-group">
              <label class="flabel">Izoh / Kvitansiya ma'lumoti</label>
              <input v-model="form.notes" type="text" class="finput" placeholder="Bank kvitansiya raqami yoki izoh..." />
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-cancel" @click="closeModal">Bekor qilish</button>
              <button type="submit" class="btn-save btn-blue-save" :disabled="saving">
                {{ saving ? "Saqlanmoqda..." : "Bank To'lovini Saqlash" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <ConfirmDeleteModal
      ref="deleteModal"
      title="To'lovni O'chirish"
      :deleting="deleting"
      :error="deleteError"
      @confirm="performDelete"
    >
      Haqiqatan ham <strong>#{{ deletingPayment?.id }}</strong> raqamli bank to'lovini o'chirmoqchimisiz?
    </ConfirmDeleteModal>

  </AppLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import ConfirmDeleteModal from '@/components/ConfirmDeleteModal.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { formatMoney } from '@/utils/formatters'

const authStore = useAuthStore()
const router = useRouter()

function goStudent(id) {
  if (!id) return
  router.push(`/students/${id}`)
}

const payments = ref([])
const loading = ref(true)
const totalCount = ref(0)

const filterStudentName = ref('')
const filterDateFrom = ref('')
const filterDateTo = ref('')
const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const saving = ref(false)
const modalError = ref(null)

const form = ref({ amountFormatted: '', amount: 0, method: 'transfer', notes: '' })

const metrics = computed(() => {
  const total = payments.value.reduce((s, p) => s + (p.amount || 0), 0)
  return { total }
})

async function fetchPayments() {
  loading.value = true
  try {
    const params = { status: 'bank', page_size: 1000 }
    if (filterStudentName.value) params.student_name = filterStudentName.value.trim()
    if (filterDateFrom.value) params.date_from = filterDateFrom.value
    if (filterDateTo.value) params.date_to = filterDateTo.value

    const res = await api.get('/payments/', { params })
    payments.value = res.data.results || res.data
    totalCount.value = res.data.count || payments.value.length
  } catch (err) { console.error(err) }
  finally { loading.value = false }
}

watch([filterStudentName, filterDateFrom, filterDateTo], () => { fetchPayments() })

function methodText(m) {
  switch (m) {
    case 'cash': return 'Naqd'
    case 'card': return 'Karta'
    case 'qr_code': return 'QR code'
    case 'click': return 'Click'
    case 'transfer': return "O'tkazma"
    default: return m
  }
}

function formatDateTime(dtStr) {
  if (!dtStr) return '-'
  const d = new Date(dtStr)
  return `${d.toLocaleDateString('uz-UZ')} ${d.toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' })}`
}

function onAmountInput(e) {
  const digits = e.target.value.replace(/\D/g, '')
  if (!digits) { form.value.amount = 0; form.value.amountFormatted = ''; return }
  const num = parseInt(digits, 10)
  form.value.amount = num
  form.value.amountFormatted = formatMoney(num, false)
}

function openCreateModal() {
  isEditing.value = false
  editingId.value = null
  modalError.value = null
  form.value = { amountFormatted: '', amount: 0, method: 'transfer', notes: '' }
  showModal.value = true
}

function openEditModal(p) {
  isEditing.value = true
  editingId.value = p.id
  modalError.value = null
  form.value = { amountFormatted: formatMoney(p.amount, false), amount: p.amount, method: p.method || 'transfer', notes: p.notes || '' }
  showModal.value = true
}

function closeModal() { showModal.value = false }

async function savePayment() {
  if (!form.value.amount || form.value.amount <= 0) { modalError.value = "To'g'ri bank summasini kiriting."; return }
  saving.value = true
  modalError.value = null
  try {
    if (isEditing.value) {
      await api.patch(`/payments/${editingId.value}/`, { amount: form.value.amount, method: form.value.method, notes: form.value.notes })
    } else {
      await api.post('/payments/', { user: authStore.user?.id, amount: form.value.amount, status: 'bank', method: form.value.method, notes: form.value.notes })
    }
    closeModal()
    fetchPayments()
  } catch (err) { modalError.value = err.response?.data?.detail || "Saqlashda xatolik yuz berdi" }
  finally { saving.value = false }
}

const deleteModal = ref(null)
const deletingPayment = ref(null)
const deleting = ref(false)
const deleteError = ref('')

function openDeleteModal(p) {
  deletingPayment.value = p
  deleteError.value = ''
  deleteModal.value?.show()
}

async function performDelete() {
  if (!deletingPayment.value) return
  deleting.value = true
  deleteError.value = ''
  try {
    await api.delete(`/payments/${deletingPayment.value.id}/`)
    deleteModal.value?.close()
    fetchPayments()
  } catch (err) {
    deleteError.value = "O'chirishda xatolik yuz berdi"
  } finally {
    deleting.value = false
  }
}

onMounted(() => { fetchPayments() })
</script>

<style scoped>
.page-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-main-title { font-size: 22px; font-weight: 700; color: #111827; }
.page-sub-title { font-size: 13px; color: #6B7280; margin-top: 2px; }
.btn-primary-action { display: inline-flex; align-items: center; gap: 8px; padding: 11px 20px; background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); color: white; border-radius: 12px; font-weight: 700; font-size: 13.5px; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25); cursor: pointer; transition: all 0.2s ease; }
.btn-primary-action:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35); }
.metrics-cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; }
.card-metric { background: white; border: 1.5px solid #E5E7EB; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); }
.card-metric-icon { font-size: 30px; }
.metric-lbl { font-size: 12.5px; color: #6B7280; font-weight: 600; }
.metric-val { font-size: 18px; font-weight: 800; color: #111827; margin-top: 4px; }
.text-blue { color: #2563EB; font-weight: 800; }
.text-purple { color: #9333EA; font-weight: 800; }
.margin-top { margin-top: 24px; }
.table-section-card { background: white; border: 1px solid #E5E7EB; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.toolbar-bar { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid #E5E7EB; gap: 16px; flex-wrap: wrap; }
.search-box { display: flex; align-items: center; gap: 10px; background: #F9FAFB; border: 1.5px solid #E5E7EB; border-radius: 10px; padding: 9px 14px; width: 300px; }
.search-input { border: none; background: transparent; outline: none; font-size: 13.5px; width: 100%; }
.filter-controls { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.filter-item { display: flex; align-items: center; gap: 6px; }
.flabel { font-size: 12.5px; font-weight: 600; color: #4B5563; }
.finput-date { padding: 8px 12px; border: 1.5px solid #E5E7EB; border-radius: 10px; font-size: 13px; background: #FAFAFA; outline: none; }
.total-count { font-size: 13px; color: #6B7280; white-space: nowrap; }
.table-container { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; th { background: #F9FAFB; padding: 13px 16px; font-size: 12px; font-weight: 700; color: #4B5563; text-align: left; border-bottom: 1px solid #E5E7EB; } td { padding: 14px 16px; font-size: 13.5px; color: #1F2937; border-bottom: 1px solid #F3F4F6; vertical-align: middle; } }
.student-name { font-weight: 700; color: #111827; }
.link-value { cursor: pointer; }
.link-value:hover { text-decoration: underline; }
.group-sub { font-size: 11.5px; color: #6B7280; margin-top: 2px; }
.method-chip { padding: 4px 12px; background: #F3F4F6; color: #374151; border-radius: 20px; font-size: 12px; font-weight: 600; }
.row-actions { display: flex; gap: 8px; justify-content: flex-end; }
.btn-action-edit, .btn-action-delete { width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; border: 1px solid #E5E7EB; background: #F9FAFB; cursor: pointer; transition: all 0.15s ease; }
.btn-action-edit { color: #2563EB; &:hover { background: #EFF6FF; border-color: #BFDBFE; transform: translateY(-1px); } }
.btn-action-delete { color: #EF4444; &:hover { background: #FEE2E2; border-color: #FCA5A5; transform: translateY(-1px); } }

.state-box, .empty-state { text-align: center; padding: 40px 0; color: #6B7280; }
.spinner { width: 28px; height: 28px; border: 3px solid #E5E7EB; border-top-color: #2563EB; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px; }
@keyframes spin { to { transform: rotate(360deg); } }

.modal-overlay { position: fixed; inset: 0; z-index: 1000; background: rgba(15, 23, 42, 0.65); backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-card { background: white; border-radius: 20px; width: 100%; max-width: 500px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); }
.modal-header-banner.blue-banner { padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #F3F4F6; background: linear-gradient(180deg, #EFF6FF 0%, #FFFFFF 100%); }
.header-left-info { display: flex; align-items: center; gap: 12px; h3 { font-size: 17px; font-weight: 700; color: #1D4ED8; } p { font-size: 12px; color: #6B7280; margin-top: 2px; } }
.header-icon-box.blue-box { width: 42px; height: 42px; border-radius: 12px; background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); color: white; display: flex; align-items: center; justify-content: center; }
.btn-modal-close { background: none; border: none; font-size: 18px; color: #9CA3AF; cursor: pointer; }
.modal-body { padding: 24px; }

/* UNIFORM FORM FIELD STYLING */
.form-group { margin-bottom: 18px; width: 100%; }
.finput, .fselect-field {
  width: 100%; box-sizing: border-box; padding: 11px 14px;
  border: 1.5px solid #E5E7EB; border-radius: 10px; font-size: 14px;
  background-color: #FAFAFA; color: #111827; outline: none;
  transition: all 0.2s ease; appearance: none; -webkit-appearance: none;
  &:focus { border-color: #2563EB; background-color: #FFFFFF; box-shadow: 0 0 0 3.5px rgba(37, 99, 235, 0.12); }
}

.select-wrap-relative { position: relative; width: 100%; }
.select-chevron-icon { position: absolute; right: 14px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #9CA3AF; font-size: 10px; }

.amount-input.blue-text { font-size: 16.5px; font-weight: 800; color: #2563EB; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.btn-cancel { padding: 10px 18px; border: 1px solid #D1D5DB; background: white; border-radius: 10px; font-weight: 600; font-size: 13px; color: #374151; cursor: pointer; }
.btn-blue-save { padding: 10px 22px; background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); color: white; border-radius: 10px; font-weight: 700; font-size: 13.5px; cursor: pointer; }
.alert-error { background: #FEE2E2; color: #991B1B; padding: 10px 14px; border-radius: 10px; font-size: 13px; margin-bottom: 16px; }
</style>
