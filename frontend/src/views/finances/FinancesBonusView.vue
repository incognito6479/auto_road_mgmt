<template>
  <AppLayout>

    <div class="page-top">
      <div>
        <h2 class="page-main-title">Agent Bonuslari (Status: Bonus)</h2>
        <p class="page-sub-title">Hamkor agentlarga to'langan bonuslar va qaytarilgan bonuslar ro'yxati</p>
      </div>

      <div style="display: flex; gap: 12px; align-items: center;">
        <button v-if="authStore.canReturnMoney" class="btn-primary-action btn-red-action" @click="openReturnModal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="18" height="18">
            <path d="M3 10h10a8 8 0 0 1 8 8v2M3 10l6 6m-6-6l6-6"></path>
          </svg>
          <span>Bonusni Qaytarish</span>
        </button>

        <button class="btn-primary-action btn-gold" @click="openCreateModal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="18" height="18">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          <span>Yangi bonus to'lovi</span>
        </button>
      </div>
    </div>

    <!-- Metrics Cards -->
    <div class="metrics-cards-grid">
      <div class="card-metric card-gold">
        <div class="card-metric-icon">🎁</div>
        <div>
          <span class="metric-lbl">Jami Bonus Operatsiyalari</span>
          <h4 class="metric-val text-gold">{{ payments.length }} ta bonus to'lov</h4>
        </div>
      </div>

      <div class="card-metric card-amber font-hero">
        <div class="card-metric-icon">💰</div>
        <div>
          <span class="metric-lbl">Jami Berilgan Bonuslar Summasi</span>
          <h4 class="metric-val text-amber">{{ formatMoney(metrics.total) }}</h4>
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
            v-model="filterAgentName"
            type="text"
            placeholder="Agent yoki O'quvchi F.I.SH..."
            class="search-input"
          />
        </div>

        <div class="filter-controls">
          <div class="filter-item">
            <label class="flabel">Agent:</label>
            <div class="select-wrap-relative">
              <select v-model="filterAgent" class="fselect-field">
                <option value="">Barchasi</option>
                <option v-for="ag in agents" :key="ag.id" :value="ag.id">{{ ag.full_name }}</option>
              </select>
            </div>
          </div>

          <div class="filter-item">
            <label class="flabel">Kategoriya:</label>
            <div class="select-wrap-relative">
              <select v-model="filterCategory" class="fselect-field">
                <option value="">Barchasi</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
            </div>
          </div>

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
          Jami: <strong>{{ totalCount }}</strong> ta bonus to'lov
        </div>
      </div>

      <div class="table-container">
        <div v-if="loading" class="state-box">
          <div class="spinner"></div>
          <span>Bonuslar yuklanmoqda...</span>
        </div>

        <div v-else-if="payments.length === 0" class="empty-state">
          <p>Bonus statusidagi to'lovlar topilmadi</p>
        </div>

        <table v-else class="data-table">
          <thead>
            <tr>
              <th>Agent F.I.SH.</th>
              <th>O'quvchi F.I.SH.</th>
              <th>Kategoriya</th>
              <th>Bonus Summasi</th>
              <th>Usul</th>
              <th>Sana & Vaqt</th>
              <th style="width: 110px; text-align: right;">Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in payments" :key="p.id" class="table-row">
              <td class="td-name">
                <div v-if="p.agent" class="agent-name link-value" @click="goAgent(p.agent)">👤 {{ p.agent_name || 'Noma\'lum Agent' }}</div>
                <div v-else class="agent-name">👤 {{ p.agent_name || 'Noma\'lum Agent' }}</div>
                <div v-if="p.agent_phone" class="agent-phone">{{ p.agent_phone }}</div>
                <div v-if="p.agent_phone2" class="agent-phone">{{ p.agent_phone2 }} (qo'shimcha)</div>
              </td>
              <td class="td-name">
                <div v-if="p.student" class="student-name link-value" @click="goStudent(p.student)">{{ p.student_name || '-' }}</div>
                <div v-else class="student-name">{{ p.student_name || '-' }}</div>
                <div v-if="p.student_jshshr" class="student-jshshr">JSHSHR: {{ p.student_jshshr }}</div>
              </td>
              <td>
                <span class="cat-pill">{{ p.category_name || '-' }}</span>
                <div v-if="p.group_name" class="group-sub">{{ p.group_name }}</div>
                <div v-if="groupsByName[p.group_name]" class="group-dates">
                  {{ formatDate(groupsByName[p.group_name].started_at) }} — {{ formatDate(groupsByName[p.group_name].ends_at) }}
                </div>
              </td>
              <td class="td-amount">
                <span class="amount-val text-amber">{{ formatMoney(p.amount) }}</span>
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

    <!-- CREATE / EDIT BONUS MODAL -->
    <Transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card">
          <div class="modal-header-banner gold-banner">
            <div class="header-left-info">
              <div class="header-icon-box gold-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="9" cy="7" r="4"></circle>
                </svg>
              </div>
              <div>
                <h3>{{ isEditing ? "Bonus To'lovini Tahrirlash" : "Yangi Agent Bonusi" }}</h3>
                <p>Agentga bonus payoutini kiriting</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closeModal">✕</button>
          </div>

          <form @submit.prevent="savePayment" class="modal-body">
            <div v-if="modalError" class="alert-error">{{ modalError }}</div>

            <!-- Searchable Agent Selector -->
            <div class="form-group" v-if="!isEditing">
              <label class="flabel required">Agentni Ism bo'yicha Qidirish *</label>
              <div class="searchable-select-wrap">
                <input
                  v-model="agentSearchQuery"
                  type="text"
                  class="finput search-input-field"
                  placeholder="Agent ismini kiriting..."
                  @focus="showAgentDropdown = true"
                  @keydown="onAgentKeydown"
                />
                <div v-if="showAgentDropdown" class="dropdown-options-list">
                  <div
                    v-for="(ag, idx) in filteredAgents"
                    :key="ag.id"
                    class="dropdown-option-item"
                    :class="{ selected: form.agent === ag.id, highlighted: agentKb.highlightedIndex.value === idx }"
                    @click="selectAgent(ag)"
                  >
                    <div class="opt-name">👤 {{ ag.full_name }}</div>
                    <div class="opt-sub">{{ ag.phone || 'Telefon ko\'rsatilmagan' }}</div>
                  </div>
                  <div v-if="filteredAgents.length === 0" class="dropdown-empty">
                    Mos agent topilmadi
                  </div>
                </div>
              </div>
              <div v-if="selectedAgentLabel" class="selected-chip">
                Tanlandi: <strong>{{ selectedAgentLabel }}</strong>
              </div>
            </div>

            <!-- Searchable Student Selector (Search by name) -->
            <div class="form-group" v-if="!isEditing">
              <label class="flabel">O'quvchini Ism bo'yicha Qidirish (Ixtiyoriy)</label>
              <div class="searchable-select-wrap">
                <input
                  v-model="studentSearchQuery"
                  type="text"
                  class="finput search-input-field"
                  placeholder="O'quvchi ismini kiriting..."
                  @focus="showStudentDropdown = true"
                  @keydown="onStudentKeydown"
                />
                <div v-if="showStudentDropdown" class="dropdown-options-list">
                  <div
                    v-for="(e, idx) in filteredEnrollments"
                    :key="e.id"
                    class="dropdown-option-item"
                    :class="{ selected: form.enrollment === e.id, highlighted: studentKb.highlightedIndex.value === idx }"
                    @click="selectEnrollment(e)"
                  >
                    <div class="opt-name">{{ e.student_name }}</div>
                    <div class="opt-sub">{{ e.category_name }} {{ e.group_name ? `(${e.group_name})` : '' }}</div>
                  </div>
                  <div v-if="filteredEnrollments.length === 0" class="dropdown-empty">
                    Mos o'quvchi topilmadi
                  </div>
                </div>
              </div>
              <div v-if="selectedStudentLabel" class="selected-chip">
                Tanlandi: <strong>{{ selectedStudentLabel }}</strong>
              </div>
            </div>

            <!-- Amount Input -->
            <div class="form-group">
              <label class="flabel required">Bonus Summasi *</label>
              <input
                v-model="form.amountFormatted"
                type="text"
                class="finput amount-input gold-text"
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
                  <option value="transfer">O'tkazma</option>
                </select>
                <div class="select-chevron-icon">▼</div>
              </div>
            </div>

            <!-- Notes -->
            <div class="form-group">
              <label class="flabel">Izoh / Eslatma</label>
              <input v-model="form.notes" type="text" class="finput" placeholder="Masalan: 1-o'quvchi uchun berilgan bonus..." />
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-cancel" @click="closeModal">Bekor qilish</button>
              <button type="submit" class="btn-save btn-gold-save" :disabled="saving">
                {{ saving ? "Saqlanmoqda..." : "🎁 Bonusni Saqlash" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- RETURN AGENT BONUS MONEY MODAL -->
    <Transition name="modal">
      <div v-if="showReturnModal" class="modal-overlay" @click.self="closeReturnModal">
        <div class="modal-card">
          <div class="modal-header-banner red-banner">
            <div class="header-left-info">
              <div class="header-icon-box red-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <path d="M3 10h10a8 8 0 0 1 8 8v2M3 10l6 6m-6-6l6-6"></path>
                </svg>
              </div>
              <div>
                <h3>Agentdan Bonusni Qaytarish</h3>
                <p>Agent berilgan bonusni qaytarganda kiritiladi</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closeReturnModal">✕</button>
          </div>

          <form @submit.prevent="saveReturnBonus" class="modal-body">
            <div v-if="returnModalError" class="alert-error">{{ returnModalError }}</div>

            <!-- Searchable Agent Selector for Return -->
            <div class="form-group">
              <label class="flabel required">Agentni Ism bo'yicha Qidirish *</label>
              <div class="searchable-select-wrap">
                <input
                  v-model="returnAgentSearchQuery"
                  type="text"
                  class="finput search-input-field"
                  placeholder="Agent ismini kiriting..."
                  @focus="showReturnAgentDropdown = true"
                  @keydown="onReturnAgentKeydown"
                />
                <div v-if="showReturnAgentDropdown" class="dropdown-options-list">
                  <div
                    v-for="(ag, idx) in filteredReturnAgents"
                    :key="ag.id"
                    class="dropdown-option-item"
                    :class="{ selected: returnForm.agent === ag.id, highlighted: returnAgentKb.highlightedIndex.value === idx }"
                    @click="selectReturnAgent(ag)"
                  >
                    <div class="opt-name">👤 {{ ag.full_name }}</div>
                    <div class="opt-sub">{{ ag.phone || 'No phone' }}</div>
                  </div>
                  <div v-if="filteredReturnAgents.length === 0" class="dropdown-empty">
                    Mos agent topilmadi
                  </div>
                </div>
              </div>
              <div v-if="selectedReturnAgentLabel" class="selected-chip red-chip">
                Tanlandi: <strong>{{ selectedReturnAgentLabel }}</strong>
              </div>
            </div>

            <!-- Amount Input -->
            <div class="form-group">
              <label class="flabel required">Qaytarilayotgan Summa *</label>
              <input
                v-model="returnForm.amountFormatted"
                type="text"
                class="finput amount-input red-text"
                placeholder="0"
                required
                @input="onReturnAmountInput"
              />
            </div>

            <!-- Method Select -->
            <div class="form-group">
              <label class="flabel required">Qaytarish Usuli *</label>
              <div class="select-wrap-relative">
                <select v-model="returnForm.method" class="fselect-field">
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
              <label class="flabel">Qaytarish Sababi / Izoh</label>
              <input v-model="returnForm.notes" type="text" class="finput" placeholder="Masalan: Bekor qilingan o'quvchi uchun bonus qaytarildi..." />
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-cancel" @click="closeReturnModal">Bekor qilish</button>
              <button type="submit" class="btn-save btn-red-save" :disabled="returnSaving">
                {{ returnSaving ? "Saqlanmoqda..." : "Qaytarishni Saqlash" }}
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
      Haqiqatan ham <strong>#{{ deletingPayment?.id }}</strong> raqamli bonus to'lovini o'chirmoqchimisiz?
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
import { formatMoney, formatDate } from '@/utils/formatters'
import { useSearchSelectKeyboard } from '@/composables/useSearchSelectKeyboard'

const authStore = useAuthStore()
const router = useRouter()

function goStudent(id) {
  if (!id) return
  router.push(`/students/${id}`)
}

function goAgent(id) {
  if (!id) return
  router.push(`/agents/${id}`)
}

const payments = ref([])
const enrollments = ref([])
const agents = ref([])
const categories = ref([])
const groups = ref([])
const loading = ref(true)
const totalCount = ref(0)

// Payments only carry the group's name (not its id), so map by name here.
const groupsByName = computed(() => {
  const map = {}
  groups.value.forEach(g => { map[g.name] = g })
  return map
})

async function fetchGroups() {
  try {
    const res = await api.get('/groups/', { params: { page_size: 1000 } })
    groups.value = res.data.results || res.data
  } catch (err) { console.error(err) }
}

const filterAgentName = ref('')
const filterAgent = ref('')
const filterCategory = ref('')
const filterDateFrom = ref('')
const filterDateTo = ref('')
const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const saving = ref(false)
const modalError = ref(null)

const agentSearchQuery = ref('')
const showAgentDropdown = ref(false)
const selectedAgentLabel = ref('')

const studentSearchQuery = ref('')
const showStudentDropdown = ref(false)
const selectedStudentLabel = ref('')

const form = ref({ agent: '', enrollment: '', amountFormatted: '', amount: 0, method: 'cash', notes: '' })

// Return Bonus Modal State
const showReturnModal = ref(false)
const returnSaving = ref(false)
const returnModalError = ref(null)
const returnAgentSearchQuery = ref('')
const showReturnAgentDropdown = ref(false)
const selectedReturnAgentLabel = ref('')
const returnForm = ref({ agent: '', amountFormatted: '', amount: 0, method: 'cash', notes: '' })

const metrics = computed(() => {
  const total = payments.value.reduce((s, p) => s + (p.amount || 0), 0)
  return { total }
})

const filteredAgents = computed(() => {
  const q = agentSearchQuery.value.toLowerCase().trim()
  if (!q) return agents.value
  return agents.value.filter(ag => (ag.full_name || '').toLowerCase().includes(q))
})

const filteredReturnAgents = computed(() => {
  const q = returnAgentSearchQuery.value.toLowerCase().trim()
  if (!q) return agents.value
  return agents.value.filter(ag => (ag.full_name || '').toLowerCase().includes(q))
})

const filteredEnrollments = computed(() => {
  const q = studentSearchQuery.value.toLowerCase().trim()
  if (!q) return enrollments.value
  return enrollments.value.filter(e => (e.student_name || '').toLowerCase().includes(q))
})

async function fetchPayments() {
  loading.value = true
  try {
    const params = { status: 'bonus', page_size: 1000 }
    if (filterAgentName.value) params.student_name = filterAgentName.value.trim()
    if (filterAgent.value) params.agent = filterAgent.value
    if (filterCategory.value) params.category = filterCategory.value
    if (filterDateFrom.value) params.date_from = filterDateFrom.value
    if (filterDateTo.value) params.date_to = filterDateTo.value

    const res = await api.get('/payments/', { params })
    payments.value = res.data.results || res.data
    totalCount.value = res.data.count || payments.value.length
  } catch (err) { console.error(err) }
  finally { loading.value = false }
}

async function fetchEnrollments() {
  try {
    const res = await api.get('/enrollments/', { params: { page_size: 1000 } })
    enrollments.value = res.data.results || res.data
  } catch (err) { console.error(err) }
}

async function fetchAgents() {
  try {
    const res = await api.get('/agents/')
    agents.value = res.data.results || res.data
  } catch (err) { console.error(err) }
}

async function fetchCategories() {
  try {
    const res = await api.get('/categories/')
    categories.value = res.data.results || res.data
  } catch (err) { console.error(err) }
}

watch([filterAgentName, filterAgent, filterCategory, filterDateFrom, filterDateTo], () => { fetchPayments() })

function selectAgent(ag) {
  form.value.agent = ag.id
  selectedAgentLabel.value = `${ag.full_name} (${ag.phone || 'No phone'})`
  agentSearchQuery.value = ag.full_name
  showAgentDropdown.value = false
}
const agentKb = useSearchSelectKeyboard()
function onAgentKeydown(e) {
  agentKb.onKeydown(e, filteredAgents.value, selectAgent, () => { showAgentDropdown.value = false })
}

function selectReturnAgent(ag) {
  returnForm.value.agent = ag.id
  selectedReturnAgentLabel.value = `${ag.full_name} (${ag.phone || 'No phone'})`
  returnAgentSearchQuery.value = ag.full_name
  showReturnAgentDropdown.value = false
}
const returnAgentKb = useSearchSelectKeyboard()
function onReturnAgentKeydown(e) {
  returnAgentKb.onKeydown(e, filteredReturnAgents.value, selectReturnAgent, () => { showReturnAgentDropdown.value = false })
}

function selectEnrollment(e) {
  form.value.enrollment = e.id
  selectedStudentLabel.value = `${e.student_name} (${e.category_name})`
  studentSearchQuery.value = e.student_name
  showStudentDropdown.value = false
}
const studentKb = useSearchSelectKeyboard()
function onStudentKeydown(e) {
  studentKb.onKeydown(e, filteredEnrollments.value, selectEnrollment, () => { showStudentDropdown.value = false })
}

function methodText(m) {
  switch (m) {
    case 'cash': return 'Naqd'
    case 'card': return 'Karta'
    case 'qr_code': return 'QR code'
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

function onReturnAmountInput(e) {
  const digits = e.target.value.replace(/\D/g, '')
  if (!digits) { returnForm.value.amount = 0; returnForm.value.amountFormatted = ''; return }
  const num = parseInt(digits, 10)
  returnForm.value.amount = num
  returnForm.value.amountFormatted = formatMoney(num, false)
}

function openCreateModal() {
  isEditing.value = false
  editingId.value = null
  modalError.value = null
  agentSearchQuery.value = ''
  selectedAgentLabel.value = ''
  showAgentDropdown.value = false
  studentSearchQuery.value = ''
  selectedStudentLabel.value = ''
  showStudentDropdown.value = false
  form.value = { agent: '', enrollment: '', amountFormatted: '', amount: 0, method: 'cash', notes: '' }
  showModal.value = true
}

function openReturnModal() {
  returnModalError.value = null
  returnAgentSearchQuery.value = ''
  selectedReturnAgentLabel.value = ''
  showReturnAgentDropdown.value = false
  returnForm.value = { agent: '', amountFormatted: '', amount: 0, method: 'cash', notes: '' }
  showReturnModal.value = true
}

function closeReturnModal() { showReturnModal.value = false }

function openEditModal(p) {
  isEditing.value = true
  editingId.value = p.id
  modalError.value = null
  form.value = { agent: p.agent, enrollment: p.enrollment, amountFormatted: formatMoney(p.amount, false), amount: p.amount, method: p.method || 'cash', notes: p.notes || '' }
  showModal.value = true
}

function closeModal() { showModal.value = false }

async function savePayment() {
  if (!isEditing.value && !form.value.agent) { modalError.value = "Agentni tanlang."; return }
  if (!form.value.amount || form.value.amount <= 0) { modalError.value = "To'g'ri bonus summasini kiriting."; return }
  saving.value = true
  modalError.value = null
  try {
    if (isEditing.value) {
      await api.patch(`/payments/${editingId.value}/`, { amount: form.value.amount, method: form.value.method, notes: form.value.notes })
    } else {
      await api.post('/payments/', {
        user: authStore.user?.id,
        agent: form.value.agent,
        enrollment: form.value.enrollment || null,
        amount: form.value.amount,
        status: 'bonus',
        method: form.value.method,
        notes: form.value.notes
      })
    }
    closeModal()
    fetchPayments()
  } catch (err) { modalError.value = err.response?.data?.detail || "Saqlashda xatolik yuz berdi" }
  finally { saving.value = false }
}

async function saveReturnBonus() {
  if (!returnForm.value.agent) { returnModalError.value = "Agentni tanlang."; return }
  if (!returnForm.value.amount || returnForm.value.amount <= 0) { returnModalError.value = "To'g'ri summani kiriting."; return }
  returnSaving.value = true
  returnModalError.value = null
  try {
    await api.post('/payments/', {
      user: authStore.user?.id,
      agent: returnForm.value.agent,
      amount: returnForm.value.amount,
      status: 'returned',
      method: returnForm.value.method,
      notes: `Agent bonus qaytarishi: ${returnForm.value.notes || ''}`
    })
    closeReturnModal()
    fetchPayments()
  } catch (err) { returnModalError.value = err.response?.data?.detail || "Saqlashda xatolik yuz berdi" }
  finally { returnSaving.value = false }
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

onMounted(() => { fetchPayments(); fetchEnrollments(); fetchAgents(); fetchCategories(); fetchGroups() })
</script>

<style scoped>
.page-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-main-title { font-size: 22px; font-weight: 700; color: #111827; }
.page-sub-title { font-size: 13px; color: #6B7280; margin-top: 2px; }

.btn-primary-action { display: inline-flex; align-items: center; gap: 8px; padding: 11px 20px; border-radius: 12px; font-weight: 700; font-size: 13.5px; cursor: pointer; transition: all 0.2s ease; }
.btn-gold { background: linear-gradient(135deg, #D97706 0%, #B45309 100%); color: white; box-shadow: 0 4px 14px rgba(217, 119, 6, 0.25); &:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(217, 119, 6, 0.35); } }
.btn-red-action { background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%); color: white; box-shadow: 0 4px 14px rgba(220, 38, 38, 0.25); &:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(220, 38, 38, 0.35); } }

.metrics-cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; }
.card-metric { background: white; border: 1.5px solid #E5E7EB; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); }
.card-metric-icon { font-size: 30px; }
.metric-lbl { font-size: 12.5px; color: #6B7280; font-weight: 600; }
.metric-val { font-size: 18px; font-weight: 800; color: #111827; margin-top: 4px; }
.text-gold { color: #D97706; font-weight: 800; }
.text-amber { color: #B45309; font-weight: 800; }
.margin-top { margin-top: 24px; }

.table-section-card { background: white; border: 1px solid #E5E7EB; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.toolbar-bar { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid #E5E7EB; gap: 16px; flex-wrap: wrap; }
.search-box { display: flex; align-items: center; gap: 10px; background: #F9FAFB; border: 1.5px solid #E5E7EB; border-radius: 10px; padding: 9px 14px; width: 300px; }
.search-input { border: none; background: transparent; outline: none; font-size: 13.5px; width: 100%; }
.filter-controls { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.filter-item { display: flex; align-items: center; gap: 6px; }
.filter-item .select-wrap-relative { width: 170px; }
.finput-date { padding: 8px 12px; border: 1.5px solid #E5E7EB; border-radius: 10px; font-size: 13px; background: #FAFAFA; outline: none; }
.total-count { font-size: 13px; color: #6B7280; white-space: nowrap; }
.table-container { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; th { background: #F9FAFB; padding: 13px 16px; font-size: 12px; font-weight: 700; color: #4B5563; text-align: left; border-bottom: 1px solid #E5E7EB; } td { padding: 14px 16px; font-size: 13.5px; color: #1F2937; border-bottom: 1px solid #F3F4F6; vertical-align: middle; } }
.agent-name { font-weight: 700; color: #D97706; }
.link-value { cursor: pointer; }
.link-value:hover { text-decoration: underline; }
.agent-phone { font-size: 11.5px; color: #6B7280; margin-top: 2px; }
.student-name { font-weight: 600; color: #111827; }
.group-sub { font-size: 11.5px; color: #6B7280; margin-top: 2px; }
.group-dates { font-size: 13px; font-weight: 600; color: #374151; margin-top: 4px; white-space: nowrap; }
.student-jshshr { font-size: 11.5px; color: #6B7280; margin-top: 2px; }
.cat-pill { padding: 4px 10px; background: #FEF3C7; color: #92400E; border-radius: 8px; font-size: 12px; font-weight: 700; }
.method-chip { padding: 4px 12px; background: #F3F4F6; color: #374151; border-radius: 20px; font-size: 12px; font-weight: 600; }
.row-actions { display: flex; gap: 8px; justify-content: flex-end; }
.btn-action-edit, .btn-action-delete { width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; border: 1px solid #E5E7EB; background: #F9FAFB; cursor: pointer; transition: all 0.15s ease; }
.btn-action-edit { color: #2563EB; &:hover { background: #EFF6FF; border-color: #BFDBFE; transform: translateY(-1px); } }
.btn-action-delete { color: #EF4444; &:hover { background: #FEE2E2; border-color: #FCA5A5; transform: translateY(-1px); } }
.state-box, .empty-state { text-align: center; padding: 40px 0; color: #6B7280; }
.spinner { width: 28px; height: 28px; border: 3px solid #E5E7EB; border-top-color: #D97706; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px; }
@keyframes spin { to { transform: rotate(360deg); } }

.modal-overlay { position: fixed; inset: 0; z-index: 1000; background: rgba(15, 23, 42, 0.65); backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-card { background: white; border-radius: 20px; width: 100%; max-width: 500px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); }
.modal-header-banner { padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #F3F4F6; &.gold-banner { background: linear-gradient(180deg, #FEF3C7 0%, #FFFFFF 100%); } &.red-banner { background: linear-gradient(180deg, #FEE2E2 0%, #FFFFFF 100%); } }
.header-left-info { display: flex; align-items: center; gap: 12px; h3 { font-size: 17px; font-weight: 700; color: #111827; } p { font-size: 12px; color: #6B7280; margin-top: 2px; } }
.header-icon-box { width: 42px; height: 42px; border-radius: 12px; color: white; display: flex; align-items: center; justify-content: center; &.gold-box { background: linear-gradient(135deg, #D97706 0%, #B45309 100%); } &.red-box { background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%); } }
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
  &:focus { border-color: #D97706; background-color: #FFFFFF; box-shadow: 0 0 0 3.5px rgba(217, 119, 6, 0.12); }
}

.select-wrap-relative { position: relative; width: 100%; }
.select-chevron-icon { position: absolute; right: 14px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #9CA3AF; font-size: 10px; }

.searchable-select-wrap { position: relative; width: 100%; }
.dropdown-options-list { position: absolute; top: 100%; left: 0; right: 0; max-height: 200px; overflow-y: auto; background: white; border: 1.5px solid #D97706; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); z-index: 50; margin-top: 4px; }
.dropdown-option-item { padding: 10px 14px; cursor: pointer; border-bottom: 1px solid #F3F4F6; &:hover { background: #FEF3C7; } &.selected { background: #FDE68A; font-weight: 700; } &.highlighted { background: #FEF3C7; } }
.opt-name { font-size: 13.5px; font-weight: 600; color: #111827; }
.opt-sub { font-size: 11.5px; color: #6B7280; margin-top: 1px; }
.dropdown-empty { padding: 12px; text-align: center; color: #9CA3AF; font-size: 13px; }
.selected-chip { font-size: 12.5px; color: #D97706; margin-top: 6px; &.red-chip { color: #DC2626; } }

.amount-input.gold-text { font-size: 16.5px; font-weight: 800; color: #B45309; }
.amount-input.red-text { font-size: 16.5px; font-weight: 800; color: #DC2626; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.btn-cancel { padding: 10px 18px; border: 1px solid #D1D5DB; background: white; border-radius: 10px; font-weight: 600; font-size: 13px; color: #374151; cursor: pointer; }
.btn-gold-save { padding: 10px 22px; background: linear-gradient(135deg, #D97706 0%, #B45309 100%); color: white; border-radius: 10px; font-weight: 700; font-size: 13.5px; cursor: pointer; }
.btn-red-save { padding: 10px 22px; background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%); color: white; border-radius: 10px; font-weight: 700; font-size: 13.5px; cursor: pointer; }
.alert-error { background: #FEE2E2; color: #991B1B; padding: 10px 14px; border-radius: 10px; font-size: 13px; margin-bottom: 16px; }
</style>
