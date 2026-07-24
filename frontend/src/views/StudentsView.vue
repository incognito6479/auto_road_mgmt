<template>
  <AppLayout>

    <!-- Top action -->
    <div class="page-top">
      <button v-if="authStore.isAdminOrSuperuser" class="btn-add" @click="openModal">Yangi O'quvchi Qo'shish</button>
    </div>

    <!-- Filter card -->
    <div class="filter-card">
      <div class="filter-field">
        <label class="filter-label">Holat bo'yicha saralash</label>
        <div class="select-wrap">
          <select v-model="filterStatus" class="filter-select">
            <option value="">Barchasi</option>
            <option value="Yangi">Yangi</option>
            <option value="Qabul qilingan">Qabul qilingan</option>
            <option value="Tugatgan">Tugatgan</option>
          </select>
          <svg class="select-arrow" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
            <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
          </svg>
        </div>
      </div>

      <div class="filter-field">
        <label class="filter-label">Kategoriya bo'yicha saralash</label>
        <div class="select-wrap">
          <select v-model="filterCategory" class="filter-select">
            <option value="">Barchasi</option>
            <option v-for="c in categories" :key="c.id" :value="c.name">
              {{ c.name }}
            </option>
          </select>
          <svg class="select-arrow" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
            <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
          </svg>
        </div>
      </div>

      <div class="filter-field">
        <label class="filter-label">Ism yoki Telefon raqami bo'yicha qidirish</label>
        <input
          v-model="filterSearch"
          class="filter-input"
          type="text"
          placeholder="Ism yoki Telefon raqami bo'yicha qidirish"
        />
      </div>

      <div class="filter-field">
        <label class="filter-label">JSHSHR bo'yicha qidirish (faqat raqam)</label>
        <input
          v-model="filterJshshr"
          class="filter-input"
          type="text"
          placeholder="JSHSHR"
        />
      </div>
    </div>

    <!-- Loading / error states -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">O'quvchilar yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchStudents">Qayta urinish</button>
    </div>

    <!-- Table -->
    <div v-else class="table-wrap">
      <table class="stbl">
        <thead>
          <tr>
            <th>To'liq Ismi</th>
            <th>Kategoriya</th>
            <th class="th-phone">Telefon Raqami</th>
            <th>JSHSHR</th>
            <th>Passport Ma'lumotlari</th>
            <th>Ro'yxatdan o'tgan sana</th>
            <th>To'langan</th>
            <th>Holat</th>
            <th>Eslatma</th>
            <th>Amallar</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="students.length === 0">
            <td colspan="10" class="no-data">Ma'lumot topilmadi</td>
          </tr>
          <tr v-for="s in students" :key="s.id" class="stbl-row clickable-row" @click="goToStudentDetail(s.id)">
            <td class="td-name">{{ s.name }}</td>
            <td class="td-cat">{{ s.category }}</td>
            <td class="td-muted td-phone">
              <div>{{ s.phone }}</div>
              <div v-if="s.phone2" style="font-size: 11.5px; color: #6B7280; margin-top: 2px;">
                Qo'shimcha: {{ s.phone2 }}
              </div>
            </td>
            <td class="td-muted">{{ s.jshshr }}</td>
            <td class="td-muted">{{ s.passport }}</td>
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

      <!-- Pagination controls -->
      <div class="pagination-bar" style="display: flex; justify-content: space-between; align-items: center; margin-top: 20px; padding: 12px 16px; background: #F9FAFB; border-top: 1px solid #E5E7EB; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;">
        <span class="pagination-info" style="font-size: 13.5px; color: #6B7280; font-weight: 500;">
          Jami: <strong>{{ totalCount }}</strong> tadan <strong>{{ totalCount > 0 ? (currentPage - 1) * pageSize + 1 : 0 }} - {{ Math.min(currentPage * pageSize, totalCount) }}</strong> ko'rsatilmoqda
        </span>
        <div class="pagination-actions" style="display: flex; gap: 8px;">
          <button class="btn-page" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">
            Oldingi
          </button>
          <span class="page-num" style="display: inline-flex; align-items: center; padding: 0 12px; font-weight: 600; color: #374151; font-size: 14px;">
            Sahifa {{ currentPage }} / {{ totalPages }}
          </span>
          <button class="btn-page" :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">
            Keyingi
          </button>
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
          <!-- Row 1: Personal Details -->
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
              type="tel"
              placeholder="+998 90 123 45 67 (ixtiyoriy)"
              class="form-input"
            />
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
          <div class="form-group">
            <label for="std-days" class="form-label">O'quv Kunlari (ixtiyoriy)</label>
            <div class="select-wrap">
              <select id="std-days" v-model="newStudent.learning_days" class="form-input select-input">
                <option value="">-- Kunlarni tanlang --</option>
                <option value="Mo-Wed-Fri">Dush - Chor - Jum (Mo-Wed-Fri)</option>
                <option value="Tue-Thu-Sat">Sesh - Pay - Shan (Tue-Thu-Sat)</option>
                <option value="everyday">Har kuni (Everyday)</option>
              </select>
              <svg class="select-arrow-modal" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
              </svg>
            </div>
          </div>

          <!-- Instruktor Searchable Select -->
          <div class="form-group staff-select-group">
            <label class="form-label">Instruktor (ixtiyoriy)</label>
            <div class="search-select-container">
              <div 
                class="search-select-trigger" 
                :class="{ 'is-open': isInstructorOpen, 'has-selected': selectedInstructor }"
                @click="isInstructorOpen = !isInstructorOpen; isCoordinatorOpen = false"
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
                    <span>Instruktorni tanlash...</span>
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
                    v-for="inst in filteredInstructors"
                    :key="inst.id"
                    class="dropdown-option-row"
                    :class="{ 'is-active': newStudent.instructor === inst.id }"
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
                    <span>O'qituvchini tanlash...</span>
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
                    v-for="coord in filteredCoordinators"
                    :key="coord.id"
                    class="dropdown-option-row"
                    :class="{ 'is-active': newStudent.coordinator === coord.id }"
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
                    <span>{{ agentSearch ? agentSearch : "Agentni tanlash..." }}</span>
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
                    v-for="ag in filteredAgents"
                    :key="ag.id"
                    class="dropdown-option-row"
                    :class="{ 'is-active': newStudent.agent === ag.id }"
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
                <option value="cash">💵 Naqd pul</option>
                <option value="card">💳 Plastik karta</option>
                <option value="qr_code">📱 QR-kod orqali</option>
                <option value="transfer">🏦 Bank o'tkazmasi</option>
              </select>
              <svg class="select-arrow-modal" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
              </svg>
            </div>
          </div>

          <!-- Row 6: Checkboxes, Custom Price & Notes -->
          <div class="form-group checkbox-group" style="grid-column: span 3; display: flex; align-items: center; gap: 24px; margin-top: 8px;">
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

          <div v-if="newStudent.has_custom_price && !newStudent.enrolled_free" class="form-group" style="grid-column: span 3;">
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
              type="tel"
              placeholder="+998 90 123 45 67 (ixtiyoriy)"
              class="form-input"
            />
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
                <option value="enrolled">Qabul qilingan</option>
                <option value="finished">Tugatgan</option>
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

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const goToStudentDetail = (id) => {
  router.push(`/students/${id}`)
}

// ── Filter state ─────────────────────────────────────────────
const filterStatus = ref('')
const filterCategory = ref('')
const filterSearch = ref('')
const filterJshshr = ref('')

// Pagination state
const currentPage = ref(1)
const totalCount = ref(0)
const pageSize = 50
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize) || 1)

// ── Loading & state ──────────────────────────────────────────
const students = ref([])
const categories = ref([])
const loading = ref(false)
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
  category: '',
  min_payment: null,
  enrolled_free: false,
  has_custom_price: false,
  enrolled_amount: null,
  notes: '',
})
const saving = ref(false)
const modalError = ref('')

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

watch(() => editingStudent.value.phone2, (newValue) => {
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
    editingStudent.value.phone2 = formatted
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

  const phone2Cleaned = s.phone2 ? s.phone2.replace(/\D/g, '') : null
  if (phone2Cleaned && phone2Cleaned.length < 12) {
    editModalError.value = "Qo'shimcha telefon raqami noto'g'ri kiritilgan."
    return
  }

  editSaving.value = true
  editModalError.value = ''

  try {
    const payload = {
      full_name: s.full_name.trim(),
      phone: phoneCleaned,
      phone2: phone2Cleaned,
      jshshr: parseInt(s.jshshr, 10),
      passport_serie: s.passport_serie.trim().toUpperCase(),
      passport_number: parseInt(s.passport_number, 10),
      category: parseInt(s.category, 10),
      status: s.status,
      notes: s.notes,
    }

    await api.patch(`/students/${s.id}/`, payload)
    closeEditModal()
    await fetchStudents()
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

watch(() => newStudent.value.phone2, (newValue) => {
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
    newStudent.value.phone2 = formatted
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

// ── Fetch data ───────────────────────────────────────────────
const fetchStudents = async () => {
  loading.value = true
  error.value = ''
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize
    }
    if (filterStatus.value) params.status = filterStatus.value
    if (filterCategory.value) params.category = filterCategory.value
    if (filterSearch.value) params.search = filterSearch.value.trim()
    if (filterJshshr.value) params.jshshr = filterJshshr.value.trim()

    const response = await api.get('/students/', { params })
    const rawList = response.data.results ? response.data.results : (Array.isArray(response.data) ? response.data : [])
    students.value = rawList.map(mapStudent)
    totalCount.value = response.data.count ?? rawList.length
  } catch (err) {
    console.error(err)
    error.value = "O'quvchilarni yuklashda xatolik yuz berdi."
  } finally {
    loading.value = false
  }
}

watch(
  [filterStatus, filterCategory, filterSearch, filterJshshr],
  () => {
    currentPage.value = 1
    fetchStudents()
  }
)

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchStudents()
}

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
  if (s.status === 'enrolled') statusText = "Qabul qilingan"
  else if (s.status === 'finished') statusText = 'Tugatgan'
  
  const dateStr = formatDateDisplay(s.date_joined || s.created_at)
  
  return {
    id: s.id,
    name: s.full_name || `${s.first_name || ''} ${s.last_name || ''}`.trim() || 'Noma\'lum',
    category: s.category || '-',
    categoryId: s.category_id,
    phone: formatPhoneDisplay(s.phone),
    phone2: s.phone2 ? formatPhoneDisplay(s.phone2) : '',
    jshshr: s.jshshr ? String(s.jshshr) : '-',
    passport: (s.passport_serie || s.passport_number) ? `${s.passport_serie || ''} ${s.passport_number || ''}`.trim() : '-',
    passportSerie: s.passport_serie || '',
    passportNumber: s.passport_number || '',
    date: dateStr,
    date_joined: dateStr,
    status: statusText,
    rawStatus: s.status,
    enrolledFree: s.enrolled_free || false,
    paymentAmount: formatPrice(s.payment_amount),
    notes: s.notes || '',
  }
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
  fetchStudents()
  fetchCategories()
  
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
})



// ── Status badge class ───────────────────────────────────────
function statusClass(status) {
  if (status === 'Yangi') return 'badge-new'
  if (status === "Qabul qilingan" || status === "Ro'yxatdan o'tgan") return 'badge-registered'
  if (status === 'Tugatgan') return 'badge-done'
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

const fetchStaff = async () => {
  try {
    const res = await api.get('/users/')
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
    const res = await api.get('/learning-places/')
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

const fetchAgents = async () => {
  try {
    const res = await api.get('/agents/')
    agents.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
  } catch (err) {
    console.error('Failed to fetch agents:', err)
  }
}

// ── Modal Actions ────────────────────────────────────────────
const openModal = async () => {
  if (!authStore.isAdminOrSuperuser) {
    alert("O'quvchini ro'yxatdan o'tkazish faqat admin va superuser uchun ruxsat etilgan.")
    return
  }
  await Promise.all([fetchStaff(), fetchLearningPlaces(), fetchAgents()])
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
    learning_days: '',
    min_payment: null,
    payment_method: 'cash',
    enrolled_free: false,
    has_custom_price: false,
    enrolled_amount: null,
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
  
  const phone2Cleaned = s.phone2 ? s.phone2.replace(/\D/g, '') : null
  if (phone2Cleaned && phone2Cleaned.length < 12) {
    modalError.value = "Qo'shimcha telefon raqami noto'g'ri kiritilgan."
    return
  }

  saving.value = true
  modalError.value = ''
  
  try {
    const payload = {
      full_name: s.full_name.trim(),
      phone: phoneCleaned,
      phone2: phone2Cleaned,
      jshshr: parseInt(s.jshshr, 10),
      passport_serie: s.passport_serie.trim().toUpperCase(),
      passport_number: parseInt(s.passport_number, 10),
      category: parseInt(s.category, 10),
      instructor: s.instructor || null,
      coordinator: s.coordinator || null,
      agent: s.agent || null,
      learning_place: s.learning_place || null,
      learning_time: s.learning_time ? s.learning_time.trim() : null,
      learning_days: s.learning_days || null,
      min_payment: parseInt(s.min_payment, 10),
      payment_method: s.payment_method || 'cash',
      enrolled_free: s.enrolled_free || false,
      enrolled_amount: (s.has_custom_price && !s.enrolled_free) ? parseInt(s.enrolled_amount, 10) : null,
      notes: s.notes,
      status: 'new' // Register new student in new status
    }
    
    await api.post('/students/', payload)
    closeModal()
    await fetchStudents()
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
/* ── Top action ─────────────────────────────────────────── */
.page-top {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
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

/* ── Filter card ─────────────────────────────────────────── */
.filter-card {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 20px;
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-label {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
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

/* Text inputs */
.filter-input {
  padding: 9px 12px;
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  font-size: 13px;
  color: #374151;
  outline: none;
  font-family: 'Inter', sans-serif;
  transition: border-color 0.15s;
}
.filter-input:focus { border-color: #2D6A4F; }
.filter-input::placeholder { color: #9CA3AF; }

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
  overflow-x: auto;
}

.stbl {
  width: 100%;
  border-collapse: collapse;
  font-size: 13.5px;
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
  background: #1B2430;
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

/* Pagination styles */
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
.btn-page:hover:not(:disabled) {
  background: #F3F4F6;
  border-color: #D1D5DB;
}
.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Strict phone column width */
.th-phone, .td-phone {
  width: 175px !important;
  min-width: 175px !important;
  max-width: 175px !important;
  white-space: nowrap !important;
}

/* ── Responsive ─────────────────────────────────────────────── */
@media (max-width: 900px) {
  .filter-card { grid-template-columns: 1fr; }
  .table-wrap  { overflow-x: auto; }
}
</style>
