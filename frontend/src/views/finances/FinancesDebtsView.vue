<template>
  <AppLayout>

    <!-- Page Header -->
    <div class="page-top">
      <div>
        <h2 class="page-main-title">Qarzdorlar Ro'yxati</h2>
        <p class="page-sub-title">Shartnoma to'lovi to'liq to'lanmagan barcha qarzdor o'quvchilar ro'yxati</p>
      </div>
    </div>

    <!-- Metrics Cards -->
    <div class="metrics-cards-grid">
      <div class="card-metric card-red">
        <div class="card-metric-icon">⚠️</div>
        <div>
          <span class="metric-lbl">Qarzdor O'quvchilar Soni</span>
          <h4 class="metric-val text-red">{{ filteredDebtEnrollments.length }} ta o'quvchi</h4>
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
      <div class="table-container">
        <div v-if="loading" class="state-box">
          <div class="spinner"></div>
          <span>Qarzdorlar ro'yxati yuklanmoqda...</span>
        </div>

        <div v-else class="table-scroll-area">
        <table class="data-table">
          <thead>
            <tr>
              <th>O'quvchi F.I.SH.</th>
              <th>Kategoriya</th>
              <th>Agent</th>
              <th>Guruh nomi</th>
              <th>Guruh boshlanishi</th>
              <th>Guruh tugashi</th>
              <th class="th-cert">Sertifikat</th>
              <th class="th-amount">Shartnoma Summasi</th>
              <th class="th-amount">O'quvchi to'lagan summa</th>
              <th class="th-amount">Qarzdorlik Summasi</th>
              <th>Holati</th>
              <th>Izoh</th>
              <th style="width: 110px; text-align: right;">Amallar</th>
            </tr>
            <tr class="col-filter-row">
              <th>
                <input v-model="filterStudentName" class="col-filter-input" type="text" placeholder="Ism bo'yicha qidirish..." />
              </th>
              <th>
                <div class="select-wrap-relative">
                  <select v-model="filterCategory" class="col-filter-select">
                    <option value="">Barchasi</option>
                    <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                  </select>
                </div>
              </th>
              <th>
                <div class="select-wrap-relative">
                  <select v-model="filterAgent" class="col-filter-select">
                    <option value="">Barchasi</option>
                    <option v-for="a in agentOptions" :key="a.id" :value="a.id">{{ a.name }}</option>
                  </select>
                </div>
              </th>
              <th>
                <input v-model="filterGroup" class="col-filter-input" type="text" placeholder="Guruh nomi..." />
              </th>
              <th>
                <div class="col-sort-group">
                  <button type="button" class="col-sort-icon-btn" :class="{ active: groupStartSort === 'asc' }" title="O'sish tartibida (eskidan yangiga)" @click="setSort('groupStart', 'asc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 20V4"></path>
                      <path d="M3 8l3-4 3 4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button type="button" class="col-sort-icon-btn" :class="{ active: groupStartSort === 'desc' }" title="Kamayish tartibida (yangidan eskiga)" @click="setSort('groupStart', 'desc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 4v16"></path>
                      <path d="M3 16l3 4 3-4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button v-if="startDateFrom || startDateTo" type="button" class="btn-clear-date" @click="startDateFrom = ''; startDateTo = ''" title="Tozalash">✕</button>
                </div>
                <div class="col-date-range">
                  <input v-model="startDateFrom" type="date" class="col-date-input" title="Guruh boshlanishi (dan)" />
                  <input v-model="startDateTo" type="date" class="col-date-input" title="Guruh boshlanishi (gacha)" />
                </div>
              </th>
              <th>
                <div class="col-sort-group">
                  <button type="button" class="col-sort-icon-btn" :class="{ active: groupEndSort === 'asc' }" title="O'sish tartibida (eskidan yangiga)" @click="setSort('groupEnd', 'asc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 20V4"></path>
                      <path d="M3 8l3-4 3 4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button type="button" class="col-sort-icon-btn" :class="{ active: groupEndSort === 'desc' }" title="Kamayish tartibida (yangidan eskiga)" @click="setSort('groupEnd', 'desc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 4v16"></path>
                      <path d="M3 16l3 4 3-4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button v-if="endDateFrom || endDateTo" type="button" class="btn-clear-date" @click="endDateFrom = ''; endDateTo = ''" title="Tozalash">✕</button>
                </div>
                <div class="col-date-range">
                  <input v-model="endDateFrom" type="date" class="col-date-input" title="Guruh tugashi (dan)" />
                  <input v-model="endDateTo" type="date" class="col-date-input" title="Guruh tugashi (gacha)" />
                </div>
              </th>
              <th>
                <div class="select-wrap-relative">
                  <select v-model="filterCertificate" class="col-filter-select">
                    <option value="">Barchasi</option>
                    <option value="bor">Bor</option>
                    <option value="yoq">Yo'q</option>
                  </select>
                </div>
              </th>
              <th>
                <div class="select-wrap-relative">
                  <select v-model="filterEnrolledAmount" class="col-filter-select">
                    <option value="">Barchasi</option>
                    <option v-for="amt in distinctEnrolledAmounts" :key="amt" :value="amt">{{ formatMoney(amt) }}</option>
                  </select>
                </div>
              </th>
              <th>
                <div class="col-sort-group">
                  <button type="button" class="col-sort-icon-btn" :class="{ active: paidAmountSort === 'asc' }" title="O'sish tartibida" @click="setSort('paidAmount', 'asc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 20V4"></path>
                      <path d="M3 8l3-4 3 4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button type="button" class="col-sort-icon-btn" :class="{ active: paidAmountSort === 'desc' }" title="Kamayish tartibida" @click="setSort('paidAmount', 'desc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 4v16"></path>
                      <path d="M3 16l3 4 3-4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                </div>
              </th>
              <th>
                <div class="col-sort-group">
                  <button type="button" class="col-sort-icon-btn" :class="{ active: debtAmountSort === 'asc' }" title="O'sish tartibida" @click="setSort('debtAmount', 'asc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 20V4"></path>
                      <path d="M3 8l3-4 3 4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button type="button" class="col-sort-icon-btn" :class="{ active: debtAmountSort === 'desc' }" title="Kamayish tartibida" @click="setSort('debtAmount', 'desc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 4v16"></path>
                      <path d="M3 16l3 4 3-4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                </div>
              </th>
              <th>
                <div class="select-wrap-relative">
                  <select v-model="filterStatus" class="col-filter-select">
                    <option value="">Barchasi</option>
                    <option value="new">Yangi</option>
                    <option value="enrolled">Faol</option>
                    <option value="finished">Tugatgan</option>
                    <option value="canceled">Bekor qilingan</option>
                  </select>
                </div>
              </th>
              <th></th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="displayedDebtEnrollments.length === 0">
              <td colspan="13" class="no-data">Qarzdor o'quvchilar topilmadi</td>
            </tr>
            <tr v-for="e in displayedDebtEnrollments" :key="e.id" class="table-row">
              <td class="td-name">
                <div class="student-name-link" @click="goStudent(e.student)">{{ e.student_name || 'Noma\'lum' }}</div>
              </td>
              <td><span class="cat-pill">{{ e.category_name || '-' }}</span></td>
              <td>
                <span v-if="e.agent" class="link-value" @click="goAgent(e.agent)">{{ e.agent_name || '-' }}</span>
                <span v-else>-</span>
              </td>
              <td>
                <span v-if="e.group" class="link-value" @click="goGroup(e.group)">{{ e.group_name || '-' }}</span>
                <span v-else>{{ e.group_name || '-' }}</span>
              </td>
              <td>{{ groupsById[e.group] ? formatDate(groupsById[e.group].started_at) : '-' }}</td>
              <td>{{ groupsById[e.group] ? formatDate(groupsById[e.group].ends_at) : '-' }}</td>
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
              <td>{{ e.notes || '-' }}</td>
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

      <!-- Pagination controls -->
      <div class="pagination-bar">
        <span class="pagination-info">
          Jami: <strong>{{ sortedDebtEnrollments.length }}</strong> tadan <strong>{{ displayedDebtEnrollments.length }}</strong> ko'rsatilmoqda
        </span>
        <div class="pagination-actions">
          <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">Oldingi</button>
          <span v-if="pageSizeOption !== 'all'" class="page-num">Sahifa {{ Math.min(currentPage, displayTotalPages) }} / {{ displayTotalPages }}</span>
          <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === displayTotalPages" @click="changePage(currentPage + 1)">Keyingi</button>
          <label class="page-size-label" for="debts-page-size">Ko'rsatish:</label>
          <div class="select-wrap-relative">
            <select id="debts-page-size" v-model="pageSizeOption" class="page-size-select">
              <option value="50">50</option>
              <option value="100">100</option>
              <option value="200">200</option>
              <option value="all">Barchasi</option>
            </select>
          </div>
        </div>
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

            <!-- Student Info Display (pre-selected from the row's "To'lov qilish" button) -->
            <div class="info-card-box">
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
                  <option value="click">Click</option>
                  <option value="transfer">O'tkazma</option>
                </select>
                <div class="select-chevron-icon">▼</div>
              </div>
            </div>

            <!-- Click check photo -->
            <div class="form-group" v-if="payForm.method === 'click'">
              <label class="flabel">Click cheki rasmi (ixtiyoriy)</label>
              <FileSelectInput ref="checkFileInputRef" accept="image/jpeg,image/png" @change="onCheckFileChange" />
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
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import FileSelectInput from '@/components/FileSelectInput.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useBranchStore } from '@/stores/branch'
import { formatMoney, formatDate } from '@/utils/formatters'

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

const filterStudentName = ref('')
const filterCategory = ref('')
const filterAgent = ref('')
const filterGroup = ref('')
const filterCertificate = ref('')
const filterStatus = ref('')

const filterEnrolledAmount = ref('')
const startDateFrom = ref('')
const startDateTo = ref('')
const endDateFrom = ref('')
const endDateTo = ref('')

// ── Row-fetch-count selector ──────────────────────────────────
// Controls how many of the *filtered* debtors show per page (see
// displayedDebtEnrollments below). The fetch itself always pulls every
// enrollment — debt totals/metrics and filtering all need to see every
// debtor, not just whatever page happened to be fetched. Defaults to
// "Barchasi", preserving the previous behavior of always showing every
// debtor at once.
const pageSizeOption = ref('all')
const currentPage = ref(1)

// ── Sorting (group start/end, paid amount, debt amount) — only one column
// sorts at a time. ──────────────────────────────────────────────────────
const groupStartSort = ref('') // '', 'asc', 'desc'
const groupEndSort = ref('')
const paidAmountSort = ref('')
const debtAmountSort = ref('')

const sortRefs = { groupStart: groupStartSort, groupEnd: groupEndSort, paidAmount: paidAmountSort, debtAmount: debtAmountSort }
function setSort(column, direction) {
  const target = sortRefs[column]
  Object.values(sortRefs).forEach(r => { if (r !== target) r.value = '' })
  target.value = target.value === direction ? '' : direction
}

// Row-fetch-count no longer needs a backend round trip — it only resets to
// page 1 of the filtered result set; every filter/sort/page above is
// purely client-side.
watch(pageSizeOption, () => {
  currentPage.value = 1
})

const showPayModal = ref(false)
const activeEnrollment = ref(null)
const saving = ref(false)
const modalError = ref(null)

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
  return filteredDebtEnrollments.value.reduce((sum, e) => sum + getDebt(e), 0)
})

// Built from the debtors actually on screen, not a separate unrelated
// "all agents" fetch — an agent only shows up as a filter option if one of
// their referred students actually has debt right now.
const agentOptions = computed(() => {
  const map = new Map()
  debtEnrollments.value.forEach(e => {
    if (e.agent && !map.has(e.agent)) map.set(e.agent, e.agent_name || '')
  })
  return Array.from(map, ([id, name]) => ({ id, name })).sort((a, b) => a.name.localeCompare(b.name))
})

// Deduped, sorted contract (enrolled) amounts among the current debtors.
const distinctEnrolledAmounts = computed(() => {
  const amounts = new Set()
  debtEnrollments.value.forEach(e => {
    if (!e.enrolled_free && e.enrolled_amount) amounts.add(Number(e.enrolled_amount))
  })
  return [...amounts].sort((a, b) => a - b)
})

const certLabel = (e) => `${e.student_certificate_series || ''} ${e.student_certificate_number}`.trim()

const filteredDebtEnrollments = computed(() => {
  return debtEnrollments.value.filter(e => {
    const q = filterStudentName.value.toLowerCase().trim()
    const matchSearch = !q || (e.student_name || '').toLowerCase().includes(q)

    const matchCategory = !filterCategory.value || String(e.category) === String(filterCategory.value)

    const matchAgent = !filterAgent.value || e.agent === filterAgent.value

    const matchGroup = !filterGroup.value || (e.group_name || '').toLowerCase().includes(filterGroup.value.toLowerCase().trim())

    const hasCert = !!e.student_certificate_number
    const matchCertificate = !filterCertificate.value ||
      (filterCertificate.value === 'bor' && hasCert) ||
      (filterCertificate.value === 'yoq' && !hasCert)

    const matchStatus = !filterStatus.value || e.status === filterStatus.value

    const matchEnrolledAmount = !filterEnrolledAmount.value || Number(e.enrolled_amount) === Number(filterEnrolledAmount.value)

    const gStart = groupsById.value[e.group]?.started_at
    const gEnd = groupsById.value[e.group]?.ends_at
    const matchStartDate = (!startDateFrom.value || (gStart && gStart >= startDateFrom.value)) &&
      (!startDateTo.value || (gStart && gStart <= startDateTo.value))
    const matchEndDate = (!endDateFrom.value || (gEnd && gEnd >= endDateFrom.value)) &&
      (!endDateTo.value || (gEnd && gEnd <= endDateTo.value))

    return matchSearch && matchCategory && matchAgent && matchGroup && matchCertificate && matchStatus && matchEnrolledAmount && matchStartDate && matchEndDate
  })
})

// Sorting doesn't remove rows, only reorders — applied after filtering, before
// the pagination slice. Enrollments without a resolved group sort last
// regardless of direction.
const sortedDebtEnrollments = computed(() => {
  const list = [...filteredDebtEnrollments.value]

  if (paidAmountSort.value || debtAmountSort.value) {
    const direction = paidAmountSort.value || debtAmountSort.value
    const dir = direction === 'asc' ? 1 : -1
    list.sort((a, b) => {
      const va = paidAmountSort.value ? (Number(a.paid_amount) || 0) : getDebt(a)
      const vb = paidAmountSort.value ? (Number(b.paid_amount) || 0) : getDebt(b)
      return (va - vb) * dir
    })
    return list
  }

  const field = groupStartSort.value ? 'started_at' : (groupEndSort.value ? 'ends_at' : null)
  if (!field) return list
  const direction = groupStartSort.value || groupEndSort.value
  list.sort((a, b) => {
    const da = groupsById.value[a.group]?.[field] || ''
    const db = groupsById.value[b.group]?.[field] || ''
    if (!da && !db) return 0
    if (!da) return 1
    if (!db) return -1
    return direction === 'asc' ? da.localeCompare(db) : db.localeCompare(da)
  })
  return list
})

// pageSizeOption now purely controls how many of the *filtered* rows show
// per page — currentPage is clamped here (not via a watcher enumerating
// every filter ref) so it self-corrects the moment a filter shrinks the
// result set out from under it.
const displayPageSize = computed(() => pageSizeOption.value === 'all' ? Infinity : Number(pageSizeOption.value))
const displayTotalPages = computed(() => {
  if (pageSizeOption.value === 'all') return 1
  return Math.max(1, Math.ceil(sortedDebtEnrollments.value.length / displayPageSize.value))
})
const displayedDebtEnrollments = computed(() => {
  if (pageSizeOption.value === 'all') return sortedDebtEnrollments.value
  const page = Math.min(currentPage.value, displayTotalPages.value)
  const start = (page - 1) * displayPageSize.value
  return sortedDebtEnrollments.value.slice(start, start + displayPageSize.value)
})
function changePage(page) {
  if (page < 1 || page > displayTotalPages.value) return
  currentPage.value = page
}

async function fetchEnrollments() {
  loading.value = true
  try {
    // Always the full enrollment list — filtering/sorting/pagination above
    // all need to see every debtor, not just one page of them.
    const res = await api.get('/enrollments/', { params: { page_size: 100000 } })
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

function goGroup(groupId) {
  if (groupId) router.push(`/groups/${groupId}`)
}

function goAgent(agentId) {
  if (agentId) router.push(`/agents/${agentId}`)
}

function openPayModal(e) {
  activeEnrollment.value = e
  const debtAmt = getDebt(e)
  modalError.value = null
  payForm.value = {
    amountFormatted: formatMoney(debtAmt, false),
    amount: debtAmt,
    method: 'cash',
    notes: 'Qarzdorlik to\'lovi'
  }
  checkFile.value = null
  checkFileInputRef.value?.reset()
  showPayModal.value = true
}

function closePayModal() {
  showPayModal.value = false
}

const checkFile = ref(null)
const checkFileInputRef = ref(null)
function onCheckFileChange(e) {
  checkFile.value = e.target.files?.[0] || null
}

function onAmountInput(e) {
  const digits = e.target.value.replace(/\D/g, '')
  if (!digits) { payForm.value.amount = 0; payForm.value.amountFormatted = ''; return }
  const num = parseInt(digits, 10)
  payForm.value.amount = num
  payForm.value.amountFormatted = formatMoney(num, false)
}

async function savePayment() {
  const enrollmentId = activeEnrollment.value?.id
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
    if (checkFile.value) {
      const formData = new FormData()
      formData.append('user', authStore.user?.id)
      formData.append('enrollment', enrollmentId)
      formData.append('amount', payForm.value.amount)
      formData.append('status', 'accepted')
      formData.append('method', payForm.value.method)
      if (payForm.value.notes) formData.append('notes', payForm.value.notes)
      formData.append('click_check_image', checkFile.value)
      await api.post('/payments/', formData)
    } else {
      await api.post('/payments/', {
        user: authStore.user?.id,
        enrollment: enrollmentId,
        amount: payForm.value.amount,
        status: 'accepted',
        method: payForm.value.method,
        notes: payForm.value.notes
      })
    }
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
.flabel { font-size: 12.5px; font-weight: 600; color: #4B5563; }

/* Bounded, independently-scrolling table body so the header (both the
   label row and the column-filter row) can stick to the top of this
   container as rows scroll underneath, instead of scrolling away with
   the page. */
.table-scroll-area { overflow: auto; max-height: 600px; }

.data-table { width: 100%; border-collapse: collapse; th { background: #F9FAFB; padding: 13px 16px; font-size: 12px; font-weight: 700; color: #4B5563; text-align: left; border-bottom: 1px solid #E5E7EB; white-space: nowrap; } td { padding: 14px 16px; font-size: 13.5px; color: #1F2937; border-bottom: 1px solid #F3F4F6; vertical-align: middle; } }

/* Sticky is applied to <thead> itself, not to individual <th> cells —
   that keeps both header rows (labels + filters) moving as a single
   pinned unit with no per-row offset math needed. */
.data-table thead { position: sticky; top: 0; z-index: 3; }

/* ── Column-head filters ─────────────────────────────────── */
/* Higher specificity than ".data-table th" (0,1,1) on purpose — equal
   specificity would let source order decide and flatten this row's
   padding/background back to the label row's values. */
.data-table thead tr.col-filter-row th {
  padding: 8px 10px;
  background: #FAFAFB;
  border-bottom: 1px solid #E5E7EB;
}

.col-filter-input, .col-filter-select {
  width: 100%;
  box-sizing: border-box;
  padding: 6px 8px;
  border: 1px solid #D1D5DB;
  border-radius: 6px;
  font-size: 12.5px;
  color: #374151;
  outline: none;
  background: white;
  font-family: 'Inter', sans-serif;
  transition: border-color 0.15s;
}
.col-filter-input:focus, .col-filter-select:focus { border-color: #2D6A4F; }
.col-filter-input::placeholder { color: #9CA3AF; }

.col-sort-group { display: flex; gap: 4px; }
.col-sort-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  flex-shrink: 0;
  box-sizing: border-box;
  padding: 0;
  border: 1px solid #D1D5DB;
  border-radius: 6px;
  color: #6B7280;
  background: white;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
}
.col-sort-icon-btn:hover { border-color: #9CA3AF; color: #374151; }
.col-sort-icon-btn.active { border-color: #2D6A4F; color: #2D6A4F; background: #F0F7F4; }

/* ── Per-column date-range filters (under sort buttons) ────── */
.col-date-range {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 6px;
}
.col-date-input {
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  padding: 4px 5px;
  border: 1px solid #D1D5DB;
  border-radius: 6px;
  font-size: 11px;
  color: #374151;
  background: white;
  font-family: 'Inter', sans-serif;
}
.col-date-input:focus { border-color: #2D6A4F; outline: none; }
.btn-clear-date {
  border: none;
  background: #F3F4F6;
  color: #6B7280;
  border-radius: 6px;
  width: 22px;
  height: 22px;
  cursor: pointer;
  font-size: 11px;
  line-height: 1;
}
.btn-clear-date:hover { background: #E5E7EB; color: #111827; }

.no-data { text-align: center; padding: 40px; color: #9CA3AF; font-size: 14px; }

/* ── Pagination / row-fetch-count bar ────────────────────────── */
.pagination-bar { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #F9FAFB; border-top: 1px solid #E5E7EB; }
.pagination-info { font-size: 13.5px; color: #6B7280; font-weight: 500; }
.pagination-note { margin-left: 8px; font-size: 12px; color: #9CA3AF; font-weight: 400; }
.pagination-actions { display: flex; align-items: center; gap: 8px; }
.page-size-label { font-size: 13px; font-weight: 600; color: #4B5563; }
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
.btn-page:hover:not(:disabled) { background: #F3F4F6; border-color: #D1D5DB; }
.btn-page:disabled { opacity: 0.5; cursor: not-allowed; }
.page-num {
  display: inline-flex;
  align-items: center;
  padding: 0 8px;
  font-weight: 600;
  color: #374151;
  font-size: 13px;
  white-space: nowrap;
}
.page-size-select {
  padding: 6px 26px 6px 10px;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  background: white;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
}
.page-size-select:focus { border-color: #2D6A4F; outline: none; }

.student-name-link { font-weight: 700; color: #2563EB; cursor: pointer; text-decoration: underline; &:hover { color: #1D4ED8; } }
.link-value { cursor: pointer; color: #2563EB !important; font-weight: 700 !important; text-decoration: underline; &:hover { color: #1D4ED8 !important; } }
.cat-pill { padding: 4px 10px; background: #E8F5E9; color: #2D6A4F; border-radius: 8px; font-size: 12px; font-weight: 700; }
.debt-chip { padding: 4px 10px; background: #FEE2E2; color: #991B1B; border-radius: 8px; font-size: 12.5px; display: inline-block; }
.th-cert, .td-cert, .th-amount, .td-amount { white-space: nowrap; }

.status-chip {
  display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11.5px; font-weight: 600;
  &.enrolled { background: #DCFCE7; color: #15803D; }
  &.new { background: #E0F2FE; color: #0369A1; }
  &.finished { background: #F3F4F6; color: #4B5563; }
  &.canceled { background: #FEE2E2; color: #991B1B; }
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


.amount-input { font-size: 16.5px; font-weight: 800; color: #2D6A4F; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.btn-cancel { padding: 10px 18px; border: 1px solid #D1D5DB; background: white; border-radius: 10px; font-weight: 600; font-size: 13px; color: #374151; cursor: pointer; }
.btn-save { padding: 10px 22px; background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%); color: white; border-radius: 10px; font-weight: 700; font-size: 13.5px; cursor: pointer; }
.alert-error { background: #FEE2E2; color: #991B1B; padding: 10px 14px; border-radius: 10px; font-size: 13px; margin-bottom: 16px; }
</style>
