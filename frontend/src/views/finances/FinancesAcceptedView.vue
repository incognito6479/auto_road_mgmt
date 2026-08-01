<template>
  <AppLayout>

    <!-- Page Top Header -->
    <div class="page-top">
      <div>
        <h2 class="page-main-title">Tushumlar (Qabul Qilingan To'lovlar)</h2>
        <p class="page-sub-title">Barcha qabul qilingan to'lovlar, bugungi va oylik tushumlar hisoboti</p>
      </div>

      <button class="btn-primary-action" @click="openCreateModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="18" height="18">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        <span>Yangi tushum qo'shish</span>
      </button>
    </div>

    <!-- 1. BUGUNGI TUSHUMLAR CARDS -->
    <div class="finance-section">
      <div class="section-header-wrap">
        <div class="section-header-title">
          <div class="icon-pulse green-pulse">
            <svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="2" width="22" height="22">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
          </div>
          <h3>Bugungi Tushumlar ({{ todayDateStr }})</h3>
        </div>
        <span class="section-total-badge green-badge font-bold">{{ formatMoney(todayMetrics.total) }}</span>
      </div>

      <div class="metrics-cards-grid big-cards">
        <div class="card-metric card-red card-hero">
          <div class="card-metric-icon">💰</div>
          <div class="metric-info">
            <span class="metric-lbl">Jami Bugungi Tushum</span>
            <h4 class="metric-val text-red-strong">{{ formatMoney(todayMetrics.total) }}</h4>
          </div>
        </div>

        <div class="card-metric card-green">
          <div class="card-metric-icon">💵</div>
          <div class="metric-info">
            <span class="metric-lbl">Bugungi Naqd</span>
            <h4 class="metric-val">{{ formatMoney(todayMetrics.cash) }}</h4>
          </div>
        </div>

        <div class="card-metric card-blue">
          <div class="card-metric-icon">💳</div>
          <div class="metric-info">
            <span class="metric-lbl">Bugungi Karta</span>
            <h4 class="metric-val">{{ formatMoney(todayMetrics.card) }}</h4>
          </div>
        </div>

        <div class="card-metric card-purple">
          <div class="card-metric-icon">🏦</div>
          <div class="metric-info">
            <span class="metric-lbl">Bugungi O'tkazma</span>
            <h4 class="metric-val">{{ formatMoney(todayMetrics.transfer) }}</h4>
          </div>
        </div>

        <div class="card-metric card-orange">
          <div class="card-metric-icon">📱</div>
          <div class="metric-info">
            <span class="metric-lbl">Bugungi QR Code</span>
            <h4 class="metric-val">{{ formatMoney(todayMetrics.qr_code) }}</h4>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. OYLIK TUSHUMLAR CARDS -->
    <div class="finance-section">
      <div class="section-header-wrap">
        <div class="section-header-title">
          <div class="icon-pulse blue-pulse">
            <svg viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" width="22" height="22">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
          </div>
          <h3 v-if="!monthlyHasActiveFilters">Oylik Tushumlar ({{ monthNameStr }})</h3>
          <h3 v-else>Filtr Natijasi — Oylar Bo'yicha</h3>
          <div class="monthly-date-filters">
            <input v-model="monthlyDateFrom" type="date" class="finput-date" />
            <span class="date-range-sep">—</span>
            <input v-model="monthlyDateTo" type="date" class="finput-date" />
            <button v-if="monthlyHasActiveFilters" type="button" class="btn-clear-monthly-filter" title="Filtrni tozalash" @click="clearMonthlyDateFilter">✕</button>
          </div>
        </div>
        <span class="section-total-badge blue-badge font-bold">
          {{ formatMoney(monthlyHasActiveFilters ? filteredGrandTotal : monthMetrics.total) }}
        </span>
      </div>

      <!-- No filters applied: show the current calendar month only -->
      <div v-if="!monthlyHasActiveFilters" class="metrics-cards-grid big-cards">
        <div class="card-metric card-red card-hero">
          <div class="card-metric-icon">📊</div>
          <div class="metric-info">
            <span class="metric-lbl">Jami Oylik Tushum</span>
            <h4 class="metric-val text-red-strong">{{ formatMoney(monthMetrics.total) }}</h4>
          </div>
        </div>

        <div class="card-metric card-green">
          <div class="card-metric-icon">💵</div>
          <div class="metric-info">
            <span class="metric-lbl">Oylik Naqd</span>
            <h4 class="metric-val">{{ formatMoney(monthMetrics.cash) }}</h4>
          </div>
        </div>

        <div class="card-metric card-blue">
          <div class="card-metric-icon">💳</div>
          <div class="metric-info">
            <span class="metric-lbl">Oylik Karta</span>
            <h4 class="metric-val">{{ formatMoney(monthMetrics.card) }}</h4>
          </div>
        </div>

        <div class="card-metric card-purple">
          <div class="card-metric-icon">🏦</div>
          <div class="metric-info">
            <span class="metric-lbl">Oylik O'tkazma</span>
            <h4 class="metric-val">{{ formatMoney(monthMetrics.transfer) }}</h4>
          </div>
        </div>

        <div class="card-metric card-orange">
          <div class="card-metric-icon">📱</div>
          <div class="metric-info">
            <span class="metric-lbl">Oylik QR Code</span>
            <h4 class="metric-val">{{ formatMoney(monthMetrics.qr_code) }}</h4>
          </div>
        </div>
      </div>

      <!-- Filters applied: break the filtered result set down by month -->
      <div v-else class="monthly-breakdown-list">
        <div v-if="monthlyBreakdown.length === 0" class="empty-state">
          <p>Filtrga mos tushumlar topilmadi</p>
        </div>
        <div v-for="m in monthlyBreakdown" :key="m.key" class="month-card-group">
          <div class="metrics-cards-grid big-cards">
            <div class="card-metric card-red card-hero">
              <div class="card-metric-icon">📊</div>
              <div class="metric-info">
                <span class="metric-lbl">Jami</span>
                <h4 class="metric-val text-red-strong">{{ formatMoney(m.total) }}</h4>
              </div>
            </div>
            <div class="card-metric card-green">
              <div class="card-metric-icon">💵</div>
              <div class="metric-info">
                <span class="metric-lbl">Naqd</span>
                <h4 class="metric-val">{{ formatMoney(m.cash) }}</h4>
              </div>
            </div>
            <div class="card-metric card-blue">
              <div class="card-metric-icon">💳</div>
              <div class="metric-info">
                <span class="metric-lbl">Karta</span>
                <h4 class="metric-val">{{ formatMoney(m.card) }}</h4>
              </div>
            </div>
            <div class="card-metric card-purple">
              <div class="card-metric-icon">🏦</div>
              <div class="metric-info">
                <span class="metric-lbl">O'tkazma</span>
                <h4 class="metric-val">{{ formatMoney(m.transfer) }}</h4>
              </div>
            </div>
            <div class="card-metric card-orange">
              <div class="card-metric-icon">📱</div>
              <div class="metric-info">
                <span class="metric-lbl">QR Code</span>
                <h4 class="metric-val">{{ formatMoney(m.qr_code) }}</h4>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. PAYMENTS TABLE -->
    <div class="table-section-card">
      <div class="table-container">
        <div v-if="loading" class="state-box">
          <div class="spinner"></div>
          <span>Tushumlar yuklanmoqda...</span>
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
              <th>Tushum Summasi</th>
              <th>To'lov Usuli</th>
              <th>Sana &amp; Vaqt</th>
              <th>To'lov qabul qiluvchi</th>
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
                </div>
              </th>
              <th></th>
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
                </div>
              </th>
              <th></th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="displayedPayments.length === 0">
              <td colspan="10" class="no-data">Tushumlar topilmadi</td>
            </tr>
            <tr v-for="p in displayedPayments" :key="p.id" class="table-row">
              <td class="td-name">
                <div v-if="p.student" class="student-name link-value" @click="goStudent(p.student)">{{ p.student_name || 'Noma\'lum' }}</div>
                <div v-else class="student-name">{{ p.student_name || 'Noma\'lum' }}</div>
                <div v-if="p.student_jshshr" class="student-jshshr">JSHSHR: {{ p.student_jshshr }}</div>
              </td>
              <td><span class="cat-pill">{{ p.category_name || '-' }}</span></td>
              <td>{{ p.group_name || '-' }}</td>
              <td>{{ p.group_started_at ? formatDate(p.group_started_at) : '-' }}</td>
              <td>{{ p.group_ends_at ? formatDate(p.group_ends_at) : '-' }}</td>
              <td class="td-amount">
                <span class="amount-val text-green">{{ formatMoney(p.amount) }}</span>
              </td>
              <td><span class="method-chip">{{ methodText(p.method) }}</span></td>
              <td class="td-date">{{ formatDateTime(p.created_at) }}</td>
              <td>
                <span v-if="p.user" class="link-value" @click="goUser(p.user)">{{ p.cashier_name || '-' }}</span>
                <span v-else>{{ p.cashier_name || '-' }}</span>
              </td>
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
          Jami: <strong>{{ totalCount }}</strong> tadan <strong>{{ totalCount > 0 ? (currentPage - 1) * pageSize + 1 : 0 }} - {{ Math.min(currentPage * pageSize, totalCount) }}</strong> ko'rsatilmoqda
        </span>
        <div class="pagination-actions">
          <button class="btn-page" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">Oldingi</button>
          <span class="page-num">Sahifa {{ currentPage }} / {{ totalPages }}</span>
          <button class="btn-page" :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">Keyingi</button>
        </div>
      </div>
    </div>

    <!-- CREATE / EDIT MODAL -->
    <Transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-card">
          <div class="modal-header-banner green-banner">
            <div class="header-left-info">
              <div class="header-icon-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <rect x="2" y="5" width="20" height="14" rx="2"></rect>
                  <line x1="2" y1="10" x2="22" y2="10"></line>
                </svg>
              </div>
              <div>
                <h3>{{ isEditing ? "Tushumni Tahrirlash" : "Yangi Tushum Qo'shish" }}</h3>
                <p>O'quvchi to'lovini tizimga kiriting</p>
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

            <!-- Amount Input -->
            <div class="form-group">
              <label class="flabel required">Tushum Summasi *</label>
              <input
                v-model="form.amountFormatted"
                type="text"
                class="finput amount-input"
                placeholder="0"
                required
                @input="onAmountInput"
              />
            </div>

            <!-- Method Select -->
            <div class="form-group">
              <label class="flabel required">To'lov Usuli *</label>
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

            <!-- Notes -->
            <div class="form-group">
              <label class="flabel">Izoh / Eslatma</label>
              <input v-model="form.notes" type="text" class="finput" placeholder="Ixtiyoriy izoh..." />
            </div>

            <div class="modal-footer">
              <button type="button" class="btn-cancel" @click="closeModal">Bekor qilish</button>
              <button type="submit" class="btn-save" :disabled="saving">
                {{ saving ? "Saqlanmoqda..." : "Saqlash" }}
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
      Haqiqatan ham <strong>#{{ deletingPayment?.id }}</strong> raqamli tushumni o'chirmoqchimisiz?
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
import { useBranchStore } from '@/stores/branch'
import { formatMoney, formatDate } from '@/utils/formatters'
import { useSearchSelectKeyboard } from '@/composables/useSearchSelectKeyboard'
import { useGroupSelect } from '@/composables/useGroupSelect'

const authStore = useAuthStore()
const router = useRouter()

function goStudent(id) {
  if (!id) return
  router.push(`/students/${id}`)
}
function goUser(id) {
  if (!id) return
  router.push(`/users/${id}`)
}
const branchStore = useBranchStore()

const payments = ref([])
const enrollments = ref([])
const categories = ref([])
const groups = ref([])
const loading = ref(true)

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
const filterMethod = ref('')
const filterGroupName = ref('')

// ── Group start/end and payment-date sorting ────────────────────────────
const groupStartSort = ref('') // '', 'asc', 'desc'
const groupEndSort = ref('')
const paymentDateSort = ref('')

// Clicking the already-active direction clears the sort; clicking the other
// direction (or another column) switches to it. Only one column sorts at a time.
function setSort(column, direction) {
  if (column === 'groupStart') {
    groupEndSort.value = ''
    paymentDateSort.value = ''
    groupStartSort.value = groupStartSort.value === direction ? '' : direction
  } else if (column === 'groupEnd') {
    groupStartSort.value = ''
    paymentDateSort.value = ''
    groupEndSort.value = groupEndSort.value === direction ? '' : direction
  } else if (column === 'paymentDate') {
    groupStartSort.value = ''
    groupEndSort.value = ''
    paymentDateSort.value = paymentDateSort.value === direction ? '' : direction
  }
}

const orderingParam = computed(() => {
  if (groupStartSort.value) return (groupStartSort.value === 'desc' ? '-' : '') + 'group_started_at'
  if (groupEndSort.value) return (groupEndSort.value === 'desc' ? '-' : '') + 'group_ends_at'
  if (paymentDateSort.value) return (paymentDateSort.value === 'desc' ? '-' : '') + 'created_at'
  return ''
})

// ── Pagination state ─────────────────────────────────────────────────────
const currentPage = ref(1)
const totalCount = ref(0)
const pageSize = 50
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize) || 1)

const displayedPayments = computed(() => payments.value.filter(p => branchStore.isBranchMatch(p)))

const showModal = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const saving = ref(false)
const modalError = ref(null)

const studentSearchQuery = ref('')
const showStudentDropdown = ref(false)
const selectedStudentLabel = ref('')

const form = ref({ enrollment: '', amountFormatted: '', amount: 0, method: 'cash', notes: '' })
const allAcceptedPayments = ref([])

const todayDateStr = computed(() => new Date().toLocaleDateString('uz-UZ'))
const monthNameStr = computed(() => new Date().toLocaleDateString('uz-UZ', { month: 'long', year: 'numeric' }))

const todayMetrics = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  const todayPayments = allAcceptedPayments.value.filter(p => p.created_at && p.created_at.startsWith(today) && branchStore.isBranchMatch(p))
  const cash = todayPayments.filter(p => p.method === 'cash').reduce((s, p) => s + (p.amount || 0), 0)
  const card = todayPayments.filter(p => p.method === 'card').reduce((s, p) => s + (p.amount || 0), 0)
  const transfer = todayPayments.filter(p => p.method === 'transfer').reduce((s, p) => s + (p.amount || 0), 0)
  const qr_code = todayPayments.filter(p => p.method === 'qr_code').reduce((s, p) => s + (p.amount || 0), 0)
  return { cash, card, transfer, qr_code, total: cash + card + transfer + qr_code }
})

const monthMetrics = computed(() => {
  const now = new Date()
  const yearMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  const monthPayments = allAcceptedPayments.value.filter(p => p.created_at && p.created_at.startsWith(yearMonth) && branchStore.isBranchMatch(p))
  const cash = monthPayments.filter(p => p.method === 'cash').reduce((s, p) => s + (p.amount || 0), 0)
  const card = monthPayments.filter(p => p.method === 'card').reduce((s, p) => s + (p.amount || 0), 0)
  const transfer = monthPayments.filter(p => p.method === 'transfer').reduce((s, p) => s + (p.amount || 0), 0)
  const qr_code = monthPayments.filter(p => p.method === 'qr_code').reduce((s, p) => s + (p.amount || 0), 0)
  return { cash, card, transfer, qr_code, total: cash + card + transfer + qr_code }
})

// Date range filter for the monthly cards section, independent of the
// payments table's own toolbar filters below.
const monthlyDateFrom = ref('')
const monthlyDateTo = ref('')

function clearMonthlyDateFilter() {
  monthlyDateFrom.value = ''
  monthlyDateTo.value = ''
}

const monthlyHasActiveFilters = computed(() => !!(monthlyDateFrom.value || monthlyDateTo.value))

// Payments within the monthly cards' own date range, independent of the
// table's toolbar filters.
const monthlyFilteredPayments = computed(() => {
  return allAcceptedPayments.value.filter(p => {
    if (!branchStore.isBranchMatch(p)) return false
    if (!p.created_at) return false
    const dateStr = p.created_at.slice(0, 10)
    if (monthlyDateFrom.value && dateStr < monthlyDateFrom.value) return false
    if (monthlyDateTo.value && dateStr > monthlyDateTo.value) return false
    return true
  })
})

// Breaks the monthly-filtered payment list down into one bucket per
// calendar month, newest first.
const monthlyBreakdown = computed(() => {
  const buckets = {}
  for (const p of monthlyFilteredPayments.value) {
    if (!p.created_at) continue
    const key = p.created_at.slice(0, 7) // "YYYY-MM"
    if (!buckets[key]) {
      buckets[key] = { key, cash: 0, card: 0, transfer: 0, qr_code: 0, total: 0 }
    }
    const bucket = buckets[key]
    const amt = p.amount || 0
    if (p.method === 'cash') bucket.cash += amt
    else if (p.method === 'card') bucket.card += amt
    else if (p.method === 'transfer') bucket.transfer += amt
    else if (p.method === 'qr_code') bucket.qr_code += amt
    bucket.total += amt
  }
  return Object.values(buckets)
    .sort((a, b) => b.key.localeCompare(a.key))
    .map(bucket => ({
      ...bucket,
      label: new Date(`${bucket.key}-01T00:00:00`).toLocaleDateString('uz-UZ', { month: 'long', year: 'numeric' }),
    }))
})

const filteredGrandTotal = computed(() => monthlyBreakdown.value.reduce((s, m) => s + m.total, 0))

const filteredEnrollments = computed(() => {
  if (!selectedGroupId.value) return []
  const q = studentSearchQuery.value.toLowerCase().trim()
  return enrollments.value.filter(e => {
    if (e.group !== selectedGroupId.value) return false
    return !q || (e.student_name || '').toLowerCase().includes(q)
  })
})

async function fetchCategories() {
  try {
    const res = await api.get('/categories/')
    categories.value = res.data.results || res.data
  } catch (err) { console.error(err) }
}

async function fetchAllAcceptedMetrics() {
  try {
    const res = await api.get('/payments/', { params: { status: 'accepted', page_size: 1000 } })
    allAcceptedPayments.value = res.data.results || res.data
  } catch (err) { console.error(err) }
}

async function fetchPayments() {
  loading.value = true
  try {
    const params = { status: 'accepted', page: currentPage.value, page_size: pageSize }
    if (filterMethod.value) params.method = filterMethod.value
    if (filterStudentName.value) params.student_name = filterStudentName.value.trim()
    if (filterCategory.value) params.category = filterCategory.value
    if (filterGroupName.value) params.group_name = filterGroupName.value.trim()
    if (orderingParam.value) params.ordering = orderingParam.value

    const res = await api.get('/payments/', { params })
    const rawList = res.data.results ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    payments.value = rawList
    totalCount.value = res.data.count ?? rawList.length
  } catch (err) { console.error(err) }
  finally { loading.value = false }
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchPayments()
}

async function fetchEnrollments() {
  try {
    const res = await api.get('/enrollments/', { params: { page_size: 1000 } })
    enrollments.value = res.data.results || res.data
  } catch (err) { console.error(err) }
}

async function fetchGroups() {
  try {
    const res = await api.get('/groups/', { params: { page_size: 1000 } })
    groups.value = res.data.results || res.data
  } catch (err) { console.error(err) }
}

// Text-input filters wait for the user to pause typing (1.2s) before
// re-fetching, so each keystroke doesn't trigger its own request.
let searchDebounceTimer = null
watch([filterStudentName, filterGroupName], () => {
  clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    currentPage.value = 1
    fetchPayments()
  }, 1200)
})

// Category/method selects and sort toggles apply immediately.
watch([filterCategory, filterMethod, groupStartSort, groupEndSort, paymentDateSort], () => {
  clearTimeout(searchDebounceTimer)
  currentPage.value = 1
  fetchPayments()
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
  if (!form.value.amount || form.value.amount <= 0) { modalError.value = "To'g'ri tushum summasini kiriting."; return }
  saving.value = true
  modalError.value = null
  try {
    if (isEditing.value) {
      await api.patch(`/payments/${editingId.value}/`, { amount: form.value.amount, method: form.value.method, notes: form.value.notes })
    } else {
      await api.post('/payments/', { user: authStore.user?.id, enrollment: form.value.enrollment, amount: form.value.amount, status: 'accepted', method: form.value.method, notes: form.value.notes })
    }
    closeModal()
    fetchPayments()
    fetchAllAcceptedMetrics()
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
    fetchAllAcceptedMetrics()
  } catch (err) {
    deleteError.value = "O'chirishda xatolik yuz berdi"
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  fetchPayments()
  fetchAllAcceptedMetrics()
  fetchEnrollments()
  fetchCategories()
  fetchGroups()
  document.addEventListener('click', handleSelectOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleSelectOutsideClick)
  clearTimeout(searchDebounceTimer)
})
</script>

<style scoped>
.page-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-main-title { font-size: 22px; font-weight: 700; color: #111827; }
.page-sub-title { font-size: 13px; color: #6B7280; margin-top: 2px; }

.btn-primary-action {
  display: inline-flex; align-items: center; gap: 8px; padding: 11px 20px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%); color: white;
  border-radius: 12px; font-weight: 700; font-size: 13.5px;
  box-shadow: 0 4px 14px rgba(45, 106, 79, 0.25); cursor: pointer; transition: all 0.2s ease;
  &:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(45, 106, 79, 0.35); }
}

.finance-section { margin-bottom: 26px; }
.section-header-wrap { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.section-header-title { display: flex; align-items: center; gap: 10px; h3 { font-size: 17px; font-weight: 700; color: #111827; display: flex; align-items: center; gap: 10px; flex-wrap: wrap; } }
.monthly-date-filters { display: flex; align-items: center; gap: 6px; margin-left: 6px; }
.monthly-date-filters .finput-date { padding: 6px 10px; font-size: 12.5px; }
.date-range-sep { color: #9CA3AF; font-size: 13px; }
.btn-clear-monthly-filter { width: 24px; height: 24px; border-radius: 50%; border: none; background: #E5E7EB; color: #4B5563; font-size: 11px; line-height: 1; cursor: pointer; display: flex; align-items: center; justify-content: center; &:hover { background: #D1D5DB; color: #111827; } }
.icon-pulse { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; &.green-pulse { background: #E8F5E9; } &.blue-pulse { background: #EFF6FF; } }
.section-total-badge { font-size: 14px; padding: 6px 14px; border-radius: 20px; &.green-badge { color: #2D6A4F; background: #E8F5E9; } &.blue-badge { color: #2563EB; background: #EFF6FF; } }

.metrics-cards-grid.big-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; min-height: 140px; }

/* Fixed footprint regardless of how many months the active date range spans —
   without this, the section above the date-range inputs grows/shrinks as the
   filter changes and visibly shoves the inputs the user is interacting with. */
/* Bounded, not fixed: a single filtered month should be roughly the same
   height as the unfiltered card row above (no jump when the date-range
   inputs are first touched), while many months still cap out and scroll
   instead of growing without limit. */
.monthly-breakdown-list { display: flex; flex-direction: column; gap: 20px; min-height: 140px; max-height: 380px; overflow-y: auto; padding-right: 4px; }
.monthly-breakdown-list .empty-state { height: 100%; display: flex; align-items: center; justify-content: center; }
.month-card-group { padding: 4px 0; }
.card-metric { background: white; border: 1.5px solid #E5E7EB; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03); transition: all 0.2s ease; &:hover { transform: translateY(-2px); border-color: #CBD5E1; box-shadow: 0 6px 16px rgba(0,0,0,0.06); } }
.card-hero { border-width: 2px; background: linear-gradient(180deg, #FFFFFF 0%, #F9FAFB 100%); grid-column: span 2; }
.card-red { border-color: #FCA5A5; background: linear-gradient(180deg, #FEF2F2 0%, #FEE2E2 100%); }
.card-metric-icon { font-size: 30px; }
.metric-lbl { font-size: 12.5px; color: #6B7280; font-weight: 600; }
.metric-val { font-size: 18px; font-weight: 800; color: #111827; margin-top: 4px; }
.text-emerald { color: #2D6A4F; }
.text-blue { color: #2563EB; }
.text-green { color: #166534; font-weight: 700; }
.text-red-strong { color: #B91C1C; }

.table-section-card { background: white; border: 1px solid #E5E7EB; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03); }
.flabel { font-size: 12.5px; font-weight: 600; color: #374151; }

.finput-date { padding: 8px 12px; border: 1.5px solid #E5E7EB; border-radius: 10px; font-size: 13px; background: #FAFAFA; outline: none; }

/* UNIFORM FORM FIELD STYLING */
.form-group { margin-bottom: 18px; width: 100%; }
.finput, .fselect-field {
  width: 100%; box-sizing: border-box; padding: 11px 14px;
  border: 1.5px solid #E5E7EB; border-radius: 10px; font-size: 14px;
  background-color: #FAFAFA; color: #111827; outline: none;
  transition: all 0.2s ease; appearance: none; -webkit-appearance: none;
  &:focus { border-color: #2D6A4F; background-color: #FFFFFF; box-shadow: 0 0 0 3.5px rgba(45, 106, 79, 0.12); }
}

.select-wrap-relative { position: relative; width: 100%; }
.select-chevron-icon { position: absolute; right: 14px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #9CA3AF; font-size: 10px; }

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
.col-filter-input:focus, .col-filter-select:focus { border-color: #2D6A4F; }
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

/* ── Pagination ───────────────────────────────────────────── */
.pagination-bar { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #F9FAFB; border-top: 1px solid #E5E7EB; }
.pagination-info { font-size: 13.5px; color: #6B7280; font-weight: 500; }
.pagination-actions { display: flex; align-items: center; gap: 8px; }
.page-num { display: inline-flex; align-items: center; padding: 0 12px; font-weight: 600; color: #374151; font-size: 14px; }
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
.student-name { font-weight: 700; color: #111827; }
.link-value { cursor: pointer; }
.link-value:hover { text-decoration: underline; }
.student-jshshr { font-size: 11.5px; color: #6B7280; margin-top: 2px; }
.cat-pill { padding: 4px 10px; background: #E8F5E9; color: #2D6A4F; border-radius: 8px; font-size: 12px; font-weight: 700; }
.method-chip { padding: 4px 12px; background: #F3F4F6; color: #374151; border-radius: 20px; font-size: 12px; font-weight: 600; }

.row-actions { display: flex; gap: 8px; justify-content: flex-end; }
.btn-action-edit, .btn-action-delete { width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; border: 1px solid #E5E7EB; background: #F9FAFB; cursor: pointer; transition: all 0.15s ease; }
.btn-action-edit { color: #2563EB; &:hover { background: #EFF6FF; border-color: #BFDBFE; transform: translateY(-1px); } }
.btn-action-delete { color: #EF4444; &:hover { background: #FEE2E2; border-color: #FCA5A5; transform: translateY(-1px); } }

.state-box, .empty-state { text-align: center; padding: 40px 0; color: #6B7280; }
.no-data { text-align: center; padding: 40px; color: #9CA3AF; font-size: 14px; }
.spinner { width: 28px; height: 28px; border: 3px solid #E5E7EB; border-top-color: #2D6A4F; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 10px; }
@keyframes spin { to { transform: rotate(360deg); } }

.modal-overlay { position: fixed; inset: 0; z-index: 1000; background: rgba(15, 23, 42, 0.65); backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-card { background: white; border-radius: 20px; width: 100%; max-width: 500px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); }
.modal-header-banner { padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #F3F4F6; &.green-banner { background: linear-gradient(180deg, #F0FDF4 0%, #FFFFFF 100%); } }
.header-left-info { display: flex; align-items: center; gap: 12px; h3 { font-size: 17px; font-weight: 700; color: #111827; } p { font-size: 12px; color: #6B7280; margin-top: 2px; } }
.header-icon-box { width: 42px; height: 42px; border-radius: 12px; background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%); color: white; display: flex; align-items: center; justify-content: center; }
.btn-modal-close { background: none; border: none; font-size: 18px; color: #9CA3AF; cursor: pointer; }
.modal-body { padding: 24px; }

.searchable-select-wrap { position: relative; width: 100%; }
.input-clear-btn {
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  width: 22px; height: 22px; border-radius: 50%; border: none;
  background: #E5E7EB; color: #4B5563; font-size: 11px; line-height: 1;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.input-clear-btn:hover { background: #D1D5DB; color: #111827; }
.searchable-select-wrap .finput { padding-right: 34px; }
.dropdown-options-list { position: absolute; top: 100%; left: 0; right: 0; max-height: 200px; overflow-y: auto; background: white; border: 1.5px solid #2D6A4F; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); z-index: 50; margin-top: 4px; }
.dropdown-option-item { padding: 10px 14px; cursor: pointer; border-bottom: 1px solid #F3F4F6; &:hover { background: #F0FDF4; } &.selected { background: #E8F5E9; font-weight: 700; } &.highlighted { background: #F0FDF4; } }
.opt-name { font-size: 13.5px; font-weight: 600; color: #111827; }
.opt-sub { font-size: 11.5px; color: #6B7280; margin-top: 1px; }
.dropdown-empty { padding: 12px; text-align: center; color: #9CA3AF; font-size: 13px; }
.selected-chip { font-size: 12.5px; color: #2D6A4F; margin-top: 6px; }

.amount-input { font-size: 16.5px; font-weight: 800; color: #2D6A4F; }
.modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }
.btn-cancel { padding: 10px 18px; border: 1px solid #D1D5DB; background: white; border-radius: 10px; font-weight: 600; font-size: 13px; color: #374151; cursor: pointer; }
.btn-save { padding: 10px 22px; background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%); color: white; border-radius: 10px; font-weight: 700; font-size: 13.5px; cursor: pointer; }
.alert-error { background: #FEE2E2; color: #991B1B; padding: 10px 14px; border-radius: 10px; font-size: 13px; margin-bottom: 16px; }
</style>
