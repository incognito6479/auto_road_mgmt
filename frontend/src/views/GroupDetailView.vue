<template>
  <AppLayout>

    <!-- Header navigation -->
    <div class="detail-header-nav">
      <button class="btn-back" @click="router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
        Orqaga
      </button>
      <div class="header-title-wrap">
        <h2 class="group-title">{{ group ? group.name : 'Guruh yuklanmoqda...' }}</h2>
        <span v-if="group" class="group-category-pill">{{ group.category_name }}</span>
      </div>
    </div>

    <!-- Loading / Error -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">Guruh ma'lumotlari yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchGroupDetail">Qayta urinish</button>
    </div>

    <div v-else-if="group" class="detail-content">

      <!-- Group summary card -->
      <div class="summary-card">
        <div class="summary-grid">
          <div class="summary-item">
            <span class="summary-label">Guruh nomi</span>
            <span class="summary-val font-bold">{{ group.name }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Kategoriya</span>
            <span class="summary-val">{{ group.category_name }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Boshlangan sana</span>
            <span class="summary-val">{{ formatDate(group.started_at) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Tugash sanasi</span>
            <span class="summary-val font-bold">{{ group.ends_at ? formatDate(group.ends_at) : '-' }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Ish kunlari</span>
            <span class="summary-val font-bold">{{ group.working_days ? group.working_days + ' kun' : '-' }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Dars kunlari</span>
            <span class="summary-val">{{ weekdaysText(group) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Davomiyligi</span>
            <span class="summary-val font-bold">{{ group.duration ? group.duration + ' oy' : '-' }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">O'quvchilar soni</span>
            <span class="summary-val font-bold">{{ group.student_count }} ta</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Holat</span>
            <span class="summary-val">
              <span class="status-badge" :class="statusClass(group.status)">
                {{ statusText(group.status) }}
              </span>
            </span>
          </div>
        </div>
        <div v-if="group.notes" class="notes-block">
          <span class="notes-label">Izoh:</span> {{ group.notes }}
        </div>
      </div>

      <!-- Students table section -->
      <div class="table-card">
        <div class="table-card-header">
          <h3 class="section-title">A'zo o'quvchilar</h3>
          <button v-if="!authStore.isMechanic" type="button" class="btn-export-excel" :disabled="exportingExcel" @click="exportPaymentsExcel">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            {{ exportingExcel ? 'Yuklanmoqda...' : "Excelga yuklash" }}
          </button>
        </div>

        <div class="table-container">
          <table class="students-table">
            <thead>
              <tr>
                <th>O'quvchi F.I.SH.</th>
                <th>Avtomaktab</th>
                <th>Holati</th>
                <th>Eslatmasi</th>
                <th>O'quv Joyi</th>
                <th>Dars Vaqti</th>
                <th>Dars Kunlari</th>
                <th>Sertifikat</th>
                <th>Imtihondan o'tganligi haqida rasm</th>
                <th v-if="authStore.isAdminOrSuperuser || authStore.isMechanic">O'qituvchi</th>
                <th v-if="authStore.isAdminOrSuperuser || authStore.isMechanic">Instruktor</th>
                <th v-if="authStore.isAdminOrSuperuser || authStore.isMechanic">Agent</th>
                <th v-if="!authStore.isMechanic">Shartnoma summasi</th>
                <th v-if="!authStore.isMechanic" class="sticky-col sticky-col-1">To'langan</th>
                <th v-if="!authStore.isMechanic" class="sticky-col sticky-col-2">Qoldiq</th>
                <th v-if="!authStore.isMechanic" class="sticky-col sticky-col-3" style="text-align: center;">Amallar</th>
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
                <th></th>
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
                  <input
                    v-model="filterLearningPlace"
                    class="col-filter-input"
                    type="text"
                    placeholder="O'quv joyi..."
                  />
                </th>
                <th>
                  <input
                    v-model="filterLearningTime"
                    class="col-filter-input"
                    type="text"
                    placeholder="Dars vaqti..."
                  />
                </th>
                <th>
                  <input
                    v-model="filterLearningDays"
                    class="col-filter-input"
                    type="text"
                    placeholder="Dars kunlari..."
                  />
                </th>
                <th>
                  <div class="select-wrap-relative">
                    <select v-model="filterCourseCert" class="col-filter-select">
                      <option value="">Barchasi</option>
                      <option value="uploaded">Bor</option>
                      <option value="not_uploaded">Yo'q</option>
                    </select>
                  </div>
                </th>
                <th>
                  <div class="select-wrap-relative">
                    <select v-model="filterExamCert" class="col-filter-select">
                      <option value="">Barchasi</option>
                      <option value="uploaded">Bor</option>
                      <option value="not_uploaded">Yo'q</option>
                    </select>
                  </div>
                </th>
                <th v-if="authStore.isAdminOrSuperuser || authStore.isMechanic">
                  <input
                    v-model="filterTeacherName"
                    class="col-filter-input"
                    type="text"
                    placeholder="O'qituvchi nomi..."
                  />
                </th>
                <th v-if="authStore.isAdminOrSuperuser || authStore.isMechanic">
                  <input
                    v-model="filterInstructorName"
                    class="col-filter-input"
                    type="text"
                    placeholder="Instruktor nomi..."
                  />
                </th>
                <th v-if="authStore.isAdminOrSuperuser || authStore.isMechanic">
                  <input
                    v-model="filterAgentName"
                    class="col-filter-input"
                    type="text"
                    placeholder="Agent nomi..."
                  />
                </th>
                <th v-if="!authStore.isMechanic">
                  <div class="select-wrap-relative">
                    <select v-model="filterEnrolledAmount" class="col-filter-select">
                      <option value="">Barchasi</option>
                      <option v-for="amt in distinctEnrolledAmounts" :key="amt" :value="amt">{{ formatMoney(amt) }}</option>
                    </select>
                  </div>
                </th>
                <th v-if="!authStore.isMechanic" class="sticky-col sticky-col-1"></th>
                <th v-if="!authStore.isMechanic" class="sticky-col sticky-col-2"></th>
                <th v-if="!authStore.isMechanic" class="sticky-col sticky-col-3"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="filteredEnrollments.length === 0">
                <td :colspan="tableColspan" class="td-empty">Hech qanday o'quvchi topilmadi.</td>
              </tr>
              <tr v-for="e in filteredEnrollments" :key="e.id" class="stbl-row clickable-row" @click="goToStudentDetail(e.student)">
                <td class="td-name link-value">{{ e.student_name }}</td>
                <td>{{ e.branch_name || '-' }}</td>
                <td><span class="enroll-status-chip" :class="e.status">{{ enrollmentStatusText(e.status) }}</span></td>
                <td class="td-notes">{{ e.notes || '-' }}</td>

                <!-- Learning Place Column -->
                <td class="td-assign" @click.stop>
                  <div class="assign-cell">
                    <template v-if="e.learning_place_name">
                      <span class="assign-name">{{ e.learning_place_name }}</span>
                      <button class="btn-assign-edit" @click.stop="openScheduleModal(e, 'place')" title="O'quv joyini o'zgartirish">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                          <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                      </button>
                    </template>
                    <template v-else>
                      <button class="btn-assign-plus" @click.stop="openScheduleModal(e, 'place')" title="O'quv joyi biriktirish">+</button>
                    </template>
                  </div>
                </td>

                <!-- Learning Time Column -->
                <td class="td-assign" @click.stop>
                  <div class="assign-cell">
                    <template v-if="e.learning_time">
                      <span class="assign-name">{{ e.learning_time }}</span>
                      <button class="btn-assign-edit" @click.stop="openScheduleModal(e, 'time')" title="Dars vaqtini o'zgartirish">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                          <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                      </button>
                    </template>
                    <template v-else>
                      <button class="btn-assign-plus" @click.stop="openScheduleModal(e, 'time')" title="Dars vaqtini biriktirish">+</button>
                    </template>
                  </div>
                </td>

                <!-- Learning Days Column -->
                <td class="td-assign" @click.stop>
                  <div class="assign-cell">
                    <template v-if="e.learning_days && e.learning_days.length">
                      <span class="assign-name">{{ formatLearningDays(e.learning_days) }}</span>
                      <button class="btn-assign-edit" @click.stop="openScheduleModal(e, 'days')" title="Dars kunlarini o'zgartirish">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                          <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                      </button>
                    </template>
                    <template v-else>
                      <button class="btn-assign-plus" @click.stop="openScheduleModal(e, 'days')" title="Dars kunlarini biriktirish">+</button>
                    </template>
                  </div>
                </td>

                <!-- Certificate (course completion) Column -->
                <td class="td-assign" @click.stop>
                  <div class="assign-cell">
                    <template v-if="e.student_certificate_number">
                      <div class="assign-name-col">
                        <span class="cert-value">{{ e.student_certificate_series || '' }} {{ e.student_certificate_number }}</span>
                        <div v-if="e.student_certificate_added_date" class="cert-date-sub">{{ formatDate(e.student_certificate_added_date) }}</div>
                      </div>
                      <button v-if="authStore.isAdminOrSuperuser" class="btn-assign-edit" @click.stop="openCertModal(e)" title="Sertifikatni o'zgartirish">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                          <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                      </button>
                    </template>
                    <template v-else>
                      <button v-if="authStore.isAdminOrSuperuser" class="btn-assign-plus" @click.stop="openCertModal(e)" title="Sertifikat qo'shish">+</button>
                      <span v-else>-</span>
                    </template>
                  </div>
                </td>

                <!-- Exam-Pass Certificate Image Column -->
                <td class="td-assign" @click.stop>
                  <div v-if="getStudentExamCert(e.student)" class="assign-name-col">
                    <button
                      type="button"
                      class="btn-view-cert"
                      @click.stop="openExamCertPreview(getStudentExamCert(e.student))"
                      title="Sertifikatni ko'rish"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                        <circle cx="12" cy="12" r="3"></circle>
                      </svg>
                      Ko'rish
                    </button>
                    <div v-if="getStudentExamCert(e.student).created_at" class="cert-date-sub">{{ formatDate(getStudentExamCert(e.student).created_at) }}</div>
                  </div>
                  <button v-else-if="authStore.canUploadCertificates" type="button" class="btn-assign-plus" @click.stop="openExamCertModal(e)" title="Imtihon sertifikatini yuklash">+</button>
                  <span v-else>-</span>
                </td>

                <!-- Coordinator ("Teacher") Column -->
                <td v-if="authStore.isAdminOrSuperuser || authStore.isMechanic" class="td-assign" @click.stop>
                  <div class="assign-cell">
                    <template v-if="e.coordinator_name">
                      <span class="assign-name link-value" @click="goUser(e.coordinator)">{{ e.coordinator_name }}</span>
                      <button class="btn-assign-edit" @click.stop="openAssignModal(e, 'coordinator')" title="O'qituvchini o'zgartirish">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                          <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                      </button>
                    </template>
                    <template v-else>
                      <button class="btn-assign-plus" @click.stop="openAssignModal(e, 'coordinator')" title="O'qituvchi biriktirish">+</button>
                    </template>
                  </div>
                </td>

                <!-- Instructor Column -->
                <td v-if="authStore.isAdminOrSuperuser || authStore.isMechanic" class="td-assign" @click.stop>
                  <div class="assign-cell">
                    <template v-if="e.instructor_name">
                      <span class="assign-name link-value" @click="goUser(e.instructor)">{{ e.instructor_name }}</span>
                      <button class="btn-assign-edit" @click.stop="openAssignModal(e, 'instructor')" title="Instruktorni o'zgartirish">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                          <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                      </button>
                    </template>
                    <template v-else>
                      <button class="btn-assign-plus" @click.stop="openAssignModal(e, 'instructor')" title="Instruktor biriktirish">+</button>
                    </template>
                  </div>
                </td>

                <!-- Agent Column -->
                <td v-if="authStore.isAdminOrSuperuser || authStore.isMechanic" class="td-assign" @click.stop>
                  <span v-if="e.agent_name" class="assign-name link-value" @click="goAgent(e.agent)">{{ e.agent_name }}</span>
                  <span v-else>-</span>
                </td>

                <!-- Payment Info Columns (Hidden for mechanic) -->
                <td v-if="!authStore.isMechanic">
                  <span v-if="e.enrolled_free" class="free-badge">Tekin</span>
                  <span v-else>{{ formatMoney(e.enrolled_amount) }}</span>
                </td>
                <td v-if="!authStore.isMechanic" class="sticky-col sticky-col-1">
                  <span v-if="e.enrolled_free">-</span>
                  <span v-else class="paid-val">{{ formatMoney(e.paid_amount) }}</span>
                </td>
                <td v-if="!authStore.isMechanic" class="sticky-col sticky-col-2">
                  <span v-if="e.enrolled_free">-</span>
                  <span v-else-if="e.excel_imported">{{ formatMoney(0) }}</span>
                  <span v-else :class="{'balance-warning': (e.enrolled_amount - e.paid_amount) > 0}">
                    {{ formatMoney(e.enrolled_amount - e.paid_amount) }}
                  </span>
                </td>
                <td v-if="!authStore.isMechanic" class="sticky-col sticky-col-3" style="text-align: center;" @click.stop>
                  <button
                    v-if="authStore.isAdminOrSuperuser && !e.enrolled_free && (e.excel_imported || e.paid_amount < e.enrolled_amount)"
                    class="btn-pay"
                    @click.stop="openPayModal(e)"
                  >
                    To'lash
                  </button>
                  <span v-else-if="!e.enrolled_free && e.paid_amount >= e.enrolled_amount" class="fully-paid-badge">To'liq to'langan</span>
                  <span v-else>-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- Payment Modal Dialog -->
    <dialog ref="payModal" class="modal-dialog">
      <div class="modal-header">
        <h3 class="modal-title">To'lov Qabul Qilish</h3>
        <button class="btn-close" @click="closePayModal">✕</button>
      </div>

      <form @submit.prevent="submitPayment" class="modal-form">
        <div v-if="payError" class="modal-error">
          {{ payError }}
        </div>

        <div v-if="activeEnrollment" class="pay-info-summary">
          <p>O'quvchi: <strong>{{ activeEnrollment.student_name }}</strong></p>
          <p>Jami shartnoma: <strong>{{ formatMoney(activeEnrollment.enrolled_amount) }}</strong></p>
          <p>Shu vaqtgacha to'langan: <strong>{{ formatMoney(activeEnrollment.paid_amount) }}</strong></p>
          <p v-if="!activeEnrollment.excel_imported">Qolgan qarzdorlik: <strong class="balance-warning">{{ formatMoney(activeEnrollment.enrolled_amount - activeEnrollment.paid_amount) }}</strong></p>
        </div>

        <div class="form-group">
          <label class="form-label">To'lanayotgan summa (so'm) <span class="req">*</span></label>
          <input
            v-model="formattedInputPrice"
            type="text"
            placeholder="Summani kiriting..."
            required
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label class="form-label">To'lov usuli <span class="req">*</span></label>
          <div class="select-wrap" style="position: relative; display: flex; width: 100%;">
            <select v-model="paymentForm.method" required class="form-input select-input" style="width: 100%; appearance: none;">
              <option value="cash">Naqd</option>
              <option value="card">Karta</option>
              <option value="qr_code">QR code</option>
              <option value="click">Click</option>
              <option value="transfer">O'tkazma</option>
            </select>
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #6B7280;">
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
            </svg>
          </div>
        </div>

        <div class="form-group" v-if="paymentForm.method === 'click'">
          <label class="form-label">Click cheki rasmi (ixtiyoriy)</label>
          <FileSelectInput ref="payCheckFileInputRef" accept="image/jpeg,image/png" @change="onPayCheckFileChange" />
        </div>

        <div class="form-group">
          <label class="form-label">Eslatma / Izoh</label>
          <textarea
            v-model="paymentForm.notes"
            rows="3"
            placeholder="Qo'shimcha izoh..."
            class="form-input text-area-input"
          ></textarea>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closePayModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="paySaving">
            <span v-if="paySaving" class="btn-spinner"></span>
            {{ paySaving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Assign Instructor / Coordinator Modal Dialog -->
    <dialog ref="assignModal" class="modal-dialog">
      <div class="modal-header">
        <h3 class="modal-title">
          {{ assignType === 'instructor' ? "Instruktor Biriktirish" : "O'qituvchi Biriktirish" }}
        </h3>
        <button class="btn-close" @click="closeAssignModal">✕</button>
      </div>

      <form @submit.prevent="submitAssign" class="modal-form">
        <div v-if="assignError" class="modal-error">
          {{ assignError }}
        </div>

        <div v-if="activeEnrollment" class="pay-info-summary">
          <p>O'quvchi: <strong>{{ activeEnrollment.student_name }}</strong></p>
          <p>Telefon: <strong>{{ formatPhone(activeEnrollment.student_phone) }}</strong></p>
        </div>

        <div class="form-group">
          <label class="form-label">
            {{ assignType === 'instructor' ? "Instruktorni tanlang" : "O'qituvchini tanlang" }}
          </label>

          <div class="assign-search-wrap" ref="assignSelectRef">
            <div class="assign-search-input-row">
              <svg viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" width="15" height="15">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
              <input
                v-model="assignSearchQuery"
                type="text"
                class="assign-search-input"
                :placeholder="assignType === 'instructor' ? 'Instruktor ismi yoki telefoni...' : &quot;O'qituvchi ismi yoki telefoni...&quot;"
                @click="assignDropdownOpen = !assignDropdownOpen"
                @input="assignDropdownOpen = true"
              />
              <button
                v-if="assignSearchQuery"
                type="button"
                class="assign-clear-btn"
                title="Tozalash"
                @click="assignSearchQuery = ''; assignDropdownOpen = true"
              >✕</button>
            </div>

            <div v-if="assignDropdownOpen" class="assign-dropdown">
              <div
                class="assign-option assign-option-clear"
                :class="{ 'is-active': selectedAssignUserId === null }"
                @click="pickAssignUser(null)"
              >
                &lt; Biriktirilmagan &gt;
              </div>
              <div
                v-for="u in filteredAssignUserOptions"
                :key="u.id"
                class="assign-option"
                :class="{ 'is-active': selectedAssignUserId === u.id }"
                @click="pickAssignUser(u.id)"
              >
                <div class="assign-option-avatar">{{ (getUserName(u) || '?').charAt(0).toUpperCase() }}</div>
                <div class="assign-option-info">
                  <span class="assign-option-name">{{ getUserName(u) || formatPhone(u.phone) }}</span>
                  <span class="assign-option-phone">{{ formatPhone(u.phone) }}</span>
                </div>
                <span v-if="selectedAssignUserId === u.id" class="assign-option-check">✓</span>
              </div>
              <div v-if="filteredAssignUserOptions.length === 0" class="assign-empty">
                {{ assignType === 'instructor' ? 'Instruktor topilmadi' : "O'qituvchi topilmadi" }}
              </div>
            </div>
          </div>

          <p class="assign-selected-hint">
            Tanlangan: <strong>{{ selectedAssignUserLabel }}</strong>
          </p>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closeAssignModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="assignSaving">
            <span v-if="assignSaving" class="btn-spinner"></span>
            {{ assignSaving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Schedule Modal Dialog (Learning Place / Time / Days — one at a time) -->
    <dialog ref="scheduleModal" class="modal-dialog">
      <div class="modal-header">
        <h3 class="modal-title">{{ scheduleModalTitle }}</h3>
        <button class="btn-close" @click="closeScheduleModal">✕</button>
      </div>

      <form @submit.prevent="submitSchedule" class="modal-form">
        <div v-if="scheduleError" class="modal-error">
          {{ scheduleError }}
        </div>

        <div v-if="activeEnrollment" class="pay-info-summary">
          <p>O'quvchi: <strong>{{ activeEnrollment.student_name }}</strong></p>
          <p>Telefon: <strong>{{ formatPhone(activeEnrollment.student_phone) }}</strong></p>
        </div>

        <div class="form-group" v-if="scheduleEditField === 'place'">
          <label class="form-label">O'quv joyi (Filial / Xona)</label>
          <div class="select-wrap" style="position: relative; display: flex; width: 100%;">
            <select v-model="scheduleForm.learning_place" class="form-input select-input" style="width: 100%; appearance: none;">
              <option :value="null">&lt; Tanlanmagan &gt;</option>
              <option v-for="p in learningPlaces" :key="p.id" :value="p.id">
                {{ p.place_name }}
              </option>
            </select>
            <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14" style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #6B7280;">
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
            </svg>
          </div>
        </div>

        <div class="form-group" v-if="scheduleEditField === 'time'">
          <label class="form-label">Dars vaqti</label>
          <input
            v-model="scheduleForm.learning_time"
            type="text"
            placeholder="Masalan: 09:00 yoki 14:00 - 16:00"
            class="form-input"
          />
        </div>

        <div class="form-group" v-if="scheduleEditField === 'days'">
          <label class="form-label">Dars kunlari</label>
          <div class="weekday-picker">
            <label v-for="d in weekdayOptions" :key="d.value" class="weekday-chip" :class="{ active: scheduleForm.learning_days.includes(d.value) }">
              <input type="checkbox" :value="d.value" v-model="scheduleForm.learning_days" style="display: none;" />
              {{ d.label }}
            </label>
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closeScheduleModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="scheduleSaving">
            <span v-if="scheduleSaving" class="btn-spinner"></span>
            {{ scheduleSaving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Certificate (course completion) Modal Dialog -->
    <dialog ref="certModal" class="modal-dialog">
      <div class="modal-header">
        <h3 class="modal-title">Kursni Tugatganlik Sertifikati</h3>
        <button class="btn-close" @click="closeCertModal">✕</button>
      </div>

      <form @submit.prevent="submitCertificate" class="modal-form">
        <div v-if="certError" class="modal-error">
          {{ certError }}
        </div>

        <div v-if="activeEnrollment" class="pay-info-summary">
          <p>O'quvchi: <strong>{{ activeEnrollment.student_name }}</strong></p>
        </div>

        <div class="form-group">
          <label class="form-label">Seriya</label>
          <input
            v-model="certForm.certificate_series"
            type="text"
            maxlength="2"
            placeholder="Masalan: AB"
            class="form-input"
            style="text-transform: uppercase;"
          />
        </div>

        <div class="form-group">
          <label class="form-label">Raqami</label>
          <input
            v-model="certForm.certificate_number"
            type="text"
            maxlength="9"
            placeholder="9 ta raqam"
            class="form-input"
          />
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closeCertModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="certSaving">
            <span v-if="certSaving" class="btn-spinner"></span>
            {{ certSaving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Exam-Pass Certificate Upload Modal (image, distinct from course-completion) -->
    <dialog ref="examCertModal" class="modal-dialog">
      <div class="modal-header">
        <h3 class="modal-title">Imtihon Sertifikatini Yuklash</h3>
        <button class="btn-close" @click="closeExamCertModal">✕</button>
      </div>

      <form @submit.prevent="submitExamCertUpload" class="modal-form">
        <div v-if="examCertError" class="modal-error">
          {{ examCertError }}
        </div>

        <div v-if="activeEnrollment" class="pay-info-summary">
          <p>O'quvchi: <strong>{{ activeEnrollment.student_name }}</strong></p>
        </div>

        <div class="form-group">
          <label class="form-label">Rasm</label>
          <FileSelectInput ref="examCertFileInputRef" accept="image/jpeg,image/png" required @change="onExamCertFileChange" />
        </div>

        <div class="form-group">
          <label class="form-label">Izoh (ixtiyoriy)</label>
          <input v-model="examCertNotes" type="text" placeholder="Izoh..." class="form-input" />
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="closeExamCertModal">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="examCertUploading || !examCertFile">
            <span v-if="examCertUploading" class="btn-spinner"></span>
            {{ examCertUploading ? 'Yuklanmoqda...' : 'Yuklash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Exam-Pass Certificate Preview Modal -->
    <dialog ref="examCertPreviewModal" class="modal-dialog cert-preview-dialog">
      <div class="modal-header">
        <h3 class="modal-title">Imtihon Sertifikati</h3>
        <button class="btn-close" @click="closeExamCertPreview">✕</button>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import FileSelectInput from '@/components/FileSelectInput.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useBranchStore } from '@/stores/branch'
import { formatLearningDays } from '@/utils/formatters'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const branchStore = useBranchStore()
const groupId = route.params.id

const goToStudentDetail = (studentId) => {
  if (studentId) {
    router.push(`/students/${studentId}`)
  }
}

function goUser(id) {
  if (id) router.push(`/users/${id}`)
}

const exportingExcel = ref(false)
async function exportPaymentsExcel() {
  if (exportingExcel.value) return
  exportingExcel.value = true
  try {
    const res = await api.get(`/groups/${groupId}/export-payments/`, { responseType: 'blob' })
    const url = URL.createObjectURL(new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }))
    const link = document.createElement('a')
    link.href = url
    link.download = `${group.value?.name || 'guruh'} to'lovlar.xlsx`
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  } catch (err) {
    console.error("Excelga yuklashda xatolik:", err)
  } finally {
    exportingExcel.value = false
  }
}

function goAgent(id) {
  if (!id || !(authStore.isAdminOrSuperuser || authStore.isMechanic)) return
  router.push(`/agents/${id}`)
}

const group = ref(null)
const loading = ref(false)
const error = ref('')
const allUsers = ref([])
const learningPlaces = ref([])

const weekendsText = (w) => {
  switch (w) {
    case 'everyday': return 'Har kuni (Mon-Sat)'
    case 'mon-wed-fri': return 'Dush-Chorsh-Juma'
    case 'tue-wed-sat': return 'Ses-Paysh-Shanba'
    default: return w || '-'
  }
}

const weekdayLabels = ['Dush', 'Sesh', 'Chor', 'Pay', 'Juma', 'Shan']
const weekdaysText = (g) => {
  if (Array.isArray(g.selected_weekdays) && g.selected_weekdays.length > 0) {
    return g.selected_weekdays
      .slice()
      .sort((a, b) => a - b)
      .map(v => weekdayLabels[v] || v)
      .join(', ')
  }
  return weekendsText(g.working_weekends)
}

// Column-head filter state
const filterName = ref('')
const filterEnrollmentStatus = ref('')
const filterLearningPlace = ref('')
const filterCourseCert = ref('')
const filterExamCert = ref('')
const filterTeacherName = ref('')
const filterInstructorName = ref('')
const filterAgentName = ref('')
const filterLearningTime = ref('')
const filterLearningDays = ref('')
const filterEnrolledAmount = ref('')

// Deduped, sorted list of contract amounts among this group's current
// students, for the "Shartnoma summasi" filter select.
const distinctEnrolledAmounts = computed(() => {
  const amounts = new Set()
  ;(group.value?.enrollments || []).forEach(e => {
    if (!e.enrolled_free && e.enrolled_amount) amounts.add(Number(e.enrolled_amount))
  })
  return [...amounts].sort((a, b) => a - b)
})

// Payment state
const payModal = ref(null)
const activeEnrollment = ref(null)
const paySaving = ref(false)
const payError = ref('')
const paymentForm = ref({
  amount: null,
  method: 'cash',
  notes: '',
})

// Assignment modal state
const assignModal = ref(null)
const assignType = ref('instructor') // 'instructor' or 'coordinator'
const selectedAssignUserId = ref(null)
const assignSaving = ref(false)
const assignError = ref('')

// Schedule modal state — one modal, scoped to a single field at a time
const scheduleModal = ref(null)
const scheduleSaving = ref(false)
const scheduleError = ref('')
const scheduleEditField = ref('place') // 'place' | 'time' | 'days'
const scheduleForm = ref({
  learning_place: null,
  learning_time: '',
  learning_days: [],
})

const scheduleModalTitle = computed(() => {
  if (scheduleEditField.value === 'time') return 'Dars Vaqtini Belgilash'
  if (scheduleEditField.value === 'days') return 'Dars Kunlarini Belgilash'
  return "O'quv Joyini Belgilash"
})

const weekdayOptions = [
  { value: 0, label: 'Dush' },
  { value: 1, label: 'Sesh' },
  { value: 2, label: 'Chor' },
  { value: 3, label: 'Pay' },
  { value: 4, label: 'Juma' },
  { value: 5, label: 'Shan' },
]

const tableColspan = computed(() => {
  let count = 9 // Student Name, Branch, Status, Notes, Learning Place, Learning Time, Learning Days, Sertifikat, Imtihon sertifikati
  if (authStore.isAdminOrSuperuser || authStore.isMechanic) count += 3 // Coordinator, Instructor, Agent
  if (!authStore.isMechanic) count += 4 // Shartnoma, Paid, Qoldiq, Amallar
  return count
})

const assignUserOptions = computed(() => {
  return allUsers.value.filter(u => u.role === assignType.value)
})

// ── Searchable assignment select ──────────────────────────────
const assignSearchQuery = ref('')
const assignDropdownOpen = ref(false)
const assignSelectRef = ref(null)

const filteredAssignUserOptions = computed(() => {
  const q = assignSearchQuery.value.trim().toLowerCase()
  if (!q) return assignUserOptions.value
  const qDigits = q.replace(/\D/g, '')
  return assignUserOptions.value.filter(u => {
    const name = getUserName(u).toLowerCase()
    const phone = (u.phone || '').replace(/\D/g, '')
    return name.includes(q) || (qDigits && phone.includes(qDigits))
  })
})

const selectedAssignUserLabel = computed(() => {
  if (selectedAssignUserId.value === null) return 'Biriktirilmagan'
  const u = assignUserOptions.value.find(x => x.id === selectedAssignUserId.value)
  return u ? getUserDisplayName(u) : 'Biriktirilmagan'
})

function pickAssignUser(id) {
  selectedAssignUserId.value = id
  assignDropdownOpen.value = false
  if (id === null) {
    assignSearchQuery.value = ''
    return
  }
  const u = assignUserOptions.value.find(x => x.id === id)
  assignSearchQuery.value = u ? (getUserName(u) || formatPhone(u.phone)) : ''
}

// Close the dropdown when the click lands outside the select. The input's own
// @click toggle handles clicks inside it.
function handleAssignOutsideClick(e) {
  if (assignSelectRef.value && !assignSelectRef.value.contains(e.target)) {
    assignDropdownOpen.value = false
  }
}

const getUserName = (u) => {
  if (!u) return ''
  return u.full_name?.trim() || `${u.first_name || ''} ${u.last_name || ''}`.trim()
}

const getUserDisplayName = (u) => {
  if (!u) return ''
  const name = getUserName(u)
  return name ? `${name} (${formatPhone(u.phone)})` : formatPhone(u.phone)
}

// Two-way space formatting for payment amount
const formattedInputPrice = computed({
  get() {
    if (paymentForm.value.amount === null || paymentForm.value.amount === undefined || isNaN(paymentForm.value.amount)) {
      return ''
    }
    return String(paymentForm.value.amount).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  },
  set(value) {
    const digits = value.replace(/\D/g, '')
    if (digits === '') {
      paymentForm.value.amount = null
    } else {
      paymentForm.value.amount = parseInt(digits, 10)
    }
  }
})

const fetchGroupDetail = async () => {
  loading.value = true
  error.value = ''
  try {
    // Awaited alongside the exam-cert list so the table doesn't render (and
    // read studentExamCerts) before that separate request finishes — else
    // every row briefly shows "no certificate" until it pops in a moment
    // later once fetchStudentExamCerts (fired in parallel in onMounted)
    // resolves.
    const [response] = await Promise.all([
      api.get(`/groups/${groupId}/`, { params: { with_enrollments: 1 } }),
      fetchStudentExamCerts(),
    ])
    group.value = response.data
  } catch (err) {
    console.error(err)
    error.value = "Guruh tafsilotlarini yuklashda xatolik yuz berdi."
  } finally {
    loading.value = false
  }
}

// After any row edit (schedule, assignment, payment), the just-edited
// enrollment jumps to the top of the table — same logic for every edit type.
const moveEnrollmentToTop = (id) => {
  if (!id || !group.value?.enrollments) return
  const idx = group.value.enrollments.findIndex(e => e.id === id)
  if (idx > 0) {
    const [item] = group.value.enrollments.splice(idx, 1)
    group.value.enrollments.unshift(item)
  }
}

const fetchUsers = async () => {
  try {
    const response = await api.get('/users/', { params: { page_size: 1000 } })
    allUsers.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
  } catch (err) {
    console.error("Foydalanuvchilarni yuklashda xatolik:", err)
  }
}

const fetchLearningPlaces = async () => {
  try {
    const response = await api.get('/learning-places/', { params: { page_size: 1000 } })
    learningPlaces.value = Array.isArray(response.data) ? response.data : (response.data.results || [])
  } catch (err) {
    console.error("O'quv joylarini yuklashda xatolik:", err)
  }
}

const filteredEnrollments = computed(() => {
  if (!group.value?.enrollments) return []
  const name = filterName.value.trim().toLowerCase()
  const place = filterLearningPlace.value.trim().toLowerCase()
  const teacher = filterTeacherName.value.trim().toLowerCase()
  const instructor = filterInstructorName.value.trim().toLowerCase()
  const agent = filterAgentName.value.trim().toLowerCase()
  const time = filterLearningTime.value.trim().toLowerCase()
  const days = filterLearningDays.value.trim().toLowerCase()
  return group.value.enrollments.filter(e => {
    if (name && !(e.student_name || '').toLowerCase().includes(name)) return false
    if (filterEnrollmentStatus.value && e.status !== filterEnrollmentStatus.value) return false
    if (place && !(e.learning_place_name || '').toLowerCase().includes(place)) return false
    if (teacher && !(e.coordinator_name || '').toLowerCase().includes(teacher)) return false
    if (instructor && !(e.instructor_name || '').toLowerCase().includes(instructor)) return false
    if (agent && !(e.agent_name || '').toLowerCase().includes(agent)) return false
    if (time && !(e.learning_time || '').toLowerCase().includes(time)) return false
    if (days && !formatLearningDays(e.learning_days || []).toLowerCase().includes(days)) return false
    if (filterEnrolledAmount.value && Number(e.enrolled_amount) !== Number(filterEnrolledAmount.value)) return false
    if (filterCourseCert.value) {
      const hasCourseCert = !!e.student_certificate_number
      if (filterCourseCert.value === 'uploaded' && !hasCourseCert) return false
      if (filterCourseCert.value === 'not_uploaded' && hasCourseCert) return false
    }
    if (filterExamCert.value) {
      const hasExamCert = !!getStudentExamCert(e.student)
      if (filterExamCert.value === 'uploaded' && !hasExamCert) return false
      if (filterExamCert.value === 'not_uploaded' && hasExamCert) return false
    }
    return true
  }).slice().sort((a, b) => (a.student_name || '').localeCompare(b.student_name || ''))
})

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('uz-UZ')
}

const formatPhone = (phoneStr) => {
  if (!phoneStr) return '-'
  if (phoneStr.length === 12) {
    return `+${phoneStr.substring(0, 3)} (${phoneStr.substring(3, 5)}) ${phoneStr.substring(5, 8)}-${phoneStr.substring(8, 10)}-${phoneStr.substring(10, 12)}`
  }
  return phoneStr
}

const formatMoney = (amount) => {
  if (amount === null || amount === undefined) return '0'
  return String(amount).replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
}

const statusText = (status) => {
  if (status === 'started') return 'Boshlangan'
  if (status === 'finished') return 'Tugatgan'
  if (status === 'canceled') return 'Bekor qilingan'
  return status
}

const statusClass = (status) => {
  return {
    'badge-started': status === 'started',
    'badge-finished': status === 'finished',
    'badge-canceled': status === 'canceled',
  }
}

// Enrollment.status (per-student) is a different set of choices than the
// group's own status above (new/enrolled/finished/canceled vs
// started/finished/canceled) — kept separate to avoid conflating the two.
const enrollmentStatusText = (status) => {
  switch (status) {
    case 'new': return 'Yangi'
    case 'enrolled': return 'Faol'
    case 'finished': return 'Tugatgan'
    case 'canceled': return 'Bekor qilingan'
    default: return status || '-'
  }
}

// Payment modal actions
const openPayModal = (enrollment) => {
  if (!authStore.isAdminOrSuperuser) {
    alert("To'lovni qabul qilish faqat admin va superuser uchun ruxsat etilgan.")
    return
  }
  activeEnrollment.value = enrollment
  payError.value = ''
  paymentForm.value = {
    amount: enrollment.excel_imported ? 0 : (enrollment.enrolled_amount - enrollment.paid_amount),
    method: 'cash',
    notes: '',
  }
  payCheckFile.value = null
  payCheckFileInputRef.value?.reset()
  if (payModal.value) {
    payModal.value.showModal()
  }
}
const payCheckFile = ref(null)
const payCheckFileInputRef = ref(null)
function onPayCheckFileChange(e) {
  payCheckFile.value = e.target.files?.[0] || null
}

const closePayModal = () => {
  if (payModal.value) {
    payModal.value.close()
  }
  activeEnrollment.value = null
}

const submitPayment = async () => {
  if (!authStore.isAdminOrSuperuser) {
    payError.value = "To'lovni qabul qilish faqat admin va superuser uchun ruxsat etilgan."
    return
  }

  if (paymentForm.value.amount === null || paymentForm.value.amount === undefined || paymentForm.value.amount <= 0) {
    payError.value = "To'g'ri to'lov summasini kiriting."
    return
  }

  paySaving.value = true
  payError.value = ''
  const enrollmentId = activeEnrollment.value.id
  try {
    if (payCheckFile.value) {
      const formData = new FormData()
      formData.append('enrollment', enrollmentId)
      formData.append('user', authStore.user?.id)
      formData.append('amount', parseInt(paymentForm.value.amount, 10))
      formData.append('method', paymentForm.value.method)
      if (paymentForm.value.notes.trim()) formData.append('notes', paymentForm.value.notes.trim())
      formData.append('status', 'accepted')
      formData.append('click_check_image', payCheckFile.value)
      await api.post('/payments/', formData)
    } else {
      const payload = {
        enrollment: enrollmentId,
        user: authStore.user?.id,
        amount: parseInt(paymentForm.value.amount, 10),
        method: paymentForm.value.method,
        notes: paymentForm.value.notes.trim() || null,
        status: 'accepted',
        branch: branchStore.activeBranchId ?? null,
      }
      await api.post('/payments/', payload)
    }
    closePayModal()
    await fetchGroupDetail()
    moveEnrollmentToTop(enrollmentId)
  } catch (err) {
    console.error(err)
    const data = err.response?.data
    if (data && typeof data === 'object') {
      const msgs = Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
      payError.value = msgs.join(' | ') || "To'lovni saqlashda xatolik yuz berdi. Qayta urinib ko'ring."
    } else {
      payError.value = "To'lovni saqlashda xatolik yuz berdi. Qayta urinib ko'ring."
    }
  } finally {
    paySaving.value = false
  }
}

// Assign modal actions
const openAssignModal = (enrollment, type) => {
  activeEnrollment.value = enrollment
  assignType.value = type
  assignError.value = ''
  assignSearchQuery.value = ''
  assignDropdownOpen.value = false
  if (type === 'instructor') {
    selectedAssignUserId.value = enrollment.instructor || null
  } else {
    selectedAssignUserId.value = enrollment.coordinator || null
  }
  if (assignModal.value) {
    assignModal.value.showModal()
  }
}

const closeAssignModal = () => {
  if (assignModal.value) {
    assignModal.value.close()
  }
}

const submitAssign = async () => {
  if (!activeEnrollment.value) return
  assignSaving.value = true
  assignError.value = ''
  const enrollmentId = activeEnrollment.value.id
  try {
    const payload = {}
    if (assignType.value === 'instructor') {
      payload.instructor = selectedAssignUserId.value
    } else {
      payload.coordinator = selectedAssignUserId.value
    }
    await api.patch(`/enrollments/${enrollmentId}/`, payload)
    closeAssignModal()
    await fetchGroupDetail()
    moveEnrollmentToTop(enrollmentId)
  } catch (err) {
    console.error(err)
    assignError.value = "Biriktirishda xatolik yuz berdi. Qayta urinib ko'ring."
  } finally {
    assignSaving.value = false
  }
}

// Schedule modal actions
const openScheduleModal = (enrollment, field) => {
  activeEnrollment.value = enrollment
  scheduleEditField.value = field
  scheduleError.value = ''
  scheduleForm.value = {
    learning_place: enrollment.learning_place || null,
    learning_time: enrollment.learning_time || '',
    learning_days: enrollment.learning_days || [],
  }
  if (scheduleModal.value) {
    scheduleModal.value.showModal()
  }
}

const closeScheduleModal = () => {
  if (scheduleModal.value) {
    scheduleModal.value.close()
  }
}

const submitSchedule = async () => {
  if (!activeEnrollment.value) return
  scheduleSaving.value = true
  scheduleError.value = ''
  const enrollmentId = activeEnrollment.value.id
  try {
    const payload = {
      learning_place: scheduleForm.value.learning_place,
      learning_time: scheduleForm.value.learning_time ? scheduleForm.value.learning_time.trim() : null,
      learning_days: scheduleForm.value.learning_days,
    }
    await api.patch(`/enrollments/${enrollmentId}/`, payload)
    closeScheduleModal()
    await fetchGroupDetail()
    moveEnrollmentToTop(enrollmentId)
  } catch (err) {
    console.error(err)
    scheduleError.value = "Saqlashda xatolik yuz berdi. Qayta urinib ko'ring."
  } finally {
    scheduleSaving.value = false
  }
}

// Certificate (course completion) modal actions
const certModal = ref(null)
const certSaving = ref(false)
const certError = ref('')
const certForm = ref({
  certificate_series: '',
  certificate_number: '',
})

const openCertModal = (enrollment) => {
  activeEnrollment.value = enrollment
  certError.value = ''
  certForm.value = {
    certificate_series: enrollment.student_certificate_series || 'SA',
    certificate_number: enrollment.student_certificate_number || '',
  }
  if (certModal.value) {
    certModal.value.showModal()
  }
}

const closeCertModal = () => {
  if (certModal.value) {
    certModal.value.close()
  }
}

const submitCertificate = async () => {
  if (!activeEnrollment.value) return
  const series = certForm.value.certificate_series.trim().toUpperCase()
  const number = certForm.value.certificate_number.trim()
  if (series && !/^[A-Z]{2}$/.test(series)) {
    certError.value = "Seriya 2 ta harfdan iborat bo'lishi kerak (masalan: AB)."
    return
  }
  if (number && !/^\d{9}$/.test(number)) {
    certError.value = "Raqam 9 ta raqamdan iborat bo'lishi kerak."
    return
  }
  certSaving.value = true
  certError.value = ''
  const enrollmentId = activeEnrollment.value.id
  const studentId = activeEnrollment.value.student
  try {
    await api.patch(`/students/${studentId}/`, {
      certificate_series: series || null,
      certificate_number: number || null,
    })
    closeCertModal()
    await fetchGroupDetail()
    moveEnrollmentToTop(enrollmentId)
  } catch (err) {
    console.error(err)
    certError.value = "Saqlashda xatolik yuz berdi. Qayta urinib ko'ring."
  } finally {
    certSaving.value = false
  }
}

// Exam-pass certificate (image upload) — a separate concept from the
// course-completion series/number certificate above. Tracks which students
// (across any instructor) already have one uploaded.
const studentExamCerts = ref([])

function getStudentExamCert(studentId) {
  return studentExamCerts.value.find(c => c.student === studentId) || null
}

async function fetchStudentExamCerts() {
  try {
    const res = await api.get('/student-certificates/', { params: { page_size: 1000 } })
    studentExamCerts.value = res.data.results || res.data || []
  } catch (err) {
    console.error("Sertifikatlar holatini yuklashda xatolik:", err)
  }
}

const examCertModal = ref(null)
const examCertFile = ref(null)
const examCertFileInputRef = ref(null)
const examCertNotes = ref('')
const examCertUploading = ref(false)
const examCertError = ref('')

function openExamCertModal(enrollment) {
  activeEnrollment.value = enrollment
  examCertFile.value = null
  examCertFileInputRef.value?.reset()
  examCertNotes.value = ''
  examCertError.value = ''
  examCertModal.value?.showModal()
}

function closeExamCertModal() {
  examCertModal.value?.close()
}

function onExamCertFileChange(e) {
  examCertFile.value = e.target.files?.[0] || null
}

const examCertPreviewModal = ref(null)
const previewingExamCert = ref(null)

function openExamCertPreview(cert) {
  previewingExamCert.value = cert
  examCertPreviewModal.value?.showModal()
}

function closeExamCertPreview() {
  examCertPreviewModal.value?.close()
}

async function submitExamCertUpload() {
  if (!examCertFile.value || !activeEnrollment.value) return
  examCertUploading.value = true
  examCertError.value = ''
  try {
    const formData = new FormData()
    formData.append('student', activeEnrollment.value.student)
    formData.append('image', examCertFile.value)
    if (examCertNotes.value) formData.append('notes', examCertNotes.value)
    await api.post('/student-certificates/', formData)
    closeExamCertModal()
    await fetchStudentExamCerts()
  } catch (err) {
    console.error(err)
    examCertError.value = err.response?.data?.detail || "Sertifikatni yuklashda xatolik yuz berdi."
  } finally {
    examCertUploading.value = false
  }
}

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchCurrentUser()
  }
  fetchGroupDetail()
  fetchUsers()
  fetchLearningPlaces()
  document.addEventListener('click', handleAssignOutsideClick)

  const dialogs = [payModal.value, assignModal.value, scheduleModal.value, certModal.value, examCertModal.value, examCertPreviewModal.value]
  dialogs.forEach(dialog => {
    if (dialog && !('closedBy' in HTMLDialogElement.prototype)) {
      dialog.addEventListener('click', (event) => {
        if (event.target !== dialog) return
        const rect = dialog.getBoundingClientRect()
        const isInside = (
          rect.top <= event.clientY &&
          event.clientY <= rect.top + rect.height &&
          rect.left <= event.clientX &&
          event.clientX <= rect.left + rect.width
        )
        if (!isInside) {
          dialog.close()
        }
      })
    }
  })
})

onUnmounted(() => {
  document.removeEventListener('click', handleAssignOutsideClick)
})
</script>

<style scoped>
/* ── Navigation ── */
.detail-header-nav {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}
.btn-back {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  color: #374151;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-back:hover {
  background: #F9FAFB;
  border-color: #D1D5DB;
  color: #111827;
}

.header-title-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
}
.group-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #111827;
}
.group-category-pill {
  background: #E8F5E9;
  color: #2D6A4F;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 20px;
}

/* ── Content Layout ── */
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Summary Card */
.summary-card {
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-label {
  font-size: 12px;
  font-weight: 600;
  color: #6B7280;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.summary-val {
  font-size: 14.5px;
  color: #111827;
}

.font-bold {
  font-weight: 700;
}

/* Status Badges */
.status-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.badge-started {
  background: #D1FAE5;
  color: #065F46;
}

.badge-finished {
  background: #DBEAFE;
  color: #1E40AF;
}

.badge-canceled {
  background: #FEE2E2;
  color: #991B1B;
}

.enroll-status-chip {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11.5px;
  font-weight: 600;
}
.enroll-status-chip.new { background: #E0F2FE; color: #0369A1; }
.enroll-status-chip.enrolled { background: #DCFCE7; color: #15803D; }
.enroll-status-chip.finished { background: #F3F4F6; color: #4B5563; }
.enroll-status-chip.canceled { background: #FEE2E2; color: #991B1B; }

.notes-block {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid #F3F4F6;
  font-size: 13.5px;
  color: #4B5563;
}
.notes-label {
  font-weight: 600;
  color: #111827;
}

/* ── Table Card ── */
.table-card {
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.table-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.section-title {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  color: #111827;
}

.btn-export-excel {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: #F0FDF4;
  color: #15803D;
  border: 1px solid #BBF7D0;
  border-radius: 8px;
  font-size: 12.5px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-export-excel:hover:not(:disabled) { background: #DCFCE7; }
.btn-export-excel:disabled { opacity: 0.6; cursor: not-allowed; }

/* Table */
.table-container {
  overflow-x: auto;
  border: 1px solid #E5E7EB;
  border-radius: 10px;
}

.students-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  text-align: left;
}

.students-table th {
  background: #F9FAFB;
  padding: 12px 16px;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #E5E7EB;
  white-space: nowrap;
}

/* Sticky is applied to <thead> itself, not to individual <th> cells — that
   keeps both header rows (labels + filters) moving as a single pinned unit. */
.students-table thead {
  position: sticky;
  top: 0;
  z-index: 3;
}

/* ── Column-head filters ─────────────────────────────────── */
/* Higher specificity than ".students-table th" (0,1,1) on purpose — equal
   specificity would let source order decide and flatten this row's
   padding/background back to the label row's values. */
.students-table thead tr.col-filter-row th {
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
  font-family: 'Inter', sans-serif;
  transition: border-color 0.15s;
}
.col-filter-input:focus { border-color: #2D6A4F; }
.col-filter-input::placeholder { color: #9CA3AF; }

.select-wrap-relative { position: relative; width: 100%; }
.col-filter-select {
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
.col-filter-select:focus { border-color: #2D6A4F; }

.students-table td {
  padding: 14px 16px;
  color: #4B5563;
  border-bottom: 1px solid #E5E7EB;
  vertical-align: middle;
}

.students-table tbody tr { cursor: pointer; }
.students-table tbody tr:hover td { background: #FAFAFA; }

/* ── Sticky right-hand columns (Paid / Remaining / Actions) ─────────────
   Fixed widths so the stacked `right` offsets are exact. Each cell needs
   its own opaque background — sticky cells overlap whatever scrolls
   underneath, and a transparent one would let that content show through. */
.sticky-col {
  position: sticky;
  background: white;
}
.students-table th.sticky-col { background: #F9FAFB; }
.students-table thead tr.col-filter-row th.sticky-col { background: #FAFAFB; }
.students-table tbody tr:hover td.sticky-col { background: #FAFAFA; }

.sticky-col-3 { right: 0; width: 130px; min-width: 130px; }
.sticky-col-2 { right: 130px; width: 110px; min-width: 110px; }
.sticky-col-1 {
  right: 240px;
  width: 110px;
  min-width: 110px;
  box-shadow: -6px 0 6px -6px rgba(0, 0, 0, 0.15);
}

.students-table tr:last-child td {
  border-bottom: none;
}

.td-name {
  font-weight: 600;
  color: #111827;
}

.td-notes {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.td-empty {
  text-align: center;
  padding: 40px;
  color: #9CA3AF;
  font-weight: 500;
}

/* Assignment Cells */
.td-assign {
  white-space: nowrap;
}
.assign-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
.assign-name {
  font-weight: 500;
  color: #111827;
  font-size: 13px;
}
.assign-name-col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.cert-value {
  font-weight: 500;
  color: #111827;
  font-size: 13px;
}
.cert-date-sub {
  font-size: 13px;
  font-weight: 700;
  color: #6B7280;
  margin-top: 3px;
}
.link-value { cursor: pointer; color: #2563EB !important; font-weight: 700 !important; text-decoration: underline; }
.link-value:hover { color: #1D4ED8 !important; }
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
.btn-assign-plus:hover {
  background: #2D6A4F;
  color: white;
  border-style: solid;
}
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
.btn-assign-edit:hover {
  background: #E5E7EB;
  color: #111827;
}

/* Pay Button */
.btn-pay {
  padding: 6px 14px;
  background: #2D6A4F;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 12.5px;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-pay:hover {
  background: #245C43;
}

.fully-paid-badge {
  font-size: 11.5px;
  font-weight: 600;
  color: #047857;
  background: #ecfdf5;
  padding: 4px 10px;
  border-radius: 12px;
  display: inline-block;
}

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

.free-badge {
  font-size: 11.5px;
  font-weight: 600;
  color: #B45309;
  background: #FFFBEB;
  padding: 4px 10px;
  border-radius: 12px;
  display: inline-block;
}

.balance-warning {
  color: #DC2626;
  font-weight: 700;
}

.paid-val {
  color: #047857;
  font-weight: 600;
}

/* Pay summary info */
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
.pay-info-summary p {
  margin: 0;
  color: #4B5563;
}
.pay-info-summary strong {
  color: #111827;
}

.text-area-input {
  resize: vertical;
  min-height: 80px;
}

/* ── Modal Dialog ───────────────────────────────────── */
.modal-dialog {
  border: none;
  border-radius: 16px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  background: white;
  max-height: 90vh;
  overflow-y: auto;
  margin: auto;
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

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 14px 24px;
  border-bottom: 1px solid #E5E7EB;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #111827;
}

.btn-close {
  background: none;
  border: none;
  font-size: 18px;
  color: #9CA3AF;
  cursor: pointer;
}
.btn-close:hover { color: #111827; }

.modal-error {
  padding: 10px 12px;
  background: #FEE2E2;
  border-left: 4px solid #EF4444;
  color: #991B1B;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
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
  color: #374151;
  background: white;
  cursor: pointer;
  user-select: none;
  transition: all 0.15s ease;
}
.weekday-chip:hover { border-color: #9CA3AF; }
.weekday-chip.active { background: #2D6A4F; border-color: #2D6A4F; color: white; }

.form-input {
  padding: 10px 12px;
  border: 1.5px solid #D1D5DB;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s;
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
}
.form-input:focus {
  border-color: #2D6A4F;
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
.btn-save:hover {
  background: #245C43;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* ── Searchable assignment select ─────────────────────── */
.assign-search-wrap { position: relative; width: 100%; }

.assign-search-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border: 1.5px solid #D1D5DB;
  border-radius: 10px;
  background: #F9FAFB;
  transition: all 0.15s ease;
}
.assign-search-input-row:focus-within {
  border-color: #2D6A4F;
  background: white;
  box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.12);
}

.assign-search-input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  outline: none;
  font-size: 13.5px;
  color: #111827;
  font-family: inherit;
}

.assign-clear-btn {
  border: none;
  background: #E5E7EB;
  color: #4B5563;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  font-size: 11px;
  line-height: 1;
  cursor: pointer;
  flex-shrink: 0;
}
.assign-clear-btn:hover { background: #D1D5DB; color: #111827; }

.assign-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  max-height: 240px;
  overflow-y: auto;
  background: white;
  border: 1.5px solid #2D6A4F;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
  z-index: 60;
}

.assign-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  cursor: pointer;
  border-bottom: 1px solid #F3F4F6;
  transition: background 0.12s ease;
}
.assign-option:last-child { border-bottom: none; }
.assign-option:hover { background: #F0FDF4; }
.assign-option.is-active { background: #E8F5E9; }

.assign-option-clear {
  font-size: 12.5px;
  font-weight: 600;
  color: #6B7280;
  font-style: italic;
}

.assign-option-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #2D6A4F;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.assign-option-info { display: flex; flex-direction: column; min-width: 0; flex: 1; }
.assign-option-name { font-size: 13px; font-weight: 600; color: #111827; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.assign-option-phone { font-size: 11.5px; color: #6B7280; }
.assign-option-check { color: #2D6A4F; font-weight: 700; flex-shrink: 0; }

.assign-empty { padding: 14px; text-align: center; color: #9CA3AF; font-size: 12.5px; }

.assign-selected-hint { margin-top: 8px; font-size: 12.5px; color: #6B7280; }
.assign-selected-hint strong { color: #2D6A4F; }

/* States */
.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  gap: 12px;
}
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #E5E7EB;
  border-top-color: #2D6A4F;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.state-text { color: #6B7280; font-size: 14px; }
.state-error { color: #DC2626; }
.btn-retry {
  padding: 8px 16px;
  background: #2D6A4F;
  color: white;
  border-radius: 6px;
  font-size: 13px;
}
</style>
