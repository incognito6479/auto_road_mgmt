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
      <div class="toolbar-card">
        <div class="search-box">
          <svg viewBox="0 0 20 20" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
            <circle cx="8.5" cy="8.5" r="5.5"/>
            <line x1="13" y1="13" x2="18" y2="18"/>
          </svg>
          <input
            v-model="theorySearchQuery"
            type="text"
            placeholder="O'quvchi ismini kiriting..."
            class="search-input"
          />
        </div>

        <div class="filter-controls">
          <div class="filter-item">
            <label class="filter-label">O'qituvchi:</label>
            <div class="select-wrap">
              <select v-model="theoryTeacherFilter" class="group-filter-select">
                <option value="">Barchasi</option>
                <option v-for="t in theoryTeachers" :key="t.id" :value="t.id">{{ t.full_name }}</option>
              </select>
            </div>
          </div>
          <div class="filter-item">
            <label class="filter-label">Guruh:</label>
            <div class="select-wrap">
              <select v-model="theoryGroupFilter" class="group-filter-select">
                <option value="">Barchasi</option>
                <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
              </select>
            </div>
          </div>
          <div class="filter-item">
            <label class="filter-label">Kategoriya:</label>
            <div class="select-wrap">
              <select v-model="theoryCategoryFilter" class="group-filter-select">
                <option value="">Barchasi</option>
                <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
          </div>
        </div>

        <div class="total-count">
          Jami: <strong>{{ filteredTheoryEnrollments.length }}</strong> ta o'quvchi
        </div>
      </div>

      <div v-if="loading" class="state-box">
        <div class="spinner"></div>
        <span>Nazariya darslari ma'lumotlari yuklanmoqda...</span>
      </div>

      <div v-else-if="filteredTheoryEnrollments.length === 0" class="empty-state">
        <p>Mos o'quvchilar topilmadi</p>
      </div>

      <!-- Theory Roster Table (one row per student, like the driving lesson history table) -->
      <div v-else class="table-section-card">
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th style="min-width: 180px;">O'quvchi F.I.SH.</th>
                <th>Telefon</th>
                <th style="min-width: 180px;">O'qituvchi</th>
                <th>Kategoriya</th>
                <th style="min-width: 190px;">Guruh</th>
                <th>Dars Vaqti</th>
                <th>Dars Kunlari</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="enr in filteredTheoryEnrollments" :key="enr.id" class="table-row">
                <td class="font-bold text-dark link-value" @click="goStudent(enr.student)">{{ enr.student_name }}</td>
                <td>{{ formatPhone(enr.student_phone) }}</td>
                <td><span class="instructor-badge link-value" @click="goUser(enr.coordinator)">👨‍🏫 {{ enr.coordinator_name }}</span></td>
                <td><span class="cat-chip">{{ enr.category_name }}</span></td>
                <td>
                  <template v-if="enr.group_name">
                    <span class="group-badge link-value" @click="goGroup(enr.group)">{{ enr.group_name }}</span>
                    <div v-if="groupsById[enr.group]" class="group-dates">
                      {{ formatDate(groupsById[enr.group].started_at) }} — {{ formatDate(groupsById[enr.group].ends_at) }}
                    </div>
                  </template>
                  <span v-else class="text-muted">-</span>
                </td>
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
      </div>
    </div>

    <!-- ━━━━━━━━━━━━━━━━━━ TAB 2: AMALIY HAYDASH (DRIVING LESSON MODEL DATA) ━━━━━━━━━━━━━━━━━━ -->
    <div v-if="activeTab === 'driving'" class="tab-content margin-top">
      <div class="toolbar-card">
        <div class="search-box">
          <svg viewBox="0 0 20 20" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
            <circle cx="8.5" cy="8.5" r="5.5"/>
            <line x1="13" y1="13" x2="18" y2="18"/>
          </svg>
          <input
            v-model="drivingSearchQuery"
            type="text"
            placeholder="Instruktor, o'quvchi yoki avtomobil nomi bo'yicha..."
            class="search-input"
          />
        </div>

        <div class="filter-controls">
          <div class="filter-item">
            <label class="filter-label">Instruktor:</label>
            <div class="select-wrap">
              <select v-model="drivingInstructorFilter" class="group-filter-select">
                <option value="">Barchasi</option>
                <option v-for="i in drivingInstructors" :key="i.id" :value="i.id">{{ i.full_name }}</option>
              </select>
            </div>
          </div>
          <div class="filter-item">
            <label class="filter-label">Guruh:</label>
            <div class="select-wrap">
              <select v-model="drivingGroupFilter" class="group-filter-select">
                <option value="">Barchasi</option>
                <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
              </select>
            </div>
          </div>
          <div class="filter-item">
            <label class="filter-label">Avtomobil:</label>
            <div class="select-wrap">
              <select v-model="drivingCarFilter" class="group-filter-select">
                <option value="">Barchasi</option>
                <option v-for="c in cars" :key="c.id" :value="c.id">{{ c.car_name }}</option>
              </select>
            </div>
          </div>
        </div>

        <div class="date-range-box">
          <label class="date-range-label">Sana:</label>
          <input v-model="drivingDateFrom" type="date" class="date-range-input" />
          <span class="date-range-sep">—</span>
          <input v-model="drivingDateTo" type="date" class="date-range-input" />
          <button v-if="drivingDateFrom || drivingDateTo" type="button" class="date-range-clear" @click="drivingDateFrom = ''; drivingDateTo = ''" title="Tozalash">✕</button>
        </div>

        <div class="total-count">
          Jami: <strong>{{ filteredDrivingLessons.length }}</strong> ta amaliy haydash darsi
        </div>
      </div>

      <div v-if="loading" class="state-box">
        <div class="spinner"></div>
        <span>Amaliy haydash darslari ma'lumotlari yuklanmoqda...</span>
      </div>

      <div v-else-if="filteredDrivingLessons.length === 0" class="empty-state">
        <p>Amaliy haydash darslari topilmadi</p>
      </div>

      <!-- Driving Lessons Data Table (From DrivingLessons Model) -->
      <div v-else class="table-section-card">
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th style="width: 60px;">ID</th>
                <th style="min-width: 140px;">Dars Sanasi</th>
                <th style="min-width: 180px;">O'quvchi F.I.SH.</th>
                <th style="min-width: 180px;">Instruktor F.I.SH.</th>
                <th style="min-width: 170px;">Avtomobil</th>
                <th style="min-width: 190px;">Guruh</th>
                <th style="width: 120px;">Holati</th>
                <th>Izoh / Eslatmalari</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="lesson in filteredDrivingLessons" :key="lesson.id" class="table-row">
                <td class="td-id">#{{ lesson.id }}</td>
                <td class="font-bold">📅 {{ formatDateTime(lesson.lesson_date) }}</td>
                <td class="font-bold text-dark link-value" @click="goStudent(lesson.student)">👤 {{ lesson.student_name }}</td>
                <td><span class="instructor-badge link-value" @click="goUser(lesson.instructor)">🏎️ {{ lesson.instructor_name }}</span></td>
                <td><span class="car-badge font-bold link-value" @click="goCar(lesson.car)">🚘 {{ lesson.car_name || '-' }}</span></td>
                <td>
                  <template v-if="getStudentGroupInfo(lesson.student)">
                    <span class="group-badge">{{ getStudentGroupInfo(lesson.student).group_name }}</span>
                    <div class="group-dates">{{ formatDate(getStudentGroupInfo(lesson.student).started_at) }} — {{ formatDate(getStudentGroupInfo(lesson.student).ends_at) }}</div>
                  </template>
                  <span v-else class="text-muted">-</span>
                </td>
                <td><span class="status-badge-pill available">✓ Tasdiqlangan</span></td>
                <td><span class="notes-text">{{ lesson.notes || '-' }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useBranchStore } from '@/stores/branch'
import { useAuthStore } from '@/stores/auth'
import { formatPhone, formatDateTime, formatLearningDays } from '@/utils/formatters'

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

const theoryTeachers = ref([])
const drivingInstructors = ref([])
const enrollments = ref([])
const drivingLessons = ref([])
const groups = ref([])
const categories = ref([])
const cars = ref([])

const theorySearchQuery = ref('')
const theoryTeacherFilter = ref('')
const theoryGroupFilter = ref('')
const theoryCategoryFilter = ref('')

const drivingSearchQuery = ref('')
const drivingDateFrom = ref('')
const drivingDateTo = ref('')
const drivingInstructorFilter = ref('')
const drivingGroupFilter = ref('')
const drivingCarFilter = ref('')

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

// One row per student enrolled with a theory teacher (coordinator) assigned.
const filteredTheoryEnrollments = computed(() => {
  const q = theorySearchQuery.value.trim().toLowerCase()
  return enrollments.value.filter(e => {
    if (!e.coordinator) return false
    if (ownStaffId.value && e.coordinator !== ownStaffId.value) return false
    if (!branchStore.isBranchMatch(e)) return false
    if (theoryTeacherFilter.value && e.coordinator !== theoryTeacherFilter.value) return false
    if (theoryGroupFilter.value && e.group !== theoryGroupFilter.value) return false
    if (theoryCategoryFilter.value && e.category !== theoryCategoryFilter.value) return false
    if (!q) return true
    return (e.student_name || '').toLowerCase().includes(q) || (e.student_phone || '').includes(q)
  })
})

// Look up a student's current enrollment (group + category) for filtering/display
function getStudentEnrollment(studentId) {
  if (!studentId) return null
  return enrollments.value.find(e => e.student === studentId && e.group) || null
}

const filteredDrivingLessons = computed(() => {
  const q = drivingSearchQuery.value.trim().toLowerCase()
  const from = drivingDateFrom.value
  const to = drivingDateTo.value
  return drivingLessons.value.filter(l => {
    if (ownStaffId.value && l.instructor !== ownStaffId.value) return false
    if (!branchStore.isBranchMatch(l)) return false
    if (drivingInstructorFilter.value && l.instructor !== drivingInstructorFilter.value) return false
    if (drivingGroupFilter.value) {
      const enr = getStudentEnrollment(l.student)
      if (!enr || enr.group !== drivingGroupFilter.value) return false
    }
    if (drivingCarFilter.value && l.car !== drivingCarFilter.value) return false
    if (from && l.lesson_date && l.lesson_date.slice(0, 10) < from) return false
    if (to && l.lesson_date && l.lesson_date.slice(0, 10) > to) return false
    if (!q) return true
    return (l.student_name || '').toLowerCase().includes(q) ||
      (l.instructor_name || '').toLowerCase().includes(q) ||
      (l.car_name || '').toLowerCase().includes(q) ||
      (l.notes || '').toLowerCase().includes(q)
  })
})

// Look up a student's current group (name + start/end dates) via their enrollment
function getStudentGroupInfo(studentId) {
  const enr = getStudentEnrollment(studentId)
  if (!enr) return null
  const group = groupsById.value[enr.group]
  return {
    group_name: enr.group_name || (group ? group.name : ''),
    started_at: group ? group.started_at : null,
    ends_at: group ? group.ends_at : null,
  }
}

async function fetchData() {
  loading.value = true
  try {
    const [coordRes, instRes, enrRes, drvRes, grpRes, catRes, carRes] = await Promise.all([
      api.get('/users/', { params: { role: 'coordinator', page_size: 1000 } }),
      api.get('/users/', { params: { role: 'instructor', page_size: 1000 } }),
      api.get('/enrollments/', { params: { page_size: 1000 } }),
      api.get('/driving-lessons/', { params: { page_size: 1000 } }),
      api.get('/groups/', { params: { page_size: 1000 } }),
      api.get('/categories/', { params: { page_size: 100 } }),
      api.get('/cars/', { params: { page_size: 1000 } })
    ])

    theoryTeachers.value = coordRes.data.results || coordRes.data || []
    drivingInstructors.value = instRes.data.results || instRes.data || []
    enrollments.value = enrRes.data.results || enrRes.data || []
    drivingLessons.value = drvRes.data.results || drvRes.data || []
    groups.value = grpRes.data.results || grpRes.data || []
    categories.value = catRes.data.results || catRes.data || []
    cars.value = carRes.data.results || carRes.data || []
  } catch (err) {
    console.error("Darslar ma'lumotlarini yuklashda xatolik:", err)
  } finally {
    loading.value = false
  }
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
.toolbar-card { background: white; border: 1px solid #E5E7EB; border-radius: 14px; padding: 14px 20px; display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.search-box { display: flex; align-items: center; gap: 10px; background: #F9FAFB; border: 1.5px solid #E5E7EB; border-radius: 10px; padding: 8px 14px; width: 300px; }
.search-input { border: none; background: transparent; outline: none; font-size: 13.5px; width: 100%; }
.total-count { font-size: 13px; color: #6B7280; white-space: nowrap; }
.filter-controls { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.filter-item { display: flex; align-items: center; gap: 8px; }
.filter-label { font-size: 12.5px; font-weight: 600; color: #4B5563; white-space: nowrap; }

.table-section-card { background: white; border: 1px solid #E5E7EB; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.table-container { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; th { background: #F9FAFB; padding: 13px 16px; font-size: 12px; font-weight: 700; color: #4B5563; text-align: left; border-bottom: 1px solid #E5E7EB; } td { padding: 14px 16px; font-size: 13.5px; color: #1F2937; border-bottom: 1px solid #F3F4F6; vertical-align: middle; } }

.instructor-badge { padding: 4px 10px; background: #F3E8FF; color: #7E22CE; border-radius: 8px; font-size: 12px; font-weight: 700; }
.car-badge { padding: 4px 10px; background: #DCFCE7; color: #15803D; border-radius: 8px; font-size: 12px; font-weight: 700; }
.link-value { cursor: pointer; }
.link-value:hover { text-decoration: underline; }
.status-badge-pill { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; display: inline-block; }
.status-badge-pill.available { background: #DCFCE7; color: #15803D; }

.font-bold { font-weight: 700; }
.text-dark { color: #0F172A; }
.cat-chip { padding: 3px 8px; background: #F1F5F9; color: #334155; border-radius: 6px; font-weight: 700; font-size: 11.5px; }
.time-chip { padding: 3px 8px; background: #FEF3C7; color: #D97706; border-radius: 6px; font-weight: 600; font-size: 12px; }
.days-chip { font-size: 12px; color: #475569; }
.notes-text { font-size: 12.5px; color: #64748B; }

.state-box, .empty-state { text-align: center; padding: 40px 0; color: #6B7280; }
.spinner { width: 28px; height: 28px; border: 3px solid #E5E7EB; border-top-color: #4F46E5; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px; }
@keyframes spin { to { transform: rotate(360deg); } }

.group-filter-select { padding: 6px 12px; border: 1.5px solid #E5E7EB; border-radius: 8px; background: #F9FAFB; font-size: 12.5px; font-weight: 500; color: #111827; cursor: pointer; outline: none; }

/* Date range filter (driving tab) */
.date-range-box { display: flex; align-items: center; gap: 8px; }
.date-range-label { font-size: 12.5px; font-weight: 600; color: #4B5563; }
.date-range-input { padding: 6px 10px; border: 1.5px solid #E5E7EB; border-radius: 8px; background: #F9FAFB; font-size: 12.5px; color: #111827; outline: none; }
.date-range-sep { color: #9CA3AF; font-size: 12px; }
.date-range-clear { border: none; background: #F3F4F6; color: #6B7280; border-radius: 6px; width: 22px; height: 22px; cursor: pointer; font-size: 11px; line-height: 1; }
.date-range-clear:hover { background: #E5E7EB; color: #111827; }

/* Group column in driving lessons table */
.group-badge { padding: 3px 9px; background: #E0E7FF; color: #4338CA; border-radius: 8px; font-size: 11.5px; font-weight: 700; display: inline-block; }
.group-dates { font-size: 11px; color: #6B7280; margin-top: 3px; }
.text-muted { color: #9CA3AF; }
</style>
