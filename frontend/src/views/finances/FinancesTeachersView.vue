<template>
  <AppLayout>

    <div class="page-top">
      <div>
        <h2 class="page-main-title">O'qituvchilar To'lovlari</h2>
        <p class="page-sub-title">O'qituvchilarga amalga oshirilgan to'lovlar ro'yxati</p>
      </div>

      <button class="btn-primary-action btn-indigo" @click="openCreateModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="18" height="18">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        <span>O'qituvchiga to'lov yozish</span>
      </button>
    </div>

    <!-- Metrics Cards -->
    <div class="metrics-cards-grid">
      <div class="card-metric card-indigo">
        <div class="card-metric-icon">👨‍🏫</div>
        <div>
          <span class="metric-lbl">To'lovlar Soni</span>
          <h4 class="metric-val text-indigo">{{ metrics.count }} ta to'lov</h4>
        </div>
      </div>

      <div class="card-metric card-purple font-hero">
        <div class="card-metric-icon">💵</div>
        <div>
          <span class="metric-lbl">Jami O'qituvchilar Summasi</span>
          <h4 class="metric-val text-purple">{{ formatMoney(metrics.total) }}</h4>
        </div>
      </div>

      <div class="card-metric card-amber font-hero">
        <div class="card-metric-icon">🎁</div>
        <div>
          <span class="metric-lbl">Sertifikat Bonuslari</span>
          <h4 class="metric-val text-amber">{{ formatMoney(metrics.bonus) }}</h4>
        </div>
      </div>
    </div>

    <!-- Table Section -->
    <div class="table-section-card margin-top">
      <div class="table-container">
        <div v-if="initialLoading" class="state-box">
          <div class="spinner"></div>
          <span>O'qituvchilar to'lovlari yuklanmoqda...</span>
        </div>

        <div v-else class="table-scroll-area">
        <table class="data-table">
          <thead>
            <tr>
              <th>O'qituvchi</th>
              <th>Turi</th>
              <th>O'quvchi</th>
              <th>O'quvchi to'lagan summa</th>
              <th>To'langan Summa</th>
              <th>Usul</th>
              <th>Sana & Vaqt</th>
              <th>To'lovni kiritgan</th>
              <th>Izoh</th>
              <th style="width: 110px; text-align: right;">Amallar</th>
            </tr>
            <tr class="col-filter-row">
              <th>
                <input v-model="filterTeacherName" class="col-filter-input" type="text" placeholder="Ism bo'yicha qidirish..." />
              </th>
              <th>
                <div class="select-wrap-relative">
                  <select v-model="filterPaymentType" class="col-filter-select">
                    <option value="">Barchasi</option>
                    <option value="paid">Oylik to'lov</option>
                    <option value="bonus_teacher">Sertifikat bonusi</option>
                  </select>
                </div>
              </th>
              <th></th>
              <th>
                <div class="col-sort-group">
                  <button type="button" class="col-sort-icon-btn" :class="{ active: studentPaidSort === 'asc' }" title="O'sish tartibida" @click="setSort('studentPaid', 'asc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 20V4"></path>
                      <path d="M3 8l3-4 3 4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button type="button" class="col-sort-icon-btn" :class="{ active: studentPaidSort === 'desc' }" title="Kamayish tartibida" @click="setSort('studentPaid', 'desc')">
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
                  <button type="button" class="col-sort-icon-btn" :class="{ active: amountSort === 'asc' }" title="O'sish tartibida" @click="setSort('amount', 'asc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 20V4"></path>
                      <path d="M3 8l3-4 3 4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button type="button" class="col-sort-icon-btn" :class="{ active: amountSort === 'desc' }" title="Kamayish tartibida" @click="setSort('amount', 'desc')">
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
                  <select v-model="filterMethod" class="col-filter-select">
                    <option value="">Barchasi</option>
                    <option value="cash">Naqd</option>
                    <option value="card">Karta</option>
                    <option value="qr_code">QR code</option>
                    <option value="click">Click</option>
                    <option value="transfer">O'tkazma</option>
                  </select>
                </div>
              </th>
              <th>
                <div class="col-sort-group">
                  <button type="button" class="col-sort-icon-btn" :class="{ active: paymentDateSort === 'asc' }" title="O'sish tartibida (eskidan yangiga)" @click="setSort('paymentDate', 'asc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 20V4"></path>
                      <path d="M3 8l3-4 3 4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button type="button" class="col-sort-icon-btn" :class="{ active: paymentDateSort === 'desc' }" title="Kamayish tartibida (yangidan eskiga)" @click="setSort('paymentDate', 'desc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 4v16"></path>
                      <path d="M3 16l3 4 3-4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button v-if="paymentDateFrom || paymentDateTo" type="button" class="btn-clear-date" @click="paymentDateFrom = ''; paymentDateTo = ''" title="Tozalash">✕</button>
                </div>
                <div class="col-date-range">
                  <input v-model="paymentDateFrom" type="date" class="col-date-input" title="Sana (dan)" />
                  <input v-model="paymentDateTo" type="date" class="col-date-input" title="Sana (gacha)" />
                </div>
              </th>
              <th>
                <div class="select-wrap-relative">
                  <select v-model="filterCashierId" class="col-filter-select">
                    <option value="">Barchasi</option>
                    <option v-for="c in distinctCashiers" :key="c.id" :value="c.id">{{ c.name }}</option>
                  </select>
                </div>
              </th>
              <th></th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="payments.length === 0">
              <td colspan="10" class="no-data">O'qituvchilar bo'yicha to'lovlar topilmadi</td>
            </tr>
            <tr v-for="p in payments" :key="p.id" class="table-row">
              <td class="td-name">
                <div v-if="p.user" class="teacher-name link-value" @click="goUser(p.user)">👨‍🏫 {{ p.user_full_name || p.cashier_name || 'O\'qituvchi' }}</div>
                <div v-else class="teacher-name">👨‍🏫 {{ p.user_full_name || p.cashier_name || 'O\'qituvchi' }}</div>
              </td>
              <td>
                <span class="type-chip" :class="{ 'type-chip-bonus': p.status === 'bonus_teacher' }">
                  {{ paymentTypeText(p) }}
                </span>
              </td>
              <td>
                <span v-if="p.status === 'bonus_teacher' && p.student" class="link-value" @click="goStudent(p.student)">{{ p.student_name || '-' }}</span>
                <span v-else>{{ p.status === 'bonus_teacher' ? (p.student_name || '-') : '-' }}</span>
              </td>
              <td>{{ p.status === 'bonus_teacher' && p.student_paid_amount != null ? formatMoney(p.student_paid_amount) : '-' }}</td>
              <td class="td-amount">
                <span class="amount-val text-purple">{{ formatMoney(p.amount) }}</span>
              </td>
              <td><span class="method-chip">{{ methodText(p.method) }}</span></td>
              <td class="td-date">{{ formatDateTime(p.created_at) }}</td>
              <td>
                <span v-if="p.created_by" class="link-value" @click="goUser(p.created_by)">{{ p.created_by_name || '-' }}</span>
                <span v-else>{{ p.created_by_name || '-' }}</span>
              </td>
              <td>{{ p.notes || '-' }}</td>
              <td style="text-align: right;">
                <div class="row-actions">
                  <template v-if="authStore.isSuperuser || (authStore.isAdminOrSuperuser && p.status !== 'bonus_teacher')">
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

      <!-- Pagination controls -->
      <div class="pagination-bar">
        <span class="pagination-info">
          Jami: <strong>{{ totalCount }}</strong> tadan <strong>{{ payments.length }}</strong> ko'rsatilmoqda
        </span>
        <div class="pagination-actions">
          <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">Oldingi</button>
          <span v-if="pageSizeOption !== 'all'" class="page-num">Sahifa {{ Math.min(currentPage, displayTotalPages) }} / {{ displayTotalPages }}</span>
          <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === displayTotalPages" @click="changePage(currentPage + 1)">Keyingi</button>
          <label class="page-size-label" for="teachers-page-size">Ko'rsatish:</label>
          <div class="select-wrap">
            <select id="teachers-page-size" v-model="pageSizeOption" class="page-size-select">
              <option value="50">50</option>
              <option value="100">100</option>
              <option value="200">200</option>
              <option value="all">Barchasi</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- CREATE / EDIT MODAL WITH SEARCHABLE TEACHER SELECT -->
    <Transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card">
          <div class="modal-header-banner indigo-banner">
            <div class="header-left-info">
              <div class="header-icon-box indigo-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
              </div>
              <div>
                <h3>{{ isEditing ? "O'qituvchi To'lovini Tahrirlash" : "Yangi O'qituvchi To'lovi" }}</h3>
                <p>O'qituvchi to'lovi</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closeModal">✕</button>
          </div>

          <form @submit.prevent="savePayment" class="modal-body">
            <div v-if="modalError" class="alert-error">{{ modalError }}</div>

            <!-- Searchable Teacher Selector -->
            <div class="form-group" v-if="!isEditing">
              <label class="flabel required">O'qituvchini Ism bo'yicha Qidirish *</label>
              <div class="searchable-select-wrap" ref="teacherSelectWrapRef">
                <input
                  v-model="teacherSearchQuery"
                  type="text"
                  class="finput search-input-field"
                  placeholder="O'qituvchi ismini kiriting..."
                  @focus="showTeacherDropdown = true"
                  @keydown="onTeacherKeydown"
                />
                <button v-if="form.teacher" type="button" class="input-clear-btn" title="O'qituvchini bekor qilish" @click="clearTeacherSelection">✕</button>
                <div v-if="showTeacherDropdown" class="dropdown-options-list">
                  <div
                    v-for="(t, idx) in filteredTeachers"
                    :key="t.id"
                    class="dropdown-option-item"
                    :class="{ selected: form.teacher === t.id, highlighted: teacherKb.highlightedIndex.value === idx }"
                    @click="selectTeacher(t)"
                  >
                    <div class="opt-name">👨‍🏫 {{ getUserFullName(t) }}</div>
                    <div class="opt-sub">{{ roleText(t.role) }} ({{ t.phone }})</div>
                  </div>
                  <div v-if="filteredTeachers.length === 0" class="dropdown-empty">
                    Mos o'qituvchi topilmadi
                  </div>
                </div>
              </div>
              <div v-if="selectedTeacherLabel" class="selected-chip">
                Tanlandi: <strong>{{ selectedTeacherLabel }}</strong>
              </div>
            </div>

            <!-- Amount Input -->
            <div class="form-group">
              <label class="flabel required">To'lov Summasi *</label>
              <input
                v-model="form.amountFormatted"
                type="text"
                class="finput amount-input purple-text"
                placeholder="0"
                required
                @input="onAmountInput"
              />
            </div>

            <!-- Payment Status Select -->
            <div class="form-group">
              <label class="flabel required">To'lov Turi *</label>
              <div class="select-wrap-relative">
                <select v-model="form.status" class="fselect-field">
                  <option value="paid">Oylik to'lov</option>
                  <option v-if="authStore.canPayBonus" value="bonus_teacher">Sertifikat bonusi</option>
                </select>
                <div class="select-chevron-icon">▼</div>
              </div>
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
              <label class="flabel">Izoh / Eslatma</label>
              <input v-model="form.notes" type="text" class="finput" placeholder="Masalan: Oylik maosh yoki soatbay ish haqida..." />
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-cancel" @click="closeModal">Bekor qilish</button>
              <button type="submit" class="btn-save btn-indigo-save" :disabled="saving">
                {{ saving ? "Saqlanmoqda..." : "To'lovni Saqlash" }}
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
      Haqiqatan ham <strong>#{{ deletingPayment?.id }}</strong> raqamli o'qituvchi to'lovini o'chirmoqchimisiz?
    </ConfirmDeleteModal>

  </AppLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import ConfirmDeleteModal from '@/components/ConfirmDeleteModal.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useBranchStore } from '@/stores/branch'
import { formatMoney } from '@/utils/formatters'
import { useSearchSelectKeyboard } from '@/composables/useSearchSelectKeyboard'
import { debounce } from '@/utils/debounce'

const authStore = useAuthStore()
const branchStore = useBranchStore()
const router = useRouter()

function goUser(id) {
  if (!id) return
  router.push(`/users/${id}`)
}

function goStudent(id) {
  if (!id) return
  router.push(`/students/${id}`)
}

const payments = ref([])
const teachers = ref([])
const loading = ref(true)
const initialLoading = ref(true)

const filterTeacherName = ref('')
const filterPaymentType = ref('')
const filterMethod = ref('')
const filterCashierId = ref('')
const paymentDateSort = ref('') // '', 'asc', 'desc'
const studentPaidSort = ref('')
const amountSort = ref('')
const paymentDateFrom = ref('')
const paymentDateTo = ref('')

const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const saving = ref(false)
const modalError = ref(null)

const teacherSearchQuery = ref('')
const showTeacherDropdown = ref(false)
const selectedTeacherLabel = ref('')

const form = ref({ teacher: '', amountFormatted: '', amount: 0, status: 'paid', method: 'cash', notes: '' })

// Filtering/sorting/pagination are applied server-side (see buildParams/
// fetchPayments) — `payments` only ever holds the current page.
const pageSizeOption = ref('50')
const totalCount = ref(0)
const currentPage = ref(1)

const sortRefs = { paymentDate: paymentDateSort, studentPaid: studentPaidSort, amount: amountSort }
const ORDERING_PARAM_MAP = { paymentDate: 'created_at', studentPaid: 'student_paid_amount', amount: 'amount' }
const ordering = computed(() => {
  for (const [column, sortRef] of Object.entries(sortRefs)) {
    if (sortRef.value) return (sortRef.value === 'desc' ? '-' : '') + ORDERING_PARAM_MAP[column]
  }
  return ''
})
function setSort(column, direction) {
  const target = sortRefs[column]
  Object.values(sortRefs).forEach(r => { if (r !== target) r.value = '' })
  target.value = target.value === direction ? '' : direction
  refetch()
}

const displayTotalPages = computed(() => {
  if (pageSizeOption.value === 'all') return 1
  return Math.max(1, Math.ceil(totalCount.value / Number(pageSizeOption.value)))
})
function changePage(page) {
  if (page < 1 || page > displayTotalPages.value) return
  currentPage.value = page
  fetchPayments()
}

// Aggregated in the DB over every row matching the active filters, not just
// the current page. The bonus subtotal is a second totals call scoped to
// status=bonus_teacher (skipped when the type filter already excludes it).
const metrics = ref({ total: 0, count: 0, bonus: 0 })
async function fetchMetrics() {
  try {
    const totalsRes = await api.get('/payments/totals/', { params: buildParams({ forTotals: true }) })
    let bonus = 0
    if (filterPaymentType.value !== 'paid') {
      const bonusRes = await api.get('/payments/totals/', { params: buildParams({ forTotals: true, forceStatus: 'bonus_teacher' }) })
      bonus = bonusRes.data.total
    }
    metrics.value = { total: totalsRes.data.total, count: totalsRes.data.count, bonus }
  } catch (err) { console.error(err) }
}

// Distinct cashiers, for the "To'lovni kiritgan" filter select. Fetched
// separately (capped at 1000) so the dropdown still lists every cashier
// even though `payments` now only holds one page.
const allTeacherPayments = ref([])
async function fetchDistinctCashiers() {
  try {
    const res = await api.get('/payments/', { params: { status: 'paid,bonus_teacher', user_role: 'coordinator', page_size: 1000 } })
    allTeacherPayments.value = res.data.results || res.data
  } catch (err) { console.error(err) }
}
const distinctCashiers = computed(() => {
  const map = {}
  allTeacherPayments.value.forEach(p => {
    if (p.created_by && !map[p.created_by]) map[p.created_by] = { id: p.created_by, name: p.created_by_name || `#${p.created_by}` }
  })
  return Object.values(map).sort((a, b) => a.name.localeCompare(b.name))
})

function paymentTypeText(p) {
  return p.status === 'bonus_teacher' ? 'Sertifikat bonusi' : 'Oylik to\'lov'
}

const filteredTeachers = computed(() => {
  const q = teacherSearchQuery.value.toLowerCase().trim()
  if (!q) return teachers.value
  return teachers.value.filter(t => getUserFullName(t).toLowerCase().includes(q))
})

function getUserFullName(u) {
  if (!u) return ''
  return u.full_name || `${u.first_name || ''} ${u.last_name || ''}`.trim() || u.username || 'Xodim'
}

function roleText(r) {
  if (r === 'instructor') return 'Instruktor'
  if (r === 'coordinator') return 'O\'qituvchi'
  return r || 'Xodim'
}

// Shared by fetchPayments and fetchMetrics so both always see the exact
// same filter set. forTotals omits page/page_size/ordering. forceStatus
// overrides the status param (used by the bonus subtotal call).
function buildParams({ forTotals = false, forceStatus = null } = {}) {
  const params = { status: forceStatus || (filterPaymentType.value || 'paid,bonus_teacher'), user_role: 'coordinator' }
  if (!forTotals) {
    params.page = currentPage.value
    params.page_size = pageSizeOption.value === 'all' ? 100000 : Number(pageSizeOption.value)
    if (ordering.value) params.ordering = ordering.value
  }
  if (filterTeacherName.value.trim()) params.student_name = filterTeacherName.value.trim()
  if (filterMethod.value) params.method = filterMethod.value
  if (filterCashierId.value) params.created_by = filterCashierId.value
  if (paymentDateFrom.value) params.date_from = paymentDateFrom.value
  if (paymentDateTo.value) params.date_to = paymentDateTo.value
  if (branchStore.activeBranchId) params.branch = branchStore.activeBranchId
  return params
}

async function fetchPayments() {
  loading.value = true
  try {
    const res = await api.get('/payments/', { params: buildParams() })
    const rawList = res.data.results ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    payments.value = rawList
    totalCount.value = res.data.count ?? rawList.length
  } catch (err) { console.error(err) }
  finally { loading.value = false; initialLoading.value = false }
}

async function fetchTeachers() {
  try {
    const res = await api.get('/users/', { params: { page_size: 1000 } })
    const allUsers = res.data.results || res.data
    teachers.value = allUsers.filter(u => u.role === 'coordinator')
  } catch (err) { console.error(err) }
}

function refetch() {
  currentPage.value = 1
  fetchPayments()
  fetchMetrics()
}
watch(pageSizeOption, refetch)
watch([filterPaymentType, filterMethod, filterCashierId, paymentDateFrom, paymentDateTo], refetch)
const debouncedRefetch = debounce(refetch, 400)
watch(filterTeacherName, debouncedRefetch)
watch(() => branchStore.activeBranchId, refetch)

function selectTeacher(t) {
  form.value.teacher = t.id
  selectedTeacherLabel.value = `${getUserFullName(t)} (${roleText(t.role)})`
  teacherSearchQuery.value = getUserFullName(t)
  showTeacherDropdown.value = false
}

function clearTeacherSelection() {
  form.value.teacher = ''
  selectedTeacherLabel.value = ''
  teacherSearchQuery.value = ''
}

const teacherSelectWrapRef = ref(null)
function handleSelectOutsideClick(e) {
  if (teacherSelectWrapRef.value && !teacherSelectWrapRef.value.contains(e.target)) {
    showTeacherDropdown.value = false
  }
}

const teacherKb = useSearchSelectKeyboard()
function onTeacherKeydown(e) {
  teacherKb.onKeydown(e, filteredTeachers.value, selectTeacher, () => { showTeacherDropdown.value = false })
}

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
  teacherSearchQuery.value = ''
  selectedTeacherLabel.value = ''
  showTeacherDropdown.value = false
  form.value = { teacher: '', amountFormatted: '', amount: 0, status: 'paid', method: 'cash', notes: '' }
  showModal.value = true
}

function openEditModal(p) {
  isEditing.value = true
  editingId.value = p.id
  modalError.value = null
  form.value = { teacher: p.user, amountFormatted: formatMoney(p.amount, false), amount: p.amount, status: p.status || 'paid', method: p.method || 'cash', notes: p.notes || '' }
  showModal.value = true
}

function closeModal() { showModal.value = false }

async function savePayment() {
  if (!isEditing.value && !form.value.teacher) { modalError.value = "O'qituvchini tanlang."; return }
  if (!form.value.amount || form.value.amount <= 0) { modalError.value = "To'g'ri to'lov summasini kiriting."; return }
  saving.value = true
  modalError.value = null
  try {
    if (isEditing.value) {
      await api.patch(`/payments/${editingId.value}/`, { amount: form.value.amount, status: form.value.status, method: form.value.method, notes: form.value.notes })
    } else {
      await api.post('/payments/', {
        user: form.value.teacher || authStore.user?.id,
        amount: form.value.amount,
        status: form.value.status,
        method: form.value.method,
        notes: form.value.notes,
        branch: branchStore.activeBranchId ?? null,
      })
    }
    closeModal()
    fetchPayments()
    fetchMetrics()
    fetchDistinctCashiers()
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
    fetchMetrics()
  } catch (err) {
    deleteError.value = "O'chirishda xatolik yuz berdi"
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  fetchPayments()
  fetchMetrics()
  fetchDistinctCashiers()
  fetchTeachers()
  document.addEventListener('click', handleSelectOutsideClick)
})
onUnmounted(() => {
  document.removeEventListener('click', handleSelectOutsideClick)
})
</script>

<style scoped>
.page-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-main-title { font-size: 22px; font-weight: 700; color: #111827; }
.page-sub-title { font-size: 13px; color: #6B7280; margin-top: 2px; }
.btn-primary-action { display: inline-flex; align-items: center; gap: 8px; padding: 11px 20px; background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%); color: white; border-radius: 12px; font-weight: 700; font-size: 13.5px; box-shadow: 0 4px 14px rgba(79, 70, 229, 0.25); cursor: pointer; transition: all 0.2s ease; }
.btn-primary-action:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(79, 70, 229, 0.35); }
.metrics-cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; }
.card-metric { background: white; border: 1.5px solid #E5E7EB; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); }
.card-metric-icon { font-size: 30px; }
.metric-lbl { font-size: 12.5px; color: #6B7280; font-weight: 600; }
.metric-val { font-size: 18px; font-weight: 800; color: #111827; margin-top: 4px; }
.text-indigo { color: #4F46E5; font-weight: 800; }
.text-purple { color: #9333EA; font-weight: 800; }
.text-amber { color: #D97706; font-weight: 800; }
.card-amber .card-metric-icon { filter: none; }
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
.col-filter-input:focus, .col-filter-select:focus { border-color: #4F46E5; }
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
.col-sort-icon-btn.active { border-color: #4F46E5; color: #4F46E5; background: #EEF2FF; }

.col-date-range { display: flex; flex-direction: column; gap: 4px; margin-top: 6px; }
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
}
.col-date-input:focus { border-color: #4F46E5; outline: none; }
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
  flex-shrink: 0;
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
.select-wrap { position: relative; }
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
.page-size-select:focus { border-color: #4F46E5; outline: none; }

.teacher-name { font-weight: 700; color: #4F46E5; }
.link-value { cursor: pointer; color: #2563EB !important; font-weight: 700 !important; text-decoration: underline; }
.link-value:hover { color: #1D4ED8 !important; }
.method-chip { padding: 4px 12px; background: #F3F4F6; color: #374151; border-radius: 20px; font-size: 12px; font-weight: 600; }
.type-chip { padding: 4px 10px; background: #EEF2FF; color: #4338CA; border-radius: 8px; font-size: 11.5px; font-weight: 700; white-space: nowrap; }
.type-chip-bonus { background: #FEF3C7; color: #92400E; }
.row-actions { display: flex; gap: 8px; justify-content: flex-end; }
.btn-action-edit, .btn-action-delete { width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; border: 1px solid #E5E7EB; background: #F9FAFB; cursor: pointer; transition: all 0.15s ease; }
.btn-action-edit { color: #2563EB; &:hover { background: #EFF6FF; border-color: #BFDBFE; transform: translateY(-1px); } }
.btn-action-delete { color: #EF4444; &:hover { background: #FEE2E2; border-color: #FCA5A5; transform: translateY(-1px); } }

.state-box, .empty-state { text-align: center; padding: 40px 0; color: #6B7280; }
.spinner { width: 28px; height: 28px; border: 3px solid #E5E7EB; border-top-color: #4F46E5; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px; }
@keyframes spin { to { transform: rotate(360deg); } }

.modal-overlay { position: fixed; inset: 0; z-index: 1000; background: rgba(15, 23, 42, 0.65); backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-card { background: white; border-radius: 20px; width: 100%; max-width: 500px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); }
.modal-header-banner.indigo-banner { padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #F3F4F6; background: linear-gradient(180deg, #EEF2FF 0%, #FFFFFF 100%); }
.header-left-info { display: flex; align-items: center; gap: 12px; h3 { font-size: 17px; font-weight: 700; color: #3730A3; } p { font-size: 12px; color: #6B7280; margin-top: 2px; } }
.header-icon-box.indigo-box { width: 42px; height: 42px; border-radius: 12px; background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%); color: white; display: flex; align-items: center; justify-content: center; }
.btn-modal-close { background: none; border: none; font-size: 18px; color: #9CA3AF; cursor: pointer; }
.modal-body { padding: 24px; }

/* UNIFORM INPUT & SELECT STYLING */
.form-group { margin-bottom: 18px; width: 100%; }
.flabel { display: block; font-size: 12.5px; font-weight: 600; color: #374151; margin-bottom: 6px; }
.finput, .fselect-field {
  width: 100%; box-sizing: border-box; padding: 11px 14px;
  border: 1.5px solid #E5E7EB; border-radius: 10px; font-size: 14px;
  background-color: #FAFAFA; color: #111827; outline: none;
  transition: all 0.2s ease; appearance: none; -webkit-appearance: none;
  &:focus { border-color: #4F46E5; background-color: #FFFFFF; box-shadow: 0 0 0 3.5px rgba(79, 70, 229, 0.12); }
}

.select-wrap-relative { position: relative; width: 100%; }
.select-chevron-icon { position: absolute; right: 14px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #9CA3AF; font-size: 10px; }

.searchable-select-wrap { position: relative; width: 100%; }
.input-clear-btn {
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  width: 22px; height: 22px; border-radius: 50%; border: none;
  background: #E5E7EB; color: #4B5563; font-size: 11px; line-height: 1;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.input-clear-btn:hover { background: #D1D5DB; color: #111827; }
.searchable-select-wrap .finput { padding-right: 34px; }
.dropdown-options-list { position: absolute; top: 100%; left: 0; right: 0; max-height: 200px; overflow-y: auto; background: white; border: 1.5px solid #4F46E5; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); z-index: 50; margin-top: 4px; }
.dropdown-option-item { padding: 10px 14px; cursor: pointer; border-bottom: 1px solid #F3F4F6; &:hover { background: #EEF2FF; } &.selected { background: #C7D2FE; font-weight: 700; } &.highlighted { background: #EEF2FF; } }
.opt-name { font-size: 13.5px; font-weight: 600; color: #111827; }
.opt-sub { font-size: 11.5px; color: #6B7280; margin-top: 1px; }
.dropdown-empty { padding: 12px; text-align: center; color: #9CA3AF; font-size: 13px; }
.selected-chip { font-size: 12.5px; color: #4F46E5; margin-top: 6px; }

.amount-input.purple-text { font-size: 16.5px; font-weight: 800; color: #9333EA; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.btn-cancel { padding: 10px 18px; border: 1px solid #D1D5DB; background: white; border-radius: 10px; font-weight: 600; font-size: 13px; color: #374151; cursor: pointer; }
.btn-indigo-save { padding: 10px 22px; background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%); color: white; border-radius: 10px; font-weight: 700; font-size: 13.5px; cursor: pointer; }
.alert-error { background: #FEE2E2; color: #991B1B; padding: 10px 14px; border-radius: 10px; font-size: 13px; margin-bottom: 16px; }
</style>
