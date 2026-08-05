<template>
  <AppLayout>

    <div class="page-top">
      <div>
        <h2 class="page-main-title">Davomat hisoboti</h2>
        <p class="page-sub-title">Yo'qlamada kelmagan deb belgilangan o'quvchilar ro'yxati</p>
      </div>
    </div>

    <div class="table-section-card margin-top">
      <div class="toolbar-bar">
        <div class="total-count">
          Jami kelmagan kunlari: <strong class="total-count-value">{{ filteredRecords.length }}</strong>
        </div>
      </div>

      <div class="table-container">
        <div v-if="loading" class="state-box">
          <div class="spinner"></div>
          <span>Yuklanmoqda...</span>
        </div>

        <div v-else-if="records.length === 0" class="empty-state">
          <p>Yozuvlar topilmadi</p>
        </div>

        <table v-else class="data-table">
          <thead>
            <tr>
              <th>O'quvchi F.I.SH.</th>
              <th>Guruh</th>
              <th>Guruh boshlanishi</th>
              <th>Guruh tugashi</th>
              <th>O'quv Joyi</th>
              <th>Dars Kunlari</th>
              <th>Dars Vaqti</th>
              <th>Instruktor</th>
              <th>O'qituvchi</th>
              <th>Agent</th>
              <th>Kelmagan kuni</th>
              <th>Yo'qlama qilgan odam</th>
            </tr>
            <tr class="col-filter-row">
              <th>
                <input v-model="filterStudentName" class="col-filter-input" type="text" placeholder="Ism bo'yicha qidirish..." />
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
              <th>
                <input v-model="filterInstructorName" class="col-filter-input" type="text" placeholder="Instruktor nomi..." />
              </th>
              <th>
                <input v-model="filterTeacherName" class="col-filter-input" type="text" placeholder="O'qituvchi nomi..." />
              </th>
              <th>
                <input v-model="filterAgentName" class="col-filter-input" type="text" placeholder="Agent nomi..." />
              </th>
              <th>
                <div class="col-sort-group">
                  <button type="button" class="col-sort-icon-btn" :class="{ active: dateSort === 'asc' }" title="O'sish tartibida (eskidan yangiga)" @click="setSort('date', 'asc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 20V4"></path>
                      <path d="M3 8l3-4 3 4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button type="button" class="col-sort-icon-btn" :class="{ active: dateSort === 'desc' }" title="Kamayish tartibida (yangidan eskiga)" @click="setSort('date', 'desc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 4v16"></path>
                      <path d="M3 16l3 4 3-4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button v-if="dateFrom || dateTo" type="button" class="btn-clear-date" @click="dateFrom = ''; dateTo = ''" title="Tozalash">✕</button>
                </div>
                <div class="col-date-range">
                  <input v-model="dateFrom" type="date" class="col-date-input" title="Sana (dan)" />
                  <input v-model="dateTo" type="date" class="col-date-input" title="Sana (gacha)" />
                </div>
              </th>
              <th>
                <input v-model="filterMarkedByName" class="col-filter-input" type="text" placeholder="Ism bo'yicha qidirish..." />
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="displayedRecords.length === 0">
              <td colspan="12" class="td-empty">Filtrlarga mos yozuv topilmadi</td>
            </tr>
            <tr v-for="r in displayedRecords" :key="r.id">
              <td class="td-name">
                <span class="link-value" @click="goStudent(r.student)">{{ r.student_name || "Noma'lum" }}</span>
              </td>
              <td>
                <span v-if="r.group" class="link-value" @click="goGroup(r.group)">{{ r.group_name || '-' }}</span>
                <span v-else>{{ r.group_name || '-' }}</span>
              </td>
              <td class="td-date">{{ r.group_started_at ? formatDate(r.group_started_at) : '-' }}</td>
              <td class="td-date">{{ r.group_ends_at ? formatDate(r.group_ends_at) : '-' }}</td>
              <td>{{ r.learning_place_name || '-' }}</td>
              <td>{{ formatLearningDays(r.learning_days) }}</td>
              <td>{{ r.learning_time || '-' }}</td>
              <td>
                <span v-if="r.instructor_name" class="link-value" @click="goUser(r.instructor)">{{ r.instructor_name }}</span>
                <span v-else>-</span>
              </td>
              <td>
                <span v-if="r.coordinator_name" class="link-value" @click="goUser(r.coordinator)">{{ r.coordinator_name }}</span>
                <span v-else>-</span>
              </td>
              <td>
                <span v-if="r.agent_name" class="link-value" @click="goAgent(r.agent)">{{ r.agent_name }}</span>
                <span v-else>-</span>
              </td>
              <td class="td-date">{{ formatDate(r.date) }}</td>
              <td>
                <span v-if="r.marked_by_name" class="link-value" @click="goUser(r.marked_by)">{{ r.marked_by_name }}</span>
                <span v-else>-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination-bar">
        <span class="pagination-info">
          Jami: <strong>{{ filteredRecords.length }}</strong> tadan <strong>{{ displayedRecords.length }}</strong> ko'rsatilmoqda
        </span>
        <div class="pagination-actions">
          <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">Oldingi</button>
          <span v-if="pageSizeOption !== 'all'" class="page-num">Sahifa {{ Math.min(currentPage, displayTotalPages) }} / {{ displayTotalPages }}</span>
          <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === displayTotalPages" @click="changePage(currentPage + 1)">Keyingi</button>
          <label class="page-size-label" for="absence-page-size">Ko'rsatish:</label>
          <div class="select-wrap">
            <select id="absence-page-size" v-model="pageSizeOption" class="page-size-select">
              <option value="50">50</option>
              <option value="100">100</option>
              <option value="200">200</option>
              <option value="all">Barchasi</option>
            </select>
          </div>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { formatDate, formatLearningDays } from '@/utils/formatters'

const router = useRouter()

const records = ref([])
const loading = ref(true)

// ── Row-fetch-count selector ──────────────────────────────────
// Replaces classic next/prev pagination: pick how many rows to pull from
// the backend in one shot, then filter/sort them instantly on the client
// (see displayedRecords below) instead of round-tripping per filter change.
// Filtering has to see every row, not just whatever page happened to be
// fetched — so the fetch itself always pulls everything; pageSizeOption
// instead controls how many of the *filtered* results are shown per page.
const pageSizeOption = ref('50')
const totalCount = ref(0)
const currentPage = ref(1)

async function fetchAbsences() {
  loading.value = true
  try {
    // Always the full dataset — filtering/sorting/pagination above all
    // need to see every row, not just one page of them.
    const res = await api.get('/attendance/', { params: { is_absent: 'true', page: 1, page_size: 100000 } })
    const rawList = res.data.results ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    records.value = rawList
    totalCount.value = res.data.count ?? rawList.length
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

// Only fetchAbsences (on mount) needs a backend round trip; pageSizeOption
// now purely controls how many of the *filtered* rows show per page.
watch(pageSizeOption, () => {
  currentPage.value = 1
})

// Header-column filters
const filterStudentName = ref('')
const filterGroupName = ref('')
const filterInstructorName = ref('')
const filterTeacherName = ref('')
const filterAgentName = ref('')
const filterMarkedByName = ref('')
const groupStartSort = ref('')
const groupEndSort = ref('')
const dateSort = ref('')
const groupStartFrom = ref('')
const groupStartTo = ref('')
const groupEndFrom = ref('')
const groupEndTo = ref('')
const dateFrom = ref('')
const dateTo = ref('')

const sortRefs = { groupStart: groupStartSort, groupEnd: groupEndSort, date: dateSort }
function setSort(field, dir) {
  const target = sortRefs[field]
  Object.values(sortRefs).forEach(r => { if (r !== target) r.value = '' })
  target.value = target.value === dir ? '' : dir
}

const filteredRecords = computed(() => {
  const name = filterStudentName.value.trim().toLowerCase()
  const group = filterGroupName.value.trim().toLowerCase()
  const instr = filterInstructorName.value.trim().toLowerCase()
  const teach = filterTeacherName.value.trim().toLowerCase()
  const agent = filterAgentName.value.trim().toLowerCase()
  const marker = filterMarkedByName.value.trim().toLowerCase()

  let list = records.value.filter(r => {
    if (name && !(r.student_name || '').toLowerCase().includes(name)) return false
    if (group && !(r.group_name || '').toLowerCase().includes(group)) return false
    if (instr && !(r.instructor_name || '').toLowerCase().includes(instr)) return false
    if (teach && !(r.coordinator_name || '').toLowerCase().includes(teach)) return false
    if (agent && !(r.agent_name || '').toLowerCase().includes(agent)) return false
    if (marker && !(r.marked_by_name || '').toLowerCase().includes(marker)) return false
    return true
  })

  if (groupStartFrom.value) list = list.filter(r => r.group_started_at && r.group_started_at >= groupStartFrom.value)
  if (groupStartTo.value) list = list.filter(r => r.group_started_at && r.group_started_at <= groupStartTo.value)
  if (groupEndFrom.value) list = list.filter(r => r.group_ends_at && r.group_ends_at >= groupEndFrom.value)
  if (groupEndTo.value) list = list.filter(r => r.group_ends_at && r.group_ends_at <= groupEndTo.value)
  if (dateFrom.value) list = list.filter(r => r.date && r.date >= dateFrom.value)
  if (dateTo.value) list = list.filter(r => r.date && r.date <= dateTo.value)

  if (groupStartSort.value) {
    const dir = groupStartSort.value === 'asc' ? 1 : -1
    list = list.slice().sort((a, b) => {
      const da = a.group_started_at ? new Date(a.group_started_at).getTime() : null
      const db = b.group_started_at ? new Date(b.group_started_at).getTime() : null
      if (da === null && db === null) return 0
      if (da === null) return 1
      if (db === null) return -1
      return (da - db) * dir
    })
  } else if (groupEndSort.value) {
    const dir = groupEndSort.value === 'asc' ? 1 : -1
    list = list.slice().sort((a, b) => {
      const da = a.group_ends_at ? new Date(a.group_ends_at).getTime() : null
      const db = b.group_ends_at ? new Date(b.group_ends_at).getTime() : null
      if (da === null && db === null) return 0
      if (da === null) return 1
      if (db === null) return -1
      return (da - db) * dir
    })
  } else if (dateSort.value) {
    const dir = dateSort.value === 'asc' ? 1 : -1
    list = list.slice().sort((a, b) => (new Date(a.date).getTime() - new Date(b.date).getTime()) * dir)
  } else {
    list = list.slice().sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
  }

  return list
})

// pageSizeOption now purely controls how many of the *filtered* rows show
// per page — currentPage is clamped here so it self-corrects the moment a
// filter shrinks the result set out from under it.
const displayPageSize = computed(() => pageSizeOption.value === 'all' ? Infinity : Number(pageSizeOption.value))
const displayTotalPages = computed(() => {
  if (pageSizeOption.value === 'all') return 1
  return Math.max(1, Math.ceil(filteredRecords.value.length / displayPageSize.value))
})
const displayedRecords = computed(() => {
  if (pageSizeOption.value === 'all') return filteredRecords.value
  const page = Math.min(currentPage.value, displayTotalPages.value)
  const start = (page - 1) * displayPageSize.value
  return filteredRecords.value.slice(start, start + displayPageSize.value)
})
function changePage(page) {
  if (page < 1 || page > displayTotalPages.value) return
  currentPage.value = page
}

function goStudent(id) {
  if (id) router.push(`/students/${id}`)
}
function goGroup(id) {
  if (id) router.push(`/groups/${id}`)
}
function goAgent(id) {
  if (id) router.push(`/agents/${id}`)
}
function goUser(id) {
  if (id) router.push(`/users/${id}`)
}

onMounted(() => {
  fetchAbsences()
})
</script>

<style scoped>
.page-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-main-title { font-size: 22px; font-weight: 700; color: #111827; }
.page-sub-title { font-size: 13px; color: #6B7280; margin-top: 2px; }
.margin-top { margin-top: 24px; }

.table-section-card { background: white; border: 1px solid #E5E7EB; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.toolbar-bar { display: flex; align-items: center; justify-content: flex-end; padding: 16px 20px; border-bottom: 1px solid #E5E7EB; gap: 16px; flex-wrap: wrap; }
.total-count { font-size: 15px; font-weight: 700; color: #374151; }
.total-count-value { font-size: 22px; font-weight: 800; color: #DC2626; margin-left: 4px; }

.table-container { overflow: auto; max-height: 600px; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: #FFFFFF; padding: 13px 16px; font-size: 12px; font-weight: 700; color: #4B5563; text-align: left; border-bottom: 1px solid #E5E7EB; white-space: nowrap; }
.data-table td { padding: 14px 16px; font-size: 13.5px; color: #1F2937; border-bottom: 1px solid #F3F4F6; vertical-align: middle; white-space: nowrap; }
.data-table thead { position: sticky; top: 0; z-index: 3; }
.data-table thead tr.col-filter-row th { padding: 8px 10px; background: #FAFAFB; }

.td-name { font-weight: 600; color: #111827; }
.td-date { white-space: nowrap; }
.td-empty { text-align: center; padding: 32px; color: #9CA3AF; }

.link-value { cursor: pointer; color: #2563EB; font-weight: 700; text-decoration: underline; }
.link-value:hover { color: #1D4ED8; }

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
.col-filter-input:focus, .col-filter-select:focus { border-color: #DC2626; }
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
.col-sort-icon-btn.active { border-color: #DC2626; color: #DC2626; background: #FEF2F2; }

.select-wrap { position: relative; }

/* ── Per-column date-range filters (under sort buttons) ────── */
.col-date-range {
  display: flex;
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
.col-date-input:focus { border-color: #DC2626; outline: none; }
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
.page-size-select:focus { border-color: #DC2626; outline: none; }

.state-box, .empty-state { text-align: center; padding: 40px 0; color: #6B7280; }
.spinner { width: 28px; height: 28px; border: 3px solid #E5E7EB; border-top-color: #DC2626; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
