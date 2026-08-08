<template>
  <AppLayout>
    <div class="agents-page">
      <!-- Top header bar -->
      <div class="page-header">
        <div>
          <h2 class="page-title">Agentlar boshqaruvi</h2>
          <p class="page-subtitle">Talabalarni jalb etuvchi agentlar ro'yxati va ma'lumotlari</p>
        </div>
        <button v-if="authStore.isAdminOrSuperuser" class="btn-primary" @click="openCreateModal">
          <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
            <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z"/>
          </svg>
          Yangi agent qo'shish
        </button>
      </div>

      <!-- Total count -->
      <div class="table-toolbar">
        <div class="total-count">
          Jami: <strong>{{ totalCount }}</strong> ta agent
        </div>
      </div>

      <!-- Data Table -->
      <div class="table-card">
        <div v-if="initialLoading" class="state-container">
          <div class="spinner"></div>
          <p class="state-text">Agentlar yuklanmoqda...</p>
        </div>

        <div v-else class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>Agent F.I.SH.</th>
                <th>Telefon</th>
                <th>Izoh</th>
                <th v-if="authStore.isAdminOrSuperuser" style="text-align: center; width: 100px;">Amallar</th>
              </tr>
              <tr class="col-filter-row">
                <th>
                  <input v-model="filterName" class="col-filter-input" type="text" placeholder="Ism bo'yicha qidirish..." />
                </th>
                <th>
                  <input v-model="filterPhone" class="col-filter-input" type="text" placeholder="Telefon bo'yicha qidirish..." />
                </th>
                <th></th>
                <th v-if="authStore.isAdminOrSuperuser"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="agents.length === 0">
                <td :colspan="authStore.isAdminOrSuperuser ? 4 : 3" class="td-empty">Agentlar topilmadi.</td>
              </tr>
              <tr v-for="agent in agents" :key="agent.id" class="table-row clickable-row" @click="goToAgentDetail(agent.id)">
                <td class="td-name">
                  <div class="agent-user-cell">
                    <div class="agent-avatar">
                      {{ agent.full_name?.[0]?.toUpperCase() || 'A' }}
                    </div>
                    <div class="agent-name">
                      {{ agent.full_name }}
                      <span v-if="agent.user" class="teacher-badge">{{ agent.user_role === 'instructor' ? 'Instruktor' : "O'qituvchi" }}</span>
                    </div>
                  </div>
                </td>
                <td class="td-phone">
                  <div>{{ formatPhone(agent.phone) }}</div>
                  <div v-if="agent.phone2" class="td-phone-sub">Qo'shimcha: {{ formatPhone(agent.phone2) }}</div>
                </td>
                <td>{{ agent.notes || '-' }}</td>
                <td v-if="authStore.isAdminOrSuperuser" style="text-align: center;" @click.stop>
                  <div class="action-btn-group">
                    <button class="btn-action btn-edit" @click.stop="openEditModal(agent)" title="Tahrirlash">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                        <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                      </svg>
                    </button>
                    <button class="btn-action btn-delete" @click.stop="openDeleteModal(agent)" title="O'chirish">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="pagination-bar">
          <span class="pagination-info">
            Jami: <strong>{{ totalCount }}</strong> tadan <strong>{{ agents.length }}</strong> ko'rsatilmoqda
          </span>
          <div class="pagination-actions">
            <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">Oldingi</button>
            <span v-if="pageSizeOption !== 'all'" class="page-num">Sahifa {{ Math.min(currentPage, displayTotalPages) }} / {{ displayTotalPages }}</span>
            <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === displayTotalPages" @click="changePage(currentPage + 1)">Keyingi</button>
            <label class="page-size-label" for="agents-page-size">Ko'rsatish:</label>
            <div class="select-wrap">
              <select id="agents-page-size" v-model="pageSizeOption" class="page-size-select">
                <option value="50">50</option>
                <option value="100">100</option>
                <option value="200">200</option>
                <option value="all">Barchasi</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Add/Edit Modal -->
      <dialog ref="agentModal" class="modal-dialog">
        <form @submit.prevent="saveAgent" class="modal-form">
          <h3 class="modal-title">{{ isEditing ? "Agent ma'lumotlarini tahrirlash" : "Yangi agent qo'shish" }}</h3>

          <div v-if="modalError" class="modal-error">
            {{ modalError }}
          </div>

          <div class="form-group checkbox-row">
            <input
              id="ag-is-teacher"
              v-model="form.is_teacher"
              type="checkbox"
              class="form-checkbox"
              @change="onToggleIsTeacher"
            />
            <label for="ag-is-teacher" class="form-checkbox-label">O'qituvchimi/Instruktormi?</label>
          </div>

          <template v-if="!form.is_teacher">
            <div class="form-group">
              <label for="ag-name" class="form-label">F.I.SH. (To'liq ism) *</label>
              <input
                id="ag-name"
                v-model="form.full_name"
                type="text"
                placeholder="Masalan: Qodirov Samandar"
                required
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label for="ag-phone" class="form-label">Telefon raqami *</label>
              <input
                id="ag-phone"
                v-model="form.phone"
                type="tel"
                placeholder="+998 90 900 90 90"
                required
                class="form-input"
                @input="handlePhoneInput($event, 'phone')"
              />
            </div>

            <div class="form-group">
              <label for="ag-phone2" class="form-label">Qo'shimcha telefon raqami</label>
              <input
                id="ag-phone2"
                v-model="form.phone2"
                type="tel"
                placeholder="+998 90 900 90 90 (ixtiyoriy)"
                class="form-input"
                @input="handlePhoneInput($event, 'phone2')"
              />
            </div>
          </template>

          <template v-else>
            <div class="form-group">
              <label class="form-label">O'qituvchi / Instruktor *</label>
              <div class="teacher-searchable-select" @click.stop>
                <input
                  type="text"
                  class="form-input"
                  :class="{ 'has-clear': form.user }"
                  v-model="teacherSearchText"
                  @focus="teacherDropdownOpen = true"
                  @input="teacherDropdownOpen = true"
                  placeholder="Ism yoki telefon bo'yicha qidirish..."
                  autocomplete="off"
                />
                <button
                  v-if="form.user"
                  type="button"
                  class="btn-clear-teacher"
                  title="Tozalash"
                  @mousedown.prevent="clearTeacher"
                >✕</button>
                <div v-if="teacherDropdownOpen" class="searchable-dropdown">
                  <div
                    v-for="t in filteredTeacherOptions"
                    :key="t.id"
                    class="searchable-option"
                    :class="{ selected: form.user === t.id }"
                    @mousedown.prevent="selectTeacher(t)"
                  >
                    {{ t.full_name || t.phone }}
                    <span class="opt-role-tag">{{ t.role === 'instructor' ? 'Instruktor' : "O'qituvchi" }}</span>
                  </div>
                  <div v-if="filteredTeacherOptions.length === 0" class="searchable-empty">Topilmadi</div>
                </div>
              </div>
            </div>
          </template>

          <div class="form-group">
            <label for="ag-notes" class="form-label">Eslatmalar</label>
            <textarea
              id="ag-notes"
              v-model="form.notes"
              placeholder="Qo'shimcha eslatmalar..."
              class="form-input"
              rows="3"
              style="resize: vertical; font-family: inherit;"
            ></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="closeModal">Bekor qilish</button>
            <button type="submit" class="btn-save" :disabled="saving">
              <span v-if="saving" class="btn-spinner"></span>
              <span>{{ isEditing ? 'Saqlash' : "Qo'shish" }}</span>
            </button>
          </div>
        </form>
      </dialog>

      <ConfirmDeleteModal
        ref="deleteModal"
        title="Agentni O'chirish"
        :deleting="deleting"
        :error="deleteError"
        @confirm="performDelete"
      >
        Haqiqatan ham <strong>{{ deletingAgent?.full_name }}</strong> agentini o'chirmoqchimisiz?
      </ConfirmDeleteModal>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import ConfirmDeleteModal from '@/components/ConfirmDeleteModal.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useBranchStore } from '@/stores/branch'
import { formatPhone } from '@/utils/formatters'
import { debounce } from '@/utils/debounce'

const authStore = useAuthStore()
const branchStore = useBranchStore()
const route = useRoute()
const router = useRouter()

function goToAgentDetail(id) {
  if (id) router.push(`/agents/${id}`)
}

const agents = ref([])
const loading = ref(false)
// Only gates the initial full-page spinner. Re-using `loading` for that
// meant every filter/page refetch unmounted the whole table — including
// the column-filter <input> the user was typing into — via v-if, stealing
// focus and resetting cursor position on every keystroke.
const initialLoading = ref(true)
const saving = ref(false)
const filterName = ref('')
const filterPhone = ref('')
const totalCount = ref(0)

// ── Row-fetch-count selector ──────────────────────────────────
// Controls the page_size sent to the backend. Filtering/sorting (always
// alphabetical by name) and pagination are all done server-side (see
// fetchAgents) — the table only ever holds the current page's rows.
const pageSizeOption = ref('50')
const currentPage = ref(1)

const displayTotalPages = computed(() => {
  if (pageSizeOption.value === 'all') return 1
  return Math.max(1, Math.ceil(totalCount.value / Number(pageSizeOption.value)))
})
function changePage(page) {
  if (page < 1 || page > displayTotalPages.value) return
  currentPage.value = page
  fetchAgents()
}

const agentModal = ref(null)
const isEditing = ref(false)
const editingId = ref(null)
const modalError = ref('')

const form = ref({
  full_name: '',
  phone: '',
  phone2: '',
  notes: '',
  is_teacher: false,
  user: null,
})

// ── Teacher/instructor agent picker ────────────────────
// An instructor/coordinator can also be an "agent" (bringing in students
// themselves) — Agent.user links the agent record to that staff account.
// Since it's a one-to-one link, a teacher already linked to another agent
// is excluded from the picker (except the agent currently being edited,
// whose own link doesn't count as "taken").
const teacherOptions = ref([])
async function fetchTeacherOptions() {
  try {
    const [instRes, coordRes] = await Promise.all([
      api.get('/users/', { params: { role: 'instructor', page_size: 1000 } }),
      api.get('/users/', { params: { role: 'coordinator', page_size: 1000 } }),
    ])
    const instructors = instRes.data.results || instRes.data || []
    const coordinators = coordRes.data.results || coordRes.data || []
    teacherOptions.value = [...instructors, ...coordinators]
  } catch (err) {
    console.error("O'qituvchi/instruktorlarni yuklashda xatolik:", err)
  }
}

const allAgentLinks = ref([])
async function fetchAllAgentLinks() {
  try {
    const res = await api.get('/agents/', { params: { page_size: 1000 } })
    const list = res.data.results || res.data || []
    allAgentLinks.value = list.filter(a => a.user).map(a => ({ id: a.id, user: a.user }))
  } catch (err) {
    console.error("Agent bog'lanishlarini yuklashda xatolik:", err)
  }
}
const assignedTeacherUserIds = computed(() => {
  const ids = new Set()
  allAgentLinks.value.forEach(link => {
    if (link.id !== editingId.value) ids.add(link.user)
  })
  return ids
})

const teacherSearchText = ref('')
const teacherDropdownOpen = ref(false)
const filteredTeacherOptions = computed(() => {
  const q = teacherSearchText.value.trim().toLowerCase()
  const available = teacherOptions.value.filter(t => !assignedTeacherUserIds.value.has(t.id))
  if (!q) return available
  return available.filter(t =>
    (t.full_name || '').toLowerCase().includes(q) || (t.phone || '').includes(q)
  )
})
function selectTeacher(t) {
  form.value.user = t ? t.id : null
  teacherSearchText.value = t ? (t.full_name || t.phone) : ''
  teacherDropdownOpen.value = false
}
function clearTeacher() {
  selectTeacher(null)
}
function onToggleIsTeacher() {
  if (form.value.is_teacher) {
    if (teacherOptions.value.length === 0) fetchTeacherOptions()
    fetchAllAgentLinks()
  } else {
    form.value.user = null
    teacherSearchText.value = ''
  }
}
function handleTeacherOutsideClick(e) {
  if (e.target.closest('.teacher-searchable-select')) return
  teacherDropdownOpen.value = false
}

// Guards against an older, slower request resolving *after* a newer
// filtered one and clobbering it with stale results.
let fetchToken = 0
const fetchAgents = async () => {
  const token = ++fetchToken
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSizeOption.value === 'all' ? 100000 : Number(pageSizeOption.value),
      // AgentsView always sorts alphabetically by name — no sort toggle.
      ordering: 'full_name',
    }
    if (filterName.value.trim()) params.name = filterName.value.trim()
    if (filterPhone.value.trim()) params.phone = filterPhone.value.trim()
    if (branchStore.activeBranchId) params.branch = branchStore.activeBranchId

    const res = await api.get('/agents/', { params })
    if (token !== fetchToken) return
    if (Array.isArray(res.data)) {
      agents.value = res.data
      totalCount.value = res.data.length
    } else {
      agents.value = res.data.results || []
      totalCount.value = res.data.count || 0
    }
  } catch (err) {
    console.error('Failed to fetch agents:', err)
  } finally {
    if (token === fetchToken) { loading.value = false; initialLoading.value = false }
  }
}

watch(pageSizeOption, () => {
  currentPage.value = 1
  fetchAgents()
})
const debouncedRefetch = debounce(() => {
  currentPage.value = 1
  fetchAgents()
}, 400)
watch([filterName, filterPhone], debouncedRefetch)
watch(() => branchStore.activeBranchId, () => {
  currentPage.value = 1
  fetchAgents()
})

const openCreateModal = () => {
  isEditing.value = false
  editingId.value = null
  form.value = {
    full_name: '',
    phone: '',
    phone2: '',
    notes: '',
    is_teacher: false,
    user: null,
  }
  teacherSearchText.value = ''
  teacherDropdownOpen.value = false
  modalError.value = ''
  if (agentModal.value) agentModal.value.showModal()
  router.replace({ query: { ...route.query, action: 'add' } })
}

const openEditModal = (agent) => {
  isEditing.value = true
  editingId.value = agent.id
  form.value = {
    full_name: agent.full_name || '',
    phone: agent.phone ? formatPhoneDisplay(agent.phone) : '',
    phone2: agent.phone2 ? formatPhoneDisplay(agent.phone2) : '',
    notes: agent.notes || '',
    is_teacher: !!agent.user,
    user: agent.user || null,
  }
  teacherSearchText.value = agent.user ? (agent.user_name || '') : ''
  teacherDropdownOpen.value = false
  if (agent.user) {
    if (teacherOptions.value.length === 0) fetchTeacherOptions()
    fetchAllAgentLinks()
  }
  modalError.value = ''
  if (agentModal.value) agentModal.value.showModal()
}

const closeModal = () => {
  if (agentModal.value) agentModal.value.close()
  if (route.query.action) {
    const q = { ...route.query }
    delete q.action
    router.replace({ query: q })
  }
}

const saveAgent = async () => {
  let payload

  if (form.value.is_teacher) {
    if (!form.value.user) {
      modalError.value = "O'qituvchi yoki instruktorni tanlang."
      return
    }
    payload = { user: form.value.user, notes: form.value.notes?.trim() || '' }
  } else {
    const name = form.value.full_name.trim()
    const phoneCleaned = form.value.phone.replace(/\D/g, '')

    if (!name || !phoneCleaned) {
      modalError.value = "F.I.SH. va telefon raqamini kiriting."
      return
    }

    if (phoneCleaned.length < 12) {
      modalError.value = "Telefon raqami noto'g'ri kiritilgan (+998 ...)."
      return
    }

    const phone2Cleaned = form.value.phone2 ? form.value.phone2.replace(/\D/g, '') : null
    payload = { user: null, full_name: name, phone: phoneCleaned, phone2: phone2Cleaned, notes: form.value.notes?.trim() || '' }
  }

  saving.value = true
  modalError.value = ''

  try {
    if (isEditing.value) {
      await api.patch(`/agents/${editingId.value}/`, payload)
    } else {
      await api.post('/agents/', { ...payload, branch: branchStore.activeBranchId ?? null })
    }
    closeModal()
    fetchAgents()
    fetchAllAgentLinks()
  } catch (err) {
    console.error(err)
    const data = err.response?.data
    if (data?.phone) {
      modalError.value = "Ushbu telefon raqamli agent allaqachon mavjud."
    } else if (data?.user) {
      modalError.value = Array.isArray(data.user) ? data.user[0] : String(data.user)
    } else if (data?.full_name) {
      modalError.value = Array.isArray(data.full_name) ? data.full_name[0] : String(data.full_name)
    } else {
      modalError.value = "Saqlashda xatolik yuz berdi."
    }
  } finally {
    saving.value = false
  }
}

const deleteModal = ref(null)
const deletingAgent = ref(null)
const deleting = ref(false)
const deleteError = ref('')

const openDeleteModal = (agent) => {
  deletingAgent.value = agent
  deleteError.value = ''
  deleteModal.value?.show()
}

const performDelete = async () => {
  if (!deletingAgent.value) return
  deleting.value = true
  deleteError.value = ''
  try {
    await api.delete(`/agents/${deletingAgent.value.id}/`)
    deleteModal.value?.close()
    fetchAgents()
  } catch (err) {
    console.error('Failed to delete agent:', err)
    deleteError.value = "Agentni o'chirishda xatolik yuz berdi."
  } finally {
    deleting.value = false
  }
}

const formatPhoneDisplay = (p) => {
  if (!p) return ''
  let digits = p.replace(/\D/g, '')
  if (!digits) return p
  if (!digits.startsWith('998') && digits.length <= 9) {
    digits = '998' + digits
  }
  digits = digits.substring(0, 12)
  let formatted = '+' + digits.substring(0, 3)
  if (digits.length > 3) formatted += ' ' + digits.substring(3, 5)
  if (digits.length > 5) formatted += ' ' + digits.substring(5, 8)
  if (digits.length > 8) formatted += ' ' + digits.substring(8, 10)
  if (digits.length > 10) formatted += ' ' + digits.substring(10, 12)
  return formatted
}

const handlePhoneInput = (event, key) => {
  const val = event.target.value
  if (!val) {
    form.value[key] = ''
    return
  }
  form.value[key] = formatPhoneDisplay(val)
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchCurrentUser()
  }
  await fetchAgents()

  if (route.query.action === 'add' && authStore.isAdminOrSuperuser) {
    openCreateModal()
  }

  // Light dismiss fallback
  if (agentModal.value && !('closedBy' in HTMLDialogElement.prototype)) {
    agentModal.value.addEventListener('click', (event) => {
      if (event.target !== agentModal.value) return
      const rect = agentModal.value.getBoundingClientRect()
      const isInside = (
        rect.top <= event.clientY &&
        event.clientY <= rect.top + rect.height &&
        rect.left <= event.clientX &&
        event.clientX <= rect.left + rect.width
      )
      if (!isInside) {
        closeModal()
      }
    })
  }

  document.addEventListener('click', handleTeacherOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleTeacherOutsideClick)
})
</script>

<style scoped>
.agents-page {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 13.5px;
  color: #6B7280;
  margin: 0;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13.5px;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(45, 106, 79, 0.2);
  transition: background 0.15s;
}
.btn-primary:hover {
  background: #1B4332;
}

.table-toolbar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-bottom: 16px;
  gap: 16px;
}

.total-count {
  font-size: 13.5px;
  color: #4B5563;
}

.table-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #E5E7EB;
  overflow: hidden;
}
/* Bounded, independently-scrolling table body so the header (both the
   label row and the column-filter row) sticks to the top of this
   container as rows scroll underneath, instead of scrolling away with
   the page. */
.table-wrap { overflow: auto; max-height: 600px; }
.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 13.5px;
}
.data-table thead { position: sticky; top: 0; z-index: 3; }
.data-table th {
  background: #F9FAFB;
  color: #4B5563;
  font-weight: 600;
  padding: 12px 16px;
  border-bottom: 1px solid #E5E7EB;
}
.data-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #F3F4F6;
  color: #1F2937;
  vertical-align: middle;
}
.table-row:hover { background: #F9FAFB; }
.clickable-row { cursor: pointer; }
.td-empty { text-align: center; padding: 32px; color: #6B7280; }

/* ── Column-head filters ─────────────────────────────────── */
.data-table thead tr.col-filter-row th {
  padding: 8px 10px;
  background: #FAFAFB;
  border-bottom: 1px solid #E5E7EB;
}
.col-filter-input {
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
.col-filter-input:focus { border-color: #2D6A4F; }
.col-filter-input::placeholder { color: #9CA3AF; }

.agent-user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.agent-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #E0E7FF;
  color: #4338CA;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 13px;
  flex-shrink: 0;
}

.agent-name {
  font-weight: 600;
  color: #111827;
}

.td-phone {
  font-weight: 500;
  color: #374151;
}

.td-phone-sub {
  font-size: 11.5px;
  font-weight: 400;
  color: #6B7280;
  margin-top: 2px;
}

.action-btn-group {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.btn-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
}
.btn-edit { background: #F3F4F6; color: #374151; }
.btn-edit:hover { background: #E5E7EB; }
.btn-delete { background: #FEE2E2; color: #DC2626; }
.btn-delete:hover { background: #FCA5A5; }

.state-container { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 48px; gap: 12px; }
.spinner { width: 32px; height: 32px; border: 3px solid #E5E7EB; border-top-color: #2D6A4F; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.state-text { color: #6B7280; font-size: 14px; }

/* ── Pagination / row-fetch-count bar ────────────────────────── */
.pagination-bar { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #F9FAFB; border-top: 1px solid #E5E7EB; }
.pagination-info { font-size: 13.5px; color: #6B7280; font-weight: 500; }
.pagination-note { margin-left: 8px; font-size: 12px; color: #9CA3AF; font-weight: 400; }
.pagination-actions { display: flex; align-items: center; gap: 8px; }
.select-wrap { position: relative; }
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

/* Modal Dialog */
.modal-dialog {
  border: none;
  border-radius: 16px;
  padding: 0;
  max-width: 480px;
  width: 90%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  background: white;
}
.modal-dialog::backdrop {
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
}

.modal-form {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
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
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
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
  transition: border-color 0.15s, box-shadow 0.15s;
}
.form-input:focus {
  border-color: #2D6A4F;
  box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.12);
}

.checkbox-row { flex-direction: row; align-items: center; gap: 8px; }
.form-checkbox { width: 16px; height: 16px; cursor: pointer; accent-color: #2D6A4F; }
.form-checkbox-label { font-size: 13.5px; font-weight: 600; color: #374151; cursor: pointer; }

.teacher-searchable-select { position: relative; }
.teacher-searchable-select .form-input { width: 100%; box-sizing: border-box; }
.teacher-searchable-select .form-input.has-clear { padding-right: 34px; }
.btn-clear-teacher {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 50%;
  background: #F3F4F6;
  color: #6B7280;
  font-size: 11px;
  cursor: pointer;
  z-index: 1;
}
.btn-clear-teacher:hover { background: #E5E7EB; color: #374151; }
.searchable-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: white;
  border: 1.5px solid #D1D5DB;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  max-height: 220px;
  overflow-y: auto;
  z-index: 20;
}
.searchable-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 9px 14px;
  font-size: 13.5px;
  color: #374151;
  cursor: pointer;
}
.searchable-option:hover { background: #F3F4F6; }
.searchable-option.selected { background: #F0F7F4; color: #1B4332; font-weight: 600; }
.searchable-empty { padding: 10px 14px; font-size: 12.5px; color: #9CA3AF; text-align: center; }
.opt-role-tag { font-size: 10.5px; font-weight: 700; color: #4338CA; background: #E0E7FF; padding: 2px 7px; border-radius: 6px; flex-shrink: 0; }

.teacher-badge {
  display: inline-block;
  margin-left: 6px;
  padding: 2px 7px;
  font-size: 10.5px;
  font-weight: 700;
  color: #4338CA;
  background: #E0E7FF;
  border-radius: 6px;
  vertical-align: middle;
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
}
.btn-cancel:hover { background: #E5E7EB; }

.btn-save {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 20px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
}
.btn-save:hover { background: #1B4332; }
</style>
