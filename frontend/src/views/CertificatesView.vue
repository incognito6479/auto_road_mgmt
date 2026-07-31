<template>
  <AppLayout>

    <div class="page-top">
      <div>
        <h2 class="page-main-title">Sertifikatlar (Kursni Tugatganlik)</h2>
        <p class="page-sub-title">Kursni tugatganlik sertifikati berilgan o'quvchilar ro'yxati</p>
      </div>

      <button v-if="authStore.isAdminOrSuperuser" class="btn-primary-action" @click="openAddModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="18" height="18">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        <span>Sertifikat qo'shish</span>
      </button>
    </div>

    <div class="table-section-card margin-top">
      <div class="toolbar-bar">
        <div class="search-box">
          <svg viewBox="0 0 20 20" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
            <circle cx="8.5" cy="8.5" r="5.5"/>
            <line x1="13" y1="13" x2="18" y2="18"/>
          </svg>
          <input
            v-model="filterSearchQuery"
            type="text"
            placeholder="O'quvchi F.I.SH., JSHSHR yoki sertifikat raqami..."
            class="search-input"
          />
        </div>

        <div class="total-count">
          Jami: <strong>{{ filteredEnrollments.length }}</strong> ta sertifikat
        </div>
      </div>

      <div class="table-container">
        <div v-if="loading" class="state-box">
          <div class="spinner"></div>
          <span>Sertifikatlar yuklanmoqda...</span>
        </div>

        <div v-else-if="filteredEnrollments.length === 0" class="empty-state">
          <p>Sertifikatlar topilmadi</p>
        </div>

        <table v-else class="data-table">
          <thead>
            <tr>
              <th>O'quvchi F.I.SH.</th>
              <th>Sertifikat</th>
              <th>Telefon</th>
              <th>JSHSHR</th>
              <th>Guruh</th>
              <th>Kategoriya</th>
              <th>O'qituvchi</th>
              <th>Instruktor</th>
              <th>Shartnoma</th>
              <th>To'langan</th>
              <th v-if="authStore.isSuperuser" style="text-align: right;">Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="e in filteredEnrollments" :key="e.id" class="table-row clickable-row" @click="goStudent(e.student)">
              <td class="td-name">{{ e.student_name || 'Noma\'lum' }}</td>
              <td class="td-cert">
                <div class="cert-main">{{ e.student_certificate_series || '' }} {{ e.student_certificate_number }}</div>
                <div v-if="e.student_certificate_added_date" class="cert-sub">{{ formatDate(e.student_certificate_added_date) }}</div>
              </td>
              <td class="td-phone">
                <div>{{ formatPhone(e.student_phone) }}</div>
                <div v-if="e.student_phone2" class="td-phone-sub">Qo'shimcha: {{ formatPhone(e.student_phone2) }}</div>
              </td>
              <td class="td-jshshr">{{ e.student_jshshr || '-' }}</td>
              <td>
                <span v-if="e.group_name">{{ e.group_name }}</span>
                <span v-else>-</span>
                <div v-if="groupsById[e.group]" class="group-dates">
                  {{ formatDate(groupsById[e.group].started_at) }} — {{ formatDate(groupsById[e.group].ends_at) }}
                </div>
              </td>
              <td><span class="cat-pill">{{ e.category_name || '-' }}</span></td>
              <td>
                <span v-if="e.coordinator_name" class="link-value" @click.stop="goUser(e.coordinator)">{{ e.coordinator_name }}</span>
                <span v-else>-</span>
              </td>
              <td>
                <span v-if="e.instructor_name" class="link-value" @click.stop="goUser(e.instructor)">{{ e.instructor_name }}</span>
                <span v-else>-</span>
              </td>
              <td class="td-amount">
                <span v-if="e.enrolled_free" class="free-chip">Tekin</span>
                <span v-else>{{ formatMoney(e.enrolled_amount) }}</span>
              </td>
              <td class="td-amount text-green">{{ formatMoney(e.paid_amount || 0) }}</td>
              <td v-if="authStore.isSuperuser" style="text-align: right;" @click.stop>
                <div class="row-actions">
                  <button class="btn-action-edit" @click="openEditModal(e)" title="Tahrirlash">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                  <button class="btn-action-delete" @click="openDeleteModal(e)" title="O'chirish">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
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
    </div>

    <!-- EDIT MODAL -->
    <Transition name="modal">
      <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
        <div class="modal-card">
          <div class="modal-header-banner amber-banner">
            <div class="header-left-info">
              <div class="header-icon-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <circle cx="12" cy="8" r="6"/><path d="M8.21 13.89L7 23l5-3 5 3-1.21-9.12"/>
                </svg>
              </div>
              <div>
                <h3>Sertifikatni Tahrirlash</h3>
                <p v-if="editTarget">{{ editTarget.student_name }}</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closeEditModal">✕</button>
          </div>

          <form @submit.prevent="saveCertificate" class="modal-body">
            <div v-if="editError" class="alert-error">{{ editError }}</div>

            <div class="form-group">
              <label class="flabel required">Seriya</label>
              <input v-model="editForm.certificate_series" type="text" maxlength="2" class="finput text-upper" placeholder="AB" />
            </div>

            <div class="form-group">
              <label class="flabel required">Raqami</label>
              <input v-model="editForm.certificate_number" type="text" maxlength="9" class="finput" placeholder="9 ta raqam" />
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-cancel" @click="closeEditModal">Bekor qilish</button>
              <button type="submit" class="btn-save" :disabled="editSaving">
                {{ editSaving ? "Saqlanmoqda..." : "Saqlash" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <ConfirmDeleteModal
      ref="deleteModal"
      title="Sertifikatni O'chirish"
      :deleting="deleting"
      :error="deleteError"
      @confirm="performDelete"
    >
      Haqiqatan ham <strong>{{ deletingTarget?.student_name }}</strong> uchun sertifikat ma'lumotlarini o'chirmoqchimisiz?
    </ConfirmDeleteModal>

    <!-- ADD MODAL: group -> student cascade + certificate fields -->
    <Transition name="modal">
      <div v-if="showAddModal" class="modal-overlay" @click.self="closeAddModal">
        <div class="modal-card">
          <div class="modal-header-banner amber-banner">
            <div class="header-left-info">
              <div class="header-icon-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <circle cx="12" cy="8" r="6"/><path d="M8.21 13.89L7 23l5-3 5 3-1.21-9.12"/>
                </svg>
              </div>
              <div>
                <h3>Sertifikat Qo'shish</h3>
                <p>O'quvchining kursni tugatganlik sertifikatini kiriting</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closeAddModal">✕</button>
          </div>

          <form @submit.prevent="submitAddCertificate" class="modal-body">
            <div v-if="addModalError" class="alert-error">{{ addModalError }}</div>

            <div class="form-group">
              <label class="flabel required">Guruhni Tanlang *</label>
              <div class="searchable-select-wrap" ref="addGroupSelectWrapRef">
                <input
                  v-model="addGroupQuery"
                  type="text"
                  class="finput search-input-field"
                  placeholder="Guruh nomi bo'yicha qidiring..."
                  @click="showAddGroupDropdown = !showAddGroupDropdown"
                  @input="showAddGroupDropdown = true"
                  @keydown="onAddGroupKeydown"
                />
                <button v-if="selectedAddGroupId" type="button" class="input-clear-btn" title="Guruhni bekor qilish" @click="clearAddGroupSelection">✕</button>
                <div v-if="showAddGroupDropdown" class="dropdown-options-list">
                  <div
                    v-for="(g, idx) in filteredAddGroups"
                    :key="g.id"
                    class="dropdown-option-item"
                    :class="{ selected: selectedAddGroupId === g.id, highlighted: addGroupKb.highlightedIndex.value === idx }"
                    @click="selectAddGroup(g)"
                  >
                    <div class="opt-name">{{ g.name }}</div>
                  </div>
                  <div v-if="filteredAddGroups.length === 0" class="dropdown-empty">
                    Mos guruh topilmadi
                  </div>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label class="flabel required">O'quvchini Ism bo'yicha Qidirish *</label>
              <div class="searchable-select-wrap" ref="addStudentSelectWrapRef">
                <input
                  v-model="addStudentQuery"
                  type="text"
                  class="finput search-input-field"
                  :placeholder="selectedAddGroupId ? 'Ism bo\'yicha qidiring...' : 'Avval guruhni tanlang'"
                  :disabled="!selectedAddGroupId"
                  @click="showAddStudentDropdown = !showAddStudentDropdown"
                  @input="showAddStudentDropdown = true"
                  @keydown="onAddStudentKeydown"
                />
                <button v-if="addForm.student" type="button" class="input-clear-btn" title="O'quvchini bekor qilish" @click="clearAddStudentSelection">✕</button>
                <div v-if="showAddStudentDropdown" class="dropdown-options-list">
                  <div
                    v-for="(e, idx) in filteredAddStudents"
                    :key="e.id"
                    class="dropdown-option-item"
                    :class="{ selected: addForm.student === e.student, highlighted: addStudentKb.highlightedIndex.value === idx }"
                    @click="selectAddStudent(e)"
                  >
                    <div class="opt-name">{{ e.student_name }}</div>
                  </div>
                  <div v-if="filteredAddStudents.length === 0" class="dropdown-empty">
                    Mos o'quvchi topilmadi
                  </div>
                </div>
              </div>
              <div v-if="selectedAddStudentLabel" class="selected-chip">
                Tanlandi: <strong>{{ selectedAddStudentLabel }}</strong>
              </div>
            </div>

            <div class="form-group">
              <label class="flabel required">Seriya *</label>
              <input v-model="addForm.certificate_series" type="text" maxlength="2" class="finput text-upper" placeholder="AB" />
            </div>

            <div class="form-group">
              <label class="flabel required">Raqami *</label>
              <input v-model="addForm.certificate_number" type="text" maxlength="9" class="finput" placeholder="9 ta raqam" />
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-cancel" @click="closeAddModal">Bekor qilish</button>
              <button type="submit" class="btn-save" :disabled="addSaving">
                {{ addSaving ? "Saqlanmoqda..." : "Saqlash" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import ConfirmDeleteModal from '@/components/ConfirmDeleteModal.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { formatMoney, formatPhone, formatDate } from '@/utils/formatters'
import { useSearchSelectKeyboard } from '@/composables/useSearchSelectKeyboard'
import { useGroupSelect } from '@/composables/useGroupSelect'

const router = useRouter()
const authStore = useAuthStore()

const enrollments = ref([])
const groups = ref([])
const loading = ref(true)
const filterSearchQuery = ref('')

const groupsById = computed(() => {
  const map = {}
  groups.value.forEach(g => { map[g.id] = g })
  return map
})

const filteredEnrollments = computed(() => {
  const q = filterSearchQuery.value.toLowerCase().trim()
  if (!q) return enrollments.value
  return enrollments.value.filter(e =>
    (e.student_name || '').toLowerCase().includes(q) ||
    String(e.student_jshshr || '').includes(q) ||
    (e.student_certificate_number || '').includes(q) ||
    (e.student_certificate_series || '').toLowerCase().includes(q)
  )
})

function goStudent(studentId) {
  if (studentId) router.push(`/students/${studentId}`)
}
function goUser(id) {
  if (id) router.push(`/users/${id}`)
}

async function fetchEnrollments() {
  loading.value = true
  try {
    const res = await api.get('/enrollments/', { params: { has_certificate: 'true', page_size: 1000 } })
    enrollments.value = res.data.results || res.data
  } catch (err) { console.error(err) }
  finally { loading.value = false }
}

async function fetchGroups() {
  try {
    const res = await api.get('/groups/', { params: { page_size: 1000 } })
    groups.value = res.data.results || res.data
  } catch (err) { console.error(err) }
}

// ── Add modal (group -> student cascade) ────────────────
const showAddModal = ref(false)
const addSaving = ref(false)
const addModalError = ref(null)
const allEnrollments = ref([])
const addStudentQuery = ref('')
const showAddStudentDropdown = ref(false)
const selectedAddStudentLabel = ref('')
const addStudentSelectWrapRef = ref(null)
const addForm = ref({ student: '', certificate_series: '', certificate_number: '' })

const {
  query: addGroupQuery,
  showDropdown: showAddGroupDropdown,
  selectedId: selectedAddGroupId,
  filtered: filteredAddGroups,
  select: selectAddGroupRaw,
  reset: resetAddGroupSelect,
  isOutside: isAddGroupOutside,
  selectRef: addGroupSelectWrapRef,
} = useGroupSelect(groups)

function selectAddGroup(g) {
  selectAddGroupRaw(g)
  addStudentQuery.value = ''
  selectedAddStudentLabel.value = ''
  addForm.value.student = ''
}

function clearAddGroupSelection() {
  resetAddGroupSelect()
  addStudentQuery.value = ''
  selectedAddStudentLabel.value = ''
  addForm.value.student = ''
}

function clearAddStudentSelection() {
  addStudentQuery.value = ''
  selectedAddStudentLabel.value = ''
  addForm.value.student = ''
}

const addGroupKb = useSearchSelectKeyboard()
function onAddGroupKeydown(e) {
  addGroupKb.onKeydown(e, filteredAddGroups.value, selectAddGroup, () => { showAddGroupDropdown.value = false })
}

// Both searchable selects close when the click lands outside their own wrapper.
function handleAddSelectOutsideClick(e) {
  if (isAddGroupOutside(e.target)) {
    showAddGroupDropdown.value = false
  }
  if (addStudentSelectWrapRef.value && !addStudentSelectWrapRef.value.contains(e.target)) {
    showAddStudentDropdown.value = false
  }
}

const filteredAddStudents = computed(() => {
  if (!selectedAddGroupId.value) return []
  const q = addStudentQuery.value.toLowerCase().trim()
  return allEnrollments.value.filter(e => {
    if (e.group !== selectedAddGroupId.value) return false
    return !q || (e.student_name || '').toLowerCase().includes(q)
  })
})

async function fetchAllEnrollments() {
  if (allEnrollments.value.length > 0) return
  try {
    const res = await api.get('/enrollments/', { params: { page_size: 1000 } })
    allEnrollments.value = res.data.results || res.data
  } catch (err) { console.error(err) }
}

function openAddModal() {
  addModalError.value = null
  addStudentQuery.value = ''
  selectedAddStudentLabel.value = ''
  showAddStudentDropdown.value = false
  resetAddGroupSelect()
  addForm.value = { student: '', certificate_series: '', certificate_number: '' }
  showAddModal.value = true
  fetchAllEnrollments()
}
function closeAddModal() { showAddModal.value = false }

function selectAddStudent(e) {
  addForm.value.student = e.student
  selectedAddStudentLabel.value = e.student_name
  addStudentQuery.value = e.student_name
  showAddStudentDropdown.value = false
}
const addStudentKb = useSearchSelectKeyboard()
function onAddStudentKeydown(e) {
  addStudentKb.onKeydown(e, filteredAddStudents.value, selectAddStudent, () => { showAddStudentDropdown.value = false })
}

async function submitAddCertificate() {
  if (!addForm.value.student) { addModalError.value = "O'quvchini tanlang."; return }
  const series = addForm.value.certificate_series.trim().toUpperCase()
  const number = addForm.value.certificate_number.trim()
  if (!/^[A-Z]{2}$/.test(series)) { addModalError.value = "Seriya 2 ta harfdan iborat bo'lishi kerak (masalan: AB)."; return }
  if (!/^\d{9}$/.test(number)) { addModalError.value = "Raqam 9 ta raqamdan iborat bo'lishi kerak."; return }
  addSaving.value = true
  addModalError.value = null
  try {
    await api.patch(`/students/${addForm.value.student}/`, {
      certificate_series: series,
      certificate_number: number,
      certificate_added_date: new Date().toISOString(),
    })
    closeAddModal()
    await fetchEnrollments()
  } catch (err) {
    addModalError.value = err.response?.data?.detail || "Saqlashda xatolik yuz berdi"
  } finally {
    addSaving.value = false
  }
}

// ── Edit modal ──────────────────────────────────────────
const showEditModal = ref(false)
const editTarget = ref(null)
const editForm = ref({ certificate_series: '', certificate_number: '' })
const editSaving = ref(false)
const editError = ref(null)

function openEditModal(e) {
  editTarget.value = e
  editForm.value = {
    certificate_series: e.student_certificate_series || '',
    certificate_number: e.student_certificate_number || '',
  }
  editError.value = null
  showEditModal.value = true
}
function closeEditModal() { showEditModal.value = false }

async function saveCertificate() {
  const series = editForm.value.certificate_series.trim().toUpperCase()
  const number = editForm.value.certificate_number.trim()
  if (series && !/^[A-Z]{2}$/.test(series)) { editError.value = "Seriya 2 ta harfdan iborat bo'lishi kerak."; return }
  if (number && !/^\d{9}$/.test(number)) { editError.value = "Raqam 9 ta raqamdan iborat bo'lishi kerak."; return }
  editSaving.value = true
  editError.value = null
  try {
    await api.patch(`/students/${editTarget.value.student}/`, {
      certificate_series: series || null,
      certificate_number: number || null,
      certificate_added_date: new Date().toISOString(),
    })
    closeEditModal()
    await fetchEnrollments()
  } catch (err) {
    editError.value = err.response?.data?.detail || "Saqlashda xatolik yuz berdi"
  } finally {
    editSaving.value = false
  }
}

// ── Delete (clear certificate) ─────────────────────────
const deleteModal = ref(null)
const deletingTarget = ref(null)
const deleting = ref(false)
const deleteError = ref('')

function openDeleteModal(e) {
  deletingTarget.value = e
  deleteError.value = ''
  deleteModal.value?.show()
}

async function performDelete() {
  if (!deletingTarget.value) return
  deleting.value = true
  deleteError.value = ''
  try {
    await api.patch(`/students/${deletingTarget.value.student}/`, {
      certificate_series: null,
      certificate_number: null,
      certificate_added_date: null,
    })
    deleteModal.value?.close()
    await fetchEnrollments()
  } catch (err) {
    deleteError.value = "O'chirishda xatolik yuz berdi"
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  fetchEnrollments()
  fetchGroups()
  document.addEventListener('click', handleAddSelectOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleAddSelectOutsideClick)
})
</script>

<style scoped>
.page-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-main-title { font-size: 22px; font-weight: 700; color: #111827; }
.page-sub-title { font-size: 13px; color: #6B7280; margin-top: 2px; }
.margin-top { margin-top: 24px; }

.table-section-card { background: white; border: 1px solid #E5E7EB; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.toolbar-bar { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid #E5E7EB; gap: 16px; flex-wrap: wrap; }
.search-box { display: flex; align-items: center; gap: 10px; background: #F9FAFB; border: 1.5px solid #E5E7EB; border-radius: 10px; padding: 9px 14px; width: 320px; }
.search-input { border: none; background: transparent; outline: none; font-size: 13.5px; width: 100%; }
.total-count { font-size: 13px; color: #6B7280; }

.table-container { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: #FFFFFF; padding: 13px 16px; font-size: 12px; font-weight: 700; color: #4B5563; text-align: left; border-bottom: 1px solid #E5E7EB; white-space: nowrap; }
.data-table td { padding: 14px 16px; font-size: 13.5px; color: #1F2937; border-bottom: 1px solid #F3F4F6; vertical-align: middle; }
.clickable-row { cursor: pointer; }
.table-row:hover td { background: #FAFAFA; }

.td-name { font-weight: 600; color: #111827; }
.td-cert { white-space: nowrap; }
.cert-main { font-weight: 700; color: #B45309; font-family: monospace; }
.cert-sub { font-size: 11px; color: #6B7280; margin-top: 2px; }

.td-phone { white-space: nowrap; font-family: monospace; font-size: 12px; }
.td-phone-sub { font-size: 11px; color: #6B7280; margin-top: 2px; }
.td-jshshr { font-family: monospace; font-size: 12px; }

.group-dates { font-size: 12px; font-weight: 600; color: #374151; margin-top: 2px; white-space: nowrap; }
.cat-pill { padding: 4px 10px; background: #E8F5E9; color: #2D6A4F; border-radius: 8px; font-size: 12px; font-weight: 700; white-space: nowrap; }
.link-value { cursor: pointer; color: #2D6A4F; }
.link-value:hover { text-decoration: underline; }

.td-amount { white-space: nowrap; }
.text-green { color: #166534; font-weight: 700; }
.free-chip { padding: 3px 9px; background: #EDE9FE; color: #6D28D9; border-radius: 8px; font-size: 12px; font-weight: 700; }

.row-actions { display: flex; gap: 8px; justify-content: flex-end; }
.btn-action-edit, .btn-action-delete { width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; border: 1px solid #E5E7EB; background: #F9FAFB; cursor: pointer; transition: all 0.15s ease; }
.btn-action-edit { color: #2563EB; }
.btn-action-edit:hover { background: #EFF6FF; border-color: #BFDBFE; }
.btn-action-delete { color: #EF4444; }
.btn-action-delete:hover { background: #FEE2E2; border-color: #FCA5A5; }

.state-box, .empty-state { text-align: center; padding: 40px 0; color: #6B7280; }
.spinner { width: 28px; height: 28px; border: 3px solid #E5E7EB; border-top-color: #B45309; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px; }
@keyframes spin { to { transform: rotate(360deg); } }

.modal-overlay { position: fixed; inset: 0; z-index: 1000; background: rgba(15, 23, 42, 0.65); backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-card { background: white; border-radius: 20px; width: 100%; max-width: 460px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); }
.modal-header-banner.amber-banner { padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #F3F4F6; background: linear-gradient(180deg, #FFFBEB 0%, #FFFFFF 100%); }
.header-left-info { display: flex; align-items: center; gap: 12px; }
.header-left-info h3 { font-size: 17px; font-weight: 700; color: #92400E; margin: 0; }
.header-left-info p { font-size: 12px; color: #6B7280; margin-top: 2px; }
.header-icon-box { width: 42px; height: 42px; border-radius: 12px; background: linear-gradient(135deg, #D97706 0%, #92400E 100%); color: white; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.btn-modal-close { background: none; border: none; font-size: 18px; color: #9CA3AF; cursor: pointer; }
.modal-body { padding: 24px; }

.form-group { margin-bottom: 18px; width: 100%; }
.flabel { display: block; font-size: 12.5px; font-weight: 600; color: #374151; margin-bottom: 6px; }
.finput {
  width: 100%; box-sizing: border-box; padding: 11px 14px;
  border: 1.5px solid #E5E7EB; border-radius: 10px; font-size: 14px;
  background-color: #FAFAFA; color: #111827; outline: none;
  transition: all 0.2s ease;
}
.finput:focus { border-color: #D97706; background-color: #FFFFFF; box-shadow: 0 0 0 3.5px rgba(217, 119, 6, 0.12); }
.finput.text-upper { text-transform: uppercase; }

.searchable-select-wrap { position: relative; width: 100%; }
.input-clear-btn {
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  width: 22px; height: 22px; border-radius: 50%; border: none;
  background: #E5E7EB; color: #4B5563; font-size: 11px; line-height: 1;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.input-clear-btn:hover { background: #D1D5DB; color: #111827; }
.searchable-select-wrap .finput { padding-right: 34px; }
.dropdown-options-list { position: absolute; top: 100%; left: 0; right: 0; max-height: 200px; overflow-y: auto; background: white; border: 1.5px solid #D97706; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); z-index: 50; margin-top: 4px; }
.dropdown-option-item { padding: 10px 14px; cursor: pointer; border-bottom: 1px solid #F3F4F6; }
.dropdown-option-item:hover { background: #FFFBEB; }
.dropdown-option-item.selected { background: #FEF3C7; font-weight: 700; }
.dropdown-option-item.highlighted { background: #FFFBEB; }
.opt-name { font-size: 13.5px; font-weight: 600; color: #111827; }
.dropdown-empty { padding: 12px; text-align: center; color: #9CA3AF; font-size: 13px; }
.selected-chip { font-size: 12.5px; color: #D97706; margin-top: 6px; }

.btn-primary-action {
  display: inline-flex; align-items: center; gap: 8px; padding: 11px 20px;
  background: linear-gradient(135deg, #D97706 0%, #92400E 100%); color: white;
  border-radius: 12px; font-weight: 700; font-size: 13.5px;
  box-shadow: 0 4px 14px rgba(217, 119, 6, 0.25); cursor: pointer; transition: all 0.2s ease; border: none;
}
.btn-primary-action:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(217, 119, 6, 0.35); }

.modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.btn-cancel { padding: 10px 18px; border: 1px solid #D1D5DB; background: white; border-radius: 10px; font-weight: 600; font-size: 13px; color: #374151; cursor: pointer; }
.btn-save { padding: 10px 22px; background: linear-gradient(135deg, #D97706 0%, #92400E 100%); color: white; border-radius: 10px; font-weight: 700; font-size: 13.5px; cursor: pointer; border: none; }
.alert-error { background: #FEE2E2; color: #991B1B; padding: 10px 14px; border-radius: 10px; font-size: 13px; margin-bottom: 16px; }
</style>
