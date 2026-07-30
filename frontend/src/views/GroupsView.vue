<template>
  <AppLayout>

    <!-- Toolbar: Search and Category Filter -->
    <div class="groups-toolbar">
      <div class="search-box">
        <svg viewBox="0 0 20 20" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
          <circle cx="8.5" cy="8.5" r="5.5"/>
          <line x1="13" y1="13" x2="18" y2="18"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Guruh nomi yoki kategoriya bo'yicha qidirish..."
          class="search-input"
        />
      </div>

      <div class="filter-group">
        <label class="filter-label">Kategoriya:</label>
        <div class="select-wrap">
          <select v-model="selectedCategory" class="filter-select">
            <option value="">Barcha kategoriyalar</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }} kategoriyasi
            </option>
          </select>
        </div>
      </div>

      <div class="filter-group">
        <label class="filter-label">Holati:</label>
        <div class="select-wrap">
          <select v-model="selectedStatus" class="filter-select">
            <option value="">Barcha holatlar</option>
            <option value="started">Boshlangan</option>
            <option value="finished">Tugatgan</option>
            <option value="canceled">Bekor qilingan</option>
          </select>
        </div>
      </div>

      <div class="filter-group date-range-group">
        <label class="filter-label">Boshlanish sanasi:</label>
        <input v-model="startDateFrom" type="date" class="filter-date-input" />
        <span class="date-range-sep">—</span>
        <input v-model="startDateTo" type="date" class="filter-date-input" />
        <button v-if="startDateFrom || startDateTo" type="button" class="btn-clear-date" @click="startDateFrom = ''; startDateTo = ''" title="Tozalash">✕</button>
      </div>

      <div class="filter-group date-range-group">
        <label class="filter-label">Tugash sanasi:</label>
        <input v-model="endDateFrom" type="date" class="filter-date-input" />
        <span class="date-range-sep">—</span>
        <input v-model="endDateTo" type="date" class="filter-date-input" />
        <button v-if="endDateFrom || endDateTo" type="button" class="btn-clear-date" @click="endDateFrom = ''; endDateTo = ''" title="Tozalash">✕</button>
      </div>

      <div class="total-count">
        Jami: <strong>{{ filteredGroups.length }}</strong> ta guruh
      </div>

      <button v-if="authStore.isAdminOrSuperuser" class="btn-start-new-group" @click="openStartGroupModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="16" height="16">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        Guruhni boshlash
      </button>
    </div>

    <!-- Loading, error, or empty states -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">Guruhlar yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchGroups">Qayta urinish</button>
    </div>

    <div v-else-if="filteredGroups.length === 0" class="state-container">
      <p class="state-text">Mos guruhlar topilmadi.</p>
    </div>

    <!-- Groups table -->
    <div v-else class="table-wrap">
      <table class="groups-table">
        <thead>
          <tr>
            <th>Guruh nomi</th>
            <th>Kategoriya</th>
            <th>Boshlanish sanasi</th>
            <th>Tugash sanasi</th>
            <th>Ish kunlari</th>
            <th>Dars kunlari</th>
            <th>Davomiyligi</th>
            <th>O'quvchilar soni</th>
            <th>Holati</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="g in filteredGroups" :key="g.id" class="clickable-row" @click="router.push({ name: 'group-detail', params: { id: g.id } })">
            <td class="font-semibold">
              <div class="group-name-cell">
                <div class="group-icon-wrap group-icon-wrap-sm">
                  <svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="1.8" width="18" height="18">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                    <circle cx="9" cy="7" r="4" />
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                  </svg>
                </div>
                {{ g.name }}
              </div>
            </td>
            <td><span class="group-cat-badge">{{ g.category_name }}</span></td>
            <td>{{ formatDate(g.started_at) }}</td>
            <td class="font-semibold">{{ g.ends_at ? formatDate(g.ends_at) : '-' }}</td>
            <td class="font-semibold">{{ g.working_days ? g.working_days + ' kun' : '-' }}</td>
            <td>{{ weekdaysText(g) }}</td>
            <td class="highlight">{{ g.duration ? g.duration + ' oy' : '-' }}</td>
            <td>{{ g.student_count }} ta</td>
            <td>
              <span class="status-badge" :class="statusClass(g.status)">
                {{ statusText(g.status) }}
              </span>
            </td>
            <td>
              <div class="group-row-actions">
                <button v-if="authStore.isAdminOrSuperuser" class="btn-edit-group" @click.stop="openEditModal(g)" title="Tahrirlash">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
                <button class="btn-view" @click.stop="router.push({ name: 'group-detail', params: { id: g.id } })">
                  Ko'rish
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit Group Dialog -->
    <dialog ref="editGroupModal" class="modal-dialog" closedby="any" aria-labelledby="edit-modal-title">
      <form class="modal-form" @submit.prevent="updateGroup">
        <h3 id="edit-modal-title" class="modal-title">Guruhni tahrirlash</h3>
        
        <div v-if="editModalError" class="modal-error">
          {{ editModalError }}
        </div>
        
        <div class="form-group">
          <label for="edit-grp-name" class="form-label">Guruh nomi</label>
          <input
            id="edit-grp-name"
            v-model="editingGroup.name"
            type="text"
            required
            class="form-input"
          />
        </div>
        
        <div class="form-group">
          <label for="edit-grp-start" class="form-label">Boshlanish sanasi</label>
          <input
            id="edit-grp-start"
            v-model="editingGroup.started_at"
            type="date"
            required
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="edit-grp-working-days" class="form-label">Ish kunlari soni</label>
          <input
            id="edit-grp-working-days"
            v-model="editingGroup.working_days"
            type="number"
            placeholder="68"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label class="form-label">Dars kunlari (Dushanba - Shanba)</label>
          <div class="weekday-picker">
            <label v-for="d in weekdayOptions" :key="d.value" class="weekday-chip" :class="{ active: editingGroup.selected_weekdays.includes(d.value) }">
              <input type="checkbox" :value="d.value" v-model="editingGroup.selected_weekdays" style="display: none;" />
              {{ d.label }}
            </label>
          </div>
        </div>

        <div class="form-group" v-if="editingGroup.ends_at">
          <label class="form-label">Tugash sanasi</label>
          <div class="form-input" style="background: #F9FAFB; color: #374151; font-weight: 600;">{{ formatDate(editingGroup.ends_at) }}</div>
        </div>

        <div class="form-group">
          <label for="edit-grp-status" class="form-label">Holati</label>
          <div class="select-wrap" style="position: relative; display: flex; width: 100%;">
            <select id="edit-grp-status" v-model="editingGroup.status" required class="form-input select-input" style="width: 100%; appearance: none; -webkit-appearance: none;">
              <option value="started">Boshlangan</option>
              <option value="finished">Tugatgan</option>
              <option value="canceled">Bekor qilingan</option>
            </select>
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #6B7280;">
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
            </svg>
          </div>
        </div>
        
        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closeEditModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="editSaving">
            <span v-if="editSaving" class="btn-spinner"></span>
            {{ editSaving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Start New Group Dialog -->
    <dialog ref="startGroupModal" class="modal-dialog start-group-dialog" closedby="any" aria-labelledby="start-group-modal-title">
      <form class="modal-form" @submit.prevent="submitStartGroup">
        <h3 id="start-group-modal-title" class="modal-title">Yangi guruh boshlash</h3>

        <div v-if="startGroupError" class="modal-error">{{ startGroupError }}</div>

        <div class="form-group">
          <label for="start-grp-category" class="form-label">Kategoriya</label>
          <div class="select-wrap" style="position: relative; display: flex; width: 100%;">
            <select
              id="start-grp-category"
              v-model="startGroupCategoryId"
              @change="onStartGroupCategoryChange"
              required
              class="form-input select-input"
              style="width: 100%; appearance: none; -webkit-appearance: none;"
            >
              <option value="" disabled>Kategoriyani tanlang</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #6B7280;">
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
            </svg>
          </div>
        </div>

        <template v-if="startGroupCategoryId">
          <div class="waiting-students-section">
            <div class="waiting-students-header">
              <span class="waiting-count-label">
                Navbatdagi o'quvchilar: <strong>{{ waitingStudents.length }}</strong> ta
                &middot; Tanlangan: <strong :class="{ 'count-ok': selectedWaitingIds.length === 23 || selectedWaitingIds.length === 24 }">{{ selectedWaitingIds.length }}</strong> ta
              </span>
              <label v-if="waitingStudents.length > 0" class="select-all-label">
                <input type="checkbox" :checked="isAllWaitingSelected" @change="toggleSelectAllWaiting" />
                Barchasini tanlash
              </label>
            </div>

            <p
              v-if="selectedWaitingIds.length > 0 && selectedWaitingIds.length !== 23 && selectedWaitingIds.length !== 24"
              class="waiting-hint waiting-hint-warn"
            >
              Guruhni boshlash uchun aynan 23 yoki 24 ta o'quvchi tanlanishi kerak.
            </p>
            <p v-else-if="selectedWaitingIds.length === 23 || selectedWaitingIds.length === 24" class="waiting-hint waiting-hint-ok">
              ✓ Guruhni boshlash mumkin ({{ selectedWaitingIds.length }} ta o'quvchi tanlandi)
            </p>

            <div v-if="loadingWaitingStudents" class="state-box-inline">Yuklanmoqda...</div>
            <div v-else-if="waitingStudents.length === 0" class="state-box-inline">Ushbu kategoriyada navbatdagi o'quvchilar topilmadi.</div>

            <div v-else class="waiting-students-table-wrap">
              <table class="waiting-students-table">
                <thead>
                  <tr>
                    <th style="width: 30px;"></th>
                    <th>F.I.SH.</th>
                    <th>Telefon</th>
                    <th>Ro'yxatdan o'tgan</th>
                    <th>To'langan</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="s in waitingStudents" :key="s.id">
                    <td><input type="checkbox" :value="s.id" v-model="selectedWaitingIds" /></td>
                    <td class="font-semibold">{{ s.full_name }}</td>
                    <td>{{ formatPhone(s.phone) }}</td>
                    <td>{{ formatDate(s.date_joined || s.created_at) }}</td>
                    <td>{{ formatMoney(s.payment_amount) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="form-group">
            <label for="start-grp-name" class="form-label">Guruh nomi</label>
            <input
              id="start-grp-name"
              v-model="startGroupForm.name"
              type="text"
              required
              class="form-input"
              placeholder="Masalan: B-Guruh 1"
            />
          </div>

          <div class="form-group">
            <label for="start-grp-start" class="form-label">Boshlanish sanasi</label>
            <input
              id="start-grp-start"
              v-model="startGroupForm.started_at"
              type="date"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Dars kunlari (Dushanba - Shanba)</label>
            <div class="weekday-picker">
              <label v-for="d in weekdayOptions" :key="d.value" class="weekday-chip" :class="{ active: startGroupForm.selected_weekdays.includes(d.value) }">
                <input type="checkbox" :value="d.value" v-model="startGroupForm.selected_weekdays" style="display: none;" />
                {{ d.label }}
              </label>
            </div>
          </div>

          <div class="form-group">
            <label for="start-grp-working-days" class="form-label">Ish kunlari soni</label>
            <input
              id="start-grp-working-days"
              v-model="startGroupForm.working_days"
              type="number"
              class="form-input"
              placeholder="68"
            />
            <p class="field-hint">Tugash sanasi tanlangan dars kunlari, bayramlar va ish kunlari soniga qarab avtomatik hisoblanadi.</p>
          </div>
        </template>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closeStartGroupModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="startGroupSaving || !canSubmitStartGroup">
            <span v-if="startGroupSaving" class="btn-spinner"></span>
            {{ startGroupSaving ? 'Boshlanmoqda...' : 'Guruhni boshlash' }}
          </button>
        </div>
      </form>
    </dialog>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { formatPhone } from '@/utils/formatters'

import { useBranchStore } from '@/stores/branch'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const branchStore = useBranchStore()
const authStore = useAuthStore()

const groups = ref([])
const categories = ref([])
const searchQuery = ref('')
const selectedCategory = ref('')
const selectedStatus = ref('')
const startDateFrom = ref('')
const startDateTo = ref('')
const endDateFrom = ref('')
const endDateTo = ref('')

const loading = ref(false)
const error = ref('')

// ── Edit Group state ──────────────────────────────────
const editGroupModal = ref(null)
const editingGroup = ref({
  id: null,
  name: '',
  started_at: '',
  working_days: 68,
  working_weekends: 'mon-wed-fri',
  selected_weekdays: [0, 2, 4],
  ends_at: null,
  duration: null,
  status: 'started',
})
const editSaving = ref(false)
const editModalError = ref('')

// ── Start Group state ─────────────────────────────────
const startGroupModal = ref(null)
const startGroupCategoryId = ref('')
const waitingStudents = ref([])
const loadingWaitingStudents = ref(false)
const selectedWaitingIds = ref([])
const startGroupSaving = ref(false)
const startGroupError = ref('')
const startGroupForm = ref({
  name: '',
  started_at: '',
  working_days: 68,
  selected_weekdays: [0, 2, 4],
})

// Mon(0) - Sat(5); Sunday is never a class day.
const weekdayOptions = [
  { value: 0, label: 'Dush' },
  { value: 1, label: 'Sesh' },
  { value: 2, label: 'Chor' },
  { value: 3, label: 'Pay' },
  { value: 4, label: 'Juma' },
  { value: 5, label: 'Shan' },
]

const filteredGroups = computed(() => {
  return groups.value.filter(g => {
    const q = searchQuery.value.toLowerCase().trim()
    const matchCat = !selectedCategory.value || String(g.category) === String(selectedCategory.value) || (g.category_name && g.category_name.toLowerCase() === String(selectedCategory.value).toLowerCase())
    const matchStatus = !selectedStatus.value || g.status === selectedStatus.value
    const nameMatch = !q || (g.name || '').toLowerCase().includes(q) || (g.category_name || '').toLowerCase().includes(q)
    const matchBranch = branchStore.isBranchMatch(g)

    const startedDate = g.started_at ? g.started_at.slice(0, 10) : null
    const matchStartFrom = !startDateFrom.value || (startedDate && startedDate >= startDateFrom.value)
    const matchStartTo = !startDateTo.value || (startedDate && startedDate <= startDateTo.value)

    const endsDate = g.ends_at ? g.ends_at.slice(0, 10) : null
    const matchEndFrom = !endDateFrom.value || (endsDate && endsDate >= endDateFrom.value)
    const matchEndTo = !endDateTo.value || (endsDate && endsDate <= endDateTo.value)

    return matchCat && matchStatus && nameMatch && matchBranch && matchStartFrom && matchStartTo && matchEndFrom && matchEndTo
  })
})

const fetchCategories = async () => {
  try {
    const res = await api.get('/categories/')
    categories.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
  } catch (err) {
    console.error('Failed to fetch categories:', err)
  }
}

const fetchGroups = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api.get('/groups/?page_size=1000')
    groups.value = response.data.results ? response.data.results : response.data
  } catch (err) {
    console.error(err)
    error.value = "Guruhlarni yuklashda xatolik yuz berdi."
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('uz-UZ')
}

const formatMoney = (val) => {
  if (val === null || val === undefined || val === '') return '0'
  return Number(val).toLocaleString('uz-UZ')
}

const weekendsText = (w) => {
  switch (w) {
    case 'everyday': return 'Har kuni (Mon-Sat)'
    case 'mon-wed-fri': return 'Dush-Chorsh-Juma'
    case 'tue-wed-sat': return 'Ses-Paysh-Shanba'
    default: return w || '-'
  }
}

const weekdaysText = (g) => {
  if (Array.isArray(g.selected_weekdays) && g.selected_weekdays.length > 0) {
    return g.selected_weekdays
      .slice()
      .sort((a, b) => a - b)
      .map(v => (weekdayOptions.find(d => d.value === v) || {}).label || v)
      .join(', ')
  }
  return weekendsText(g.working_weekends)
}

const statusText = (status) => {
  if (status === 'started') return 'Boshlangan'
  if (status === 'finished') return 'Tugatgan'
  if (status === 'canceled') return 'Bekor qilingan'
  return status
}

const statusClass = (status) => {
  return {
    'badge-started': status === 'started',
    'badge-finished': status === 'finished',
    'badge-canceled': status === 'canceled',
  }
}

// ── Edit actions ───────────────────────────────────
const openEditModal = (g) => {
  if (!authStore.isAdminOrSuperuser) return
  editingGroup.value = {
    id: g.id,
    name: g.name,
    started_at: g.started_at || '',
    working_days: g.working_days || 68,
    working_weekends: g.working_weekends || 'mon-wed-fri',
    selected_weekdays: Array.isArray(g.selected_weekdays) && g.selected_weekdays.length > 0 ? [...g.selected_weekdays] : [0, 2, 4],
    ends_at: g.ends_at || null,
    duration: g.duration,
    status: g.status,
  }
  editModalError.value = ''
  if (editGroupModal.value) {
    editGroupModal.value.showModal()
  }
}

const closeEditModal = () => {
  if (editGroupModal.value) {
    editGroupModal.value.close()
  }
}

const updateGroup = async () => {
  if (!editingGroup.value.name.trim() || !editingGroup.value.started_at) {
    editModalError.value = "Barcha maydonlarni to'ldiring."
    return
  }

  editSaving.value = true
  editModalError.value = ''
  try {
    const payload = {
      name: editingGroup.value.name.trim(),
      started_at: editingGroup.value.started_at,
      working_days: Number(editingGroup.value.working_days) || 68,
      working_weekends: editingGroup.value.working_weekends,
      selected_weekdays: editingGroup.value.selected_weekdays,
      status: editingGroup.value.status,
    }
    await api.patch(`/groups/${editingGroup.value.id}/`, payload)
    closeEditModal()
    await fetchGroups()
  } catch (err) {
    console.error(err)
    editModalError.value = "Saqlashda xatolik yuz berdi. Qayta urinib ko'ring."
  } finally {
    editSaving.value = false
  }
}

// ── Start Group actions ─────────────────────────────
const isAllWaitingSelected = computed(() => {
  return waitingStudents.value.length > 0 && selectedWaitingIds.value.length === waitingStudents.value.length
})

const canSubmitStartGroup = computed(() => {
  return !!startGroupCategoryId.value &&
    (selectedWaitingIds.value.length === 23 || selectedWaitingIds.value.length === 24) &&
    !!startGroupForm.value.name.trim() &&
    !!startGroupForm.value.started_at
})

function toggleSelectAllWaiting(e) {
  if (e.target.checked) {
    selectedWaitingIds.value = waitingStudents.value.map(s => s.id)
  } else {
    selectedWaitingIds.value = []
  }
}

async function onStartGroupCategoryChange() {
  selectedWaitingIds.value = []
  waitingStudents.value = []
  if (!startGroupCategoryId.value) return

  const cat = categories.value.find(c => String(c.id) === String(startGroupCategoryId.value))
  startGroupForm.value.name = cat ? `${cat.name} guruhi` : ''
  startGroupForm.value.working_days = cat && cat.duration ? cat.duration : 68

  loadingWaitingStudents.value = true
  try {
    const res = await api.get('/students/', { params: { category: startGroupCategoryId.value, status: 'new', page_size: 1000 } })
    waitingStudents.value = res.data.results ? res.data.results : (res.data || [])
  } catch (err) {
    console.error("Navbatdagi o'quvchilarni yuklashda xatolik:", err)
  } finally {
    loadingWaitingStudents.value = false
  }
}

function openStartGroupModal() {
  if (!authStore.isAdminOrSuperuser) return
  startGroupCategoryId.value = ''
  waitingStudents.value = []
  selectedWaitingIds.value = []
  startGroupError.value = ''
  startGroupForm.value = {
    name: '',
    started_at: new Date().toISOString().substring(0, 10),
    working_days: 68,
    selected_weekdays: [0, 2, 4],
  }
  if (startGroupModal.value) {
    startGroupModal.value.showModal()
  }
}

function closeStartGroupModal() {
  if (startGroupModal.value) {
    startGroupModal.value.close()
  }
}

async function submitStartGroup() {
  if (!canSubmitStartGroup.value) {
    startGroupError.value = "Guruhni boshlash uchun kategoriya, guruh nomi, boshlanish sanasini kiriting va aynan 23 yoki 24 ta o'quvchi tanlang."
    return
  }

  startGroupSaving.value = true
  startGroupError.value = ''
  try {
    const payload = {
      name: startGroupForm.value.name.trim(),
      started_at: startGroupForm.value.started_at,
      working_days: Number(startGroupForm.value.working_days) || 68,
      selected_weekdays: startGroupForm.value.selected_weekdays,
      category: parseInt(startGroupCategoryId.value, 10),
      status: 'started',
      student_ids: selectedWaitingIds.value,
    }
    await api.post('/groups/', payload)
    closeStartGroupModal()
    await fetchGroups()
  } catch (err) {
    console.error(err)
    if (err.response?.data) {
      const data = err.response.data
      if (typeof data === 'object') {
        const msgs = Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
        startGroupError.value = msgs.join(' | ')
      } else {
        startGroupError.value = String(data)
      }
    } else {
      startGroupError.value = "Guruhni boshlashda xatolik yuz berdi."
    }
  } finally {
    startGroupSaving.value = false
  }
}

// Light dismiss listener fallback
onMounted(() => {
  fetchGroups()
  fetchCategories()

  if (route.query.action === 'create') {
    openStartGroupModal()
  }

  if (editGroupModal.value && !('closedBy' in HTMLDialogElement.prototype)) {
    editGroupModal.value.addEventListener('click', (event) => {
      if (event.target !== editGroupModal.value) return
      const rect = editGroupModal.value.getBoundingClientRect()
      const isInside = (
        rect.top <= event.clientY &&
        event.clientY <= rect.top + rect.height &&
        rect.left <= event.clientX &&
        event.clientX <= rect.left + rect.width
      )
      if (!isInside) {
        closeEditModal()
      }
    })
  }

  if (startGroupModal.value && !('closedBy' in HTMLDialogElement.prototype)) {
    startGroupModal.value.addEventListener('click', (event) => {
      if (event.target !== startGroupModal.value) return
      const rect = startGroupModal.value.getBoundingClientRect()
      const isInside = (
        rect.top <= event.clientY &&
        event.clientY <= rect.top + rect.height &&
        rect.left <= event.clientX &&
        event.clientX <= rect.left + rect.width
      )
      if (!isInside) {
        closeStartGroupModal()
      }
    })
  }
})
</script>

<style scoped>
.groups-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  background: white;
  padding: 14px 20px;
  border-radius: 14px;
  border: 1px solid #E5E7EB;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #F9FAFB;
  border: 1.5px solid #E5E7EB;
  border-radius: 10px;
  padding: 8px 14px;
  flex: 1;
  min-width: 260px;
  transition: all 0.2s;
}

.search-box:focus-within {
  border-color: #2D6A4F;
  background: white;
  box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.12);
}

.search-input {
  border: none;
  background: transparent;
  outline: none;
  font-size: 13.5px;
  width: 100%;
  color: #111827;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 13px;
  font-weight: 600;
  color: #4B5563;
}

.select-wrap {
  position: relative;
}

.filter-select {
  padding: 8px 14px;
  border: 1.5px solid #E5E7EB;
  border-radius: 10px;
  background: #F9FAFB;
  font-size: 13.5px;
  font-weight: 500;
  color: #111827;
  cursor: pointer;
  outline: none;
  transition: all 0.2s;

  &:focus {
    border-color: #2D6A4F;
    background: white;
    box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.12);
  }
}

.date-range-group { gap: 6px; }
.filter-date-input {
  padding: 7px 10px;
  border: 1.5px solid #E5E7EB;
  border-radius: 10px;
  background: #F9FAFB;
  font-size: 13px;
  color: #111827;
  outline: none;
  transition: all 0.2s;
}
.filter-date-input:focus { border-color: #2D6A4F; background: white; box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.12); }
.date-range-sep { color: #9CA3AF; font-size: 12px; }
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

.total-count {
  font-size: 13.5px;
  color: #6B7280;
}

/* ── States ─────────────────────────────────────────── */
.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: white;
  border-radius: 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
}
.state-text {
  font-size: 15px;
  color: #6B7280;
  font-weight: 500;
  margin: 12px 0 0 0;
}
.state-error .state-text {
  color: #DC2626;
}
.btn-retry {
  margin-top: 16px;
  padding: 8px 16px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}
.btn-retry:hover {
  background: #245C43;
}

/* Spinner */
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(45, 106, 79, 0.2);
  border-top-color: #2D6A4F;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── Groups table ───────────────────────────────────── */
.table-wrap {
  background: white;
  border-radius: 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
  overflow-x: auto;
}

.groups-table {
  width: 100%;
  border-collapse: collapse;
  white-space: nowrap;
}

.groups-table th {
  text-align: left;
  padding: 12px 16px;
  font-size: 11.5px;
  font-weight: 700;
  color: #6B7280;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  border-bottom: 1px solid #F3F4F6;
}

.groups-table td {
  padding: 12px 16px;
  font-size: 13px;
  color: #374151;
  border-bottom: 1px solid #F9FAFB;
  vertical-align: middle;
}

.groups-table tbody tr:last-child td { border-bottom: none; }
.groups-table tbody tr:hover td { background: #FAFAFA; }
.clickable-row { cursor: pointer; }

.group-name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #111827;
}

.group-icon-wrap-sm {
  width: 32px;
  height: 32px;
  background: #d1fae5;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.group-cat-badge {
  font-size: 11px;
  font-weight: 600;
  color: #047857;
  background: #ecfdf5;
  padding: 2px 8px;
  border-radius: 6px;
}

.highlight {
  color: #2D6A4F;
  font-weight: 700;
}

.status-badge {
  font-size: 11.5px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
  white-space: nowrap;
}

.badge-started {
  background: #eff6ff;
  color: #1d4ed8;
}

.badge-finished {
  background: #f3f4f6;
  color: #4b5563;
}

.badge-canceled {
  background: #fef2f2;
  color: #b91c1c;
}

.group-row-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-view {
  padding: 6px 14px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-view:hover {
  background: #245C43;
}

.btn-edit-group {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: #F3F4F6;
  border: 1px solid #E5E7EB;
  color: #4B5563;
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.btn-edit-group:hover {
  background: #E5E7EB;
  color: #111827;
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

/* ── Modal Dialog ───────────────────────────────────── */
.modal-dialog {
  border: none;
  border-radius: 16px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  background: white;
  max-height: 90vh;
  overflow-y: auto;
}
.modal-dialog::backdrop {
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
}

.modal-form {
  padding: 28px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  border-bottom: 1px solid #E5E7EB;
  padding-bottom: 12px;
}

.modal-error {
  padding: 10px 12px;
  background: #FEE2E2;
  border-left: 4px solid #EF4444;
  color: #991B1B;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  text-align: left;
}

.form-label {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}

.form-input {
  padding: 10px 12px;
  border: 1.5px solid #D1D5DB;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s;
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
}
.form-input:focus {
  border-color: #2D6A4F;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

.btn-cancel {
  padding: 9px 16px;
  background: #F3F4F6;
  color: #374151;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-cancel:hover {
  background: #E5E7EB;
}

.btn-save {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 9px 20px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-save:hover {
  background: #245C43;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.weekday-picker { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 4px; }
.weekday-chip {
  padding: 8px 12px;
  border: 1.5px solid #D1D5DB;
  border-radius: 8px;
  font-size: 12.5px;
  font-weight: 600;
  color: #374151;
  background: white;
  cursor: pointer;
  user-select: none;
  transition: all 0.15s ease;
}
.weekday-chip:hover { border-color: #9CA3AF; }
.weekday-chip.active { background: #2D6A4F; border-color: #2D6A4F; color: white; }

/* ── Start Group button & modal ────────────────────── */
.btn-start-new-group {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 16px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  white-space: nowrap;
}
.btn-start-new-group:hover { background: #245C43; }

.start-group-dialog { max-width: 620px; }

.field-hint {
  margin: 4px 0 0;
  font-size: 12px;
  color: #9CA3AF;
}

.waiting-students-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px;
  background: #F9FAFB;
  border: 1px solid #E5E7EB;
  border-radius: 10px;
}

.waiting-students-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.waiting-count-label {
  font-size: 12.5px;
  color: #4B5563;
}

.waiting-count-label strong { color: #111827; }
.waiting-count-label strong.count-ok { color: #2D6A4F; }

.select-all-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #4B5563;
  cursor: pointer;
}

.waiting-hint {
  margin: 0;
  font-size: 12px;
  font-weight: 600;
  padding: 6px 10px;
  border-radius: 6px;
}
.waiting-hint-warn { background: #FEF3C7; color: #B45309; }
.waiting-hint-ok { background: #DCFCE7; color: #15803D; }

.state-box-inline {
  text-align: center;
  padding: 16px 0;
  color: #9CA3AF;
  font-size: 12.5px;
}

.waiting-students-table-wrap {
  max-height: 240px;
  overflow-y: auto;
  overflow-x: auto;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  background: white;
}

.waiting-students-table {
  width: 100%;
  border-collapse: collapse;
}
.waiting-students-table th {
  position: sticky;
  top: 0;
  background: #F3F4F6;
  padding: 8px 10px;
  font-size: 11px;
  font-weight: 700;
  color: #6B7280;
  text-align: left;
  border-bottom: 1px solid #E5E7EB;
}
.waiting-students-table td {
  padding: 8px 10px;
  font-size: 12.5px;
  color: #374151;
  border-bottom: 1px solid #F3F4F6;
  vertical-align: middle;
}
.waiting-students-table .font-semibold { font-weight: 600; color: #111827; }
</style>
