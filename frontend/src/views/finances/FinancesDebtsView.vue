<template>
  <AppLayout>

    <!-- Page Header -->
    <div class="page-top">
      <div>
        <h2 class="page-main-title">Qarzdorlar Ro'yxati (Debts)</h2>
        <p class="page-sub-title">Shartnoma to'lovi to'liq to'lanmagan barcha qarzdor o'quvchilar ro'yxati</p>
      </div>

      <button class="btn-primary-action" @click="openGeneralPayModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="18" height="18">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        <span>Qarzdorlik to'lovini kiritish</span>
      </button>
    </div>

    <!-- Metrics Cards -->
    <div class="metrics-cards-grid">
      <div class="card-metric card-red">
        <div class="card-metric-icon">⚠️</div>
        <div>
          <span class="metric-lbl">Qarzdor O'quvchilar Soni</span>
          <h4 class="metric-val text-red">{{ debtEnrollments.length }} ta o'quvchi</h4>
        </div>
      </div>

      <div class="card-metric card-orange font-hero">
        <div class="card-metric-icon">💸</div>
        <div>
          <span class="metric-lbl">Jami Qarzdorlik Summasi</span>
          <h4 class="metric-val text-orange">{{ formatMoney(totalDebtSum) }}</h4>
        </div>
      </div>
    </div>

    <!-- Table Section with Filters -->
    <div class="table-section-card margin-top">
      <div class="toolbar-bar">
        <div class="search-box">
          <svg viewBox="0 0 20 20" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
            <circle cx="8.5" cy="8.5" r="5.5"/>
            <line x1="13" y1="13" x2="18" y2="18"/>
          </svg>
          <input
            v-model="filterSearchQuery"
            type="text"
            placeholder="O'quvchi F.I.SH., JSHSHR yoki telefon..."
            class="search-input"
          />
        </div>

        <div class="filter-controls">
          <div class="filter-item">
            <label class="flabel">Kategoriya:</label>
            <div class="select-wrap-relative">
              <select v-model="filterCategory" class="fselect-field">
                <option value="">Barcha kategoriyalar</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
              <div class="select-chevron-icon">▼</div>
            </div>
          </div>

          <div class="filter-item">
            <label class="flabel">Guruh:</label>
            <div class="select-wrap-relative">
              <select v-model="filterGroup" class="fselect-field">
                <option value="">Barcha guruhlar</option>
                <option v-for="g in groupOptions" :key="g" :value="g">
                  {{ g }}
                </option>
              </select>
              <div class="select-chevron-icon">▼</div>
            </div>
          </div>

          <div class="filter-item">
            <label class="flabel">Sertifikat:</label>
            <div class="select-wrap-relative">
              <select v-model="filterCertificate" class="fselect-field">
                <option value="">Barchasi</option>
                <option value="bor">Bor</option>
                <option value="yoq">Yo'q</option>
              </select>
              <div class="select-chevron-icon">▼</div>
            </div>
          </div>
        </div>

        <div class="total-count">
          Jami: <strong>{{ filteredDebtEnrollments.length }}</strong> ta qarzdor
        </div>
      </div>

      <div class="table-container">
        <div v-if="loading" class="state-box">
          <div class="spinner"></div>
          <span>Qarzdorlar ro'yxati yuklanmoqda...</span>
        </div>

        <div v-else-if="filteredDebtEnrollments.length === 0" class="empty-state">
          <p>Qarzdor o'quvchilar topilmadi</p>
        </div>

        <table v-else class="data-table">
          <thead>
            <tr>
              <th>O'quvchi F.I.SH.</th>
              <th>Kategoriya / Guruh</th>
              <th class="th-cert">Sertifikat</th>
              <th class="th-amount">Shartnoma Summasi</th>
              <th class="th-amount">To'langan Summa</th>
              <th class="th-amount">Qarzdorlik Summasi</th>
              <th>Holati</th>
              <th style="text-align: right;">Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="e in filteredDebtEnrollments" :key="e.id" class="table-row">
              <td class="td-name">
                <div class="student-name-link" @click="goStudent(e.student)">{{ e.student_name || 'Noma\'lum' }}</div>
                <div class="student-sub">
                  <div v-if="e.student_phone">📞 {{ formatPhone(e.student_phone) }}</div>
                  <div v-if="e.student_phone2">📞 {{ formatPhone(e.student_phone2) }} (qo'shimcha)</div>
                  <div v-if="e.student_jshshr">JSHSHR: {{ e.student_jshshr }}</div>
                </div>
              </td>
              <td>
                <span class="cat-pill">{{ e.category_name || '-' }}</span>
                <div v-if="e.group_name" class="group-sub">{{ e.group_name }}</div>
                <div v-if="groupsById[e.group]" class="group-dates">
                  {{ formatDate(groupsById[e.group].started_at) }} — {{ formatDate(groupsById[e.group].ends_at) }}
                </div>
              </td>
              <td class="td-cert">
                <span v-if="e.student_certificate_number">{{ certLabel(e) }}</span>
                <span v-else>-</span>
              </td>
              <td class="td-amount">{{ formatMoney(e.enrolled_amount) }}</td>
              <td class="td-amount text-green">{{ formatMoney(e.paid_amount || 0) }}</td>
              <td class="td-amount">
                <span class="debt-chip font-bold">-{{ formatMoney(getDebt(e)) }}</span>
              </td>
              <td>
                <span class="status-chip" :class="e.status">{{ statusText(e.status) }}</span>
              </td>
              <td style="text-align: right;">
                <button class="btn-pay-action" @click="openPayModal(e)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="13" height="13">
                    <rect x="2" y="5" width="20" height="14" rx="2"></rect>
                    <line x1="2" y1="10" x2="22" y2="10"></line>
                  </svg>
                  <span>To'lov qilish ({{ formatMoney(getDebt(e)) }})</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- PAYMENT MODAL FOR DEBT -->
    <Transition name="modal">
      <div v-if="showPayModal" class="modal-overlay" @click.self="closePayModal">
        <div class="modal-card">
          <div class="modal-header-banner green-banner">
            <div class="header-left-info">
              <div class="header-icon-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <rect x="2" y="5" width="20" height="14" rx="2"></rect>
                  <line x1="2" y1="10" x2="22" y2="10"></line>
                </svg>
              </div>
              <div>
                <h3>To'lov Qabul Qilish</h3>
                <p>Qarzdorlik to'lovini tizimga kiriting</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closePayModal">✕</button>
          </div>

          <form @submit.prevent="savePayment" class="modal-body">
            <div v-if="modalError" class="alert-error">{{ modalError }}</div>

            <!-- Searchable Student Selector (For General Payment Button) -->
            <div class="form-group" v-if="isGeneralModal">
              <label class="flabel required">Qarzdor O'quvchini Ism bo'yicha Qidirish *</label>
              <div class="searchable-select-wrap">
                <input
                  v-model="studentSearchQuery"
                  type="text"
                  class="finput search-input-field"
                  placeholder="Ism bo'yicha qidiring..."
                  @focus="showStudentDropdown = true"
                  @keydown="onStudentKeydown"
                />
                <div v-if="showStudentDropdown" class="dropdown-options-list">
                  <div
                    v-for="(e, idx) in filteredModalDebtEnrollments"
                    :key="e.id"
                    class="dropdown-option-item"
                    :class="{ selected: selectedEnrollmentId === e.id, highlighted: studentKb.highlightedIndex.value === idx }"
                    @click="selectDebtEnrollment(e)"
                  >
                    <div class="opt-name">{{ e.student_name }}</div>
                    <div class="opt-sub">
                      {{ e.category_name }} | Qarzdorlik: <strong class="text-red">-{{ formatMoney(getDebt(e)) }}</strong>
                    </div>
                  </div>
                  <div v-if="filteredModalDebtEnrollments.length === 0" class="dropdown-empty">
                    Qarzdor o'quvchi topilmadi
                  </div>
                </div>
              </div>
              <div v-if="selectedStudentLabel" class="selected-chip">
                Tanlandi: <strong>{{ selectedStudentLabel }}</strong>
              </div>
            </div>

            <!-- Student Info Display (When Pre-selected from row) -->
            <div v-else class="info-card-box">
              <div class="info-line">
                <span>O'quvchi:</span> <strong>{{ activeEnrollment?.student_name }}</strong>
              </div>
              <div class="info-line">
                <span>Kategoriya:</span> <strong>{{ activeEnrollment?.category_name }}</strong>
              </div>
              <div class="info-line">
                <span>Qarzdorlik Summasi:</span> <strong class="text-red">-{{ formatMoney(getDebt(activeEnrollment)) }}</strong>
              </div>
            </div>

            <!-- Amount Input -->
            <div class="form-group">
              <label class="flabel required">To'lanayotgan Summa * <span class="hint-text">(Tahrirlanadigan summa)</span></label>
              <input
                v-model="payForm.amountFormatted"
                type="text"
                class="finput amount-input"
                placeholder="0"
                required
                @input="onAmountInput"
              />
            </div>

            <!-- Method Select -->
            <div class="form-group">
              <label class="flabel required">To'lov Usuli *</label>
              <div class="select-wrap-relative">
                <select v-model="payForm.method" class="fselect-field">
                  <option value="cash">Naqd</option>
                  <option value="card">Karta</option>
                  <option value="qr_code">QR code</option>
                  <option value="transfer">O'tkazma</option>
                </select>
                <div class="select-chevron-icon">▼</div>
              </div>
            </div>

            <!-- Notes -->
            <div class="form-group">
              <label class="flabel">Izoh / Eslatma</label>
              <input v-model="payForm.notes" type="text" class="finput" placeholder="Qarzdorlik to'lovi bo'yicha izoh..." />
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-cancel" @click="closePayModal">Bekor qilish</button>
              <button type="submit" class="btn-save" :disabled="saving">
                {{ saving ? "Saqlanmoqda..." : "To'lovni Saqlash" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useBranchStore } from '@/stores/branch'
import { formatMoney, formatPhone, formatDate } from '@/utils/formatters'
import { useSearchSelectKeyboard } from '@/composables/useSearchSelectKeyboard'

const router = useRouter()
const authStore = useAuthStore()
const branchStore = useBranchStore()

const enrollments = ref([])
const categories = ref([])
const groups = ref([])
const loading = ref(true)

const groupsById = computed(() => {
  const map = {}
  groups.value.forEach(g => { map[g.id] = g })
  return map
})

const filterSearchQuery = ref('')
const filterCategory = ref('')
const filterGroup = ref('')
const filterCertificate = ref('')

const showPayModal = ref(false)
const isGeneralModal = ref(false)
const activeEnrollment = ref(null)
const selectedEnrollmentId = ref(null)
const saving = ref(false)
const modalError = ref(null)

const studentSearchQuery = ref('')
const showStudentDropdown = ref(false)
const selectedStudentLabel = ref('')

const payForm = ref({ amountFormatted: '', amount: 0, method: 'cash', notes: '' })

const getDebt = (e) => {
  if (!e || e.enrolled_free) return 0
  const contract = Number(e.enrolled_amount) || 0
  const paid = Number(e.paid_amount) || 0
  return Math.max(0, contract - paid)
}

const debtEnrollments = computed(() => {
  return enrollments.value.filter(e => getDebt(e) > 0 && branchStore.isBranchMatch(e))
})

const totalDebtSum = computed(() => {
  return debtEnrollments.value.reduce((sum, e) => sum + getDebt(e), 0)
})

const filteredModalDebtEnrollments = computed(() => {
  const q = studentSearchQuery.value.toLowerCase().trim()
  if (!q) return debtEnrollments.value
  return debtEnrollments.value.filter(e => (e.student_name || '').toLowerCase().includes(q))
})

const groupOptions = computed(() => {
  const names = debtEnrollments.value.map(e => e.group_name).filter(Boolean)
  return [...new Set(names)].sort()
})

const certLabel = (e) => `${e.student_certificate_series || ''} ${e.student_certificate_number}`.trim()

const filteredDebtEnrollments = computed(() => {
  return debtEnrollments.value.filter(e => {
    const q = filterSearchQuery.value.toLowerCase().trim()
    const matchSearch = !q ||
      (e.student_name || '').toLowerCase().includes(q) ||
      (e.student_jshshr || '').toLowerCase().includes(q) ||
      (e.student_phone || '').toLowerCase().includes(q) ||
      (e.group_name || '').toLowerCase().includes(q) ||
      (e.category_name || '').toLowerCase().includes(q)

    const catVal = filterCategory.value
    const catObj = categories.value.find(c => String(c.id) === String(catVal))
    const catName = catObj ? catObj.name.toLowerCase() : ''

    const matchCategory = !catVal ||
      String(e.category) === String(catVal) ||
      (e.category_name && e.category_name.toLowerCase() === catVal.toString().toLowerCase()) ||
      (catName && e.category_name && e.category_name.toLowerCase() === catName)

    const matchGroup = !filterGroup.value || e.group_name === filterGroup.value

    const hasCert = !!e.student_certificate_number
    const matchCertificate = !filterCertificate.value ||
      (filterCertificate.value === 'bor' && hasCert) ||
      (filterCertificate.value === 'yoq' && !hasCert)

    return matchSearch && matchCategory && matchGroup && matchCertificate
  })
})

async function fetchEnrollments() {
  loading.value = true
  try {
    const res = await api.get('/enrollments/', { params: { page_size: 1000 } })
    enrollments.value = res.data.results || res.data
  } catch (err) { console.error(err) }
  finally { loading.value = false }
}

async function fetchCategories() {
  try {
    const res = await api.get('/categories/')
    categories.value = res.data.results || res.data
  } catch (err) { console.error(err) }
}

async function fetchGroups() {
  try {
    const res = await api.get('/groups/', { params: { page_size: 1000 } })
    groups.value = res.data.results || res.data
  } catch (err) { console.error(err) }
}

function statusText(st) {
  switch (st) {
    case 'new': return 'Yangi'
    case 'enrolled': return 'Faol'
    case 'finished': return 'Tugatgan'
    case 'canceled': return 'Bekor qilingan'
    default: return st
  }
}

function goStudent(studentId) {
  if (studentId) router.push(`/students/${studentId}`)
}

function openGeneralPayModal() {
  isGeneralModal.value = true
  activeEnrollment.value = null
  selectedEnrollmentId.value = null
  studentSearchQuery.value = ''
  selectedStudentLabel.value = ''
  showStudentDropdown.value = false
  modalError.value = null
  payForm.value = { amountFormatted: '', amount: 0, method: 'cash', notes: 'Qarzdorlik to\'lovi' }
  showPayModal.value = true
}

function openPayModal(e) {
  isGeneralModal.value = false
  activeEnrollment.value = e
  selectedEnrollmentId.value = e.id
  const debtAmt = getDebt(e)
  modalError.value = null
  payForm.value = {
    amountFormatted: formatMoney(debtAmt, false),
    amount: debtAmt,
    method: 'cash',
    notes: 'Qarzdorlik to\'lovi'
  }
  showPayModal.value = true
}

function selectDebtEnrollment(e) {
  selectedEnrollmentId.value = e.id
  activeEnrollment.value = e
  selectedStudentLabel.value = `${e.student_name} (${e.category_name})`
  studentSearchQuery.value = e.student_name
  showStudentDropdown.value = false
  const debtAmt = getDebt(e)
  payForm.value.amount = debtAmt
  payForm.value.amountFormatted = formatMoney(debtAmt, false)
}
const studentKb = useSearchSelectKeyboard()
function onStudentKeydown(e) {
  studentKb.onKeydown(e, filteredModalDebtEnrollments.value, selectDebtEnrollment, () => { showStudentDropdown.value = false })
}

function closePayModal() {
  showPayModal.value = false
}

function onAmountInput(e) {
  const digits = e.target.value.replace(/\D/g, '')
  if (!digits) { payForm.value.amount = 0; payForm.value.amountFormatted = ''; return }
  const num = parseInt(digits, 10)
  payForm.value.amount = num
  payForm.value.amountFormatted = formatMoney(num, false)
}

async function savePayment() {
  const enrollmentId = isGeneralModal.value ? selectedEnrollmentId.value : activeEnrollment.value?.id
  if (!enrollmentId) {
    modalError.value = "O'quvchini tanlang."
    return
  }
  if (!payForm.value.amount || payForm.value.amount <= 0) {
    modalError.value = "To'g'ri to'lov summasini kiriting."
    return
  }

  saving.value = true
  modalError.value = null
  try {
    await api.post('/payments/', {
      user: authStore.user?.id,
      enrollment: enrollmentId,
      amount: payForm.value.amount,
      status: 'accepted',
      method: payForm.value.method,
      notes: payForm.value.notes
    })
    closePayModal()
    fetchEnrollments()
  } catch (err) {
    modalError.value = err.response?.data?.detail || "Saqlashda xatolik yuz berdi"
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchEnrollments()
  fetchCategories()
  fetchGroups()
})
</script>

<style scoped>
.page-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-main-title { font-size: 22px; font-weight: 700; color: #111827; }
.page-sub-title { font-size: 13px; color: #6B7280; margin-top: 2px; }

.btn-primary-action {
  display: inline-flex; align-items: center; gap: 8px; padding: 11px 20px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%); color: white;
  border-radius: 12px; font-weight: 700; font-size: 13.5px;
  box-shadow: 0 4px 14px rgba(45, 106, 79, 0.25); cursor: pointer; transition: all 0.2s ease;
  &:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(45, 106, 79, 0.35); }
}

.metrics-cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; }
.card-metric { background: white; border: 1.5px solid #E5E7EB; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); }
.card-metric-icon { font-size: 30px; }
.metric-lbl { font-size: 12.5px; color: #6B7280; font-weight: 600; }
.metric-val { font-size: 18px; font-weight: 800; color: #111827; margin-top: 4px; }
.text-red { color: #DC2626; font-weight: 800; }
.text-orange { color: #EA580C; font-weight: 800; }
.text-green { color: #166534; font-weight: 700; }
.margin-top { margin-top: 24px; }

.table-section-card { background: white; border: 1px solid #E5E7EB; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.toolbar-bar { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid #E5E7EB; gap: 16px; flex-wrap: wrap; }
.search-box { display: flex; align-items: center; gap: 10px; background: #F9FAFB; border: 1.5px solid #E5E7EB; border-radius: 10px; padding: 9px 14px; width: 300px; &:focus-within { border-color: #2D6A4F; background: white; box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.12); } }
.search-input { border: none; background: transparent; outline: none; font-size: 13.5px; width: 100%; }

.filter-controls { display: flex; align-items: center; gap: 12px; }
.filter-item { display: flex; align-items: center; gap: 6px; }

.total-count { font-size: 13px; color: #6B7280; }
.table-container { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; th { background: #F9FAFB; padding: 13px 16px; font-size: 12px; font-weight: 700; color: #4B5563; text-align: left; border-bottom: 1px solid #E5E7EB; } td { padding: 14px 16px; font-size: 13.5px; color: #1F2937; border-bottom: 1px solid #F3F4F6; vertical-align: middle; } }

.student-name-link { font-weight: 700; color: #111827; cursor: pointer; &:hover { color: #2D6A4F; text-decoration: underline; } }
.student-sub { font-size: 11.5px; color: #6B7280; margin-top: 2px; }
.cat-pill { padding: 4px 10px; background: #E8F5E9; color: #2D6A4F; border-radius: 8px; font-size: 12px; font-weight: 700; }
.group-sub { font-size: 11.5px; color: #6B7280; margin-top: 2px; }
.group-dates { font-size: 13px; font-weight: 600; color: #374151; margin-top: 4px; white-space: nowrap; }
.debt-chip { padding: 4px 10px; background: #FEE2E2; color: #991B1B; border-radius: 8px; font-size: 12.5px; display: inline-block; }
.th-cert, .td-cert, .th-amount, .td-amount { white-space: nowrap; }

.status-chip {
  display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11.5px; font-weight: 600;
  &.enrolled { background: #DCFCE7; color: #15803D; }
  &.new { background: #E0F2FE; color: #0369A1; }
  &.finished { background: #F3F4F6; color: #4B5563; }
}

/* PAY ACTION BUTTON WITH DEBT AMOUNT (COMPACT) */
.btn-pay-action {
  display: inline-flex; align-items: center; gap: 5px; padding: 6px 12px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%); color: white;
  border-radius: 8px; font-weight: 700; font-size: 11.5px; cursor: pointer; transition: all 0.15s ease;
  box-shadow: 0 2px 6px rgba(45, 106, 79, 0.18);
  &:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(45, 106, 79, 0.3); }
}

.hint-text { font-size: 11px; font-weight: 500; color: #6B7280; margin-left: 4px; }

.state-box, .empty-state { text-align: center; padding: 40px 0; color: #6B7280; }
.spinner { width: 28px; height: 28px; border: 3px solid #E5E7EB; border-top-color: #2D6A4F; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px; }
@keyframes spin { to { transform: rotate(360deg); } }

.modal-overlay { position: fixed; inset: 0; z-index: 1000; background: rgba(15, 23, 42, 0.65); backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-card { background: white; border-radius: 20px; width: 100%; max-width: 500px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); }
.modal-header-banner.green-banner { padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #F3F4F6; background: linear-gradient(180deg, #F0FDF4 0%, #FFFFFF 100%); }
.header-left-info { display: flex; align-items: center; gap: 12px; h3 { font-size: 17px; font-weight: 700; color: #111827; } p { font-size: 12px; color: #6B7280; margin-top: 2px; } }
.header-icon-box { width: 42px; height: 42px; border-radius: 12px; background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%); color: white; display: flex; align-items: center; justify-content: center; }
.btn-modal-close { background: none; border: none; font-size: 18px; color: #9CA3AF; cursor: pointer; }
.modal-body { padding: 24px; }

.info-card-box { background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 12px; padding: 14px; margin-bottom: 18px; }
.info-line { font-size: 13px; color: #4B5563; margin-bottom: 6px; &:last-child { margin-bottom: 0; } }

/* UNIFORM INPUT & SELECT FIELD STYLING */
.form-group { margin-bottom: 18px; width: 100%; }
.flabel { display: block; font-size: 12.5px; font-weight: 600; color: #374151; margin-bottom: 6px; }
.finput, .fselect-field {
  width: 100%; box-sizing: border-box; padding: 11px 14px;
  border: 1.5px solid #E5E7EB; border-radius: 10px; font-size: 14px;
  background-color: #FAFAFA; color: #111827; outline: none;
  transition: all 0.2s ease; appearance: none; -webkit-appearance: none;
  &:focus { border-color: #2D6A4F; background-color: #FFFFFF; box-shadow: 0 0 0 3.5px rgba(45, 106, 79, 0.12); }
}

.select-wrap-relative { position: relative; width: 100%; }
.select-chevron-icon { position: absolute; right: 14px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #9CA3AF; font-size: 10px; }

.searchable-select-wrap { position: relative; width: 100%; }
.dropdown-options-list { position: absolute; top: 100%; left: 0; right: 0; max-height: 200px; overflow-y: auto; background: white; border: 1.5px solid #2D6A4F; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); z-index: 50; margin-top: 4px; }
.dropdown-option-item { padding: 10px 14px; cursor: pointer; border-bottom: 1px solid #F3F4F6; &:hover { background: #F0FDF4; } &.selected { background: #E8F5E9; font-weight: 700; } &.highlighted { background: #F0FDF4; } }
.opt-name { font-size: 13.5px; font-weight: 600; color: #111827; }
.opt-sub { font-size: 11.5px; color: #6B7280; margin-top: 1px; }
.dropdown-empty { padding: 12px; text-align: center; color: #9CA3AF; font-size: 13px; }
.selected-chip { font-size: 12.5px; color: #2D6A4F; margin-top: 6px; }

.amount-input { font-size: 16.5px; font-weight: 800; color: #2D6A4F; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.btn-cancel { padding: 10px 18px; border: 1px solid #D1D5DB; background: white; border-radius: 10px; font-weight: 600; font-size: 13px; color: #374151; cursor: pointer; }
.btn-save { padding: 10px 22px; background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%); color: white; border-radius: 10px; font-weight: 700; font-size: 13.5px; cursor: pointer; }
.alert-error { background: #FEE2E2; color: #991B1B; padding: 10px 14px; border-radius: 10px; font-size: 13px; margin-bottom: 16px; }
</style>
