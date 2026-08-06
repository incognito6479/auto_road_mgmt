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
        <div class="total-count">
          Jami: <strong>{{ filteredEnrollments.length }}</strong> ta sertifikat
        </div>
      </div>

      <div class="table-container">
        <div v-if="loading" class="state-box">
          <div class="spinner"></div>
          <span>Sertifikatlar yuklanmoqda...</span>
        </div>

        <div v-else-if="enrollments.length === 0" class="empty-state">
          <p>Sertifikatlar topilmadi</p>
        </div>

        <table v-else class="data-table">
          <thead>
            <tr>
              <th>O'quvchi F.I.SH.</th>
              <th>Sertifikat</th>
              <th>Sertifikat sanasi</th>
              <th>Kategoriya</th>
              <th>Guruh</th>
              <th>Guruh boshlanishi</th>
              <th>Guruh tugashi</th>
              <th>O'qituvchi</th>
              <th>Instruktor</th>
              <th>Agent</th>
              <th>Shartnoma</th>
              <th>To'langan</th>
              <th>Qarzdorlik</th>
              <th v-if="authStore.isSuperuser" style="text-align: right;">Amallar</th>
            </tr>
            <tr class="col-filter-row">
              <th>
                <input v-model="filterStudentName" class="col-filter-input" type="text" placeholder="Ism bo'yicha qidirish..." />
              </th>
              <th>
                <input v-model="filterCertif" class="col-filter-input" type="text" placeholder="Sertifikat raqami..." />
              </th>
              <th>
                <div class="col-sort-group">
                  <button type="button" class="col-sort-icon-btn" :class="{ active: certDateSort === 'asc' }" title="O'sish tartibida (eskidan yangiga)" @click="setSort('certDate', 'asc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 20V4"></path>
                      <path d="M3 8l3-4 3 4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button type="button" class="col-sort-icon-btn" :class="{ active: certDateSort === 'desc' }" title="Kamayish tartibida (yangidan eskiga)" @click="setSort('certDate', 'desc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 4v16"></path>
                      <path d="M3 16l3 4 3-4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button v-if="certDateFrom || certDateTo" type="button" class="btn-clear-date" @click="certDateFrom = ''; certDateTo = ''" title="Tozalash">✕</button>
                </div>
                <div class="col-date-range">
                  <input v-model="certDateFrom" type="date" class="col-date-input" title="Sertifikat sanasi (dan)" />
                  <input v-model="certDateTo" type="date" class="col-date-input" title="Sertifikat sanasi (gacha)" />
                </div>
              </th>
              <th>
                <div class="select-wrap-relative">
                  <select v-model="filterCategory" class="col-filter-select">
                    <option value="">Barchasi</option>
                    <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                  </select>
                </div>
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
              <th></th>
              <th></th>
              <th>
                <div class="select-wrap-relative">
                  <select v-model="filterDebt" class="col-filter-select">
                    <option value="">Barchasi</option>
                    <option value="has">Bor</option>
                    <option value="none">Yo'q</option>
                  </select>
                </div>
              </th>
              <th v-if="authStore.isSuperuser"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="displayedEnrollments.length === 0">
              <td :colspan="authStore.isSuperuser ? 14 : 13" class="td-empty">Filtrlarga mos sertifikat topilmadi</td>
            </tr>
            <tr v-for="e in displayedEnrollments" :key="e.id" class="table-row clickable-row" @click="goStudent(e.student)">
              <td class="td-name">{{ e.student_name || 'Noma\'lum' }}</td>
              <td class="td-cert">
                <div class="cert-main">{{ e.student_certificate_series || '' }} {{ e.student_certificate_number }}</div>
              </td>
              <td class="td-date">{{ e.student_certificate_added_date ? formatDate(e.student_certificate_added_date) : '-' }}</td>
              <td><span class="cat-pill">{{ e.category_name || '-' }}</span></td>
              <td @click.stop>
                <span v-if="e.group" class="link-value" @click="goGroup(e.group)">{{ e.group_name || '-' }}</span>
                <span v-else>{{ e.group_name || '-' }}</span>
              </td>
              <td class="td-date">{{ groupsById[e.group] ? formatDate(groupsById[e.group].started_at) : '-' }}</td>
              <td class="td-date">{{ groupsById[e.group] ? formatDate(groupsById[e.group].ends_at) : '-' }}</td>
              <td @click.stop>
                <span v-if="e.coordinator_name" class="link-value" @click="goUser(e.coordinator)">{{ e.coordinator_name }}</span>
                <span v-else>-</span>
              </td>
              <td @click.stop>
                <span v-if="e.instructor_name" class="link-value" @click="goUser(e.instructor)">{{ e.instructor_name }}</span>
                <span v-else>-</span>
              </td>
              <td @click.stop>
                <span v-if="e.agent_name" class="link-value" @click="goAgent(e.agent)">{{ e.agent_name }}</span>
                <span v-else>-</span>
              </td>
              <td class="td-amount">
                <span v-if="e.enrolled_free" class="free-chip">Tekin</span>
                <span v-else>{{ formatMoney(e.enrolled_amount) }}</span>
              </td>
              <td class="td-amount text-green">{{ formatMoney(e.paid_amount || 0) }}</td>
              <td class="td-amount">
                <span v-if="getDebt(e) > 0" class="debt-chip">-{{ formatMoney(getDebt(e)) }}</span>
                <span v-else class="paid-chip">To'langan</span>
              </td>
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

      <div class="pagination-bar">
        <span class="pagination-info">
          Jami: <strong>{{ filteredEnrollments.length }}</strong> tadan <strong>{{ displayedEnrollments.length }}</strong> ko'rsatilmoqda
        </span>
        <div class="pagination-actions">
          <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">Oldingi</button>
          <span v-if="pageSizeOption !== 'all'" class="page-num">Sahifa {{ Math.min(currentPage, displayTotalPages) }} / {{ displayTotalPages }}</span>
          <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === displayTotalPages" @click="changePage(currentPage + 1)">Keyingi</button>
          <label class="page-size-label" for="certificates-page-size">Ko'rsatish:</label>
          <div class="select-wrap">
            <select id="certificates-page-size" v-model="pageSizeOption" class="page-size-select">
              <option value="50">50</option>
              <option value="100">100</option>
              <option value="200">200</option>
              <option value="all">Barchasi</option>
            </select>
          </div>
        </div>
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
                  <div v-if="loadingAddStudents" class="dropdown-empty">Yuklanmoqda...</div>
                  <template v-else>
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
                  </template>
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
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import ConfirmDeleteModal from '@/components/ConfirmDeleteModal.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { formatMoney, formatDate } from '@/utils/formatters'
import { useSearchSelectKeyboard } from '@/composables/useSearchSelectKeyboard'
import { useGroupSelect } from '@/composables/useGroupSelect'

const router = useRouter()
const authStore = useAuthStore()

const enrollments = ref([])
const groups = ref([])
const categories = ref([])
const loading = ref(true)

const groupsById = computed(() => {
  const map = {}
  groups.value.forEach(g => { map[g.id] = g })
  return map
})

// Header-column filters
const filterStudentName = ref('')
const filterCertif = ref('')
const filterCategory = ref('')
const filterGroupName = ref('')
const filterDebt = ref('')
const groupStartSort = ref('')
const groupEndSort = ref('')
const certDateSort = ref('')

// ── Group start/end date-range column filters ───────────────────────────
const groupStartFrom = ref('')
const groupStartTo = ref('')
const groupEndFrom = ref('')
const groupEndTo = ref('')
const certDateFrom = ref('')
const certDateTo = ref('')

const sortRefs = { groupStart: groupStartSort, groupEnd: groupEndSort, certDate: certDateSort }
function setSort(field, dir) {
  const target = sortRefs[field]
  Object.values(sortRefs).forEach(r => { if (r !== target) r.value = '' })
  target.value = target.value === dir ? '' : dir
}

const getDebt = (e) => {
  if (!e || e.enrolled_free) return 0
  const contract = Number(e.enrolled_amount) || 0
  const paid = Number(e.paid_amount) || 0
  return Math.max(0, contract - paid)
}

// All header filters (student name, certificate, category, group name,
// group start/end date ranges, debt, sort) run entirely on the client
// against the already-fetched `enrollments` list — no per-keystroke or
// per-filter network round trip, so there's no debounce delay and no
// input re-render to steal focus/cursor position. Only the row-fetch-count
// selector triggers a new backend request (see watch below).
const filteredEnrollments = computed(() => {
  const name = filterStudentName.value.toLowerCase().trim()
  const certif = filterCertif.value.toLowerCase().trim()
  const group = filterGroupName.value.toLowerCase().trim()

  let list = enrollments.value.filter(e => {
    if (name && !(e.student_name || '').toLowerCase().includes(name)) return false
    if (certif && !`${e.student_certificate_series || ''}${e.student_certificate_number || ''}`.toLowerCase().includes(certif)) return false
    if (filterCategory.value && String(e.category) !== String(filterCategory.value)) return false
    if (group && !(e.group_name || '').toLowerCase().includes(group)) return false
    if (filterDebt.value === 'has' && getDebt(e) <= 0) return false
    if (filterDebt.value === 'none' && getDebt(e) > 0) return false
    // student_certificate_added_date is a full timestamp, not a bare date —
    // slice before comparing to the plain YYYY-MM-DD filter value, otherwise
    // records from the selected "to" day itself get wrongly excluded.
    if (certDateFrom.value && !(e.student_certificate_added_date && e.student_certificate_added_date.slice(0, 10) >= certDateFrom.value)) return false
    if (certDateTo.value && !(e.student_certificate_added_date && e.student_certificate_added_date.slice(0, 10) <= certDateTo.value)) return false

    const g = groupsById.value[e.group]
    if (groupStartFrom.value && !(g && g.started_at && g.started_at >= groupStartFrom.value)) return false
    if (groupStartTo.value && !(g && g.started_at && g.started_at <= groupStartTo.value)) return false
    if (groupEndFrom.value && !(g && g.ends_at && g.ends_at >= groupEndFrom.value)) return false
    if (groupEndTo.value && !(g && g.ends_at && g.ends_at <= groupEndTo.value)) return false

    return true
  })

  const field = groupStartSort.value ? 'started_at' : (groupEndSort.value ? 'ends_at' : null)
  if (field) {
    const dir = (groupStartSort.value || groupEndSort.value) === 'asc' ? 1 : -1
    list = list.slice().sort((a, b) => {
      const ga = groupsById.value[a.group]
      const gb = groupsById.value[b.group]
      const ta = ga && ga[field] ? new Date(ga[field]).getTime() : null
      const tb = gb && gb[field] ? new Date(gb[field]).getTime() : null
      if (ta === null && tb === null) return 0
      if (ta === null) return 1
      if (tb === null) return -1
      return (ta - tb) * dir
    })
  } else if (certDateSort.value) {
    const dir = certDateSort.value === 'asc' ? 1 : -1
    list = list.slice().sort((a, b) => {
      const ta = a.student_certificate_added_date ? new Date(a.student_certificate_added_date).getTime() : null
      const tb = b.student_certificate_added_date ? new Date(b.student_certificate_added_date).getTime() : null
      if (ta === null && tb === null) return 0
      if (ta === null) return 1
      if (tb === null) return -1
      return (ta - tb) * dir
    })
  }

  return list
})

// ── Row-fetch-count selector ──────────────────────────────────
// Replaces classic next/prev pagination: pick how many rows to pull from
// the backend in one shot, then filter/sort them instantly on the client
// (see displayedEnrollments below) instead of round-tripping per filter
// change. Filtering has to see every row — not just whatever page happened
// to be fetched — so the fetch itself always pulls everything;
// pageSizeOption instead controls how many of the *filtered* results are
// shown per page (see displayedEnrollments/changePage below).
const pageSizeOption = ref('50')
const totalCount = ref(0) // total certificate-bearing enrollments, per backend
const currentPage = ref(1)

// pageSizeOption now purely controls how many of the *filtered* rows show
// per page — currentPage is clamped here so it self-corrects the moment a
// filter shrinks the result set out from under it.
const displayPageSize = computed(() => pageSizeOption.value === 'all' ? Infinity : Number(pageSizeOption.value))
const displayTotalPages = computed(() => {
  if (pageSizeOption.value === 'all') return 1
  return Math.max(1, Math.ceil(filteredEnrollments.value.length / displayPageSize.value))
})
const displayedEnrollments = computed(() => {
  if (pageSizeOption.value === 'all') return filteredEnrollments.value
  const page = Math.min(currentPage.value, displayTotalPages.value)
  const start = (page - 1) * displayPageSize.value
  return filteredEnrollments.value.slice(start, start + displayPageSize.value)
})
function changePage(page) {
  if (page < 1 || page > displayTotalPages.value) return
  currentPage.value = page
}

function goStudent(studentId) {
  if (studentId) router.push(`/students/${studentId}`)
}
function goUser(id) {
  if (id) router.push(`/users/${id}`)
}
function goGroup(id) {
  if (id) router.push(`/groups/${id}`)
}
function goAgent(id) {
  if (id) router.push(`/agents/${id}`)
}

async function fetchCategories() {
  try {
    const res = await api.get('/categories/')
    categories.value = res.data.results ? res.data.results : res.data
  } catch (err) {
    console.error(err)
  }
}

async function fetchGroups() {
  try {
    const res = await api.get('/groups/', { params: { page_size: 1000 } })
    groups.value = res.data.results || res.data
  } catch (err) { console.error(err) }
}

// Memoized so every call after the first reuses the same in-flight/settled
// request instead of re-fetching.
let groupsLoadPromise = null
function ensureGroupsLoaded() {
  if (!groupsLoadPromise) groupsLoadPromise = fetchGroups()
  return groupsLoadPromise
}

async function fetchEnrollments() {
  loading.value = true
  try {
    // Awaited alongside groups so the table doesn't reveal itself (and
    // read groupsById) before group start/end data actually exists —
    // otherwise those columns render as "-" and pop in once the separate
    // /groups/ request finishes a moment later.
    // Always the full dataset — filtering/sorting/pagination above all
    // need to see every row, not just one page of them.
    const [res] = await Promise.all([
      api.get('/enrollments/', { params: { has_certificate: 'true', page: 1, page_size: 100000 } }),
      ensureGroupsLoaded(),
    ])
    const rawList = res.data.results ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    enrollments.value = rawList
    totalCount.value = res.data.count ?? rawList.length
  } catch (err) { console.error(err) }
  finally { loading.value = false }
}

// Only fetchEnrollments (on mount) needs a backend round trip; every
// filter above is purely client-side, and pageSizeOption now only controls
// how many of the filtered rows show per page.
watch(pageSizeOption, () => {
  currentPage.value = 1
})

// ── Add modal (group -> student cascade) ────────────────
const showAddModal = ref(false)
const addSaving = ref(false)
const addModalError = ref(null)
const allEnrollments = ref([])
const loadingAddStudents = ref(false)
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
  loadingAddStudents.value = true
  try {
    const res = await api.get('/enrollments/', { params: { page_size: 1000 } })
    allEnrollments.value = res.data.results || res.data
  } catch (err) { console.error(err) }
  finally { loadingAddStudents.value = false }
}

function openAddModal() {
  addModalError.value = null
  addStudentQuery.value = ''
  selectedAddStudentLabel.value = ''
  showAddStudentDropdown.value = false
  resetAddGroupSelect()
  addForm.value = { student: '', certificate_series: 'SA', certificate_number: '' }
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
  fetchCategories()
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
.toolbar-bar { display: flex; align-items: center; justify-content: flex-end; padding: 16px 20px; border-bottom: 1px solid #E5E7EB; gap: 16px; flex-wrap: wrap; }
.total-count { font-size: 13px; color: #6B7280; }

/* Bounded, independently-scrolling table body so the header (both the
   label row and the column-filter row) sticks to the top of this
   container as rows scroll underneath, instead of scrolling away with
   the page. */
.table-container { overflow: auto; max-height: 600px; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { background: #FFFFFF; padding: 13px 16px; font-size: 12px; font-weight: 700; color: #4B5563; text-align: left; border-bottom: 1px solid #E5E7EB; white-space: nowrap; }
.data-table td { padding: 14px 16px; font-size: 13.5px; color: #1F2937; border-bottom: 1px solid #F3F4F6; vertical-align: middle; }
.data-table thead { position: sticky; top: 0; z-index: 3; }
.data-table thead tr.col-filter-row th { padding: 8px 10px; background: #FAFAFB; }
.clickable-row { cursor: pointer; }
.table-row:hover td { background: #FAFAFA; }

.td-name { font-weight: 600; color: #111827; }
.td-cert { white-space: nowrap; }
.td-date { white-space: nowrap; }
.td-empty { text-align: center; padding: 32px; color: #9CA3AF; }
.cert-main { font-weight: 700; color: #B45309; font-family: monospace; }

.cat-pill { padding: 4px 10px; background: #E8F5E9; color: #2D6A4F; border-radius: 8px; font-size: 12px; font-weight: 700; white-space: nowrap; }
.link-value { cursor: pointer; color: #2563EB; text-decoration: underline; }
.debt-chip { padding: 4px 10px; background: #FEE2E2; color: #991B1B; border-radius: 8px; font-size: 12.5px; font-weight: 700; display: inline-block; }
.paid-chip { padding: 4px 10px; background: #DCFCE7; color: #15803D; border-radius: 8px; font-size: 12.5px; font-weight: 700; display: inline-block; }

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
.col-filter-input:focus, .col-filter-select:focus { border-color: #D97706; }
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
.col-sort-icon-btn.active { border-color: #D97706; color: #D97706; background: #FFFBEB; }

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

/* ── Per-column date-range filters (under sort buttons) ────── */
.col-date-range {
  display: flex;
  flex-direction: column;
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
.col-date-input:focus { border-color: #D97706; outline: none; }

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
.page-size-select:focus { border-color: #D97706; outline: none; }
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
.select-wrap-relative { position: relative; width: 100%; }
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
