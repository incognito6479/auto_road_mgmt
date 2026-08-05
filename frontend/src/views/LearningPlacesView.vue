<template>
  <AppLayout>

    <!-- Top Action Bar -->
    <div class="page-top">
      <div class="top-title-wrap">
        <h2 class="page-main-title">O'quv Joylari</h2>
        <p class="page-sub-title">Tizim o'quv joylari, o'quv xonalari va filiallari ro'yxati</p>
      </div>
      <button v-if="authStore.isAdminOrSuperuser" class="btn-add" @click="openCreateModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="16" height="16" style="margin-right: 6px;">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        Yangi O'quv Joyi
      </button>
    </div>

    <!-- Table Container -->
    <div class="table-card">
      <div v-if="loading" class="state-container">
        <div class="spinner"></div>
        <p class="state-text">O'quv joylari yuklanmoqda...</p>
      </div>

      <div v-else-if="error" class="state-container state-error">
        <p class="state-text">{{ error }}</p>
        <button class="btn-retry" @click="fetchPlaces">Qayta urinish</button>
      </div>

      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>O'quv joyi nomi</th>
              <th>Yaratilgan sana</th>
              <th v-if="authStore.isAdminOrSuperuser" style="text-align: center; width: 100px;">Amallar</th>
            </tr>
            <tr class="col-filter-row">
              <th>
                <input v-model="filterName" class="col-filter-input" type="text" placeholder="Nomi bo'yicha qidirish..." />
              </th>
              <th>
                <div class="col-sort-group">
                  <button type="button" class="col-sort-icon-btn" :class="{ active: dateSort === 'asc' }" title="O'sish tartibida (eskidan yangiga)" @click="setDateSort('asc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 20V4"></path>
                      <path d="M3 8l3-4 3 4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button type="button" class="col-sort-icon-btn" :class="{ active: dateSort === 'desc' }" title="Kamayish tartibida (yangidan eskiga)" @click="setDateSort('desc')">
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
                  <input v-model="dateFrom" type="date" class="col-date-input" title="Yaratilgan sana (dan)" />
                  <input v-model="dateTo" type="date" class="col-date-input" title="Yaratilgan sana (gacha)" />
                </div>
              </th>
              <th v-if="authStore.isAdminOrSuperuser"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="displayedPlaces.length === 0">
              <td :colspan="authStore.isAdminOrSuperuser ? 3 : 2" class="td-empty">O'quv joylari topilmadi.</td>
            </tr>
            <tr v-for="p in displayedPlaces" :key="p.id" class="table-row clickable-row" @click="goToPlaceDetail(p.id)">
              <td class="td-name">
                <div class="place-name-text">{{ p.place_name }}</div>
              </td>
              <td class="td-date">{{ formatDate(p.created_at) }}</td>
              <td v-if="authStore.isAdminOrSuperuser" style="text-align: center;">
                <div class="action-btn-group">
                  <button class="btn-action btn-edit" @click.stop="openEditModal(p)" title="Tahrirlash">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                  <button class="btn-action btn-delete" @click.stop="openDeleteModal(p)" title="O'chirish">
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

      <div v-if="filteredPlaces.length > 0" class="pagination-bar">
        <span class="pagination-info">
          Jami: <strong>{{ filteredPlaces.length }}</strong> tadan <strong>{{ displayedPlaces.length }}</strong> ko'rsatilmoqda
        </span>
        <div class="pagination-actions">
          <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">Oldingi</button>
          <span v-if="pageSizeOption !== 'all'" class="page-num">Sahifa {{ Math.min(currentPage, displayTotalPages) }} / {{ displayTotalPages }}</span>
          <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === displayTotalPages" @click="changePage(currentPage + 1)">Keyingi</button>
          <label class="page-size-label" for="places-page-size">Ko'rsatish:</label>
          <div class="select-wrap">
            <select id="places-page-size" v-model="pageSizeOption" class="page-size-select">
              <option value="50">50</option>
              <option value="100">100</option>
              <option value="200">200</option>
              <option value="all">Barchasi</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Create / Edit Modal Dialog -->
    <dialog ref="placeModal" class="modal-dialog" @click="onPlaceModalClick">
      <div class="modal-header">
        <div class="header-badge-wrap">
          <div class="header-badge-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="2" width="22" height="22">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
              <circle cx="12" cy="10" r="3"></circle>
            </svg>
          </div>
          <div>
            <h3 class="modal-title">{{ isEditing ? "O'quv Joyini Tahrirlash" : "Yangi O'quv Joyi Yaratish" }}</h3>
            <p class="modal-sub">O'quv binosi yoki filiali nomini kiriting</p>
          </div>
        </div>
        <button class="btn-close" @click="closePlaceModal">✕</button>
      </div>

      <form @submit.prevent="savePlace" class="modal-form">
        <div v-if="modalError" class="modal-alert modal-alert-error">
          {{ modalError }}
        </div>

        <div class="form-group">
          <label class="form-label">O'quv joyi nomi <span class="req">*</span></label>
          <input
            v-model="placeForm.place_name"
            type="text"
            placeholder="Masalan: Chilonzor filiali (102-xona)"
            required
            class="form-input"
          />
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closePlaceModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="saving">
            <span v-if="saving" class="btn-spinner"></span>
            {{ saving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Delete Confirmation Modal Dialog -->
    <dialog ref="deleteModal" class="modal-dialog modal-dialog-sm">
      <div class="modal-header">
        <h3 class="modal-title">O'quv Joyini O'chirish</h3>
        <button class="btn-close" @click="closeDeleteModal">✕</button>
      </div>

      <div class="modal-body" style="padding: 20px 24px;">
        <div class="delete-warning-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2" width="48" height="48">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
        </div>
        <p class="delete-confirm-text">
          Haqiqatan ham <strong>{{ deletingPlace ? deletingPlace.place_name : '' }}</strong> o'quv joyini o'chirmoqchimisiz?
        </p>

        <div v-if="deleteError" class="modal-alert modal-alert-error" style="margin-top: 12px;">
          {{ deleteError }}
        </div>

        <div class="modal-actions" style="margin-top: 24px;">
          <button type="button" class="btn-cancel" @click="closeDeleteModal">Bekor qilish</button>
          <button type="button" class="btn-delete-confirm" :disabled="deleting" @click="confirmDelete">
            <span v-if="deleting" class="btn-spinner"></span>
            {{ deleting ? "O'chirilmoqda..." : "Ha, O'chirish" }}
          </button>
        </div>
      </div>
    </dialog>

  </AppLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useBranchStore } from '@/stores/branch'

const authStore = useAuthStore()
const branchStore = useBranchStore()
const router = useRouter()

const goToPlaceDetail = (id) => {
  router.push(`/learning-places/${id}`)
}
const places = ref([])
const loading = ref(false)
const error = ref('')
const filterName = ref('')
const dateSort = ref('')
const dateFrom = ref('')
const dateTo = ref('')

// ── Row-fetch-count selector ──────────────────────────────────
// Replaces classic next/prev pagination: fetch always pulls every learning
// place (see fetchPlaces below), filtering runs client-side against the
// full set (filteredPlaces), and pageSizeOption instead controls how many
// of the *filtered* results are shown per page (see
// displayedPlaces/changePage below).
const pageSizeOption = ref('50')
const totalCount = ref(0)
const currentPage = ref(1)

function setDateSort(dir) {
  dateSort.value = dateSort.value === dir ? '' : dir
}

// Modal state
const placeModal = ref(null)
const isEditing = ref(false)
const editingId = ref(null)
const saving = ref(false)
const modalError = ref('')
const placeForm = ref({
  place_name: '',
})

// Delete modal state
const deleteModal = ref(null)
const deletingPlace = ref(null)
const deleting = ref(false)
const deleteError = ref('')

const fetchPlaces = async () => {
  loading.value = true
  error.value = ''
  try {
    // Always the full dataset — filtering/sorting/pagination below all
    // need to see every row, not just one page of them.
    const response = await api.get('/learning-places/', { params: { page: 1, page_size: 100000 } })
    places.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
    totalCount.value = response.data.count ?? places.value.length
  } catch (err) {
    console.error(err)
    error.value = "O'quv joylarini yuklashda xatolik yuz berdi."
  } finally {
    loading.value = false
  }
}

const filteredPlaces = computed(() => {
  let list = places.value.filter(p => {
    const q = filterName.value.toLowerCase().trim()
    const matchSearch = !q || p.place_name.toLowerCase().includes(q)
    return matchSearch && branchStore.isBranchMatch(p)
  })
  if (dateFrom.value) list = list.filter(p => p.created_at && p.created_at.slice(0, 10) >= dateFrom.value)
  if (dateTo.value) list = list.filter(p => p.created_at && p.created_at.slice(0, 10) <= dateTo.value)
  if (dateSort.value) {
    list.sort((a, b) => {
      const da = new Date(a.created_at).getTime()
      const db = new Date(b.created_at).getTime()
      return dateSort.value === 'asc' ? da - db : db - da
    })
  }
  return list
})

// pageSizeOption now purely controls how many of the *filtered* rows show
// per page — currentPage is clamped here (not via a watcher enumerating
// every filter ref) so it self-corrects the moment a filter shrinks the
// result set out from under it.
const displayPageSize = computed(() => pageSizeOption.value === 'all' ? Infinity : Number(pageSizeOption.value))
const displayTotalPages = computed(() => {
  if (pageSizeOption.value === 'all') return 1
  return Math.max(1, Math.ceil(filteredPlaces.value.length / displayPageSize.value))
})
const displayedPlaces = computed(() => {
  if (pageSizeOption.value === 'all') return filteredPlaces.value
  const page = Math.min(currentPage.value, displayTotalPages.value)
  const start = (page - 1) * displayPageSize.value
  return filteredPlaces.value.slice(start, start + displayPageSize.value)
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

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('uz-UZ')
}

const openCreateModal = () => {
  if (!authStore.isAdminOrSuperuser) {
    alert("O'quv joyini yaratish faqat admin va superuser uchun ruxsat etilgan.")
    return
  }
  isEditing.value = false
  editingId.value = null
  modalError.value = ''
  placeForm.value = { place_name: '' }
  if (placeModal.value) placeModal.value.showModal()
}

const openEditModal = (p) => {
  if (!authStore.isAdminOrSuperuser) {
    alert("O'quv joyini tahrirlash faqat admin va superuser uchun ruxsat etilgan.")
    return
  }
  isEditing.value = true
  editingId.value = p.id
  modalError.value = ''
  placeForm.value = { place_name: p.place_name }
  if (placeModal.value) placeModal.value.showModal()
}

const closePlaceModal = () => {
  if (placeModal.value) placeModal.value.close()
}

// A click on the <dialog> element itself (rather than on its content) means
// the click landed on the backdrop, since the dialog box is sized to its
// content — checking bounding coordinates is more reliable cross-browser
// than comparing event.target.
const onPlaceModalClick = (e) => {
  if (!placeModal.value) return
  const rect = placeModal.value.getBoundingClientRect()
  const clickedOutside = e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom
  if (clickedOutside) closePlaceModal()
}

const savePlace = async () => {
  if (!authStore.isAdminOrSuperuser) return
  if (!placeForm.value.place_name.trim()) {
    modalError.value = "O'quv joyi nomini kiriting."
    return
  }

  saving.value = true
  modalError.value = ''

  try {
    const payload = { place_name: placeForm.value.place_name.trim() }
    if (isEditing.value) {
      await api.patch(`/learning-places/${editingId.value}/`, payload)
    } else {
      await api.post('/learning-places/', payload)
    }
    closePlaceModal()
    await fetchPlaces()
  } catch (err) {
    console.error(err)
    modalError.value = "Saqlashda xatolik yuz berdi. Qayta urinib ko'ring."
  } finally {
    saving.value = false
  }
}

const openDeleteModal = (p) => {
  if (!authStore.isAdminOrSuperuser) return
  deletingPlace.value = p
  deleteError.value = ''
  if (deleteModal.value) deleteModal.value.showModal()
}

const closeDeleteModal = () => {
  if (deleteModal.value) deleteModal.value.close()
  deletingPlace.value = null
}

const confirmDelete = async () => {
  if (!deletingPlace.value) return
  deleting.value = true
  deleteError.value = ''
  try {
    await api.delete(`/learning-places/${deletingPlace.value.id}/`)
    closeDeleteModal()
    await fetchPlaces()
  } catch (err) {
    console.error(err)
    deleteError.value = "O'chirishda xatolik yuz berdi."
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchCurrentUser()
  }
  fetchPlaces()
})
</script>

<style scoped>
.page-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.page-main-title {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
}
.page-sub-title {
  font-size: 13px;
  color: #6B7280;
  margin-top: 2px;
}
.btn-add {
  display: inline-flex;
  align-items: center;
  padding: 10px 18px;
  background: #2D6A4F;
  color: white;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13.5px;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-add:hover { background: #1B4332; }

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
.place-name-text { font-weight: 600; color: #111827; }
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
  flex-shrink: 0;
}
.btn-clear-date:hover { background: #E5E7EB; color: #111827; }

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

/* Modal Dialog Base */
.modal-dialog {
  border: none;
  border-radius: 20px;
  padding: 0;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  margin: auto;
}
.modal-dialog-sm { max-width: 440px; }
.modal-dialog::backdrop {
  background: rgba(17, 24, 39, 0.45);
  backdrop-filter: blur(6px);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px 28px 18px 28px;
  border-bottom: 1px solid #F3F4F6;
}
.header-badge-wrap { display: flex; align-items: flex-start; gap: 14px; }
.header-badge-icon {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
  border: 1px solid #A7F3D0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.modal-title { font-size: 18px; font-weight: 700; color: #111827; margin: 0 0 4px 0; }
.modal-sub { font-size: 12.5px; color: #6B7280; margin: 0; }
.btn-close {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #F3F4F6;
  border: none;
  color: #6B7280;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.modal-form {
  padding: 24px 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  box-sizing: border-box;
}
.form-group { display: flex; flex-direction: column; gap: 6px; width: 100%; box-sizing: border-box; }
.form-label { font-size: 12.5px; font-weight: 600; color: #374151; }
.req { color: #DC2626; }
.form-input {
  width: 100%;
  box-sizing: border-box;
  padding: 10px 14px;
  font-size: 13.5px;
  border: 1px solid #D1D5DB;
  border-radius: 10px;
  outline: none;
  background: #F9FAFB;
}
.form-input:focus { border-color: #2D6A4F; background: white; }

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}
.btn-cancel {
  padding: 10px 20px;
  background: #F3F4F6;
  color: #4B5563;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13.5px;
  border: none;
}
.btn-save {
  padding: 10px 24px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%);
  color: white;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13.5px;
  border: none;
}
.btn-delete-confirm {
  padding: 10px 22px;
  background: #DC2626;
  color: white;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13.5px;
  border: none;
}

.modal-alert {
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 13px;
}
.modal-alert-error {
  background: #FEE2E2;
  color: #991B1B;
  border: 1px solid #FCA5A5;
}

.delete-warning-icon { display: flex; justify-content: center; margin-bottom: 12px; }
.delete-confirm-text { text-align: center; font-size: 15px; color: #111827; }

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
.page-size-select:focus { border-color: #2D6A4F; outline: none; }

.state-container { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 48px; gap: 12px; }
.spinner { width: 32px; height: 32px; border: 3px solid #E5E7EB; border-top-color: #2D6A4F; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.state-text { color: #6B7280; font-size: 14px; }
</style>
