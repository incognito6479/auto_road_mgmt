<template>
  <AppLayout>

    <!-- Page Header -->
    <div class="page-top">
      <div>
        <h2 class="page-main-title">Darslar Boshqaruvi (Lessons)</h2>
        <p class="page-sub-title">Nazariya va amaliy haydash darslari bo'yicha biriktirilgan o'qituvchilar hamda o'quvchilar</p>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="lessons-tabs-bar">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'theory' }"
        @click="activeTab = 'theory'"
      >
        <span class="tab-icon">📖</span>
        <span>Nazariya (Theory)</span>
        <span class="tab-badge blue-badge">{{ theoryTotalCount }}</span>
      </button>

      <button
        class="tab-btn"
        :class="{ active: activeTab === 'driving' }"
        @click="activeTab = 'driving'"
      >
        <span class="tab-icon">🏎️</span>
        <span>Amaliy Haydash (Driving lesson)</span>
        <span class="tab-badge purple-badge">{{ drivingTotalCount }} ta dars</span>
      </button>
    </div>

    <!-- ━━━━━━━━━━━━━━━━━━ TAB 1: NAZARIYA (THEORY) ━━━━━━━━━━━━━━━━━━ -->
    <div v-if="activeTab === 'theory'" class="tab-content margin-top">
      <div v-if="initialLoading" class="state-box">
        <div class="spinner"></div>
        <span>Nazariya darslari ma'lumotlari yuklanmoqda...</span>
      </div>

      <!-- Theory Roster Table (one row per student, like the driving lesson history table) -->
      <div v-else class="table-section-card">
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th style="min-width: 180px;">O'quvchi F.I.SH.</th>
                <th style="min-width: 180px;">O'qituvchi</th>
                <th>Kategoriya</th>
                <th style="min-width: 160px;">Guruh</th>
                <th style="width: 130px;">Boshlanish sanasi</th>
                <th style="width: 130px;">Tugash sanasi</th>
                <th>Dars Vaqti</th>
                <th>Dars Kunlari</th>
              </tr>
              <tr class="col-filter-row">
                <th>
                  <input v-model="theorySearchQuery" class="col-filter-input" type="text" placeholder="O'quvchi ismi..." />
                </th>
                <th>
                  <input v-model="theoryTeacherFilter" class="col-filter-input" type="text" placeholder="O'qituvchi ismi..." />
                </th>
                <th>
                  <select v-model="theoryCategoryFilter" class="col-filter-select">
                    <option value="">Barchasi</option>
                    <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
                  </select>
                </th>
                <th>
                  <input v-model="theoryGroupFilter" class="col-filter-input" type="text" placeholder="Guruh nomi..." />
                </th>
                <th>
                  <div class="col-sort-group">
                    <button type="button" class="col-sort-icon-btn" :class="{ active: theoryGroupStartSort === 'asc' }" title="O'sish tartibida" @click="setTheoryGroupSort('start', 'asc')">
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 20V4"></path><path d="M3 8l3-4 3 4"></path></svg>
                    </button>
                    <button type="button" class="col-sort-icon-btn" :class="{ active: theoryGroupStartSort === 'desc' }" title="Kamayish tartibida" @click="setTheoryGroupSort('start', 'desc')">
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4v16"></path><path d="M3 16l3 4 3-4"></path></svg>
                    </button>
                    <button v-if="theoryGroupStartFrom || theoryGroupStartTo" type="button" class="btn-clear-date" @click="theoryGroupStartFrom = ''; theoryGroupStartTo = ''" title="Tozalash">✕</button>
                  </div>
                  <div class="col-date-range">
                    <input v-model="theoryGroupStartFrom" type="date" class="col-date-input" title="Boshlanish sanasi (dan)" />
                    <input v-model="theoryGroupStartTo" type="date" class="col-date-input" title="Boshlanish sanasi (gacha)" />
                  </div>
                </th>
                <th>
                  <div class="col-sort-group">
                    <button type="button" class="col-sort-icon-btn" :class="{ active: theoryGroupEndSort === 'asc' }" title="O'sish tartibida" @click="setTheoryGroupSort('end', 'asc')">
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 20V4"></path><path d="M3 8l3-4 3 4"></path></svg>
                    </button>
                    <button type="button" class="col-sort-icon-btn" :class="{ active: theoryGroupEndSort === 'desc' }" title="Kamayish tartibida" @click="setTheoryGroupSort('end', 'desc')">
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4v16"></path><path d="M3 16l3 4 3-4"></path></svg>
                    </button>
                    <button v-if="theoryGroupEndFrom || theoryGroupEndTo" type="button" class="btn-clear-date" @click="theoryGroupEndFrom = ''; theoryGroupEndTo = ''" title="Tozalash">✕</button>
                  </div>
                  <div class="col-date-range">
                    <input v-model="theoryGroupEndFrom" type="date" class="col-date-input" title="Tugash sanasi (dan)" />
                    <input v-model="theoryGroupEndTo" type="date" class="col-date-input" title="Tugash sanasi (gacha)" />
                  </div>
                </th>
                <th></th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="enrollments.length === 0">
                <td colspan="8" class="td-empty">Mos o'quvchilar topilmadi</td>
              </tr>
              <tr v-for="enr in enrollments" :key="enr.id" class="table-row">
                <td class="font-bold text-dark link-value" @click="goStudent(enr.student)">{{ enr.student_name }}</td>
                <td><span class="instructor-badge link-value" @click="goUser(enr.coordinator)">👨‍🏫 {{ enr.coordinator_name }}</span></td>
                <td><span class="cat-chip">{{ enr.category_name }}</span></td>
                <td>
                  <span v-if="enr.group_name" class="group-badge link-value" @click="goGroup(enr.group)">{{ enr.group_name }}</span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td>{{ groupsById[enr.group] ? formatDate(groupsById[enr.group].started_at) : '-' }}</td>
                <td>{{ groupsById[enr.group] ? formatDate(groupsById[enr.group].ends_at) : '-' }}</td>
                <td>
                  <span v-if="enr.learning_time" class="time-chip">⏰ {{ enr.learning_time }}</span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td>
                  <span v-if="enr.learning_days" class="days-chip">{{ formatLearningDays(enr.learning_days) }}</span>
                  <span v-else class="text-muted">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="pagination-bar" v-if="theoryTotalCount > 0">
          <span class="pagination-info">
            Jami: <strong>{{ theoryTotalCount }}</strong> tadan <strong>{{ enrollments.length }}</strong> ko'rsatilmoqda
          </span>
          <div class="pagination-actions">
            <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentTheoryPage === 1" @click="changeTheoryPage(currentTheoryPage - 1)">Oldingi</button>
            <span v-if="pageSizeOption !== 'all'" class="page-num">Sahifa {{ Math.min(currentTheoryPage, displayTotalTheoryPages) }} / {{ displayTotalTheoryPages }}</span>
            <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentTheoryPage === displayTotalTheoryPages" @click="changeTheoryPage(currentTheoryPage + 1)">Keyingi</button>
            <label class="page-size-label" for="theory-page-size">Ko'rsatish:</label>
            <div class="select-wrap">
              <select id="theory-page-size" v-model="pageSizeOption" class="page-size-select">
                <option value="50">50</option>
                <option value="100">100</option>
                <option value="200">200</option>
                <option value="all">Barchasi</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ━━━━━━━━━━━━━━━━━━ TAB 2: AMALIY HAYDASH (DRIVING LESSON MODEL DATA) ━━━━━━━━━━━━━━━━━━ -->
    <div v-if="activeTab === 'driving'" class="tab-content margin-top">
      <div v-if="initialLoading" class="state-box">
        <div class="spinner"></div>
        <span>Amaliy haydash darslari ma'lumotlari yuklanmoqda...</span>
      </div>

      <!-- Driving Lessons Data Table (From DrivingLessons Model) -->
      <div v-else class="table-section-card">
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th style="min-width: 170px;">Dars Sanasi</th>
                <th style="min-width: 180px;">O'quvchi F.I.SH.</th>
                <th style="min-width: 180px;">Instruktor F.I.SH.</th>
                <th style="min-width: 170px;">Avtomobil</th>
                <th style="min-width: 160px;">Guruh</th>
                <th style="width: 130px;">Boshlanish sanasi</th>
                <th style="width: 130px;">Tugash sanasi</th>
                <th style="width: 120px;">Holati</th>
                <th>Izoh / Eslatmalari</th>
              </tr>
              <tr class="col-filter-row">
                <th>
                  <div class="col-sort-group">
                    <button type="button" class="col-sort-icon-btn" :class="{ active: drivingDateSort === 'asc' }" title="O'sish tartibida" @click="setDrivingSort('date', 'asc')">
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 20V4"></path><path d="M3 8l3-4 3 4"></path></svg>
                    </button>
                    <button type="button" class="col-sort-icon-btn" :class="{ active: drivingDateSort === 'desc' }" title="Kamayish tartibida" @click="setDrivingSort('date', 'desc')">
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4v16"></path><path d="M3 16l3 4 3-4"></path></svg>
                    </button>
                    <button v-if="drivingDateFrom || drivingDateTo" type="button" class="btn-clear-date" @click="drivingDateFrom = ''; drivingDateTo = ''" title="Tozalash">✕</button>
                  </div>
                  <div class="date-range-box">
                    <input v-model="drivingDateFrom" type="date" class="col-filter-input date-range-input" title="Sanadan" />
                    <input v-model="drivingDateTo" type="date" class="col-filter-input date-range-input" title="Sanagacha" />
                  </div>
                </th>
                <th>
                  <input v-model="drivingSearchQuery" class="col-filter-input" type="text" placeholder="O'quvchi ismi..." />
                </th>
                <th>
                  <input v-model="drivingInstructorFilter" class="col-filter-input" type="text" placeholder="Instruktor ismi..." />
                </th>
                <th>
                  <input v-model="drivingCarFilter" class="col-filter-input" type="text" placeholder="Avtomobil nomi..." />
                </th>
                <th>
                  <input v-model="drivingGroupFilter" class="col-filter-input" type="text" placeholder="Guruh nomi..." />
                </th>
                <th>
                  <div class="col-sort-group">
                    <button type="button" class="col-sort-icon-btn" :class="{ active: drivingGroupStartSort === 'asc' }" title="O'sish tartibida" @click="setDrivingSort('start', 'asc')">
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 20V4"></path><path d="M3 8l3-4 3 4"></path></svg>
                    </button>
                    <button type="button" class="col-sort-icon-btn" :class="{ active: drivingGroupStartSort === 'desc' }" title="Kamayish tartibida" @click="setDrivingSort('start', 'desc')">
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4v16"></path><path d="M3 16l3 4 3-4"></path></svg>
                    </button>
                    <button v-if="drivingGroupStartFrom || drivingGroupStartTo" type="button" class="btn-clear-date" @click="drivingGroupStartFrom = ''; drivingGroupStartTo = ''" title="Tozalash">✕</button>
                  </div>
                  <div class="col-date-range">
                    <input v-model="drivingGroupStartFrom" type="date" class="col-date-input" title="Boshlanish sanasi (dan)" />
                    <input v-model="drivingGroupStartTo" type="date" class="col-date-input" title="Boshlanish sanasi (gacha)" />
                  </div>
                </th>
                <th>
                  <div class="col-sort-group">
                    <button type="button" class="col-sort-icon-btn" :class="{ active: drivingGroupEndSort === 'asc' }" title="O'sish tartibida" @click="setDrivingSort('end', 'asc')">
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 20V4"></path><path d="M3 8l3-4 3 4"></path></svg>
                    </button>
                    <button type="button" class="col-sort-icon-btn" :class="{ active: drivingGroupEndSort === 'desc' }" title="Kamayish tartibida" @click="setDrivingSort('end', 'desc')">
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4v16"></path><path d="M3 16l3 4 3-4"></path></svg>
                    </button>
                    <button v-if="drivingGroupEndFrom || drivingGroupEndTo" type="button" class="btn-clear-date" @click="drivingGroupEndFrom = ''; drivingGroupEndTo = ''" title="Tozalash">✕</button>
                  </div>
                  <div class="col-date-range">
                    <input v-model="drivingGroupEndFrom" type="date" class="col-date-input" title="Tugash sanasi (dan)" />
                    <input v-model="drivingGroupEndTo" type="date" class="col-date-input" title="Tugash sanasi (gacha)" />
                  </div>
                </th>
                <th></th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="drivingLessons.length === 0">
                <td colspan="9" class="td-empty">Amaliy haydash darslari topilmadi</td>
              </tr>
              <tr v-for="lesson in drivingLessons" :key="lesson.id" class="table-row">
                <td class="font-bold">📅 {{ formatDateTime(lesson.lesson_date) }}</td>
                <td class="font-bold text-dark link-value" @click="goStudent(lesson.student)">👤 {{ lesson.student_name }}</td>
                <td><span class="instructor-badge link-value" @click="goUser(lesson.instructor)">🏎️ {{ lesson.instructor_name }}</span></td>
                <td><span class="car-badge font-bold link-value" @click="goCar(lesson.car)">🚘 {{ lesson.car_name || '-' }}</span></td>
                <td>
                  <span v-if="lesson.group_name" class="group-badge link-value" @click="goGroup(lesson.group)">{{ lesson.group_name }}</span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td>{{ lesson.group_started_at ? formatDate(lesson.group_started_at) : '-' }}</td>
                <td>{{ lesson.group_ends_at ? formatDate(lesson.group_ends_at) : '-' }}</td>
                <td><span class="status-badge-pill available">✓ Tasdiqlangan</span></td>
                <td><span class="notes-text">{{ lesson.notes || '-' }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="pagination-bar" v-if="drivingTotalCount > 0">
          <span class="pagination-info">
            Jami: <strong>{{ drivingTotalCount }}</strong> tadan <strong>{{ drivingLessons.length }}</strong> ko'rsatilmoqda
          </span>
          <div class="pagination-actions">
            <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentDrivingPage === 1" @click="changeDrivingPage(currentDrivingPage - 1)">Oldingi</button>
            <span v-if="pageSizeOption !== 'all'" class="page-num">Sahifa {{ Math.min(currentDrivingPage, displayTotalDrivingPages) }} / {{ displayTotalDrivingPages }}</span>
            <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentDrivingPage === displayTotalDrivingPages" @click="changeDrivingPage(currentDrivingPage + 1)">Keyingi</button>
            <label class="page-size-label" for="driving-page-size">Ko'rsatish:</label>
            <div class="select-wrap">
              <select id="driving-page-size" v-model="pageSizeOption" class="page-size-select">
                <option value="50">50</option>
                <option value="100">100</option>
                <option value="200">200</option>
                <option value="all">Barchasi</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useBranchStore } from '@/stores/branch'
import { useAuthStore } from '@/stores/auth'
import { formatDateTime, formatLearningDays } from '@/utils/formatters'
import { debounce } from '@/utils/debounce'

const router = useRouter()
const authStore = useAuthStore()

function goStudent(id) {
  if (!id) return
  router.push(`/students/${id}`)
}

function goUser(id) {
  if (!id) return
  router.push(`/users/${id}`)
}

function goCar(id) {
  if (!id) return
  router.push(`/vehicles/${id}`)
}

function goGroup(id) {
  if (!id) return
  router.push(`/groups/${id}`)
}

const branchStore = useBranchStore()
const activeTab = ref('theory')
// Only gates the initial full-page spinner (both tabs are fetched together
// on mount). Gating on a flag that's also set true/false around every
// filter/sort/page refetch would unmount the whole tab's table on each one
// — including the column-filter <input> the user was typing into — via
// v-if, stealing focus and resetting cursor position on every keystroke.
const initialLoading = ref(true)

const enrollments = ref([])
const drivingLessons = ref([])
const groups = ref([])
const theoryTotalCount = ref(0)
const drivingTotalCount = ref(0)

// All categories, not just ones present on whatever page happens to be
// loaded — simpler than deriving from the (now server-paginated)
// enrollments array.
const categories = ref([])
async function fetchCategories() {
  try {
    const res = await api.get('/categories/')
    const list = Array.isArray(res.data) ? res.data : (res.data.results || [])
    categories.value = list.slice().sort((a, b) => a.name.localeCompare(b.name))
  } catch (err) { console.error(err) }
}

const theorySearchQuery = ref('')
const theoryTeacherFilter = ref('')
const theoryGroupFilter = ref('')
const theoryCategoryFilter = ref('')
const theoryGroupStartSort = ref('') // '', 'asc', 'desc'
const theoryGroupEndSort = ref('')
const theoryGroupStartFrom = ref('')
const theoryGroupStartTo = ref('')
const theoryGroupEndFrom = ref('')
const theoryGroupEndTo = ref('')

const drivingSearchQuery = ref('')
const drivingDateSort = ref('')
const drivingDateFrom = ref('')
const drivingDateTo = ref('')
const drivingInstructorFilter = ref('')
const drivingGroupFilter = ref('')
const drivingCarFilter = ref('')
const drivingGroupStartSort = ref('')
const drivingGroupEndSort = ref('')
const drivingGroupStartFrom = ref('')
const drivingGroupStartTo = ref('')
const drivingGroupEndFrom = ref('')
const drivingGroupEndTo = ref('')

const groupsById = computed(() => {
  const map = {}
  groups.value.forEach(g => { map[g.id] = g })
  return map
})

// Instructors and coordinators only ever see their own lessons — both the
// theory roster (their own students) and the practical table below.
const ownStaffId = computed(() =>
  authStore.isTeachingStaff ? authStore.user?.id : null
)

const THEORY_ORDERING_MAP = { start: 'group_started_at', end: 'group_ends_at' }
const theoryOrdering = computed(() => {
  if (theoryGroupStartSort.value) return (theoryGroupStartSort.value === 'desc' ? '-' : '') + THEORY_ORDERING_MAP.start
  if (theoryGroupEndSort.value) return (theoryGroupEndSort.value === 'desc' ? '-' : '') + THEORY_ORDERING_MAP.end
  return ''
})

const drivingOrdering = computed(() => {
  if (drivingDateSort.value) return (drivingDateSort.value === 'desc' ? '-' : '') + 'lesson_date'
  if (drivingGroupStartSort.value) return (drivingGroupStartSort.value === 'desc' ? '-' : '') + 'group_started_at'
  if (drivingGroupEndSort.value) return (drivingGroupEndSort.value === 'desc' ? '-' : '') + 'group_ends_at'
  return ''
})

const pageSizeOption = ref('50')
const currentTheoryPage = ref(1)
const currentDrivingPage = ref(1)

// Guards against an older, slower request (e.g. the initial load) resolving
// *after* a newer filtered one and clobbering it with stale results —
// debounce only limits how often a request starts, not the order replies
// come back in. Each tab tracks its own token since the two fetch
// independently of one another.
let theoryFetchToken = 0
async function fetchTheory() {
  const token = ++theoryFetchToken
  try {
    const params = {
      page: currentTheoryPage.value,
      page_size: pageSizeOption.value === 'all' ? 100000 : Number(pageSizeOption.value),
    }
    if (ownStaffId.value) params.coordinator = ownStaffId.value
    else params.has_coordinator = 'true'
    if (theorySearchQuery.value.trim()) params.student_name = theorySearchQuery.value.trim()
    if (theoryTeacherFilter.value.trim()) params.coordinator_name = theoryTeacherFilter.value.trim()
    if (theoryGroupFilter.value.trim()) params.group_name = theoryGroupFilter.value.trim()
    if (theoryCategoryFilter.value) params.category = theoryCategoryFilter.value
    if (theoryGroupStartFrom.value) params.group_start_from = theoryGroupStartFrom.value
    if (theoryGroupStartTo.value) params.group_start_to = theoryGroupStartTo.value
    if (theoryGroupEndFrom.value) params.group_end_from = theoryGroupEndFrom.value
    if (theoryGroupEndTo.value) params.group_end_to = theoryGroupEndTo.value
    if (theoryOrdering.value) params.ordering = theoryOrdering.value
    if (branchStore.activeBranchId) params.branch = branchStore.activeBranchId

    const res = await api.get('/enrollments/', { params })
    if (token !== theoryFetchToken) return // a newer request has since been sent — discard this stale response
    enrollments.value = res.data.results || res.data || []
    theoryTotalCount.value = res.data.count ?? enrollments.value.length
  } catch (err) {
    console.error("Nazariya darslarini yuklashda xatolik:", err)
  }
}

let drivingFetchToken = 0
async function fetchDriving() {
  const token = ++drivingFetchToken
  try {
    const params = {
      page: currentDrivingPage.value,
      page_size: pageSizeOption.value === 'all' ? 100000 : Number(pageSizeOption.value),
    }
    if (ownStaffId.value) params.instructor = ownStaffId.value
    if (drivingSearchQuery.value.trim()) params.student_name = drivingSearchQuery.value.trim()
    if (drivingInstructorFilter.value.trim()) params.instructor_name = drivingInstructorFilter.value.trim()
    if (drivingCarFilter.value.trim()) params.car_name = drivingCarFilter.value.trim()
    if (drivingGroupFilter.value.trim()) params.group_name = drivingGroupFilter.value.trim()
    if (drivingDateFrom.value) params.lesson_date_from = drivingDateFrom.value
    if (drivingDateTo.value) params.lesson_date_to = drivingDateTo.value
    if (drivingGroupStartFrom.value) params.group_start_from = drivingGroupStartFrom.value
    if (drivingGroupStartTo.value) params.group_start_to = drivingGroupStartTo.value
    if (drivingGroupEndFrom.value) params.group_end_from = drivingGroupEndFrom.value
    if (drivingGroupEndTo.value) params.group_end_to = drivingGroupEndTo.value
    if (drivingOrdering.value) params.ordering = drivingOrdering.value
    if (branchStore.activeBranchId) params.branch = branchStore.activeBranchId

    const res = await api.get('/driving-lessons/', { params })
    if (token !== drivingFetchToken) return
    drivingLessons.value = res.data.results || res.data || []
    drivingTotalCount.value = res.data.count ?? drivingLessons.value.length
  } catch (err) {
    console.error("Amaliy haydash darslarini yuklashda xatolik:", err)
  }
}

async function fetchGroups() {
  try {
    // Groups are only used to look up start/end dates for the theory table
    // above, not displayed as their own paginated list — always fetch the
    // full (small) set.
    const res = await api.get('/groups/', { params: { page_size: 1000 } })
    groups.value = res.data.results || res.data || []
  } catch (err) {
    console.error(err)
  }
}

// Every filter/sort below triggers a backend refetch of its own tab only
// (see fetchTheory/fetchDriving) — the other tab's already-loaded data and
// tab-count badge stay untouched. Select/date/sort filters refetch
// immediately on change (discrete input, no per-keystroke risk); text
// filters are debounced so typing doesn't fire a request per keystroke —
// the input itself is never re-rendered/replaced by any of this (only the
// table rows below it are, gated by initialLoading rather than a per-fetch
// flag), so there's no risk of losing focus or cursor position mid-word.
function setTheoryGroupSort(column, direction) {
  if (column === 'start') {
    theoryGroupEndSort.value = ''
    theoryGroupStartSort.value = theoryGroupStartSort.value === direction ? '' : direction
  } else {
    theoryGroupStartSort.value = ''
    theoryGroupEndSort.value = theoryGroupEndSort.value === direction ? '' : direction
  }
  currentTheoryPage.value = 1
  fetchTheory()
}

// Only one of the three driving-table date columns (lesson date, group
// start, group end) sorts at a time — picking one clears the others.
function setDrivingSort(column, direction) {
  const target = column === 'date' ? drivingDateSort : (column === 'start' ? drivingGroupStartSort : drivingGroupEndSort)
  ;[drivingDateSort, drivingGroupStartSort, drivingGroupEndSort].forEach(r => { if (r !== target) r.value = '' })
  target.value = target.value === direction ? '' : direction
  currentDrivingPage.value = 1
  fetchDriving()
}

watch(theoryCategoryFilter, () => { currentTheoryPage.value = 1; fetchTheory() })
watch([theoryGroupStartFrom, theoryGroupStartTo, theoryGroupEndFrom, theoryGroupEndTo], () => {
  currentTheoryPage.value = 1
  fetchTheory()
})
const debouncedTheoryRefetch = debounce(() => { currentTheoryPage.value = 1; fetchTheory() }, 400)
watch([theorySearchQuery, theoryTeacherFilter, theoryGroupFilter], debouncedTheoryRefetch)

watch([drivingDateFrom, drivingDateTo, drivingGroupStartFrom, drivingGroupStartTo, drivingGroupEndFrom, drivingGroupEndTo], () => {
  currentDrivingPage.value = 1
  fetchDriving()
})
const debouncedDrivingRefetch = debounce(() => { currentDrivingPage.value = 1; fetchDriving() }, 400)
watch([drivingSearchQuery, drivingInstructorFilter, drivingCarFilter, drivingGroupFilter], debouncedDrivingRefetch)

// pageSizeOption and branch are shared across both tabs (one selector/nav
// bar drives both tables), so changing either refetches both.
watch(pageSizeOption, () => {
  currentTheoryPage.value = 1
  currentDrivingPage.value = 1
  fetchTheory()
  fetchDriving()
})
watch(() => branchStore.activeBranchId, () => {
  currentTheoryPage.value = 1
  currentDrivingPage.value = 1
  fetchTheory()
  fetchDriving()
})

const displayTotalTheoryPages = computed(() => {
  if (pageSizeOption.value === 'all') return 1
  return Math.max(1, Math.ceil(theoryTotalCount.value / Number(pageSizeOption.value)))
})
function changeTheoryPage(page) {
  if (page < 1 || page > displayTotalTheoryPages.value) return
  currentTheoryPage.value = page
  fetchTheory()
}

const displayTotalDrivingPages = computed(() => {
  if (pageSizeOption.value === 'all') return 1
  return Math.max(1, Math.ceil(drivingTotalCount.value / Number(pageSizeOption.value)))
})
function changeDrivingPage(page) {
  if (page < 1 || page > displayTotalDrivingPages.value) return
  currentDrivingPage.value = page
  fetchDriving()
}

onMounted(async () => {
  // Instructors teach practical lessons only, so open them straight on that
  // tab rather than an empty theory list.
  if (authStore.isInstructor) activeTab.value = 'driving'
  fetchCategories()
  fetchGroups()
  await Promise.all([fetchTheory(), fetchDriving()])
  initialLoading.value = false
})

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const parts = dateStr.split('-')
  if (parts.length === 3) return `${parts[2]}.${parts[1]}.${parts[0]}`
  return dateStr
}

</script>

<style scoped>
.page-top { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 20px; }
.page-main-title { font-size: 22px; font-weight: 800; color: #111827; }
.page-sub-title { font-size: 13px; color: #6B7280; margin-top: 2px; }

/* TABS BAR */
.lessons-tabs-bar { display: flex; align-items: center; gap: 12px; border-bottom: 2px solid #E5E7EB; padding-bottom: 2px; }
.tab-btn { display: flex; align-items: center; gap: 8px; padding: 12px 20px; border: none; background: transparent; border-bottom: 3px solid transparent; font-size: 14px; font-weight: 700; color: #6B7280; cursor: pointer; transition: all 0.2s ease; }
.tab-btn:hover { color: #111827; }
.tab-btn.active { color: #4F46E5; border-bottom-color: #4F46E5; }
.tab-icon { font-size: 18px; }
.tab-badge { font-size: 11px; padding: 2px 8px; border-radius: 12px; font-weight: 800; }
.blue-badge { background: #DBEAFE; color: #1D4ED8; }
.purple-badge { background: #F3E8FF; color: #7E22CE; }

.margin-top { margin-top: 20px; }

.table-section-card { background: white; border: 1px solid #E5E7EB; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.table-container { overflow-x: auto; }

.pagination-bar { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #F9FAFB; border-top: 1px solid #E5E7EB; }
.pagination-info { font-size: 13.5px; color: #6B7280; font-weight: 500; }
.pagination-note { margin-left: 8px; font-size: 12px; color: #9CA3AF; font-weight: 400; }
.pagination-actions { display: flex; align-items: center; gap: 8px; }
.page-size-label { font-size: 13px; font-weight: 600; color: #4B5563; }
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
.data-table { width: 100%; border-collapse: collapse; th { background: #F9FAFB; padding: 13px 16px; font-size: 12px; font-weight: 700; color: #4B5563; text-align: left; border-bottom: 1px solid #E5E7EB; } td { padding: 14px 16px; font-size: 13.5px; color: #1F2937; border-bottom: 1px solid #F3F4F6; vertical-align: middle; } }
.td-empty { text-align: center; padding: 32px; color: #6B7280; }

/* Sticky is applied to <thead> itself, not to individual <th> cells — that
   keeps both header rows (labels + filters) moving as a single pinned unit. */
.data-table thead { position: sticky; top: 0; z-index: 3; }

/* ── Column-head filters ─────────────────────────────────── */
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
.col-filter-input:focus, .col-filter-select:focus { border-color: #4F46E5; }
.col-filter-input::placeholder { color: #9CA3AF; }

.col-sort-group { display: flex; gap: 4px; }
.col-sort-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
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

/* ── Per-column date-range filters (under sort buttons) ────── */
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
}
.btn-clear-date:hover { background: #E5E7EB; color: #111827; }

.instructor-badge { padding: 4px 10px; background: #F3E8FF; color: #7E22CE; border-radius: 8px; font-size: 12px; font-weight: 700; }
.car-badge { padding: 4px 10px; background: #DCFCE7; color: #15803D; border-radius: 8px; font-size: 12px; font-weight: 700; }
.link-value { cursor: pointer; color: #2563EB; text-decoration: underline; }
.link-value:hover { text-decoration: underline; }
.status-badge-pill { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; display: inline-block; }
.status-badge-pill.available { background: #DCFCE7; color: #15803D; }

.font-bold { font-weight: 700; }
.text-dark { color: #0F172A; }
.cat-chip { padding: 3px 8px; background: #F1F5F9; color: #334155; border-radius: 6px; font-weight: 700; font-size: 11.5px; }
.time-chip { padding: 3px 8px; background: #FEF3C7; color: #D97706; border-radius: 6px; font-weight: 600; font-size: 12px; }
.days-chip { font-size: 12px; color: #475569; }
.notes-text { font-size: 12.5px; color: #64748B; }

.state-box { text-align: center; padding: 40px 0; color: #6B7280; }
.spinner { width: 28px; height: 28px; border: 3px solid #E5E7EB; border-top-color: #4F46E5; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Date range filter (driving tab, "Dars Sanasi" column header) */
.date-range-box { display: flex; align-items: center; gap: 4px; }
.date-range-input { padding: 6px 8px; }

/* Group column in driving lessons table */
.group-badge { padding: 3px 9px; background: #E0E7FF; color: #4338CA; border-radius: 8px; font-size: 11.5px; font-weight: 700; display: inline-block; }
.text-muted { color: #9CA3AF; }
</style>
