<template>
  <AppLayout>

    <!-- Top action / back bar -->
    <div class="page-top">
      <button class="btn-back" @click="router.push({ name: 'categories' })">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        Kategoriyalarga qaytish
      </button>
      <div class="top-actions-right">
        <button
          v-if="authStore.isAdminOrSuperuser && (selectedStudentIds.length === 23 || selectedStudentIds.length === 24)"
          class="btn-start-group"
          @click="openGroupConfirmModal"
        >
          Guruhni boshlash
        </button>
        <button v-if="authStore.isAdminOrSuperuser" class="btn-add" @click="openModal">Yangi O'quvchi Qo'shish</button>
      </div>
    </div>

    <!-- Category Header Card -->
    <div v-if="category" class="category-header-card">
      <div class="cat-details">
        <div class="cat-icon-wrap" v-html="categoryIcon"></div>
        <div class="cat-info-block">
          <h2 class="cat-name">{{ category.name }}</h2>
          <p class="cat-price">Narxi: <span class="price-val">{{ formattedPrice }}</span></p>
        </div>
      </div>
      <div class="cat-stat-badge">
        <span class="stat-count">{{ totalCount }}</span>
        <span class="stat-label">Yangi O'quvchi</span>
      </div>
    </div>

    <!-- Loading, error, or empty states -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">Ma'lumotlar yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchData">Qayta urinish</button>
    </div>

    <!-- Table of registered students with status new -->
    <div v-else class="table-wrap">
      <div class="table-header">
        <h3>Navbatdagi / Yangi O'quvchilar Ro'yxati</h3>
        <span class="selected-count" v-if="selectedStudentIds.length > 0">Tanlangan: {{ selectedStudentIds.length }} ta</span>
      </div>
      <div class="table-scroll-area">
      <table class="stbl">
        <thead>
          <tr>
            <th>To'liq Ismi</th>
            <th>
              <input type="checkbox" @change="toggleSelectAll" :checked="isAllSelected" class="th-chk" />
            </th>
            <th class="th-phone">Telefon Raqami</th>
            <th>JSHSHR</th>
            <th>Passport Ma'lumotlari</th>
            <th>Ro'yxatdan o'tgan sana</th>
            <th>To'langan</th>
            <th>Holat</th>
            <th>Eslatma</th>
            <th>Amallar</th>
          </tr>
          <tr class="col-filter-row">
            <th>
              <input v-model="filterName" class="col-filter-input" type="text" placeholder="Ism bo'yicha qidirish..." />
            </th>
            <th></th>
            <th>
              <input v-model="filterPhone" class="col-filter-input" type="text" placeholder="Telefon bo'yicha qidirish..." />
            </th>
            <th>
              <input v-model="filterJshshr" class="col-filter-input" type="text" placeholder="JSHSHR" />
            </th>
            <th></th>
            <th>
              <div class="col-sort-group">
                <button type="button" class="col-sort-icon-btn" :class="{ active: enrolledDateSort === 'asc' }" title="O'sish tartibida (eskidan yangiga)" @click="setSort('enrolledDate', 'asc')">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 20V4"></path><path d="M3 8l3-4 3 4"></path></svg>
                </button>
                <button type="button" class="col-sort-icon-btn" :class="{ active: enrolledDateSort === 'desc' }" title="Kamayish tartibida (yangidan eskiga)" @click="setSort('enrolledDate', 'desc')">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4v16"></path><path d="M3 16l3 4 3-4"></path></svg>
                </button>
                <button v-if="enrolledDateFrom || enrolledDateTo" type="button" class="btn-clear-date" @click="enrolledDateFrom = ''; enrolledDateTo = ''" title="Tozalash">✕</button>
              </div>
              <div class="col-date-range">
                <input v-model="enrolledDateFrom" type="date" class="col-date-input" title="Ro'yxatdan o'tgan sana (dan)" />
                <input v-model="enrolledDateTo" type="date" class="col-date-input" title="Ro'yxatdan o'tgan sana (gacha)" />
              </div>
            </th>
            <th>
              <div class="col-sort-group">
                <button type="button" class="col-sort-icon-btn" :class="{ active: paidAmountSort === 'asc' }" title="O'sish tartibida" @click="setSort('paidAmount', 'asc')">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 20V4"></path><path d="M3 8l3-4 3 4"></path></svg>
                </button>
                <button type="button" class="col-sort-icon-btn" :class="{ active: paidAmountSort === 'desc' }" title="Kamayish tartibida" @click="setSort('paidAmount', 'desc')">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4v16"></path><path d="M3 16l3 4 3-4"></path></svg>
                </button>
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
          </tr>
        </thead>
        <tbody>
          <tr v-if="displayedStudents.length === 0">
            <td colspan="10" class="no-data">Hozircha ushbu kategoriyada yangi o'quvchilar mavjud emas</td>
          </tr>
          <tr v-for="s in displayedStudents" :key="s.id" class="stbl-row clickable-row" @click="goToStudentDetail(s.id)">
            <td class="td-name">{{ s.name }}</td>
            <td @click.stop>
              <input type="checkbox" :value="s.id" v-model="selectedStudentIds" class="td-chk" />
            </td>
            <td class="td-muted td-phone">
              <div>{{ s.phone }}</div>
              <div v-if="s.phone2" style="font-size: 11.5px; color: #6B7280; margin-top: 2px;">
                Qo'shimcha: {{ s.phone2 }}
              </div>
            </td>
            <td class="td-muted">{{ s.jshshr }}</td>
            <td class="td-muted">{{ s.passport }}</td>
            <td class="td-muted">{{ s.date }}</td>
            <td class="td-bold">
              <span v-if="s.enrolledFree" class="status-badge badge-free">Tekin</span>
              <span v-else>{{ s.paymentAmount }}</span>
            </td>
            <td>
              <span class="status-badge" :class="statusClass(s.rawStatus)">{{ s.status }}</span>
            </td>
            <td>
              <div class="td-notes" :title="s.notes">{{ s.notes || '-' }}</div>
            </td>
            <td>
              <button class="btn-edit" @click.stop="openEditModal(s)" title="Tahrirlash">
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
      <div class="pagination-bar">
        <span class="pagination-info">
          Jami: <strong>{{ filteredStudents.length }}</strong> tadan <strong>{{ displayedStudents.length }}</strong> ko'rsatilmoqda
        </span>
        <div class="pagination-actions">
          <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">Oldingi</button>
          <span v-if="pageSizeOption !== 'all'" class="page-num">Sahifa {{ Math.min(currentPage, displayTotalPages) }} / {{ displayTotalPages }}</span>
          <button v-if="pageSizeOption !== 'all'" class="btn-page" :disabled="currentPage === displayTotalPages" @click="changePage(currentPage + 1)">Keyingi</button>
          <label class="page-size-label" for="cat-students-page-size">Ko'rsatish:</label>
          <div class="select-wrap-relative">
            <select id="cat-students-page-size" v-model="pageSizeOption" class="page-size-select">
              <option value="50">50</option>
              <option value="100">100</option>
              <option value="200">200</option>
              <option value="all">Barchasi</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- New Student Modal Dialog -->
    <dialog ref="studentModal" class="modal-dialog" closedby="any" aria-labelledby="modal-title">
      <form class="modal-form" @submit.prevent="saveStudent">
        <h3 id="modal-title" class="modal-title">Yangi o'quvchi qo'shish (Yangi holatda)</h3>

        <div v-if="modalError" class="modal-error">
          {{ modalError }}
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label for="std-name" class="form-label">F.I.SH. (To'liq ism)</label>
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
            <label for="std-phone" class="form-label">Telefon raqami</label>
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
            <label for="std-phone2" class="form-label">Qo'shimcha telefon raqami</label>
            <input
              id="std-phone2"
              v-model="newStudent.phone2"
              type="text"
              placeholder="+998 90 123 45 67 ayasi / dadasi (ixtiyoriy)"
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
            <label class="form-label">Tanlangan Kategoriya</label>
            <input
              v-if="category"
              type="text"
              :value="category.name"
              disabled
              class="form-input disabled-input"
            />
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
            <label for="edit-std-phone2" class="form-label">Qo'shimcha telefon raqami</label>
            <input
              id="edit-std-phone2"
              v-model="editingStudent.phone2"
              type="text"
              placeholder="+998 90 123 45 67 ayasi / dadasi (ixtiyoriy)"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="edit-std-jshshr" class="form-label">JSHSHR (14 xonali raqam)</label>
            <input
              id="edit-std-jshshr"
              v-model="editingStudent.jshshr"
              type="number"
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

    <!-- Start Group Confirmation Modal Dialog -->
    <dialog ref="groupConfirmModal" class="modal-dialog" closedby="any" aria-labelledby="group-modal-title">
      <form class="modal-form" @submit.prevent="startGroup">
        <h3 id="group-modal-title" class="modal-title">Guruhni boshlash</h3>

        <div class="modal-confirm-body" style="display: flex; flex-direction: column; gap: 16px;">
          <p style="margin: 0; font-size: 14px; color: #4B5563;">
            Tanlangan <strong>{{ selectedStudentIds.length }}</strong> ta o'quvchi bilan yangi guruh boshlamoqchimisiz?
          </p>

          <div class="form-group">
            <label for="group-name-input" class="form-label">Guruh nomi</label>
            <input
              id="group-name-input"
              v-model="groupForm.name"
              type="text"
              required
              class="form-input"
              placeholder="Masalan: B-Guruh 1"
            />
          </div>

          <div class="form-group">
            <label for="group-start-input" class="form-label">Boshlanish sanasi</label>
            <input
              id="group-start-input"
              v-model="groupForm.started_at"
              type="date"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label class="form-label">Dars kunlari (Dushanba - Shanba)</label>
            <div class="weekday-picker">
              <label v-for="d in weekdayOptions" :key="d.value" class="weekday-chip" :class="{ active: groupForm.selected_weekdays.includes(d.value) }">
                <input type="checkbox" :value="d.value" v-model="groupForm.selected_weekdays" style="display: none;" />
                {{ d.label }}
              </label>
            </div>
          </div>

          <div class="form-group">
            <label for="group-working-days-input" class="form-label">Ish kunlari soni</label>
            <input
              id="group-working-days-input"
              v-model="groupForm.working_days"
              type="number"
              class="form-input"
              placeholder="68"
            />
            <p style="margin: 6px 0 0; font-size: 12px; color: #9CA3AF;">
              Tugash sanasi tanlangan dars kunlari, bayramlar va ish kunlari soniga qarab avtomatik hisoblanadi.
            </p>
          </div>
        </div>

        <div class="modal-actions" style="margin-top: 16px;">
          <button type="button" class="btn-cancel" @click="closeGroupConfirmModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="groupSaving">
            <span v-if="groupSaving" class="btn-spinner"></span>
            {{ groupSaving ? 'Boshlanmoqda...' : 'Tasdiqlash' }}
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

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const branchStore = useBranchStore()
const categoryId = route.params.id

const goToStudentDetail = (id) => {
  router.push(`/students/${id}`)
}

// ── Filter State ─────────────────────────────────────
const filterName = ref('')
const filterPhone = ref('')
const filterJshshr = ref('')
const filterStatus = ref('')
const enrolledDateSort = ref('')
const enrolledDateFrom = ref('')
const enrolledDateTo = ref('')
const paidAmountSort = ref('')

const sortRefs = { enrolledDate: enrolledDateSort, paidAmount: paidAmountSort }
function setSort(field, dir) {
  const target = sortRefs[field]
  Object.values(sortRefs).forEach(r => { if (r !== target) r.value = '' })
  target.value = target.value === dir ? '' : dir
}

// ── Row-fetch-count selector ──────────────────────────────────
// Replaces classic next/prev pagination: pick how many rows to pull from
// the backend in one shot, then filter/sort them instantly on the client
// (see displayedStudents below) instead of round-tripping per filter
// change. Filtering has to see every row — not just whatever page happened
// to be fetched — so the fetch itself always pulls everything;
// pageSizeOption instead controls how many of the *filtered* results are
// shown per page (see displayedStudents/changePage below).
const pageSizeOption = ref('50')
const totalCount = ref(0)
const currentPage = ref(1)

// ── State ───────────────────────────────────────────
const category = ref(null)
const students = ref([])
const categories = ref([])
const loading = ref(false)
const error = ref('')

// ── Selection State ──────────────────────────────────
const selectedStudentIds = ref([])
const groupConfirmModal = ref(null)
const groupSaving = ref(false)

const groupForm = ref({
  name: '',
  started_at: '',
  working_days: 68,
  selected_weekdays: [0, 2, 4], // Mon, Wed, Fri by default
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

const isAllSelected = computed(() => {
  return filteredStudents.value.length > 0 && selectedStudentIds.value.length === filteredStudents.value.length
})

const toggleSelectAll = (e) => {
  if (e.target.checked) {
    selectedStudentIds.value = filteredStudents.value.map(s => s.id)
  } else {
    selectedStudentIds.value = []
  }
}

const openGroupConfirmModal = () => {
  if (!authStore.isAdminOrSuperuser) {
    alert("Guruh yaratish faqat admin va superuser uchun ruxsat etilgan.")
    return
  }
  groupForm.value = {
    name: category.value ? `${category.value.name} guruhi` : '',
    started_at: new Date().toISOString().substring(0, 10),
    working_days: category.value && category.value.duration ? category.value.duration : 68,
    selected_weekdays: [0, 2, 4],
  }
  if (groupConfirmModal.value) {
    groupConfirmModal.value.showModal()
  }
}

const closeGroupConfirmModal = () => {
  if (groupConfirmModal.value) {
    groupConfirmModal.value.close()
  }
}

const startGroup = async () => {
  if (!authStore.isAdminOrSuperuser) {
    alert("Guruh yaratish faqat admin va superuser uchun ruxsat etilgan.")
    return
  }

  if (!groupForm.value.name.trim() || !groupForm.value.started_at || !groupForm.value.working_days) {
    alert("Barcha maydonlarni to'ldiring.")
    return
  }

  groupSaving.value = true
  try {
    const payload = {
      name: groupForm.value.name.trim(),
      started_at: groupForm.value.started_at,
      working_days: Number(groupForm.value.working_days) || 68,
      selected_weekdays: groupForm.value.selected_weekdays,
      category: parseInt(categoryId, 10),
      status: 'started',
      student_ids: selectedStudentIds.value,
      branch: branchStore.activeBranchId ?? null,
    }
    await api.post('/groups/', payload)

    selectedStudentIds.value = []
    closeGroupConfirmModal()
    await fetchData()
  } catch (err) {
    console.error(err)
    alert("Guruhni boshlashda xatolik yuz berdi.")
  } finally {
    groupSaving.value = false
  }
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
  notes: '',
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

const openEditModal = (student) => {
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
    notes: student.notes || '',
  }
  editModalError.value = ''
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

  editSaving.value = true
  editModalError.value = ''

  try {
    const payload = {
      full_name: s.full_name.trim(),
      phone: phoneCleaned,
      phone2: s.phone2 ? s.phone2.trim() : null,
      jshshr: parseInt(s.jshshr, 10),
      passport_serie: s.passport_serie.trim().toUpperCase(),
      passport_number: parseInt(s.passport_number, 10),
      birth_date: s.birth_date || null,
      category: parseInt(s.category, 10),
      status: s.status,
      notes: s.notes,
    }

    await api.patch(`/students/${s.id}/`, payload)
    closeEditModal()
    await fetchData()
  } catch (err) {
    console.error(err)
    if (err.response?.data?.phone) {
      editModalError.value = "Ushbu telefon raqamli o'quvchi allaqachon mavjud."
    } else if (err.response?.data?.jshshr) {
      editModalError.value = "Ushbu JSHSHR egasi bo'lgan o'quvchi allaqachon mavjud."
    } else if (err.response?.data?.passport_number) {
      editModalError.value = "Ushbu passport raqamli o'quvchi allaqachon mavjud."
    } else {
      editModalError.value = "Tahrirlashda xatolik yuz berdi. Ma'lumotlarni tekshirib qayta urinib ko'ring."
    }
  } finally {
    editSaving.value = false
  }
}

const filteredStudents = computed(() => {
  const nameQ = filterName.value.toLowerCase().trim()
  const phoneQ = filterPhone.value.replace(/\D/g, '')
  let list = students.value.filter(s => {
    if (nameQ && !s.name.toLowerCase().includes(nameQ)) return false
    if (phoneQ && !s.phone.replace(/\D/g, '').includes(phoneQ)) return false
    if (filterJshshr.value && !s.jshshr.includes(filterJshshr.value)) return false
    if (filterStatus.value && s.rawStatus !== filterStatus.value) return false
    if (enrolledDateFrom.value && !(s.dateRaw && s.dateRaw.slice(0, 10) >= enrolledDateFrom.value)) return false
    if (enrolledDateTo.value && !(s.dateRaw && s.dateRaw.slice(0, 10) <= enrolledDateTo.value)) return false
    return true
  })

  if (enrolledDateSort.value) {
    const dir = enrolledDateSort.value === 'asc' ? 1 : -1
    list = list.slice().sort((a, b) => {
      const ta = a.dateRaw ? new Date(a.dateRaw).getTime() : null
      const tb = b.dateRaw ? new Date(b.dateRaw).getTime() : null
      if (ta === null && tb === null) return 0
      if (ta === null) return 1
      if (tb === null) return -1
      return (ta - tb) * dir
    })
  } else if (paidAmountSort.value) {
    const dir = paidAmountSort.value === 'asc' ? 1 : -1
    list = list.slice().sort((a, b) => (a.paymentAmountRaw - b.paymentAmountRaw) * dir)
  }

  return list
})

// pageSizeOption now purely controls how many of the *filtered* rows show
// per page — currentPage is clamped here so it self-corrects the moment a
// filter shrinks the result set out from under it.
const displayPageSize = computed(() => pageSizeOption.value === 'all' ? Infinity : Number(pageSizeOption.value))
const displayTotalPages = computed(() => {
  if (pageSizeOption.value === 'all') return 1
  return Math.max(1, Math.ceil(filteredStudents.value.length / displayPageSize.value))
})
const displayedStudents = computed(() => {
  if (pageSizeOption.value === 'all') return filteredStudents.value
  const page = Math.min(currentPage.value, displayTotalPages.value)
  const start = (page - 1) * displayPageSize.value
  return filteredStudents.value.slice(start, start + displayPageSize.value)
})
function changePage(page) {
  if (page < 1 || page > displayTotalPages.value) return
  currentPage.value = page
}

// ── Modal State ──────────────────────────────────────
const studentModal = ref(null)
const newStudent = ref({
  full_name: '',
  phone: '',
  phone2: '',
  jshshr: '',
  passport_serie: '',
  passport_number: '',
  birth_date: '',
  category: categoryId,
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
const studentPhotoInputRef = ref(null)
const passportPhotoInputRef = ref(null)

function onStudentPhotoChange(e) {
  selectedStudentPhoto.value = e.target.files?.[0] || null
}
function onPassportPhotoChange(e) {
  selectedPassportPhoto.value = e.target.files?.[0] || null
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

// ── Icons & pricing helpers ──────────────────────────
const categoryIcon = computed(() => {
  if (!category.value) return ''
  const norm = category.value.name.toUpperCase()
  if (norm.includes('B') && !norm.includes('C')) {
    return `<svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="1.6" width="36" height="36">
      <circle cx="12" cy="12" r="9.5"/>
      <circle cx="12" cy="12" r="3.5"/>
      <line x1="12" y1="8.5" x2="12" y2="2.5"/>
      <line x1="6.3" y1="15.5" x2="9.3" y2="13.4"/>
      <line x1="17.7" y1="15.5" x2="14.7" y2="13.4"/>
    </svg>`
  } else if (norm.includes('A')) {
    return `<svg viewBox="0 0 32 24" fill="none" stroke="#2D6A4F" stroke-width="1.6" width="36" height="36">
      <circle cx="6" cy="18" r="4"/>
      <circle cx="26" cy="18" r="4"/>
      <path d="M6 18h5l3-7h5l4 7"/>
      <path d="M14 11l1.5-4h3"/>
      <circle cx="20" cy="6" r="1.5"/>
    </svg>`
  } else if (norm.includes('BC') || norm.includes('C')) {
    return `<svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="1.6" width="36" height="36">
      <rect x="1" y="7" width="14" height="11" rx="1"/>
      <path d="M15 10h5l3 4v3h-8V10z"/>
      <circle cx="5.5" cy="18.5" r="1.5"/>
      <circle cx="18.5" cy="18.5" r="1.5"/>
    </svg>`
  } else if (norm.includes('D')) {
    return `<svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="1.6" width="36" height="36">
      <rect x="2" y="4" width="20" height="14" rx="2"/>
      <line x1="2" y1="9" x2="22" y2="9"/>
      <line x1="12" y1="4" x2="12" y2="18"/>
      <circle cx="6" cy="20" r="1.5"/>
      <circle cx="18" cy="20" r="1.5"/>
      <line x1="6" y1="18" x2="6" y2="21"/>
      <line x1="18" y1="18" x2="18" y2="21"/>
    </svg>`
  } else {
    return `<svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="1.6" width="36" height="36">
      <circle cx="12" cy="12" r="9.5"/>
      <path d="M12 8v8M8 12h8" stroke="#2D6A4F" stroke-width="1.6" stroke-linecap="round"/>
    </svg>`
  }
})

const formattedPrice = computed(() => {
  if (!category.value || !category.value.price) return "0 so'm"
  return Number(category.value.price).toLocaleString('uz-UZ') + " so'm"
})

// ── Fetch Category & Students ────────────────────────
const fetchData = async () => {
  loading.value = true
  error.value = ''
  try {
    // Always the full dataset — filtering/sorting/pagination above all
    // need to see every row, not just one page of them.
    const [catRes, stdRes, allCatsRes] = await Promise.all([
      api.get(`/categories/${categoryId}/`),
      api.get(`/students/`, { params: { category: categoryId, status: 'new', page: 1, page_size: 100000 } }),
      api.get(`/categories/`)
    ])
    category.value = catRes.data
    const stdList = Array.isArray(stdRes.data) ? stdRes.data : (stdRes.data?.results || [])
    students.value = stdList.map(mapStudent)
    totalCount.value = stdRes.data?.count ?? students.value.length
    categories.value = Array.isArray(allCatsRes.data) ? allCatsRes.data : (allCatsRes.data?.results || [])
  } catch (err) {
    console.error(err)
    error.value = "Ma'lumotlarni yuklashda xatolik yuz berdi."
  } finally {
    loading.value = false
  }
}

// Only fetchData (on mount) needs a backend round trip; every filter/sort
// above is purely client-side, and pageSizeOption now only controls how
// many of the filtered rows show per page.
watch(pageSizeOption, () => {
  currentPage.value = 1
})

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

const statusLabels = { new: 'Yangi', enrolled: 'Faol', finished: 'Tugatgan', canceled: 'Bekor qilingan' }

const mapStudent = (s) => {
  const dateStr = formatDateDisplay(s.date_joined || s.created_at)
  return {
    id: s.id,
    name: s.full_name,
    phone: formatPhoneDisplay(s.phone),
    phone2: s.phone2 ? formatPhoneDisplay(s.phone2) : '',
    jshshr: String(s.jshshr),
    passport: `${s.passport_serie} ${s.passport_number}`,
    passportSerie: s.passport_serie,
    passportNumber: s.passport_number,
    birthDateRaw: s.birth_date || '',
    date: dateStr,
    date_joined: dateStr,
    dateRaw: s.date_joined || s.created_at || null,
    status: statusLabels[s.status] || 'Yangi',
    rawStatus: s.status,
    categoryId: s.category_id,
    enrolledFree: s.enrolled_free || false,
    paymentAmount: formatPrice(s.payment_amount),
    paymentAmountRaw: Number(s.payment_amount) || 0,
    notes: s.notes || '',
  }
}

const statusClass = (rawStatus) => ({
  new: 'badge-new',
  enrolled: 'badge-enrolled',
  finished: 'badge-canceled',
  canceled: 'badge-canceled',
}[rawStatus] || 'badge-new')

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
  fetchData()
  
  // Light dismiss fallback (for browsers that don't yet support the native
  // `closedby="any"` dialog attribute)
  const lightDismissDialogs = [
    { dialog: studentModal, close: closeModal },
    { dialog: editStudentModal, close: closeEditModal },
    { dialog: groupConfirmModal, close: closeGroupConfirmModal },
  ]
  if (!('closedBy' in HTMLDialogElement.prototype)) {
    lightDismissDialogs.forEach(({ dialog, close }) => {
      if (!dialog.value) return
      dialog.value.addEventListener('click', (event) => {
        if (event.target !== dialog.value) return
        const rect = dialog.value.getBoundingClientRect()
        const isInside = (
          rect.top <= event.clientY &&
          event.clientY <= rect.top + rect.height &&
          rect.left <= event.clientX &&
          event.clientX <= rect.left + rect.width
        )
        if (!isInside) {
          close()
        }
      })
    })
  }

  document.addEventListener('click', handleSearchSelectOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleSearchSelectOutsideClick)
})

// Any click landing outside all instructor/coordinator/agent searchable
// selects closes whichever is open.
function handleSearchSelectOutsideClick(event) {
  if (event.target.closest('.search-select-container')) return
  isInstructorOpen.value = false
  isCoordinatorOpen.value = false
  isAgentOpen.value = false
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

const getUserFullName = (u) => {
  if (!u) return '-'
  const full = u.full_name || `${u.first_name || ''} ${u.last_name || ''}`.trim()
  return full || u.phone || `Xodim #${u.id}`
}

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
    birth_date: '',
    category: categoryId,
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
  
  if (!s.full_name.trim() || !phoneCleaned || !s.jshshr || !s.passport_serie.trim() || !s.passport_number || s.min_payment === null) {
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
  
  saving.value = true
  modalError.value = ''

  try {
    const payload = {
      full_name: s.full_name.trim(),
      phone: phoneCleaned,
      phone2: s.phone2 ? s.phone2.trim() : null,
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
      status: 'new', // Set student status to new!
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
    await fetchData()
  } catch (err) {
    console.error(err)
    if (err.response?.data?.phone) {
      modalError.value = "Ushbu telefon raqamli o'quvchi allaqachon mavjud."
    } else if (err.response?.data?.jshshr) {
      modalError.value = "Ushbu JSHSHR egasi bo'lgan o'quvchi allaqachon mavjud."
    } else if (err.response?.data?.passport_number) {
      modalError.value = "Ushbu passport raqamli o'quvchi allaqachon mavjud."
    } else {
      modalError.value = "Saqlashda xatolik yuz berdi. Ma'lumotlarni tekshirib qayta urinib ko'ring."
    }
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
/* ── Top actions / back link ──────────────────────────────── */
.page-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: background 0.15s, border-color 0.15s;
}
.btn-back:hover {
  background: #F9FAFB;
  border-color: #D1D5DB;
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

/* ── Category Header Card ─────────────────────────────────── */
.category-header-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  border-radius: 14px;
  padding: 24px 28px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
  margin-bottom: 24px;
}

.cat-details {
  display: flex;
  align-items: center;
  gap: 20px;
}

.cat-icon-wrap {
  width: 68px;
  height: 68px;
  background: #d1fae5;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.cat-info-block {
  text-align: left;
}

.cat-name {
  font-size: 20px;
  font-weight: 800;
  color: #111827;
  margin: 0 0 6px 0;
}

.cat-price {
  font-size: 14px;
  color: #6B7280;
  margin: 0;
  font-weight: 500;
}

.price-val {
  font-weight: 700;
  color: #111827;
  font-size: 15px;
}

.cat-stat-badge {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.stat-count {
  font-size: 36px;
  font-weight: 900;
  color: #2D6A4F;
  line-height: 1;
}

.stat-label {
  font-size: 13px;
  font-weight: 600;
  color: #6B7280;
  margin-top: 4px;
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

/* ── Table ─────────────────────────────────────────────────── */
.table-wrap {
  background: white;
  border-radius: 12px;
  border: 1px solid #E5E7EB;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

/* The scroll container is separate from .table-wrap so the whole table
   (including the checkbox column) scrolls together on the x-axis, while
   the title bar above it stays put. */
.table-scroll-area {
  overflow-x: auto;
}

/* ── Row-fetch-count pagination bar ──────────────────────────── */
.pagination-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #F9FAFB;
  border-top: 1px solid #E5E7EB;
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 12px;
}
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

.table-header {
  padding: 16px 20px;
  border-bottom: 1px solid #F3F4F6;
  text-align: left;
  display: flex;
  align-items: center;
  gap: 12px;
}

.table-header h3 {
  margin: 0;
  font-size: 15.5px;
  font-weight: 700;
  color: #111827;
}

.selected-count {
  font-size: 13px;
  font-weight: 600;
  color: #2D6A4F;
  background: #F0F7F4;
  padding: 3px 10px;
  border-radius: 20px;
}

.stbl {
  /* `width: 100%` would force every column (including the checkbox column)
     to always squeeze/stretch to fill the container instead of sizing to
     its own content — which both made narrower columns unreadable and
     prevented `.table-scroll-area`'s overflow-x from ever kicking in.
     `width: max-content` (no min-width) sizes each column strictly to its
     own text, growing past the container only when content actually needs
     the room, which is exactly when horizontal scroll should appear. */
  width: max-content;
  border-collapse: collapse;
  font-size: 13.5px;
}

/* Sticky on <thead> itself (not per-row) so both the label row and the
   filter row beneath it move together as one unit while the body scrolls
   vertically underneath — and both still scroll horizontally in sync with
   the body, since they're all part of the same table inside
   .table-scroll-area. */
.stbl thead {
  position: sticky;
  top: 0;
  z-index: 2;
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

.select-wrap-relative { position: relative; width: 100%; }

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
  text-align: left;
}

.td-muted { color: #6B7280; text-align: left; }

/* No data row */
.no-data {
  text-align: center;
  padding: 48px;
  color: #9CA3AF;
  font-size: 14.5px;
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

.badge-enrolled {
  background: #2D6A4F;
  color: white;
}

.badge-canceled {
  background: #DC2626;
  color: white;
}

.badge-free {
  background: #E8F5E9;
  color: #2E7D32;
  border: 1.5px solid #A5D6A7;
}

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
  text-align: left;
}

.modal-error {
  padding: 10px 12px;
  background: #FEE2E2;
  border-left: 4px solid #EF4444;
  color: #991B1B;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  text-align: left;
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

.weekday-picker { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 4px; }
.weekday-chip {
  padding: 8px 12px;
  border: 1.5px solid #D1D5DB;
  border-radius: 8px;
  font-size: 12.5px;
  font-weight: 600;
  color: #4B5563;
  background: #F9FAFB;
  cursor: pointer;
  user-select: none;
  transition: all 0.15s ease;
}
.weekday-chip:hover { border-color: #9CA3AF; }
.weekday-chip.active { background: #2D6A4F; border-color: #2D6A4F; color: white; }

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

.disabled-input {
  background: #F3F4F6;
  color: #9CA3AF;
  border-color: #E5E7EB;
  cursor: not-allowed;
}

.text-uppercase {
  text-transform: uppercase;
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

.top-actions-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.btn-start-group {
  padding: 10px 20px;
  background: #3B82F6;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: background 0.15s, transform 0.1s;
}
.btn-start-group:hover {
  background: #2563EB;
  transform: translateY(-1px);
}

.modal-confirm-body {
  padding: 10px 0;
  text-align: left;
  font-size: 14.5px;
  color: #374151;
  line-height: 1.5;
}

.modal-confirm-sub {
  margin-top: 8px;
  font-size: 13px;
  color: #6B7280;
}

.th-chk, .td-chk {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #2D6A4F;
}

/* Strict phone column width */
.th-phone, .td-phone {
  width: 175px !important;
  min-width: 175px !important;
  max-width: 175px !important;
  white-space: nowrap !important;
}

@media (max-width: 900px) {
  .table-scroll-area { overflow-x: auto; }
}
</style>
