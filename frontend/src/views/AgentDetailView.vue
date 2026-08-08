<template>
  <AppLayout>

    <!-- Top Navigation & Action Bar -->
    <div class="page-top">
      <div class="top-left">
        <button class="btn-back" @click="goBack" title="Orqaga">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          <span>Agentlar ro'yxatiga qaytish</span>
        </button>
        <h2 class="page-main-title">{{ agent?.full_name || 'Agent Ma\'lumotlari' }}</h2>
      </div>

      <button v-if="authStore.isStaff && agent" class="btn-edit-profile" @click="openEditAgentModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" style="margin-right: 6px;">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
          <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
        </svg>
        <span>Agentni Tahrirlash</span>
      </button>
    </div>

    <!-- Loading / Error States -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">Agent ma'lumotlari yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchAll">Qayta urinish</button>
    </div>

    <div v-else-if="agent" class="detail-container">

      <!-- Profile Overview Card -->
      <div class="profile-card">
        <div class="profile-header">
          <div class="avatar-large">
            {{ agentInitials }}
          </div>
          <div class="profile-identity">
            <h3 class="profile-name">{{ agent.full_name }}</h3>
            <span class="agent-chip">Agent / Hamkor</span>
          </div>
        </div>

        <div class="profile-grid">
          <div class="info-item">
            <span class="info-label">Telefon Raqami</span>
            <span class="info-value font-semibold">{{ formatPhone(agent.phone) }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">Qo'shimcha Telefon</span>
            <span class="info-value">{{ formatPhone(agent.phone2) || '-' }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">Ro'yxatdan o'tgan sana</span>
            <span class="info-value">{{ formatDate(agent.created_at) }}</span>
          </div>
        </div>

        <div v-if="agent.notes" class="notes-block">
          <span class="info-label">Izoh / Eslatma:</span>
          <p class="notes-text">{{ agent.notes }}</p>
        </div>
      </div>

      <!-- Bonus Metrics Cards Grid -->
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-icon green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
            </svg>
          </div>
          <div>
            <span class="metric-label">Jalb Etilgan O'quvchilar</span>
            <h4 class="metric-value">{{ filteredEnrollmentsWithBonus.length }} ta qabul</h4>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon gold">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
            </svg>
          </div>
          <div>
            <span class="metric-label">Bonus Berilgan Qabullar</span>
            <h4 class="metric-value bonus-val">{{ bonusPaidCount }} ta qabul</h4>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon orange">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
          </div>
          <div>
            <span class="metric-label">Bonus Kutilmoqda</span>
            <h4 class="metric-value warning-text">{{ bonusPendingCount }} ta qabul</h4>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon purple">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
            </svg>
          </div>
          <div>
            <span class="metric-label">Jami Berilgan Bonuslar Summasi</span>
            <h4 class="metric-value font-bold text-amber">{{ formatMoney(totalBonusSum) }}</h4>
          </div>
        </div>
      </div>

      <!-- Section heading + count, above the filters -->
      <div class="section-title-wrap">
        <h3 class="section-title">👥 Jalb Qilingan O'quvchilar va Bonus To'lovlari</h3>
        <span class="section-badge">{{ filteredEnrollmentsWithBonus.length }} ta qabul</span>
      </div>

      <!-- ATTRACTED STUDENTS & BONUS PAYMENTS TABLE -->
      <div class="section-container">

        <div v-if="loadingEnrollments" class="state-container">
          <div class="spinner"></div>
          <p class="state-text">O'quvchilar ro'yxati va bonus to'lovlari yuklanmoqda...</p>
        </div>

        <div v-else-if="enrollmentsWithBonus.length === 0" class="empty-state">
          <div class="empty-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="1.5" width="36" height="36">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
            </svg>
          </div>
          <p class="empty-title">O'quvchilar topilmadi</p>
          <p class="empty-sub">Ushbu agent orqali biriktirilgan o'quvchilar mavjud emas.</p>
        </div>

        <div v-else class="table-card">
          <div class="table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>O'quvchi F.I.SH.</th>
                  <th>Avtomaktab</th>
                  <th>Kategoriya</th>
                  <th>Guruh</th>
                  <th>Guruh boshlanishi</th>
                  <th>Guruh tugashi</th>
                  <th>Ro'yxatdan o'tgan</th>
                  <th>Shartnoma Summasi</th>
                  <th>O'quvchi to'lagan summa</th>
                  <th>Holati</th>
                  <th>Izoh</th>
                  <th>To'lov Turi</th>
                  <th>Bonus summasi</th>
                  <th>Bonus to'langan sana</th>
                  <th>Bonus Holati</th>
                  <th style="width: 140px;">Amallar</th>
                </tr>
                <tr class="col-filter-row">
                  <th>
                    <input v-model="filterStudentName" class="col-filter-input" type="text" placeholder="Ism bo'yicha qidirish..." />
                  </th>
                  <th></th>
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
                      <button type="button" class="col-sort-icon-btn" :class="{ active: enrolledDateSort === 'asc' }" title="O'sish tartibida (eskidan yangiga)" @click="setSort('enrolledDate', 'asc')">
                        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M6 20V4"></path>
                          <path d="M3 8l3-4 3 4"></path>
                          <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                          <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                        </svg>
                      </button>
                      <button type="button" class="col-sort-icon-btn" :class="{ active: enrolledDateSort === 'desc' }" title="Kamayish tartibida (yangidan eskiga)" @click="setSort('enrolledDate', 'desc')">
                        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M6 4v16"></path>
                          <path d="M3 16l3 4 3-4"></path>
                          <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                          <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                        </svg>
                      </button>
                      <button v-if="enrolledDateFrom || enrolledDateTo" type="button" class="btn-clear-date" @click="enrolledDateFrom = ''; enrolledDateTo = ''" title="Tozalash">✕</button>
                    </div>
                    <div class="col-date-range">
                      <input v-model="enrolledDateFrom" type="date" class="col-date-input" title="Ro'yxatdan o'tgan sana (dan)" />
                      <input v-model="enrolledDateTo" type="date" class="col-date-input" title="Ro'yxatdan o'tgan sana (gacha)" />
                    </div>
                  </th>
                  <th></th>
                  <th>
                    <div class="select-wrap-relative">
                      <select v-model="filterPaidAmount" class="col-filter-select">
                        <option value="">Barchasi</option>
                        <option v-for="amt in distinctPaidAmounts" :key="amt" :value="amt">{{ formatMoney(amt) }}</option>
                      </select>
                    </div>
                  </th>
                  <th>
                    <div class="select-wrap-relative">
                      <select v-model="filterEnrollmentStatus" class="col-filter-select">
                        <option value="">Barchasi</option>
                        <option value="new">Yangi</option>
                        <option value="enrolled">Faol</option>
                        <option value="finished">Tugatgan</option>
                        <option value="canceled">Bekor qilingan</option>
                      </select>
                    </div>
                  </th>
                  <th></th>
                  <th>
                    <div class="select-wrap-relative">
                      <select v-model="filterBonusMethod" class="col-filter-select">
                        <option value="">Barchasi</option>
                        <option value="cash">Naqd</option>
                        <option value="card">Karta</option>
                        <option value="qr_code">QR code</option>
                        <option value="click">Click</option>
                        <option value="transfer">O'tkazma</option>
                      </select>
                    </div>
                  </th>
                  <th></th>
                  <th>
                    <div class="col-sort-group">
                      <button type="button" class="col-sort-icon-btn" :class="{ active: bonusPaidDateSort === 'asc' }" title="O'sish tartibida (eskidan yangiga)" @click="setSort('bonusPaidDate', 'asc')">
                        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M6 20V4"></path>
                          <path d="M3 8l3-4 3 4"></path>
                          <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                          <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                        </svg>
                      </button>
                      <button type="button" class="col-sort-icon-btn" :class="{ active: bonusPaidDateSort === 'desc' }" title="Kamayish tartibida (yangidan eskiga)" @click="setSort('bonusPaidDate', 'desc')">
                        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M6 4v16"></path>
                          <path d="M3 16l3 4 3-4"></path>
                          <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                          <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                        </svg>
                      </button>
                      <button v-if="bonusPaidDateFrom || bonusPaidDateTo" type="button" class="btn-clear-date" @click="bonusPaidDateFrom = ''; bonusPaidDateTo = ''" title="Tozalash">✕</button>
                    </div>
                    <div class="col-date-range">
                      <input v-model="bonusPaidDateFrom" type="date" class="col-date-input" title="Bonus to'langan sana (dan)" />
                      <input v-model="bonusPaidDateTo" type="date" class="col-date-input" title="Bonus to'langan sana (gacha)" />
                    </div>
                  </th>
                  <th>
                    <div class="select-wrap-relative">
                      <select v-model="filterBonusStatus" class="col-filter-select">
                        <option value="">Barchasi</option>
                        <option value="paid">Bonus to'langan</option>
                        <option value="pending">Bonus to'lanmagan</option>
                      </select>
                    </div>
                  </th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="paginatedEnrollmentsWithBonus.length === 0">
                  <td colspan="16" class="td-empty">Filtrlarga mos o'quvchi topilmadi</td>
                </tr>
                <tr v-for="item in paginatedEnrollmentsWithBonus" :key="item.id" class="table-row">
                  <td class="td-name">
                    <router-link :to="`/students/${item.student}`" class="student-link">
                      {{ item.student_name || 'Noma\'lum' }}
                    </router-link>
                  </td>
                  <td>{{ item.branch_name || '-' }}</td>
                  <td><span class="cat-badge">{{ item.category_name || '-' }}</span></td>
                  <td>
                    <span v-if="item.group" class="link-value" @click="goGroup(item.group)">{{ item.group_name || '-' }}</span>
                    <span v-else>{{ item.group_name || '-' }}</span>
                  </td>
                  <td class="td-date">{{ groupsById[item.group] ? formatDate(groupsById[item.group].started_at) : '-' }}</td>
                  <td class="td-date">{{ groupsById[item.group] ? formatDate(groupsById[item.group].ends_at) : '-' }}</td>
                  <td class="td-date">{{ formatDate(item.created_at) }}</td>
                  <td class="td-amount">
                    <span v-if="item.enrolled_free" class="grant-pill">Bepul (Grant)</span>
                    <span v-else class="amount-val">{{ formatMoney(item.enrolled_amount) }}</span>
                  </td>
                  <td class="td-amount">
                    <span class="amount-val" style="color: #2D6A4F;">{{ formatMoney(item.paid_amount) }}</span>
                  </td>
                  <td>
                    <span class="status-chip" :class="item.status">{{ statusText(item.status) }}</span>
                  </td>
                  <td>{{ item.notes || '-' }}</td>
                  <td>{{ item.bonusPayment ? methodText(item.bonusPayment.method) : '-' }}</td>
                  <td>{{ item.bonusPayment ? formatMoney(item.bonusPayment.amount) : '-' }}</td>
                  <td class="td-date">{{ item.bonusPayment?.created_at ? formatDate(item.bonusPayment.created_at) : '-' }}</td>
                  <td>
                    <span class="bonus-chip-tag" v-if="item.bonusPayment">Bonus to'langan</span>
                    <span class="bonus-chip-unpaid" v-else>Bonus to'lanmagan</span>
                  </td>
                  <td>
                    <button
                      v-if="!item.bonusPayment && authStore.canPayBonus"
                      class="btn-pay-bonus"
                      @click="openPayBonusModal(item)"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                      </svg>
                      <span>To'lov qilish</span>
                    </button>
                    <span v-else>-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pagination-bar">
            <span class="pagination-info">
              Jami: <strong>{{ filteredEnrollmentsWithBonus.length }}</strong> tadan <strong>{{ paginatedEnrollmentsWithBonus.length }}</strong> ko'rsatilmoqda
            </span>
            <div class="pagination-actions">
              <label class="page-size-label" for="agent-page-size">Ko'rsatish:</label>
              <div class="select-wrap-relative">
                <select id="agent-page-size" v-model="pageSizeOption" class="page-size-select">
                  <option value="50">50</option>
                  <option value="100">100</option>
                  <option value="200">200</option>
                  <option value="all">Barchasi</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- PAY BONUS MODAL -->
    <Transition name="modal">
      <div v-if="showPayModal" class="modal-overlay" @click.self="closePayModal">
        <div class="modal-card">
          <div class="modal-header-banner bonus-banner">
            <div class="modal-header-left">
              <div class="header-icon-box gold-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                </svg>
              </div>
              <div>
                <h3 class="modal-title-text">Agentga Bonus To'lovini Amalga Oshirish</h3>
                <p class="modal-subtitle-text">Tanlangan o'quvchi uchun agentga bonus summasi to'lanadi</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closePayModal" title="Yopish">✕</button>
          </div>

          <form @submit.prevent="submitBonusPayment" class="modal-form-body">
            <div v-if="payModalError" class="modal-error-alert">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" style="flex-shrink: 0;">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
              <span>{{ payModalError }}</span>
            </div>

            <!-- Target Student & Enrollment Info Card -->
            <div v-if="selectedEnrollment" class="target-info-card">
              <div class="target-card-header">
                <div class="target-avatar">
                  {{ selectedEnrollment.student_name?.[0] || 'O' }}
                </div>
                <div class="target-student-meta">
                  <h4 class="target-student-name">{{ selectedEnrollment.student_name }}</h4>
                  <span class="target-cat-tag">{{ selectedEnrollment.category_name }} {{ selectedEnrollment.group_name ? `(${selectedEnrollment.group_name})` : '' }}</span>
                </div>
              </div>
              <div class="target-card-footer">
                <span class="target-label">Hamkor Agent:</span>
                <span class="target-agent-name">👤 {{ agent?.full_name }}</span>
              </div>
            </div>

            <!-- Bonus Amount Input -->
            <div class="form-field-group">
              <label class="field-label required">Bonus Summasi *</label>
              <div class="input-with-addon">
                <input
                  v-model="payForm.amountFormatted"
                  type="text"
                  class="field-input amount-field"
                  placeholder="0"
                  required
                  @input="onBonusAmountInput"
                />
              </div>
            </div>

            <!-- Payment Method Select -->
            <div class="form-field-group">
              <label class="field-label required">To'lov Usuli *</label>
              <div class="select-field-wrap">
                <div class="input-icon-left">
                  <svg viewBox="0 0 24 24" fill="none" stroke="#6B7280" stroke-width="2" width="18" height="18">
                    <rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect>
                    <line x1="1" y1="10" x2="23" y2="10"></line>
                  </svg>
                </div>
                <select v-model="payForm.method" class="field-input field-select select-has-icon">
                  <option value="cash">Naqd</option>
                  <option value="card">Karta</option>
                  <option value="qr_code">QR code</option>
                  <option value="click">Click</option>
                  <option value="transfer">O'tkazma</option>
                </select>
                <div class="select-chevron">
                  <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                  </svg>
                </div>
              </div>
            </div>

            <!-- Notes Input -->
            <div class="form-field-group">
              <label class="field-label">Izoh / Eslatma</label>
              <div class="input-with-addon">
                <div class="input-icon-left">
                  <svg viewBox="0 0 24 24" fill="none" stroke="#6B7280" stroke-width="2" width="18" height="18">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </div>
                <input v-model="payForm.notes" type="text" class="field-input input-has-icon" placeholder="Masalan: Ushbu o'quvchi uchun berilgan bonus..." />
              </div>
            </div>

            <div class="modal-footer-actions">
              <button type="button" class="btn-modal-cancel" @click="closePayModal">Bekor qilish</button>
              <button type="submit" class="btn-modal-submit gold-btn" :disabled="paySaving">
                <div v-if="paySaving" class="btn-spinner"></div>
                <span>{{ paySaving ? "To'lov saqlanmoqda..." : "🎁 Bonusni To'lash" }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- EDIT AGENT MODAL -->
    <Transition name="modal">
      <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditAgentModal">
        <div class="modal-card">
          <div class="modal-header-banner">
            <div class="modal-header-left">
              <div class="header-icon-box">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="22" height="22">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="9" cy="7" r="4"></circle>
                </svg>
              </div>
              <div>
                <h3 class="modal-title-text">Agent Ma'lumotlarini Tahrirlash</h3>
                <p class="modal-subtitle-text">Hamkor agent ma'lumotlarini yangilang</p>
              </div>
            </div>
            <button class="btn-modal-close" @click="closeEditAgentModal" title="Yopish">✕</button>
          </div>

          <form @submit.prevent="saveAgent" class="modal-form-body">
            <div v-if="editModalError" class="modal-error-alert">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" style="flex-shrink: 0;">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
              <span>{{ editModalError }}</span>
            </div>

            <div class="form-field-group checkbox-row">
              <input
                id="edit-ag-is-teacher"
                v-model="editForm.is_teacher"
                type="checkbox"
                class="form-checkbox"
                @change="onToggleEditIsTeacher"
              />
              <label for="edit-ag-is-teacher" class="form-checkbox-label">O'qituvchimi/Instruktormi?</label>
            </div>

            <template v-if="!editForm.is_teacher">
              <div class="form-field-group">
                <label class="field-label required">Agent F.I.SH.</label>
                <div class="input-with-addon">
                  <div class="input-icon-left">
                    <svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="2" width="18" height="18">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                      <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                  </div>
                  <input v-model="editForm.full_name" type="text" class="field-input input-has-icon" placeholder="Masalan: Samandar Qodirov" required />
                </div>
              </div>

              <div class="form-two-cols">
                <div class="form-field-group">
                  <label class="field-label required">Telefon raqami</label>
                  <div class="input-with-addon">
                    <div class="input-icon-left">
                      <svg viewBox="0 0 24 24" fill="none" stroke="#6B7280" stroke-width="2" width="18" height="18">
                        <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                      </svg>
                    </div>
                    <input v-model="editForm.phone" type="text" class="field-input input-has-icon" placeholder="+998 90 123 45 67" required @input="handlePhoneInput($event, 'phone')" />
                  </div>
                </div>

                <div class="form-field-group">
                  <label class="field-label">Qo'shimcha telefon</label>
                  <div class="input-with-addon">
                    <div class="input-icon-left">
                      <svg viewBox="0 0 24 24" fill="none" stroke="#6B7280" stroke-width="2" width="18" height="18">
                        <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                      </svg>
                    </div>
                    <input v-model="editForm.phone2" type="text" class="field-input input-has-icon" placeholder="+998 90 987 65 43" @input="handlePhoneInput($event, 'phone2')" />
                  </div>
                </div>
              </div>
            </template>

            <template v-else>
              <div class="form-field-group">
                <label class="field-label required">O'qituvchi / Instruktor</label>
                <div class="teacher-searchable-select" @click.stop>
                  <input
                    type="text"
                    class="field-input"
                    :class="{ 'has-clear': editForm.user }"
                    v-model="editTeacherSearchText"
                    @focus="editTeacherDropdownOpen = true"
                    @input="editTeacherDropdownOpen = true"
                    placeholder="Ism yoki telefon bo'yicha qidirish..."
                    autocomplete="off"
                  />
                  <button
                    v-if="editForm.user"
                    type="button"
                    class="btn-clear-teacher"
                    title="Tozalash"
                    @mousedown.prevent="clearEditTeacher"
                  >✕</button>
                  <div v-if="editTeacherDropdownOpen" class="searchable-dropdown">
                    <div
                      v-for="t in filteredEditTeacherOptions"
                      :key="t.id"
                      class="searchable-option"
                      :class="{ selected: editForm.user === t.id }"
                      @mousedown.prevent="selectEditTeacher(t)"
                    >
                      {{ t.full_name || t.phone }}
                      <span class="opt-role-tag">{{ t.role === 'instructor' ? 'Instruktor' : "O'qituvchi" }}</span>
                    </div>
                    <div v-if="filteredEditTeacherOptions.length === 0" class="searchable-empty">Topilmadi</div>
                  </div>
                </div>
              </div>
            </template>

            <div class="form-field-group">
              <label class="field-label">Izoh / Eslatma</label>
              <textarea v-model="editForm.notes" rows="3" class="field-input field-textarea" placeholder="Agent bo'yicha qo'shimcha izohlar..."></textarea>
            </div>

            <div class="modal-footer-actions">
              <button type="button" class="btn-modal-cancel" @click="closeEditAgentModal">Bekor qilish</button>
              <button type="submit" class="btn-modal-submit" :disabled="editSaving">
                <div v-if="editSaving" class="btn-spinner"></div>
                <span>{{ editSaving ? 'Saqlanmoqda...' : 'Saqlash' }}</span>
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
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useBranchStore } from '@/stores/branch'
import { formatMoney, formatPhone, formatDate } from '@/utils/formatters'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const branchStore = useBranchStore()

const agent = ref(null)
const loading = ref(true)
const error = ref(null)

const enrollments = ref([])
const bonusPayments = ref([])
const loadingEnrollments = ref(false)
const groups = ref([])

const groupsById = computed(() => {
  const map = {}
  groups.value.forEach(g => { map[g.id] = g })
  return map
})

async function fetchGroups() {
  try {
    const res = await api.get('/groups/', { params: { page_size: 1000 } })
    groups.value = res.data.results || res.data
  } catch (err) {
    console.error("Guruhlarni yuklashda xatolik:", err)
  }
}

// Pay Bonus Modal state
const showPayModal = ref(false)
const selectedEnrollment = ref(null)
const payModalError = ref(null)
const paySaving = ref(false)
const payForm = ref({
  amountFormatted: '',
  amount: 0,
  method: 'cash',
  notes: ''
})

// Edit Agent Modal state
const showEditModal = ref(false)
const editSaving = ref(false)
const editModalError = ref(null)
const editForm = ref({
  full_name: '',
  phone: '',
  phone2: '',
  notes: '',
  is_teacher: false,
  user: null,
})

// ── Teacher/instructor agent picker (edit modal) ───────
// Mirrors AgentsView.vue's create/edit modal: an instructor/coordinator can
// also be an "agent" via Agent.user. A teacher already linked to another
// agent is excluded from the picker (except this agent's own current link).
const editTeacherOptions = ref([])
async function fetchEditTeacherOptions() {
  try {
    const [instRes, coordRes] = await Promise.all([
      api.get('/users/', { params: { role: 'instructor', page_size: 1000 } }),
      api.get('/users/', { params: { role: 'coordinator', page_size: 1000 } }),
    ])
    const instructors = instRes.data.results || instRes.data || []
    const coordinators = coordRes.data.results || coordRes.data || []
    editTeacherOptions.value = [...instructors, ...coordinators]
  } catch (err) {
    console.error("O'qituvchi/instruktorlarni yuklashda xatolik:", err)
  }
}

const editAllAgentLinks = ref([])
async function fetchEditAllAgentLinks() {
  try {
    const res = await api.get('/agents/', { params: { page_size: 1000 } })
    const list = res.data.results || res.data || []
    editAllAgentLinks.value = list.filter(a => a.user).map(a => ({ id: a.id, user: a.user }))
  } catch (err) {
    console.error("Agent bog'lanishlarini yuklashda xatolik:", err)
  }
}
const editAssignedTeacherUserIds = computed(() => {
  const ids = new Set()
  editAllAgentLinks.value.forEach(link => {
    if (link.id !== agent.value?.id) ids.add(link.user)
  })
  return ids
})

const editTeacherSearchText = ref('')
const editTeacherDropdownOpen = ref(false)
const filteredEditTeacherOptions = computed(() => {
  const q = editTeacherSearchText.value.trim().toLowerCase()
  const available = editTeacherOptions.value.filter(t => !editAssignedTeacherUserIds.value.has(t.id))
  if (!q) return available
  return available.filter(t =>
    (t.full_name || '').toLowerCase().includes(q) || (t.phone || '').includes(q)
  )
})
function selectEditTeacher(t) {
  editForm.value.user = t ? t.id : null
  editTeacherSearchText.value = t ? (t.full_name || t.phone) : ''
  editTeacherDropdownOpen.value = false
}
function clearEditTeacher() {
  selectEditTeacher(null)
}
function onToggleEditIsTeacher() {
  if (editForm.value.is_teacher) {
    if (editTeacherOptions.value.length === 0) fetchEditTeacherOptions()
    fetchEditAllAgentLinks()
  } else {
    editForm.value.user = null
    editTeacherSearchText.value = ''
  }
}
function handleEditTeacherOutsideClick(e) {
  if (e.target.closest('.teacher-searchable-select')) return
  editTeacherDropdownOpen.value = false
}

const agentInitials = computed(() => {
  if (!agent.value || !agent.value.full_name) return 'A'
  const parts = agent.value.full_name.trim().split(' ')
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  return agent.value.full_name.slice(0, 2).toUpperCase()
})

// Cards reflect the currently filtered table rows, not the agent's whole
// history — so applying a header filter narrows the summary cards too.
const totalBonusSum = computed(() => {
  return filteredEnrollmentsWithBonus.value.reduce((acc, e) => acc + (e.bonusPayment ? Number(e.bonusPayment.amount) || 0 : 0), 0)
})

// Header-column filters
const categories = ref([])
const filterStudentName = ref('')
const filterCategory = ref('')
const filterGroupName = ref('')
const filterPaidAmount = ref('')
const filterEnrollmentStatus = ref('')
const filterBonusStatus = ref('')
const filterBonusMethod = ref('')
const groupStartSort = ref('')
const groupEndSort = ref('')
const groupStartFrom = ref('')
const groupStartTo = ref('')
const groupEndFrom = ref('')
const groupEndTo = ref('')
const enrolledDateSort = ref('')
const bonusPaidDateSort = ref('')
const enrolledDateFrom = ref('')
const enrolledDateTo = ref('')
const bonusPaidDateFrom = ref('')
const bonusPaidDateTo = ref('')

const sortRefs = { groupStart: groupStartSort, groupEnd: groupEndSort, enrolledDate: enrolledDateSort, bonusPaidDate: bonusPaidDateSort }
function setSort(field, dir) {
  const target = sortRefs[field]
  Object.values(sortRefs).forEach(r => { if (r !== target) r.value = '' })
  target.value = target.value === dir ? '' : dir
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

function goGroup(id) {
  if (id) router.push(`/groups/${id}`)
}

async function fetchCategories() {
  try {
    const res = await api.get('/categories/')
    categories.value = res.data.results ? res.data.results : res.data
  } catch (err) {
    console.error(err)
  }
}

const enrollmentsWithBonus = computed(() => {
  return enrollments.value.map(e => {
    // Find matching bonus payment for this enrollment or student
    const bp = bonusPayments.value.find(p => 
      p.enrollment === e.id || p.enrollment_id === e.id || p.student === e.student || p.student_id === e.student
    )
    return {
      ...e,
      bonusPayment: bp || null
    }
  })
})

const bonusPaidCount = computed(() => {
  return filteredEnrollmentsWithBonus.value.filter(e => e.bonusPayment != null).length
})

const bonusPendingCount = computed(() => {
  return filteredEnrollmentsWithBonus.value.filter(e => e.bonusPayment == null).length
})

// Deduped, sorted list of paid amounts among this agent's students, for
// the "To'langan Summa" filter select.
const distinctPaidAmounts = computed(() => {
  const amounts = new Set()
  enrollments.value.forEach(e => {
    if (e.paid_amount) amounts.add(Number(e.paid_amount))
  })
  return [...amounts].sort((a, b) => a - b)
})

const filteredEnrollmentsWithBonus = computed(() => {
  const name = filterStudentName.value.trim().toLowerCase()
  const group = filterGroupName.value.trim().toLowerCase()

  let list = enrollmentsWithBonus.value.filter(e => {
    if (filterBonusStatus.value === 'paid' && e.bonusPayment == null) return false
    if (filterBonusStatus.value === 'pending' && e.bonusPayment != null) return false
    if (filterBonusMethod.value && e.bonusPayment?.method !== filterBonusMethod.value) return false
    if (filterCategory.value && String(e.category) !== String(filterCategory.value)) return false
    if (filterPaidAmount.value && Number(e.paid_amount) !== Number(filterPaidAmount.value)) return false
    if (filterEnrollmentStatus.value && e.status !== filterEnrollmentStatus.value) return false
    if (name && !(e.student_name || '').toLowerCase().includes(name)) return false
    if (group && !(e.group_name || '').toLowerCase().includes(group)) return false
    const g = groupsById.value[e.group]
    if (groupStartFrom.value && !(g?.started_at && g.started_at >= groupStartFrom.value)) return false
    if (groupStartTo.value && !(g?.started_at && g.started_at <= groupStartTo.value)) return false
    if (groupEndFrom.value && !(g?.ends_at && g.ends_at >= groupEndFrom.value)) return false
    if (groupEndTo.value && !(g?.ends_at && g.ends_at <= groupEndTo.value)) return false
    // created_at is a full timestamp, not a bare date — slice before
    // comparing to the plain YYYY-MM-DD filter value, otherwise every
    // record on the selected "to" day (any time after 00:00:00) sorts as
    // greater than the bare date and gets wrongly excluded.
    if (enrolledDateFrom.value && !(e.created_at && e.created_at.slice(0, 10) >= enrolledDateFrom.value)) return false
    if (enrolledDateTo.value && !(e.created_at && e.created_at.slice(0, 10) <= enrolledDateTo.value)) return false
    if (bonusPaidDateFrom.value && !(e.bonusPayment?.created_at && e.bonusPayment.created_at.slice(0, 10) >= bonusPaidDateFrom.value)) return false
    if (bonusPaidDateTo.value && !(e.bonusPayment?.created_at && e.bonusPayment.created_at.slice(0, 10) <= bonusPaidDateTo.value)) return false
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
  } else if (enrolledDateSort.value) {
    const dir = enrolledDateSort.value === 'asc' ? 1 : -1
    list = list.slice().sort((a, b) => {
      const ta = a.created_at ? new Date(a.created_at).getTime() : null
      const tb = b.created_at ? new Date(b.created_at).getTime() : null
      if (ta === null && tb === null) return 0
      if (ta === null) return 1
      if (tb === null) return -1
      return (ta - tb) * dir
    })
  } else if (bonusPaidDateSort.value) {
    const dir = bonusPaidDateSort.value === 'asc' ? 1 : -1
    list = list.slice().sort((a, b) => {
      const ta = a.bonusPayment?.created_at ? new Date(a.bonusPayment.created_at).getTime() : null
      const tb = b.bonusPayment?.created_at ? new Date(b.bonusPayment.created_at).getTime() : null
      if (ta === null && tb === null) return 0
      if (ta === null) return 1
      if (tb === null) return -1
      return (ta - tb) * dir
    })
  }

  return list
})

// Row-fetch-count selector: how many of the filtered rows to display,
// replacing classic next/prev pagination (all data is already loaded
// client-side, so this is purely a display cap).
const pageSizeOption = ref('50')
const paginatedEnrollmentsWithBonus = computed(() => {
  if (pageSizeOption.value === 'all') return filteredEnrollmentsWithBonus.value
  return filteredEnrollmentsWithBonus.value.slice(0, Number(pageSizeOption.value))
})

function goBack() {
  router.push('/agents')
}

async function fetchAll() {
  loading.value = true
  error.value = null
  try {
    const res = await api.get(`/agents/${route.params.id}/`)
    agent.value = res.data
    await fetchAgentEnrollmentsAndPayments()
  } catch (err) {
    console.error(err)
    error.value = "Agent ma'lumotlarini yuklashda xatolik"
  } finally {
    loading.value = false
  }
}

async function fetchAgentEnrollmentsAndPayments() {
  loadingEnrollments.value = true
  try {
    // fetchGroups() runs alongside the enrollment/payment fetches (rather
    // than as its own unawaited call in onMounted) so the table only
    // reveals itself once groupsById has what it needs — otherwise the
    // table renders as soon as enrollments arrive, group start/end read
    // '-' from the still-empty groups list, and the dates visibly pop in
    // a moment later once the separate /groups/ request finishes.
    const [eRes, pRes] = await Promise.all([
      api.get('/enrollments/', { params: { agent: route.params.id, page_size: 5000 } }),
      api.get('/payments/', { params: { agent: route.params.id, status: 'bonus', page_size: 5000 } }),
      fetchGroups(),
    ])
    enrollments.value = eRes.data.results ? eRes.data.results : eRes.data
    bonusPayments.value = pRes.data.results ? pRes.data.results : pRes.data
  } catch (err) {
    console.error(err)
  } finally {
    loadingEnrollments.value = false
  }
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

// Bonus amount formatting on input
function onBonusAmountInput(e) {
  const val = e.target.value
  const digits = val.replace(/\D/g, '')
  if (!digits) {
    payForm.value.amount = 0
    payForm.value.amountFormatted = ''
    return
  }
  const num = parseInt(digits, 10)
  payForm.value.amount = num
  payForm.value.amountFormatted = formatMoney(num, false)
}

// Open Pay Bonus Modal for specific student enrollment
function openPayBonusModal(item) {
  selectedEnrollment.value = item
  payModalError.value = null
  payForm.value = {
    amountFormatted: '',
    amount: 0,
    method: 'cash',
    notes: ''
  }
  showPayModal.value = true
}

function closePayModal() {
  showPayModal.value = false
  selectedEnrollment.value = null
}

async function submitBonusPayment() {
  if (!payForm.value.amount || payForm.value.amount <= 0) {
    payModalError.value = "Iltimos, to'g'ri bonus summasini kiriting."
    return
  }

  paySaving.value = true
  payModalError.value = null
  try {
    await api.post('/payments/', {
      user: authStore.user?.id,
      enrollment: selectedEnrollment.value.id,
      agent: agent.value.id,
      amount: payForm.value.amount,
      method: payForm.value.method,
      status: 'bonus',
      notes: payForm.value.notes || `Bonus payment for ${selectedEnrollment.value.student_name}`,
      branch: branchStore.activeBranchId ?? null,
    })

    closePayModal()
    await fetchAgentEnrollmentsAndPayments()
  } catch (err) {
    console.error(err)
    payModalError.value = err.response?.data?.detail || "Bonus to'lovini saqlashda xatolik yuz berdi."
  } finally {
    paySaving.value = false
  }
}

// Digits-only stored phone -> "+998 90 900 90 90" for display/editing.
function formatPhoneDisplay(p) {
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

function handlePhoneInput(event, key) {
  const val = event.target.value
  if (!val) {
    editForm.value[key] = ''
    return
  }
  editForm.value[key] = formatPhoneDisplay(val)
}

function openEditAgentModal() {
  editModalError.value = null
  editForm.value = {
    full_name: agent.value.full_name || '',
    phone: agent.value.phone ? formatPhoneDisplay(agent.value.phone) : '',
    phone2: agent.value.phone2 ? formatPhoneDisplay(agent.value.phone2) : '',
    notes: agent.value.notes || '',
    is_teacher: !!agent.value.user,
    user: agent.value.user || null,
  }
  editTeacherSearchText.value = agent.value.user ? (agent.value.user_name || '') : ''
  editTeacherDropdownOpen.value = false
  if (agent.value.user) {
    if (editTeacherOptions.value.length === 0) fetchEditTeacherOptions()
    fetchEditAllAgentLinks()
  }
  showEditModal.value = true
}

function closeEditAgentModal() {
  showEditModal.value = false
}

async function saveAgent() {
  let payload

  if (editForm.value.is_teacher) {
    if (!editForm.value.user) {
      editModalError.value = "O'qituvchi yoki instruktorni tanlang."
      return
    }
    payload = { user: editForm.value.user, notes: editForm.value.notes?.trim() || '' }
  } else {
    if (!editForm.value.full_name.trim() || !editForm.value.phone.trim()) {
      editModalError.value = "Barcha majburiy maydonlarni to'ldiring."
      return
    }
    payload = {
      user: null,
      full_name: editForm.value.full_name.trim(),
      phone: editForm.value.phone.replace(/\D/g, ''),
      phone2: editForm.value.phone2 ? editForm.value.phone2.replace(/\D/g, '') : '',
      notes: editForm.value.notes,
    }
  }

  editSaving.value = true
  editModalError.value = null
  try {
    const res = await api.patch(`/agents/${agent.value.id}/`, payload)
    agent.value = res.data
    closeEditAgentModal()
  } catch (err) {
    const data = err.response?.data
    if (data?.phone) {
      editModalError.value = "Ushbu telefon raqamli agent allaqachon mavjud."
    } else if (data?.user) {
      editModalError.value = Array.isArray(data.user) ? data.user[0] : String(data.user)
    } else {
      editModalError.value = data?.detail || "Saqlashda xatolik yuz berdi"
    }
  } finally {
    editSaving.value = false
  }
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchCurrentUser()
  }
  fetchAll()
  fetchCategories()
  document.addEventListener('click', handleEditTeacherOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleEditTeacherOutsideClick)
})
</script>

<style scoped>
.page-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.top-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: #6B7280;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  padding: 0;

  &:hover {
    color: #2D6A4F;
  }
}

.page-main-title {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
}

.btn-edit-profile {
  display: inline-flex;
  align-items: center;
  padding: 10px 18px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13px;
  box-shadow: 0 4px 12px rgba(45, 106, 79, 0.25);
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(45, 106, 79, 0.35);
  }
}

.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 0;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #E5E7EB;
  border-top-color: #2D6A4F;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.detail-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile-card {
  background: white;
  border-radius: 16px;
  border: 1px solid #E5E7EB;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #F3F4F6;
}

.avatar-large {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%);
  color: white;
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 16px rgba(45, 106, 79, 0.25);
}

.profile-name {
  font-size: 19px;
  font-weight: 700;
  color: #111827;
}

.agent-chip {
  display: inline-block;
  padding: 3px 10px;
  background: #F0FDF4;
  color: #2D6A4F;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  margin-top: 4px;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: #6B7280;
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  color: #111827;
}

.notes-block {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #F3F4F6;
}

.notes-text {
  font-size: 13.5px;
  color: #4B5563;
  background: #F9FAFB;
  padding: 10px 14px;
  border-radius: 8px;
  border-left: 3px solid #2D6A4F;
  margin-top: 6px;
}

/* Bonus Metrics Cards */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}

.metric-card {
  background: white;
  border-radius: 14px;
  border: 1px solid #E5E7EB;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  &.green { background: #E8F5E9; color: #2D6A4F; }
  &.gold { background: #FEF3C7; color: #D97706; }
  &.orange { background: #FFF7ED; color: #EA580C; }
  &.purple { background: #F3E8FF; color: #9333EA; }
}

.metric-label {
  font-size: 12px;
  color: #6B7280;
  font-weight: 500;
  display: block;
}

.metric-value {
  font-size: 19px;
  font-weight: 700;
  color: #111827;
  margin-top: 2px;

  &.bonus-val { color: #D97706; }
  &.warning-text { color: #EA580C; }
  &.text-amber { color: #B45309; }
}

.select-wrap-relative { position: relative; width: 100%; }

/* Table Section */
.section-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-title {
  font-size: 17px;
  font-weight: 700;
  color: #111827;
}

.section-badge {
  font-size: 12.5px;
  font-weight: 600;
  color: #2D6A4F;
  background: #E8F5E9;
  padding: 4px 12px;
  border-radius: 20px;
}

.table-card {
  background: white;
  border-radius: 14px;
  border: 1px solid #E5E7EB;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

/* Bounded, independently-scrolling table body so the header (both the
   label row and the column-filter row) sticks to the top of this
   container as rows scroll underneath, instead of scrolling away with
   the page. */
.table-wrap {
  overflow: auto;
  max-height: 600px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;

  th {
    background: #F9FAFB;
    padding: 12px 18px;
    font-size: 12px;
    font-weight: 600;
    color: #4B5563;
    text-align: left;
    border-bottom: 1px solid #E5E7EB;
    white-space: nowrap;
  }

  td {
    padding: 14px 18px;
    font-size: 13.5px;
    color: #1F2937;
    border-bottom: 1px solid #F3F4F6;
    vertical-align: middle;
  }

  tr:last-child td {
    border-bottom: none;
  }

  thead {
    position: sticky;
    top: 0;
    z-index: 3;
  }

  thead tr.col-filter-row th {
    padding: 8px 10px;
    background: #FAFAFB;
  }
}

.td-date { white-space: nowrap; }
.td-empty { text-align: center; padding: 32px; color: #9CA3AF; }

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
.col-filter-input:focus, .col-filter-select:focus { border-color: #2D6A4F; }
.col-filter-input::placeholder { color: #9CA3AF; }

.col-date-range { display: flex; flex-direction: column; gap: 4px; margin-top: 6px; }
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

.link-value { cursor: pointer; color: #2563EB; font-weight: 600; text-decoration: underline; }
.link-value:hover { color: #1D4ED8; text-decoration: underline; }

.status-chip { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11.5px; font-weight: 600; }
.status-chip.new { background: #E0F2FE; color: #0369A1; }
.status-chip.enrolled { background: #DCFCE7; color: #15803D; }
.status-chip.finished { background: #F3F4F6; color: #4B5563; }
.status-chip.canceled { background: #FEE2E2; color: #B91C1C; }

.pagination-bar { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #F9FAFB; border-top: 1px solid #E5E7EB; }
.pagination-info { font-size: 13.5px; color: #6B7280; font-weight: 500; }
.pagination-actions { display: flex; align-items: center; gap: 8px; }
.page-num { display: inline-flex; align-items: center; padding: 0 12px; font-weight: 600; color: #374151; font-size: 14px; }
.page-size-label { font-size: 13px; font-weight: 600; color: #4B5563; }
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
.btn-page {
  padding: 7px 16px;
  border-radius: 8px;
  border: 1px solid #E5E7EB;
  background: white;
  color: #374151;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-page:hover:not(:disabled) { background: #F3F4F6; border-color: #D1D5DB; }
.btn-page:disabled { opacity: 0.5; cursor: not-allowed; }

.student-link {
  color: #2D6A4F;
  font-weight: 700;
  text-decoration: none;

  &:hover { text-decoration: underline; }
}

.cat-badge {
  padding: 3px 8px;
  background: #E8F5E9;
  color: #2D6A4F;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
}

.group-pill {
  padding: 3px 8px;
  background: #EFF6FF;
  color: #2563EB;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.grant-pill {
  padding: 3px 8px;
  background: #F3E8FF;
  color: #9333EA;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.amount-val { font-weight: 600; color: #111827; }

/* Bonus status — plain text, no badge/box styling */
.bonus-chip-tag { font-size: 12.5px; font-weight: 700; color: #15803D; }
.bonus-chip-unpaid { font-size: 12.5px; font-weight: 600; color: #C2410C; }

.btn-pay-bonus {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 12.5px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(217, 119, 6, 0.25);
  transition: all 0.15s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(217, 119, 6, 0.35);
  }
}

.empty-state {
  text-align: center;
  padding: 48px 24px;
  background: white;
  border-radius: 14px;
  border: 1px dashed #D1D5DB;
}

.empty-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.empty-title { font-size: 15px; font-weight: 700; color: #111827; }
.empty-sub { font-size: 13px; color: #6B7280; margin-top: 4px; }

/* Modal Overlay & Card Styling */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-card {
  background: white;
  border-radius: 20px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.modal-header-banner {
  padding: 20px 24px;
  background: linear-gradient(180deg, #F0FDF4 0%, #FFFFFF 100%);
  border-bottom: 1px solid #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: space-between;

  &.bonus-banner {
    background: linear-gradient(180deg, #FEF3C7 0%, #FFFFFF 100%);
  }
}

.modal-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;

  &.gold-box {
    background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
  }
}

.modal-title-text { font-size: 16.5px; font-weight: 700; color: #111827; }
.modal-subtitle-text { font-size: 12px; color: #6B7280; }

.btn-modal-close {
  background: none;
  border: none;
  font-size: 18px;
  color: #9CA3AF;
  cursor: pointer;
}

.modal-form-body { padding: 24px; }

.target-info-card {
  background: linear-gradient(135deg, #FEF3C7 0%, #FFFBEB 100%);
  border: 1px solid #FDE68A;
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 22px;
  box-shadow: 0 2px 8px rgba(217, 119, 6, 0.08);
}

.target-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.target-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
  color: white;
  font-weight: 700;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 3px 8px rgba(217, 119, 6, 0.25);
}

.target-student-meta {
  display: flex;
  flex-direction: column;
}

.target-student-name {
  font-size: 15px;
  font-weight: 700;
  color: #78350F;
}

.target-cat-tag {
  font-size: 12px;
  font-weight: 600;
  color: #92400E;
}

.target-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px dashed #FCD34D;
  font-size: 12.5px;
}

.target-label {
  color: #92400E;
  font-weight: 500;
}

.target-agent-name {
  color: #2D6A4F;
  font-weight: 700;
}

.input-with-addon {
  position: relative;
  display: flex;
  align-items: center;
}

.select-field-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon-left {
  position: absolute;
  left: 12px;
  display: flex;
  align-items: center;
  pointer-events: none;
  z-index: 2;
}

.input-has-icon {
  padding-left: 40px !important;
}

.select-has-icon {
  padding-left: 40px !important;
  appearance: none;
  -webkit-appearance: none;
}

.input-addon-right {
  position: absolute;
  right: 14px;
  font-size: 13px;
  font-weight: 700;
  color: #D97706;
  pointer-events: none;
}

.select-chevron {
  position: absolute;
  right: 12px;
  color: #6B7280;
  pointer-events: none;
}

.form-field-group { margin-bottom: 18px; }
.form-two-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }

.field-label {
  display: block;
  font-size: 12.5px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 6px;

  &.required::after {
    content: " *";
    color: #EF4444;
  }
}

.field-input {
  width: 100%;
  box-sizing: border-box;
  padding: 11px 14px;
  border: 1.5px solid #E5E7EB;
  border-radius: 10px;
  font-size: 14px;
  background-color: #FAFAFA;
  transition: all 0.2s ease;

  &:focus {
    border-color: #D97706;
    background-color: white;
    outline: none;
    box-shadow: 0 0 0 3.5px rgba(217, 119, 6, 0.15);
  }

  &.amount-field {
    font-size: 17px;
    font-weight: 800;
    color: #B45309;
  }
}

.field-select {
  background-color: #FAFAFA;
  cursor: pointer;
}

.field-textarea { width: 100%; max-width: 100%; resize: vertical; }

.checkbox-row { display: flex; flex-direction: row; align-items: center; gap: 8px; }
.form-checkbox { width: 16px; height: 16px; cursor: pointer; accent-color: #2D6A4F; }
.form-checkbox-label { font-size: 13.5px; font-weight: 600; color: #374151; cursor: pointer; }

.teacher-searchable-select { position: relative; }
.teacher-searchable-select .field-input { width: 100%; box-sizing: border-box; }
.teacher-searchable-select .field-input.has-clear { padding-right: 34px; }
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

.modal-footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 26px;
}

.btn-modal-cancel {
  padding: 10px 18px;
  border: 1px solid #D1D5DB;
  background: white;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13px;
  color: #374151;
  cursor: pointer;

  &:hover {
    background: #F9FAFB;
  }
}

.btn-modal-submit {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 22px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  font-size: 13.5px;
  cursor: pointer;
  transition: all 0.15s ease;

  &.gold-btn {
    background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
    box-shadow: 0 4px 14px rgba(217, 119, 6, 0.3);

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 18px rgba(217, 119, 6, 0.4);
    }
  }
}
</style>
