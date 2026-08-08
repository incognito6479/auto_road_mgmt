<template>
  <AppLayout>

    <div class="page-flex-col" ref="pageFlexColRef">
    <!-- Top action -->
    <div class="page-top">
      <button v-if="authStore.isAdminOrSuperuser" class="btn-add" :disabled="openingModal" @click="openModal">
        <span v-if="openingModal" class="btn-spinner"></span>
        {{ openingModal ? 'Yuklanmoqda...' : "Yangi O'quvchi Qo'shish" }}
      </button>
    </div>

    <!-- Enrollment status tabs -->
    <div class="status-tabs-bar">
      <button
        v-for="tab in statusTabs"
        :key="tab.key"
        type="button"
        class="status-tab-btn"
        :class="{ active: activeTab === tab.key }"
        @click="selectTab(tab.key)"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Loading / error states — only gates the very first load; later
         refetches (filters/sort/pagination) leave the table (and whatever
         column-filter input the user is typing in) mounted the whole time. -->
    <div v-if="initialLoading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">O'quvchilar yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchStudents">Qayta urinish</button>
    </div>

    <!-- Table -->
    <div v-else class="table-wrap">
      <div class="table-scroll-area">
        <table class="stbl">
          <thead>
            <tr>
              <th>To'liq Ismi</th>
              <th>Kategoriya</th>
              <th class="th-phone">Telefon Raqami</th>
              <th>JSHSHR</th>
              <th>Guruh</th>
              <th>Guruh boshlanishi</th>
              <th>Guruh tugashi</th>
              <th>Passport Ma'lumotlari</th>
              <th>Tug'ilgan sana</th>
              <th>Ro'yxatdan o'tgan sana</th>
              <th>To'langan</th>
              <th>Holat</th>
              <th>Eslatma</th>
              <th>Amallar</th>
            </tr>
            <tr class="col-filter-row">
              <th>
                <input
                  v-model="filterName"
                  class="col-filter-input"
                  type="text"
                  placeholder="Ism bo'yicha qidirish..."
                />
              </th>
              <th>
                <div class="select-wrap">
                  <select v-model="filterCategory" class="col-filter-select">
                    <option v-for="c in categories" :key="c.id" :value="c.name">
                      {{ c.name }}
                    </option>
                  </select>
                </div>
              </th>
              <th>
                <input
                  v-model="filterPhone"
                  class="col-filter-input"
                  type="text"
                  placeholder="Telefon bo'yicha qidirish..."
                />
              </th>
              <th>
                <input
                  v-model="filterJshshr"
                  class="col-filter-input"
                  type="text"
                  placeholder="JSHSHR"
                />
              </th>
              <th>
                <input
                  v-model="filterGroupName"
                  class="col-filter-input"
                  type="text"
                  placeholder="Guruh nomi..."
                />
              </th>
              <th>
                <div class="col-sort-group">
                  <button
                    type="button"
                    class="col-sort-icon-btn"
                    :class="{ active: groupStartSort === 'asc' }"
                    title="O'sish tartibida (eskidan yangiga)"
                    @click="setGroupSort('start', 'asc')"
                  >
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 20V4"></path>
                      <path d="M3 8l3-4 3 4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button
                    type="button"
                    class="col-sort-icon-btn"
                    :class="{ active: groupStartSort === 'desc' }"
                    title="Kamayish tartibida (yangidan eskiga)"
                    @click="setGroupSort('start', 'desc')"
                  >
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 4v16"></path>
                      <path d="M3 16l3 4 3-4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button v-if="groupStartDateFrom || groupStartDateTo" type="button" class="btn-clear-date" @click="groupStartDateFrom = ''; groupStartDateTo = ''" title="Tozalash">✕</button>
                </div>
                <div class="col-date-range">
                  <input v-model="groupStartDateFrom" type="date" class="col-date-input" title="Guruh boshlanishi (dan)" />
                  <input v-model="groupStartDateTo" type="date" class="col-date-input" title="Guruh boshlanishi (gacha)" />
                </div>
              </th>
              <th>
                <div class="col-sort-group">
                  <button
                    type="button"
                    class="col-sort-icon-btn"
                    :class="{ active: groupEndSort === 'asc' }"
                    title="O'sish tartibida (eskidan yangiga)"
                    @click="setGroupSort('end', 'asc')"
                  >
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 20V4"></path>
                      <path d="M3 8l3-4 3 4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button
                    type="button"
                    class="col-sort-icon-btn"
                    :class="{ active: groupEndSort === 'desc' }"
                    title="Kamayish tartibida (yangidan eskiga)"
                    @click="setGroupSort('end', 'desc')"
                  >
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 4v16"></path>
                      <path d="M3 16l3 4 3-4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button v-if="groupEndDateFrom || groupEndDateTo" type="button" class="btn-clear-date" @click="groupEndDateFrom = ''; groupEndDateTo = ''" title="Tozalash">✕</button>
                </div>
                <div class="col-date-range">
                  <input v-model="groupEndDateFrom" type="date" class="col-date-input" title="Guruh tugashi (dan)" />
                  <input v-model="groupEndDateTo" type="date" class="col-date-input" title="Guruh tugashi (gacha)" />
                </div>
              </th>
              <th></th>
              <th>
                <div class="col-sort-group">
                  <button
                    type="button"
                    class="col-sort-icon-btn"
                    :class="{ active: birthDateSort === 'asc' }"
                    title="O'sish tartibida (eskidan yangiga)"
                    @click="setGroupSort('birth', 'asc')"
                  >
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 20V4"></path>
                      <path d="M3 8l3-4 3 4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button
                    type="button"
                    class="col-sort-icon-btn"
                    :class="{ active: birthDateSort === 'desc' }"
                    title="Kamayish tartibida (yangidan eskiga)"
                    @click="setGroupSort('birth', 'desc')"
                  >
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 4v16"></path>
                      <path d="M3 16l3 4 3-4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button v-if="birthDateFrom || birthDateTo" type="button" class="btn-clear-date" @click="birthDateFrom = ''; birthDateTo = ''" title="Tozalash">✕</button>
                </div>
                <div class="col-date-range">
                  <input v-model="birthDateFrom" type="date" class="col-date-input" title="Tug'ilgan sana (dan)" />
                  <input v-model="birthDateTo" type="date" class="col-date-input" title="Tug'ilgan sana (gacha)" />
                </div>
              </th>
              <th>
                <div class="col-sort-group">
                  <button
                    type="button"
                    class="col-sort-icon-btn"
                    :class="{ active: joinedDateSort === 'asc' }"
                    title="O'sish tartibida (eskidan yangiga)"
                    @click="setGroupSort('joined', 'asc')"
                  >
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 20V4"></path>
                      <path d="M3 8l3-4 3 4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button
                    type="button"
                    class="col-sort-icon-btn"
                    :class="{ active: joinedDateSort === 'desc' }"
                    title="Kamayish tartibida (yangidan eskiga)"
                    @click="setGroupSort('joined', 'desc')"
                  >
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M6 4v16"></path>
                      <path d="M3 16l3 4 3-4"></path>
                      <text x="12" y="10" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">9</text>
                      <text x="12" y="19" font-size="7.5" font-family="Arial, sans-serif" font-weight="700" stroke="none" fill="currentColor">1</text>
                    </svg>
                  </button>
                  <button v-if="joinedDateFrom || joinedDateTo" type="button" class="btn-clear-date" @click="joinedDateFrom = ''; joinedDateTo = ''" title="Tozalash">✕</button>
                </div>
                <div class="col-date-range">
                  <input v-model="joinedDateFrom" type="date" class="col-date-input" title="Ro'yxatdan o'tgan sana (dan)" />
                  <input v-model="joinedDateTo" type="date" class="col-date-input" title="Ro'yxatdan o'tgan sana (gacha)" />
                </div>
              </th>
              <th colspan="4"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="students.length === 0">
              <td colspan="14" class="no-data">Ma'lumot topilmadi</td>
            </tr>
            <tr v-for="s in students" :key="s.id" class="stbl-row clickable-row" @click="goToStudentDetail(s.id)">
              <td class="td-name">
                <div style="display: flex; align-items: center; gap: 10px;">
                  <img :src="s.image || '/default_photo.png'" alt="Student" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover; border: 1px solid #E5E7EB; flex-shrink: 0;" />
                  <span>{{ s.name }}</span>
                </div>
              </td>
              <td class="td-cat">{{ s.category }}</td>
              <td class="td-muted td-phone">
                <div class="td-phone-main">{{ s.phone }}</div>
                <div v-if="s.phone2" class="td-phone-sub">
                  Qo'shimcha: {{ s.phone2 }}
                </div>
              </td>
              <td class="td-muted">{{ s.jshshr }}</td>
              <td class="td-muted">{{ s.groupName || '-' }}</td>
              <td class="td-muted">{{ s.groupStartedAt || '-' }}</td>
              <td class="td-muted">{{ s.groupEndsAt || '-' }}</td>
              <td class="td-muted">{{ s.passport }}</td>
              <td class="td-muted">{{ s.birthDate || '-' }}</td>
              <td class="td-muted">{{ s.date_joined }}</td>
              <td class="td-muted">
                <span v-if="s.enrolledFree" class="status-badge badge-free">Tekin</span>
                <span v-else>{{ s.paymentAmount }}</span>
              </td>
              <td>
                <span class="status-badge" :class="statusClass(s.status)">{{ s.status }}</span>
              </td>
              <td>
                <div class="td-notes" :title="s.notes">{{ s.notes || '-' }}</div>
              </td>
              <td>
                <button v-if="authStore.isAdminOrSuperuser" class="btn-edit" @click.stop="openEditModal(s)" title="Tahrirlash">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15" style="vertical-align: middle;">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination controls -->
      <div class="pagination-bar">
        <span class="pagination-info">
          Jami: <strong>{{ totalCount }}</strong> tadan <strong>{{ students.length }}</strong> ko'rsatilmoqda
        </span>
        <div class="pagination-actions">
          <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">Oldingi</button>
          <span v-if="pageSizeOption !== 'all'" class="page-num">Sahifa {{ Math.min(currentPage, displayTotalPages) }} / {{ displayTotalPages }}</span>
          <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === displayTotalPages" @click="changePage(currentPage + 1)">Keyingi</button>
          <label class="page-size-label" for="students-page-size">Ko'rsatish:</label>
          <div class="select-wrap">
            <select id="students-page-size" v-model="pageSizeOption" class="page-size-select">
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

    <!-- New Student Modal Dialog -->
    <dialog ref="studentModal" class="modal-dialog" closedby="any" aria-labelledby="modal-title">
      <form class="modal-form" @submit.prevent="saveStudent">
        <h3 id="modal-title" class="modal-title">Yangi o'quvchi qo'shish</h3>

        <div v-if="modalError" class="modal-error">
          {{ modalError }}
        </div>

        <div class="form-grid">
          <!-- Row 1: Personal Details & Photos -->
          <div class="form-group">
            <label for="std-name" class="form-label">F.I.SH. (To'liq ism) *</label>
            <input
              id="std-name"
              v-model="newStudent.full_name"
              type="text"
              placeholder="Masalan: Abdullayev Ali"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="std-phone" class="form-label">Telefon raqami *</label>
            <input
              id="std-phone"
              v-model="newStudent.phone"
              type="tel"
              placeholder="+998 90 123 45 67"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="std-phone2" class="form-label">Qo'shimcha telefon (qarindoshi)</label>
            <input
              id="std-phone2"
              v-model="newStudent.phone2"
              type="text"
              placeholder="+998 90 123 45 67 otasi / amakisi"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label class="form-label">O'quvchi rasmi (foto)</label>
            <FileSelectInput ref="studentPhotoInputRef" accept="image/jpeg,image/png" @change="onStudentPhotoChange" />
          </div>

          <div class="form-group">
            <label class="form-label">Pasport rasmi / nusxasi</label>
            <FileSelectInput ref="passportPhotoInputRef" accept="image/jpeg,image/png,.pdf" @change="onPassportPhotoChange" />
          </div>

          <!-- Row 2: Passport & JSHSHR -->
          <div class="form-group">
            <label for="std-jshshr" class="form-label">JSHSHR (14 xonali raqam)</label>
            <input
              id="std-jshshr"
              v-model="newStudent.jshshr"
              type="text"
              placeholder="Masalan: 30101990001014"
              required
              maxlength="14"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="std-pass-serie" class="form-label">Pass. Seriya</label>
            <input
              id="std-pass-serie"
              v-model="newStudent.passport_serie"
              type="text"
              placeholder="AA"
              required
              maxlength="2"
              class="form-input text-uppercase"
            />
          </div>

          <div class="form-group">
            <label for="std-pass-num" class="form-label">Pass. Raqam</label>
            <input
              id="std-pass-num"
              v-model="newStudent.passport_number"
              type="text"
              placeholder="1234567"
              required
              maxlength="7"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="std-birth-date" class="form-label">Tug'ilgan sana</label>
            <input
              id="std-birth-date"
              v-model="newStudent.birth_date"
              type="date"
              required
              class="form-input"
            />
          </div>

          <!-- Row 3: Category, Learning Place, Learning Time -->
          <div class="form-group">
            <label for="std-cat" class="form-label">Kategoriya</label>
            <div class="select-wrap">
              <select id="std-cat" v-model="newStudent.category" required class="form-input select-input">
                <option value="" disabled>Kategoriyani tanlang</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
              <svg class="select-arrow-modal" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
              </svg>
            </div>
          </div>

          <div class="form-group">
            <label for="std-place" class="form-label">O'quv Joyi (ixtiyoriy)</label>
            <div class="select-wrap">
              <select id="std-place" v-model="newStudent.learning_place" class="form-input select-input">
                <option :value="null">-- O'quv joyini tanlang --</option>
                <option v-for="place in learningPlaces" :key="place.id" :value="place.id">
                  {{ place.place_name }}
                </option>
              </select>
              <svg class="select-arrow-modal" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
              </svg>
            </div>
          </div>

          <div class="form-group">
            <label for="std-time" class="form-label">O'quv Vaqti (ixtiyoriy)</label>
            <input
              id="std-time"
              v-model="newStudent.learning_time"
              type="text"
              placeholder="Masalan: 09:00"
              class="form-input"
            />
          </div>

          <!-- Row 4: Learning Days, Instructor, Coordinator -->
          <div class="form-group fg-full">
            <label class="form-label">O'quv Kunlari (ixtiyoriy)</label>
            <div class="weekday-picker">
              <label v-for="d in weekdayOptions" :key="d.value" class="weekday-chip" :class="{ active: newStudent.learning_days.includes(d.value) }">
                <input type="checkbox" :value="d.value" v-model="newStudent.learning_days" style="display: none;" />
                {{ d.label }}
              </label>
            </div>
          </div>

          <!-- Instruktor Searchable Select -->
          <div class="form-group staff-select-group">
            <label class="form-label">Instruktor (ixtiyoriy)</label>
            <div class="search-select-container">
              <div 
                class="search-select-trigger" 
                :class="{ 'is-open': isInstructorOpen, 'has-selected': selectedInstructor }"
                @click="isInstructorOpen = !isInstructorOpen; isCoordinatorOpen = false; isAgentOpen = false"
              >
                <template v-if="selectedInstructor">
                  <div class="selected-user-card">
                    <div class="user-avatar-badge avatar-inst">
                      {{ selectedInstructor.first_name?.[0] || 'I' }}
                    </div>
                    <div class="selected-user-details">
                      <span class="selected-user-name">{{ getUserFullName(selectedInstructor) }}</span>
                      <span class="selected-user-phone">{{ formatPhoneDisplay(selectedInstructor.phone) }}</span>
                    </div>
                    <button type="button" class="btn-remove-selection" @click.stop="selectInstructor(null)" title="Tozalash">✕</button>
                  </div>
                </template>
                <template v-else>
                  <div class="select-placeholder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
                      <circle cx="11" cy="11" r="8"></circle>
                      <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    <span>Instruktorni tanlash uchun bosing...</span>
                  </div>
                  <svg class="select-arrow-icon" :class="{ 'rotate': isInstructorOpen }" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                    <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
                  </svg>
                </template>
              </div>

              <!-- Dropdown Popup -->
              <div v-if="isInstructorOpen" class="search-select-dropdown" @click.stop>
                <div class="dropdown-search-wrap">
                  <input
                    type="text"
                    v-model="instructorSearch"
                    placeholder="Ism yoki telefon raqami..."
                    class="dropdown-search-field"
                    autofocus
                    @keydown="onInstructorKeydown"
                  />
                </div>
                <div class="dropdown-options-container">
                  <div
                    class="dropdown-option-row option-clear"
                    :class="{ 'is-active': !newStudent.instructor }"
                    @click="selectInstructor(null)"
                  >
                    <span>&lt; Tanlanmagan &gt;</span>
                  </div>
                  <div
                    v-for="(inst, idx) in filteredInstructors"
                    :key="inst.id"
                    class="dropdown-option-row"
                    :class="{ 'is-active': newStudent.instructor === inst.id, 'is-highlighted': instructorKb.highlightedIndex.value === idx }"
                    @click="selectInstructor(inst.id)"
                  >
                    <div class="opt-avatar avatar-inst">
                      {{ inst.first_name?.[0] || 'I' }}
                    </div>
                    <div class="opt-info">
                      <span class="opt-name">{{ getUserFullName(inst) }}</span>
                      <span class="opt-phone">{{ formatPhoneDisplay(inst.phone) }}</span>
                    </div>
                    <span v-if="newStudent.instructor === inst.id" class="opt-check">✓</span>
                  </div>
                  <div v-if="filteredInstructors.length === 0" class="dropdown-empty">
                    Instruktor topilmadi
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- O'qituvchi Searchable Select -->
          <div class="form-group staff-select-group">
            <label class="form-label">O'qituvchi (ixtiyoriy)</label>
            <div class="search-select-container">
              <div 
                class="search-select-trigger" 
                :class="{ 'is-open': isCoordinatorOpen, 'has-selected': selectedCoordinator }"
                @click="isCoordinatorOpen = !isCoordinatorOpen; isInstructorOpen = false; isAgentOpen = false"
              >
                <template v-if="selectedCoordinator">
                  <div class="selected-user-card">
                    <div class="user-avatar-badge avatar-coord">
                      {{ selectedCoordinator.first_name?.[0] || 'O' }}
                    </div>
                    <div class="selected-user-details">
                      <span class="selected-user-name">{{ getUserFullName(selectedCoordinator) }}</span>
                      <span class="selected-user-phone">{{ formatPhoneDisplay(selectedCoordinator.phone) }}</span>
                    </div>
                    <button type="button" class="btn-remove-selection" @click.stop="selectCoordinator(null)" title="Tozalash">✕</button>
                  </div>
                </template>
                <template v-else>
                  <div class="select-placeholder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
                      <circle cx="11" cy="11" r="8"></circle>
                      <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    <span>O'qituvchini tanlash uchun bosing...</span>
                  </div>
                  <svg class="select-arrow-icon" :class="{ 'rotate': isCoordinatorOpen }" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                    <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
                  </svg>
                </template>
              </div>

              <!-- Dropdown Popup -->
              <div v-if="isCoordinatorOpen" class="search-select-dropdown" @click.stop>
                <div class="dropdown-search-wrap">
                  <input
                    type="text"
                    v-model="coordinatorSearch"
                    placeholder="Ism yoki telefon raqami..."
                    class="dropdown-search-field"
                    autofocus
                    @keydown="onCoordinatorKeydown"
                  />
                </div>
                <div class="dropdown-options-container">
                  <div
                    class="dropdown-option-row option-clear"
                    :class="{ 'is-active': !newStudent.coordinator }"
                    @click="selectCoordinator(null)"
                  >
                    <span>&lt; Tanlanmagan &gt;</span>
                  </div>
                  <div
                    v-for="(coord, idx) in filteredCoordinators"
                    :key="coord.id"
                    class="dropdown-option-row"
                    :class="{ 'is-active': newStudent.coordinator === coord.id, 'is-highlighted': coordinatorKb.highlightedIndex.value === idx }"
                    @click="selectCoordinator(coord.id)"
                  >
                    <div class="opt-avatar avatar-coord">
                      {{ coord.first_name?.[0] || 'O' }}
                    </div>
                    <div class="opt-info">
                      <span class="opt-name">{{ getUserFullName(coord) }}</span>
                      <span class="opt-phone">{{ formatPhoneDisplay(coord.phone) }}</span>
                    </div>
                    <span v-if="newStudent.coordinator === coord.id" class="opt-check">✓</span>
                  </div>
                  <div v-if="filteredCoordinators.length === 0" class="dropdown-empty">
                    O'qituvchi topilmadi
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Agent Searchable Select -->
          <div class="form-group staff-select-group">
            <label class="form-label">Agent (ixtiyoriy)</label>
            <div class="search-select-container">
              <div 
                class="search-select-trigger" 
                :class="{ 'is-open': isAgentOpen, 'has-selected': selectedAgent }"
                @click="isAgentOpen = !isAgentOpen; isInstructorOpen = false; isCoordinatorOpen = false"
              >
                <template v-if="selectedAgent">
                  <div class="selected-user-card">
                    <div class="user-avatar-badge avatar-agent">
                      {{ selectedAgent.full_name?.[0] || 'A' }}
                    </div>
                    <div class="selected-user-details">
                      <span class="selected-user-name">{{ selectedAgent.full_name }}</span>
                      <span class="selected-user-phone">{{ formatPhoneDisplay(selectedAgent.phone) }}</span>
                    </div>
                    <button type="button" class="btn-remove-selection" @click.stop="selectAgent(null)" title="Tozalash">✕</button>
                  </div>
                </template>
                <template v-else>
                  <div class="select-placeholder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
                      <circle cx="11" cy="11" r="8"></circle>
                      <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    <span>Agentni tanlash...</span>
                  </div>
                  <svg class="select-arrow-icon" :class="{ 'rotate': isAgentOpen }" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                    <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
                  </svg>
                </template>
              </div>

              <!-- Dropdown Popup -->
              <div v-if="isAgentOpen" class="search-select-dropdown" @click.stop>
                <div class="dropdown-search-wrap">
                  <input
                    type="text"
                    v-model="agentSearch"
                    placeholder="Agent ismi yoki telefon..."
                    class="dropdown-search-field"
                    autofocus
                    @keydown="onAgentKeydown"
                  />
                </div>
                <div class="dropdown-options-container">
                  <div
                    class="dropdown-option-row option-clear"
                    :class="{ 'is-active': !newStudent.agent }"
                    @click="selectAgent(null)"
                  >
                    <span>&lt; Tanlanmagan &gt;</span>
                  </div>
                  <div
                    v-for="(ag, idx) in filteredAgents"
                    :key="ag.id"
                    class="dropdown-option-row"
                    :class="{ 'is-active': newStudent.agent === ag.id, 'is-highlighted': agentKb.highlightedIndex.value === idx }"
                    @click="selectAgent(ag.id)"
                  >
                    <div class="opt-avatar avatar-agent">
                      {{ ag.full_name?.[0] || 'A' }}
                    </div>
                    <div class="opt-info">
                      <span class="opt-name">{{ ag.full_name }}</span>
                      <span class="opt-phone">{{ formatPhoneDisplay(ag.phone) }}</span>
                    </div>
                    <span v-if="newStudent.agent === ag.id" class="opt-check">✓</span>
                  </div>
                  <div v-if="filteredAgents.length === 0" class="dropdown-empty">
                    Agent topilmadi
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Row 5: Payment Info -->
          <div v-if="!newStudent.enrolled_free" class="form-group">
            <label for="std-payment" class="form-label">Boshlang'ich to'lov (so'm)</label>
            <input
              id="std-payment"
              v-model="formattedMinPayment"
              type="text"
              placeholder="Masalan: 1 000 000"
              required
              class="form-input"
            />
          </div>

          <div v-if="!newStudent.enrolled_free" class="form-group">
            <label for="std-payment-method" class="form-label">To'lov turi</label>
            <div class="select-wrap">
              <select id="std-payment-method" v-model="newStudent.payment_method" required class="form-input select-input">
                <option value="cash">Naqd</option>
                <option value="card">Karta</option>
                <option value="qr_code">QR code</option>
                <option value="click">Click</option>
                <option value="transfer">O'tkazma</option>
              </select>
              <svg class="select-arrow-modal" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
              </svg>
            </div>
          </div>

          <!-- Row 6: Checkboxes, Custom Price & Notes -->
          <div v-if="authStore.canManageFinances" class="form-group checkbox-group" style="grid-column: span 3; display: flex; align-items: center; gap: 24px; margin-top: 8px;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <input
                id="std-enrolled-free"
                v-model="newStudent.enrolled_free"
                type="checkbox"
                class="form-checkbox"
              />
              <label for="std-enrolled-free" class="form-checkbox-label" style="font-weight: 600; color: #374151; cursor: pointer; font-size: 13.5px;">Bepul o'qish (Grant)</label>
            </div>
            <div v-if="!newStudent.enrolled_free" style="display: flex; align-items: center; gap: 8px;">
              <input
                id="std-custom-price-chk"
                v-model="newStudent.has_custom_price"
                type="checkbox"
                class="form-checkbox"
              />
              <label for="std-custom-price-chk" class="form-checkbox-label" style="font-weight: 600; color: #374151; cursor: pointer; font-size: 13.5px;">Maxsus shartnoma summasi belgilash</label>
            </div>
          </div>

          <div v-if="authStore.canManageFinances && newStudent.has_custom_price && !newStudent.enrolled_free" class="form-group" style="grid-column: span 3;">
            <label for="std-enrolled-amount" class="form-label">Shartnoma summasi (so'm)</label>
            <input
              id="std-enrolled-amount"
              v-model="formattedEnrolledAmount"
              type="text"
              placeholder="Masalan: 4 000 000"
              required
              class="form-input"
            />
          </div>

          <div class="form-group checkbox-group" style="grid-column: span 3; display: flex; align-items: center; gap: 8px; margin-top: 8px;">
            <input
              id="std-can-view-payments"
              v-model="newStudent.can_view_payments"
              type="checkbox"
              class="form-checkbox"
            />
            <label for="std-can-view-payments" class="form-checkbox-label" style="font-weight: 600; color: #374151; cursor: pointer; font-size: 13.5px;">O'quvchi to'lovlar tarixini ko'ra oladi</label>
          </div>
          <div class="form-group" style="grid-column: span 3;">
            <label for="std-notes" class="form-label">Eslatmalar</label>
            <textarea
              id="std-notes"
              v-model="newStudent.notes"
              placeholder="Qo'shimcha eslatmalar..."
              class="form-input"
              rows="2"
              style="resize: vertical; font-family: inherit; padding: 10px;"
            ></textarea>
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closeModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="saving">
            <span v-if="saving" class="btn-spinner"></span>
            {{ saving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Edit Student Modal Dialog -->
    <dialog ref="editStudentModal" class="modal-dialog" closedby="any" aria-labelledby="edit-modal-title">
      <form class="modal-form" @submit.prevent="updateStudent">
        <h3 id="edit-modal-title" class="modal-title">O'quvchi ma'lumotlarini tahrirlash</h3>

        <div v-if="editModalError" class="modal-error">
          {{ editModalError }}
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label for="edit-std-name" class="form-label">F.I.SH. (To'liq ism)</label>
            <input
              id="edit-std-name"
              v-model="editingStudent.full_name"
              type="text"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="edit-std-phone" class="form-label">Telefon raqami</label>
            <input
              id="edit-std-phone"
              v-model="editingStudent.phone"
              type="tel"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="edit-std-phone2" class="form-label">Qo'shimcha telefon (qarindoshi)</label>
            <input
              id="edit-std-phone2"
              v-model="editingStudent.phone2"
              type="text"
              placeholder="+998 90 123 45 67 otasi / amakisi"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label class="form-label">O'quvchi rasmi (foto)</label>
            <FileSelectInput ref="editStudentPhotoInputRef" accept="image/jpeg,image/png" @change="onEditStudentPhotoChange" />
          </div>

          <div class="form-group">
            <label class="form-label">Pasport rasmi / nusxasi</label>
            <FileSelectInput ref="editPassportPhotoInputRef" accept="image/jpeg,image/png,.pdf" @change="onEditPassportPhotoChange" />
          </div>

          <div class="form-group">
            <label for="edit-std-jshshr" class="form-label">JSHSHR (14 xonali raqam)</label>
            <input
              id="edit-std-jshshr"
              v-model="editingStudent.jshshr"
              type="text"
              required
              maxlength="14"
              class="form-input"
            />
          </div>

          <div class="form-row-group">
            <div class="form-group half-width">
              <label for="edit-std-pass-serie" class="form-label">Pass. Seriya</label>
              <input
                id="edit-std-pass-serie"
                v-model="editingStudent.passport_serie"
                type="text"
                required
                maxlength="2"
                class="form-input text-uppercase"
              />
            </div>
            <div class="form-group half-width">
              <label for="edit-std-pass-num" class="form-label">Pass. Raqam</label>
              <input
                id="edit-std-pass-num"
                v-model="editingStudent.passport_number"
                type="text"
                required
                maxlength="7"
                class="form-input"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="edit-std-birth-date" class="form-label">Tug'ilgan sana</label>
            <input
              id="edit-std-birth-date"
              v-model="editingStudent.birth_date"
              type="date"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="edit-std-category" class="form-label">Kategoriya</label>
            <div class="select-wrap">
              <select id="edit-std-category" v-model="editingStudent.category" required class="filter-select">
                <option value="" disabled>Kategoriyani tanlang</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
              <span class="select-arrow" style="top: 10px;">▼</span>
            </div>
          </div>

          <div class="form-group">
            <label for="edit-std-status" class="form-label">Holat</label>
            <div class="select-wrap">
              <select id="edit-std-status" v-model="editingStudent.status" required class="filter-select">
                <option value="new">Yangi</option>
                <option value="enrolled">Faol</option>
                <option value="finished">Tugatgan</option>
                <option value="canceled">Bekor qilingan</option>
              </select>
              <span class="select-arrow" style="top: 10px;">▼</span>
            </div>
          </div>

          <div class="form-group">
            <label for="edit-std-time" class="form-label">O'quv Vaqti (ixtiyoriy)</label>
            <input
              id="edit-std-time"
              v-model="editingStudent.learning_time"
              type="text"
              placeholder="Masalan: 09:00"
              class="form-input"
            />
          </div>

          <div class="form-group fg-full">
            <label class="form-label">O'quv Kunlari (ixtiyoriy)</label>
            <div class="weekday-picker">
              <label v-for="d in weekdayOptions" :key="d.value" class="weekday-chip" :class="{ active: editingStudent.learning_days.includes(d.value) }">
                <input type="checkbox" :value="d.value" v-model="editingStudent.learning_days" style="display: none;" />
                {{ d.label }}
              </label>
            </div>
          </div>

          <!-- Instruktor Searchable Select -->
          <div class="form-group staff-select-group">
            <label class="form-label">Instruktor</label>
            <div class="search-select-container">
              <div
                class="search-select-trigger"
                :class="{ 'is-open': isEditInstructorOpen, 'has-selected': selectedEditInstructor }"
                @click="isEditInstructorOpen = !isEditInstructorOpen; isEditCoordinatorOpen = false; isEditAgentOpen = false"
              >
                <template v-if="selectedEditInstructor">
                  <div class="selected-user-card">
                    <div class="user-avatar-badge avatar-inst">
                      {{ selectedEditInstructor.first_name?.[0] || 'I' }}
                    </div>
                    <div class="selected-user-details">
                      <span class="selected-user-name">{{ getUserFullName(selectedEditInstructor) }}</span>
                      <span class="selected-user-phone">{{ formatPhoneDisplay(selectedEditInstructor.phone) }}</span>
                    </div>
                    <button type="button" class="btn-remove-selection" @click.stop="selectEditInstructor(null)" title="Tozalash">✕</button>
                  </div>
                </template>
                <template v-else>
                  <div class="select-placeholder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
                      <circle cx="11" cy="11" r="8"></circle>
                      <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    <span>Instruktorni tanlash uchun bosing...</span>
                  </div>
                  <svg class="select-arrow-icon" :class="{ 'rotate': isEditInstructorOpen }" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                    <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
                  </svg>
                </template>
              </div>

              <div v-if="isEditInstructorOpen" class="search-select-dropdown" @click.stop>
                <div class="dropdown-search-wrap">
                  <input type="text" v-model="editInstructorSearch" placeholder="Ism yoki telefon raqami..." class="dropdown-search-field" autofocus @keydown="onEditInstructorKeydown" />
                </div>
                <div class="dropdown-options-container">
                  <div class="dropdown-option-row option-clear" :class="{ 'is-active': !editingStudent.instructor }" @click="selectEditInstructor(null)">
                    <span>&lt; Tanlanmagan &gt;</span>
                  </div>
                  <div
                    v-for="(inst, idx) in filteredEditInstructors"
                    :key="inst.id"
                    class="dropdown-option-row"
                    :class="{ 'is-active': editingStudent.instructor === inst.id, 'is-highlighted': editInstructorKb.highlightedIndex.value === idx }"
                    @click="selectEditInstructor(inst.id)"
                  >
                    <div class="opt-avatar avatar-inst">{{ inst.first_name?.[0] || 'I' }}</div>
                    <div class="opt-info">
                      <span class="opt-name">{{ getUserFullName(inst) }}</span>
                      <span class="opt-phone">{{ formatPhoneDisplay(inst.phone) }}</span>
                    </div>
                    <span v-if="editingStudent.instructor === inst.id" class="opt-check">✓</span>
                  </div>
                  <div v-if="filteredEditInstructors.length === 0" class="dropdown-empty">Instruktor topilmadi</div>
                </div>
              </div>
            </div>
          </div>

          <!-- O'qituvchi Searchable Select -->
          <div class="form-group staff-select-group">
            <label class="form-label">O'qituvchi</label>
            <div class="search-select-container">
              <div
                class="search-select-trigger"
                :class="{ 'is-open': isEditCoordinatorOpen, 'has-selected': selectedEditCoordinator }"
                @click="isEditCoordinatorOpen = !isEditCoordinatorOpen; isEditInstructorOpen = false; isEditAgentOpen = false"
              >
                <template v-if="selectedEditCoordinator">
                  <div class="selected-user-card">
                    <div class="user-avatar-badge avatar-coord">
                      {{ selectedEditCoordinator.first_name?.[0] || 'O' }}
                    </div>
                    <div class="selected-user-details">
                      <span class="selected-user-name">{{ getUserFullName(selectedEditCoordinator) }}</span>
                      <span class="selected-user-phone">{{ formatPhoneDisplay(selectedEditCoordinator.phone) }}</span>
                    </div>
                    <button type="button" class="btn-remove-selection" @click.stop="selectEditCoordinator(null)" title="Tozalash">✕</button>
                  </div>
                </template>
                <template v-else>
                  <div class="select-placeholder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
                      <circle cx="11" cy="11" r="8"></circle>
                      <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    <span>O'qituvchini tanlash uchun bosing...</span>
                  </div>
                  <svg class="select-arrow-icon" :class="{ 'rotate': isEditCoordinatorOpen }" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                    <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
                  </svg>
                </template>
              </div>

              <div v-if="isEditCoordinatorOpen" class="search-select-dropdown" @click.stop>
                <div class="dropdown-search-wrap">
                  <input type="text" v-model="editCoordinatorSearch" placeholder="Ism yoki telefon raqami..." class="dropdown-search-field" autofocus @keydown="onEditCoordinatorKeydown" />
                </div>
                <div class="dropdown-options-container">
                  <div class="dropdown-option-row option-clear" :class="{ 'is-active': !editingStudent.coordinator }" @click="selectEditCoordinator(null)">
                    <span>&lt; Tanlanmagan &gt;</span>
                  </div>
                  <div
                    v-for="(coord, idx) in filteredEditCoordinators"
                    :key="coord.id"
                    class="dropdown-option-row"
                    :class="{ 'is-active': editingStudent.coordinator === coord.id, 'is-highlighted': editCoordinatorKb.highlightedIndex.value === idx }"
                    @click="selectEditCoordinator(coord.id)"
                  >
                    <div class="opt-avatar avatar-coord">{{ coord.first_name?.[0] || 'O' }}</div>
                    <div class="opt-info">
                      <span class="opt-name">{{ getUserFullName(coord) }}</span>
                      <span class="opt-phone">{{ formatPhoneDisplay(coord.phone) }}</span>
                    </div>
                    <span v-if="editingStudent.coordinator === coord.id" class="opt-check">✓</span>
                  </div>
                  <div v-if="filteredEditCoordinators.length === 0" class="dropdown-empty">O'qituvchi topilmadi</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Agent Searchable Select -->
          <div class="form-group staff-select-group">
            <label class="form-label">Agent</label>
            <div class="search-select-container">
              <div
                class="search-select-trigger"
                :class="{ 'is-open': isEditAgentOpen, 'has-selected': selectedEditAgent }"
                @click="isEditAgentOpen = !isEditAgentOpen; isEditInstructorOpen = false; isEditCoordinatorOpen = false"
              >
                <template v-if="selectedEditAgent">
                  <div class="selected-user-card">
                    <div class="user-avatar-badge avatar-agent">
                      {{ selectedEditAgent.full_name?.[0] || 'A' }}
                    </div>
                    <div class="selected-user-details">
                      <span class="selected-user-name">{{ selectedEditAgent.full_name }}</span>
                      <span class="selected-user-phone">{{ formatPhoneDisplay(selectedEditAgent.phone) }}</span>
                    </div>
                    <button type="button" class="btn-remove-selection" @click.stop="selectEditAgent(null)" title="Tozalash">✕</button>
                  </div>
                </template>
                <template v-else>
                  <div class="select-placeholder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
                      <circle cx="11" cy="11" r="8"></circle>
                      <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    <span>Agentni tanlash...</span>
                  </div>
                  <svg class="select-arrow-icon" :class="{ 'rotate': isEditAgentOpen }" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                    <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
                  </svg>
                </template>
              </div>

              <div v-if="isEditAgentOpen" class="search-select-dropdown" @click.stop>
                <div class="dropdown-search-wrap">
                  <input type="text" v-model="editAgentSearch" placeholder="Agent ismi yoki telefon..." class="dropdown-search-field" autofocus @keydown="onEditAgentKeydown" />
                </div>
                <div class="dropdown-options-container">
                  <div class="dropdown-option-row option-clear" :class="{ 'is-active': !editingStudent.agent }" @click="selectEditAgent(null)">
                    <span>&lt; Tanlanmagan &gt;</span>
                  </div>
                  <div
                    v-for="(ag, idx) in filteredEditAgents"
                    :key="ag.id"
                    class="dropdown-option-row"
                    :class="{ 'is-active': editingStudent.agent === ag.id, 'is-highlighted': editAgentKb.highlightedIndex.value === idx }"
                    @click="selectEditAgent(ag.id)"
                  >
                    <div class="opt-avatar avatar-agent">{{ ag.full_name?.[0] || 'A' }}</div>
                    <div class="opt-info">
                      <span class="opt-name">{{ ag.full_name }}</span>
                      <span class="opt-phone">{{ formatPhoneDisplay(ag.phone) }}</span>
                    </div>
                    <span v-if="editingStudent.agent === ag.id" class="opt-check">✓</span>
                  </div>
                  <div v-if="filteredEditAgents.length === 0" class="dropdown-empty">Agent topilmadi</div>
                </div>
              </div>
            </div>
          </div>

          <div class="form-group" style="grid-column: span 2;">
            <label for="edit-std-notes" class="form-label">Eslatmalar</label>
            <textarea
              id="edit-std-notes"
              v-model="editingStudent.notes"
              placeholder="Qo'shimcha eslatmalar..."
              class="form-input"
              rows="3"
              style="resize: vertical; font-family: inherit; padding: 10px;"
            ></textarea>
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

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import FileSelectInput from '@/components/FileSelectInput.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useBranchStore } from '@/stores/branch'
import { useSearchSelectKeyboard } from '@/composables/useSearchSelectKeyboard'
import { useFillViewportHeight } from '@/composables/useFillViewportHeight'
import { debounce } from '@/utils/debounce'

const pageFlexColRef = ref(null)
useFillViewportHeight(pageFlexColRef)

const weekdayOptions = [
  { value: 0, label: 'Dush' },
  { value: 1, label: 'Sesh' },
  { value: 2, label: 'Chor' },
  { value: 3, label: 'Pay' },
  { value: 4, label: 'Juma' },
  { value: 5, label: 'Shan' },
]

const authStore = useAuthStore()
const branchStore = useBranchStore()
const router = useRouter()
const route = useRoute()

const goToStudentDetail = (id) => {
  router.push(`/students/${id}`)
}

// ── Filter state ─────────────────────────────────────────────
const filterStatus = ref('Faol')
// Persisted so revisiting this view (e.g. back from a student's detail
// page) restores the last category filter instead of re-loading the
// full ~6k-row "faol" tab unfiltered.
const filterCategory = ref(localStorage.getItem('students_filter_category') || '')
const filterName = ref('')
const filterPhone = ref('')
const filterJshshr = ref('')
const filterGroupName = ref('')
const groupFilter = ref('') // '', 'true' (guruhga olingan), 'false' (guruhga olinmagan)

// ── Date-column sorting & date-range filters (all client-side) ──────
const groupStartSort = ref('') // '', 'asc', 'desc'
const groupEndSort = ref('')
const birthDateSort = ref('')
const joinedDateSort = ref('')
const groupStartDateFrom = ref('')
const groupStartDateTo = ref('')
const groupEndDateFrom = ref('')
const groupEndDateTo = ref('')
const birthDateFrom = ref('')
const birthDateTo = ref('')
const joinedDateFrom = ref('')
const joinedDateTo = ref('')

// Clicking the already-active direction clears the sort; clicking the other
// direction (or another column) switches to it. Only one column sorts at a time.
function setGroupSort(column, direction) {
  const refs = { start: groupStartSort, end: groupEndSort, birth: birthDateSort, joined: joinedDateSort }
  const target = refs[column]
  Object.entries(refs).forEach(([key, r]) => {
    if (key !== column) r.value = ''
  })
  target.value = target.value === direction ? '' : direction
  currentPage.value = 1
  fetchStudents()
}

// ── Enrollment status tabs ─────────────────────────────────────
// Defaults to "Faol" (active) rather than the full historical roster —
// students stay in the table permanently after finishing, so "Barchasi"
// only grows over time and was making the everyday page load slower every
// month; the day-to-day case only needs currently-active students anyway.
const activeTab = ref('Faol')
const statusTabs = [
  { key: 'Yangi', label: 'Yangi' },
  { key: 'Faol', label: 'Faol' },
  { key: 'Tugatgan', label: 'Tugatgan' },
  { key: 'Bekor qilingan', label: 'Bekor qilingan' },
  { key: 'has_group', label: 'Guruhga olingan' },
  { key: 'no_group', label: 'Guruhga olinmagan' },
]

function selectTab(key) {
  activeTab.value = key
  if (key === 'has_group') {
    filterStatus.value = ''
    groupFilter.value = 'true'
  } else if (key === 'no_group') {
    filterStatus.value = ''
    groupFilter.value = 'false'
  } else {
    filterStatus.value = key
    groupFilter.value = ''
  }
}

// ── Row-fetch-count selector ──────────────────────────────────
// Controls the page_size sent to the backend. Filtering/sorting/pagination
// are all done server-side (see fetchStudents) — the table only ever
// holds the current page's rows, not the whole scoped table.
const pageSizeOption = ref('50')
const totalCount = ref(0) // total rows matching every active filter, per backend
const currentPage = ref(1)

// ── Loading & state ──────────────────────────────────────────
const students = ref([])
const categories = ref([])
const loading = ref(false)
// Only gates the initial full-page spinner. Re-using `loading` for that
// meant every filter/sort/page refetch unmounted the whole table (via
// v-if) — including whatever column-filter <input> the user was typing
// into — stealing focus and resetting cursor position on every keystroke.
const initialLoading = ref(true)
const error = ref('')

// ── Modal state ──────────────────────────────────────────────
const studentModal = ref(null)
const newStudent = ref({
  full_name: '',
  phone: '',
  phone2: '',
  jshshr: '',
  passport_serie: '',
  passport_number: '',
  birth_date: '',
  category: '',
  learning_days: [],
  min_payment: null,
  enrolled_free: false,
  has_custom_price: false,
  enrolled_amount: null,
  can_view_payments: true,
  notes: '',
})
const saving = ref(false)
const modalError = ref('')

const selectedStudentPhoto = ref(null)
const selectedPassportPhoto = ref(null)
const selectedEditStudentPhoto = ref(null)
const selectedEditPassportPhoto = ref(null)
const studentPhotoInputRef = ref(null)
const passportPhotoInputRef = ref(null)
const editStudentPhotoInputRef = ref(null)
const editPassportPhotoInputRef = ref(null)

function onStudentPhotoChange(e) {
  selectedStudentPhoto.value = e.target.files?.[0] || null
}
function onPassportPhotoChange(e) {
  selectedPassportPhoto.value = e.target.files?.[0] || null
}
function onEditStudentPhotoChange(e) {
  selectedEditStudentPhoto.value = e.target.files?.[0] || null
}
function onEditPassportPhotoChange(e) {
  selectedEditPassportPhoto.value = e.target.files?.[0] || null
}

// ── Edit Modal state ─────────────────────────────────────────
const editStudentModal = ref(null)
const editingStudent = ref({
  id: null,
  full_name: '',
  phone: '',
  phone2: '',
  jshshr: '',
  passport_serie: '',
  passport_number: '',
  birth_date: '',
  category: '',
  status: '',
  instructor: null,
  coordinator: null,
  agent: null,
  notes: '',
  learning_time: '',
  learning_days: [],
})
const editSaving = ref(false)
const editModalError = ref('')

watch(() => editingStudent.value.phone, (newValue) => {
  if (!newValue) return
  let digits = newValue.replace(/\D/g, '')

  if (digits.length > 0 && !digits.startsWith('998')) {
    digits = '998' + digits
  }

  digits = digits.substring(0, 12)

  let formatted = ''
  if (digits.length > 0) {
    formatted += '+' + digits.substring(0, 3)
  }
  if (digits.length > 3) {
    formatted += ' ' + digits.substring(3, 5)
  }
  if (digits.length > 5) {
    formatted += ' ' + digits.substring(5, 8)
  }
  if (digits.length > 8) {
    formatted += ' ' + digits.substring(8, 10)
  }
  if (digits.length > 10) {
    formatted += ' ' + digits.substring(10, 12)
  }

  if (newValue !== formatted) {
    editingStudent.value.phone = formatted
  }
})

// phone2 is intentionally free-form (e.g. "+998 90 900 90 90 uncle") — no
// auto-reformatting here, unlike the primary `phone` field, since it also
// doubles as a relative/relation label field.

const openEditModal = async (student) => {
  selectedEditStudentPhoto.value = null
  selectedEditPassportPhoto.value = null
  editStudentPhotoInputRef.value?.reset()
  editPassportPhotoInputRef.value?.reset()
  editingStudent.value = {
    id: student.id,
    full_name: student.name,
    phone: student.phone,
    phone2: student.phone2 || '',
    jshshr: student.jshshr,
    passport_serie: student.passportSerie,
    passport_number: student.passportNumber,
    birth_date: student.birthDateRaw || '',
    category: student.categoryId || '',
    status: student.rawStatus,
    instructor: student.instructor || null,
    coordinator: student.coordinator || null,
    agent: student.agent || null,
    notes: student.notes || '',
    learning_time: student.learning_time || '',
    learning_days: student.learning_days || [],
  }
  editModalError.value = ''

  // Reset any stray open/search state from a previous use of these selects.
  isEditInstructorOpen.value = false
  editInstructorSearch.value = ''
  isEditCoordinatorOpen.value = false
  editCoordinatorSearch.value = ''
  isEditAgentOpen.value = false
  editAgentSearch.value = ''

  // Belt-and-suspenders: make sure the option lists are populated even if
  // the initial page-load fetch hasn't resolved yet.
  if (!staffInstructors.value.length || !staffCoordinators.value.length) fetchStaff()
  if (!agents.value.length) fetchAgents()

  if (editStudentModal.value) {
    editStudentModal.value.showModal()
  }
}

const closeEditModal = () => {
  if (editStudentModal.value) {
    editStudentModal.value.close()
  }
}

const updateStudent = async () => {
  const s = editingStudent.value
  const phoneCleaned = s.phone.replace(/\D/g, '')

  if (!s.full_name.trim() || !phoneCleaned || !s.jshshr || !s.passport_serie.trim() || !s.passport_number || !s.category) {
    editModalError.value = "Barcha maydonlarni to'ldiring."
    return
  }

  if (phoneCleaned.length < 12) {
    editModalError.value = "Telefon raqami noto'g'ri kiritilgan."
    return
  }

  if (String(s.jshshr).length !== 14) {
    editModalError.value = "JSHSHR 14 ta raqam bo'lishi shart."
    return
  }

  const phone2Val = s.phone2 ? s.phone2.trim() : null

  editSaving.value = true
  editModalError.value = ''

  try {
    const payload = {
      full_name: s.full_name.trim(),
      phone: phoneCleaned,
      phone2: phone2Val,
      jshshr: parseInt(s.jshshr, 10),
      passport_serie: s.passport_serie.trim().toUpperCase(),
      passport_number: parseInt(s.passport_number, 10),
      birth_date: s.birth_date || null,
      category: parseInt(s.category, 10),
      status: s.status,
      instructor: s.instructor || '',
      coordinator: s.coordinator || '',
      agent: s.agent || '',
      notes: s.notes,
      learning_time: s.learning_time || '',
      learning_days: s.learning_days || [],
    }

    if (selectedEditStudentPhoto.value || selectedEditPassportPhoto.value) {
      const formData = new FormData()
      Object.keys(payload).forEach(key => {
        if (payload[key] === null || payload[key] === undefined) return
        if (Array.isArray(payload[key])) {
          payload[key].forEach(v => formData.append(key, v))
        } else {
          formData.append(key, payload[key])
        }
      })
      if (selectedEditStudentPhoto.value) formData.append('image', selectedEditStudentPhoto.value)
      if (selectedEditPassportPhoto.value) formData.append('pass_img', selectedEditPassportPhoto.value)
      await api.patch(`/students/${s.id}/`, formData)
    } else {
      await api.patch(`/students/${s.id}/`, payload)
    }

    closeEditModal()
    await fetchStudents()
  } catch (err) {
    console.error(err)
    if (err.response?.data) {
      const data = err.response.data
      if (typeof data === 'object') {
        const msgs = Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
        editModalError.value = msgs.join(' | ')
      } else {
        editModalError.value = String(data)
      }
    } else {
      editModalError.value = "Tahrirlashda xatolik yuz berdi."
    }
  } finally {
    editSaving.value = false
  }
}

// Watch phone for formatting: +998 90 900 90 90
watch(() => newStudent.value.phone, (newValue) => {
  if (!newValue) return
  let digits = newValue.replace(/\D/g, '')

  if (digits.length > 0 && !digits.startsWith('998')) {
    digits = '998' + digits
  }

  // Enforce max 12 digits (998 + 9 digits)
  digits = digits.substring(0, 12)

  let formatted = ''
  if (digits.length > 0) {
    formatted += '+' + digits.substring(0, 3)
  }
  if (digits.length > 3) {
    formatted += ' ' + digits.substring(3, 5)
  }
  if (digits.length > 5) {
    formatted += ' ' + digits.substring(5, 8)
  }
  if (digits.length > 8) {
    formatted += ' ' + digits.substring(8, 10)
  }
  if (digits.length > 10) {
    formatted += ' ' + digits.substring(10, 12)
  }

  if (newValue !== formatted) {
    newStudent.value.phone = formatted
  }
})

// phone2 is intentionally free-form (e.g. "+998 90 900 90 90 uncle") — no
// auto-reformatting here, unlike the primary `phone` field, since it also
// doubles as a relative/relation label field.

// Two-way formatting for min_payment
const formattedMinPayment = computed({
  get() {
    if (newStudent.value.min_payment === null || newStudent.value.min_payment === undefined || isNaN(newStudent.value.min_payment)) {
      return ''
    }
    return String(newStudent.value.min_payment).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  },
  set(value) {
    const digits = value.replace(/\D/g, '')
    if (digits === '') {
      newStudent.value.min_payment = null
    } else {
      newStudent.value.min_payment = parseInt(digits, 10)
    }
  }
})

// Two-way formatting for enrolled_amount
const formattedEnrolledAmount = computed({
  get() {
    if (newStudent.value.enrolled_amount === null || newStudent.value.enrolled_amount === undefined || isNaN(newStudent.value.enrolled_amount)) {
      return ''
    }
    return String(newStudent.value.enrolled_amount).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  },
  set(value) {
    const digits = value.replace(/\D/g, '')
    if (digits === '') {
      newStudent.value.enrolled_amount = null
    } else {
      newStudent.value.enrolled_amount = parseInt(digits, 10)
    }
  }
})

// ── Fetch data ───────────────────────────────────────────────
// Every filter, sort, and page below is now applied server-side
// (StudentViewSet.get_queryset) — `students` only ever holds the current
// page's rows, not a full tab-scoped copy of the table. This replaced a
// page_size=100000 fetch-everything-then-filter-client-side model: even
// after scoping to one category, StudentSerializer's 17 per-row computed
// fields took ~7.5s to serialize alone for a ~4k-row category, on top of
// the payload size — a cost that scaled with any category's row count,
// not just the unfiltered worst case.
const ORDERING_PARAM_MAP = {
  groupStart: 'group_started_at',
  groupEnd: 'group_ends_at',
  birth: 'birth_date',
  joined: 'date_joined',
}
const ordering = computed(() => {
  const refs = { groupStart: groupStartSort, groupEnd: groupEndSort, birth: birthDateSort, joined: joinedDateSort }
  for (const [key, sortRef] of Object.entries(refs)) {
    if (sortRef.value) return (sortRef.value === 'desc' ? '-' : '') + ORDERING_PARAM_MAP[key]
  }
  return ''
})

// Guards against an older, slower request (e.g. the initial load) resolving
// *after* a newer filtered one and clobbering it with stale results —
// debounce only limits how often a request starts, not the order replies
// come back in.
let fetchToken = 0
const fetchStudents = async () => {
  const token = ++fetchToken
  loading.value = true
  error.value = ''
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSizeOption.value === 'all' ? 100000 : Number(pageSizeOption.value),
    }
    if (filterStatus.value) params.status = filterStatus.value
    if (groupFilter.value) params.has_group = groupFilter.value
    if (filterCategory.value) params.category = filterCategory.value
    if (filterName.value.trim()) params.search = filterName.value.trim()
    if (filterPhone.value.trim()) params.phone = filterPhone.value.trim()
    if (filterJshshr.value.trim()) params.jshshr = filterJshshr.value.trim()
    if (filterGroupName.value.trim()) params.group_name = filterGroupName.value.trim()
    if (groupStartDateFrom.value) params.group_start_from = groupStartDateFrom.value
    if (groupStartDateTo.value) params.group_start_to = groupStartDateTo.value
    if (groupEndDateFrom.value) params.group_end_from = groupEndDateFrom.value
    if (groupEndDateTo.value) params.group_end_to = groupEndDateTo.value
    if (birthDateFrom.value) params.birth_date_from = birthDateFrom.value
    if (birthDateTo.value) params.birth_date_to = birthDateTo.value
    if (joinedDateFrom.value) params.joined_date_from = joinedDateFrom.value
    if (joinedDateTo.value) params.joined_date_to = joinedDateTo.value
    if (ordering.value) params.ordering = ordering.value
    if (branchStore.activeBranchId) params.branch = branchStore.activeBranchId

    const response = await api.get('/students/', { params })
    if (token !== fetchToken) return // a newer request has since been sent — discard this stale response
    const rawList = response.data.results ? response.data.results : (Array.isArray(response.data) ? response.data : [])
    students.value = rawList.map(mapStudent)
    totalCount.value = response.data.count ?? rawList.length
  } catch (err) {
    console.error(err)
    error.value = "O'quvchilarni yuklashda xatolik yuz berdi."
  } finally {
    if (token === fetchToken) { loading.value = false; initialLoading.value = false }
  }
}

// Every filter/sort below now triggers a backend refetch (see
// fetchStudents). Select/date/tab filters refetch immediately on change
// (discrete input, no per-keystroke risk); text filters are debounced so
// typing doesn't fire a request per keystroke — the input itself is never
// re-rendered/replaced by any of this (only the table rows below it are),
// so there's no risk of losing focus or cursor position mid-word.
watch(activeTab, () => {
  currentPage.value = 1
  fetchStudents()
})
watch(filterCategory, (val) => {
  if (val) {
    localStorage.setItem('students_filter_category', val)
  } else {
    localStorage.removeItem('students_filter_category')
  }
  currentPage.value = 1
  fetchStudents()
})
watch(pageSizeOption, () => {
  currentPage.value = 1
  fetchStudents()
})
watch([groupStartDateFrom, groupStartDateTo, groupEndDateFrom, groupEndDateTo, birthDateFrom, birthDateTo, joinedDateFrom, joinedDateTo], () => {
  currentPage.value = 1
  fetchStudents()
})
const debouncedRefetch = debounce(() => {
  currentPage.value = 1
  fetchStudents()
}, 400)
watch([filterName, filterPhone, filterJshshr, filterGroupName], debouncedRefetch)
watch(() => branchStore.activeBranchId, () => {
  currentPage.value = 1
  fetchStudents()
})

const fetchCategories = async () => {
  try {
    const response = await api.get('/categories/?page_size=100')
    categories.value = response.data.results ? response.data.results : (Array.isArray(response.data) ? response.data : [])
  } catch (err) {
    console.error('Error fetching categories:', err)
  }
}

const formatPrice = (price) => {
  if (price === null || price === undefined) return "0 so'm"
  return Number(price).toLocaleString('uz-UZ') + " so'm"
}

const formatDateDisplay = (dateVal) => {
  if (!dateVal) return '-'
  const d = new Date(dateVal)
  if (isNaN(d.getTime())) return dateVal
  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const year = d.getFullYear()
  return `${day}.${month}.${year}`
}

const mapStudent = (s) => {
  if (!s) return {}
  let statusText = 'Yangi'
  if (s.status === 'enrolled') statusText = 'Faol'
  else if (s.status === 'finished') statusText = 'Tugatgan'
  else if (s.status === 'canceled') statusText = 'Bekor qilingan'
  
  const dateStr = formatDateDisplay(s.date_joined || s.created_at)
  
  return {
    id: s.id,
    name: s.full_name || `${s.first_name || ''} ${s.last_name || ''}`.trim() || 'Noma\'lum',
    category: s.category || '-',
    categoryId: s.category_id,
    instructor: s.instructor || null,
    instructorName: s.instructor_name || '',
    coordinator: s.coordinator || null,
    coordinatorName: s.coordinator_name || '',
    agent: s.agent || null,
    agentName: s.agent_name || '',
    groupName: s.group_name || '',
    groupStartedAt: formatDateDisplay(s.group_started_at),
    groupEndsAt: formatDateDisplay(s.group_ends_at),
    groupStartedAtRaw: s.group_started_at || '',
    groupEndsAtRaw: s.group_ends_at || '',
    phone: formatPhoneDisplay(s.phone),
    phone2: s.phone2 ? formatPhoneDisplay(s.phone2) : '',
    jshshr: s.jshshr ? String(s.jshshr) : '-',
    passport: (s.passport_serie || s.passport_number) ? `${s.passport_serie || ''} ${s.passport_number || ''}`.trim() : '-',
    passportSerie: s.passport_serie || '',
    passportNumber: s.passport_number || '',
    birthDate: formatDateDisplay(s.birth_date),
    birthDateRaw: s.birth_date || '',
    date: dateStr,
    date_joined: dateStr,
    dateJoinedRaw: s.date_joined || s.created_at || '',
    status: statusText,
    rawStatus: s.status,
    enrolledFree: s.enrolled_free || false,
    paymentAmount: formatPrice(s.payment_amount),
    notes: s.notes || '',
    image: s.image || null,
    pass_img: s.pass_img || null,
    branch_name: s.branch_name || s.branch?.name || null,
    learning_time: s.learning_time || '',
    learning_days: s.learning_days || [],
  }
}

// Every header filter, sort, and page is applied server-side now (see
// fetchStudents/ordering above) — `students` already holds exactly the
// rows to display, in the right order, for the current page.
const displayTotalPages = computed(() => {
  if (pageSizeOption.value === 'all') return 1
  return Math.max(1, Math.ceil(totalCount.value / Number(pageSizeOption.value)))
})
function changePage(page) {
  if (page < 1 || page > displayTotalPages.value) return
  currentPage.value = page
  fetchStudents()
}

const formatPhoneDisplay = (p) => {
  if (!p) return ''
  if (p.includes(' ')) return p
  const digits = p.replace(/\D/g, '')
  if (digits.length === 12) {
    return `+${digits.substring(0, 3)} ${digits.substring(3, 5)} ${digits.substring(5, 8)} ${digits.substring(8, 10)} ${digits.substring(10, 12)}`
  }
  return p
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchCurrentUser()
  }
  await fetchCategories()
  // No persisted category yet (first-ever visit) — default to the first
  // one from the DB so the initial "faol" tab load is scoped server-side
  // from the start instead of pulling all ~6k rows unfiltered. Setting
  // this triggers the filterCategory watcher's own fetchStudents() call.
  if (!filterCategory.value && categories.value.length > 0) {
    filterCategory.value = categories.value[0].name
  } else {
    fetchStudents()
  }
  // Fetched here (not just when the "add student" modal opens) so the edit
  // modal's instructor/coordinator/agent selects always have options, even
  // if the user opens "edit" without ever opening "add" first.
  fetchStaff()
  fetchAgents()

  if (route.query.action === 'create') {
    openModal()
  }

  // Light dismiss fallback
  if (studentModal.value && !('closedBy' in HTMLDialogElement.prototype)) {
    studentModal.value.addEventListener('click', (event) => {
      if (event.target !== studentModal.value) return
      const rect = studentModal.value.getBoundingClientRect()
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

  document.addEventListener('click', handleSearchSelectOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleSearchSelectOutsideClick)
})

// Any click landing outside all instructor/coordinator/agent searchable
// selects (in either the add or edit student modal) closes whichever is open.
function handleSearchSelectOutsideClick(event) {
  if (event.target.closest('.search-select-container')) return
  isInstructorOpen.value = false
  isCoordinatorOpen.value = false
  isAgentOpen.value = false
  isEditInstructorOpen.value = false
  isEditCoordinatorOpen.value = false
  isEditAgentOpen.value = false
}



// ── Status badge class ───────────────────────────────────────
function statusClass(status) {
  if (status === 'Yangi') return 'badge-new'
  if (status === 'Faol' || status === "Qabul qilingan" || status === "Ro'yxatdan o'tgan") return 'badge-registered'
  if (status === 'Tugatgan' || status === 'Bekor qilingan') return 'badge-done'
  return ''
}

const staffInstructors = ref([])
const staffCoordinators = ref([])

// Searchable select state for Instructor & Coordinator
const isInstructorOpen = ref(false)
const instructorSearch = ref('')
const isCoordinatorOpen = ref(false)
const coordinatorSearch = ref('')

const selectedInstructor = computed(() => {
  if (!newStudent.value.instructor) return null
  return staffInstructors.value.find(u => u.id === newStudent.value.instructor) || null
})

const filteredInstructors = computed(() => {
  const q = instructorSearch.value.toLowerCase().trim()
  if (!q) return staffInstructors.value
  return staffInstructors.value.filter(u => {
    const name = getUserFullName(u).toLowerCase()
    return name.includes(q)
  })
})

const selectInstructor = (id) => {
  newStudent.value.instructor = id
  isInstructorOpen.value = false
  instructorSearch.value = ''
}
const instructorKb = useSearchSelectKeyboard()
const onInstructorKeydown = (e) => instructorKb.onKeydown(e, filteredInstructors.value, (inst) => selectInstructor(inst.id), () => { isInstructorOpen.value = false })

const selectedCoordinator = computed(() => {
  if (!newStudent.value.coordinator) return null
  return staffCoordinators.value.find(u => u.id === newStudent.value.coordinator) || null
})

const filteredCoordinators = computed(() => {
  const q = coordinatorSearch.value.toLowerCase().trim()
  if (!q) return staffCoordinators.value
  return staffCoordinators.value.filter(u => {
    const name = getUserFullName(u).toLowerCase()
    return name.includes(q)
  })
})

const selectCoordinator = (id) => {
  newStudent.value.coordinator = id
  isCoordinatorOpen.value = false
  coordinatorSearch.value = ''
}
const coordinatorKb = useSearchSelectKeyboard()
const onCoordinatorKeydown = (e) => coordinatorKb.onKeydown(e, filteredCoordinators.value, (c) => selectCoordinator(c.id), () => { isCoordinatorOpen.value = false })

const fetchStaff = async () => {
  try {
    const res = await api.get('/users/', { params: { page_size: 1000 } })
    const list = Array.isArray(res.data) ? res.data : (res.data.results || [])
    staffInstructors.value = list.filter(u => u.role === 'instructor' && u.is_active)
    staffCoordinators.value = list.filter(u => u.role === 'coordinator' && u.is_active)
  } catch (err) {
    console.error('Failed to fetch staff:', err)
  }
}

const learningPlaces = ref([])

const fetchLearningPlaces = async () => {
  try {
    const res = await api.get('/learning-places/', { params: { page_size: 1000 } })
    learningPlaces.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
  } catch (err) {
    console.error('Failed to fetch learning places:', err)
  }
}

const agents = ref([])
const isAgentOpen = ref(false)
const agentSearch = ref('')

const selectedAgent = computed(() => {
  if (!newStudent.value.agent) return null
  return agents.value.find(a => a.id === newStudent.value.agent) || null
})

const filteredAgents = computed(() => {
  const q = agentSearch.value.toLowerCase().trim()
  if (!q) return agents.value
  return agents.value.filter(a => {
    const name = (a.full_name || '').toLowerCase()
    return name.includes(q)
  })
})

const selectAgent = (id) => {
  newStudent.value.agent = id
  isAgentOpen.value = false
  agentSearch.value = ''
}
const agentKb = useSearchSelectKeyboard()
const onAgentKeydown = (e) => agentKb.onKeydown(e, filteredAgents.value, (a) => selectAgent(a.id), () => { isAgentOpen.value = false })

const fetchAgents = async () => {
  try {
    const res = await api.get('/agents/', { params: { page_size: 1000 } })
    agents.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
  } catch (err) {
    console.error('Failed to fetch agents:', err)
  }
}

// THE ROOT CAUSE of "instructor/coordinator select not opening": this helper
// was called throughout the file (filteredInstructors/filteredCoordinators,
// and the selected-instructor/coordinator display in both modals) but was
// never actually defined here, unlike CategoryDetailView. Agent never calls
// it (uses `.full_name` directly), which is why only Agent appeared to work
// — Instructor/Coordinator threw a ReferenceError during render as soon as
// the dropdown opened or a selected value needed to be displayed.
const getUserFullName = (u) => {
  if (!u) return '-'
  const full = u.full_name || `${u.first_name || ''} ${u.last_name || ''}`.trim()
  return full || u.phone || `Xodim #${u.id}`
}

// ── Searchable select state for the EDIT modal (separate from the create
// modal's state above so the two dialogs never fight over the same open/
// search flags) ──────────────────────────────────────────────
const isEditInstructorOpen = ref(false)
const editInstructorSearch = ref('')
const isEditCoordinatorOpen = ref(false)
const editCoordinatorSearch = ref('')
const isEditAgentOpen = ref(false)
const editAgentSearch = ref('')

const selectedEditInstructor = computed(() => {
  if (!editingStudent.value.instructor) return null
  return staffInstructors.value.find(u => u.id === editingStudent.value.instructor) || null
})

const filteredEditInstructors = computed(() => {
  const q = editInstructorSearch.value.toLowerCase().trim()
  if (!q) return staffInstructors.value
  return staffInstructors.value.filter(u => getUserFullName(u).toLowerCase().includes(q))
})

const selectEditInstructor = (id) => {
  editingStudent.value.instructor = id
  isEditInstructorOpen.value = false
  editInstructorSearch.value = ''
}
const editInstructorKb = useSearchSelectKeyboard()
const onEditInstructorKeydown = (e) => editInstructorKb.onKeydown(e, filteredEditInstructors.value, (inst) => selectEditInstructor(inst.id), () => { isEditInstructorOpen.value = false })

const selectedEditCoordinator = computed(() => {
  if (!editingStudent.value.coordinator) return null
  return staffCoordinators.value.find(u => u.id === editingStudent.value.coordinator) || null
})

const filteredEditCoordinators = computed(() => {
  const q = editCoordinatorSearch.value.toLowerCase().trim()
  if (!q) return staffCoordinators.value
  return staffCoordinators.value.filter(u => getUserFullName(u).toLowerCase().includes(q))
})

const selectEditCoordinator = (id) => {
  editingStudent.value.coordinator = id
  isEditCoordinatorOpen.value = false
  editCoordinatorSearch.value = ''
}
const editCoordinatorKb = useSearchSelectKeyboard()
const onEditCoordinatorKeydown = (e) => editCoordinatorKb.onKeydown(e, filteredEditCoordinators.value, (c) => selectEditCoordinator(c.id), () => { isEditCoordinatorOpen.value = false })

const selectedEditAgent = computed(() => {
  if (!editingStudent.value.agent) return null
  return agents.value.find(a => a.id === editingStudent.value.agent) || null
})

const filteredEditAgents = computed(() => {
  const q = editAgentSearch.value.toLowerCase().trim()
  if (!q) return agents.value
  return agents.value.filter(a => (a.full_name || '').toLowerCase().includes(q))
})

const selectEditAgent = (id) => {
  editingStudent.value.agent = id
  isEditAgentOpen.value = false
  editAgentSearch.value = ''
}
const editAgentKb = useSearchSelectKeyboard()
const onEditAgentKeydown = (e) => editAgentKb.onKeydown(e, filteredEditAgents.value, (a) => selectEditAgent(a.id), () => { isEditAgentOpen.value = false })

// ── Modal Actions ────────────────────────────────────────────
const openModal = async () => {
  if (!authStore.isAdminOrSuperuser) {
    alert("O'quvchini ro'yxatdan o'tkazish faqat admin va superuser uchun ruxsat etilgan.")
    return
  }
  await Promise.all([fetchStaff(), fetchLearningPlaces(), fetchAgents()])
  selectedStudentPhoto.value = null
  selectedPassportPhoto.value = null
  studentPhotoInputRef.value?.reset()
  passportPhotoInputRef.value?.reset()
  newStudent.value = {
    full_name: '',
    phone: '',
    phone2: '',
    jshshr: '',
    passport_serie: '',
    passport_number: '',
    category: '',
    instructor: null,
    coordinator: null,
    agent: null,
    learning_place: null,
    learning_time: '',
    learning_days: [],
    min_payment: null,
    payment_method: 'cash',
    enrolled_free: false,
    has_custom_price: false,
    enrolled_amount: null,
    can_view_payments: true,
    notes: '',
  }
  modalError.value = ''
  if (studentModal.value) {
    studentModal.value.showModal()
  }
}

const closeModal = () => {
  if (studentModal.value) {
    studentModal.value.close()
  }
}

const saveStudent = async () => {
  if (!authStore.isAdminOrSuperuser) {
    modalError.value = "O'quvchini ro'yxatdan o'tkazish faqat admin va superuser uchun ruxsat etilgan."
    return
  }
  const s = newStudent.value
  const phoneCleaned = s.phone.replace(/\D/g, '')
  
  if (s.enrolled_free) {
    s.min_payment = 0
  }
  
  if (!s.full_name.trim() || !phoneCleaned || !s.jshshr || !s.passport_serie.trim() || !s.passport_number || !s.category || s.min_payment === null) {
    modalError.value = "Barcha maydonlarni to'ldiring."
    return
  }
  
  if (s.has_custom_price && !s.enrolled_free && s.enrolled_amount === null) {
    modalError.value = "Shartnoma summasini kiriting."
    return
  }
  
  if (phoneCleaned.length < 12) {
    modalError.value = "Telefon raqami noto'g'ri kiritilgan."
    return
  }
  
  if (String(s.jshshr).length !== 14) {
    modalError.value = "JSHSHR 14 ta raqam bo'lishi shart."
    return
  }
  
  const phone2Val = s.phone2 ? s.phone2.trim() : null

  saving.value = true
  modalError.value = ''

  try {
    const payload = {
      full_name: s.full_name.trim(),
      phone: phoneCleaned,
      phone2: phone2Val,
      jshshr: parseInt(s.jshshr, 10),
      passport_serie: s.passport_serie.trim().toUpperCase(),
      passport_number: parseInt(s.passport_number, 10),
      birth_date: s.birth_date || null,
      category: parseInt(s.category, 10),
      instructor: s.instructor || null,
      coordinator: s.coordinator || null,
      agent: s.agent || null,
      learning_place: s.learning_place || null,
      learning_time: s.learning_time ? s.learning_time.trim() : null,
      learning_days: s.learning_days || [],
      min_payment: parseInt(s.min_payment, 10),
      payment_method: s.payment_method || 'cash',
      enrolled_free: s.enrolled_free || false,
      enrolled_amount: (s.has_custom_price && !s.enrolled_free) ? parseInt(s.enrolled_amount, 10) : null,
      can_view_payments: s.can_view_payments !== false,
      notes: s.notes,
      status: 'new', // Register new student in new status
      branch: branchStore.activeBranchId ?? null,
    }
    
    if (selectedStudentPhoto.value || selectedPassportPhoto.value) {
      const formData = new FormData()
      Object.keys(payload).forEach(key => {
        if (payload[key] === null || payload[key] === undefined) return
        if (Array.isArray(payload[key])) {
          payload[key].forEach(v => formData.append(key, v))
        } else {
          formData.append(key, payload[key])
        }
      })
      if (selectedStudentPhoto.value) formData.append('image', selectedStudentPhoto.value)
      if (selectedPassportPhoto.value) formData.append('pass_img', selectedPassportPhoto.value)
      await api.post('/students/', formData)
    } else {
      await api.post('/students/', payload)
    }

    closeModal()
    await fetchStudents()
  } catch (err) {
    console.error(err)
    if (err.response?.data) {
      const data = err.response.data
      if (typeof data === 'object') {
        const msgs = Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
        modalError.value = msgs.join(' | ')
      } else {
        modalError.value = String(data)
      }
    } else {
      modalError.value = "Saqlashda xatolik yuz berdi."
    }
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
/* Height is set at runtime by useFillViewportHeight (measured via
   getBoundingClientRect, not assumed from hardcoded topbar/padding
   constants — those drifted out of sync with the real rendered chrome).
   That makes the table body the only thing that scrolls: the header
   stays sticky within it, and the pagination bar (a fixed-size flex item
   below it) never has to be reached by scrolling the outer page. */
.page-flex-col {
  display: flex;
  flex-direction: column;
}

/* ── Top action ─────────────────────────────────────────── */
.page-top {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
  flex-shrink: 0;
}

.btn-add {
  padding: 10px 20px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: background 0.15s, transform 0.1s;
}
.btn-add:hover { background: #245C43; transform: translateY(-1px); }

/* ── Enrollment status tabs ─────────────────────────────────── */
.status-tabs-bar {
  display: flex;
  align-items: center;
  gap: 4px;
  border-bottom: 2px solid #E5E7EB;
  margin-bottom: 20px;
  overflow-x: auto;
  flex-shrink: 0;
}

.status-tab-btn {
  padding: 11px 16px;
  border: none;
  background: transparent;
  border-bottom: 3px solid transparent;
  font-size: 13.5px;
  font-weight: 600;
  color: #6B7280;
  cursor: pointer;
  white-space: nowrap;
  font-family: 'Inter', sans-serif;
  transition: color 0.15s, border-color 0.15s;
}
.status-tab-btn:hover { color: #111827; }
.status-tab-btn.active { color: #2D6A4F; border-bottom-color: #2D6A4F; }

/* ── Column-head filters ─────────────────────────────────────── */
.col-filter-input,
.col-filter-select {
  width: 100%;
  box-sizing: border-box;
  padding: 6px 8px;
  border: 1px solid #D1D5DB;
  border-radius: 6px;
  font-size: 12.5px;
  font-weight: 400;
  color: #374151;
  outline: none;
  background: white;
  font-family: 'Inter', sans-serif;
  transition: border-color 0.15s;
}
.col-filter-input:focus,
.col-filter-select:focus { border-color: #2D6A4F; }
.col-filter-input::placeholder { color: #9CA3AF; }

.col-sort-group {
  display: flex;
  gap: 4px;
}
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
.col-date-input:focus { border-color: #2D6A4F; outline: none; }

/* Select wrapper */
.select-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.filter-select {
  width: 100%;
  appearance: none;
  -webkit-appearance: none;
  padding: 9px 34px 9px 12px;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  font-size: 13px;
  color: #374151;
  background: white;
  outline: none;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  transition: border-color 0.15s;
}
.filter-select:focus { border-color: #2D6A4F; }

.select-arrow {
  position: absolute;
  right: 10px;
  color: #9CA3AF;
  pointer-events: none;
  flex-shrink: 0;
}

.btn-edit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: white;
  border: 1px solid #D1D5DB;
  border-radius: 6px;
  color: #374151;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
  padding: 0;
}
.btn-edit:hover {
  background: #F9FAFB;
  border-color: #9CA3AF;
}

/* ── States ─────────────────────────────────────────── */
.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-height: 0;
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

/* ── Table ─────────────────────────────────────────────────── */
/* flex column + flex:1 (rather than a guessed max-height) so this card
   fills exactly whatever vertical space is left below the tabs/filters —
   auto-sized to the screen, not a fixed pixel value. The pagination bar
   below the scroll area is a fixed-size flex item, so it never has to be
   reached by scrolling — it's always visible right under the table. */
.table-wrap {
  background: white;
  border-radius: 12px;
  border: 1px solid #E5E7EB;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

/* Independently-scrolling table body so the header (and the column-filter
   row beneath it) can stick to the top of this container as rows scroll
   underneath, instead of scrolling away with the page. */
.table-scroll-area {
  overflow: auto;
  flex: 1;
  min-height: 240px;
}

/* ── Pagination / row-fetch-count bar ────────────────────────── */
.pagination-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #F9FAFB;
  border-top: 1px solid #E5E7EB;
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 12px;
  flex-shrink: 0;
}
.pagination-info {
  font-size: 13.5px;
  color: #6B7280;
  font-weight: 500;
}
.pagination-note {
  margin-left: 8px;
  font-size: 12px;
  color: #9CA3AF;
  font-weight: 400;
}
.pagination-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.page-size-label {
  font-size: 13px;
  font-weight: 600;
  color: #4B5563;
}
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

.stbl {
  width: 100%;
  border-collapse: collapse;
  font-size: 13.5px;
}

/* Sticky is applied to <thead> itself, not to individual <th> cells with
   per-row top offsets — that approach requires guessing each row's pixel
   height and breaks the moment row heights change (label row vs. the
   shorter filter-input row), which is why only one row was sticking.
   Modern browsers support making a <thead> itself the sticky element, so
   both header rows move as a single unit with no offset math needed. */
.stbl thead {
  position: sticky;
  top: 0;
  z-index: 3;
}

.stbl thead th {
  padding: 13px 16px;
  text-align: left;
  font-size: 13px;
  font-weight: 700;
  color: #111827;
  border-bottom: 2px solid #F3F4F6;
  white-space: nowrap;
  background: white;
}

.stbl thead tr.col-filter-row th {
  padding: 8px 10px;
  background: #FAFAFB;
  border-bottom: 2px solid #F3F4F6;
}

.stbl tbody .stbl-row td {
  padding: 13px 16px;
  border-bottom: 1px solid #F9FAFB;
  vertical-align: middle;
}

.stbl tbody .stbl-row { cursor: pointer; }
.stbl tbody .stbl-row:last-child td { border-bottom: none; }
.stbl tbody .stbl-row:hover td { background: #FAFAFA; }

.td-notes {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #6B7280;
  font-size: 13px;
}

.td-name {
  font-weight: 600;
  color: #111827;
  white-space: nowrap;
}

.td-cat {
  font-size: 20px;
  font-weight: 900;
  color: #2D6A4F;
  letter-spacing: -0.01em;
}

.td-muted { color: #6B7280; }

/* No data row */
.no-data {
  text-align: center;
  padding: 40px;
  color: #9CA3AF;
  font-size: 14px;
}

/* ── Status badges ──────────────────────────────────────────── */
.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.badge-new {
  background: white;
  color: #374151;
  border: 1.5px solid #D1D5DB;
}

.badge-registered {
  background: #2D6A4F;
  color: white;
}

.badge-done {
  background: #DC2626;
  color: white;
}

.badge-free {
  background: #E8F5E9;
  color: #2E7D32;
  border: 1.5px solid #A5D6A7;
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

/* Searchable Select Styles */
.search-select-container {
  position: relative;
  width: 100%;
}

.search-select-trigger {
  min-height: 44px;
  padding: 6px 12px;
  border: 1.5px solid #D1D5DB;
  border-radius: 10px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.search-select-trigger:hover {
  border-color: #9CA3AF;
  background: #F9FAFB;
}

.search-select-trigger.is-open {
  border-color: #2D6A4F;
  box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.12);
}

.search-select-trigger.has-selected {
  padding: 4px 8px;
  border-color: #A7F3D0;
  background: #F0FDF4;
}

.trigger-placeholder, .select-placeholder {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13.5px;
  color: #6B7280;
}

.select-arrow-icon {
  color: #6B7280;
  transition: transform 0.2s ease;
}

.select-arrow-icon.rotate {
  transform: rotate(180deg);
}

.selected-user-card {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.user-avatar-badge {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 12px;
  flex-shrink: 0;
}

.avatar-inst {
  background: #FEF3C7;
  color: #92400E;
  border: 1px solid #FDE68A;
}

.avatar-coord {
  background: #E0E7FF;
  color: #3730A3;
  border: 1px solid #C7D2FE;
}

.avatar-agent {
  background: #F3E8FF;
  color: #6B21A8;
  border: 1px solid #E9D5FF;
}

.selected-user-details {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
  text-align: left;
}

.selected-user-name {
  font-size: 13px;
  font-weight: 600;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.selected-user-phone {
  font-size: 11px;
  color: #6B7280;
}

.btn-remove-selection {
  background: none;
  border: none;
  color: #9CA3AF;
  font-size: 14px;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 6px;
  transition: all 0.15s;
}

.btn-remove-selection:hover {
  background: #F3F4F6;
  color: #EF4444;
}

/* Dropdown menu */
.search-select-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  z-index: 100;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  animation: dropIn 0.15s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes dropIn {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}

.dropdown-search-wrap {
  padding: 2px;
}

.dropdown-search-field {
  width: 100%;
  padding: 8px 12px;
  font-size: 13px;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.15s;
  box-sizing: border-box;
}

.dropdown-search-field:focus {
  border-color: #2D6A4F;
}

.dropdown-options-container {
  max-height: 180px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dropdown-option-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
  text-align: left;
}

.dropdown-option-row:hover {
  background: #F3F4F6;
}

.dropdown-option-row.is-active {
  background: #ECFDF5;
}

.dropdown-option-row.is-highlighted {
  background: #F3F4F6;
}

.option-clear {
  color: #6B7280;
  font-weight: 500;
  font-size: 12.5px;
  justify-content: center;
}

.opt-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 11px;
  flex-shrink: 0;
}

.opt-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.opt-name {
  font-size: 13px;
  font-weight: 600;
  color: #111827;
}

.opt-phone {
  font-size: 11px;
  color: #6B7280;
}

.opt-check {
  color: #059669;
  font-weight: 700;
  font-size: 14px;
}

.dropdown-empty {
  padding: 12px;
  text-align: center;
  font-size: 12.5px;
  color: #9CA3AF;
}

/* ── Modal Dialog ───────────────────────────────────── */
.modal-dialog {
  border: none;
  border-radius: 16px;
  padding: 0;
  max-width: 900px;
  width: 92%;
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

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}

.form-row-group {
  display: flex;
  gap: 16px;
}

.half-width {
  flex: 1;
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
  padding: 10px 14px;
  border: 1.5px solid #D1D5DB;
  border-radius: 10px;
  font-size: 13.5px;
  color: #111827;
  font-weight: 500;
  outline: none;
  transition: all 0.15s ease;
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  background-color: white;
}
.form-input:hover {
  border-color: #9CA3AF;
}
.form-input:focus {
  border-color: #2D6A4F;
  box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.14);
}

.text-uppercase {
  text-transform: uppercase;
}

.select-wrap {
  position: relative;
  width: 100%;
}

.select-input {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-color: white;
  padding: 10px 36px 10px 14px;
  border: 1.5px solid #D1D5DB;
  border-radius: 10px;
  font-size: 13.5px;
  color: #111827;
  font-family: inherit;
  font-weight: 500;
  width: 100%;
  box-sizing: border-box;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  transition: all 0.15s ease;
}

.select-input:hover {
  border-color: #9CA3AF;
  background-color: #FAFAFA;
}

.select-input:focus {
  border-color: #2D6A4F;
  box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.14);
  background-color: white;
  outline: none;
}

.select-arrow-modal {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: #6B7280;
  transition: color 0.15s ease;
}

.select-wrap:hover .select-arrow-modal {
  color: #2D6A4F;
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
.btn-save:hover:not(:disabled) {
  background: #245C43;
}
.btn-save:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Strict phone column width */
.th-phone, .td-phone {
  width: 175px !important;
  min-width: 175px !important;
  max-width: 175px !important;
  white-space: normal !important;
}

.td-phone-main {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.td-phone-sub {
  font-size: 11.5px;
  color: #6B7280;
  margin-top: 2px;
  white-space: normal;
  overflow-wrap: break-word;
  word-break: break-word;
}

</style>
