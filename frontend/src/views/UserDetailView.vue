<template>
  <AppLayout>

    <!-- Top Action Bar with Back button -->
    <div class="page-top">
      <div class="top-left">
        <button class="btn-back" @click="goBack" title="Orqaga">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          Foydalanuvchilar ro'yxatiga qarash
        </button>
        <h2 class="page-main-title">{{ user?.full_name || 'Foydalanuvchi Ma\'lumotlari' }}</h2>
      </div>

      <button v-if="authStore.isSuperuser && user" class="btn-edit-profile" @click="openEditModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" style="margin-right: 6px;">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
          <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
        </svg>
        Tahrirlash
      </button>
    </div>

    <!-- Loading / Error States -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">Foydalanuvchi ma'lumotlari yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchUserDetail">Qayta urinish</button>
    </div>

    <div v-else-if="user" class="detail-container">

      <!-- Profile Overview Card -->
      <div class="profile-card">
        <div class="profile-header">
          <div class="avatar-large" @click="openImageModal(user.image || '/default_photo.png')" title="Rasmni kattalashtirish" style="cursor: pointer;">
            <img :src="user.image || '/default_photo.png'" alt="Profile" class="user-avatar-img" />
          </div>
          <div class="profile-identity">
            <h3 class="profile-name">{{ user.full_name || (user.first_name + ' ' + user.last_name) }}</h3>
            <div class="role-badge-wrap">
              <span class="role-badge" :class="roleClass(user.role, user.is_superuser)">
                {{ roleText(user.role, user.is_superuser) }}
              </span>
            </div>
          </div>
        </div>

        <div class="profile-grid">
          <div class="info-item">
            <span class="info-label">Asosiy Telefon</span>
            <span class="info-value">{{ formatPhone(user.phone) }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">Qo'shimcha Telefon</span>
            <span class="info-value">{{ formatPhone(user.phone2) || '-' }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">JSHSHR</span>
            <span class="info-value">{{ user.jshshr || '-' }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">Pasport</span>
            <span class="info-value">{{ formatPassport(user.passport_serie, user.passport_number) }}</span>
          </div>

          <div class="info-item" v-if="user.role === 'instructor'">
            <span class="info-label">Guvohnoma</span>
            <span class="info-value">{{ user.license_series || user.license_number ? `${user.license_series || ''} ${user.license_number || ''}`.trim() : '-' }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">Email</span>
            <span class="info-value">{{ user.email || '-' }}</span>
          </div>

          <div class="info-item">
            <span class="info-label">Qo'shilgan sana</span>
            <span class="info-value">{{ formatDate(user.date_joined) }}</span>
          </div>
        </div>

        <div v-if="user.notes" class="notes-block">
          <span class="info-label">Qo'shimcha izoh:</span>
          <p class="notes-text">{{ user.notes }}</p>
        </div>
      </div>

      <!-- Reviews Section -->
      <div class="linked-section" v-if="user.role === 'instructor' || user.role === 'coordinator'">
        <div class="section-header">
          <h3 class="section-title">O'quvchilar Sharhlari</h3>
          <div class="section-header-right">
            <span v-if="reviews.length > 0" class="count-badge">⭐ {{ averageRating }} / 5 ({{ reviews.length }} ta sharh)</span>
            <span v-else class="count-badge">0 ta sharh</span>
            <button v-if="canLeaveReview" type="button" class="btn-leave-review-top" @click="openReviewModal">
              ⭐ Sharh qoldirish
            </button>
          </div>
        </div>

        <div v-if="loadingReviews" class="state-container">
          <div class="spinner"></div>
        </div>

        <div v-else-if="reviews.length === 0" class="empty-groups">
          <p class="empty-title">Hozircha sharhlar yo'q</p>
          <p class="empty-sub">O'quvchilar ushbu xodimga hali sharh qoldirmagan.</p>
        </div>

        <template v-else>
          <div class="table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>O'quvchi</th>
                  <th>Baho</th>
                  <th>Izoh</th>
                  <th>Sana</th>
                </tr>
                <tr class="col-filter-row">
                  <th>
                    <input v-model="reviewFilterStudentName" class="col-filter-input" type="text" placeholder="Ism bo'yicha qidirish..." />
                  </th>
                  <th></th>
                  <th></th>
                  <th>
                    <div class="col-sort-group">
                      <button type="button" class="col-sort-icon-btn" :class="{ active: reviewDateSort === 'asc' }" title="O'sish tartibida" @click="setReviewSort('asc')">
                        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M6 20V4"></path>
                          <path d="M3 8l3-4 3 4"></path>
                          <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                          <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                        </svg>
                      </button>
                      <button type="button" class="col-sort-icon-btn" :class="{ active: reviewDateSort === 'desc' }" title="Kamayish tartibida" @click="setReviewSort('desc')">
                        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M6 4v16"></path>
                          <path d="M3 16l3 4 3-4"></path>
                          <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                          <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                        </svg>
                      </button>
                      <button v-if="reviewDateFrom || reviewDateTo" type="button" class="btn-clear-date" @click="reviewDateFrom = ''; reviewDateTo = ''" title="Tozalash">✕</button>
                    </div>
                    <div class="col-date-range">
                      <input v-model="reviewDateFrom" type="date" class="col-date-input" title="Sana (dan)" />
                      <input v-model="reviewDateTo" type="date" class="col-date-input" title="Sana (gacha)" />
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="paginatedReviews.length === 0">
                  <td colspan="4" class="td-empty">Filtrlarga mos sharh topilmadi</td>
                </tr>
                <tr v-for="r in paginatedReviews" :key="r.id">
                  <td>
                    <span v-if="r.student" class="link-value" @click="goStudent(r.student)">{{ r.student_name }}</span>
                    <span v-else>{{ r.student_name }}</span>
                  </td>
                  <td class="review-row-stars">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5 - r.rating) }}</td>
                  <td class="review-row-comment">{{ r.comment || '-' }}</td>
                  <td>{{ formatDate(r.created_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pagination-bar">
            <span class="pagination-info">
              Jami: <strong>{{ filteredReviews.length }}</strong> tadan <strong>{{ filteredReviews.length > 0 ? (reviewCurrentPage - 1) * reviewPageSize + 1 : 0 }} - {{ Math.min(reviewCurrentPage * reviewPageSize, filteredReviews.length) }}</strong> ko'rsatilmoqda
            </span>
            <div class="pagination-actions">
              <button class="btn-page" :disabled="reviewCurrentPage === 1" @click="changeReviewPage(reviewCurrentPage - 1)">Oldingi</button>
              <span class="page-num">Sahifa {{ reviewCurrentPage }} / {{ reviewTotalPages }}</span>
              <button class="btn-page" :disabled="reviewCurrentPage === reviewTotalPages" @click="changeReviewPage(reviewCurrentPage + 1)">Keyingi</button>
            </div>
          </div>
        </template>
      </div>

      <!-- Assigned Car(s) — visible to everyone, including students -->
      <div class="linked-section" v-if="user.role === 'instructor'">
        <div class="section-header">
          <h3 class="section-title">Biriktirilgan Avtomobil</h3>
        </div>

        <div v-if="loadingInstructorCars" class="state-container">
          <div class="spinner"></div>
        </div>

        <template v-else>
          <div v-if="currentAssignedCar" class="current-car-card" @click="router.push(`/vehicles/${currentAssignedCar.id}`)">
            <div class="current-car-icon">🚘</div>
            <div>
              <div class="current-car-name">{{ currentAssignedCar.car_name }}</div>
              <div class="current-car-sub">{{ currentAssignedCar.manufact_year || '-' }} · <span class="current-badge">Hozirgi</span></div>
            </div>
          </div>
          <div v-else class="empty-groups">
            <p class="empty-title">Hozirda avtomobil biriktirilmagan</p>
          </div>

          <template v-if="pastAssignedCars.length > 0">
            <div class="table-wrap" style="margin-top: 14px;">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Avtomobil</th>
                    <th>Biriktirilgan sana</th>
                    <th>Ajratilgan sana</th>
                  </tr>
                  <tr class="col-filter-row">
                    <th>
                      <input v-model="carFilterName" class="col-filter-input" type="text" placeholder="Avtomobil nomi..." />
                    </th>
                    <th>
                      <div class="col-sort-group">
                        <button type="button" class="col-sort-icon-btn" :class="{ active: carAssignedSort === 'asc' }" title="O'sish tartibida" @click="setCarSort('assigned', 'asc')">
                          <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M6 20V4"></path>
                            <path d="M3 8l3-4 3 4"></path>
                            <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                            <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                          </svg>
                        </button>
                        <button type="button" class="col-sort-icon-btn" :class="{ active: carAssignedSort === 'desc' }" title="Kamayish tartibida" @click="setCarSort('assigned', 'desc')">
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
                        <button type="button" class="col-sort-icon-btn" :class="{ active: carUnassignedSort === 'asc' }" title="O'sish tartibida" @click="setCarSort('unassigned', 'asc')">
                          <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M6 20V4"></path>
                            <path d="M3 8l3-4 3 4"></path>
                            <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                            <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                          </svg>
                        </button>
                        <button type="button" class="col-sort-icon-btn" :class="{ active: carUnassignedSort === 'desc' }" title="Kamayish tartibida" @click="setCarSort('unassigned', 'desc')">
                          <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M6 4v16"></path>
                            <path d="M3 16l3 4 3-4"></path>
                            <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                            <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                          </svg>
                        </button>
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="paginatedAssignedCars.length === 0">
                    <td colspan="3" class="td-empty">Filtrlarga mos avtomobil topilmadi</td>
                  </tr>
                  <tr v-for="h in paginatedAssignedCars" :key="h.id">
                    <td class="link-value" @click="router.push(`/vehicles/${h.car.id}`)">{{ h.car.car_name }}</td>
                    <td>{{ formatDate(h.assigned_at) }}</td>
                    <td>{{ formatDate(h.unassigned_at) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="pagination-bar">
              <span class="pagination-info">
                Jami: <strong>{{ filteredAssignedCars.length }}</strong> tadan <strong>{{ filteredAssignedCars.length > 0 ? (carCurrentPage - 1) * carPageSize + 1 : 0 }} - {{ Math.min(carCurrentPage * carPageSize, filteredAssignedCars.length) }}</strong> ko'rsatilmoqda
              </span>
              <div class="pagination-actions">
                <button class="btn-page" :disabled="carCurrentPage === 1" @click="changeCarPage(carCurrentPage - 1)">Oldingi</button>
                <span class="page-num">Sahifa {{ carCurrentPage }} / {{ carTotalPages }}</span>
                <button class="btn-page" :disabled="carCurrentPage === carTotalPages" @click="changeCarPage(carCurrentPage + 1)">Keyingi</button>
              </div>
            </div>
          </template>
        </template>
      </div>

      <!-- Payments Section — staff-only, never shown to students -->
      <div class="linked-section" v-if="canSeePayments && !isAdminOrSuperuserProfile">
        <div class="section-header">
          <h3 class="section-title">To'lovlar Tarixi</h3>
          <span class="count-badge">Jami: {{ formatMoney(filteredHistoryPaymentsTotal) }}</span>
        </div>

        <div v-if="loadingPayments" class="state-container">
          <div class="spinner"></div>
        </div>

        <div v-else-if="userPayments.length === 0" class="empty-groups">
          <p class="empty-title">Hozircha to'lov yo'q</p>
          <p class="empty-sub">Ushbu foydalanuvchiga hali to'lov qilinmagan.</p>
        </div>

        <template v-else>
          <div class="payments-table-wrap">
            <table class="payments-table">
              <thead>
                <tr>
                  <th>Sana &amp; Vaqt</th>
                  <th>Turi</th>
                  <th>Summa</th>
                  <th>Usuli</th>
                  <th>Izoh</th>
                </tr>
                <tr class="col-filter-row">
                  <th>
                    <div class="col-sort-group">
                      <button type="button" class="col-sort-icon-btn" :class="{ active: histDateSort === 'asc' }" title="O'sish tartibida" @click="setHistSort('date', 'asc')">
                        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M6 20V4"></path>
                          <path d="M3 8l3-4 3 4"></path>
                          <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                          <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                        </svg>
                      </button>
                      <button type="button" class="col-sort-icon-btn" :class="{ active: histDateSort === 'desc' }" title="Kamayish tartibida" @click="setHistSort('date', 'desc')">
                        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M6 4v16"></path>
                          <path d="M3 16l3 4 3-4"></path>
                          <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                          <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                        </svg>
                      </button>
                      <button v-if="histDateFrom || histDateTo" type="button" class="btn-clear-date" @click="histDateFrom = ''; histDateTo = ''" title="Tozalash">✕</button>
                    </div>
                    <div class="col-date-range">
                      <input v-model="histDateFrom" type="date" class="col-date-input" title="Sana (dan)" />
                      <input v-model="histDateTo" type="date" class="col-date-input" title="Sana (gacha)" />
                    </div>
                  </th>
                  <th>
                    <div class="select-wrap-relative">
                      <select v-model="histStatusFilter" class="col-filter-select">
                        <option value="">Barchasi</option>
                        <option v-for="st in paymentStatusTabs" :key="st" :value="st">{{ paymentStatusText(st) }}</option>
                      </select>
                    </div>
                  </th>
                  <th>
                    <div class="col-sort-group">
                      <button type="button" class="col-sort-icon-btn" :class="{ active: histAmountSort === 'asc' }" title="O'sish tartibida" @click="setHistSort('amount', 'asc')">
                        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M6 20V4"></path>
                          <path d="M3 8l3-4 3 4"></path>
                          <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                          <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                        </svg>
                      </button>
                      <button type="button" class="col-sort-icon-btn" :class="{ active: histAmountSort === 'desc' }" title="Kamayish tartibida" @click="setHistSort('amount', 'desc')">
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
                      <select v-model="histMethodFilter" class="col-filter-select">
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
                </tr>
              </thead>
              <tbody>
                <tr v-if="paginatedHistoryPayments.length === 0">
                  <td colspan="5" class="td-empty">Filtrlarga mos to'lov topilmadi</td>
                </tr>
                <tr v-for="p in paginatedHistoryPayments" :key="p.id">
                  <td class="pay-date">{{ formatDateTime(p.created_at) }}</td>
                  <td><span class="pay-status-chip" :class="p.status">{{ paymentStatusText(p.status) }}</span></td>
                  <td class="pay-amount">{{ formatMoney(p.amount) }}</td>
                  <td class="pay-method">{{ methodText(p.method) }}</td>
                  <td class="pay-notes">{{ p.notes || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pagination-bar">
            <span class="pagination-info">
              Jami: <strong>{{ filteredHistoryPayments.length }}</strong> tadan <strong>{{ filteredHistoryPayments.length > 0 ? (histCurrentPage - 1) * histPageSize + 1 : 0 }} - {{ Math.min(histCurrentPage * histPageSize, filteredHistoryPayments.length) }}</strong> ko'rsatilmoqda
            </span>
            <div class="pagination-actions">
              <button class="btn-page" :disabled="histCurrentPage === 1" @click="changeHistPage(histCurrentPage - 1)">Oldingi</button>
              <span class="page-num">Sahifa {{ histCurrentPage }} / {{ histTotalPages }}</span>
              <button class="btn-page" :disabled="histCurrentPage === histTotalPages" @click="changeHistPage(histCurrentPage + 1)">Keyingi</button>
            </div>
          </div>
        </template>
      </div>

      <!-- Payments Section — Admin/Superuser profiles: tabbed by status, filterable, paginated -->
      <div class="linked-section" v-if="canSeePayments && isAdminOrSuperuserProfile">
        <div class="section-header">
          <h3 class="section-title">Shu {{ user.full_name || user.phone }} {{ adminProfileRoleWord }} qabul qilgan(bergan) to'lovlar tarixi</h3>
          <span class="count-badge">Jami: {{ formatMoney(filteredPaymentsTotal) }}</span>
        </div>

        <div v-if="loadingPayments" class="state-container">
          <div class="spinner"></div>
        </div>

        <template v-else>
          <div class="payment-status-tabs">
            <button
              v-for="status in paymentStatusTabs"
              :key="status"
              type="button"
              class="payment-status-tab"
              :class="{ active: activePaymentTab === status }"
              @click="selectPaymentTab(status)"
            >
              {{ paymentStatusText(status) }}
              <span class="tab-count">{{ userPayments.filter(p => p.status === status).length }}</span>
            </button>
          </div>

          <div v-if="paymentsForActiveTab.length === 0" class="empty-groups">
            <p class="empty-title">Hozircha to'lov yo'q</p>
            <p class="empty-sub">Ushbu statusda to'lov topilmadi.</p>
          </div>

          <template v-else>
            <div class="table-wrap admin-payments-table-wrap">
              <table class="data-table admin-payments-table">
                <thead>
                  <tr>
                    <th class="sticky-col">Ism</th>
                    <th>Summa</th>
                    <th>Turi</th>
                    <th>Sana &amp; Vaqt</th>
                    <th>Izoh</th>
                  </tr>
                  <tr class="col-filter-row">
                    <th class="sticky-col">
                      <input v-model="paymentFilterName" class="col-filter-input" type="text" placeholder="Ism bo'yicha qidirish..." />
                    </th>
                    <th></th>
                    <th>
                      <div class="select-wrap-relative">
                        <select v-model="paymentFilterMethod" class="col-filter-select">
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
                        <button type="button" class="col-sort-icon-btn" :class="{ active: paymentDateSort === 'asc' }" title="O'sish tartibida (eskidan yangiga)" @click="setPaymentDateSort('asc')">
                          <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M6 20V4"></path>
                            <path d="M3 8l3-4 3 4"></path>
                            <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                            <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                          </svg>
                        </button>
                        <button type="button" class="col-sort-icon-btn" :class="{ active: paymentDateSort === 'desc' }" title="Kamayish tartibida (yangidan eskiga)" @click="setPaymentDateSort('desc')">
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
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="paginatedPaymentsForActiveTab.length === 0">
                    <td colspan="5" class="td-empty">Filtrlarga mos to'lov topilmadi</td>
                  </tr>
                  <tr v-for="p in paginatedPaymentsForActiveTab" :key="p.id">
                    <td class="sticky-col">
                      <template v-if="paymentCounterpartId(p)">
                        <span class="counterpart-badge" :class="paymentCounterpartType(p)">{{ counterpartTypeLabels[paymentCounterpartType(p)] }}</span>
                        <span class="link-value" @click="goPaymentCounterpart(p)">{{ paymentCounterpartName(p) }}</span>
                      </template>
                      <span v-else>{{ paymentCounterpartName(p) }}</span>
                    </td>
                    <td>{{ formatMoney(p.amount) }}</td>
                    <td><span class="method-chip">{{ methodText(p.method) }}</span></td>
                    <td>{{ formatDateTime(p.created_at) }}</td>
                    <td>{{ p.notes || '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="pagination-bar">
              <span class="pagination-info">
                Jami: <strong>{{ filteredPaymentsForActiveTab.length }}</strong> tadan <strong>{{ filteredPaymentsForActiveTab.length > 0 ? (paymentCurrentPage - 1) * paymentPageSize + 1 : 0 }} - {{ Math.min(paymentCurrentPage * paymentPageSize, filteredPaymentsForActiveTab.length) }}</strong> ko'rsatilmoqda
              </span>
              <div class="pagination-actions">
                <button class="btn-page" :disabled="paymentCurrentPage === 1" @click="changePaymentPage(paymentCurrentPage - 1)">Oldingi</button>
                <span class="page-num">Sahifa {{ paymentCurrentPage }} / {{ paymentTotalPages }}</span>
                <button class="btn-page" :disabled="paymentCurrentPage === paymentTotalPages" @click="changePaymentPage(paymentCurrentPage + 1)">Keyingi</button>
              </div>
            </div>
          </template>
        </template>
      </div>

      <!-- Linked Students Section — teacher/instructor pages only, hidden from students -->
      <div class="linked-section" v-if="(user.role === 'instructor' || user.role === 'coordinator') && !authStore.isStudent">
        <div class="section-header">
          <h3 class="section-title">Biriktirilgan O'quvchilar</h3>
          <span class="count-badge">{{ filteredLinkedEnrollments.length }} ta o'quvchi</span>
        </div>

        <div v-if="loadingEnrollments" class="state-container">
          <div class="spinner"></div>
        </div>

        <div v-else-if="enrollments.length === 0" class="empty-groups">
          <svg viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="1.5" width="40" height="40">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
          </svg>
          <p class="empty-title">O'quvchilar topilmadi</p>
          <p class="empty-sub">Ushbu xodimga hali birorta o'quvchi biriktirilmagan yoki filtrga mos o'quvchi yo'q.</p>
        </div>

        <template v-else>
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>O'quvchi F.I.SH.</th>
                <th>Kategoriya</th>
                <th>Guruh nomi</th>
                <th>Guruh boshlanishi</th>
                <th>Guruh tugashi</th>
                <th>Holati</th>
                <th>Dars Kunlari</th>
                <th>Dars Vaqti</th>
                <th>O'quv Joyi</th>
                <th>Agent</th>
                <th>Shartnoma</th>
                <th>To'langan</th>
                <th v-if="showCoordinatorColumn">O'qituvchi</th>
                <th v-if="showInstructorColumn">Instruktor</th>
                <th>Sertifikat</th>
                <th>Imtihondan o'tganligi haqida</th>
                <th>Bonus summasi</th>
                <th>Bonus to'langan sana</th>
              </tr>
              <tr class="col-filter-row">
                <th>
                  <input v-model="studentTableSearch" class="col-filter-input" type="text" placeholder="Ism bo'yicha qidirish..." />
                </th>
                <th>
                  <div class="select-wrap-relative">
                    <select v-model="studentTableCategoryFilter" class="col-filter-select">
                      <option value="">Barchasi</option>
                      <option v-for="c in linkedCategoryOptions" :key="c.id" :value="c.id">{{ c.name }}</option>
                    </select>
                  </div>
                </th>
                <th>
                  <input v-model="studentTableGroupFilter" class="col-filter-input" type="text" placeholder="Guruh nomi..." />
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
                    <input v-model="groupStartFrom" type="date" class="col-date-input" title="Boshlanish sanasi (dan)" />
                    <input v-model="groupStartTo" type="date" class="col-date-input" title="Boshlanish sanasi (gacha)" />
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
                    <input v-model="groupEndFrom" type="date" class="col-date-input" title="Tugash sanasi (dan)" />
                    <input v-model="groupEndTo" type="date" class="col-date-input" title="Tugash sanasi (gacha)" />
                  </div>
                </th>
                <th>
                  <div class="select-wrap-relative">
                    <select v-model="filterStatus" class="col-filter-select">
                      <option value="">Barchasi</option>
                      <option value="new">Yangi</option>
                      <option value="enrolled">Faol</option>
                      <option value="finished">Tugatgan</option>
                      <option value="canceled">Bekor qilingan</option>
                    </select>
                  </div>
                </th>
                <th></th>
                <th></th>
                <th>
                  <input v-model="filterLearningPlace" class="col-filter-input" type="text" placeholder="O'quv joyi..." />
                </th>
                <th>
                  <input v-model="filterAgentName" class="col-filter-input" type="text" placeholder="Agent nomi..." />
                </th>
                <th></th>
                <th></th>
                <th v-if="showCoordinatorColumn">
                  <input v-model="filterCounterpartName" class="col-filter-input" type="text" placeholder="O'qituvchi nomi..." />
                </th>
                <th v-if="showInstructorColumn">
                  <input v-model="filterCounterpartName" class="col-filter-input" type="text" placeholder="Instruktor nomi..." />
                </th>
                <th>
                  <div class="select-wrap-relative">
                    <select v-model="filterCourseCertStatus" class="col-filter-select">
                      <option value="">Barchasi</option>
                      <option value="uploaded">Bor</option>
                      <option value="not_uploaded">Yo'q</option>
                    </select>
                  </div>
                </th>
                <th>
                  <div class="select-wrap-relative">
                    <select v-model="filterExamCertStatus" class="col-filter-select">
                      <option value="">Barchasi</option>
                      <option value="uploaded">Bor</option>
                      <option value="not_uploaded">Yo'q</option>
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
              </tr>
            </thead>
            <tbody>
              <tr v-if="paginatedLinkedEnrollments.length === 0">
                <td :colspan="studentTableColspan" class="td-empty">O'quvchilar topilmadi</td>
              </tr>
              <tr v-for="e in paginatedLinkedEnrollments" :key="e.id" class="table-row" @click="goStudent(e.student)" style="cursor: pointer;">
                <td class="td-name">
                  <div class="student-link">{{ e.student_name }}</div>
                </td>
                <td><span class="group-badge">{{ e.category_name || '-' }}</span></td>
                <td class="td-group" @click.stop>
                  <span v-if="e.group" class="link-value" @click="goGroup(e.group)">{{ e.group_name || '-' }}</span>
                  <span v-else>{{ e.group_name || '-' }}</span>
                </td>
                <td>{{ groupsById[e.group] ? formatDate(groupsById[e.group].started_at) : '-' }}</td>
                <td>{{ groupsById[e.group] ? formatDate(groupsById[e.group].ends_at) : '-' }}</td>
                <td>
                  <span class="status-chip" :class="e.status">
                    {{ statusText(e.status) }}
                  </span>
                </td>
                <td>{{ formatLearningDays(e.learning_days) }}</td>
                <td>{{ e.learning_time || '-' }}</td>
                <td>{{ e.learning_place_name || '-' }}</td>
                <td @click.stop>
                  <span v-if="e.agent" class="link-value" @click="goAgent(e.agent)">{{ e.agent_name || '-' }}</span>
                  <span v-else>{{ e.agent_name || '-' }}</span>
                </td>
                <td>
                  <span v-if="e.enrolled_free" class="free-chip">Tekin</span>
                  <span v-else>{{ formatMoney(e.enrolled_amount) }}</span>
                </td>
                <td class="text-green">{{ formatMoney(e.paid_amount || 0) }}</td>
                <td v-if="showCoordinatorColumn" @click.stop>
                  <span v-if="e.coordinator" class="link-value" @click="goUser(e.coordinator)">{{ e.coordinator_name || '-' }}</span>
                  <span v-else>{{ e.coordinator_name || '-' }}</span>
                </td>
                <td v-if="showInstructorColumn" @click.stop>
                  <span v-if="e.instructor" class="link-value" @click="goUser(e.instructor)">{{ e.instructor_name || '-' }}</span>
                  <span v-else>{{ e.instructor_name || '-' }}</span>
                </td>
                <td @click.stop>
                  <div class="assign-cell">
                    <template v-if="e.student_certificate_number">
                      <div class="assign-name-col">
                        <span class="cert-value">{{ e.student_certificate_series || '' }} {{ e.student_certificate_number }}</span>
                        <div v-if="e.student_certificate_added_date" class="cert-date-sub">{{ formatDate(e.student_certificate_added_date) }}</div>
                      </div>
                      <button v-if="authStore.isAdminOrSuperuser" type="button" class="btn-assign-edit" @click="openCourseCertModal(e)" title="Sertifikatni o'zgartirish">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                          <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                      </button>
                    </template>
                    <template v-else>
                      <button v-if="authStore.isAdminOrSuperuser" type="button" class="btn-assign-plus" @click="openCourseCertModal(e)" title="Sertifikat qo'shish">+</button>
                      <span v-else>-</span>
                    </template>
                  </div>
                </td>
                <td @click.stop>
                  <div v-if="getStudentExamCert(e.student)" class="assign-name-col">
                    <button
                      type="button"
                      class="btn-view-cert"
                      @click="openExamCertPreview(getStudentExamCert(e.student))"
                      title="Sertifikatni ko'rish"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                        <circle cx="12" cy="12" r="3"></circle>
                      </svg>
                      Ko'rish
                    </button>
                    <div v-if="getStudentExamCert(e.student).created_at" class="cert-date-sub">{{ formatDate(getStudentExamCert(e.student).created_at) }}</div>
                    <button
                      v-if="canPayBonus && !getStudentExamCert(e.student).bonus_paid"
                      type="button"
                      class="btn-pay-cert-bonus-user"
                      @click="openBonusModal(getStudentExamCert(e.student))"
                      title="Sertifikat bonusini to'lash"
                    >
                      Bonus to'lash
                    </button>
                  </div>
                  <button
                    v-else-if="canUploadExamCert"
                    type="button"
                    class="btn-assign-plus"
                    @click="openCertUploadModal(e)"
                    title="Imtihon sertifikatini yuklash"
                  >
                    +
                  </button>
                  <span v-else>-</span>
                </td>
                <td class="td-amount">{{ getStudentExamCert(e.student)?.bonus_amount != null ? formatMoney(getStudentExamCert(e.student).bonus_amount) : '-' }}</td>
                <td class="td-date">{{ getCertBonusPaymentDate(getStudentExamCert(e.student)) ? formatDate(getCertBonusPaymentDate(getStudentExamCert(e.student))) : '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination controls -->
        <div class="pagination-bar">
          <span class="pagination-info">
            Jami: <strong>{{ filteredLinkedEnrollments.length }}</strong> tadan <strong>{{ filteredLinkedEnrollments.length > 0 ? (studentTableCurrentPage - 1) * studentTablePageSize + 1 : 0 }} - {{ Math.min(studentTableCurrentPage * studentTablePageSize, filteredLinkedEnrollments.length) }}</strong> ko'rsatilmoqda
          </span>
          <div class="pagination-actions">
            <button class="btn-page" :disabled="studentTableCurrentPage === 1" @click="changeStudentTablePage(studentTableCurrentPage - 1)">Oldingi</button>
            <span class="page-num">Sahifa {{ studentTableCurrentPage }} / {{ studentTableTotalPages }}</span>
            <button class="btn-page" :disabled="studentTableCurrentPage === studentTableTotalPages" @click="changeStudentTablePage(studentTableCurrentPage + 1)">Keyingi</button>
          </div>
        </div>
        </template>
      </div>

      <!-- Yo'qlama jadvali (Davomat) — teacher (coordinator) profile only -->
      <div class="linked-section" v-if="user.role === 'coordinator' && (authStore.isAdminOrSuperuser || authStore.user?.id === user.id)">
        <div class="section-header">
          <h3 class="section-title">Yo'qlama jadvali</h3>
          <span class="count-badge">{{ sortedAttendanceEnrollments.length }} ta o'quvchi</span>
        </div>

        <div v-if="loadingEnrollments || loadingTeacherAttendance" class="state-container">
          <div class="spinner"></div>
        </div>

        <div v-else-if="enrollments.length === 0" class="empty-groups">
          <svg viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="1.5" width="40" height="40">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
          </svg>
          <p class="empty-title">O'quvchilar topilmadi</p>
          <p class="empty-sub">Ushbu o'qituvchiga hali birorta o'quvchi biriktirilmagan.</p>
        </div>

        <template v-else>
          <div class="table-wrap">
            <table class="data-table attendance-history-table">
              <thead>
                <tr>
                  <th class="davomat-frozen-col">O'quvchi F.I.SH.</th>
                  <th class="davomat-frozen-col">Guruh nomi</th>
                  <th class="davomat-frozen-col">Guruh boshlanishi</th>
                  <th class="davomat-frozen-col">Guruh tugashi</th>
                  <th class="davomat-frozen-col">Davomat hisoboti</th>
                  <th v-for="ds in attendanceAllDates" :key="ds" class="davomat-date-th">{{ dayLabel(ds) }}</th>
                </tr>
                <tr class="col-filter-row">
                  <th class="davomat-frozen-col">
                    <input v-model="attendanceTableSearch" class="col-filter-input" type="text" placeholder="Ism bo'yicha qidirish..." />
                  </th>
                  <th class="davomat-frozen-col">
                    <input v-model="attendanceTableGroupFilter" class="col-filter-input" type="text" placeholder="Guruh nomi..." />
                  </th>
                  <th class="davomat-frozen-col">
                    <div class="col-sort-group">
                      <button type="button" class="col-sort-icon-btn" :class="{ active: attendanceGroupStartSort === 'asc' }" title="O'sish tartibida (eskidan yangiga)" @click="setAttendanceSort('groupStart', 'asc')">
                        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M6 20V4"></path>
                          <path d="M3 8l3-4 3 4"></path>
                          <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                          <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                        </svg>
                      </button>
                      <button type="button" class="col-sort-icon-btn" :class="{ active: attendanceGroupStartSort === 'desc' }" title="Kamayish tartibida (yangidan eskiga)" @click="setAttendanceSort('groupStart', 'desc')">
                        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M6 4v16"></path>
                          <path d="M3 16l3 4 3-4"></path>
                          <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                          <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                        </svg>
                      </button>
                    </div>
                    <div class="col-date-range col-date-range-vertical">
                      <input v-model="attendanceGroupStartFrom" type="date" class="col-date-input" title="Boshlanish sanasi (dan)" />
                      <input v-model="attendanceGroupStartTo" type="date" class="col-date-input" title="Boshlanish sanasi (gacha)" />
                    </div>
                  </th>
                  <th class="davomat-frozen-col">
                    <div class="col-sort-group">
                      <button type="button" class="col-sort-icon-btn" :class="{ active: attendanceGroupEndSort === 'asc' }" title="O'sish tartibida (eskidan yangiga)" @click="setAttendanceSort('groupEnd', 'asc')">
                        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M6 20V4"></path>
                          <path d="M3 8l3-4 3 4"></path>
                          <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                          <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                        </svg>
                      </button>
                      <button type="button" class="col-sort-icon-btn" :class="{ active: attendanceGroupEndSort === 'desc' }" title="Kamayish tartibida (yangidan eskiga)" @click="setAttendanceSort('groupEnd', 'desc')">
                        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M6 4v16"></path>
                          <path d="M3 16l3 4 3-4"></path>
                          <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                          <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                        </svg>
                      </button>
                    </div>
                    <div class="col-date-range col-date-range-vertical">
                      <input v-model="attendanceGroupEndFrom" type="date" class="col-date-input" title="Tugash sanasi (dan)" />
                      <input v-model="attendanceGroupEndTo" type="date" class="col-date-input" title="Tugash sanasi (gacha)" />
                    </div>
                  </th>
                  <th class="davomat-frozen-col"></th>
                  <th v-for="ds in attendanceAllDates" :key="ds"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="sortedAttendanceEnrollments.length === 0">
                  <td :colspan="5 + attendanceAllDates.length" class="td-empty">Filtrlarga mos o'quvchi topilmadi</td>
                </tr>
                <tr v-for="(e, idx) in sortedAttendanceEnrollments" :key="e.id">
                  <td class="td-name davomat-frozen-col">
                    <span class="link-value" @click="goStudent(e.student)">{{ e.student_name }}</span>
                  </td>
                  <td class="davomat-frozen-col">
                    <span v-if="e.group" class="link-value" @click="goGroup(e.group)">{{ e.group_name || '-' }}</span>
                    <span v-else>{{ e.group_name || '-' }}</span>
                  </td>
                  <td class="td-date davomat-frozen-col">{{ groupsById[e.group] ? formatDate(groupsById[e.group].started_at) : '-' }}</td>
                  <td class="td-date davomat-frozen-col">{{ groupsById[e.group] ? formatDate(groupsById[e.group].ends_at) : '-' }}</td>
                  <td class="davomat-frozen-col davomat-report-cell" :title="`${attendanceReport(e).visited} kun keldi / ${attendanceReport(e).total} kundan`">
                    {{ attendanceReport(e).visited }}/{{ attendanceReport(e).total }}
                  </td>
                  <td v-for="ds in attendanceAllDates" :key="ds" class="davomat-cell">
                    <div v-if="isToday(dayFor(e, ds))" class="davomat-today-wrap">
                      <button
                        type="button"
                        class="davomat-icon-btn"
                        :class="attendanceIconClass(dayFor(e, ds))"
                        :disabled="!canMarkAttendance || !!markingAttendance[markKey(e, dayFor(e, ds))]"
                        :title="canMarkAttendance ? 'Bugungi kun uchun belgilash uchun bosing' : 'Faqat biriktirilgan o\'qituvchi yoki admin belgilashi mumkin'"
                        @click.stop="toggleMarkPopup(e, dayFor(e, ds))"
                      >{{ attendanceIconSymbol(dayFor(e, ds)) }}</button>
                      <div
                        v-if="openPopupKey === markKey(e, dayFor(e, ds))"
                        class="davomat-mark-popup"
                        :class="{ 'davomat-mark-popup-above': idx === sortedAttendanceEnrollments.length - 1 }"
                        @click.stop
                      >
                        <button type="button" class="davomat-popup-option davomat-popup-present" @click="chooseMark(e, dayFor(e, ds), false)">✓ Keldi</button>
                      </div>
                    </div>
                    <span v-else class="davomat-icon" :class="attendanceIconClass(dayFor(e, ds))">{{ attendanceIconSymbol(dayFor(e, ds)) }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </div>

      <!-- Agent sifatida biriktirilgan o'quvchilar -->
      <div class="linked-section" v-if="agentRecord">
        <div class="section-header">
          <h3 class="section-title">Agent sifatida biriktirilgan o'quvchilar</h3>
          <span class="count-badge">{{ filteredAgentReferredEnrollments.length }} ta o'quvchi</span>
        </div>

        <div v-if="loadingAgentReferred" class="state-container">
          <div class="spinner"></div>
        </div>

        <div v-else-if="agentReferredEnrollments.length === 0" class="empty-groups">
          <svg viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="1.5" width="40" height="40">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
          </svg>
          <p class="empty-title">O'quvchilar topilmadi</p>
          <p class="empty-sub">Ushbu agent orqali hali birorta o'quvchi ro'yxatdan o'tmagan yoki filtrga mos o'quvchi yo'q.</p>
        </div>

        <template v-else>
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>O'quvchi F.I.SH.</th>
                <th>Kategoriya</th>
                <th>Guruh nomi</th>
                <th>Guruh boshlanishi</th>
                <th>Guruh tugashi</th>
                <th>Holati</th>
                <th>Shartnoma</th>
                <th>To'langan</th>
              </tr>
              <tr class="col-filter-row">
                <th>
                  <input v-model="agentReferredSearch" class="col-filter-input" type="text" placeholder="Ism bo'yicha qidirish..." />
                </th>
                <th>
                  <div class="select-wrap-relative">
                    <select v-model="agentReferredCategoryFilter" class="col-filter-select">
                      <option value="">Barchasi</option>
                      <option v-for="c in linkedCategoryOptions" :key="c.id" :value="c.id">{{ c.name }}</option>
                    </select>
                  </div>
                </th>
                <th>
                  <input v-model="agentReferredGroupFilter" class="col-filter-input" type="text" placeholder="Guruh nomi..." />
                </th>
                <th>
                  <div class="col-sort-group">
                    <button type="button" class="col-sort-icon-btn" :class="{ active: agentReferredGroupStartSort === 'asc' }" title="O'sish tartibida (eskidan yangiga)" @click="setAgentReferredSort('groupStart', 'asc')">
                      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M6 20V4"></path>
                        <path d="M3 8l3-4 3 4"></path>
                        <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                        <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                      </svg>
                    </button>
                    <button type="button" class="col-sort-icon-btn" :class="{ active: agentReferredGroupStartSort === 'desc' }" title="Kamayish tartibida (yangidan eskiga)" @click="setAgentReferredSort('groupStart', 'desc')">
                      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M6 4v16"></path>
                        <path d="M3 16l3 4 3-4"></path>
                        <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                        <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                      </svg>
                    </button>
                    <button v-if="agentReferredGroupStartFrom || agentReferredGroupStartTo" type="button" class="btn-clear-date" @click="agentReferredGroupStartFrom = ''; agentReferredGroupStartTo = ''" title="Tozalash">✕</button>
                  </div>
                  <div class="col-date-range">
                    <input v-model="agentReferredGroupStartFrom" type="date" class="col-date-input" title="Boshlanish sanasi (dan)" />
                    <input v-model="agentReferredGroupStartTo" type="date" class="col-date-input" title="Boshlanish sanasi (gacha)" />
                  </div>
                </th>
                <th>
                  <div class="col-sort-group">
                    <button type="button" class="col-sort-icon-btn" :class="{ active: agentReferredGroupEndSort === 'asc' }" title="O'sish tartibida (eskidan yangiga)" @click="setAgentReferredSort('groupEnd', 'asc')">
                      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M6 20V4"></path>
                        <path d="M3 8l3-4 3 4"></path>
                        <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                        <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                      </svg>
                    </button>
                    <button type="button" class="col-sort-icon-btn" :class="{ active: agentReferredGroupEndSort === 'desc' }" title="Kamayish tartibida (yangidan eskiga)" @click="setAgentReferredSort('groupEnd', 'desc')">
                      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M6 4v16"></path>
                        <path d="M3 16l3 4 3-4"></path>
                        <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                        <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                      </svg>
                    </button>
                    <button v-if="agentReferredGroupEndFrom || agentReferredGroupEndTo" type="button" class="btn-clear-date" @click="agentReferredGroupEndFrom = ''; agentReferredGroupEndTo = ''" title="Tozalash">✕</button>
                  </div>
                  <div class="col-date-range">
                    <input v-model="agentReferredGroupEndFrom" type="date" class="col-date-input" title="Tugash sanasi (dan)" />
                    <input v-model="agentReferredGroupEndTo" type="date" class="col-date-input" title="Tugash sanasi (gacha)" />
                  </div>
                </th>
                <th>
                  <div class="select-wrap-relative">
                    <select v-model="agentReferredStatusFilter" class="col-filter-select">
                      <option value="">Barchasi</option>
                      <option value="new">Yangi</option>
                      <option value="enrolled">Faol</option>
                      <option value="finished">Tugatgan</option>
                      <option value="canceled">Bekor qilingan</option>
                    </select>
                  </div>
                </th>
                <th></th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="paginatedAgentReferredEnrollments.length === 0">
                <td colspan="8" class="td-empty">O'quvchilar topilmadi</td>
              </tr>
              <tr v-for="e in paginatedAgentReferredEnrollments" :key="e.id" class="table-row" @click="goStudent(e.student)" style="cursor: pointer;">
                <td class="td-name">
                  <div class="student-link">{{ e.student_name }}</div>
                </td>
                <td><span class="group-badge">{{ e.category_name || '-' }}</span></td>
                <td class="td-group" @click.stop>
                  <span v-if="e.group" class="link-value" @click="goGroup(e.group)">{{ e.group_name || '-' }}</span>
                  <span v-else>{{ e.group_name || '-' }}</span>
                </td>
                <td>{{ groupsById[e.group] ? formatDate(groupsById[e.group].started_at) : '-' }}</td>
                <td>{{ groupsById[e.group] ? formatDate(groupsById[e.group].ends_at) : '-' }}</td>
                <td>
                  <span class="status-chip" :class="e.status">{{ statusText(e.status) }}</span>
                </td>
                <td>
                  <span v-if="e.enrolled_free" class="free-chip">Tekin</span>
                  <span v-else>{{ formatMoney(e.enrolled_amount) }}</span>
                </td>
                <td class="text-green">{{ formatMoney(e.paid_amount || 0) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="pagination-bar" v-if="filteredAgentReferredEnrollments.length > 0">
          <span class="pagination-info">
            Jami: <strong>{{ filteredAgentReferredEnrollments.length }}</strong> tadan <strong>{{ filteredAgentReferredEnrollments.length > 0 ? (agentReferredPage - 1) * agentReferredPageSize + 1 : 0 }} - {{ Math.min(agentReferredPage * agentReferredPageSize, filteredAgentReferredEnrollments.length) }}</strong> ko'rsatilmoqda
          </span>
          <div class="pagination-actions">
            <button class="btn-page" :disabled="agentReferredPage === 1" @click="agentReferredPage--">Oldingi</button>
            <span class="page-num">Sahifa {{ agentReferredPage }} / {{ agentReferredTotalPages }}</span>
            <button class="btn-page" :disabled="agentReferredPage === agentReferredTotalPages" @click="agentReferredPage++">Keyingi</button>
          </div>
        </div>
        </template>
      </div>

      <!-- Amaliy darslar tarixi (instructor only) -->
      <div class="linked-section" v-if="user.role === 'instructor'">
        <div class="section-header">
          <h3 class="section-title">Amaliy darslar tarixi</h3>
          <span class="count-badge">{{ filteredInstructorLessonStudents.length }} ta o'quvchi</span>
        </div>

        <div v-if="loadingInstructorLessons" class="state-container">
          <div class="spinner"></div>
        </div>

        <div v-else-if="instructorLessonRows.length === 0" class="empty-groups">
          <svg viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="1.5" width="40" height="40">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
          <p class="empty-title">O'quvchilar topilmadi</p>
          <p class="empty-sub">Ushbu instruktor hali birorta o'quvchi bilan amaliy dars o'tkazmagan yoki filtrga mos o'quvchi yo'q.</p>
        </div>

        <template v-else>
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>O'quvchi F.I.SH.</th>
                <th>Kategoriya</th>
                <th>Guruh nomi</th>
                <th>Guruh boshlanishi</th>
                <th>Guruh tugashi</th>
                <th>Holati</th>
                <th>Darslar soni</th>
                <th>Oxirgi dars sanasi</th>
              </tr>
              <tr class="col-filter-row">
                <th>
                  <input v-model="instructorLessonSearch" class="col-filter-input" type="text" placeholder="Ism bo'yicha qidirish..." />
                </th>
                <th>
                  <div class="select-wrap-relative">
                    <select v-model="instructorLessonCategoryFilter" class="col-filter-select">
                      <option value="">Barchasi</option>
                      <option v-for="c in linkedCategoryOptions" :key="c.id" :value="c.id">{{ c.name }}</option>
                    </select>
                  </div>
                </th>
                <th>
                  <input v-model="instructorLessonGroupFilter" class="col-filter-input" type="text" placeholder="Guruh nomi..." />
                </th>
                <th>
                  <div class="col-sort-group">
                    <button type="button" class="col-sort-icon-btn" :class="{ active: instructorGroupStartSort === 'asc' }" title="O'sish tartibida (eskidan yangiga)" @click="setInstructorLessonSort('groupStart', 'asc')">
                      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M6 20V4"></path>
                        <path d="M3 8l3-4 3 4"></path>
                        <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                        <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                      </svg>
                    </button>
                    <button type="button" class="col-sort-icon-btn" :class="{ active: instructorGroupStartSort === 'desc' }" title="Kamayish tartibida (yangidan eskiga)" @click="setInstructorLessonSort('groupStart', 'desc')">
                      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M6 4v16"></path>
                        <path d="M3 16l3 4 3-4"></path>
                        <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                        <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                      </svg>
                    </button>
                    <button v-if="instructorGroupStartFrom || instructorGroupStartTo" type="button" class="btn-clear-date" @click="instructorGroupStartFrom = ''; instructorGroupStartTo = ''" title="Tozalash">✕</button>
                  </div>
                  <div class="col-date-range">
                    <input v-model="instructorGroupStartFrom" type="date" class="col-date-input" title="Boshlanish sanasi (dan)" />
                    <input v-model="instructorGroupStartTo" type="date" class="col-date-input" title="Boshlanish sanasi (gacha)" />
                  </div>
                </th>
                <th>
                  <div class="col-sort-group">
                    <button type="button" class="col-sort-icon-btn" :class="{ active: instructorGroupEndSort === 'asc' }" title="O'sish tartibida (eskidan yangiga)" @click="setInstructorLessonSort('groupEnd', 'asc')">
                      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M6 20V4"></path>
                        <path d="M3 8l3-4 3 4"></path>
                        <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                        <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                      </svg>
                    </button>
                    <button type="button" class="col-sort-icon-btn" :class="{ active: instructorGroupEndSort === 'desc' }" title="Kamayish tartibida (yangidan eskiga)" @click="setInstructorLessonSort('groupEnd', 'desc')">
                      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M6 4v16"></path>
                        <path d="M3 16l3 4 3-4"></path>
                        <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                        <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                      </svg>
                    </button>
                    <button v-if="instructorGroupEndFrom || instructorGroupEndTo" type="button" class="btn-clear-date" @click="instructorGroupEndFrom = ''; instructorGroupEndTo = ''" title="Tozalash">✕</button>
                  </div>
                  <div class="col-date-range">
                    <input v-model="instructorGroupEndFrom" type="date" class="col-date-input" title="Tugash sanasi (dan)" />
                    <input v-model="instructorGroupEndTo" type="date" class="col-date-input" title="Tugash sanasi (gacha)" />
                  </div>
                </th>
                <th></th>
                <th></th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="paginatedInstructorLessonStudents.length === 0">
                <td colspan="8" class="td-empty">O'quvchilar topilmadi</td>
              </tr>
              <tr v-for="row in paginatedInstructorLessonStudents" :key="row.student" class="table-row" @click="goStudent(row.student)" style="cursor: pointer;">
                <td class="td-name">
                  <div class="student-link">{{ row.student_name }}</div>
                </td>
                <td><span class="group-badge">{{ row.category_name || '-' }}</span></td>
                <td class="td-group" @click.stop>
                  <span v-if="row.group" class="link-value" @click="goGroup(row.group)">{{ row.group_name || '-' }}</span>
                  <span v-else>{{ row.group_name || '-' }}</span>
                </td>
                <td>{{ groupsById[row.group] ? formatDate(groupsById[row.group].started_at) : '-' }}</td>
                <td>{{ groupsById[row.group] ? formatDate(groupsById[row.group].ends_at) : '-' }}</td>
                <td>
                  <span v-if="row.status" class="status-chip" :class="row.status">{{ statusText(row.status) }}</span>
                  <span v-else>-</span>
                </td>
                <td>{{ row.lessonCount }}</td>
                <td>{{ row.lastLessonDate ? formatDate(row.lastLessonDate) : '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="pagination-bar" v-if="filteredInstructorLessonStudents.length > 0">
          <span class="pagination-info">
            Jami: <strong>{{ filteredInstructorLessonStudents.length }}</strong> tadan <strong>{{ filteredInstructorLessonStudents.length > 0 ? (instructorLessonPage - 1) * instructorLessonPageSize + 1 : 0 }} - {{ Math.min(instructorLessonPage * instructorLessonPageSize, filteredInstructorLessonStudents.length) }}</strong> ko'rsatilmoqda
          </span>
          <div class="pagination-actions">
            <button class="btn-page" :disabled="instructorLessonPage === 1" @click="instructorLessonPage--">Oldingi</button>
            <span class="page-num">Sahifa {{ instructorLessonPage }} / {{ instructorLessonTotalPages }}</span>
            <button class="btn-page" :disabled="instructorLessonPage === instructorLessonTotalPages" @click="instructorLessonPage++">Keyingi</button>
          </div>
        </div>
        </template>
      </div>

    </div>

    <!-- Edit User Modal -->
    <dialog ref="userModal" class="modal-dialog" closedby="any" @click="onDialogBackdropClick($event, userModal)">
      <div class="user-modal-header">
        <div class="header-badge-wrap">
          <div class="header-badge-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="2" width="22" height="22">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
          <div>
            <h3 class="user-modal-title">Foydalanuvchini Tahrirlash</h3>
            <p class="user-modal-sub">Profil ma'lumotlarini yangilang</p>
          </div>
        </div>
        <button class="user-btn-close" @click="closeModal" title="Yopish">✕</button>
      </div>

      <form @submit.prevent="saveUser" class="user-modal-form">
        <div v-if="modalError" class="modal-alert modal-alert-error">
          <span>{{ modalError }}</span>
        </div>

        <div class="form-group">
          <label class="form-label required">To'liq ismi (F.I.SH.)</label>
          <input v-model="editForm.full_name" type="text" class="form-input" required />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label required">Telefon raqami</label>
            <input
              v-model="editForm.phone"
              type="tel"
              class="form-input"
              placeholder="+998 90 900 90 90"
              required
              @input="onEditPhoneInput"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Qo'shimcha telefon</label>
            <input v-model="editForm.phone2" type="text" class="form-input" placeholder="+998 90 900 90 90" @input="onEditPhone2Input" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Filial</label>
          <select v-model="editForm.branch" class="form-input">
            <option :value="null">&lt; Filial biriktirilmagan &gt;</option>
            <option v-for="b in branchStore.branches" :key="b.id" :value="b.id">{{ b.name }}</option>
          </select>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">JSHSHR</label>
            <input v-model="editForm.jshshr" type="number" class="form-input" />
          </div>

          <div class="form-group">
            <label class="form-label">Roli</label>
            <select v-model="editForm.role" class="form-input">
              <option value="instructor">Instruktor</option>
              <option value="coordinator">O'qituvchi</option>
              <option value="mechanic">Mexanik</option>
              <option value="admin">Admin</option>
              <option value="superuser">Superuser</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Pasport seriyasi</label>
            <input v-model="editForm.passport_serie" type="text" maxlength="2" class="form-input" placeholder="AA" />
          </div>

          <div class="form-group">
            <label class="form-label">Pasport raqami</label>
            <input v-model="editForm.passport_number" type="number" class="form-input" placeholder="1234567" />
          </div>
        </div>

        <div class="form-row" v-if="editForm.role === 'instructor'">
          <div class="form-group">
            <label class="form-label">Guvohnoma seriyasi</label>
            <input v-model="editForm.license_series" type="text" maxlength="2" class="form-input" placeholder="AA" @input="editForm.license_series = editForm.license_series.toUpperCase()" />
          </div>

          <div class="form-group">
            <label class="form-label">Guvohnoma raqami</label>
            <input v-model="editForm.license_number" type="text" maxlength="6" class="form-input" placeholder="123456" @input="editForm.license_number = editForm.license_number.replace(/\D/g, '')" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Yangi parol</label>
            <input v-model="editForm.password" type="password" class="form-input" placeholder="O'zgartirmaslik uchun bo'sh qoldiring" autocomplete="new-password" />
          </div>

          <div class="form-group">
            <label class="form-label">Parolni tasdiqlash</label>
            <input v-model="editForm.passwordConfirm" type="password" class="form-input" placeholder="Yangi parolni qayta kiriting" autocomplete="new-password" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Foydalanuvchi Rasmi (Foto)</label>
          <div style="display: flex; align-items: center; gap: 12px; width: 100%;">
            <img v-if="editForm.existingImage" :src="editForm.existingImage" alt="Current Photo" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover; border: 1px solid #E5E7EB; flex-shrink: 0;" />
            <FileSelectInput ref="userFileInputRef" accept="image/jpeg,image/png" @change="onUserFileChange" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Qo'shimcha izoh</label>
          <textarea v-model="editForm.notes" rows="3" class="form-input form-textarea"></textarea>
        </div>

        <div class="user-modal-footer">
          <button type="button" class="btn-cancel" @click="closeModal">Bekor qilish</button>
          <button type="submit" class="btn-submit" :disabled="saving">
            {{ saving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Leave Review Modal -->
    <dialog ref="reviewModal" class="modal-dialog modal-sm" closedby="any">
      <form class="user-modal-form" @submit.prevent="submitReview">
        <div class="user-modal-header">
          <div class="header-badge-wrap">
            <div>
              <h3 class="user-modal-title">Sharh qoldirish: {{ user?.full_name || user?.phone }}</h3>
            </div>
          </div>
          <button type="button" class="user-btn-close" @click="reviewModal?.close()">✕</button>
        </div>
        <div v-if="reviewError" class="modal-alert modal-alert-error"><span>{{ reviewError }}</span></div>

        <div class="form-group">
          <label class="form-label">Baho</label>
          <div class="star-picker">
            <span
              v-for="n in 5"
              :key="n"
              class="star"
              :class="{ filled: n <= reviewForm.rating }"
              @click="reviewForm.rating = n"
            >★</span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Izoh (ixtiyoriy)</label>
          <textarea v-model="reviewForm.comment" rows="3" class="form-input form-textarea"></textarea>
        </div>

        <div class="user-modal-footer">
          <button type="button" class="btn-cancel" @click="reviewModal?.close()">Bekor qilish</button>
          <button type="submit" class="btn-submit" :disabled="reviewSaving">
            {{ reviewSaving ? 'Yuborilmoqda...' : 'Yuborish' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Pay Certificate Bonus Modal -->
    <dialog ref="bonusModal" class="modal-dialog modal-sm" closedby="any" @click="onDialogBackdropClick($event, bonusModal)">
      <form class="user-modal-form" @submit.prevent="submitCertBonus">
        <div class="user-modal-header">
          <div class="header-badge-wrap">
            <div>
              <h3 class="user-modal-title">Sertifikat Bonusini To'lash</h3>
              <p class="user-modal-sub" v-if="bonusTarget">{{ bonusTarget.student_name }}</p>
            </div>
          </div>
          <button type="button" class="user-btn-close" @click="bonusModal?.close()">✕</button>
        </div>
        <div v-if="bonusError" class="modal-alert modal-alert-error"><span>{{ bonusError }}</span></div>

        <div v-if="bonusTarget" class="pay-info-summary">
          <p>O'qituvchi: <strong>{{ user?.full_name || user?.phone }}</strong></p>
          <p v-if="bonusTarget.created_at">Sertifikat yuklangan sana: <strong>{{ formatDate(bonusTarget.created_at) }}</strong></p>
        </div>

        <div class="form-group">
          <label class="form-label">Summa</label>
          <input v-model="bonusForm.amountFormatted" type="text" class="form-input" placeholder="0" required @input="onBonusFormAmountInput" />
        </div>

        <div class="form-group">
          <label class="form-label">To'lov usuli</label>
          <select v-model="bonusForm.method" class="form-input">
            <option value="cash">Naqd</option>
            <option value="card">Karta</option>
            <option value="qr_code">QR code</option>
            <option value="click">Click</option>
            <option value="transfer">O'tkazma</option>
          </select>
        </div>

        <div class="user-modal-footer">
          <button type="button" class="btn-cancel" @click="bonusModal?.close()">Bekor qilish</button>
          <button type="submit" class="btn-submit" :disabled="bonusSaving">
            {{ bonusSaving ? 'Saqlanmoqda...' : "To'lash" }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Certificate Upload Modal (for a specific linked student) -->
    <dialog ref="certUploadModal" class="modal-dialog modal-sm" closedby="any" @click="onDialogBackdropClick($event, certUploadModal)">
      <form class="user-modal-form" @submit.prevent="submitCertUpload">
        <div class="user-modal-header">
          <div class="header-badge-wrap">
            <div>
              <h3 class="user-modal-title">Imtihondan o'tganligi haqida qo'shish</h3>
              <p class="user-modal-sub" v-if="certUploadTarget">{{ certUploadTarget.student_name }}</p>
            </div>
          </div>
          <button type="button" class="user-btn-close" @click="closeCertUploadModal">✕</button>
        </div>
        <div v-if="certUploadError" class="modal-alert modal-alert-error"><span>{{ certUploadError }}</span></div>

        <div class="form-group">
          <label class="form-label required">Rasm</label>
          <FileSelectInput ref="certUploadFileInputRef" accept="image/jpeg,image/png" required @change="onCertUploadFileChange" />
        </div>

        <div class="form-group">
          <label class="form-label">Izoh (ixtiyoriy)</label>
          <input v-model="certUploadNotes" type="text" placeholder="Izoh..." class="form-input" />
        </div>

        <div class="user-modal-footer">
          <button type="button" class="btn-cancel" @click="closeCertUploadModal">Bekor qilish</button>
          <button type="submit" class="btn-submit" :disabled="certUploadSaving || !certUploadFile">
            {{ certUploadSaving ? 'Yuklanmoqda...' : 'Yuklash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Course-Completion Certificate Modal (series/number — dedicated, not the full edit modal) -->
    <dialog ref="courseCertModal" class="modal-dialog modal-sm" closedby="any" @click="onDialogBackdropClick($event, courseCertModal)">
      <form class="user-modal-form" @submit.prevent="submitCourseCert">
        <div class="user-modal-header">
          <div class="header-badge-wrap">
            <div>
              <h3 class="user-modal-title">Kursni Tugatganlik Sertifikati</h3>
              <p class="user-modal-sub" v-if="courseCertTarget">{{ courseCertTarget.student_name }}</p>
            </div>
          </div>
          <button type="button" class="user-btn-close" @click="closeCourseCertModal">✕</button>
        </div>
        <div v-if="courseCertError" class="modal-alert modal-alert-error"><span>{{ courseCertError }}</span></div>

        <div class="form-group">
          <label class="form-label required">Seriya</label>
          <input v-model="courseCertForm.certificate_series" type="text" maxlength="2" class="form-input" placeholder="AB" style="text-transform: uppercase;" />
        </div>

        <div class="form-group">
          <label class="form-label required">Raqami</label>
          <input v-model="courseCertForm.certificate_number" type="text" maxlength="9" class="form-input" placeholder="9 ta raqam" />
        </div>

        <div class="user-modal-footer">
          <button type="button" class="btn-cancel" @click="closeCourseCertModal">Bekor qilish</button>
          <button type="submit" class="btn-submit" :disabled="courseCertSaving">
            {{ courseCertSaving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Image Zoom Modal -->
    <dialog ref="imageZoomModal" class="image-zoom-dialog" @click="imageZoomModal?.close()">
      <div class="image-zoom-content" @click.stop>
        <button type="button" class="image-zoom-close" @click="imageZoomModal?.close()">✕</button>
        <img :src="zoomedImageUrl" alt="Enlarged Photo" class="zoomed-img" />
      </div>
    </dialog>

    <!-- Exam-Pass Certificate Preview Modal -->
    <dialog ref="examCertPreviewModal" class="modal-dialog cert-preview-dialog" closedby="any" @click="onDialogBackdropClick($event, examCertPreviewModal)">
      <div class="user-modal-header">
        <div class="header-badge-wrap">
          <div>
            <h3 class="user-modal-title">Imtihon Sertifikati</h3>
          </div>
        </div>
        <button type="button" class="user-btn-close" @click="examCertPreviewModal?.close()">✕</button>
      </div>
      <div class="cert-preview-body">
        <img
          v-if="previewingExamCert?.image"
          :src="previewingExamCert.image"
          alt="Imtihon sertifikati"
          class="cert-preview-img"
        />
        <p v-if="previewingExamCert?.notes" class="cert-preview-notes">{{ previewingExamCert.notes }}</p>
      </div>
    </dialog>

  </AppLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import FileSelectInput from '@/components/FileSelectInput.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useBranchStore } from '@/stores/branch'
import { formatPhone, formatPhoneInput, formatPassport, formatDate, formatMoney, formatLearningDays } from '@/utils/formatters'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const branchStore = useBranchStore()

const user = ref(null)
const loading = ref(true)
const error = ref(null)

const enrollments = ref([])
const loadingEnrollments = ref(false)
const groups = ref([])

// ── Assigned car(s) — current + history, visible to students too ──
const instructorCars = ref([])
const loadingInstructorCars = ref(false)

async function fetchInstructorCars() {
  if (!user.value || user.value.role !== 'instructor') return
  loadingInstructorCars.value = true
  try {
    const res = await api.get('/cars/', { params: { page_size: 1000 } })
    instructorCars.value = res.data.results || res.data || []
  } catch (err) {
    console.error("Avtomobil ma'lumotlarini yuklashda xatolik:", err)
  } finally {
    loadingInstructorCars.value = false
  }
}

const currentAssignedCar = computed(() => instructorCars.value.find(c => c.instructor === user.value?.id) || null)

const pastAssignedCars = computed(() => {
  const rows = []
  instructorCars.value.forEach(c => {
    (c.assignment_history || []).forEach(h => {
      if (h.instructor === user.value?.id && h.unassigned_at) {
        rows.push({ ...h, car: c })
      }
    })
  })
  return rows.sort((a, b) => new Date(b.unassigned_at) - new Date(a.unassigned_at))
})

// ── Header-column filter/sort/pagination for the assigned-car history table ──
const carFilterName = ref('')
const carAssignedSort = ref('')
const carUnassignedSort = ref('')

const carSortRefs = { assigned: carAssignedSort, unassigned: carUnassignedSort }
function setCarSort(column, direction) {
  const target = carSortRefs[column]
  Object.values(carSortRefs).forEach(r => { if (r !== target) r.value = '' })
  target.value = target.value === direction ? '' : direction
}

const filteredAssignedCars = computed(() => {
  const q = carFilterName.value.trim().toLowerCase()
  let list = pastAssignedCars.value.filter(h => !q || (h.car.car_name || '').toLowerCase().includes(q))
  if (carAssignedSort.value) {
    const dir = carAssignedSort.value === 'asc' ? 1 : -1
    list = [...list].sort((a, b) => (new Date(a.assigned_at).getTime() - new Date(b.assigned_at).getTime()) * dir)
  } else if (carUnassignedSort.value) {
    const dir = carUnassignedSort.value === 'asc' ? 1 : -1
    list = [...list].sort((a, b) => (new Date(a.unassigned_at).getTime() - new Date(b.unassigned_at).getTime()) * dir)
  }
  return list
})

const carPageSize = 10
const carCurrentPage = ref(1)
const carTotalPages = computed(() => Math.max(1, Math.ceil(filteredAssignedCars.value.length / carPageSize)))
const paginatedAssignedCars = computed(() => {
  const start = (carCurrentPage.value - 1) * carPageSize
  return filteredAssignedCars.value.slice(start, start + carPageSize)
})
function changeCarPage(p) {
  if (p < 1 || p > carTotalPages.value) return
  carCurrentPage.value = p
}
watch([carFilterName, carAssignedSort, carUnassignedSort], () => {
  carCurrentPage.value = 1
})

const groupsById = computed(() => {
  const map = {}
  groups.value.forEach(g => { map[g.id] = g })
  return map
})

async function fetchGroupsForSchedule() {
  try {
    const res = await api.get('/groups/', { params: { page_size: 1000 } })
    groups.value = res.data.results ? res.data.results : (res.data || [])
  } catch (err) {
    console.error("Guruhlarni yuklashda xatolik:", err)
  }
}

// Four separate tables below (student list, davomat, agent-referred, and
// instructor lesson history) all read a group's started_at/ends_at via
// groupsById — but each is its own independent, unawaited fetch. Without
// this, each table's own loading flag flips off as soon as its own request
// resolves, the table renders with groupsById still empty, and the group
// start/end cells briefly show "-" until the separate /groups/ request
// (fired in parallel, not coordinated with any of them) finishes a moment
// later — a visible pop-in, not real backend slowness. Memoizing the
// promise here lets every consumer await the same in-flight request and
// only reveal its table once its own data AND groups are both ready.
let groupsLoadPromise = null
function ensureGroupsLoaded() {
  if (!groupsLoadPromise) groupsLoadPromise = fetchGroupsForSchedule()
  return groupsLoadPromise
}

// Driven by the page's own role (the profile being viewed), not the
// viewer's: an instructor's page shows the counterpart teacher column,
// a teacher's (coordinator's) page shows the counterpart instructor column.
const showCoordinatorColumn = computed(() => user.value?.role === 'instructor')
const showInstructorColumn = computed(() => user.value?.role === 'coordinator')

// Exam-pass certificate uploads are restricted to the teacher (coordinator)
// role, plus superuser — regardless of whose detail page is viewed.
const canUploadExamCert = computed(() => !!(
  authStore.user?.role === 'coordinator' || authStore.isSuperuser
))

const reviews = ref([])
const loadingReviews = ref(false)

// ── Payments made to this teacher/instructor ──────────────────
// Students must never see staff payment figures, so the whole section is
// gated on the viewer not being a student.
const userPayments = ref([])
const loadingPayments = ref(false)
const canSeePayments = computed(() => !!(authStore.user && !authStore.isStudent))
// ── Header-column filters/sort/pagination for the simple (non-admin)
// payments-history table ──
const histDateSort = ref('')
const histAmountSort = ref('')
const histStatusFilter = ref('')
const histMethodFilter = ref('')
const histDateFrom = ref('')
const histDateTo = ref('')

const histSortRefs = { date: histDateSort, amount: histAmountSort }
function setHistSort(column, direction) {
  const target = histSortRefs[column]
  Object.values(histSortRefs).forEach(r => { if (r !== target) r.value = '' })
  target.value = target.value === direction ? '' : direction
}

const filteredHistoryPayments = computed(() => {
  let list = userPayments.value.filter(p => {
    if (histStatusFilter.value && p.status !== histStatusFilter.value) return false
    if (histMethodFilter.value && p.method !== histMethodFilter.value) return false
    if (histDateFrom.value && !(p.created_at && p.created_at.slice(0, 10) >= histDateFrom.value)) return false
    if (histDateTo.value && !(p.created_at && p.created_at.slice(0, 10) <= histDateTo.value)) return false
    return true
  })
  if (histDateSort.value) {
    const dir = histDateSort.value === 'asc' ? 1 : -1
    list = [...list].sort((a, b) => (new Date(a.created_at).getTime() - new Date(b.created_at).getTime()) * dir)
  } else if (histAmountSort.value) {
    const dir = histAmountSort.value === 'asc' ? 1 : -1
    list = [...list].sort((a, b) => ((Number(a.amount) || 0) - (Number(b.amount) || 0)) * dir)
  }
  return list
})

const filteredHistoryPaymentsTotal = computed(() =>
  filteredHistoryPayments.value.reduce((sum, p) => sum + (Number(p.amount) || 0), 0)
)

const histPageSize = 10
const histCurrentPage = ref(1)
const histTotalPages = computed(() => Math.max(1, Math.ceil(filteredHistoryPayments.value.length / histPageSize)))
const paginatedHistoryPayments = computed(() => {
  const start = (histCurrentPage.value - 1) * histPageSize
  return filteredHistoryPayments.value.slice(start, start + histPageSize)
})
function changeHistPage(p) {
  if (p < 1 || p > histTotalPages.value) return
  histCurrentPage.value = p
}
watch([histStatusFilter, histMethodFilter, histDateSort, histAmountSort, histDateFrom, histDateTo], () => {
  histCurrentPage.value = 1
})

async function fetchUserPayments() {
  if (!user.value || !canSeePayments.value) return
  loadingPayments.value = true
  try {
    // On a teacher/instructor's own profile "user" is the payout recipient
    // (this page), so payments-made-to-them are found via that field. On an
    // admin/superuser's profile there's no recipient concept — it's about
    // which payments they themselves recorded, tracked by "created_by".
    const paramKey = isAdminOrSuperuserProfile.value ? 'created_by' : 'user'
    const res = await api.get('/payments/', { params: { [paramKey]: user.value.id, page_size: 500 } })
    userPayments.value = res.data.results ? res.data.results : (res.data || [])
  } catch (err) {
    console.error("To'lovlarni yuklashda xatolik:", err)
  } finally {
    loadingPayments.value = false
  }
}

// ── Admin/Superuser profile page: payments-received table is tabbed by
// status, filterable, and paginated per tab (unlike the plain "last 5"
// list shown on every other role's profile). ──
const isAdminOrSuperuserProfile = computed(() => user.value?.role === 'admin' || user.value?.role === 'superuser')
// Shown in the section title instead of the literal "admin/superuser" —
// only the profile's actual role.
const adminProfileRoleWord = computed(() => user.value?.role === 'admin' ? 'admin' : (user.value?.role === 'superuser' ? 'superuser' : ''))

const paymentStatusTabs = ['accepted', 'returned', 'paid', 'bonus', 'bank', 'bonus_teacher']
const activePaymentTab = ref('accepted')

const counterpartTypeLabels = { student: "O'quvchi", agent: 'Agent', teacher: "O'qituvchi", instructor: 'Instruktor' }

// A payment's counterpart depends on its status: agent bonuses name an
// agent, teacher/instructor payouts name that staff member (via the
// payment's own user/user_role, since that's who "user" is for those
// statuses), everything else names the student.
function paymentCounterpartType(p) {
  if (p.agent) return 'agent'
  if (p.user_role === 'instructor') return 'instructor'
  if (p.user_role === 'coordinator') return 'teacher'
  if (p.student) return 'student'
  return null
}

function paymentCounterpartId(p) {
  const type = paymentCounterpartType(p)
  if (type === 'agent') return p.agent
  if (type === 'teacher' || type === 'instructor') return p.user
  if (type === 'student') return p.student
  return null
}

function paymentCounterpartName(p) {
  const type = paymentCounterpartType(p)
  if (type === 'agent') return p.agent_name || '-'
  if (type === 'teacher' || type === 'instructor') return p.user_full_name || p.cashier_name || '-'
  if (type === 'student') return p.student_name || '-'
  return p.notes || '-'
}

function goPaymentCounterpart(p) {
  const type = paymentCounterpartType(p)
  const id = paymentCounterpartId(p)
  if (!id) return
  if (type === 'agent') router.push(`/agents/${id}`)
  else if (type === 'student') router.push(`/students/${id}`)
  else router.push(`/users/${id}`)
}

const paymentsForActiveTab = computed(() => userPayments.value.filter(p => p.status === activePaymentTab.value))

const paymentFilterName = ref('')
const paymentFilterMethod = ref('')
const paymentDateSort = ref('')
const paymentDateFrom = ref('')
const paymentDateTo = ref('')

function setPaymentDateSort(dir) {
  paymentDateSort.value = paymentDateSort.value === dir ? '' : dir
}

const filteredPaymentsForActiveTab = computed(() => {
  const name = paymentFilterName.value.trim().toLowerCase()
  let list = paymentsForActiveTab.value.filter(p => {
    if (name && !paymentCounterpartName(p).toLowerCase().includes(name)) return false
    if (paymentFilterMethod.value && p.method !== paymentFilterMethod.value) return false
    if (paymentDateFrom.value && !(p.created_at && p.created_at.slice(0, 10) >= paymentDateFrom.value)) return false
    if (paymentDateTo.value && !(p.created_at && p.created_at.slice(0, 10) <= paymentDateTo.value)) return false
    return true
  })
  if (paymentDateSort.value) {
    list = [...list].sort((a, b) => {
      const da = new Date(a.created_at).getTime()
      const db = new Date(b.created_at).getTime()
      return paymentDateSort.value === 'asc' ? da - db : db - da
    })
  }
  return list
})

// The "Jami" badge must track whatever the current tab + filters are
// actually showing, not the profile's overall total.
const filteredPaymentsTotal = computed(() =>
  filteredPaymentsForActiveTab.value.reduce((sum, p) => sum + (Number(p.amount) || 0), 0)
)

// Each status tab keeps its own page number so switching tabs doesn't lose
// the reader's place in a different tab.
const paymentPageSize = 10
const paymentPageByTab = ref({})
const paymentCurrentPage = computed({
  get: () => paymentPageByTab.value[activePaymentTab.value] || 1,
  set: (v) => { paymentPageByTab.value[activePaymentTab.value] = v },
})
const paymentTotalPages = computed(() => Math.max(1, Math.ceil(filteredPaymentsForActiveTab.value.length / paymentPageSize)))
const paginatedPaymentsForActiveTab = computed(() => {
  const start = (paymentCurrentPage.value - 1) * paymentPageSize
  return filteredPaymentsForActiveTab.value.slice(start, start + paymentPageSize)
})

function changePaymentPage(p) {
  if (p < 1 || p > paymentTotalPages.value) return
  paymentCurrentPage.value = p
}

function selectPaymentTab(status) {
  activePaymentTab.value = status
}

watch([paymentFilterName, paymentFilterMethod, paymentDateSort, paymentDateFrom, paymentDateTo], () => {
  paymentPageByTab.value[activePaymentTab.value] = 1
})

function paymentStatusText(st) {
  switch (st) {
    case 'accepted': return 'Qabul qilingan'
    case 'returned': return 'Qaytarilgan'
    case 'paid': return "To'langan"
    case 'bonus': return 'Bonus'
    case 'bank': return 'Bank'
    case 'bonus_teacher': return "Sertifikat bonusi"
    default: return st
  }
}

function methodText(m) {
  switch (m) {
    case 'cash': return 'Naqd'
    case 'card': return 'Karta'
    case 'qr_code': return 'QR code'
    case 'click': return 'Click'
    case 'transfer': return "O'tkazma"
    default: return m || '-'
  }
}

function formatDateTime(dtStr) {
  if (!dtStr) return '-'
  const d = new Date(dtStr)
  if (isNaN(d.getTime())) return dtStr
  return `${d.toLocaleDateString('uz-UZ')} ${d.toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' })}`
}

const averageRating = computed(() => {
  if (reviews.value.length === 0) return '0.0'
  const sum = reviews.value.reduce((acc, r) => acc + (r.rating || 0), 0)
  return (sum / reviews.value.length).toFixed(1)
})

// ── Header-column filter/sort/pagination for the reviews table ──
const reviewFilterStudentName = ref('')
const reviewDateSort = ref('')
const reviewDateFrom = ref('')
const reviewDateTo = ref('')
function setReviewSort(direction) {
  reviewDateSort.value = reviewDateSort.value === direction ? '' : direction
}

const filteredReviews = computed(() => {
  const q = reviewFilterStudentName.value.trim().toLowerCase()
  let list = reviews.value.filter(r => {
    if (q && !(r.student_name || '').toLowerCase().includes(q)) return false
    if (reviewDateFrom.value && !(r.created_at && r.created_at.slice(0, 10) >= reviewDateFrom.value)) return false
    if (reviewDateTo.value && !(r.created_at && r.created_at.slice(0, 10) <= reviewDateTo.value)) return false
    return true
  })
  if (reviewDateSort.value) {
    const dir = reviewDateSort.value === 'asc' ? 1 : -1
    list = [...list].sort((a, b) => (new Date(a.created_at).getTime() - new Date(b.created_at).getTime()) * dir)
  }
  return list
})

const reviewPageSize = 10
const reviewCurrentPage = ref(1)
const reviewTotalPages = computed(() => Math.max(1, Math.ceil(filteredReviews.value.length / reviewPageSize)))
const paginatedReviews = computed(() => {
  const start = (reviewCurrentPage.value - 1) * reviewPageSize
  return filteredReviews.value.slice(start, start + reviewPageSize)
})
function changeReviewPage(p) {
  if (p < 1 || p > reviewTotalPages.value) return
  reviewCurrentPage.value = p
}
watch([reviewFilterStudentName, reviewDateSort, reviewDateFrom, reviewDateTo], () => {
  reviewCurrentPage.value = 1
})

async function fetchReviews() {
  if (!user.value) return
  loadingReviews.value = true
  try {
    const res = await api.get('/teacher-reviews/', { params: { teacher: user.value.id, page_size: 200 } })
    reviews.value = res.data.results ? res.data.results : (res.data || [])
  } catch (err) {
    console.error("Sharhlarni yuklashda xatolik:", err)
  } finally {
    loadingReviews.value = false
  }
}

// Reviews come from students only, and never for yourself.
const canLeaveReview = computed(() => !!(
  authStore.canLeaveReviews && user.value && authStore.user?.id !== user.value.id
))

const reviewModal = ref(null)
const reviewForm = ref({ rating: 5, comment: '' })
const reviewSaving = ref(false)
const reviewError = ref('')

function openReviewModal() {
  reviewForm.value = { rating: 5, comment: '' }
  reviewError.value = ''
  reviewModal.value?.showModal()
}

async function submitReview() {
  if (!user.value) return
  reviewSaving.value = true
  reviewError.value = ''
  try {
    await api.post('/teacher-reviews/', {
      teacher: user.value.id,
      rating: reviewForm.value.rating,
      comment: reviewForm.value.comment || '',
    })
    reviewModal.value?.close()
    await fetchReviews()
  } catch (err) {
    console.error(err)
    reviewError.value = err.response?.data?.detail || "Sharhni yuborishda xatolik yuz berdi."
  } finally {
    reviewSaving.value = false
  }
}

// ── Bonus payment (paid on the exam-pass cert, from the teacher's/
// coordinator's assigned-students table) ──────────────────
// Only superuser can pay a bonus, and never while viewing their own profile.
const canPayBonus = computed(() => !!(authStore.isSuperuser && authStore.user && user.value && authStore.user.id !== user.value.id))

// All certificates (any instructor), used only to know whether a given
// linked student already has one uploaded — for the students table filter.
const allStudentCerts = ref([])
async function fetchAllStudentCerts() {
  try {
    const res = await api.get('/student-certificates/', { params: { page_size: 1000 } })
    allStudentCerts.value = res.data.results ? res.data.results : (res.data || [])
  } catch (err) {
    console.error("Sertifikatlar holatini yuklashda xatolik:", err)
  }
}

// ── Certificate upload (for a specific linked student, from this table) ──
const certUploadModal = ref(null)
const certUploadFileInputRef = ref(null)
const certUploadTarget = ref(null)
const certUploadFile = ref(null)
const certUploadNotes = ref('')
const certUploadSaving = ref(false)
const certUploadError = ref('')

function openCertUploadModal(enrollment) {
  certUploadTarget.value = enrollment
  certUploadFile.value = null
  certUploadFileInputRef.value?.reset()
  certUploadNotes.value = ''
  certUploadError.value = ''
  certUploadModal.value?.showModal()
}

function closeCertUploadModal() {
  certUploadModal.value?.close()
}

function onCertUploadFileChange(e) {
  certUploadFile.value = e.target.files?.[0] || null
}

async function submitCertUpload() {
  if (!certUploadFile.value || !certUploadTarget.value) return
  certUploadSaving.value = true
  certUploadError.value = ''
  try {
    const formData = new FormData()
    formData.append('student', certUploadTarget.value.student)
    formData.append('image', certUploadFile.value)
    if (certUploadNotes.value) formData.append('notes', certUploadNotes.value)
    await api.post('/student-certificates/', formData)
    closeCertUploadModal()
    await fetchAllStudentCerts()
  } catch (err) {
    console.error(err)
    certUploadError.value = err.response?.data?.detail || "Sertifikatni yuklashda xatolik yuz berdi."
  } finally {
    certUploadSaving.value = false
  }
}

// ── Course-completion certificate (series/number, dedicated small modal) ──
const courseCertModal = ref(null)
const courseCertTarget = ref(null)
const courseCertForm = ref({ certificate_series: '', certificate_number: '' })
const courseCertSaving = ref(false)
const courseCertError = ref('')

function openCourseCertModal(enrollment) {
  courseCertTarget.value = enrollment
  courseCertForm.value = {
    certificate_series: enrollment.student_certificate_series || 'SA',
    certificate_number: enrollment.student_certificate_number || '',
  }
  courseCertError.value = ''
  courseCertModal.value?.showModal()
}

function closeCourseCertModal() {
  courseCertModal.value?.close()
}

async function submitCourseCert() {
  if (!courseCertTarget.value) return
  const series = courseCertForm.value.certificate_series.trim().toUpperCase()
  const number = courseCertForm.value.certificate_number.trim()
  if (!/^[A-Z]{2}$/.test(series)) { courseCertError.value = "Seriya 2 ta harfdan iborat bo'lishi kerak (masalan: AB)."; return }
  if (!/^\d{9}$/.test(number)) { courseCertError.value = "Raqam 9 ta raqamdan iborat bo'lishi kerak."; return }
  courseCertSaving.value = true
  courseCertError.value = ''
  try {
    await api.patch(`/students/${courseCertTarget.value.student}/`, {
      certificate_series: series,
      certificate_number: number,
    })
    closeCourseCertModal()
    await fetchLinkedEnrollments()
  } catch (err) {
    console.error(err)
    courseCertError.value = err.response?.data?.detail || "Saqlashda xatolik yuz berdi."
  } finally {
    courseCertSaving.value = false
  }
}

const bonusModal = ref(null)
const bonusTarget = ref(null)
const bonusForm = ref({ amountFormatted: '', amount: 0, method: 'cash' })
const bonusSaving = ref(false)
const bonusError = ref('')

// Re-checks the certificate's paid status right before opening the modal —
// the table's cert list can go stale between page load and the click (e.g.
// another admin/tab paid it in the meantime), which previously let the
// button stay clickable and the submit fail with "already paid".
async function openBonusModal(cert) {
  if (!cert) return
  await fetchAllStudentCerts()
  const fresh = allStudentCerts.value.find(c => c.id === cert.id) || cert
  if (fresh.bonus_paid) return
  bonusTarget.value = fresh
  bonusForm.value = { amountFormatted: '', amount: 0, method: 'cash' }
  bonusError.value = ''
  bonusModal.value?.showModal()
}

function onBonusFormAmountInput(e) {
  const digits = e.target.value.replace(/\D/g, '')
  if (!digits) { bonusForm.value.amount = 0; bonusForm.value.amountFormatted = ''; return }
  const num = parseInt(digits, 10)
  bonusForm.value.amount = num
  bonusForm.value.amountFormatted = num.toLocaleString('uz-UZ')
}

async function submitCertBonus() {
  if (!bonusTarget.value || !bonusForm.value.amount) {
    bonusError.value = "To'g'ri summa kiriting."
    return
  }
  bonusSaving.value = true
  bonusError.value = ''
  try {
    await api.post(`/student-certificates/${bonusTarget.value.id}/pay-bonus/`, {
      amount: bonusForm.value.amount,
      method: bonusForm.value.method,
    })
    bonusModal.value?.close()
    await fetchAllStudentCerts()
    await fetchUserPayments()
  } catch (err) {
    console.error(err)
    bonusError.value = err.response?.data?.detail || "Bonus to'lashda xatolik yuz berdi."
    // Whatever caused the failure (most likely: already paid elsewhere in
    // the meantime), refresh so the table/button reflect the real state.
    await fetchAllStudentCerts()
  } finally {
    bonusSaving.value = false
  }
}

const userModal = ref(null)
const saving = ref(false)
const modalError = ref(null)

const editForm = ref({
  full_name: '',
  phone: '',
  phone2: '',
  role: '',
  branch: null,
  jshshr: '',
  passport_serie: '',
  passport_number: '',
  license_series: '',
  license_number: '',
  notes: '',
  password: '',
  passwordConfirm: ''
})

// Formats the phone field as the user types into "+998 90 900 90 90".
// The raw digits are what actually get sent on save.
function onEditPhoneInput(e) {
  editForm.value.phone = formatPhoneInput(e.target.value)
}

function onEditPhone2Input(e) {
  editForm.value.phone2 = formatPhoneInput(e.target.value)
}

const userInitials = computed(() => {
  if (!user.value) return 'U'
  const name = user.value.full_name || `${user.value.first_name || ''} ${user.value.last_name || ''}`.strip()
  if (!name) return 'U'
  const parts = name.split(' ')
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  return name.slice(0, 2).toUpperCase()
})

const studentTableSearch = ref('')
const studentTableGroupFilter = ref('')
const studentTableCategoryFilter = ref('')
const filterExamCertStatus = ref('')
const filterCourseCertStatus = ref('')
const filterStatus = ref('')
const filterAgentName = ref('')
const filterLearningPlace = ref('')
// Filters whichever counterpart column is currently shown (O'qituvchi on an
// instructor's page, Instruktor on a teacher's page) — only one is ever
// rendered at a time, so a single ref covers both.
const filterCounterpartName = ref('')

// ── Group start/end sorting ──────────────────────────────────────────────
const groupStartSort = ref('') // '', 'asc', 'desc'
const groupEndSort = ref('')
const bonusPaidDateSort = ref('')
const groupStartFrom = ref('')
const groupStartTo = ref('')
const groupEndFrom = ref('')
const groupEndTo = ref('')
const bonusPaidDateFrom = ref('')
const bonusPaidDateTo = ref('')

function setSort(column, direction) {
  if (column === 'groupStart') {
    groupEndSort.value = ''
    bonusPaidDateSort.value = ''
    groupStartSort.value = groupStartSort.value === direction ? '' : direction
  } else if (column === 'groupEnd') {
    groupStartSort.value = ''
    bonusPaidDateSort.value = ''
    groupEndSort.value = groupEndSort.value === direction ? '' : direction
  } else if (column === 'bonusPaidDate') {
    groupStartSort.value = ''
    groupEndSort.value = ''
    bonusPaidDateSort.value = bonusPaidDateSort.value === direction ? '' : direction
  }
}

// The bonus_teacher Payment's own created_at for a given certificate — the
// certificate itself only stores which payment paid its bonus (bonus_payment
// id), not the date, so it's looked up from this teacher's own payments list.
function getCertBonusPaymentDate(cert) {
  if (!cert || !cert.bonus_payment) return null
  const payment = userPayments.value.find(p => p.id === cert.bonus_payment)
  return payment ? payment.created_at : null
}

// ── Pagination state (client-side — the full linked-student list is
// already loaded) ──────────────────────────────────────────────────────
const studentTableCurrentPage = ref(1)
const studentTablePageSize = 50
const studentTableTotalPages = computed(() => Math.ceil(filteredLinkedEnrollments.value.length / studentTablePageSize) || 1)

function changeStudentTablePage(page) {
  if (page < 1 || page > studentTableTotalPages.value) return
  studentTableCurrentPage.value = page
}

// Fixed columns (16) plus whichever of the counterpart teacher/instructor
// columns is currently shown — kept in sync with the <thead> so the empty
// state row spans the table correctly.
const studentTableColspan = computed(() => 16 + (showCoordinatorColumn.value ? 1 : 0) + (showInstructorColumn.value ? 1 : 0))

watch([studentTableSearch, studentTableGroupFilter, studentTableCategoryFilter, filterExamCertStatus, filterCourseCertStatus, filterStatus, filterAgentName, filterLearningPlace, filterCounterpartName, groupStartSort, groupEndSort, bonusPaidDateSort, groupStartFrom, groupStartTo, groupEndFrom, groupEndTo, bonusPaidDateFrom, bonusPaidDateTo], () => {
  studentTableCurrentPage.value = 1
})

// Distinct groups/categories among this staff member's linked students, for
// the filter dropdowns — no point offering options that would match nothing.
const linkedCategoryOptions = computed(() => {
  const map = {}
  enrollments.value.forEach(e => {
    if (e.category && !map[e.category]) map[e.category] = { id: e.category, name: e.category_name || `#${e.category}` }
  })
  return Object.values(map).sort((a, b) => a.name.localeCompare(b.name))
})

// The exam-pass certificate (image upload) for a given student, regardless
// of which instructor/coordinator it's attributed to — null if none yet.
function getStudentExamCert(studentId) {
  return allStudentCerts.value.find(c => c.student === studentId) || null
}

function studentHasCertificate(studentId) {
  return !!getStudentExamCert(studentId)
}

const filteredLinkedEnrollments = computed(() => {
  const q = studentTableSearch.value.trim().toLowerCase()
  const groupQ = studentTableGroupFilter.value.trim().toLowerCase()
  const agentQ = filterAgentName.value.trim().toLowerCase()
  const placeQ = filterLearningPlace.value.trim().toLowerCase()
  const counterpartQ = filterCounterpartName.value.trim().toLowerCase()
  return enrollments.value.filter(e => {
    if (groupQ && !(e.group_name || '').toLowerCase().includes(groupQ)) return false
    if (studentTableCategoryFilter.value && e.category !== studentTableCategoryFilter.value) return false
    if (filterStatus.value && e.status !== filterStatus.value) return false
    if (agentQ && !(e.agent_name || '').toLowerCase().includes(agentQ)) return false
    if (placeQ && !(e.learning_place_name || '').toLowerCase().includes(placeQ)) return false
    if (counterpartQ) {
      const counterpartName = showCoordinatorColumn.value ? e.coordinator_name : e.instructor_name
      if (!(counterpartName || '').toLowerCase().includes(counterpartQ)) return false
    }
    if (filterCourseCertStatus.value) {
      const hasCourseCert = !!e.student_certificate_number
      if (filterCourseCertStatus.value === 'uploaded' && !hasCourseCert) return false
      if (filterCourseCertStatus.value === 'not_uploaded' && hasCourseCert) return false
    }
    if (filterExamCertStatus.value) {
      const hasCert = studentHasCertificate(e.student)
      if (filterExamCertStatus.value === 'uploaded' && !hasCert) return false
      if (filterExamCertStatus.value === 'not_uploaded' && hasCert) return false
    }
    const g = groupsById.value[e.group]
    if (groupStartFrom.value && !(g?.started_at && g.started_at >= groupStartFrom.value)) return false
    if (groupStartTo.value && !(g?.started_at && g.started_at <= groupStartTo.value)) return false
    if (groupEndFrom.value && !(g?.ends_at && g.ends_at >= groupEndFrom.value)) return false
    if (groupEndTo.value && !(g?.ends_at && g.ends_at <= groupEndTo.value)) return false
    if (bonusPaidDateFrom.value || bonusPaidDateTo.value) {
      const bonusDate = getCertBonusPaymentDate(getStudentExamCert(e.student))
      if (bonusPaidDateFrom.value && !(bonusDate && bonusDate.slice(0, 10) >= bonusPaidDateFrom.value)) return false
      if (bonusPaidDateTo.value && !(bonusDate && bonusDate.slice(0, 10) <= bonusPaidDateTo.value)) return false
    }
    if (!q) return true
    return (e.student_name || '').toLowerCase().includes(q)
  })
})

// Sorting doesn't remove rows, only reorders — applied after filtering,
// before the pagination slice. Enrollments without a resolved group sort
// last regardless of direction.
const sortedLinkedEnrollments = computed(() => {
  const list = [...filteredLinkedEnrollments.value]
  if (bonusPaidDateSort.value) {
    const dir = bonusPaidDateSort.value === 'asc' ? 1 : -1
    list.sort((a, b) => {
      const da = getCertBonusPaymentDate(getStudentExamCert(a.student))
      const db = getCertBonusPaymentDate(getStudentExamCert(b.student))
      const ta = da ? new Date(da).getTime() : null
      const tb = db ? new Date(db).getTime() : null
      if (ta === null && tb === null) return 0
      if (ta === null) return 1
      if (tb === null) return -1
      return (ta - tb) * dir
    })
    return list
  }
  const field = groupStartSort.value ? 'started_at' : (groupEndSort.value ? 'ends_at' : null)
  if (!field) return list
  const direction = groupStartSort.value || groupEndSort.value
  list.sort((a, b) => {
    const da = groupsById.value[a.group]?.[field] || ''
    const db = groupsById.value[b.group]?.[field] || ''
    if (!da && !db) return 0
    if (!da) return 1
    if (!db) return -1
    return direction === 'asc' ? da.localeCompare(db) : db.localeCompare(da)
  })
  return list
})

const paginatedLinkedEnrollments = computed(() => {
  const start = (studentTableCurrentPage.value - 1) * studentTablePageSize
  return sortedLinkedEnrollments.value.slice(start, start + studentTablePageSize)
})

async function fetchUserDetail() {
  loading.value = true
  error.value = null
  try {
    const res = await api.get(`/users/${route.params.id}/`)
    user.value = res.data
    fetchLinkedEnrollments()
    fetchReviews()
    fetchUserPayments()
    ensureGroupsLoaded()
    fetchInstructorCars()
    fetchAgentReferredStudents()
    fetchInstructorLessonHistory()
  } catch (err) {
    error.value = "Foydalanuvchi ma'lumotlarini yuklashda xatolik"
  } finally {
    loading.value = false
  }
}

// ── Agent sifatida biriktirilgan o'quvchilar — this profile may itself be
// linked as an Agent (Agent.user), in which case it earns referral bonuses
// like any other agent; surfaced here so admins don't have to cross-
// reference the separate Agents page to see who this teacher referred. ──
const agentRecord = ref(null)
const agentReferredEnrollments = ref([])
const loadingAgentReferred = ref(false)
const agentReferredSearch = ref('')
const agentReferredGroupFilter = ref('')
const agentReferredCategoryFilter = ref('')
const agentReferredStatusFilter = ref('')
const agentReferredGroupStartSort = ref('')
const agentReferredGroupEndSort = ref('')
const agentReferredGroupStartFrom = ref('')
const agentReferredGroupStartTo = ref('')
const agentReferredGroupEndFrom = ref('')
const agentReferredGroupEndTo = ref('')
const agentReferredPage = ref(1)
const agentReferredPageSize = 50

function setAgentReferredSort(column, direction) {
  if (column === 'groupStart') {
    agentReferredGroupEndSort.value = ''
    agentReferredGroupStartSort.value = agentReferredGroupStartSort.value === direction ? '' : direction
  } else if (column === 'groupEnd') {
    agentReferredGroupStartSort.value = ''
    agentReferredGroupEndSort.value = agentReferredGroupEndSort.value === direction ? '' : direction
  }
}

async function fetchAgentReferredStudents() {
  if (!user.value) return
  loadingAgentReferred.value = true
  try {
    const groupsReady = ensureGroupsLoaded()
    const agentsRes = await api.get('/agents/', { params: { page_size: 1000 } })
    const agentsList = agentsRes.data.results || agentsRes.data || []
    const match = agentsList.find(a => a.user === user.value.id)
    agentRecord.value = match || null
    if (match) {
      const res = await api.get('/enrollments/', { params: { agent: match.id, page_size: 1000 } })
      agentReferredEnrollments.value = res.data.results || res.data || []
    } else {
      agentReferredEnrollments.value = []
    }
    await groupsReady
  } catch (err) {
    console.error("Agent sifatida biriktirilgan o'quvchilarni yuklashda xatolik:", err)
  } finally {
    loadingAgentReferred.value = false
  }
}

const filteredAgentReferredEnrollments = computed(() => {
  const q = agentReferredSearch.value.trim().toLowerCase()
  const groupQ = agentReferredGroupFilter.value.trim().toLowerCase()
  let list = agentReferredEnrollments.value.filter(e => {
    if (q && !(e.student_name || '').toLowerCase().includes(q)) return false
    if (groupQ && !(e.group_name || '').toLowerCase().includes(groupQ)) return false
    if (agentReferredCategoryFilter.value && String(e.category) !== String(agentReferredCategoryFilter.value)) return false
    if (agentReferredStatusFilter.value && e.status !== agentReferredStatusFilter.value) return false
    const g = groupsById.value[e.group]
    if (agentReferredGroupStartFrom.value && !(g?.started_at && g.started_at >= agentReferredGroupStartFrom.value)) return false
    if (agentReferredGroupStartTo.value && !(g?.started_at && g.started_at <= agentReferredGroupStartTo.value)) return false
    if (agentReferredGroupEndFrom.value && !(g?.ends_at && g.ends_at >= agentReferredGroupEndFrom.value)) return false
    if (agentReferredGroupEndTo.value && !(g?.ends_at && g.ends_at <= agentReferredGroupEndTo.value)) return false
    return true
  })

  const field = agentReferredGroupStartSort.value ? 'started_at' : (agentReferredGroupEndSort.value ? 'ends_at' : null)
  if (field) {
    const dir = agentReferredGroupStartSort.value || agentReferredGroupEndSort.value
    list = [...list].sort((a, b) => {
      const da = groupsById.value[a.group]?.[field] || ''
      const db = groupsById.value[b.group]?.[field] || ''
      if (!da && !db) return 0
      if (!da) return 1
      if (!db) return -1
      return dir === 'asc' ? da.localeCompare(db) : db.localeCompare(da)
    })
  }
  return list
})
const agentReferredTotalPages = computed(() => Math.max(1, Math.ceil(filteredAgentReferredEnrollments.value.length / agentReferredPageSize)))
const paginatedAgentReferredEnrollments = computed(() => {
  const start = (agentReferredPage.value - 1) * agentReferredPageSize
  return filteredAgentReferredEnrollments.value.slice(start, start + agentReferredPageSize)
})
watch([agentReferredSearch, agentReferredGroupFilter, agentReferredCategoryFilter, agentReferredStatusFilter, agentReferredGroupStartSort, agentReferredGroupEndSort, agentReferredGroupStartFrom, agentReferredGroupStartTo, agentReferredGroupEndFrom, agentReferredGroupEndTo], () => { agentReferredPage.value = 1 })

// ── Amaliy darslar tarixi — every distinct student this instructor has
// actually given a practical driving lesson to, independent of who they're
// currently assigned to (an instructor reassignment shouldn't erase the
// history of who they used to teach). ──
const instructorLessonRows = ref([])
const loadingInstructorLessons = ref(false)
const instructorLessonSearch = ref('')
const instructorLessonCategoryFilter = ref('')
const instructorLessonGroupFilter = ref('')
const instructorLessonPage = ref(1)
const instructorLessonPageSize = 50

async function fetchInstructorLessonHistory() {
  if (!user.value || user.value.role !== 'instructor') return
  loadingInstructorLessons.value = true
  try {
    const [lessonsRes, enrollRes] = await Promise.all([
      api.get('/driving-lessons/', { params: { instructor: user.value.id, lesson_type: 'driving', page_size: 1000 } }),
      api.get('/enrollments/', { params: { page_size: 1000 } }),
      ensureGroupsLoaded(),
    ])
    const lessons = lessonsRes.data.results || lessonsRes.data || []
    const allEnrollments = enrollRes.data.results || enrollRes.data || []

    const byStudent = new Map()
    lessons.forEach(l => {
      if (!l.student) return
      const lessonTime = l.lesson_date ? new Date(l.lesson_date).getTime() : 0
      const existing = byStudent.get(l.student)
      if (!existing) {
        byStudent.set(l.student, { count: 1, lastTime: lessonTime, lastDate: l.lesson_date, studentName: l.student_name })
      } else {
        existing.count += 1
        if (lessonTime > existing.lastTime) {
          existing.lastTime = lessonTime
          existing.lastDate = l.lesson_date
        }
      }
    })

    instructorLessonRows.value = Array.from(byStudent, ([studentId, info]) => {
      const enr = allEnrollments.find(e => e.student === studentId && e.is_active) || allEnrollments.find(e => e.student === studentId)
      return {
        student: studentId,
        student_name: enr?.student_name || info.studentName || "Noma'lum",
        category: enr?.category || null,
        category_name: enr?.category_name || null,
        group: enr?.group || null,
        group_name: enr?.group_name || null,
        status: enr?.status || null,
        lessonCount: info.count,
        lastLessonDate: info.lastDate,
      }
    }).sort((a, b) => (b.lastLessonDate ? new Date(b.lastLessonDate).getTime() : 0) - (a.lastLessonDate ? new Date(a.lastLessonDate).getTime() : 0))
  } catch (err) {
    console.error("Amaliy darslar tarixini yuklashda xatolik:", err)
  } finally {
    loadingInstructorLessons.value = false
  }
}

const instructorGroupStartSort = ref('')
const instructorGroupEndSort = ref('')
const instructorGroupStartFrom = ref('')
const instructorGroupStartTo = ref('')
const instructorGroupEndFrom = ref('')
const instructorGroupEndTo = ref('')
function setInstructorLessonSort(column, direction) {
  if (column === 'groupStart') {
    instructorGroupEndSort.value = ''
    instructorGroupStartSort.value = instructorGroupStartSort.value === direction ? '' : direction
  } else if (column === 'groupEnd') {
    instructorGroupStartSort.value = ''
    instructorGroupEndSort.value = instructorGroupEndSort.value === direction ? '' : direction
  }
}

const filteredInstructorLessonStudents = computed(() => {
  const q = instructorLessonSearch.value.trim().toLowerCase()
  const groupQ = instructorLessonGroupFilter.value.trim().toLowerCase()
  let list = instructorLessonRows.value.filter(row => {
    if (q && !(row.student_name || '').toLowerCase().includes(q)) return false
    if (groupQ && !(row.group_name || '').toLowerCase().includes(groupQ)) return false
    if (instructorLessonCategoryFilter.value && String(row.category) !== String(instructorLessonCategoryFilter.value)) return false
    const g = groupsById.value[row.group]
    if (instructorGroupStartFrom.value && !(g?.started_at && g.started_at >= instructorGroupStartFrom.value)) return false
    if (instructorGroupStartTo.value && !(g?.started_at && g.started_at <= instructorGroupStartTo.value)) return false
    if (instructorGroupEndFrom.value && !(g?.ends_at && g.ends_at >= instructorGroupEndFrom.value)) return false
    if (instructorGroupEndTo.value && !(g?.ends_at && g.ends_at <= instructorGroupEndTo.value)) return false
    return true
  })

  const field = instructorGroupStartSort.value ? 'started_at' : (instructorGroupEndSort.value ? 'ends_at' : null)
  if (field) {
    const dir = instructorGroupStartSort.value || instructorGroupEndSort.value
    list = [...list].sort((a, b) => {
      const da = groupsById.value[a.group]?.[field] || ''
      const db = groupsById.value[b.group]?.[field] || ''
      if (!da && !db) return 0
      if (!da) return 1
      if (!db) return -1
      return dir === 'asc' ? da.localeCompare(db) : db.localeCompare(da)
    })
  }
  return list
})
const instructorLessonTotalPages = computed(() => Math.max(1, Math.ceil(filteredInstructorLessonStudents.value.length / instructorLessonPageSize)))
const paginatedInstructorLessonStudents = computed(() => {
  const start = (instructorLessonPage.value - 1) * instructorLessonPageSize
  return filteredInstructorLessonStudents.value.slice(start, start + instructorLessonPageSize)
})
watch([instructorLessonSearch, instructorLessonCategoryFilter, instructorLessonGroupFilter, instructorGroupStartSort, instructorGroupEndSort, instructorGroupStartFrom, instructorGroupStartTo, instructorGroupEndFrom, instructorGroupEndTo], () => { instructorLessonPage.value = 1 })

async function fetchLinkedEnrollments() {
  if (!user.value) return
  loadingEnrollments.value = true
  try {
    // Check role to query either instructor or coordinator. Also awaited
    // alongside the exam-cert list so the "Sertifikat" column doesn't
    // briefly show "no certificate" for every row before it pops in once
    // that separate request (previously fired unawaited) resolves.
    const paramKey = user.value.role === 'instructor' ? 'instructor' : 'coordinator'
    const [res] = await Promise.all([
      api.get('/enrollments/', { params: { [paramKey]: user.value.id, page_size: 1000 } }),
      ensureGroupsLoaded(),
      fetchAllStudentCerts(),
    ])
    enrollments.value = res.data.results ? res.data.results : res.data
    if (user.value.role === 'coordinator') fetchTeacherAttendance()
  } catch (err) {
    console.error(err)
  } finally {
    loadingEnrollments.value = false
  }
}

// ── Yo'qlama jadvali (Davomat) — full history for this teacher's students,
// computed entirely server-side (management/views.py AttendanceViewSet.
// history): every calendar day from the student's own date_joined to
// today, no learning_days or group date involved. Only today's cell is
// ever writable; a click marks it keldi. ──
const loadingTeacherAttendance = ref(false)
const teacherAttendanceHistory = ref({})
const markingAttendance = ref({})
const todayStr = new Date().toISOString().slice(0, 10)

async function fetchTeacherAttendance() {
  if (enrollments.value.length === 0) {
    teacherAttendanceHistory.value = {}
    return
  }
  loadingTeacherAttendance.value = true
  try {
    const ids = enrollments.value.map(e => e.id)
    const [res] = await Promise.all([
      api.get('/attendance/history/', { params: { enrollment__in: ids.join(',') } }),
      ensureGroupsLoaded(),
    ])
    teacherAttendanceHistory.value = res.data || {}
  } catch (err) {
    console.error("Davomat tarixini yuklashda xatolik:", err)
  } finally {
    loadingTeacherAttendance.value = false
  }
}

function attendanceDaysFor(e) {
  return teacherAttendanceHistory.value[e.id] || []
}

// One shared date header for the whole table: a fixed rolling 15-day
// window, today first then 14 days back, independent of whatever any
// single enrollment's own day list happens to contain.
const attendanceAllDates = computed(() => {
  const dates = []
  for (let i = 0; i <= 14; i++) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    dates.push(d.toISOString().slice(0, 10))
  }
  return dates
})

// ── Yo'qlama jadvali filters/sort — separate refs from the "Biriktirilgan
// O'quvchilar" table above (setSort already owns groupStartSort/groupEndSort
// there, and resets them on every call, so reusing it would fight this
// table's own sort state). ─────────────────────────────────────────────
const attendanceTableSearch = ref('')
const attendanceTableGroupFilter = ref('')
const attendanceGroupStartSort = ref('') // '', 'asc', 'desc'
const attendanceGroupEndSort = ref('')
const attendanceGroupStartFrom = ref('')
const attendanceGroupStartTo = ref('')
const attendanceGroupEndFrom = ref('')
const attendanceGroupEndTo = ref('')

function setAttendanceSort(column, direction) {
  if (column === 'groupStart') {
    attendanceGroupEndSort.value = ''
    attendanceGroupStartSort.value = attendanceGroupStartSort.value === direction ? '' : direction
  } else if (column === 'groupEnd') {
    attendanceGroupStartSort.value = ''
    attendanceGroupEndSort.value = attendanceGroupEndSort.value === direction ? '' : direction
  }
}

// Finished/canceled students have nothing left to attend, and their group
// may already be locked from further attendance changes (backend rejects
// marking either case) — showing them in Yo'qlama jadvali would just be a
// row of dead buttons, so they're excluded from this table entirely.
const INACTIVE_STATUSES = ['finished', 'canceled']

const filteredAttendanceEnrollments = computed(() => {
  const q = attendanceTableSearch.value.trim().toLowerCase()
  const groupQ = attendanceTableGroupFilter.value.trim().toLowerCase()
  return enrollments.value.filter(e => {
    if (INACTIVE_STATUSES.includes(e.status)) return false
    const g = groupsById.value[e.group]
    if (g && INACTIVE_STATUSES.includes(g.status)) return false
    if (groupQ && !(e.group_name || '').toLowerCase().includes(groupQ)) return false
    if (q && !(e.student_name || '').toLowerCase().includes(q)) return false
    if (attendanceGroupStartFrom.value && !(g?.started_at && g.started_at >= attendanceGroupStartFrom.value)) return false
    if (attendanceGroupStartTo.value && !(g?.started_at && g.started_at <= attendanceGroupStartTo.value)) return false
    if (attendanceGroupEndFrom.value && !(g?.ends_at && g.ends_at >= attendanceGroupEndFrom.value)) return false
    if (attendanceGroupEndTo.value && !(g?.ends_at && g.ends_at <= attendanceGroupEndTo.value)) return false
    return true
  })
})

const sortedAttendanceEnrollments = computed(() => {
  const list = [...filteredAttendanceEnrollments.value]
  const field = attendanceGroupStartSort.value ? 'started_at' : (attendanceGroupEndSort.value ? 'ends_at' : null)
  if (!field) return list
  const direction = attendanceGroupStartSort.value || attendanceGroupEndSort.value
  list.sort((a, b) => {
    const da = groupsById.value[a.group]?.[field] || ''
    const db = groupsById.value[b.group]?.[field] || ''
    if (!da && !db) return 0
    if (!da) return 1
    if (!db) return -1
    return direction === 'asc' ? da.localeCompare(db) : db.localeCompare(da)
  })
  return list
})

// A given student may not have a recorded mark for every shared column.
// Today always resolves to something markable, even if the backend hasn't
// returned a placeholder for it yet, so the "?" is never silently missing.
// A date the backend didn't return at all is before the student's own
// enrolment date (the 15-day strip is a fixed window, wider than some
// enrolments) — shown blank, neither present nor absent.
function dayFor(e, dateStr) {
  const found = attendanceDaysFor(e).find(d => d.date === dateStr)
  if (found) return found
  if (dateStr === todayStr) return { date: dateStr, status: 'today' }
  return { date: dateStr, status: 'none' }
}

// No mark recorded for a closed day ("unknown" from the backend) means the
// student was absent — there's no separate "kelmadi" action to take
// anymore, silence is absence by default.
const ABSENT_STATUSES = ['kelmadi', 'unknown']

// "Davomat hisoboti": visited/total days from the student's own date_joined
// through today (the full history the backend returns, not just the
// 15-day strip shown in the table).
function attendanceReport(e) {
  const days = attendanceDaysFor(e)
  const total = days.length
  const visited = days.filter(d => d.status === 'keldi').length
  return { visited, total }
}

function dayLabel(dateStr) {
  const [y, m, day] = dateStr.split('-')
  return `${day}.${m}.${y}`
}

function isToday(d) {
  return d.date === todayStr
}

const canMarkAttendance = computed(() => authStore.isAdminOrSuperuser || authStore.user?.id === user.value?.id)

function attendanceIconSymbol(d) {
  if (d.status === 'keldi') return '✓'
  if (ABSENT_STATUSES.includes(d.status)) return '✕'
  if (d.status === 'today') return '?'
  return '-'
}
function attendanceIconClass(d) {
  if (d.status === 'keldi') return 'davomat-present'
  if (ABSENT_STATUSES.includes(d.status)) return 'davomat-absent'
  if (d.status === 'today') return 'davomat-unknown'
  return 'davomat-none'
}
function markKey(e, d) {
  return `${e.id}-${d.date}`
}

// Today's cell opens a small keldi/kelmadi popup instead of cycling on
// click — only one popup open at a time, closed by picking an option or
// by the document-level outside-click handler registered in onMounted.
const openPopupKey = ref(null)

function toggleMarkPopup(e, d) {
  if (!canMarkAttendance.value) return
  const key = markKey(e, d)
  openPopupKey.value = openPopupKey.value === key ? null : key
}

function closeMarkPopupOnOutsideClick(event) {
  if (openPopupKey.value && !event.target.closest('.davomat-today-wrap')) {
    openPopupKey.value = null
  }
}

async function chooseMark(e, d, isAbsent) {
  openPopupKey.value = null
  const key = markKey(e, d)
  if (markingAttendance.value[key]) return
  markingAttendance.value = { ...markingAttendance.value, [key]: true }
  try {
    const res = await api.post('/attendance/', {
      enrollment: e.id,
      date: d.date,
      is_absent: isAbsent,
    })
    const days = teacherAttendanceHistory.value[e.id] || []
    const idx = days.findIndex(day => day.date === d.date)
    const updated = [...days]
    const newStatus = res.data.is_absent ? 'kelmadi' : 'keldi'
    if (idx >= 0) updated.splice(idx, 1, { date: d.date, status: newStatus })
    teacherAttendanceHistory.value = { ...teacherAttendanceHistory.value, [e.id]: updated }
  } catch (err) {
    console.error("Davomatni belgilashda xatolik:", err)
  } finally {
    const rest = { ...markingAttendance.value }
    delete rest[key]
    markingAttendance.value = rest
  }
}

function roleClass(role, isSuperuser) {
  if (isSuperuser) return 'role-superuser'
  switch (role) {
    case 'admin': return 'role-admin'
    case 'instructor': return 'role-instructor'
    case 'coordinator': return 'role-coordinator'
    case 'mechanic': return 'role-mechanic'
    default: return 'role-default'
  }
}

function roleText(role, isSuperuser) {
  if (isSuperuser) return 'Superuser'
  switch (role) {
    case 'admin': return 'Admin'
    case 'instructor': return 'Instruktor'
    case 'coordinator': return "O'qituvchi"
    case 'mechanic': return 'Mexanik'
    default: return role
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

const imageZoomModal = ref(null)
const zoomedImageUrl = ref('')

function openImageModal(url) {
  if (!url) return
  zoomedImageUrl.value = url
  imageZoomModal.value?.showModal()
}

const examCertPreviewModal = ref(null)
const previewingExamCert = ref(null)

function openExamCertPreview(cert) {
  previewingExamCert.value = cert
  examCertPreviewModal.value?.showModal()
}

const selectedUserFile = ref(null)
const userFileInputRef = ref(null)
function onUserFileChange(e) {
  selectedUserFile.value = e.target.files?.[0] || null
}

function openEditModal() {
  modalError.value = null
  selectedUserFile.value = null
  userFileInputRef.value?.reset()
  if (branchStore.branches.length === 0) branchStore.fetchBranches()
  editForm.value = {
    full_name: user.value.full_name || '',
    phone: formatPhoneInput(user.value.phone),
    phone2: user.value.phone2 ? formatPhoneInput(user.value.phone2) : '',
    role: user.value.role || 'instructor',
    branch: user.value.branch ?? null,
    jshshr: user.value.jshshr || '',
    passport_serie: user.value.passport_serie || '',
    passport_number: user.value.passport_number || '',
    license_series: user.value.license_series || '',
    license_number: user.value.license_number || '',
    notes: user.value.notes || '',
    password: '',
    passwordConfirm: '',
    existingImage: user.value.image || null,
  }
  userModal.value?.showModal()
}

function closeModal() {
  userModal.value?.close()
}

// A click on the <dialog> element itself (rather than on its content) means
// the click landed on the backdrop, since the dialog box is sized to its
// content — checking bounding coordinates is more reliable cross-browser
// than comparing event.target.
function onDialogBackdropClick(e, dialogEl) {
  if (!dialogEl) return
  const rect = dialogEl.getBoundingClientRect()
  const outside = e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom
  if (outside) dialogEl.close()
}

async function saveUser() {
  // Password is optional on edit — only validate/send it when the admin
  // actually typed something into the "Yangi parol" field.
  if (editForm.value.password || editForm.value.passwordConfirm) {
    if (editForm.value.password.length < 4) {
      modalError.value = "Parol kamida 4 ta belgidan iborat bo'lishi kerak."
      return
    }
    if (editForm.value.password !== editForm.value.passwordConfirm) {
      modalError.value = "Parollar bir-biriga mos kelmadi."
      return
    }
  }

  saving.value = true
  modalError.value = null
  try {
    const phoneCleaned = editForm.value.phone ? editForm.value.phone.replace(/\D/g, '') : ''
    const payload = {
      full_name: editForm.value.full_name.trim(),
      phone: phoneCleaned,
      phone2: editForm.value.phone2 ? editForm.value.phone2.replace(/\D/g, '') : null,
      role: editForm.value.role,
      branch: editForm.value.branch ?? null,
      jshshr: editForm.value.jshshr ? parseInt(editForm.value.jshshr, 10) : null,
      passport_serie: editForm.value.passport_serie ? editForm.value.passport_serie.trim().toUpperCase() : null,
      passport_number: editForm.value.passport_number ? parseInt(editForm.value.passport_number, 10) : null,
      notes: editForm.value.notes || '',
    }
    if (editForm.value.role === 'instructor') {
      payload.license_series = editForm.value.license_series ? editForm.value.license_series.trim().toUpperCase() : null
      payload.license_number = editForm.value.license_number ? editForm.value.license_number.trim() : null
    }
    if (editForm.value.password) {
      payload.password = editForm.value.password
    }

    let res
    if (selectedUserFile.value) {
      const formData = new FormData()
      Object.keys(payload).forEach(k => {
        if (payload[k] !== null && payload[k] !== undefined) {
          formData.append(k, payload[k])
        }
      })
      formData.append('image', selectedUserFile.value)
      res = await api.patch(`/users/${user.value.id}/`, formData)
    } else {
      res = await api.patch(`/users/${user.value.id}/`, payload)
    }

    user.value = res.data
    closeModal()
  } catch (err) {
    console.error(err)
    modalError.value = err.response?.data?.detail || "Saqlashda xatolik yuz berdi"
  } finally {
    saving.value = false
  }
}

function goBack() {
  if (user.value?.role) {
    router.push({ path: '/users', query: { role: user.value.role } })
  } else {
    router.push('/users')
  }
}

function goStudent(studentId) {
  if (studentId) {
    router.push(`/students/${studentId}`)
  }
}

function goUser(id) {
  if (id) router.push(`/users/${id}`)
}

function goAgent(id) {
  if (id) router.push(`/agents/${id}`)
}

function goGroup(id) {
  if (id) router.push(`/groups/${id}`)
}

onMounted(() => {
  fetchUserDetail()
  document.addEventListener('click', closeMarkPopupOnOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', closeMarkPopupOnOutsideClick)
})

// Route is reused when navigating between two /users/:id pages (e.g. clicking
// the counterpart teacher/instructor link in the linked students table), so
// without this watcher the component never refetches and appears stuck.
watch(() => route.params.id, () => {
  fetchUserDetail()
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
  color: #2D6A4F;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  padding: 0;

  &:hover { text-decoration: underline; }
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
  background: #2D6A4F;
  color: white;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
}

.detail-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #E5E7EB;
  padding: 24px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #F3F4F6;
}

.avatar-large {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #1B2430;
  color: white;
  font-size: 22px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-name {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
}

.role-badge-wrap { margin-top: 4px; }

.role-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.role-superuser { background: #FEE2E2; color: #991B1B; }
.role-admin { background: #FEF3C7; color: #92400E; }
.role-instructor { background: #DCFCE7; color: #166534; }
.role-coordinator { background: #E0F2FE; color: #075985; }
.role-mechanic { background: #F3E8FF; color: #6B21A8; }
.role-default { background: #F3F4F6; color: #374151; }

.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
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
  font-weight: 600;
  color: #111827;
}

.notes-block {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #F3F4F6;
}

.notes-text {
  font-size: 14px;
  color: #374151;
  background: #F9FAFB;
  padding: 10px 14px;
  border-radius: 8px;
  margin-top: 4px;
}

.linked-section {
  background: white;
  border-radius: 12px;
  border: 1px solid #E5E7EB;
  padding: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
}

.count-badge {
  background: #F3F4F6;
  color: #374151;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.empty-groups {
  text-align: center;
  padding: 40px 0;
}

.empty-title {
  font-size: 15px;
  font-weight: 600;
  color: #374151;
  margin-top: 8px;
}

.empty-sub {
  font-size: 13px;
  color: #6B7280;
}

.link-value { cursor: pointer; color: #2563EB !important; font-weight: 700 !important; text-decoration: underline; }
.link-value:hover { color: #1D4ED8 !important; }

.current-car-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  background: #F0FDF4;
  border: 1px solid #A7F3D0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.current-car-card:hover { background: #DCFCE7; border-color: #6EE7B7; }
.current-car-icon { font-size: 28px; }
.current-car-name { font-size: 14.5px; font-weight: 700; color: #111827; }
.current-car-sub { font-size: 12.5px; color: #6B7280; margin-top: 2px; }

.group-badge {
  background: #2D6A4F;
  color: white;
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 700;
  font-size: 12px;
}

.td-group {
  white-space: nowrap;
}

.free-chip {
  padding: 3px 9px;
  background: #EDE9FE;
  color: #6D28D9;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  display: inline-block;
}

.text-green { color: #15803D; font-weight: 700; }

/* ── Column-head filters ─────────────────────────────────── */
.select-wrap-relative { position: relative; width: 100%; }
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

.col-date-range { display: flex; flex-direction: column; gap: 4px; margin-top: 6px; }
/* Narrow frozen davomat columns (100px) can't fit two date inputs
   side-by-side — stack them instead. */
.col-date-range-vertical { flex-direction: column; }
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

/* ── Pagination ───────────────────────────────────────────── */
.pagination-bar { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #F9FAFB; border-top: 1px solid #E5E7EB; margin-top: -1px; }
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

/* ── Certificate columns (course-completion + exam-pass) ────── */
.assign-cell { display: flex; align-items: center; gap: 8px; }
.assign-name-col { display: flex; flex-direction: column; align-items: flex-start; }
.cert-value { font-weight: 500; color: #111827; font-size: 13px; }
.cert-date-sub { font-size: 13px; font-weight: 700; color: #6B7280; margin-top: 3px; }
.btn-assign-plus {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  border: 1px dashed #2D6A4F;
  background: #ECFDF5;
  color: #2D6A4F;
  font-size: 15px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-assign-plus:hover { background: #2D6A4F; color: white; border-style: solid; }
.btn-assign-edit {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: none;
  background: #F3F4F6;
  color: #4B5563;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.btn-assign-edit:hover { background: #E5E7EB; color: #111827; }
.btn-view-cert {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid #BFDBFE;
  border-radius: 20px;
  background: #EFF6FF;
  color: #2563EB;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
.btn-view-cert:hover { background: #DBEAFE; border-color: #93C5FD; }

.cert-preview-dialog { max-width: 640px; }
.cert-preview-body {
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.cert-preview-img {
  max-width: 100%;
  max-height: 70vh;
  border-radius: 10px;
  border: 1px solid #E5E7EB;
  object-fit: contain;
}
.cert-preview-notes {
  margin: 0;
  font-size: 13px;
  color: #6B7280;
  text-align: center;
}

.review-row-stars {
  color: #D97706;
  font-size: 13px;
  letter-spacing: 1px;
}

.review-row-comment {
  font-size: 13px;
  color: #4B5563;
}

/* Bounded, independently-scrolling table body so the header (both the
   label row and the column-filter row) can stick to the top of this
   container as rows scroll underneath, instead of scrolling away with
   the page. */
.table-wrap {
  overflow: auto;
  max-height: 600px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;

  th {
    background: #FAFAFA;
    padding: 10px 16px;
    text-align: left;
    font-weight: 600;
    color: #4B5563;
    border-bottom: 1px solid #E5E7EB;
    white-space: nowrap;
  }

  td {
    padding: 12px 16px;
    border-bottom: 1px solid #F3F4F6;
    color: #1F2937;
  }

  td.td-empty {
    text-align: center;
    padding: 32px;
    color: #9CA3AF;
  }

  /* Sticky is applied to <thead> itself, not to individual <th> cells —
     that keeps both header rows (labels + filters) moving as a single
     pinned unit with no per-row offset math needed. */
  thead {
    position: sticky;
    top: 0;
    z-index: 3;
  }
}

/* ── Yo'qlama jadvali (Davomat) history strip ──
   The four identity columns (name/group/dates) shrink to their own text
   width (width:1% + nowrap is the standard trick for that in an
   auto-layout table); the date columns that follow all get a fixed,
   equal width so the shared header row lines up with every row's marks. */
/* The 4 identity columns stay pinned to the left (both individually
   sticky, and — since they sit inside a <thead> that's already sticky to
   the top — pinned as a corner in both directions) while the 15-day
   strip scrolls underneath inside .table-wrap's horizontal overflow.
   Auto layout (not fixed) lets each date column shrink-wrap to its own
   header text instead of sharing one arbitrary fixed width. */
.attendance-history-table .davomat-frozen-col {
  position: sticky;
  background: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.attendance-history-table th.davomat-frozen-col {
  background: #FAFAFA;
  z-index: 2;
}
.attendance-history-table td.davomat-frozen-col {
  z-index: 1;
}
.attendance-history-table .davomat-frozen-col:nth-child(1) { left: 0; width: 180px; min-width: 180px; max-width: 180px; }
.attendance-history-table .davomat-frozen-col:nth-child(2) { left: 180px; width: 110px; min-width: 110px; max-width: 110px; }
.attendance-history-table .davomat-frozen-col:nth-child(3) { left: 290px; width: 100px; min-width: 100px; max-width: 100px; }
.attendance-history-table .davomat-frozen-col:nth-child(4) { left: 390px; width: 100px; min-width: 100px; max-width: 100px; }
.attendance-history-table .davomat-frozen-col:nth-child(5) {
  left: 490px;
  width: 92px;
  min-width: 92px;
  max-width: 92px;
  box-shadow: 4px 0 6px -4px rgba(0, 0, 0, 0.15);
}
.davomat-report-cell {
  text-align: center;
  font-weight: 700;
  color: #374151;
  font-variant-numeric: tabular-nums;
}
.davomat-date-th {
  width: auto;
  padding: 0 6px 6px !important;
  font-size: 10.5px;
  font-weight: 600;
  color: #6B7280;
  text-align: center !important;
  white-space: nowrap;
}
.davomat-cell {
  width: auto;
  padding: 6px 6px !important;
  text-align: center;
  vertical-align: middle;
  white-space: nowrap;
}
.davomat-icon, .davomat-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  margin: 0 auto;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  line-height: 1;
}
.davomat-icon-btn {
  border: 1.5px solid #D1D5DB;
  background: white;
  cursor: pointer;
  transition: all 0.15s;
}
.davomat-icon-btn:hover:not(:disabled) { transform: translateY(-1px); }
.davomat-icon-btn:disabled { cursor: not-allowed; opacity: 0.7; }
.davomat-today-wrap {
  position: relative;
  display: inline-block;
}
.davomat-mark-popup {
  position: absolute;
  top: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 10px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.12);
  padding: 6px;
  z-index: 20;
}
.davomat-mark-popup-above {
  top: auto;
  bottom: calc(100% + 6px);
}
.davomat-popup-option {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: none;
  border-radius: 7px;
  background: #F9FAFB;
  font-size: 12.5px;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
  transition: background 0.15s;
}
.davomat-popup-present { color: #15803D; }
.davomat-popup-present:hover { background: #DCFCE7; }
.davomat-popup-absent { color: #DC2626; }
.davomat-popup-absent:hover { background: #FEE2E2; }
.davomat-none { color: #D1D5DB; }
.davomat-unknown { border-color: #FBBF24 !important; color: #B45309; background: #FFFBEB !important; }
.davomat-present { color: #15803D; background: #DCFCE7; }
.davomat-icon-btn.davomat-present { border-color: #86EFAC !important; }
.davomat-absent { color: #DC2626; background: #FEE2E2; }
.davomat-icon-btn.davomat-absent { border-color: #FCA5A5 !important; }

.payment-status-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.payment-status-tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 999px;
  border: 1px solid #E5E7EB;
  background: #F9FAFB;
  color: #4B5563;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.payment-status-tab:hover { border-color: #9CA3AF; color: #374151; }
.payment-status-tab.active { background: #2D6A4F; border-color: #2D6A4F; color: white; }

.tab-count {
  font-size: 11px;
  font-weight: 700;
  padding: 1px 7px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.08);
}
.payment-status-tab.active .tab-count { background: rgba(255, 255, 255, 0.25); }

.method-chip {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  background: #EEF2FF;
  color: #4338CA;
}

.counterpart-badge {
  display: inline-block;
  margin-right: 6px;
  padding: 2px 7px;
  border-radius: 10px;
  font-size: 10.5px;
  font-weight: 700;
  background: #F3F4F6;
  color: #4B5563;
}
.counterpart-badge.student { background: #E0F2FE; color: #0369A1; }
.counterpart-badge.agent { background: #FEF3C7; color: #92400E; }
.counterpart-badge.teacher { background: #DCFCE7; color: #166534; }
.counterpart-badge.instructor { background: #EDE9FE; color: #6D28D9; }

/* Keeps the name column visible while the rest of the row scrolls
   horizontally underneath it. */
.admin-payments-table .sticky-col {
  position: sticky;
  left: 0;
  z-index: 2;
}
.admin-payments-table th.sticky-col { background: #FAFAFA; }
.admin-payments-table td.sticky-col { background: white; }
.admin-payments-table tbody tr:hover td.sticky-col { background: #FAFAFA; }

.student-link {
  font-weight: 600;
  color: #2D6A4F;

  &:hover { text-decoration: underline; }
}

.status-chip {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;

  &.new { background: #E0F2FE; color: #0369A1; }
  &.enrolled { background: #DCFCE7; color: #15803D; }
  &.finished { background: #F3F4F6; color: #4B5563; }
}

.modal-dialog {
  border: none;
  border-radius: 20px;
  padding: 0;
  width: 90%;
  max-width: 620px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  background: white;
  margin: auto;
  overflow: hidden;

  &::backdrop {
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(6px);
  }

  *, *::before, *::after {
    box-sizing: border-box;
  }
}

.user-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  background: linear-gradient(180deg, #F0FDF4 0%, #FFFFFF 100%);
  border-bottom: 1px solid #F3F4F6;
}

.header-badge-wrap {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-badge-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(45, 106, 79, 0.2);

  svg {
    stroke: white;
  }
}

.user-modal-title { font-size: 17px; font-weight: 700; color: #111827; }
.user-modal-sub { font-size: 12px; color: #6B7280; margin-top: 2px; }
.user-btn-close { background: none; border: none; font-size: 18px; color: #9CA3AF; cursor: pointer; }
.user-modal-form { padding: 24px; width: 100%; box-sizing: border-box; }

.pay-info-summary {
  background: #F3F4F6;
  border-radius: 10px;
  padding: 14px 16px;
  margin-bottom: 18px;
  font-size: 13.5px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.pay-info-summary p { margin: 0; color: #4B5563; }
.pay-info-summary strong { color: #111827; }

.form-group { margin-bottom: 16px; width: 100%; min-width: 0; box-sizing: border-box; }
.form-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; width: 100%; box-sizing: border-box; }

.form-label {
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

.form-input {
  width: 100%;
  box-sizing: border-box;
  padding: 11px 14px;
  border: 1.5px solid #E5E7EB;
  border-radius: 10px;
  font-size: 14px;
  background-color: #FAFAFA;
  color: #111827;
  outline: none;
  transition: all 0.2s ease;

  &:focus {
    border-color: #2D6A4F;
    background-color: white;
    box-shadow: 0 0 0 3.5px rgba(45, 106, 79, 0.12);
  }
}

select.form-input {
  cursor: pointer;
}

.form-textarea {
  resize: vertical;
}

.user-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 26px;
}

.btn-cancel {
  padding: 10px 18px;
  border: 1px solid #D1D5DB;
  background: white;
  border-radius: 10px;
  font-weight: 600;
  font-size: 13px;
  color: #374151;
  cursor: pointer;
  transition: background 0.15s ease;

  &:hover {
    background: #F9FAFB;
  }
}

.btn-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 22px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  font-size: 13.5px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(45, 106, 79, 0.25);
  transition: all 0.15s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(45, 106, 79, 0.35);
  }
}

.user-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.avatar-placeholder-large {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F3F4F6;
  border-radius: 50%;
}

/* Image Zoom Modal */
.image-zoom-dialog {
  border: none;
  background: transparent;
  padding: 0;
  max-width: 90vw;
  max-height: 90vh;
  margin: auto;
  overflow: visible;
}
.image-zoom-dialog::backdrop {
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(5px);
}
.image-zoom-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.image-zoom-close {
  position: absolute;
  top: -16px;
  right: -16px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: white;
  color: #111827;
  font-weight: 700;
  font-size: 14px;
  border: none;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  cursor: pointer;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}
.zoomed-img {
  max-width: 85vw;
  max-height: 85vh;
  border-radius: 14px;
  object-fit: contain;
  box-shadow: 0 20px 50px rgba(0,0,0,0.5);
}

.modal-sm { max-width: 460px; }

.modal-alert {
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 13px;
  margin-bottom: 16px;
}
.modal-alert-error { background: #FEE2E2; color: #991B1B; }

.section-header-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }

.btn-leave-review-top {
  display: inline-flex;
  align-items: center;
  padding: 6px 14px;
  background: #FEF3C7;
  color: #92400E;
  border: none;
  border-radius: 20px;
  font-weight: 600;
  font-size: 12px;
  cursor: pointer;
}
.btn-leave-review-top:hover { background: #FDE68A; }

.star-picker { display: flex; gap: 6px; font-size: 26px; }
.star { color: #E5E7EB; cursor: pointer; transition: color 0.15s ease; }
.star.filled { color: #F59E0B; }


/* ── Payments table (staff-only section) ─────────────────── */
.payments-table-wrap {
  overflow: auto;
  max-height: 600px;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  background: white;
}
.payments-table { width: 100%; border-collapse: collapse; }
.payments-table th {
  background: #F9FAFB;
  padding: 11px 14px;
  font-size: 11.5px;
  font-weight: 700;
  color: #4B5563;
  text-align: left;
  border-bottom: 1px solid #E5E7EB;
  white-space: nowrap;
}
.payments-table td {
  padding: 12px 14px;
  font-size: 13px;
  color: #1F2937;
  border-bottom: 1px solid #F3F4F6;
  vertical-align: middle;
}
.payments-table tbody tr:last-child td { border-bottom: none; }
.payments-table tbody tr:hover td { background: #FAFAFA; }
.payments-table thead { position: sticky; top: 0; z-index: 3; }
.payments-table thead tr.col-filter-row th { padding: 8px 10px; background: #FAFAFB; }

.pay-date { color: #6B7280; white-space: nowrap; }
.pay-amount { font-weight: 800; color: #166534; white-space: nowrap; }
.pay-method { color: #6B7280; }
.pay-notes { color: #6B7280; max-width: 240px; }

.pay-status-chip {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11.5px;
  font-weight: 700;
  white-space: nowrap;
}
.pay-status-chip.bonus_teacher { background: #FEF3C7; color: #92400E; }
.pay-status-chip.bonus { background: #FDE68A; color: #92400E; }
.pay-status-chip.paid { background: #DBEAFE; color: #1D4ED8; }
.pay-status-chip.accepted { background: #DCFCE7; color: #15803D; }
.pay-status-chip.returned { background: #FEE2E2; color: #B91C1C; }
.pay-status-chip.bank { background: #EDE9FE; color: #6D28D9; }

.btn-pay-cert-bonus-user {
  margin-top: 4px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #2D6A4F 0%, #1B4332 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  font-size: 11.5px;
  cursor: pointer;
}
</style>
