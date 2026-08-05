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
        <span class="tab-badge blue-badge">{{ filteredTheoryEnrollments.length }}</span>
      </button>

      <button
        class="tab-btn"
        :class="{ active: activeTab === 'driving' }"
        @click="activeTab = 'driving'"
      >
        <span class="tab-icon">🏎️</span>
        <span>Amaliy Haydash (Driving lesson)</span>
        <span class="tab-badge purple-badge">{{ filteredDrivingLessons.length }} ta dars</span>
      </button>
    </div>

    <!-- ━━━━━━━━━━━━━━━━━━ TAB 1: NAZARIYA (THEORY) ━━━━━━━━━━━━━━━━━━ -->
    <div v-if="activeTab === 'theory'" class="tab-content margin-top">
      <div v-if="loading" class="state-box">
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
                    <option v-for="c in theoryCategoryOptions" :key="c.id" :value="c.id">{{ c.name }}</option>
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
              <tr v-if="displayedTheoryEnrollments.length === 0">
                <td colspan="8" class="td-empty">Mos o'quvchilar topilmadi</td>
              </tr>
              <tr v-for="enr in displayedTheoryEnrollments" :key="enr.id" class="table-row">
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
        <div class="pagination-bar" v-if="filteredTheoryEnrollments.length > 0">
          <span class="pagination-info">
            Jami: <strong>{{ filteredTheoryEnrollments.length }}</strong> tadan <strong>{{ displayedTheoryEnrollments.length }}</strong> ko'rsatilmoqda
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
      <div v-if="loading" class="state-box">
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
              <tr v-if="displayedDrivingLessons.length === 0">
                <td colspan="9" class="td-empty">Amaliy haydash darslari topilmadi</td>
              </tr>
              <tr v-for="lesson in displayedDrivingLessons" :key="lesson.id" class="table-row">
                <td class="font-bold">📅 {{ formatDateTime(lesson.lesson_date) }}</td>
                <td class="font-bold text-dark link-value" @click="goStudent(lesson.student)">👤 {{ lesson.student_name }}</td>
                <td><span class="instructor-badge link-value" @click="goUser(lesson.instructor)">🏎️ {{ lesson.instructor_name }}</span></td>
                <td><span class="car-badge font-bold link-value" @click="goCar(lesson.car)">🚘 {{ lesson.car_name || '-' }}</span></td>
                <td>
                  <span v-if="getStudentGroupInfo(lesson.student)" class="group-badge link-value" @click="goGroup(getStudentGroupInfo(lesson.student).id)">{{ getStudentGroupInfo(lesson.student).group_name }}</span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td>{{ getStudentGroupInfo(lesson.student)?.started_at ? formatDate(getStudentGroupInfo(lesson.student).started_at) : '-' }}</td>
                <td>{{ getStudentGroupInfo(lesson.student)?.ends_at ? formatDate(getStudentGroupInfo(lesson.student).ends_at) : '-' }}</td>
                <td><span class="status-badge-pill available">✓ Tasdiqlangan</span></td>
                <td><span class="notes-text">{{ lesson.notes || '-' }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="pagination-bar" v-if="filteredDrivingLessons.length > 0">
          <span class="pagination-info">
            Jami: <strong>{{ filteredDrivingLessons.length }}</strong> tadan <strong>{{ displayedDrivingLessons.length }}</strong> ko'rsatilmoqda
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
const loading = ref(true)

// theoryTeachers/drivingInstructors/categories/cars are intentionally not
// fetched from their own unrelated "give me everything" endpoints — the
// header select filters below are built from the rows actually on screen
// (enrollments / driving lessons), so a filter never offers a
// teacher/group/instructor/car/category that isn't present in the table.
const enrollments = ref([])
const drivingLessons = ref([])
const groups = ref([])

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

function setTheoryGroupSort(column, direction) {
  if (column === 'start') {
    theoryGroupEndSort.value = ''
    theoryGroupStartSort.value = theoryGroupStartSort.value === direction ? '' : direction
  } else {
    theoryGroupStartSort.value = ''
    theoryGroupEndSort.value = theoryGroupEndSort.value === direction ? '' : direction
  }
}

// Only one of the three driving-table date columns (lesson date, group
// start, group end) sorts at a time — picking one clears the others.
function setDrivingSort(column, direction) {
  const target = column === 'date' ? drivingDateSort : (column === 'start' ? drivingGroupStartSort : drivingGroupEndSort)
  ;[drivingDateSort, drivingGroupStartSort, drivingGroupEndSort].forEach(r => { if (r !== target) r.value = '' })
  target.value = target.value === direction ? '' : direction
}

// Nulls (no date) always sort last, regardless of direction.
function compareDates(dateA, dateB, direction) {
  const a = dateA ? new Date(dateA).getTime() : null
  const b = dateB ? new Date(dateB).getTime() : null
  if (a == null && b == null) return 0
  if (a == null) return 1
  if (b == null) return -1
  return direction === 'asc' ? a - b : b - a
}

const groupsById = computed(() => {
  const map = {}
  groups.value.forEach(g => { map[g.id] = g })
  return map
})

// Builds { id, name } option lists from the rows actually visible in a
// table, deduplicated and alphabetically sorted, instead of pulling from a
// separate unrelated master list.
function uniqueOptions(list, idKey, nameKey) {
  const map = new Map()
  list.forEach(item => {
    const id = item[idKey]
    if (id == null || map.has(id)) return
    map.set(id, item[nameKey] || '')
  })
  return Array.from(map, ([id, name]) => ({ id, name })).sort((a, b) => a.name.localeCompare(b.name))
}

// Instructors and coordinators only ever see their own lessons — both the
// theory roster (their own students) and the practical table below.
const ownStaffId = computed(() =>
  authStore.isTeachingStaff ? authStore.user?.id : null
)

// Theory rows visible before the column filters are applied — the base set
// the header filter options are drawn from.
const baseTheoryEnrollments = computed(() =>
  enrollments.value.filter(e =>
    e.coordinator &&
    (!ownStaffId.value || e.coordinator === ownStaffId.value) &&
    branchStore.isBranchMatch(e)
  )
)

const theoryCategoryOptions = computed(() => uniqueOptions(baseTheoryEnrollments.value, 'category', 'category_name'))

// One row per student enrolled with a theory teacher (coordinator) assigned.
const filteredTheoryEnrollments = computed(() => {
  const q = theorySearchQuery.value.trim().toLowerCase()
  const teacherQ = theoryTeacherFilter.value.trim().toLowerCase()
  const groupQ = theoryGroupFilter.value.trim().toLowerCase()
  const list = baseTheoryEnrollments.value.filter(e => {
    if (teacherQ && !(e.coordinator_name || '').toLowerCase().includes(teacherQ)) return false
    if (groupQ && !(e.group_name || '').toLowerCase().includes(groupQ)) return false
    if (theoryCategoryFilter.value && e.category !== theoryCategoryFilter.value) return false
    const grp = groupsById.value[e.group]
    if (theoryGroupStartFrom.value && !(grp && grp.started_at && grp.started_at >= theoryGroupStartFrom.value)) return false
    if (theoryGroupStartTo.value && !(grp && grp.started_at && grp.started_at <= theoryGroupStartTo.value)) return false
    if (theoryGroupEndFrom.value && !(grp && grp.ends_at && grp.ends_at >= theoryGroupEndFrom.value)) return false
    if (theoryGroupEndTo.value && !(grp && grp.ends_at && grp.ends_at <= theoryGroupEndTo.value)) return false
    if (!q) return true
    return (e.student_name || '').toLowerCase().includes(q)
  })
  if (theoryGroupStartSort.value || theoryGroupEndSort.value) {
    const dir = theoryGroupStartSort.value || theoryGroupEndSort.value
    const field = theoryGroupStartSort.value ? 'started_at' : 'ends_at'
    return [...list].sort((a, b) => compareDates(groupsById.value[a.group]?.[field], groupsById.value[b.group]?.[field], dir))
  }
  return list
})

// Look up a student's current enrollment (group + category) for filtering/display
function getStudentEnrollment(studentId) {
  if (!studentId) return null
  return enrollments.value.find(e => e.student === studentId && e.group) || null
}

// Look up a student's current group (name + start/end dates) via their enrollment
function getStudentGroupInfo(studentId) {
  const enr = getStudentEnrollment(studentId)
  if (!enr) return null
  const group = groupsById.value[enr.group]
  return {
    id: enr.group,
    group_name: enr.group_name || (group ? group.name : ''),
    started_at: group ? group.started_at : null,
    ends_at: group ? group.ends_at : null,
  }
}

// Driving lesson rows visible before the column filters are applied.
const baseDrivingLessons = computed(() =>
  drivingLessons.value.filter(l =>
    (!ownStaffId.value || l.instructor === ownStaffId.value) &&
    branchStore.isBranchMatch(l)
  )
)

const filteredDrivingLessons = computed(() => {
  const q = drivingSearchQuery.value.trim().toLowerCase()
  const instructorQ = drivingInstructorFilter.value.trim().toLowerCase()
  const carQ = drivingCarFilter.value.trim().toLowerCase()
  const groupQ = drivingGroupFilter.value.trim().toLowerCase()
  const from = drivingDateFrom.value
  const to = drivingDateTo.value
  const list = baseDrivingLessons.value.filter(l => {
    if (instructorQ && !(l.instructor_name || '').toLowerCase().includes(instructorQ)) return false
    const info = groupQ || drivingGroupStartFrom.value || drivingGroupStartTo.value || drivingGroupEndFrom.value || drivingGroupEndTo.value
      ? getStudentGroupInfo(l.student)
      : null
    if (groupQ && (!info || !(info.group_name || '').toLowerCase().includes(groupQ))) return false
    if (drivingGroupStartFrom.value && !(info && info.started_at && info.started_at >= drivingGroupStartFrom.value)) return false
    if (drivingGroupStartTo.value && !(info && info.started_at && info.started_at <= drivingGroupStartTo.value)) return false
    if (drivingGroupEndFrom.value && !(info && info.ends_at && info.ends_at >= drivingGroupEndFrom.value)) return false
    if (drivingGroupEndTo.value && !(info && info.ends_at && info.ends_at <= drivingGroupEndTo.value)) return false
    if (carQ && !(l.car_name || '').toLowerCase().includes(carQ)) return false
    if (from && l.lesson_date && l.lesson_date.slice(0, 10) < from) return false
    if (to && l.lesson_date && l.lesson_date.slice(0, 10) > to) return false
    if (!q) return true
    return (l.student_name || '').toLowerCase().includes(q)
  })
  if (drivingDateSort.value) {
    const dir = drivingDateSort.value
    return [...list].sort((a, b) => compareDates(a.lesson_date, b.lesson_date, dir))
  }
  if (drivingGroupStartSort.value || drivingGroupEndSort.value) {
    const dir = drivingGroupStartSort.value || drivingGroupEndSort.value
    const field = drivingGroupStartSort.value ? 'started_at' : 'ends_at'
    return [...list].sort((a, b) => compareDates(getStudentGroupInfo(a.student)?.[field], getStudentGroupInfo(b.student)?.[field], dir))
  }
  return list
})

// ── Row-fetch-count selector ──────────────────────────────────
// pageSizeOption no longer controls how much is fetched — fetchData always
// pulls the entire dataset (see page_size: 100000 below) so every filter
// above sees every row, not just whatever page happened to be loaded.
// Instead it controls how many of the *filtered* rows show per page (see
// the displayTheory*/displayDriving* computeds below). Both tabs' datasets
// are fetched together in fetchData, so they share one selector, but each
// tab tracks its own current page independently.
const pageSizeOption = ref('50')
const currentTheoryPage = ref(1)
const currentDrivingPage = ref(1)

async function fetchData() {
  loading.value = true
  try {
    const [enrRes, drvRes, grpRes] = await Promise.all([
      api.get('/enrollments/', { params: { page_size: 100000 } }),
      api.get('/driving-lessons/', { params: { page_size: 100000 } }),
      // Groups are only used to look up start/end dates for the rows above,
      // not displayed as their own list — always fetch the full set.
      api.get('/groups/', { params: { page_size: 1000 } }),
    ])

    enrollments.value = enrRes.data.results || enrRes.data || []
    drivingLessons.value = drvRes.data.results || drvRes.data || []
    groups.value = grpRes.data.results || grpRes.data || []
  } catch (err) {
    console.error("Darslar ma'lumotlarini yuklashda xatolik:", err)
  } finally {
    loading.value = false
  }
}

// pageSizeOption now purely controls how many of the *filtered* rows show
// per page — no backend round trip, just reset both tabs back to page 1.
watch(pageSizeOption, () => {
  currentTheoryPage.value = 1
  currentDrivingPage.value = 1
})

const displayPageSize = computed(() => pageSizeOption.value === 'all' ? Infinity : Number(pageSizeOption.value))

const displayTotalTheoryPages = computed(() => {
  if (pageSizeOption.value === 'all') return 1
  return Math.max(1, Math.ceil(filteredTheoryEnrollments.value.length / displayPageSize.value))
})
const displayedTheoryEnrollments = computed(() => {
  if (pageSizeOption.value === 'all') return filteredTheoryEnrollments.value
  const page = Math.min(currentTheoryPage.value, displayTotalTheoryPages.value)
  const start = (page - 1) * displayPageSize.value
  return filteredTheoryEnrollments.value.slice(start, start + displayPageSize.value)
})
function changeTheoryPage(page) {
  if (page < 1 || page > displayTotalTheoryPages.value) return
  currentTheoryPage.value = page
}

const displayTotalDrivingPages = computed(() => {
  if (pageSizeOption.value === 'all') return 1
  return Math.max(1, Math.ceil(filteredDrivingLessons.value.length / displayPageSize.value))
})
const displayedDrivingLessons = computed(() => {
  if (pageSizeOption.value === 'all') return filteredDrivingLessons.value
  const page = Math.min(currentDrivingPage.value, displayTotalDrivingPages.value)
  const start = (page - 1) * displayPageSize.value
  return filteredDrivingLessons.value.slice(start, start + displayPageSize.value)
})
function changeDrivingPage(page) {
  if (page < 1 || page > displayTotalDrivingPages.value) return
  currentDrivingPage.value = page
}

onMounted(() => {
  // Instructors teach practical lessons only, so open them straight on that
  // tab rather than an empty theory list.
  if (authStore.isInstructor) activeTab.value = 'driving'
  fetchData()
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
