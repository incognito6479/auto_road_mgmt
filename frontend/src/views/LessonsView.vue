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
        <span class="tab-badge blue-badge">{{ filteredTheoryTeachers.length }}</span>
      </button>

      <button
        class="tab-btn"
        :class="{ active: activeTab === 'driving' }"
        @click="activeTab = 'driving'"
      >
        <span class="tab-icon">🏎️</span>
        <span>Amaliy Haydash (Driving lesson)</span>
        <span class="tab-badge purple-badge">{{ drivingLessons.length }} ta dars</span>
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
            placeholder="Nazariya o'qituvchisi ismini kiriting..."
            class="search-input"
          />
        </div>

        <div class="total-count">
          Jami: <strong>{{ filteredTheoryTeachers.length }}</strong> ta nazariya o'qituvchisi
        </div>
      </div>

      <div v-if="loading" class="state-box">
        <div class="spinner"></div>
        <span>Nazariya darslari ma'lumotlari yuklanmoqda...</span>
      </div>

      <div v-else-if="filteredTheoryTeachers.length === 0" class="empty-state">
        <p>Nazariya o'qituvchilari topilmadi</p>
      </div>

      <div v-else class="teachers-grid">
        <div v-for="teacher in filteredTheoryTeachers" :key="teacher.id" class="teacher-card">
          <div class="teacher-card-header" @click="toggleTeacherExpand(teacher.id)">
            <div class="teacher-info">
              <div class="teacher-avatar">👨‍🏫</div>
              <div>
                <h4 class="teacher-title">{{ teacher.full_name }}</h4>
                <div class="teacher-sub">
                  <span>📞 {{ formatPhone(teacher.phone) }}</span>
                  <span v-if="teacher.passport_serie" style="margin-left: 8px;">({{ teacher.passport_serie }} {{ teacher.passport_number }})</span>
                </div>
              </div>
            </div>

            <div class="header-right font-bold">
              <span class="students-count-chip blue-chip">
                {{ getLinkedStudentsCount(teacher.id, 'coordinator') }} ta o'quvchi
              </span>
              <span class="chevron-icon" :class="{ rotated: expandedTeachers.has(teacher.id) }">▼</span>
            </div>
          </div>

          <!-- Linked Students List -->
          <div v-if="expandedTeachers.has(teacher.id)" class="students-list-wrap">
            <div v-if="getLinkedStudents(teacher.id, 'coordinator').length === 0" class="no-students">
              Ushbu o'qituvchiga hozirda o'quvchilar biriktirilmagan
            </div>

            <table v-else class="students-table">
              <thead>
                <tr>
                  <th>O'quvchi F.I.SH.</th>
                  <th>Telefon</th>
                  <th>Kategoriya / Guruh</th>
                  <th>Dars Vaqti</th>
                  <th>Dars Kunlari</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="enr in getLinkedStudents(teacher.id, 'coordinator')" :key="enr.id">
                  <td class="font-bold text-dark">{{ enr.student_name }}</td>
                  <td>{{ formatPhone(enr.student_phone) }}</td>
                  <td>
                    <span class="cat-chip">{{ enr.category_name }}</span>
                    <span v-if="enr.group_name" class="group-sub">{{ enr.group_name }}</span>
                  </td>
                  <td>
                    <span v-if="enr.learning_time" class="time-chip">⏰ {{ enr.learning_time }}</span>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td>
                    <span v-if="enr.learning_days" class="days-chip">{{ formatDays(enr.learning_days) }}</span>
                    <span v-else class="text-muted">-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
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
                <th style="width: 120px;">Holati</th>
                <th>Izoh / Eslatmalari</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="lesson in filteredDrivingLessons" :key="lesson.id" class="table-row">
                <td class="td-id">#{{ lesson.id }}</td>
                <td class="font-bold">📅 {{ formatDate(lesson.lesson_date) }}</td>
                <td class="font-bold text-dark">👤 {{ lesson.student_name }}</td>
                <td><span class="instructor-badge">🏎️ {{ lesson.instructor_name }}</span></td>
                <td><span class="car-badge font-bold">🚘 {{ lesson.car_name || '-' }}</span></td>
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
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useBranchStore } from '@/stores/branch'
import { formatPhone } from '@/utils/formatters'

const branchStore = useBranchStore()
const activeTab = ref('theory')
const loading = ref(true)

const theoryTeachers = ref([])
const drivingInstructors = ref([])
const enrollments = ref([])
const drivingLessons = ref([])

const theorySearchQuery = ref('')
const drivingSearchQuery = ref('')

const expandedTeachers = ref(new Set())
const expandedInstructors = ref(new Set())

const filteredTheoryTeachers = computed(() => {
  const q = theorySearchQuery.value.trim().toLowerCase()
  return theoryTeachers.value.filter(t => {
    if (!branchStore.isBranchMatch(t)) return false
    if (!q) return true
    return (t.full_name || '').toLowerCase().includes(q) || (t.phone || '').includes(q)
  })
})

const filteredDrivingLessons = computed(() => {
  const q = drivingSearchQuery.value.trim().toLowerCase()
  return drivingLessons.value.filter(l => {
    if (!branchStore.isBranchMatch(l)) return false
    if (!q) return true
    return (l.student_name || '').toLowerCase().includes(q) ||
      (l.instructor_name || '').toLowerCase().includes(q) ||
      (l.car_name || '').toLowerCase().includes(q) ||
      (l.notes || '').toLowerCase().includes(q)
  })
})

async function fetchData() {
  loading.value = true
  try {
    const [coordRes, instRes, enrRes, drvRes] = await Promise.all([
      api.get('/users/', { params: { role: 'coordinator', page_size: 100 } }),
      api.get('/users/', { params: { role: 'instructor', page_size: 100 } }),
      api.get('/enrollments/', { params: { page_size: 200 } }),
      api.get('/driving-lessons/', { params: { page_size: 200 } })
    ])

    theoryTeachers.value = coordRes.data.results || coordRes.data || []
    drivingInstructors.value = instRes.data.results || instRes.data || []
    enrollments.value = enrRes.data.results || enrRes.data || []
    drivingLessons.value = drvRes.data.results || drvRes.data || []

    // Auto-expand all teachers by default
    theoryTeachers.value.forEach(t => expandedTeachers.value.add(t.id))
    drivingInstructors.value.forEach(i => expandedInstructors.value.add(i.id))
  } catch (err) {
    console.error("Darslar ma'lumotlarini yuklashda xatolik:", err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})

function toggleTeacherExpand(id) {
  if (expandedTeachers.value.has(id)) {
    expandedTeachers.value.delete(id)
  } else {
    expandedTeachers.value.add(id)
  }
}

function getLinkedStudents(staffId, roleType) {
  if (roleType === 'coordinator') {
    return enrollments.value.filter(e => e.coordinator === staffId)
  } else if (roleType === 'instructor') {
    return enrollments.value.filter(e => e.instructor === staffId)
  }
  return []
}

function getLinkedStudentsCount(staffId, roleType) {
  return getLinkedStudents(staffId, roleType).length
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const parts = dateStr.split('-')
  if (parts.length === 3) return `${parts[2]}.${parts[1]}.${parts[0]}`
  return dateStr
}

function formatDays(dayStr) {
  if (!dayStr) return '-'
  if (dayStr === 'Mo-Wed-Fri') return 'Dushanba - Chorshanba - Juma (Mo-Wed-Fri)'
  if (dayStr === 'Tue-Thu-Sat') return 'Seshanba - Payshanba - Shanba (Tue-Thu-Sat)'
  if (dayStr === 'everyday') return 'Har kuni (Har kuni)'
  return dayStr
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
.toolbar-card { background: white; border: 1px solid #E5E7EB; border-radius: 14px; padding: 14px 20px; display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.search-box { display: flex; align-items: center; gap: 10px; background: #F9FAFB; border: 1.5px solid #E5E7EB; border-radius: 10px; padding: 8px 14px; width: 360px; }
.search-input { border: none; background: transparent; outline: none; font-size: 13.5px; width: 100%; }
.total-count { font-size: 13px; color: #6B7280; }

.table-section-card { background: white; border: 1px solid #E5E7EB; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.table-container { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; th { background: #F9FAFB; padding: 13px 16px; font-size: 12px; font-weight: 700; color: #4B5563; text-align: left; border-bottom: 1px solid #E5E7EB; } td { padding: 14px 16px; font-size: 13.5px; color: #1F2937; border-bottom: 1px solid #F3F4F6; vertical-align: middle; } }

.instructor-badge { padding: 4px 10px; background: #F3E8FF; color: #7E22CE; border-radius: 8px; font-size: 12px; font-weight: 700; }
.car-badge { padding: 4px 10px; background: #DCFCE7; color: #15803D; border-radius: 8px; font-size: 12px; font-weight: 700; }
.status-badge-pill { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; display: inline-block; }
.status-badge-pill.available { background: #DCFCE7; color: #15803D; }

.teachers-grid { display: flex; flex-direction: column; gap: 18px; }
.teacher-card { background: white; border: 1.5px solid #E5E7EB; border-radius: 16px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.03); transition: border-color 0.2s ease; }
.teacher-card:hover { border-color: #CBD5E1; }

.teacher-card-header { padding: 18px 22px; background: #FAFAFA; display: flex; align-items: center; justify-content: space-between; cursor: pointer; user-select: none; border-bottom: 1px solid #E5E7EB; }
.teacher-info { display: flex; align-items: center; gap: 14px; }
.teacher-avatar { font-size: 28px; width: 44px; height: 44px; background: white; border: 1px solid #E2E8F0; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.teacher-title { font-size: 16px; font-weight: 700; color: #1E293B; }
.teacher-sub { font-size: 12.5px; color: #64748B; margin-top: 2px; }

.header-right { display: flex; align-items: center; gap: 14px; }
.students-count-chip { padding: 5px 14px; border-radius: 20px; font-size: 12.5px; font-weight: 700; }
.purple-chip { background: #F3E8FF; color: #7E22CE; }
.blue-chip { background: #DBEAFE; color: #1D4ED8; }
.chevron-icon { font-size: 12px; color: #94A3B8; transition: transform 0.2s ease; }
.chevron-icon.rotated { transform: rotate(180deg); }

.students-list-wrap { padding: 16px 22px; background: white; }
.no-students { text-align: center; padding: 20px; color: #94A3B8; font-size: 13px; font-style: italic; }
.students-table { width: 100%; border-collapse: collapse; th { background: #F8FAFC; padding: 10px 14px; font-size: 11.5px; font-weight: 700; color: #64748B; text-align: left; border-bottom: 1px solid #E2E8F0; } td { padding: 12px 14px; font-size: 13px; color: #334155; border-bottom: 1px solid #F1F5F9; vertical-align: middle; } }
.font-bold { font-weight: 700; }
.text-dark { color: #0F172A; }
.cat-chip { padding: 3px 8px; background: #F1F5F9; color: #334155; border-radius: 6px; font-weight: 700; font-size: 11.5px; }
.group-sub { margin-left: 6px; font-size: 12px; color: #64748B; }
.time-chip { padding: 3px 8px; background: #FEF3C7; color: #D97706; border-radius: 6px; font-weight: 600; font-size: 12px; }
.days-chip { font-size: 12px; color: #475569; }
.notes-text { font-size: 12.5px; color: #64748B; }

.state-box, .empty-state { text-align: center; padding: 40px 0; color: #6B7280; }
.spinner { width: 28px; height: 28px; border: 3px solid #E5E7EB; border-top-color: #4F46E5; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
