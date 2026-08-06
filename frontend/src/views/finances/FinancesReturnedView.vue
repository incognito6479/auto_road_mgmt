<template>
  <AppLayout>

    <div class="page-top">
      <div>
        <h2 class="page-main-title">Pul Qaytarish</h2>
        <p class="page-sub-title">O'quvchilarga bekor qilingan yoki qaytarilgan pul operatsiyalari</p>
      </div>

      <button v-if="authStore.canReturnMoney" class="btn-primary-action btn-orange" @click="openCreateModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="18" height="18">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        <span>Pul qaytarish</span>
      </button>
    </div>

    <!-- Metrics Cards -->
    <div class="metrics-cards-grid">
      <div class="card-metric card-red">
        <div class="card-metric-icon">↩️</div>
        <div>
          <span class="metric-lbl">Qaytarilgan Operatsiyalar Soni</span>
          <h4 class="metric-val text-red">{{ metrics.count }} ta to'lov</h4>
        </div>
      </div>

      <div class="card-metric card-orange font-hero">
        <div class="card-metric-icon">💸</div>
        <div>
          <span class="metric-lbl">Jami Qaytarilgan Summa</span>
          <h4 class="metric-val text-orange">{{ formatMoney(metrics.total) }}</h4>
        </div>
      </div>
    </div>

    <!-- Table Section -->
    <div class="table-section-card margin-top">
      <div class="table-container">
        <div v-if="loading" class="state-box">
          <div class="spinner"></div>
          <span>Qaytarilgan to'lovlar yuklanmoqda...</span>
        </div>

        <div v-else class="table-scroll-area">
        <table class="data-table">
          <thead>
            <tr>
              <th>O'quvchi F.I.SH.</th>
              <th>Kategoriya</th>
              <th>Guruh</th>
              <th>Guruh boshlanishi</th>
              <th>Guruh tugashi</th>
              <th>O'quvchi to'lagan summa</th>
              <th>Qaytarilgan Summa</th>
              <th>Usul</th>
              <th>Sana &amp; Vaqt</th>
              <th>To'lovni kiritgan</th>
              <th>Izoh</th>
              <th style="width: 110px; text-align: right;">Amallar</th>
            </tr>
            <tr class="col-filter-row">
              <th>
                <input v-model="filterStudentName" class="col-filter-input" type="text" placeholder="Ism bo'yicha qidirish..." />
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
              <th>
                <div class="col-sort-group">
                  <button type="button" class="col-sort-icon-btn" :class="{ active: studentPaidSort === 'asc' }" title="O'sish tartibida" @click="setSort('studentPaid', 'asc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 20V4"></path>
                      <path d="M3 8l3-4 3 4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button type="button" class="col-sort-icon-btn" :class="{ active: studentPaidSort === 'desc' }" title="Kamayish tartibida" @click="setSort('studentPaid', 'desc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 4v16"></path>
                      <path d="M3 16l3 4 3-4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                </div>
              </th>
              <th>
                <div class="col-sort-group">
                  <button type="button" class="col-sort-icon-btn" :class="{ active: amountSort === 'asc' }" title="O'sish tartibida" @click="setSort('amount', 'asc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 20V4"></path>
                      <path d="M3 8l3-4 3 4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button type="button" class="col-sort-icon-btn" :class="{ active: amountSort === 'desc' }" title="Kamayish tartibida" @click="setSort('amount', 'desc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 4v16"></path>
                      <path d="M3 16l3 4 3-4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                </div>
              </th>
              <th>
                <div class="select-wrap-relative">
                  <select v-model="filterMethod" class="col-filter-select">
                    <option value="">Barchasi</option>
                    <option value="cash">Naqd</option>
                    <option value="card">Karta</option>
                    <option value="qr_code">QR code</option>
                    <option value="click">Click</option>
                    <option value="transfer">O'tkazma</option>
                  </select>
                </div>
              </th>
              <th>
                <div class="col-sort-group">
                  <button type="button" class="col-sort-icon-btn" :class="{ active: paymentDateSort === 'asc' }" title="O'sish tartibida (eskidan yangiga)" @click="setSort('paymentDate', 'asc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 20V4"></path>
                      <path d="M3 8l3-4 3 4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button type="button" class="col-sort-icon-btn" :class="{ active: paymentDateSort === 'desc' }" title="Kamayish tartibida (yangidan eskiga)" @click="setSort('paymentDate', 'desc')">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 4v16"></path>
                      <path d="M3 16l3 4 3-4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button v-if="paymentDateFrom || paymentDateTo" type="button" class="btn-clear-date" @click="paymentDateFrom = ''; paymentDateTo = ''" title="Tozalash">✕</button>
                </div>
                <div class="col-date-range">
                  <input v-model="paymentDateFrom" type="date" class="col-date-input" title="Sana (dan)" />
                  <input v-model="paymentDateTo" type="date" class="col-date-input" title="Sana (gacha)" />
                </div>
              </th>
              <th>
                <div class="select-wrap-relative">
                  <select v-model="filterCashierId" class="col-filter-select">
                    <option value="">Barchasi</option>
                    <option v-for="c in distinctCashiers" :key="c.id" :value="c.id">{{ c.name }}</option>
                  </select>
                </div>
              </th>
              <th></th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="displayedPayments.length === 0">
              <td colspan="12" class="no-data">Qaytarilgan statusdagi to'lovlar topilmadi</td>
            </tr>
            <tr v-for="p in displayedPayments" :key="p.id" class="table-row">
              <td class="td-name">
                <div v-if="p.student" class="student-name link-value" @click="goStudent(p.student)">{{ p.student_name || 'Noma\'lum' }}</div>
                <div v-else class="student-name">{{ p.student_name || 'Noma\'lum' }}</div>
              </td>
              <td><span class="cat-pill">{{ p.category_name || '-' }}</span></td>
              <td>
                <span v-if="p.group" class="link-value" @click="goGroup(p.group)">{{ p.group_name || '-' }}</span>
                <span v-else>{{ p.group_name || '-' }}</span>
              </td>
              <td>{{ p.group_started_at ? formatDate(p.group_started_at) : '-' }}</td>
              <td>{{ p.group_ends_at ? formatDate(p.group_ends_at) : '-' }}</td>
              <td>{{ p.student_paid_amount != null ? formatMoney(p.student_paid_amount) : '-' }}</td>
              <td class="td-amount">
                <span class="amount-val text-red">-{{ formatMoney(p.amount) }}</span>
              </td>
              <td><span class="method-chip">{{ methodText(p.method) }}</span></td>
              <td class="td-date">{{ formatDateTime(p.created_at) }}</td>
              <td>
                <span v-if="p.created_by" class="link-value" @click="goUser(p.created_by)">{{ p.created_by_name || '-' }}</span>
                <span v-else>{{ p.created_by_name || '-' }}</span>
              </td>
              <td>{{ p.notes || '-' }}</td>
              <td style="text-align: right;">
                <div class="row-actions">
                  <template v-if="authStore.isSuperuser">
                    <button class="btn-action-edit" @click="openEditModal(p)" title="Tahrirlash">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                        <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                      </svg>
                    </button>
                    <button class="btn-action-delete" @click="openDeleteModal(p)" title="O'chirish">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                      </svg>
                    </button>
                  </template>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>

      <!-- Pagination controls -->
      <div class="pagination-bar">
        <span class="pagination-info">
          Jami: <strong>{{ filteredPayments.length }}</strong> tadan <strong>{{ displayedPayments.length }}</strong> ko'rsatilmoqda
        </span>
        <div class="pagination-actions">
          <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">Oldingi</button>
          <span v-if="pageSizeOption !== 'all'" class="page-num">Sahifa {{ Math.min(currentPage, displayTotalPages) }} / {{ displayTotalPages }}</span>
          <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === displayTotalPages" @click="changePage(currentPage + 1)">Keyingi</button>
          <label class="page-size-label" for="returned-page-size">Ko'rsatish:</label>
          <div class="select-wrap">
            <select id="returned-page-size" v-model="pageSizeOption" class="page-size-select">
              <option value="50">50</option>
              <option value="100">100</option>
              <option value="200">200</option>
              <option value="all">Barchasi</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- CREATE / EDIT MODAL -->
    <Transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card">
          <div class="modal-header-banner red-banner">
            <div class="header-left-info">
              <div class="header-icon-box red-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <path d="M3 10h10a8 8 0 0 1 8 8v2M3 10l6 6m-6-6l6-6"></path>
                </svg>
              </div>
              <div>
                <h3>{{ isEditing ? "Pul Qaytarishni Tahrirlash" : "Yangi Pul Qaytarish" }}</h3>
                <p>Status: Qaytarilgan / Returned</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closeModal">✕</button>
          </div>

          <form @submit.prevent="savePayment" class="modal-body">
            <div v-if="modalError" class="alert-error">{{ modalError }}</div>

            <!-- Group-first cascade, then Searchable Student Select -->
            <div class="form-group" v-if="!isEditing">
              <label class="flabel required">Guruhni Tanlang *</label>
              <div class="searchable-select-wrap" ref="groupSelectWrapRef">
                <input
                  v-model="groupSearchQuery"
                  type="text"
                  class="finput search-input-field"
                  placeholder="Guruh nomi bo'yicha qidiring..."
                  @focus="showGroupDropdown = true"
                  @keydown="onGroupKeydown"
                />
                <button v-if="selectedGroupId" type="button" class="input-clear-btn" title="Guruhni bekor qilish" @click="clearGroupSelection">✕</button>
                <div v-if="showGroupDropdown" class="dropdown-options-list">
                  <div
                    v-for="(g, idx) in filteredGroups"
                    :key="g.id"
                    class="dropdown-option-item"
                    :class="{ selected: selectedGroupId === g.id, highlighted: groupKb.highlightedIndex.value === idx }"
                    @click="selectGroup(g)"
                  >
                    <div class="opt-name">{{ g.name }}</div>
                  </div>
                  <div v-if="filteredGroups.length === 0" class="dropdown-empty">
                    Mos guruh topilmadi
                  </div>
                </div>
              </div>
            </div>

            <div class="form-group" v-if="!isEditing">
              <label class="flabel required">O'quvchini Ism bo'yicha Qidirish *</label>
              <div class="searchable-select-wrap" ref="studentSelectWrapRef">
                <input
                  v-model="studentSearchQuery"
                  type="text"
                  class="finput search-input-field"
                  :placeholder="selectedGroupId ? 'Ism bo\'yicha qidiring...' : 'Avval guruhni tanlang'"
                  :disabled="!selectedGroupId"
                  @focus="showStudentDropdown = true"
                  @keydown="onStudentKeydown"
                />
                <button v-if="form.enrollment" type="button" class="input-clear-btn" title="O'quvchini bekor qilish" @click="clearStudentSelection">✕</button>
                <div v-if="showStudentDropdown" class="dropdown-options-list">
                  <div
                    v-for="(e, idx) in filteredEnrollments"
                    :key="e.id"
                    class="dropdown-option-item"
                    :class="{ selected: form.enrollment === e.id, highlighted: studentKb.highlightedIndex.value === idx }"
                    @click="selectEnrollment(e)"
                  >
                    <div class="opt-name">{{ e.student_name }}</div>
                    <div class="opt-sub">{{ e.category_name }} {{ e.group_name ? `(${e.group_name})` : '' }}</div>
                  </div>
                  <div v-if="filteredEnrollments.length === 0" class="dropdown-empty">
                    Mos o'quvchi topilmadi
                  </div>
                </div>
              </div>
              <div v-if="selectedStudentLabel" class="selected-chip">
                Tanlandi: <strong>{{ selectedStudentLabel }}</strong>
              </div>
            </div>

            <div class="form-group">
              <label class="flabel required">Qaytarilgan Summa *</label>
              <input
                v-model="form.amountFormatted"
                type="text"
                class="finput amount-input red-text"
                placeholder="0"
                required
                @input="onAmountInput"
              />
            </div>

            <div class="form-group">
              <label class="flabel required">Qaytarish Usuli *</label>
              <div class="select-wrap-relative">
                <select v-model="form.method" class="fselect-field">
                  <option value="cash">Naqd</option>
                  <option value="card">Karta</option>
                  <option value="qr_code">QR code</option>
                  <option value="click">Click</option>
                  <option value="transfer">O'tkazma</option>
                </select>
                <div class="select-chevron-icon">▼</div>
              </div>
            </div>

            <div class="form-group">
              <label class="flabel">Qaytarish Sababi / Izoh</label>
              <input v-model="form.notes" type="text" class="finput" placeholder="Masalan: O'quvchi darsni to'xtatganligi sababli..." />
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-cancel" @click="closeModal">Bekor qilish</button>
              <button type="submit" class="btn-save btn-red-save" :disabled="saving">
                {{ saving ? "Saqlanmoqda..." : "Qaytarishni Saqlash" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <ConfirmDeleteModal
      ref="deleteModal"
      title="To'lovni O'chirish"
      :deleting="deleting"
      :error="deleteError"
      @confirm="performDelete"
    >
      Haqiqatan ham <strong>#{{ deletingPayment?.id }}</strong> raqamli qaytarilgan to'lovni o'chirmoqchimisiz?
    </ConfirmDeleteModal>

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

const authStore = useAuthStore()
const router = useRouter()

function goStudent(id) {
  if (!id) return
  router.push(`/students/${id}`)
}

function goGroup(id) {
  if (!id) return
  router.push(`/groups/${id}`)
}

function goUser(id) {
  if (!id) return
  router.push(`/users/${id}`)
}

const payments = ref([])
const enrollments = ref([])
const categories = ref([])
const groups = ref([])
const loading = ref(true)

// ── Row-fetch-count selector ──────────────────────────────────
// Replaces classic next/prev pagination: pick how many rows to show per
// page of the filtered result set (see displayedPayments below). The
// fetch itself always pulls the full status=returned dataset — filtering
// has to see every row, not just whatever page happened to be fetched.
const pageSizeOption = ref('50')
const totalCount = ref(0) // total rows matching status=returned, per backend
const currentPage = ref(1)

// Group-first cascade: pick a group, then the student list narrows to that group.
const {
  query: groupSearchQuery,
  showDropdown: showGroupDropdown,
  selectedId: selectedGroupId,
  filtered: filteredGroups,
  select: selectGroupRaw,
  reset: resetGroupSelect,
  isOutside: isGroupSelectOutside,
  selectRef: groupSelectWrapRef,
} = useGroupSelect(groups)

function selectGroup(g) {
  selectGroupRaw(g)
  studentSearchQuery.value = ''
  selectedStudentLabel.value = ''
  form.value.enrollment = ''
}

function clearGroupSelection() {
  resetGroupSelect()
  studentSearchQuery.value = ''
  selectedStudentLabel.value = ''
  form.value.enrollment = ''
}

function clearStudentSelection() {
  studentSearchQuery.value = ''
  selectedStudentLabel.value = ''
  form.value.enrollment = ''
}

const studentSelectWrapRef = ref(null)
function handleSelectOutsideClick(e) {
  if (isGroupSelectOutside(e.target)) {
    showGroupDropdown.value = false
  }
  if (studentSelectWrapRef.value && !studentSelectWrapRef.value.contains(e.target)) {
    showStudentDropdown.value = false
  }
}

const groupKb = useSearchSelectKeyboard()
function onGroupKeydown(e) {
  groupKb.onKeydown(e, filteredGroups.value, selectGroup, () => { showGroupDropdown.value = false })
}

const filterStudentName = ref('')
const filterCategory = ref('')
const filterGroupName = ref('')
const filterMethod = ref('')
const filterCashierId = ref('')

// ── Group start/end date-range column filters ───────────────────────────
const groupStartFrom = ref('')
const groupStartTo = ref('')
const groupEndFrom = ref('')
const groupEndTo = ref('')
const paymentDateFrom = ref('')
const paymentDateTo = ref('')

// ── Sorting (group start/end, payment date, student-paid amount, refund
// amount) — only one column sorts at a time. ────────────────────────────
const groupStartSort = ref('') // '', 'asc', 'desc'
const groupEndSort = ref('')
const paymentDateSort = ref('')
const studentPaidSort = ref('')
const amountSort = ref('')

const sortRefs = { groupStart: groupStartSort, groupEnd: groupEndSort, paymentDate: paymentDateSort, studentPaid: studentPaidSort, amount: amountSort }
function setSort(column, direction) {
  const target = sortRefs[column]
  Object.values(sortRefs).forEach(r => { if (r !== target) r.value = '' })
  target.value = target.value === direction ? '' : direction
}

// Distinct admins/superusers who recorded payments in the fetched batch,
// for the "To'lovni kiritgan" filter select.
const distinctCashiers = computed(() => {
  const map = {}
  payments.value.forEach(p => {
    if (p.created_by && !map[p.created_by]) map[p.created_by] = { id: p.created_by, name: p.created_by_name || `#${p.created_by}` }
  })
  return Object.values(map).sort((a, b) => a.name.localeCompare(b.name))
})

const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const saving = ref(false)
const modalError = ref(null)

const studentSearchQuery = ref('')
const showStudentDropdown = ref(false)
const selectedStudentLabel = ref('')

const form = ref({ enrollment: '', amountFormatted: '', amount: 0, method: 'cash', notes: '' })

// All header filters (student name, category, group name, date ranges,
// method, cashier, sort) run entirely on the client against the
// already-fetched `payments` list — no per-keystroke or per-filter network
// round trip, so there's no debounce delay and no input re-render to steal
// focus/cursor position, AND they see every row matching status=returned
// (fetchPayments always pulls all of them), not just whatever page happened
// to be loaded. No filter/sort triggers a backend request.
const filteredPayments = computed(() => {
  let list = payments.value

  if (filterStudentName.value.trim()) {
    const q = filterStudentName.value.trim().toLowerCase()
    list = list.filter(p => (p.student_name || '').toLowerCase().includes(q))
  }
  if (filterCategory.value) list = list.filter(p => String(p.category) === String(filterCategory.value))
  if (filterGroupName.value.trim()) {
    const q = filterGroupName.value.trim().toLowerCase()
    list = list.filter(p => (p.group_name || '').toLowerCase().includes(q))
  }
  if (filterMethod.value) list = list.filter(p => p.method === filterMethod.value)
  if (filterCashierId.value) list = list.filter(p => String(p.created_by) === String(filterCashierId.value))

  if (groupStartFrom.value) list = list.filter(p => p.group_started_at && p.group_started_at >= groupStartFrom.value)
  if (groupStartTo.value) list = list.filter(p => p.group_started_at && p.group_started_at <= groupStartTo.value)
  if (groupEndFrom.value) list = list.filter(p => p.group_ends_at && p.group_ends_at >= groupEndFrom.value)
  if (groupEndTo.value) list = list.filter(p => p.group_ends_at && p.group_ends_at <= groupEndTo.value)
  if (paymentDateFrom.value) list = list.filter(p => p.created_at && p.created_at.slice(0, 10) >= paymentDateFrom.value)
  if (paymentDateTo.value) list = list.filter(p => p.created_at && p.created_at.slice(0, 10) <= paymentDateTo.value)

  if (groupStartSort.value) {
    list = list.slice().sort((a, b) => {
      const d = (a.group_started_at || '').localeCompare(b.group_started_at || '')
      return groupStartSort.value === 'desc' ? -d : d
    })
  } else if (groupEndSort.value) {
    list = list.slice().sort((a, b) => {
      const d = (a.group_ends_at || '').localeCompare(b.group_ends_at || '')
      return groupEndSort.value === 'desc' ? -d : d
    })
  } else if (paymentDateSort.value) {
    list = list.slice().sort((a, b) => {
      const d = (a.created_at || '').localeCompare(b.created_at || '')
      return paymentDateSort.value === 'desc' ? -d : d
    })
  } else if (studentPaidSort.value) {
    list = list.slice().sort((a, b) => {
      const d = (a.student_paid_amount ?? -Infinity) - (b.student_paid_amount ?? -Infinity)
      return studentPaidSort.value === 'desc' ? -d : d
    })
  } else if (amountSort.value) {
    list = list.slice().sort((a, b) => {
      const d = (a.amount || 0) - (b.amount || 0)
      return amountSort.value === 'desc' ? -d : d
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
  return Math.max(1, Math.ceil(filteredPayments.value.length / displayPageSize.value))
})
const displayedPayments = computed(() => {
  if (pageSizeOption.value === 'all') return filteredPayments.value
  const page = Math.min(currentPage.value, displayTotalPages.value)
  const start = (page - 1) * displayPageSize.value
  return filteredPayments.value.slice(start, start + displayPageSize.value)
})
function changePage(page) {
  if (page < 1 || page > displayTotalPages.value) return
  currentPage.value = page
}

// Metrics reflect the currently filtered dataset (not just the visible
// page) — consistent with "Jami" in the pagination footer below.
const metrics = computed(() => {
  const total = filteredPayments.value.reduce((s, p) => s + (p.amount || 0), 0)
  return { total, count: filteredPayments.value.length }
})

const filteredEnrollments = computed(() => {
  if (!selectedGroupId.value) return []
  const q = studentSearchQuery.value.toLowerCase().trim()
  return enrollments.value.filter(e => {
    if (e.group !== selectedGroupId.value) return false
    return !q || (e.student_name || '').toLowerCase().includes(q)
  })
})

async function fetchPayments() {
  loading.value = true
  try {
    // Always the full status=returned dataset — filtering/sorting/pagination
    // above all need to see every row, not just one page of them.
    const params = { status: 'returned', page: 1, page_size: 100000 }
    const res = await api.get('/payments/', { params })
    const rawList = res.data.results ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    payments.value = rawList
    totalCount.value = res.data.count ?? rawList.length
  } catch (err) { console.error(err) }
  finally { loading.value = false }
}

async function fetchEnrollments() {
  try {
    const res = await api.get('/enrollments/', { params: { page_size: 1000 } })
    enrollments.value = res.data.results || res.data
  } catch (err) { console.error(err) }
}

async function fetchCategories() {
  try {
    const res = await api.get('/categories/')
    categories.value = res.data.results || res.data
  } catch (err) { console.error(err) }
}

async function fetchGroups() {
  try {
    const res = await api.get('/groups/', { params: { page_size: 1000 } })
    groups.value = res.data.results || res.data
  } catch (err) { console.error(err) }
}

// Row-fetch-count no longer needs a backend round trip — it only resets to
// page 1 of the filtered result set; every filter/sort/page above is
// purely client-side.
watch(pageSizeOption, () => {
  currentPage.value = 1
})

function selectEnrollment(e) {
  form.value.enrollment = e.id
  selectedStudentLabel.value = `${e.student_name} (${e.category_name})`
  studentSearchQuery.value = e.student_name
  showStudentDropdown.value = false
}
const studentKb = useSearchSelectKeyboard()
function onStudentKeydown(e) {
  studentKb.onKeydown(e, filteredEnrollments.value, selectEnrollment, () => { showStudentDropdown.value = false })
}

function methodText(m) {
  switch (m) {
    case 'cash': return 'Naqd'
    case 'card': return 'Karta'
    case 'qr_code': return 'QR code'
    case 'click': return 'Click'
    case 'transfer': return "O'tkazma"
    default: return m
  }
}

function formatDateTime(dtStr) {
  if (!dtStr) return '-'
  const d = new Date(dtStr)
  return `${d.toLocaleDateString('uz-UZ')} ${d.toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' })}`
}

function onAmountInput(e) {
  const digits = e.target.value.replace(/\D/g, '')
  if (!digits) { form.value.amount = 0; form.value.amountFormatted = ''; return }
  const num = parseInt(digits, 10)
  form.value.amount = num
  form.value.amountFormatted = formatMoney(num, false)
}

function openCreateModal() {
  isEditing.value = false
  editingId.value = null
  modalError.value = null
  studentSearchQuery.value = ''
  selectedStudentLabel.value = ''
  showStudentDropdown.value = false
  resetGroupSelect()
  form.value = { enrollment: '', amountFormatted: '', amount: 0, method: 'cash', notes: '' }
  showModal.value = true
}

function openEditModal(p) {
  isEditing.value = true
  editingId.value = p.id
  modalError.value = null
  form.value = { enrollment: p.enrollment, amountFormatted: formatMoney(p.amount, false), amount: p.amount, method: p.method || 'cash', notes: p.notes || '' }
  showModal.value = true
}

function closeModal() { showModal.value = false }

async function savePayment() {
  if (!isEditing.value && !form.value.enrollment) { modalError.value = "O'quvchini tanlang."; return }
  if (!form.value.amount || form.value.amount <= 0) { modalError.value = "To'g'ri qaytarilgan summani kiriting."; return }
  saving.value = true
  modalError.value = null
  try {
    if (isEditing.value) {
      await api.patch(`/payments/${editingId.value}/`, { amount: form.value.amount, method: form.value.method, notes: form.value.notes })
    } else {
      await api.post('/payments/', { user: authStore.user?.id, enrollment: form.value.enrollment, amount: form.value.amount, status: 'returned', method: form.value.method, notes: form.value.notes })
    }
    closeModal()
    fetchPayments()
  } catch (err) { modalError.value = err.response?.data?.detail || "Saqlashda xatolik yuz berdi" }
  finally { saving.value = false }
}

const deleteModal = ref(null)
const deletingPayment = ref(null)
const deleting = ref(false)
const deleteError = ref('')

function openDeleteModal(p) {
  deletingPayment.value = p
  deleteError.value = ''
  deleteModal.value?.show()
}

async function performDelete() {
  if (!deletingPayment.value) return
  deleting.value = true
  deleteError.value = ''
  try {
    await api.delete(`/payments/${deletingPayment.value.id}/`)
    deleteModal.value?.close()
    fetchPayments()
  } catch (err) {
    deleteError.value = "O'chirishda xatolik yuz berdi"
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  fetchPayments()
  fetchEnrollments()
  fetchCategories()
  fetchGroups()
  document.addEventListener('click', handleSelectOutsideClick)
})
onUnmounted(() => {
  document.removeEventListener('click', handleSelectOutsideClick)
})
</script>

<style scoped>
.page-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-main-title { font-size: 22px; font-weight: 700; color: #111827; }
.page-sub-title { font-size: 13px; color: #6B7280; margin-top: 2px; }
.btn-primary-action { display: inline-flex; align-items: center; gap: 8px; padding: 11px 20px; background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%); color: white; border-radius: 12px; font-weight: 700; font-size: 13.5px; box-shadow: 0 4px 14px rgba(220, 38, 38, 0.25); cursor: pointer; transition: all 0.2s ease; }
.btn-primary-action:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(220, 38, 38, 0.35); }
.metrics-cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; }
.card-metric { background: white; border: 1.5px solid #E5E7EB; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); }
.card-metric-icon { font-size: 30px; }
.metric-lbl { font-size: 12.5px; color: #6B7280; font-weight: 600; }
.metric-val { font-size: 18px; font-weight: 800; color: #111827; margin-top: 4px; }
.text-red { color: #DC2626; font-weight: 800; }
.text-orange { color: #EA580C; font-weight: 800; }
.margin-top { margin-top: 24px; }
.table-section-card { background: white; border: 1px solid #E5E7EB; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }
.flabel { font-size: 12.5px; font-weight: 600; color: #4B5563; }

/* Bounded, independently-scrolling table body so the header (both the
   label row and the column-filter row) can stick to the top of this
   container as rows scroll underneath, instead of scrolling away with
   the page. */
.table-scroll-area { overflow: auto; max-height: 600px; }

.data-table { width: 100%; border-collapse: collapse; th { background: #F9FAFB; padding: 13px 16px; font-size: 12px; font-weight: 700; color: #4B5563; text-align: left; border-bottom: 1px solid #E5E7EB; white-space: nowrap; } td { padding: 14px 16px; font-size: 13.5px; color: #1F2937; border-bottom: 1px solid #F3F4F6; vertical-align: middle; } }

/* Sticky is applied to <thead> itself, not to individual <th> cells —
   that keeps both header rows (labels + filters) moving as a single
   pinned unit with no per-row offset math needed. */
.data-table thead { position: sticky; top: 0; z-index: 3; }

/* ── Column-head filters ─────────────────────────────────── */
/* Higher specificity than ".data-table th" (0,1,1) on purpose — equal
   specificity would let source order decide and flatten this row's
   padding/background back to the label row's values. */
.data-table thead tr.col-filter-row th {
  padding: 8px 10px;
  background: #FAFAFB;
  border-bottom: 1px solid #E5E7EB;
}

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
  font-family: 'Inter', sans-serif;
  transition: border-color 0.15s;
}
.col-filter-input:focus, .col-filter-select:focus { border-color: #DC2626; }
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
.col-sort-icon-btn.active { border-color: #DC2626; color: #DC2626; background: #FEF2F2; }

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
.col-date-input:focus { border-color: #DC2626; outline: none; }

.no-data { text-align: center; padding: 40px; color: #9CA3AF; font-size: 14px; }

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
.page-size-select:focus { border-color: #DC2626; outline: none; }

.student-name { font-weight: 700; color: #111827; }
.link-value { cursor: pointer; color: #2563EB !important; font-weight: 700 !important; text-decoration: underline; }
.link-value:hover { color: #1D4ED8 !important; }
.cat-pill { padding: 4px 10px; background: #FEE2E2; color: #991B1B; border-radius: 8px; font-size: 12px; font-weight: 700; }
.method-chip { padding: 4px 12px; background: #F3F4F6; color: #374151; border-radius: 20px; font-size: 12px; font-weight: 600; }
.row-actions { display: flex; gap: 8px; justify-content: flex-end; }
.btn-action-edit, .btn-action-delete { width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; border: 1px solid #E5E7EB; background: #F9FAFB; cursor: pointer; transition: all 0.15s ease; }
.btn-action-edit { color: #2563EB; &:hover { background: #EFF6FF; border-color: #BFDBFE; transform: translateY(-1px); } }
.btn-action-delete { color: #EF4444; &:hover { background: #FEE2E2; border-color: #FCA5A5; transform: translateY(-1px); } }

.state-box, .empty-state { text-align: center; padding: 40px 0; color: #6B7280; }
.spinner { width: 28px; height: 28px; border: 3px solid #E5E7EB; border-top-color: #DC2626; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px; }
@keyframes spin { to { transform: rotate(360deg); } }

.modal-overlay { position: fixed; inset: 0; z-index: 1000; background: rgba(15, 23, 42, 0.65); backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-card { background: white; border-radius: 20px; width: 100%; max-width: 500px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); }
.modal-header-banner.red-banner { padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #F3F4F6; background: linear-gradient(180deg, #FEE2E2 0%, #FFFFFF 100%); }
.header-left-info { display: flex; align-items: center; gap: 12px; h3 { font-size: 17px; font-weight: 700; color: #991B1B; } p { font-size: 12px; color: #6B7280; margin-top: 2px; } }
.header-icon-box.red-box { width: 42px; height: 42px; border-radius: 12px; background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%); color: white; display: flex; align-items: center; justify-content: center; }
.btn-modal-close { background: none; border: none; font-size: 18px; color: #9CA3AF; cursor: pointer; }
.modal-body { padding: 24px; }

/* UNIFORM INPUT & SELECT STYLING */
.form-group { margin-bottom: 18px; width: 100%; }
.flabel { display: block; font-size: 12.5px; font-weight: 600; color: #374151; margin-bottom: 6px; }
.finput, .fselect-field {
  width: 100%; box-sizing: border-box; padding: 11px 14px;
  border: 1.5px solid #E5E7EB; border-radius: 10px; font-size: 14px;
  background-color: #FAFAFA; color: #111827; outline: none;
  transition: all 0.2s ease; appearance: none; -webkit-appearance: none;
  &:focus { border-color: #DC2626; background-color: #FFFFFF; box-shadow: 0 0 0 3.5px rgba(220, 38, 38, 0.12); }
}

.select-wrap-relative { position: relative; width: 100%; }
.select-chevron-icon { position: absolute; right: 14px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #9CA3AF; font-size: 10px; }

.searchable-select-wrap { position: relative; width: 100%; }
.input-clear-btn {
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  width: 22px; height: 22px; border-radius: 50%; border: none;
  background: #E5E7EB; color: #4B5563; font-size: 11px; line-height: 1;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.input-clear-btn:hover { background: #D1D5DB; color: #111827; }
.searchable-select-wrap .finput { padding-right: 34px; }
.dropdown-options-list { position: absolute; top: 100%; left: 0; right: 0; max-height: 200px; overflow-y: auto; background: white; border: 1.5px solid #DC2626; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); z-index: 50; margin-top: 4px; }
.dropdown-option-item { padding: 10px 14px; cursor: pointer; border-bottom: 1px solid #F3F4F6; &:hover { background: #FEE2E2; } &.selected { background: #FCA5A5; font-weight: 700; } &.highlighted { background: #FEE2E2; } }
.opt-name { font-size: 13.5px; font-weight: 600; color: #111827; }
.opt-sub { font-size: 11.5px; color: #6B7280; margin-top: 1px; }
.dropdown-empty { padding: 12px; text-align: center; color: #9CA3AF; font-size: 13px; }
.selected-chip { font-size: 12.5px; color: #DC2626; margin-top: 6px; }

.amount-input.red-text { font-size: 16.5px; font-weight: 800; color: #DC2626; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.btn-cancel { padding: 10px 18px; border: 1px solid #D1D5DB; background: white; border-radius: 10px; font-weight: 600; font-size: 13px; color: #374151; cursor: pointer; }
.btn-red-save { padding: 10px 22px; background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%); color: white; border-radius: 10px; font-weight: 700; font-size: 13.5px; cursor: pointer; }
.alert-error { background: #FEE2E2; color: #991B1B; padding: 10px 14px; border-radius: 10px; font-size: 13px; margin-bottom: 16px; }
</style>
