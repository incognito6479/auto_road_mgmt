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
      <!-- Metric cards -->
      <div class="metrics-cards-grid">
        <div class="card-metric card-green">
          <div class="card-metric-icon">👥</div>
          <div>
            <span class="metric-lbl">Biriktirilgan O'quvchilar</span>
            <h4 class="metric-val text-green">{{ enrollments.length }} ta o'quvchi</h4>
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

      <!-- Students table -->
      <div class="table-section-card">
        <div class="toolbar-bar">
          <h3 class="section-title">O'quvchilar Ro'yxati</h3>
          <div class="search-box">
            <svg viewBox="0 0 20 20" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
              <circle cx="8.5" cy="8.5" r="5.5"/>
              <line x1="13" y1="13" x2="18" y2="18"/>
            </svg>
            <input v-model="searchQuery" type="text" placeholder="O'quvchi F.I.SH..." class="search-input" />
          </div>

          <div class="filter-item">
            <label class="flabel">Holati:</label>
            <div class="select-wrap-relative">
              <select v-model="filterStatus" class="fselect-field">
                <option value="">Barcha holatlar</option>
                <option value="new">Yangi</option>
                <option value="enrolled">Faol</option>
                <option value="finished">Tugatgan</option>
                <option value="canceled">Bekor qilingan</option>
              </select>
              <div class="select-chevron-icon">▼</div>
            </div>
          </div>

          <div class="filter-item">
            <label class="flabel">Kategoriya:</label>
            <div class="select-wrap-relative">
              <select v-model="filterCategory" class="fselect-field">
                <option value="">Barchasi</option>
                <option v-for="c in categoryOptions" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
              <div class="select-chevron-icon">▼</div>
            </div>
          </div>

          <div class="filter-item">
            <label class="flabel">Guruh:</label>
            <div class="select-wrap-relative">
              <select v-model="filterGroup" class="fselect-field">
                <option value="">Barchasi</option>
                <option v-for="g in groupOptions" :key="g.id" :value="g.id">{{ g.name }}</option>
              </select>
              <div class="select-chevron-icon">▼</div>
            </div>
          </div>

          <div class="total-count">
            Jami: <strong>{{ filteredEnrollments.length }}</strong> ta
          </div>
        </div>

        <div class="table-container">
          <div v-if="filteredEnrollments.length === 0" class="empty-state">
            <p>Ushbu o'quv joyiga biriktirilgan o'quvchilar topilmadi</p>
          </div>

          <table v-else class="data-table">
            <thead>
              <tr>
                <th>O'quvchi F.I.SH.</th>
                <th>Kategoriya / Guruh</th>
                <th>Instruktor</th>
                <th>O'qituvchi</th>
                <th>O'quv vaqti</th>
                <th>Dars kunlari</th>
                <th class="th-sortable" @click="toggleEnrolledSort" title="Ro'yxatdan o'tgan sana bo'yicha saralash">
                  Ro'yxatdan o'tgan
                  <span class="sort-arrow" :class="{ active: true }">{{ enrolledSortAsc ? '▲' : '▼' }}</span>
                </th>
                <th>Shartnoma</th>
                <th>To'langan</th>
                <th>Qarzdorlik</th>
                <th>Holati</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="e in filteredEnrollments" :key="e.id" class="table-row">
                <td class="td-name">
                  <div class="student-name-link" @click="goStudent(e.student)">{{ e.student_name || "Noma'lum" }}</div>
                  <div v-if="e.student_phone" class="student-sub">📞 {{ formatPhone(e.student_phone) }}</div>
                </td>
                <td>
                  <span class="cat-pill">{{ e.category_name || '-' }}</span>
                  <div v-if="e.group_name" class="group-sub">{{ e.group_name }}</div>
                </td>
                <td class="td-muted">{{ e.instructor_name || '-' }}</td>
                <td class="td-muted">{{ e.coordinator_name || '-' }}</td>
                <td class="td-muted">{{ e.learning_time || '-' }}</td>
                <td class="td-muted td-days">{{ daysText(e.learning_days) }}</td>
                <td class="td-muted td-date">{{ formatDate(e.created_at) }}</td>
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
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { formatMoney, formatPhone, formatDate } from '@/utils/formatters'

const route = useRoute()
const router = useRouter()

const place = ref(null)
const enrollments = ref([])
const loading = ref(true)
const error = ref('')
const searchQuery = ref('')
const filterStatus = ref('')
const filterCategory = ref('')
const filterGroup = ref('')
// Newest enrolments first by default — that is what staff usually want to see.
const enrolledSortAsc = ref(false)

const getDebt = (e) => {
  if (!e || e.enrolled_free) return 0
  const contract = Number(e.enrolled_amount) || 0
  const paid = Number(e.paid_amount) || 0
  return Math.max(0, contract - paid)
}

// Distinct category/group options among this place's own enrollments — no
// point offering a filter value that would match nothing here.
const categoryOptions = computed(() => {
  const map = {}
  enrollments.value.forEach(e => {
    if (e.category && !map[e.category]) map[e.category] = { id: e.category, name: e.category_name || `#${e.category}` }
  })
  return Object.values(map).sort((a, b) => a.name.localeCompare(b.name))
})

const groupOptions = computed(() => {
  const map = {}
  enrollments.value.forEach(e => {
    if (e.group && !map[e.group]) map[e.group] = { id: e.group, name: e.group_name || `#${e.group}` }
  })
  return Object.values(map).sort((a, b) => a.name.localeCompare(b.name))
})

// Metric cards reflect the active filters, not the place's full roster.
const activeCount = computed(() => filteredEnrollments.value.filter(e => e.status === 'enrolled').length)
const totalPaid = computed(() => filteredEnrollments.value.reduce((s, e) => s + (Number(e.paid_amount) || 0), 0))
const totalDebt = computed(() => filteredEnrollments.value.reduce((s, e) => s + getDebt(e), 0))

const filteredEnrollments = computed(() => {
  const q = searchQuery.value.toLowerCase().trim()
  const status = filterStatus.value

  const rows = enrollments.value.filter(e => {
    if (status && e.status !== status) return false
    if (filterCategory.value && e.category !== filterCategory.value) return false
    if (filterGroup.value && e.group !== filterGroup.value) return false
    if (!q) return true
    return (e.student_name || '').toLowerCase().includes(q) ||
      (e.group_name || '').toLowerCase().includes(q) ||
      (e.category_name || '').toLowerCase().includes(q)
  })

  // Sort by enrolment date. Rows with no date sink to the bottom either way.
  const dir = enrolledSortAsc.value ? 1 : -1
  return rows.slice().sort((a, b) => {
    const ta = a.created_at ? new Date(a.created_at).getTime() : null
    const tb = b.created_at ? new Date(b.created_at).getTime() : null
    if (ta === null && tb === null) return 0
    if (ta === null) return 1
    if (tb === null) return -1
    return (ta - tb) * dir
  })
})

function toggleEnrolledSort() {
  enrolledSortAsc.value = !enrolledSortAsc.value
}

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

async function fetchAll() {
  loading.value = true
  error.value = ''
  try {
    const [placeRes, enrRes] = await Promise.all([
      api.get(`/learning-places/${route.params.id}/`),
      api.get('/enrollments/', { params: { learning_place: route.params.id, page_size: 1000 } }),
    ])
    place.value = placeRes.data
    enrollments.value = enrRes.data.results ? enrRes.data.results : enrRes.data
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

.info-card { background: white; border: 1px solid #E5E7EB; border-radius: 16px; padding: 20px 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.section-title { font-size: 15px; font-weight: 700; color: #111827; margin-bottom: 14px; }
.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; }
.info-item { display: flex; flex-direction: column; gap: 4px; }
.info-lbl { font-size: 12px; color: #6B7280; font-weight: 600; }
.info-val { font-size: 14px; color: #111827; font-weight: 600; }

.table-section-card { background: white; border: 1px solid #E5E7EB; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.toolbar-bar { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid #E5E7EB; gap: 16px; flex-wrap: wrap; }
.toolbar-bar .section-title { margin-bottom: 0; }
.search-box { display: flex; align-items: center; gap: 10px; background: #F9FAFB; border: 1.5px solid #E5E7EB; border-radius: 10px; padding: 9px 14px; width: 280px; }
.search-box:focus-within { border-color: #2D6A4F; background: white; box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.12); }
.search-input { border: none; background: transparent; outline: none; font-size: 13.5px; width: 100%; }
.total-count { font-size: 13px; color: #6B7280; }

.filter-item { display: flex; align-items: center; gap: 6px; }
.flabel { font-size: 12.5px; font-weight: 600; color: #374151; white-space: nowrap; }
.select-wrap-relative { position: relative; }
.fselect-field {
  padding: 9px 32px 9px 12px;
  border: 1.5px solid #E5E7EB;
  border-radius: 10px;
  font-size: 13.5px;
  background: #FAFAFA;
  color: #111827;
  outline: none;
  appearance: none;
  -webkit-appearance: none;
  cursor: pointer;
  transition: all 0.2s ease;
}
.fselect-field:focus { border-color: #2D6A4F; background: #fff; box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.12); }
.select-chevron-icon { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #9CA3AF; font-size: 10px; }

.th-sortable { cursor: pointer; user-select: none; }
.th-sortable:hover { color: #2D6A4F; }
.sort-arrow { margin-left: 4px; font-size: 9px; color: #9CA3AF; }
.sort-arrow.active { color: #2D6A4F; }
.td-date { white-space: nowrap; }
.td-days { white-space: nowrap; }

.table-container { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: #F9FAFB; padding: 13px 16px; font-size: 12px; font-weight: 700; color: #4B5563; text-align: left; border-bottom: 1px solid #E5E7EB; white-space: nowrap; }
.data-table td { padding: 14px 16px; font-size: 13.5px; color: #1F2937; border-bottom: 1px solid #F3F4F6; vertical-align: middle; }

.student-name-link { font-weight: 700; color: #111827; cursor: pointer; }
.student-name-link:hover { color: #2D6A4F; text-decoration: underline; }
.student-sub { font-size: 11.5px; color: #6B7280; margin-top: 2px; }
.td-muted { color: #6B7280; }
.td-amount { font-weight: 600; white-space: nowrap; }
.cat-pill { padding: 4px 10px; background: #E8F5E9; color: #2D6A4F; border-radius: 8px; font-size: 12px; font-weight: 700; }
.group-sub { font-size: 11.5px; color: #6B7280; margin-top: 2px; }
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

.state-box { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 20px; gap: 12px; background: white; border-radius: 16px; color: #6B7280; }
.state-error p { color: #DC2626; }
.empty-state { text-align: center; padding: 40px 0; color: #6B7280; }
.spinner { width: 30px; height: 30px; border: 3px solid #E5E7EB; border-top-color: #2D6A4F; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.btn-retry { padding: 8px 16px; background: #2D6A4F; color: white; border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; }
</style>
