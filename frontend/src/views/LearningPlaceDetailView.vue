<template>
  <AppLayout>

    <!-- Header -->
    <div class="page-top">
      <div class="top-left">
        <button class="btn-back" @click="$router.back()" title="Orqaga">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="18" height="18">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
        <div>
          <h2 class="page-main-title">{{ place?.place_name || "O'quv Joyi" }}</h2>
          <p class="page-sub-title">O'quv joyi ma'lumotlari va biriktirilgan o'quvchilar</p>
        </div>
      </div>
    </div>

    <div v-if="loading" class="state-box">
      <div class="spinner"></div>
      <span>Yuklanmoqda...</span>
    </div>

    <div v-else-if="error" class="state-box state-error">
      <p>{{ error }}</p>
      <button class="btn-retry" @click="fetchAll">Qayta urinish</button>
    </div>

    <template v-else>
      <!-- Place info -->
      <div class="info-card">
        <h3 class="section-title">O'quv Joyi Ma'lumotlari</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-lbl">ID</span>
            <span class="info-val">#{{ place?.id }}</span>
          </div>
          <div class="info-item">
            <span class="info-lbl">Nomi</span>
            <span class="info-val">{{ place?.place_name || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-lbl">Filial</span>
            <span class="info-val">{{ place?.branch_name || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-lbl">Yaratilgan sana</span>
            <span class="info-val">{{ formatDate(place?.created_at) }}</span>
          </div>
          <div class="info-item">
            <span class="info-lbl">Holati</span>
            <span class="info-val">
              <span class="status-chip" :class="place?.is_active ? 'chip-ok' : 'chip-off'">
                {{ place?.is_active ? 'Faol' : 'Nofaol' }}
              </span>
            </span>
          </div>
        </div>
      </div>

      <!-- Metric cards -->
      <div class="metrics-cards-grid">
        <div class="card-metric card-indigo">
          <div class="card-metric-icon">👨‍🏫</div>
          <div>
            <span class="metric-lbl">Faol O'qituvchilar</span>
            <h4 class="metric-val text-indigo">{{ activeTeachersCount }} ta o'qituvchi</h4>
          </div>
        </div>

        <div class="card-metric card-purple">
          <div class="card-metric-icon">🚘</div>
          <div>
            <span class="metric-lbl">Faol Instruktorlar</span>
            <h4 class="metric-val text-purple">{{ activeInstructorsCount }} ta instruktor</h4>
          </div>
        </div>

        <div class="card-metric card-blue">
          <div class="card-metric-icon">🎓</div>
          <div>
            <span class="metric-lbl">Faol</span>
            <h4 class="metric-val text-blue">{{ activeCount }} ta o'quvchi</h4>
          </div>
        </div>

        <div class="card-metric card-emerald">
          <div class="card-metric-icon">💰</div>
          <div>
            <span class="metric-lbl">Jami To'langan</span>
            <h4 class="metric-val text-emerald">{{ formatMoney(totalPaid) }}</h4>
          </div>
        </div>

        <div class="card-metric card-red">
          <div class="card-metric-icon">⚠️</div>
          <div>
            <span class="metric-lbl">Jami Qarzdorlik</span>
            <h4 class="metric-val text-red">{{ formatMoney(totalDebt) }}</h4>
          </div>
        </div>
      </div>

      <!-- Students table -->
      <div class="table-section-card">
        <div class="toolbar-bar">
          <h3 class="section-title">O'quvchilar Ro'yxati</h3>
          <div class="total-count">
            Jami: <strong>{{ filteredEnrollments.length }}</strong> ta
          </div>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>O'quvchi F.I.SH.</th>
                <th>Kategoriya</th>
                <th>Guruh</th>
                <th>Guruh boshlanishi</th>
                <th>Guruh tugashi</th>
                <th>Instruktor</th>
                <th>O'qituvchi</th>
                <th>O'quv vaqti</th>
                <th>Dars kunlari</th>
                <th>Shartnoma</th>
                <th>To'langan</th>
                <th>Qarzdorlik</th>
                <th>Holati</th>
                <th>Izoh</th>
              </tr>
              <tr class="col-filter-row">
                <th>
                  <input v-model="filterStudentName" class="col-filter-input" type="text" placeholder="Ism bo'yicha qidirish..." />
                </th>
                <th>
                  <div class="select-wrap-relative">
                    <select v-model="filterCategory" class="col-filter-select">
                      <option value="">Barchasi</option>
                      <option v-for="c in categoryOptions" :key="c.id" :value="c.id">{{ c.name }}</option>
                    </select>
                  </div>
                </th>
                <th>
                  <input v-model="filterGroupName" class="col-filter-input" type="text" placeholder="Guruh nomi..." />
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
                    <button v-if="groupStartFrom || groupStartTo" type="button" class="btn-clear-date" @click="groupStartFrom = ''; groupStartTo = ''" title="Tozalash">✕</button>
                  </div>
                  <div class="col-date-range">
                    <input v-model="groupStartFrom" type="date" class="col-date-input" title="Guruh boshlanishi (dan)" />
                    <input v-model="groupStartTo" type="date" class="col-date-input" title="Guruh boshlanishi (gacha)" />
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
                    <button v-if="groupEndFrom || groupEndTo" type="button" class="btn-clear-date" @click="groupEndFrom = ''; groupEndTo = ''" title="Tozalash">✕</button>
                  </div>
                  <div class="col-date-range">
                    <input v-model="groupEndFrom" type="date" class="col-date-input" title="Guruh tugashi (dan)" />
                    <input v-model="groupEndTo" type="date" class="col-date-input" title="Guruh tugashi (gacha)" />
                  </div>
                </th>
                <th></th>
                <th></th>
                <th></th>
                <th></th>
                <th></th>
                <th></th>
                <th>
                  <div class="select-wrap-relative">
                    <select v-model="filterDebt" class="col-filter-select">
                      <option value="">Barchasi</option>
                      <option value="has">Bor</option>
                      <option value="none">Yo'q</option>
                    </select>
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
              </tr>
            </thead>
            <tbody>
              <tr v-for="e in displayedEnrollments" :key="e.id" class="table-row">
                <td class="td-name">
                  <div class="student-name-link" @click="goStudent(e.student)">{{ e.student_name || "Noma'lum" }}</div>
                </td>
                <td><span class="cat-badge">{{ e.category_name || '-' }}</span></td>
                <td>
                  <span v-if="e.group_name" class="group-pill link-value" @click="goGroup(e.group)">{{ e.group_name }}</span>
                  <span v-else>-</span>
                </td>
                <td class="td-muted td-date">{{ groupsById[e.group] ? formatDate(groupsById[e.group].started_at) : '-' }}</td>
                <td class="td-muted td-date">{{ groupsById[e.group] ? formatDate(groupsById[e.group].ends_at) : '-' }}</td>
                <td class="td-muted">
                  <span v-if="e.instructor" class="link-value" @click="goUser(e.instructor)">{{ e.instructor_name || '-' }}</span>
                  <span v-else>{{ e.instructor_name || '-' }}</span>
                </td>
                <td class="td-muted">
                  <span v-if="e.coordinator" class="link-value" @click="goUser(e.coordinator)">{{ e.coordinator_name || '-' }}</span>
                  <span v-else>{{ e.coordinator_name || '-' }}</span>
                </td>
                <td class="td-muted">{{ e.learning_time || '-' }}</td>
                <td class="td-muted td-days">{{ daysText(e.learning_days) }}</td>
                <td class="td-amount">
                  <span v-if="e.enrolled_free" class="free-chip">Tekin</span>
                  <span v-else>{{ formatMoney(e.enrolled_amount) }}</span>
                </td>
                <td class="td-amount text-green">{{ formatMoney(e.paid_amount || 0) }}</td>
                <td class="td-amount">
                  <span v-if="getDebt(e) > 0" class="debt-chip">-{{ formatMoney(getDebt(e)) }}</span>
                  <span v-else class="paid-chip">To'langan</span>
                </td>
                <td>
                  <span class="status-chip" :class="e.status">{{ statusText(e.status) }}</span>
                </td>
                <td>{{ e.notes || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="filteredEnrollments.length > 0" class="pagination-bar">
          <span class="pagination-info">
            Jami: <strong>{{ filteredEnrollments.length }}</strong> tadan <strong>{{ displayedEnrollments.length }}</strong> ko'rsatilmoqda
          </span>
          <div class="pagination-actions">
            <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">Oldingi</button>
            <span v-if="pageSizeOption !== 'all'" class="page-num">Sahifa {{ Math.min(currentPage, displayTotalPages) }} / {{ displayTotalPages }}</span>
            <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === displayTotalPages" @click="changePage(currentPage + 1)">Keyingi</button>
            <label class="page-size-label" for="place-enr-page-size">Ko'rsatish:</label>
            <div class="select-wrap-relative">
              <select id="place-enr-page-size" v-model="pageSizeOption" class="page-size-select">
                <option value="50">50</option>
                <option value="100">100</option>
                <option value="200">200</option>
                <option value="all">Barchasi</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </template>

  </AppLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { formatMoney, formatDate } from '@/utils/formatters'

const route = useRoute()
const router = useRouter()

const place = ref(null)
const enrollments = ref([])
const groups = ref([])
const loading = ref(true)

const groupsById = computed(() => {
  const map = {}
  groups.value.forEach(g => { map[g.id] = g })
  return map
})
const error = ref('')
const filterStudentName = ref('')
const filterStatus = ref('')
const filterCategory = ref('')
const filterGroupName = ref('')
const filterDebt = ref('')
const groupStartSort = ref('')
const groupEndSort = ref('')
const groupStartFrom = ref('')
const groupStartTo = ref('')
const groupEndFrom = ref('')
const groupEndTo = ref('')

// ── Row-fetch-count selector ──────────────────────────────────
// Replaces classic next/prev pagination: fetch always pulls every
// enrollment for this learning place (see fetchAll below), filtering runs
// client-side against the full set (filteredEnrollments), and
// pageSizeOption instead controls how many of the *filtered* results are
// shown per page (see displayedEnrollments/changePage below).
const pageSizeOption = ref('50')
const totalCount = ref(0)
const currentPage = ref(1)

function setSort(field, dir) {
  const target = field === 'groupStart' ? groupStartSort : groupEndSort
  const other = field === 'groupStart' ? groupEndSort : groupStartSort
  other.value = ''
  target.value = target.value === dir ? '' : dir
}

const getDebt = (e) => {
  if (!e || e.enrolled_free) return 0
  const contract = Number(e.enrolled_amount) || 0
  const paid = Number(e.paid_amount) || 0
  return Math.max(0, contract - paid)
}

// Distinct category options among this place's own enrollments — no point
// offering a filter value that would match nothing here.
const categoryOptions = computed(() => {
  const map = {}
  enrollments.value.forEach(e => {
    if (e.category && !map[e.category]) map[e.category] = { id: e.category, name: e.category_name || `#${e.category}` }
  })
  return Object.values(map).sort((a, b) => a.name.localeCompare(b.name))
})

// "Active" teachers/instructors: distinct coordinators/instructors drawn
// from this place's students, excluding only canceled enrolments — a
// student who is new or already finished the course still counts toward
// their teacher/instructor's active roster here.
const activeTeachersCount = computed(() => {
  const ids = new Set()
  enrollments.value.forEach(e => { if (e.status !== 'canceled' && e.coordinator) ids.add(e.coordinator) })
  return ids.size
})
const activeInstructorsCount = computed(() => {
  const ids = new Set()
  enrollments.value.forEach(e => { if (e.status !== 'canceled' && e.instructor) ids.add(e.instructor) })
  return ids.size
})

// Metric cards reflect the active filters, not the place's full roster.
const activeCount = computed(() => filteredEnrollments.value.filter(e => e.status === 'enrolled').length)
const totalPaid = computed(() => filteredEnrollments.value.reduce((s, e) => s + (Number(e.paid_amount) || 0), 0))
const totalDebt = computed(() => filteredEnrollments.value.reduce((s, e) => s + getDebt(e), 0))

const filteredEnrollments = computed(() => {
  const q = filterStudentName.value.toLowerCase().trim()

  const groupQ = filterGroupName.value.toLowerCase().trim()

  const rows = enrollments.value.filter(e => {
    if (filterStatus.value && e.status !== filterStatus.value) return false
    if (filterCategory.value && e.category !== filterCategory.value) return false
    if (filterDebt.value === 'has' && getDebt(e) <= 0) return false
    if (filterDebt.value === 'none' && getDebt(e) > 0) return false
    if (q && !(e.student_name || '').toLowerCase().includes(q)) return false
    if (groupQ && !(e.group_name || '').toLowerCase().includes(groupQ)) return false
    const grp = groupsById.value[e.group]
    if (groupStartFrom.value && !(grp && grp.started_at && grp.started_at >= groupStartFrom.value)) return false
    if (groupStartTo.value && !(grp && grp.started_at && grp.started_at <= groupStartTo.value)) return false
    if (groupEndFrom.value && !(grp && grp.ends_at && grp.ends_at >= groupEndFrom.value)) return false
    if (groupEndTo.value && !(grp && grp.ends_at && grp.ends_at <= groupEndTo.value)) return false
    return true
  })

  const field = groupStartSort.value ? 'started_at' : (groupEndSort.value ? 'ends_at' : null)
  if (!field) return rows

  const dir = (groupStartSort.value || groupEndSort.value) === 'asc' ? 1 : -1
  return rows.slice().sort((a, b) => {
    const ga = groupsById.value[a.group]
    const gb = groupsById.value[b.group]
    const ta = ga && ga[field] ? new Date(ga[field]).getTime() : null
    const tb = gb && gb[field] ? new Date(gb[field]).getTime() : null
    if (ta === null && tb === null) return 0
    if (ta === null) return 1
    if (tb === null) return -1
    return (ta - tb) * dir
  })
})

// pageSizeOption now purely controls how many of the *filtered* rows show
// per page — currentPage is clamped here (not via a watcher enumerating
// every filter ref) so it self-corrects the moment a filter shrinks the
// result set out from under it.
const displayPageSize = computed(() => pageSizeOption.value === 'all' ? Infinity : Number(pageSizeOption.value))
const displayTotalPages = computed(() => {
  if (pageSizeOption.value === 'all') return 1
  return Math.max(1, Math.ceil(filteredEnrollments.value.length / displayPageSize.value))
})
const displayedEnrollments = computed(() => {
  if (pageSizeOption.value === 'all') return filteredEnrollments.value
  const page = Math.min(currentPage.value, displayTotalPages.value)
  const start = (page - 1) * displayPageSize.value
  return filteredEnrollments.value.slice(start, start + displayPageSize.value)
})
function changePage(page) {
  if (page < 1 || page > displayTotalPages.value) return
  currentPage.value = page
}

// This view has no scope-narrowing tabs, so nothing ever needs a refetch
// after the initial load — the row-fetch-count selector only resets the
// display page.
watch(pageSizeOption, () => {
  currentPage.value = 1
})

const weekdayShortNames = ['Dush', 'Sesh', 'Chor', 'Pay', 'Juma', 'Shan']
function daysText(d) {
  if (Array.isArray(d)) {
    if (d.length === 0) return '-'
    if (d.length === 6) return 'Har kuni (Dush-Shan)'
    return [...d].sort((a, b) => a - b).map(v => weekdayShortNames[v] || v).join(' - ')
  }
  switch (d) {
    case 'Mo-Wed-Fri': return 'Dush - Chor - Juma'
    case 'Tue-Thu-Sat': return 'Sesh - Pay - Shan'
    case 'everyday': return 'Har kuni (Dush-Shan)'
    default: return d || '-'
  }
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

function goStudent(id) {
  if (id) router.push(`/students/${id}`)
}

function goUser(id) {
  if (id) router.push(`/users/${id}`)
}

function goGroup(id) {
  if (id) router.push(`/groups/${id}`)
}

async function fetchAll() {
  loading.value = true
  error.value = ''
  try {
    const [placeRes, enrRes, groupsRes] = await Promise.all([
      api.get(`/learning-places/${route.params.id}/`),
      // Always the full place-scoped dataset — filtering/sorting/pagination
      // above all need to see every row, not just one page of them.
      api.get('/enrollments/', { params: { learning_place: route.params.id, page_size: 100000 } }),
      // Groups are only used to look up start/end dates for the rows above,
      // not displayed as their own list — always fetch the full set.
      api.get('/groups/', { params: { page_size: 1000 } }),
    ])
    place.value = placeRes.data
    enrollments.value = enrRes.data.results ? enrRes.data.results : enrRes.data
    totalCount.value = enrRes.data.count ?? enrollments.value.length
    groups.value = groupsRes.data.results ? groupsRes.data.results : groupsRes.data
  } catch (err) {
    console.error(err)
    error.value = "O'quv joyi ma'lumotlarini yuklashda xatolik yuz berdi."
  } finally {
    loading.value = false
  }
}

onMounted(fetchAll)
</script>

<style scoped>
.page-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; gap: 16px; flex-wrap: wrap; }
.top-left { display: flex; align-items: center; gap: 14px; }
.page-main-title { font-size: 22px; font-weight: 700; color: #111827; }
.page-sub-title { font-size: 13px; color: #6B7280; margin-top: 2px; }

.btn-back {
  display: flex; align-items: center; justify-content: center;
  width: 38px; height: 38px; border-radius: 10px;
  background: white; border: 1px solid #E5E7EB; color: #4B5563;
  cursor: pointer; transition: all 0.15s ease; flex-shrink: 0;
}
.btn-back:hover { background: #F3F4F6; color: #111827; }

.metrics-cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; margin-bottom: 24px; }
.card-metric { background: white; border: 1.5px solid #E5E7EB; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); }
.card-metric-icon { font-size: 30px; }
.metric-lbl { font-size: 12.5px; color: #6B7280; font-weight: 600; }
.metric-val { font-size: 18px; font-weight: 800; color: #111827; margin-top: 4px; }
.text-green { color: #166534; }
.text-blue { color: #2563EB; }
.text-emerald { color: #2D6A4F; }
.text-red { color: #DC2626; }
.text-indigo { color: #4338CA; }
.text-purple { color: #7C3AED; }

.info-card { background: white; border: 1px solid #E5E7EB; border-radius: 16px; padding: 20px 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.section-title { font-size: 15px; font-weight: 700; color: #111827; margin-bottom: 14px; }
.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; }
.info-item { display: flex; flex-direction: column; gap: 4px; }
.info-lbl { font-size: 12px; color: #6B7280; font-weight: 600; }
.info-val { font-size: 14px; color: #111827; font-weight: 600; }

.table-section-card { background: white; border: 1px solid #E5E7EB; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.toolbar-bar { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid #E5E7EB; gap: 16px; flex-wrap: wrap; }
.toolbar-bar .section-title { margin-bottom: 0; }
.total-count { font-size: 13px; color: #6B7280; }

.select-wrap-relative { position: relative; width: 100%; }

.td-date { white-space: nowrap; }
.td-days { white-space: nowrap; }

/* Bounded, independently-scrolling table body so the header (both the
   label row and the column-filter row) sticks to the top of this
   container as rows scroll underneath, instead of scrolling away with
   the page. */
.table-container { overflow: auto; max-height: 600px; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: #F9FAFB; padding: 13px 16px; font-size: 12px; font-weight: 700; color: #4B5563; text-align: left; border-bottom: 1px solid #E5E7EB; white-space: nowrap; }
.data-table td { padding: 14px 16px; font-size: 13.5px; color: #1F2937; border-bottom: 1px solid #F3F4F6; vertical-align: middle; }
.data-table thead { position: sticky; top: 0; z-index: 3; }
.data-table thead tr.col-filter-row th { padding: 8px 10px; background: #FAFAFB; border-bottom: 1px solid #E5E7EB; }

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
.col-date-range { display: flex; gap: 4px; margin-top: 6px; }
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

.link-value { cursor: pointer; color: #2563EB; font-weight: 600; text-decoration: underline; }
.link-value:hover { color: #1D4ED8; text-decoration: underline; }

.student-name-link { font-weight: 700; color: #111827; cursor: pointer; }
.student-name-link:hover { color: #2D6A4F; text-decoration: underline; }
.td-muted { color: #6B7280; }
.td-amount { font-weight: 600; white-space: nowrap; }
.cat-badge { padding: 3px 8px; background: #E8F5E9; color: #2D6A4F; border-radius: 6px; font-size: 12px; font-weight: 700; }
.group-pill { padding: 3px 8px; background: #EFF6FF; color: #2563EB; border-radius: 6px; font-size: 12px; font-weight: 600; }
.debt-chip { padding: 4px 10px; background: #FEE2E2; color: #991B1B; border-radius: 8px; font-size: 12.5px; font-weight: 700; display: inline-block; }
.paid-chip { padding: 4px 10px; background: #DCFCE7; color: #15803D; border-radius: 8px; font-size: 12.5px; font-weight: 700; display: inline-block; }
.free-chip { padding: 4px 10px; background: #EDE9FE; color: #6D28D9; border-radius: 8px; font-size: 12.5px; font-weight: 700; display: inline-block; }

.status-chip { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11.5px; font-weight: 600; }
.status-chip.enrolled { background: #DCFCE7; color: #15803D; }
.status-chip.new { background: #E0F2FE; color: #0369A1; }
.status-chip.finished { background: #F3F4F6; color: #4B5563; }
.status-chip.canceled { background: #FEE2E2; color: #B91C1C; }
.status-chip.chip-ok { background: #DCFCE7; color: #15803D; }
.status-chip.chip-off { background: #F3F4F6; color: #4B5563; }

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

.state-box { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 20px; gap: 12px; background: white; border-radius: 16px; color: #6B7280; }
.state-error p { color: #DC2626; }
.empty-state { text-align: center; padding: 40px 0; color: #6B7280; }
.spinner { width: 30px; height: 30px; border: 3px solid #E5E7EB; border-top-color: #2D6A4F; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.btn-retry { padding: 8px 16px; background: #2D6A4F; color: white; border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; }
</style>
