<template>
  <AppLayout>

    <!-- ───────────────────── HEADER ───────────────────── -->
    <div class="detail-header">
      <button class="btn-back" v-if="!authStore.isStudent" @click="$router.back()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
        Orqaga
      </button>

      <div v-if="student" class="header-info">
        <div class="header-avatar" @click="openImageModal(student.image || '/default_photo.png')" title="Rasmni kattalashtirish">
          <img :src="student.image || '/default_photo.png'" alt="Student" class="user-avatar-img" />
        </div>
        <div>
          <h1 class="header-name">{{ student.full_name || student.phone }}</h1>
          <div class="header-meta">
            <span class="status-badge" :class="statusClass(activeStatus)">{{ statusText(activeStatus) }}</span>
            <span class="meta-sep">·</span>
            <span class="meta-phone">{{ formatPhone(student.phone) }}</span>
            <template v-if="student.phone2">
              <span class="meta-sep">·</span>
              <span class="meta-phone">{{ formatPhone(student.phone2) }}</span>
            </template>
            <template v-if="enrollment?.category_name">
              <span class="meta-sep">·</span>
              <span class="meta-cat">{{ enrollment.category_name }}</span>
            </template>
          </div>
        </div>
      </div>

      <div class="header-actions" v-if="student">
        <button class="btn-view-pass-header" v-if="student.pass_img" @click="openPassportPreview">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
          Pasport rasmi
        </button>
        <button class="btn-confirm-lesson" v-if="canAddLesson" @click="openLessonModal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          Amaliy haydash darsini tasdiqlash
        </button>
        <button class="btn-payment" v-if="canTakePayment" @click="openPaymentModal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
            <rect x="2" y="5" width="20" height="14" rx="2"/>
            <line x1="2" y1="10" x2="22" y2="10"/>
          </svg>
          To'lov qabul qilish
        </button>
        <button class="btn-edit-main" v-if="authStore.isAdminOrSuperuser" @click="openEditModal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          Tahrirlash
        </button>
      </div>
    </div>

    <!-- LOADING / ERROR -->
    <div v-if="loading" class="state-box">
      <div class="spinner"></div>
      <p>Yuklanmoqda...</p>
    </div>
    <div v-else-if="error" class="state-box state-error">
      <p>{{ error }}</p>
      <button class="btn-retry" @click="fetchAll">Qayta urinish</button>
    </div>

    <!-- CONTENT GRID -->
    <div v-else-if="student" class="content-grid">

      <!-- LEFT COLUMN -->
      <div class="col-left">

        <!-- Student Info Card -->
        <div class="detail-card">
          <div class="card-header">
            <span class="card-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </span>
            <h2 class="card-title">Shaxsiy Ma'lumotlar</h2>
          </div>
          <div class="info-grid">
            <div class="info-row"><span class="info-label">To'liq Ismi</span><span class="info-value fw">{{ student.full_name || '-' }}</span></div>
            <div class="info-row"><span class="info-label">Telefon</span><span class="info-value">{{ formatPhone(student.phone) || '-' }}</span></div>
            <div class="info-row" v-if="student.phone2"><span class="info-label">Qo'shimcha tel.</span><span class="info-value">{{ formatPhone(student.phone2) }}</span></div>
            <div class="info-row"><span class="info-label">JSHSHR</span><span class="info-value mono">{{ student.jshshr || '-' }}</span></div>
            <div class="info-row"><span class="info-label">Pasport</span><span class="info-value mono">{{ student.passport_serie || '' }} {{ student.passport_number || '' }}</span></div>
            <div class="info-row">
              <span class="info-label">Pasport nusxasi</span>
              <span class="info-value">
                <button v-if="student.pass_img" type="button" class="btn-view-pass" @click="openPassportPreview">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  Pasport rasmini ko'rish
                </button>
                <span v-else style="color: #9CA3AF; font-size: 13px;">Yuklanmagan</span>
              </span>
            </div>
            <div class="info-row"><span class="info-label">Ro'yxatdan o'tgan</span><span class="info-value">{{ formatDate(student.date_joined) }}</span></div>
            <div class="info-row" v-if="student.notes"><span class="info-label">Eslatma</span><span class="info-value">{{ student.notes }}</span></div>
          </div>
        </div>

        <!-- Enrollment Card -->
        <div class="detail-card" v-if="enrollment">
          <div class="card-header">
            <span class="card-icon card-icon-blue">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>
            </span>
            <h2 class="card-title">O'quv Ma'lumotlari</h2>
          </div>
          <div class="info-grid">
            <div class="info-row"><span class="info-label">Kategoriya</span><span class="info-value"><span class="cat-badge">{{ enrollment.category_name || '-' }}</span></span></div>
            <div class="info-row"><span class="info-label">Holat</span><span class="info-value"><span class="status-badge" :class="statusClass(activeStatus)">{{ statusText(activeStatus) }}</span></span></div>
            <div class="info-row" v-if="enrollment.instructor_name"><span class="info-label">Instruktor</span><span class="info-value">{{ enrollment.instructor_name }}</span></div>
            <div class="info-row" v-if="enrollment.coordinator_name"><span class="info-label">O'qituvchi</span><span class="info-value">{{ enrollment.coordinator_name }}</span></div>
            <div class="info-row" v-if="enrollment.learning_place_name"><span class="info-label">O'quv joyi</span><span class="info-value">{{ enrollment.learning_place_name }}</span></div>
            <div class="info-row" v-if="enrollment.learning_time"><span class="info-label">O'quv vaqti</span><span class="info-value">{{ enrollment.learning_time }}</span></div>
            <div class="info-row" v-if="enrollment.learning_days"><span class="info-label">O'quv kunlari</span><span class="info-value">{{ formatLearningDays(enrollment.learning_days) }}</span></div>
            <div class="info-row" v-if="enrollment.agent_name"><span class="info-label">Agent</span><span class="info-value">{{ enrollment.agent_name }}</span></div>
            <div class="info-row" v-if="canSeePaymentInfo"><span class="info-label">Shartnoma summasi</span><span class="info-value fw"><span v-if="enrollment.enrolled_free" class="badge-free">Tekin (Bonus)</span><span v-else>{{ formatMoney(enrollment.enrolled_amount) }}</span></span></div>
          </div>
        </div>

        <!-- Group Card -->
        <div class="detail-card">
          <div class="card-header">
            <span class="card-icon card-icon-purple">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            </span>
            <h2 class="card-title">Guruh Ma'lumotlari</h2>
          </div>
          <div class="info-grid">
            <div class="info-row">
              <span class="info-label">Guruh nomi</span>
              <span class="info-value fw">{{ group ? group.name : "Biriktirilmagan" }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Kategoriya</span>
              <span class="info-value">{{ group?.category_name || enrollment?.category_name || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Boshlanish sanasi</span>
              <span class="info-value">{{ group?.started_at ? formatDate(group.started_at) : '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Davomiylik</span>
              <span class="info-value">{{ group?.duration ? (group.duration + ' oy') : '-' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Guruh holati</span>
              <span class="info-value">
                <span class="status-badge" :class="group ? groupStatusClass(group.status) : 'badge-notstarted'">
                  {{ group ? groupStatusText(group.status) : 'Boshlanmagan' }}
                </span>
              </span>
            </div>
          </div>
        </div>

        <!-- Teachers & Reviews Card -->
        <div class="detail-card" v-if="teacherCards.length > 0">
          <div class="teacher-tabs">
            <button type="button" class="teacher-tab-btn" :class="{ active: activeTeacherTab === 'info' }" @click="activeTeacherTab = 'info'">
              O'qituvchilar
            </button>
            <button type="button" class="teacher-tab-btn" :class="{ active: activeTeacherTab === 'cars' }" @click="activeTeacherTab = 'cars'">
              🚘 Avtomobillar
            </button>
          </div>

          <div v-if="activeTeacherTab === 'info'" class="teacher-cards-wrap">
            <div
              v-for="t in teacherCards"
              :key="t.role"
              class="teacher-mini-card clickable"
              @click="goTeacher(t.info.id)"
            >
              <img :src="t.info.image || '/default_photo.png'" alt="Teacher" class="teacher-mini-avatar" />
              <div class="teacher-mini-info">
                <div class="teacher-mini-name">{{ t.info.full_name || t.info.phone }}</div>
                <div class="teacher-mini-role">{{ t.roleLabel }}</div>
                <div class="teacher-mini-phone">{{ formatPhone(t.info.phone) }}</div>
                <div v-if="teacherRatings[t.info.id]" class="teacher-mini-rating">
                  ⭐ {{ teacherRatings[t.info.id].avg }} <span class="rating-count">({{ teacherRatings[t.info.id].count }} ta sharh)</span>
                </div>
              </div>
              <button v-if="canLeaveReview" type="button" class="btn-leave-review" @click.stop="openReviewModal(t)">
                ⭐ Sharh qoldirish
              </button>
            </div>
          </div>

          <div v-else class="teacher-cars-wrap">
            <div v-if="loadingTeacherCars" class="mini-state"><div class="spinner spinner-sm"></div><span>Yuklanmoqda...</span></div>
            <template v-else>
              <div v-for="t in teacherCards.filter(x => x.role === 'instructor')" :key="t.role" class="teacher-cars-group">
                <div class="teacher-cars-owner">{{ t.info.full_name || t.info.phone }}</div>
                <div v-if="!teacherCars[t.info.id] || teacherCars[t.info.id].length === 0" class="empty-certs">
                  Biriktirilgan avtomobil topilmadi.
                </div>
                <div v-else class="cars-grid">
                  <div v-for="c in teacherCars[t.info.id]" :key="c.id" class="car-mini-card" @click="goCar(c.id)">
                    <img :src="c.image || '/default_car_photo.png'" alt="Car" class="car-mini-image" />
                    <div class="car-mini-info">
                      <div class="car-mini-name">{{ c.car_name }}</div>
                      <div class="car-mini-sub">{{ c.manufact_year || '-' }} · <span class="car-status-chip" :class="c.status">{{ carStatusText(c.status) }}</span></div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="teacherCards.filter(x => x.role === 'instructor').length === 0" class="empty-certs">
                Instruktor biriktirilmagan.
              </div>
            </template>
          </div>

          <div v-if="reviews.length > 0" class="reviews-list">
            <div class="reviews-list-title">Sharhlar</div>
            <div v-for="r in reviews" :key="r.id" class="review-item">
              <div class="review-item-top">
                <span class="review-stars">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5 - r.rating) }}</span>
                <span class="review-teacher">{{ r.teacher_name }}</span>
                <span class="review-date">{{ formatDate(r.created_at) }}</span>
              </div>
              <p v-if="r.comment" class="review-comment">{{ r.comment }}</p>
            </div>
          </div>
        </div>

        <!-- Certificates Card -->
        <div class="detail-card" v-if="canUploadCertificate || certificates.length > 0 || authStore.isAdminOrSuperuser">
          <div class="card-header">
            <span class="card-icon card-icon-amber">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><circle cx="12" cy="8" r="6"/><path d="M8.21 13.89L7 23l5-3 5 3-1.21-9.12"/></svg>
            </span>
            <h2 class="card-title">Imtihondan o'tganligi haqida</h2>
            <button v-if="canUploadCertificate" type="button" class="btn-add-payment" @click="openCertModal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Qo'shish
            </button>
          </div>

          <div v-if="certificates.length === 0" class="empty-certs">Hali ma'lumot yuklanmagan.</div>
          <div v-else class="certs-grid">
            <div v-for="c in certificates" :key="c.id" class="cert-card">
              <img :src="c.image" alt="Imtihondan o'tganligi haqida" class="cert-image" @click="openImageModal(c.image)" />
              <div class="cert-meta">
                <div class="cert-uploader">{{ c.instructor_name || '-' }}</div>
                <div class="cert-date">{{ formatDate(c.created_at) }}</div>
                <p v-if="c.notes" class="cert-notes">{{ c.notes }}</p>
              </div>
              <div v-if="authStore.isAdminOrSuperuser" class="cert-bonus-row">
                <span v-if="c.bonus_paid" class="bonus-paid-badge">✓ Bonus to'landi ({{ formatMoney(c.bonus_amount) }})</span>
                <button v-else type="button" class="btn-pay-cert-bonus" @click="openBonusModal(c)">Bonus to'lash</button>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- RIGHT COLUMN -->
      <div class="col-right">

        <!-- Payment Summary -->
        <div class="detail-card" v-if="enrollment && canSeePaymentInfo">
          <div class="card-header">
            <span class="card-icon card-icon-green">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            </span>
            <h2 class="card-title">To'lov Holati</h2>
            <button class="btn-add-payment" v-if="canTakePayment" @click="openPaymentModal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              To'lov
            </button>
          </div>
          <div class="payment-stats">
            <div class="pay-stat"><div class="pay-stat-label">Shartnoma</div><div class="pay-stat-value">{{ enrollment.enrolled_free ? 'Tekin' : formatMoney(enrollment.enrolled_amount) }}</div></div>
            <div class="pay-stat"><div class="pay-stat-label">To'langan</div><div class="pay-stat-value green">{{ formatMoney(paidTotal) }}</div></div>
            <div class="pay-stat"><div class="pay-stat-label">Qoldiq</div><div class="pay-stat-value" :class="remaining > 0 ? 'red' : 'green'">{{ enrollment.enrolled_free ? '—' : formatMoney(remaining) }}</div></div>
          </div>
          <div class="progress-wrap" v-if="!enrollment.enrolled_free && enrollment.enrolled_amount > 0">
            <div class="progress-bar"><div class="progress-fill" :style="{ width: progressPct + '%' }"></div></div>
            <span class="progress-label">{{ progressPct }}%</span>
          </div>
        </div>

        <!-- Payment History -->
        <div class="detail-card" v-if="canSeePaymentInfo">
          <div class="card-header">
            <span class="card-icon card-icon-orange">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            </span>
            <h2 class="card-title">To'lovlar Tarixi</h2>
          </div>
          <div v-if="loadingPayments" class="mini-state"><div class="spinner spinner-sm"></div><span>Yuklanmoqda...</span></div>
          <div v-else-if="payments.length === 0" class="mini-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="#D1D5DB" stroke-width="1.5" width="32" height="32"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
            <span>To'lovlar mavjud emas</span>
          </div>
          <div v-else class="pay-table-wrap">
            <table class="pay-table">
              <thead><tr><th>Sana</th><th>Summa</th><th>Usul</th><th>Holat</th><th>Eslatma</th></tr></thead>
              <tbody>
                <tr v-for="p in payments" :key="p.id" class="pay-row">
                  <td class="td-date">{{ formatDateTime(p.created_at) }}</td>
                  <td class="td-amount">{{ formatMoney(p.amount) }}</td>
                  <td><span class="method-badge">{{ methodText(p.method) }}</span></td>
                  <td><span class="pay-status-badge" :class="payStatusClass(p.status)">{{ payStatusText(p.status) }}</span></td>
                  <td class="td-notes">{{ p.notes || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Driving Lessons History -->
        <div class="detail-card margin-top-card">
          <div class="card-header">
            <span class="card-icon card-icon-purple">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
            </span>
            <h2 class="card-title">Amaliy Haydash Darslari Tarixi</h2>
            <button class="btn-add-payment btn-add-lesson" v-if="canAddLesson" @click="openLessonModal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              Dars tasdiqlash
            </button>
          </div>

          <div v-if="loadingLessons" class="mini-state">
            <div class="spinner spinner-sm"></div>
            <span>Yuklanmoqda...</span>
          </div>

          <div v-else-if="drivingLessons.length === 0" class="mini-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="#D1D5DB" stroke-width="1.5" width="32" height="32">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <span>Tasdiqlangan amaliy darslar mavjud emas</span>
          </div>

          <div v-else class="pay-table-wrap">
            <table class="pay-table">
              <thead>
                <tr>
                  <th>Sana</th>
                  <th>Instruktor</th>
                  <th>Avtomobil</th>
                  <th>Holat</th>
                  <th>Izoh</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="l in drivingLessons" :key="l.id" class="pay-row">
                  <td class="td-date font-bold">📅 {{ formatDateTime(l.lesson_date) }}</td>
                  <td><span class="instructor-chip font-bold">👤 {{ l.instructor_name || '-' }}</span></td>
                  <td><span class="car-chip font-bold">🚘 {{ l.car_name || '-' }}</span></td>
                  <td><span class="pay-status-badge pstatus-accepted">✓ Tasdiqlangan</span></td>
                  <td class="td-notes">{{ l.notes || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- EDIT MODAL -->
    <dialog ref="editModal" class="modal-dialog" closedby="any">
      <form class="modal-form" @submit.prevent="saveStudent">
        <div class="modal-head">
          <h3 class="modal-title">O'quvchini Tahrirlash</h3>
          <button type="button" class="btn-close" @click="editModal?.close()">✕</button>
        </div>
        <div v-if="editError" class="modal-error">{{ editError }}</div>
        <div class="form-section">
          <div class="section-tag">Shaxsiy Ma'lumotlar</div>
          <div class="form-grid-2">
            <div class="form-group fg-full"><label class="form-label">To'liq Ismi <span class="req">*</span></label><input v-model="editForm.full_name" type="text" class="form-input" placeholder="Ali Valiyev" required/></div>
            <div class="form-group"><label class="form-label">Telefon <span class="req">*</span></label><input v-model="editForm.phone" type="text" class="form-input" placeholder="+998 90 123 45 67" @input="onEditPhoneInput" required/></div>
            <div class="form-group"><label class="form-label">Qo'shimcha Telefon</label><input v-model="editForm.phone2" type="text" class="form-input" placeholder="+998 90 123 45 67 otasi / amakisi"/></div>
            <div class="form-group"><label class="form-label">JSHSHR</label><input v-model="editForm.jshshr" type="text" maxlength="14" class="form-input mono" placeholder="14 ta raqam"/></div>
            <div class="form-group"><label class="form-label">Pasport Seriyasi</label><input v-model="editForm.passport_serie" type="text" maxlength="2" class="form-input text-upper" placeholder="AA"/></div>
            <div class="form-group"><label class="form-label">Pasport Raqami</label><input v-model="editForm.passport_number" type="text" maxlength="7" class="form-input mono" placeholder="1234567"/></div>
            <div class="form-group">
              <label class="form-label">O'quvchi Rasmi (Foto)</label>
              <div style="display: flex; align-items: center; gap: 10px; width: 100%;">
                <img v-if="editForm.existingImage" :src="editForm.existingImage" alt="Photo" style="width: 36px; height: 36px; border-radius: 50%; object-fit: cover; border: 1px solid #E5E7EB; flex-shrink: 0;" />
                <input type="file" accept="image/*" class="form-input" style="width: 100%;" @change="onEditStudentPhotoChange" />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Pasport Rasmi / Nusxasi</label>
              <div style="display: flex; align-items: center; gap: 10px; width: 100%;">
                <img v-if="editForm.existingPassImg" :src="editForm.existingPassImg" alt="Passport" style="width: 36px; height: 36px; border-radius: 6px; object-fit: cover; border: 1px solid #E5E7EB; flex-shrink: 0;" />
                <input type="file" accept="image/*,.pdf" class="form-input" style="width: 100%;" @change="onEditPassportPhotoChange" />
              </div>
            </div>
          </div>
        </div>
        <div class="form-section">
          <div class="section-tag">Holat va Eslatmalar</div>
          <div class="form-grid-2">
            <div class="form-group">
              <label class="form-label">Holat</label>
              <div class="select-wrap">
                <select v-model="editForm.status" class="form-input form-select">
                  <option value="new">Yangi</option>
                  <option value="enrolled">Faol</option>
                  <option value="finished">Tugatgan</option>
                  <option value="canceled">Bekor qilingan</option>
                </select>
                <svg class="sel-arrow" viewBox="0 0 20 20" fill="currentColor" width="14" height="14"><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/></svg>
              </div>
            </div>
            <div class="form-group"><label class="form-label">O'quv Vaqti (ixtiyoriy)</label><input v-model="editForm.learning_time" type="text" class="form-input" placeholder="Masalan: 09:00"/></div>
            <div class="form-group fg-full">
              <label class="form-label">O'quv Kunlari (ixtiyoriy)</label>
              <div class="weekday-picker">
                <label v-for="d in weekdayOptions" :key="d.value" class="weekday-chip" :class="{ active: editForm.learning_days.includes(d.value) }">
                  <input type="checkbox" :value="d.value" v-model="editForm.learning_days" style="display: none;" />
                  {{ d.label }}
                </label>
              </div>
            </div>
            <div class="form-group fg-full"><label class="form-label">Eslatma</label><textarea v-model="editForm.notes" class="form-input" rows="3" placeholder="Qo'shimcha eslatmalar..."></textarea></div>
          </div>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="editModal?.close()">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="editSaving"><span v-if="editSaving" class="btn-spinner"></span>{{ editSaving ? 'Saqlanmoqda...' : 'Saqlash' }}</button>
        </div>
      </form>
    </dialog>

    <!-- PAYMENT MODAL -->
    <dialog ref="paymentModal" class="modal-dialog modal-sm" closedby="any">
      <form class="modal-form" @submit.prevent="savePayment">
        <div class="modal-head">
          <h3 class="modal-title">To'lov Qabul Qilish</h3>
          <button type="button" class="btn-close" @click="paymentModal?.close()">✕</button>
        </div>
        <div v-if="payError" class="modal-error">{{ payError }}</div>
        <div class="form-section">
          <div class="pay-remaining-hint" v-if="!enrollment?.enrolled_free">
            Qoldiq: <strong>{{ formatMoney(remaining) }}</strong>
          </div>
          <div class="form-grid-2">
            <div class="form-group fg-full"><label class="form-label">Summa <span class="req">*</span></label><input v-model="payForm.amountFormatted" type="text" class="form-input" placeholder="0" required @input="onPayAmountInput"/></div>
            <div class="form-group">
              <label class="form-label">To'lov usuli</label>
              <div class="select-wrap">
                <select v-model="payForm.method" class="form-input form-select"><option value="cash">Naqd</option><option value="card">Karta</option><option value="qr_code">QR code</option><option value="transfer">O'tkazma</option></select>
                <svg class="sel-arrow" viewBox="0 0 20 20" fill="currentColor" width="14" height="14"><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/></svg>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">To'lov holati</label>
              <div class="select-wrap">
                <select v-model="payForm.status" class="form-input form-select"><option value="accepted">Qabul qilingan</option><option value="paid">To'langan</option><option value="bank">Bank</option></select>
                <svg class="sel-arrow" viewBox="0 0 20 20" fill="currentColor" width="14" height="14"><path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/></svg>
              </div>
            </div>
            <div class="form-group fg-full"><label class="form-label">Eslatma</label><input v-model="payForm.notes" type="text" class="form-input" placeholder="Ixtiyoriy..."/></div>
          </div>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="paymentModal?.close()">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="paySaving"><span v-if="paySaving" class="btn-spinner"></span>{{ paySaving ? 'Saqlanmoqda...' : "To'lovni Saqlash" }}</button>
        </div>
      </form>
    </dialog>

    <!-- DRIVING LESSON CONFIRMATION MODAL -->
    <dialog ref="lessonModal" class="modal-dialog" closedby="any">
      <form class="modal-form" @submit.prevent="submitLessonConfirmation">
        <div class="modal-head">
          <h3 class="modal-title">🏎️ Amaliy Haydash Darsini Tasdiqlash</h3>
          <button type="button" class="btn-close" @click="lessonModal?.close()">✕</button>
        </div>
        <div v-if="lessonError" class="modal-error">{{ lessonError }}</div>
        <div v-if="lessonSuccess" class="alert-success-box">{{ lessonSuccess }}</div>

        <div class="form-section">
          <div class="form-grid-2">

            <!-- Student (Disabled) -->
            <div class="form-group fg-full">
              <label class="form-label">O'quvchi F.I.SH. (Cheklangan)</label>
              <input :value="student?.full_name" type="text" class="form-input disabled-input" disabled />
            </div>

            <!-- Instructor (Disabled) -->
            <div class="form-group">
              <label class="form-label">Instruktor (Cheklangan)</label>
              <input :value="enrollment?.instructor_name || 'Instruktor biriktirilmagan'" type="text" class="form-input disabled-input" disabled />
            </div>

            <!-- Date (Disabled) -->
            <div class="form-group">
              <label class="form-label">Dars Sanasi (Cheklangan)</label>
              <input :value="todayDateFormatted" type="text" class="form-input disabled-input" disabled />
            </div>

            <!-- Instructor's Car (Disabled) -->
            <div class="form-group fg-full">
              <label class="form-label">Avtomobil (Instruktorga biriktirilgan, Cheklangan)</label>
              <input
                :value="instructorCar ? `🚘 ${instructorCar.car_name} (${instructorCar.manufact_year || '-'})` : 'Instruktorga avtomobil biriktirilmagan'"
                type="text"
                class="form-input disabled-input"
                disabled
              />
            </div>

            <!-- Notes -->
            <div class="form-group fg-full">
              <label class="form-label">Izoh / Eslatma</label>
              <input v-model="lessonForm.notes" type="text" class="form-input" placeholder="Amaliy dars bo'yicha qo'shimcha izoh..." />
            </div>

          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="lessonModal?.close()">Bekor qilish</button>
          <button type="submit" class="btn-save btn-green" :disabled="lessonSaving">
            <span v-if="lessonSaving" class="btn-spinner"></span>
            {{ lessonSaving ? 'Tasdiqlanmoqda...' : 'Darsni Tasdiqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- LEAVE REVIEW MODAL -->
    <dialog ref="reviewModal" class="modal-dialog modal-sm" closedby="any">
      <form class="modal-form" @submit.prevent="submitReview">
        <div class="modal-head">
          <h3 class="modal-title">Sharh qoldirish: {{ reviewTarget?.info?.full_name || reviewTarget?.info?.phone }}</h3>
          <button type="button" class="btn-close" @click="reviewModal?.close()">✕</button>
        </div>
        <div v-if="reviewError" class="modal-error">{{ reviewError }}</div>

        <div class="form-section">
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
            <textarea v-model="reviewForm.comment" rows="3" class="form-input"></textarea>
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="reviewModal?.close()">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="reviewSaving">
            <span v-if="reviewSaving" class="btn-spinner"></span>{{ reviewSaving ? 'Yuborilmoqda...' : 'Yuborish' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- ADD CERTIFICATE MODAL -->
    <dialog ref="certModal" class="modal-dialog modal-sm" closedby="any">
      <form class="modal-form" @submit.prevent="uploadCertificate">
        <div class="modal-head">
          <h3 class="modal-title">Imtihondan o'tganligi haqida qo'shish</h3>
          <button type="button" class="btn-close" @click="certModal?.close()">✕</button>
        </div>
        <div v-if="certUploadError" class="modal-error">{{ certUploadError }}</div>

        <div class="form-section">
          <div class="form-group">
            <label class="form-label">Rasm <span class="req">*</span></label>
            <input type="file" accept="image/*" class="form-input" @change="onCertFileChange" required />
          </div>

          <div class="form-group">
            <label class="form-label">Izoh (ixtiyoriy)</label>
            <input v-model="certNotes" type="text" placeholder="Izoh..." class="form-input" />
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="certModal?.close()">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="certUploading || !selectedCertFile">
            <span v-if="certUploading" class="btn-spinner"></span>{{ certUploading ? 'Yuklanmoqda...' : 'Yuklash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- PAY TEACHER BONUS MODAL -->
    <dialog ref="bonusModal" class="modal-dialog modal-sm" closedby="any">
      <form class="modal-form" @submit.prevent="submitCertBonus">
        <div class="modal-head">
          <h3 class="modal-title">Instruktorga bonus to'lash</h3>
          <button type="button" class="btn-close" @click="bonusModal?.close()">✕</button>
        </div>
        <div v-if="bonusError" class="modal-error">{{ bonusError }}</div>

        <div class="form-section">
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
              <option value="transfer">O'tkazma</option>
            </select>
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-cancel" @click="bonusModal?.close()">Bekor qilish</button>
          <button type="submit" class="btn-save" :disabled="bonusSaving">
            <span v-if="bonusSaving" class="btn-spinner"></span>{{ bonusSaving ? 'Saqlanmoqda...' : "To'lash" }}
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

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const student    = ref(null)
const enrollment = ref(null)
const payments   = ref([])
const group      = ref(null)
const loading    = ref(false)
const loadingPayments = ref(false)
const error      = ref('')

const editModal    = ref(null)
const paymentModal = ref(null)
const lessonModal  = ref(null)
const imageZoomModal = ref(null)
const zoomedImageUrl = ref('')

// ── Teachers, reviews & certificates ──────────────────
const instructorInfo = ref(null)
const coordinatorInfo = ref(null)
const reviews = ref([])
const certificates = ref([])
const activeTeacherTab = ref('info')
const teacherRatings = ref({})
const teacherCars = ref({})
const loadingTeacherCars = ref(false)

const teacherCards = computed(() => {
  const arr = []
  if (instructorInfo.value) arr.push({ role: 'instructor', roleLabel: 'Instruktor', info: instructorInfo.value })
  if (coordinatorInfo.value) arr.push({ role: 'coordinator', roleLabel: "O'qituvchi", info: coordinatorInfo.value })
  return arr
})

// Only the student themself, viewing their own page, may leave a review.
const canLeaveReview = computed(() => !!(
  authStore.canLeaveReviews && student.value && authStore.user?.id === student.value.id
))

// Certificates are uploaded by instructors (and admins/superusers) — never by
// the student whose page this is.
const canUploadCertificate = computed(() => !!(
  authStore.canUploadCertificates && student.value && authStore.user?.id !== student.value.id
))

// Taking/recording payments is admin/superuser business, but teaching staff
// (instructors/coordinators) can see a student's payment info read-only, and
// the student sees their own.
const canSeePaymentInfo = computed(() => !!(
  authStore.canManageFinances ||
  authStore.isTeachingStaff ||
  (authStore.isStudent && student.value && authStore.user?.id === student.value.id)
))

// Taking a payment is admin/superuser only.
const canTakePayment = computed(() => !!(
  authStore.canManageFinances && !enrollment.value?.enrolled_free && !isFullyPaid.value
))

// Students log their own practical-driving history; admins/superusers may too.
const canAddLesson = computed(() => !!(
  authStore.canAddDrivingLesson &&
  (!authStore.isStudent || (student.value && authStore.user?.id === student.value.id))
))

// Students may open their teachers' profiles (to leave a review). Instructors
// and coordinators may only open their *own* profile — not another teacher's.
function goTeacher(id) {
  if (!id) return
  if (authStore.isTeachingStaff && authStore.user?.id !== id) return
  router.push(`/users/${id}`)
}

function goCar(id) {
  if (!id || authStore.isStudent) return
  router.push(`/vehicles/${id}`)
}

function carStatusText(st) {
  switch (st) {
    case 'available': return 'Mavjud'
    case 'repairing': return "Ta'mirlashda"
    case 'not_available': return 'Mavjud emas'
    default: return st || 'Mavjud'
  }
}

async function fetchTeacherInfo() {
  instructorInfo.value = null
  coordinatorInfo.value = null
  if (!enrollment.value) return
  try {
    const calls = []
    if (enrollment.value.instructor) {
      calls.push(api.get(`/users/${enrollment.value.instructor}/`).then(r => { instructorInfo.value = r.data }))
    }
    if (enrollment.value.coordinator) {
      calls.push(api.get(`/users/${enrollment.value.coordinator}/`).then(r => { coordinatorInfo.value = r.data }))
    }
    await Promise.all(calls)
  } catch (err) {
    console.error("O'qituvchi ma'lumotlarini yuklashda xatolik:", err)
  }
}

// Average rating per teacher, computed across ALL students' reviews for
// that teacher (not just this student's own review) — matches the same
// aggregate shown on the teacher's own UserDetailView profile.
async function fetchTeacherRatings() {
  teacherRatings.value = {}
  const ids = teacherCards.value.map(t => t.info?.id).filter(Boolean)
  if (ids.length === 0) return
  try {
    const results = await Promise.all(ids.map(id =>
      api.get('/teacher-reviews/', { params: { teacher: id, page_size: 200 } })
        .then(res => ({ id, list: res.data.results || res.data || [] }))
    ))
    const ratings = {}
    results.forEach(({ id, list }) => {
      if (list.length === 0) return
      const sum = list.reduce((acc, r) => acc + (r.rating || 0), 0)
      ratings[id] = { avg: (sum / list.length).toFixed(1), count: list.length }
    })
    teacherRatings.value = ratings
  } catch (err) {
    console.error("Reyting ma'lumotlarini yuklashda xatolik:", err)
  }
}

async function fetchTeacherCars() {
  teacherCars.value = {}
  const instructorIds = teacherCards.value.filter(t => t.role === 'instructor').map(t => t.info?.id).filter(Boolean)
  if (instructorIds.length === 0) return
  loadingTeacherCars.value = true
  try {
    const results = await Promise.all(instructorIds.map(id =>
      api.get('/cars/', { params: { instructor: id, page_size: 100 } })
        .then(res => ({ id, list: res.data.results || res.data || [] }))
    ))
    const cars = {}
    results.forEach(({ id, list }) => { cars[id] = list })
    teacherCars.value = cars
  } catch (err) {
    console.error("Avtomobil ma'lumotlarini yuklashda xatolik:", err)
  } finally {
    loadingTeacherCars.value = false
  }
}

async function fetchReviews() {
  if (!student.value) return
  try {
    const res = await api.get('/teacher-reviews/', { params: { student: student.value.id, page_size: 100 } })
    reviews.value = res.data.results || res.data || []
  } catch (err) {
    console.error("Sharhlarni yuklashda xatolik:", err)
  }
}

const reviewModal = ref(null)
const reviewTarget = ref(null)
const reviewForm = ref({ rating: 5, comment: '' })
const reviewSaving = ref(false)
const reviewError = ref('')

function openReviewModal(teacherCard) {
  reviewTarget.value = teacherCard
  reviewForm.value = { rating: 5, comment: '' }
  reviewError.value = ''
  reviewModal.value?.showModal()
}

async function submitReview() {
  if (!reviewTarget.value?.info) return
  reviewSaving.value = true
  reviewError.value = ''
  try {
    await api.post('/teacher-reviews/', {
      teacher: reviewTarget.value.info.id,
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

const certModal = ref(null)
const selectedCertFile = ref(null)
const certNotes = ref('')
const certUploading = ref(false)
const certUploadError = ref('')

function openCertModal() {
  selectedCertFile.value = null
  certNotes.value = ''
  certUploadError.value = ''
  certModal.value?.showModal()
}

function onCertFileChange(e) {
  selectedCertFile.value = e.target.files?.[0] || null
}

async function fetchCertificates() {
  if (!student.value) return
  try {
    const res = await api.get('/student-certificates/', { params: { student: student.value.id, page_size: 100 } })
    certificates.value = res.data.results || res.data || []
  } catch (err) {
    console.error("Sertifikatlarni yuklashda xatolik:", err)
  }
}

async function uploadCertificate() {
  if (!selectedCertFile.value || !student.value) return
  certUploading.value = true
  certUploadError.value = ''
  try {
    const formData = new FormData()
    formData.append('student', student.value.id)
    formData.append('image', selectedCertFile.value)
    if (certNotes.value) formData.append('notes', certNotes.value)
    await api.post('/student-certificates/', formData)
    selectedCertFile.value = null
    certNotes.value = ''
    certModal.value?.close()
    await fetchCertificates()
  } catch (err) {
    console.error(err)
    certUploadError.value = err.response?.data?.detail || "Sertifikatni yuklashda xatolik yuz berdi."
  } finally {
    certUploading.value = false
  }
}

const bonusModal = ref(null)
const bonusTarget = ref(null)
const bonusForm = ref({ amountFormatted: '', amount: 0, method: 'cash' })
const bonusSaving = ref(false)
const bonusError = ref('')

function openBonusModal(cert) {
  bonusTarget.value = cert
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
    await api.post(`/payments/${bonusTarget.value.bonus_payment}/pay-bonus/`, {
      amount: bonusForm.value.amount,
      method: bonusForm.value.method,
    })
    bonusModal.value?.close()
    await fetchCertificates()
  } catch (err) {
    console.error(err)
    bonusError.value = err.response?.data?.detail || "Bonus to'lashda xatolik yuz berdi."
  } finally {
    bonusSaving.value = false
  }
}

function openImageModal(url) {
  if (!url) return
  zoomedImageUrl.value = url
  imageZoomModal.value?.showModal()
}

const editError    = ref('')
const editSaving   = ref(false)
const payError     = ref('')
const paySaving    = ref(false)
const lessonError  = ref('')
const lessonSuccess= ref('')
const lessonSaving = ref(false)

const instructorCar = ref(null)
const lessonForm    = ref({ car: '', notes: '' })

const editForm = ref({ full_name: '', phone: '', phone2: '', jshshr: '', passport_serie: '', passport_number: '', status: 'enrolled', notes: '', learning_time: '', learning_days: [] })
const weekdayOptions = [
  { value: 0, label: 'Dush' },
  { value: 1, label: 'Sesh' },
  { value: 2, label: 'Chor' },
  { value: 3, label: 'Pay' },
  { value: 4, label: 'Juma' },
  { value: 5, label: 'Shan' },
]
const payForm  = ref({ amountFormatted: '', amount: 0, method: 'cash', status: 'accepted', notes: '' })

const todayDateFormatted = computed(() => {
  const d = new Date()
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${day}.${month}.${year}`
})

const openLessonModal = async () => {
  lessonError.value = ''
  lessonSuccess.value = ''
  lessonForm.value = { car: '', notes: '' }
  instructorCar.value = null
  if (enrollment.value?.instructor) {
    try {
      const res = await api.get('/cars/', { params: { instructor: enrollment.value.instructor, page_size: 1 } })
      const list = res.data.results || res.data || []
      instructorCar.value = list[0] || null
      lessonForm.value.car = instructorCar.value?.id || ''
    } catch (err) {
      console.error("Instruktor avtomobilini yuklashda xatolik:", err)
    }
  }
  lessonModal.value?.showModal()
}

const submitLessonConfirmation = async () => {
  if (!enrollment.value?.instructor) {
    lessonError.value = "Ushbu o'quvchiga instruktor biriktirilmagan."
    return
  }
  if (!lessonForm.value.car) {
    lessonError.value = "Instruktorga avtomobil biriktirilmagan."
    return
  }
  lessonSaving.value = true
  lessonError.value = ''
  lessonSuccess.value = ''

  try {
    const nowISO = new Date().toISOString()
    const carName = instructorCar.value ? instructorCar.value.car_name : 'Avtomobil'

    // 1. Create DrivingLessons record
    await api.post('/driving-lessons/', {
      student: student.value.id,
      instructor: enrollment.value.instructor,
      car: lessonForm.value.car,
      lesson_date: nowISO,
      notes: lessonForm.value.notes || ''
    })

    // 2. Create Notification for admins
    await api.post('/notifications/', {
      title: `Yangi amaliy dars tasdiqlandi: ${student.value.full_name}`,
      note: `O'quvchi: ${student.value.full_name} | Instruktor: ${enrollment.value.instructor_name || '-'} | Avtomobil: ${carName} | Sana: ${todayDateFormatted.value}`,
      status: 'driving_lesson',
      target_id: student.value.id,
    })

    await fetchDrivingLessons()
    lessonSuccess.value = "Amaliy dars muvaffaqiyatli tasdiqlandi va adminlarga bildirishnoma yuborildi!"
    setTimeout(() => {
      lessonModal.value?.close()
    }, 1500)
  } catch (err) {
    console.error("Darsni tasdiqlashda xatolik:", err)
    lessonError.value = err.response?.data?.detail || "Darsni tasdiqlashda xatolik yuz berdi."
  } finally {
    lessonSaving.value = false
  }
}

function openPassportPreview() {
  if (student.value?.pass_img) {
    openImageModal(student.value.pass_img)
  }
}

const initials = computed(() => {
  const name = student.value?.full_name || ''
  const parts = name.trim().split(' ')
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  if (parts[0]) return parts[0][0].toUpperCase()
  return '?'
})

const activeStatus = computed(() => {
  return enrollment.value?.status || student.value?.status || 'new'
})

const acceptedAmount = computed(() =>
  payments.value.filter(p => p.is_active && p.status === 'accepted').reduce((s, p) => s + (p.amount || 0), 0)
)
const returnedAmount = computed(() =>
  payments.value.filter(p => p.is_active && p.status === 'returned').reduce((s, p) => s + (p.amount || 0), 0)
)
const netAcceptedAmount = computed(() =>
  acceptedAmount.value - returnedAmount.value
)
const paidTotal = computed(() =>
  Math.max(0, netAcceptedAmount.value)
)
const remaining = computed(() => {
  if (!enrollment.value || enrollment.value.enrolled_free) return 0
  return Math.max(0, (enrollment.value.enrolled_amount || 0) - paidTotal.value)
})
const isFullyPaid = computed(() => {
  if (!enrollment.value || enrollment.value.enrolled_free) return false
  const contract = Number(enrollment.value.enrolled_amount) || 0
  return contract > 0 && netAcceptedAmount.value >= contract
})
const progressPct = computed(() => {
  const amt = enrollment.value?.enrolled_amount
  if (!amt) return 0
  return Math.min(100, Math.round((paidTotal.value / amt) * 100))
})

const drivingLessons = ref([])
const loadingLessons = ref(false)

const fetchDrivingLessons = async () => {
  if (!student.value) return
  loadingLessons.value = true
  try {
    const studentId = Number(student.value.id)
    const res = await api.get('/driving-lessons/', { params: { student: studentId, page_size: 100 } })
    const list = Array.isArray(res.data) ? res.data : (res.data.results || [])
    drivingLessons.value = list
  } catch (err) {
    console.error("Amaliy darslarni yuklashda xatolik:", err)
  } finally {
    loadingLessons.value = false
  }
}

const fetchAll = async () => {
  loading.value = true; error.value = ''
  try {
    const id = route.params.id
    const [sRes, eRes] = await Promise.all([
      api.get(`/students/${id}/`),
      api.get('/enrollments/', { params: { student: id } }),
    ])
    student.value = sRes.data
    const list = Array.isArray(eRes.data) ? eRes.data : (eRes.data.results || [])
    enrollment.value = list.find(e => e.is_active) || list[0] || null
    if (enrollment.value?.group) {
      const gRes = await api.get(`/groups/${enrollment.value.group}/`)
      group.value = gRes.data
    } else {
      group.value = null
    }
    await Promise.all([
      fetchPayments(),
      fetchDrivingLessons(),
      fetchTeacherInfo(),
      fetchReviews(),
      fetchCertificates(),
    ])
    // Depend on teacherCards, which is only populated once fetchTeacherInfo above resolves.
    await Promise.all([fetchTeacherRatings(), fetchTeacherCars()])
  } catch (err) {
    console.error(err); error.value = "Ma'lumotlarni yuklashda xatolik yuz berdi."
  } finally { loading.value = false }
}

const fetchPayments = async () => {
  if (!student.value) return
  loadingPayments.value = true
  try {
    const studentId = Number(student.value.id)
    const currentEnrollmentId = enrollment.value?.id

    const res = await api.get('/payments/', { params: { student: studentId, page_size: 100 } })
    const list = Array.isArray(res.data) ? res.data : (res.data.results || [])
    
    payments.value = list.filter(p => {
      if (p.status === 'bonus') return false
      if (currentEnrollmentId && (p.enrollment === currentEnrollmentId || p.enrollment_id === currentEnrollmentId)) return true
      if (p.student === studentId || p.student_id === studentId) return true
      return true
    }).sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  } catch (err) { console.error(err) }
  finally { loadingPayments.value = false }
}

const selectedStudentPhoto = ref(null)
const selectedPassportPhoto = ref(null)

function onEditStudentPhotoChange(e) {
  selectedStudentPhoto.value = e.target.files?.[0] || null
}
function onEditPassportPhotoChange(e) {
  selectedPassportPhoto.value = e.target.files?.[0] || null
}

const openEditModal = () => {
  const s = student.value
  selectedStudentPhoto.value = null
  selectedPassportPhoto.value = null
  editForm.value = {
    full_name: s.full_name || '',
    phone: formatPhone(s.phone),
    phone2: s.phone2 || '',
    jshshr: s.jshshr ? String(s.jshshr) : '',
    passport_serie: s.passport_serie || '',
    passport_number: s.passport_number ? String(s.passport_number) : '',
    status: activeStatus.value,
    notes: s.notes || '',
    existingImage: s.image || null,
    existingPassImg: s.pass_img || null,
    learning_time: enrollment.value?.learning_time || '',
    learning_days: enrollment.value?.learning_days || [],
  }
  editError.value = ''
  editModal.value?.showModal()
}

const maskPhone = (val) => {
  let d = val.replace(/\D/g, '')
  if (!d.startsWith('998')) d = d.length === 0 ? '998' : '998' + d
  d = d.slice(0, 12)
  let f = '+' + d.slice(0, 3)
  if (d.length > 3) f += ' ' + d.slice(3, 5)
  if (d.length > 5) f += ' ' + d.slice(5, 8)
  if (d.length > 8) f += ' ' + d.slice(8, 10)
  if (d.length > 10) f += ' ' + d.slice(10, 12)
  return f
}
const onEditPhoneInput = (e) => { editForm.value.phone = maskPhone(e.target.value) }

// phone2 is intentionally free-form (e.g. "+998 90 900 90 90 uncle") — no
// auto-reformatting, unlike the primary `phone` field.

const saveStudent = async () => {
  editError.value = ''
  const f = editForm.value
  const phoneCleaned = f.phone.replace(/\D/g, '')
  if (!f.full_name.trim())      { editError.value = "Ism kiritilishi shart."; return }
  if (phoneCleaned.length < 12) { editError.value = "Telefon raqami noto'g'ri."; return }
  editSaving.value = true
  try {
    const payload = {
      full_name: f.full_name.trim(),
      phone: phoneCleaned,
      phone2: f.phone2 ? f.phone2.trim() : null,
      jshshr: f.jshshr ? parseInt(f.jshshr, 10) : null,
      passport_serie: f.passport_serie ? f.passport_serie.trim().toUpperCase() : null,
      passport_number: f.passport_number ? parseInt(f.passport_number, 10) : null,
      status: f.status,
      notes: f.notes || '',
      learning_time: f.learning_time || '',
      learning_days: f.learning_days || [],
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
      await api.patch(`/students/${student.value.id}/`, formData)
    } else {
      await api.patch(`/students/${student.value.id}/`, payload)
    }

    editModal.value?.close()
    await fetchAll()
  } catch (err) {
    console.error(err)
    if (err.response?.data) {
      const data = err.response.data
      if (typeof data === 'object') {
        const msgs = Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
        editError.value = msgs.join(' | ')
      } else {
        editError.value = String(data)
      }
    } else {
      editError.value = "Saqlashda xatolik yuz berdi."
    }
  } finally {
    editSaving.value = false
  }
}

const openPaymentModal = () => {
  payForm.value = { amountFormatted: '', amount: 0, method: 'cash', status: 'accepted', notes: '' }
  payError.value = ''; paymentModal.value?.showModal()
}

const onPayAmountInput = (e) => {
  const digits = e.target.value.replace(/\D/g, '')
  payForm.value.amount = digits ? parseInt(digits, 10) : 0
  payForm.value.amountFormatted = digits ? Number(digits).toLocaleString('uz-UZ').replace(/,/g, ' ') : ''
}

const savePayment = async () => {
  payError.value = ''
  if (!payForm.value.amount || payForm.value.amount <= 0) { payError.value = "Summa kiritilishi shart."; return }
  if (!enrollment.value) { payError.value = "O'quvchining aktiv qabuli mavjud emas."; return }
  paySaving.value = true
  try {
    await api.post('/payments/', {
      enrollment: enrollment.value.id, user: authStore.user?.id,
      amount: payForm.value.amount, method: payForm.value.method,
      status: payForm.value.status, notes: payForm.value.notes || null,
    })
    paymentModal.value?.close(); await fetchPayments()
  } catch (err) { console.error(err); payError.value = "To'lovni saqlashda xatolik yuz berdi." }
  finally { paySaving.value = false }
}

// Phone numbers may carry free-form trailing text (e.g. "+998 90 900 90 90
// uncle" for a relative's contact) — that text is preserved as-is, only the
// leading phone-looking portion gets formatted.
const formatPhone = (p) => {
  if (!p) return ''
  const str = String(p).trim()
  const match = str.match(/^(\+?[\d\s()-]+)(.*)$/)
  const phonePart = match ? match[1] : str
  const textPart = match ? match[2].trim() : ''
  const d = phonePart.replace(/\D/g, '')
  let formatted
  if (d.length === 12) {
    formatted = `+${d.slice(0,3)} ${d.slice(3,5)} ${d.slice(5,8)} ${d.slice(8,10)} ${d.slice(10,12)}`
  } else {
    formatted = phonePart.trim() || str
  }
  return textPart ? `${formatted} ${textPart}` : formatted
}
const formatDate = (d) => {
  if (!d) return '-'; const dt = new Date(d); if (isNaN(dt)) return d
  return `${String(dt.getDate()).padStart(2,'0')}.${String(dt.getMonth()+1).padStart(2,'0')}.${dt.getFullYear()}`
}
const formatDateTime = (d) => {
  if (!d) return '-'; const dt = new Date(d); if (isNaN(dt)) return d
  return `${String(dt.getDate()).padStart(2,'0')}.${String(dt.getMonth()+1).padStart(2,'0')}.${dt.getFullYear()} ${String(dt.getHours()).padStart(2,'0')}:${String(dt.getMinutes()).padStart(2,'0')}`
}
const formatMoney = (n) => {
  if (n == null) return "0 so'm"
  return Number(n).toLocaleString('uz-UZ').replace(/,/g, ' ') + " so'm"
}
const weekdayShortNames = ['Dush', 'Sesh', 'Chor', 'Pay', 'Juma', 'Shan']
const formatLearningDays = (d) => {
  if (Array.isArray(d)) {
    if (d.length === 0) return '-'
    if (d.length === 6) return 'Har kuni'
    return [...d].sort((a, b) => a - b).map(v => weekdayShortNames[v] || v).join(' – ')
  }
  if (d === 'Mo-Wed-Fri') return 'Dush – Chor – Juma'
  if (d === 'Tue-Thu-Sat') return 'Sesh – Pay – Shan'
  if (d === 'everyday') return "Har kuni"
  return d || '-'
}
const statusText  = (s) => ({ new: 'Yangi', enrolled: 'Faol', finished: 'Tugatgan', canceled: 'Bekor qilingan' }[s] || s || '-')
const statusClass = (s) => ({ new: 'badge-new', enrolled: 'badge-enrolled', finished: 'badge-canceled', canceled: 'badge-canceled' }[s] || '')
const groupStatusText  = (s) => ({ started: 'Boshlangan', finished: 'Tugatgan', canceled: 'Bekor qilingan' }[s] || s || '-')
const groupStatusClass = (s) => ({ started: 'badge-enrolled', finished: 'badge-done', canceled: 'badge-canceled' }[s] || '')
const payStatusText  = (s) => ({ accepted: 'Qabul qilingan', paid: "To'langan", returned: 'Qaytarilgan', bonus: 'Bonus', bank: 'Bank' }[s] || s || '-')
const payStatusClass = (s) => ({ accepted: 'pstatus-accepted', paid: 'pstatus-paid', returned: 'pstatus-returned', bonus: 'pstatus-bonus', bank: 'pstatus-bank' }[s] || '')
const methodText = (m) => ({ cash: 'Naqd', card: 'Karta', qr_code: 'QR code', transfer: "O'tkazma" }[m] || m || '-')

onMounted(async () => {
  if (!authStore.user) await authStore.fetchCurrentUser()
  await fetchAll()

  // Setup light dismiss for dialogs
  const dialogs = [editModal.value, paymentModal.value, reviewModal.value, bonusModal.value]
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
        if (!isInside) dialog.close()
      })
    }
  })
})
</script>

<style scoped>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
button{cursor:pointer;background:none;border:none;font-family:inherit}

.btn-back{display:inline-flex;align-items:center;gap:6px;padding:8px 14px;border-radius:8px;font-size:13.5px;font-weight:500;color:#374151;background:white;border:1px solid #E5E7EB;transition:background 0.15s,border-color 0.15s}
.btn-back:hover{background:#F9FAFB;border-color:#D1D5DB}

.detail-header{display:flex;align-items:center;gap:16px;margin-bottom:24px;flex-wrap:wrap}
.header-info{display:flex;align-items:center;gap:16px;flex:1}
.header-avatar{width:72px;height:72px;border-radius:50%;background:#F3F4F6;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:0 4px 14px rgba(0,0,0,0.08);border:2.5px solid #E5E7EB;overflow:hidden;cursor:pointer;transition:transform 0.15s ease}
.header-avatar:hover{transform:scale(1.04);border-color:#2D6A4F}
.user-avatar-img{width:100%;height:100%;object-fit:cover;border-radius:50%}

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
.header-name{font-size:20px;font-weight:700;color:#111827;line-height:1.2}
.header-meta{display:flex;align-items:center;gap:8px;margin-top:4px;flex-wrap:wrap}
.meta-sep{color:#D1D5DB;font-size:12px}
.meta-phone{font-size:13px;color:#6B7280;font-weight:500}
.meta-cat{font-size:13px;color:#374151;font-weight:600}
.header-actions{display:flex;gap:10px;flex-shrink:0}

.btn-edit-main{display:inline-flex;align-items:center;gap:6px;padding:10px 16px;border-radius:8px;font-size:13.5px;font-weight:600;color:#374151;background:white;border:1px solid #E5E7EB;transition:background 0.15s,border-color 0.15s}
.btn-edit-main:hover{background:#F9FAFB;border-color:#D1D5DB}
.btn-payment{display:inline-flex;align-items:center;gap:6px;padding:10px 18px;border-radius:8px;font-size:13.5px;font-weight:600;color:white;background:#2D6A4F;transition:background 0.15s;box-shadow:0 2px 8px rgba(45,106,79,0.25)}
.btn-payment:hover{background:#1B4332}

.btn-save{display:inline-flex;align-items:center;gap:6px;padding:10px 22px;border-radius:8px;font-size:13.5px;font-weight:600;color:white;background:#2D6A4F;transition:background 0.15s;box-shadow:0 2px 6px rgba(45,106,79,0.25)}
.btn-save:hover{background:#1B4332}

.btn-confirm-lesson { display: inline-flex; align-items: center; gap: 8px; padding: 10px 18px; border-radius: 10px; font-size: 13.5px; font-weight: 600; color: white; background: linear-gradient(135deg, #10B981, #059669); border: none; cursor: pointer; transition: all 0.2s ease; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25); }
.btn-confirm-lesson:hover { transform: translateY(-1px); box-shadow: 0 6px 16px rgba(16, 185, 129, 0.35); }

.disabled-input { background: #E2E8F0 !important; color: #475569 !important; font-weight: 600; cursor: not-allowed; }
.alert-success-box { margin: 12px 24px 0; padding: 12px 16px; background: #DCFCE7; border-left: 4px solid #10B981; color: #15803D; font-size: 13px; font-weight: 600; border-radius: 8px; }
.btn-green { background: #10B981 !important; box-shadow: 0 2px 6px rgba(16, 185, 129, 0.3) !important; }
.btn-green:hover { background: #059669 !important; }

.margin-top-card { margin-top: 20px; }
.card-icon-purple { background: #F3E8FF; color: #7E22CE; }
.instructor-chip { font-size: 12px; color: #4338CA; background: #EEF2FF; padding: 2px 8px; border-radius: 6px; }
.car-chip { font-size: 12px; color: #065F46; background: #ECFDF5; padding: 2px 8px; border-radius: 6px; }
.btn-add-lesson { background: #16A34A !important; color: #fff !important; box-shadow: 0 2px 6px rgba(22, 163, 74, 0.25) !important; }
.btn-add-lesson:hover { background: #15803D !important; }

.state-box{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;padding:60px 20px;color:#6B7280;font-size:14px}
.state-error{color:#EF4444}
.btn-retry{padding:8px 16px;border-radius:8px;background:#EF4444;color:white;font-size:13.5px;font-weight:600;cursor:pointer}

.content-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start}
@media(max-width:900px){.content-grid{grid-template-columns:1fr}}
.col-left,.col-right{display:flex;flex-direction:column;gap:20px}

.detail-card{background:white;border-radius:14px;border:1px solid #E5E7EB;box-shadow:0 1px 4px rgba(0,0,0,0.05);overflow:hidden}
.card-header{display:flex;align-items:center;gap:10px;padding:16px 20px 14px;border-bottom:1px solid #F3F4F6}
.card-icon{width:30px;height:30px;border-radius:8px;background:#ECFDF5;color:#2D6A4F;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.card-icon-blue{background:#EFF6FF;color:#3B82F6}
.card-icon-green{background:#ECFDF5;color:#2D6A4F}
.card-icon-purple{background:#F5F3FF;color:#7C3AED}
.card-icon-orange{background:#FFF7ED;color:#EA580C}
.card-title{font-size:14px;font-weight:700;color:#111827;flex:1}
.btn-add-payment{display:inline-flex;align-items:center;gap:4px;padding:5px 12px;border-radius:6px;font-size:12.5px;font-weight:600;color:#2D6A4F;background:#ECFDF5;border:1px solid #A7F3D0;transition:background 0.15s}
.btn-add-payment:hover{background:#D1FAE5}

.info-grid{padding:4px 0 8px}
.info-row{display:flex;align-items:flex-start;gap:12px;padding:10px 20px;border-bottom:1px solid #F9FAFB}
.info-row:last-child{border-bottom:none}
.info-label{font-size:12.5px;font-weight:600;color:#6B7280;width:150px;flex-shrink:0;padding-top:1px}
.info-value{font-size:13.5px;color:#1F2937;flex:1;line-height:1.5}
.info-value.fw{font-weight:600}
.info-value.mono{font-family:monospace}

.status-badge{display:inline-block;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600;letter-spacing:.02em}
.badge-new{background:#F3F4F6;color:#4B5563}
.badge-enrolled{background:#D1FAE5;color:#065F46}
.badge-done{background:#E0E7FF;color:#3730A3}
.badge-canceled{background:#FEE2E2;color:#991B1B}
.badge-notstarted{background:#F3F4F6;color:#6B7280}
.badge-free{background:#D1FAE5;color:#065F46;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600}
.cat-badge{display:inline-block;padding:3px 10px;background:#1B2430;color:white;border-radius:20px;font-size:12px;font-weight:700;letter-spacing:.04em}

.payment-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:#F3F4F6;border-bottom:1px solid #F3F4F6}
.pay-stat{background:white;padding:16px 18px;text-align:center}
.pay-stat-label{font-size:11.5px;color:#9CA3AF;font-weight:600;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px}
.pay-stat-value{font-size:16px;font-weight:700;color:#111827}
.pay-stat-value.green{color:#2D6A4F}
.pay-stat-value.red{color:#EF4444}
.progress-wrap{display:flex;align-items:center;gap:10px;padding:14px 20px}
.progress-bar{flex:1;height:8px;background:#F3F4F6;border-radius:99px;overflow:hidden}
.progress-fill{height:100%;background:linear-gradient(90deg,#52B788,#2D6A4F);border-radius:99px;transition:width 0.5s ease}
.progress-label{font-size:12px;font-weight:700;color:#2D6A4F;width:36px;text-align:right}

.mini-state{display:flex;align-items:center;justify-content:center;gap:10px;padding:32px;color:#9CA3AF;font-size:13.5px;flex-direction:column}
.pay-table-wrap{overflow-x:auto}
.pay-table{width:100%;border-collapse:collapse;font-size:13px}
.pay-table th{padding:10px 16px;background:#F9FAFB;color:#6B7280;font-weight:600;font-size:12px;text-align:left;border-bottom:1px solid #E5E7EB;white-space:nowrap}
.pay-table td{padding:11px 16px;border-bottom:1px solid #F3F4F6;color:#1F2937;vertical-align:middle}
.pay-row:last-child td{border-bottom:none}
.pay-row:hover td{background:#FAFAFA}
.td-date{color:#6B7280;font-size:12.5px;white-space:nowrap}
.td-amount{font-weight:700;color:#2D6A4F;white-space:nowrap}
.td-notes{color:#6B7280;font-size:12.5px;max-width:120px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.method-badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11.5px;font-weight:600;background:#F3F4F6;color:#374151}
.pay-status-badge{display:inline-block;padding:2px 8px;border-radius:20px;font-size:11.5px;font-weight:600}
.pstatus-accepted{background:#D1FAE5;color:#065F46}
.pstatus-paid{background:#DBEAFE;color:#1D4ED8}
.pstatus-returned{background:#FEE2E2;color:#991B1B}
.pstatus-bonus{background:#FEF9C3;color:#92400E}
.pstatus-bank{background:#F5F3FF;color:#5B21B6}

.spinner{width:32px;height:32px;border:3px solid #E5E7EB;border-top-color:#2D6A4F;border-radius:50%;animation:spin 0.7s linear infinite}
.spinner-sm{width:16px;height:16px;border-width:2px}
@keyframes spin{to{transform:rotate(360deg)}}

/* ── Perfectly Centered Dialogs ── */
.modal-dialog{
  border:none;
  border-radius:16px;
  padding:0;
  width:90%;
  max-width:640px;
  box-shadow:0 20px 60px rgba(0,0,0,0.22);
  overflow:hidden;
  position:fixed;
  top:50%;
  left:50%;
  transform:translate(-50%, -50%);
  margin:0;
}
.modal-dialog.modal-sm{max-width:480px}
.modal-dialog::backdrop{background:rgba(17,24,39,0.5);backdrop-filter:blur(3px)}
.modal-form{display:flex;flex-direction:column}
.modal-head{display:flex;align-items:center;justify-content:space-between;padding:20px 24px 16px;border-bottom:1px solid #F3F4F6}
.modal-title{font-size:17px;font-weight:700;color:#111827}
.btn-close{width:30px;height:30px;border-radius:50%;background:#F3F4F6;color:#6B7280;font-size:13px;display:flex;align-items:center;justify-content:center;transition:background 0.15s}
.btn-close:hover{background:#E5E7EB}
.modal-error{margin:12px 24px 0;padding:10px 14px;background:#FEE2E2;border-radius:8px;color:#991B1B;font-size:13px;font-weight:500}
.form-section{padding:18px 24px 4px}
.section-tag{font-size:11px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:#2D6A4F;display:flex;align-items:center;gap:8px;margin-bottom:14px}
.section-tag::after{content:'';flex:1;height:1px;background:#E5E7EB}
.form-grid-2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.form-group{display:flex;flex-direction:column;gap:6px}
.form-section>.form-group+.form-group{margin-top:14px}
.fg-full{grid-column:span 2}
.form-label{font-size:12.5px;font-weight:600;color:#374151}
.req{color:#EF4444}
.form-input{width:100%;padding:9px 12px;font-size:13.5px;border:1.5px solid #D1D5DB;border-radius:10px;outline:none;background:#F9FAFB;color:#111827;font-family:inherit;transition:border-color 0.2s,background 0.2s,box-shadow 0.2s}
.form-input:focus{border-color:#2D6A4F;background:white;box-shadow:0 0 0 3px rgba(45,106,79,0.1)}
.form-input.mono{font-family:monospace}
.form-input.text-upper{text-transform:uppercase}
.form-select{appearance:none;-webkit-appearance:none;padding-right:32px}
.select-wrap{position:relative}
.sel-arrow{position:absolute;right:10px;top:50%;transform:translateY(-50%);pointer-events:none;color:#6B7280}
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
textarea.form-input{resize:vertical;min-height:80px}
.modal-actions{display:flex;justify-content:flex-end;gap:10px;padding:16px 24px 20px;border-top:1px solid #F3F4F6;margin-top:8px}
.btn-cancel{padding:10px 18px;border-radius:8px;font-size:13.5px;font-weight:600;color:#374151;background:#F9FAFB;border:1px solid #E5E7EB;transition:background 0.15s}
.btn-cancel:hover{background:#F3F4F6}
.btn-save{display:inline-flex;align-items:center;gap:6px;padding:10px 22px;border-radius:8px;font-size:13.5px;font-weight:600;color:white;background:#2D6A4F;transition:background 0.15s;box-shadow:0 2px 6px rgba(45,106,79,0.25)}
.btn-save:hover:not(:disabled){background:#1B4332}
.btn-save:disabled{opacity:.6;cursor:not-allowed}
.btn-spinner{display:inline-block;width:13px;height:13px;border:2px solid rgba(255,255,255,0.4);border-top-color:white;border-radius:50%;animation:spin 0.7s linear infinite}
.pay-remaining-hint{padding:10px 14px;background:#ECFDF5;border-radius:8px;color:#065F46;font-size:13px;font-weight:500;margin-bottom:14px}
.btn-view-pass {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: #E0E7FF;
  color: #3730A3;
  border: 1px solid #C7D2FE;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-view-pass:hover {
  background: #C7D2FE;
}
.btn-view-pass-header {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 16px;
  background: #059669;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-view-pass-header:hover {
  background: #047857;
}
.avatar-placeholder-box {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 20px;
  color: white;
}

/* ── Teachers & Reviews ─────────────────────────────── */
.teacher-cards-wrap { display: flex; flex-direction: column; gap: 12px; }
.teacher-mini-card { display: flex; align-items: center; gap: 12px; padding: 12px; border: 1px solid #F3F4F6; border-radius: 10px; }
.teacher-mini-card.clickable { cursor: pointer; transition: background 0.15s, border-color 0.15s; }
.teacher-mini-card.clickable:hover { background: #F9FAFB; border-color: #E5E7EB; }
.teacher-mini-avatar { width: 44px; height: 44px; border-radius: 50%; object-fit: cover; border: 1px solid #E5E7EB; flex-shrink: 0; }
.teacher-mini-info { flex: 1; min-width: 0; }
.teacher-mini-name { font-size: 13.5px; font-weight: 700; color: #111827; }
.teacher-mini-role { font-size: 11.5px; color: #2563EB; font-weight: 600; margin-top: 1px; }
.teacher-mini-phone { font-size: 12px; color: #6B7280; margin-top: 1px; }
.btn-leave-review { padding: 7px 12px; background: #FEF3C7; color: #92400E; border: none; border-radius: 8px; font-size: 12px; font-weight: 700; cursor: pointer; white-space: nowrap; }
.btn-leave-review:hover { background: #FDE68A; }
.teacher-mini-rating { font-size: 11.5px; color: #92400E; font-weight: 700; margin-top: 3px; }
.teacher-mini-rating .rating-count { color: #9CA3AF; font-weight: 500; }

.teacher-tabs { display: flex; gap: 8px; margin-bottom: 14px; margin-left: 12px; margin-top: 14px;}
.teacher-tab-btn { padding: 6px 14px; border-radius: 20px; font-size: 12.5px; font-weight: 600; border: 1px solid #E5E7EB; background: #F9FAFB; color: #4B5563; cursor: pointer; transition: all 0.15s ease; }
.teacher-tab-btn:hover { background: #F3F4F6; }
.teacher-tab-btn.active { background: #2D6A4F; color: white; border-color: #2D6A4F; }

.teacher-cars-wrap { display: flex; flex-direction: column; gap: 16px; }
.teacher-cars-group + .teacher-cars-group { padding-top: 14px; border-top: 1px solid #F3F4F6; }
.teacher-cars-owner { font-size: 12.5px; font-weight: 700; color: #374151; margin-bottom: 8px; }
.cars-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; }
.car-mini-card { border: 1px solid #F3F4F6; border-radius: 10px; overflow: hidden; cursor: pointer; transition: border-color 0.15s, box-shadow 0.15s; }
.car-mini-card:hover { border-color: #E5E7EB; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.car-mini-image { width: 100%; height: 90px; object-fit: cover; display: block; }
.car-mini-info { padding: 8px 10px; }
.car-mini-name { font-size: 12.5px; font-weight: 700; color: #111827; }
.car-mini-sub { font-size: 11px; color: #6B7280; margin-top: 2px; display: flex; align-items: center; gap: 4px; }
.car-status-chip { font-size: 10.5px; font-weight: 700; padding: 1px 7px; border-radius: 10px; }
.car-status-chip.available { background: #DCFCE7; color: #15803D; }
.car-status-chip.repairing { background: #FEF3C7; color: #92400E; }
.car-status-chip.not_available { background: #FEE2E2; color: #991B1B; }

.reviews-list { margin-top: 16px; padding-top: 14px; border-top: 1px solid #F3F4F6; display: flex; flex-direction: column; gap: 10px; }
.reviews-list-title { font-size: 12.5px; font-weight: 700; color: #374151; }
.review-item { background: #F9FAFB; border-radius: 8px; padding: 10px 12px; }
.review-item-top { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.review-stars { color: #D97706; font-size: 13px; letter-spacing: 1px; }
.review-teacher { font-size: 12.5px; font-weight: 600; color: #111827; }
.review-date { font-size: 11px; color: #9CA3AF; margin-left: auto; }
.review-comment { font-size: 12.5px; color: #4B5563; margin-top: 4px; }

.star-picker { display: flex; gap: 4px; }
.star { font-size: 26px; color: #D1D5DB; cursor: pointer; user-select: none; transition: color 0.1s; }
.star.filled { color: #D97706; }

/* ── Certificates ───────────────────────────────────── */
.cert-upload-row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-bottom: 12px; }
.cert-upload-row .form-input { flex: 1; min-width: 160px; }
.btn-upload-cert { padding: 10px 16px; background: #2D6A4F; color: white; border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; white-space: nowrap; }
.btn-upload-cert:hover:not(:disabled) { background: #1B4332; }
.btn-upload-cert:disabled { opacity: 0.6; cursor: not-allowed; }

.empty-certs { text-align: center; padding: 16px 0; color: #9CA3AF; font-size: 12.5px; }
.certs-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 14px; }
.cert-card { border: 1px solid #F3F4F6; border-radius: 10px; overflow: hidden; }
.cert-image { width: 100%; height: 110px; object-fit: cover; cursor: pointer; display: block; }
.cert-meta { padding: 8px 10px; }
.cert-uploader { font-size: 12px; font-weight: 700; color: #111827; }
.cert-date { font-size: 11px; color: #9CA3AF; margin-top: 1px; }
.cert-notes { font-size: 11.5px; color: #6B7280; margin-top: 4px; }
.cert-bonus-row { padding: 0 10px 10px; }
.bonus-paid-badge { display: inline-block; font-size: 11px; font-weight: 700; color: #15803D; background: #DCFCE7; padding: 3px 8px; border-radius: 8px; }
.btn-pay-cert-bonus { width: 100%; padding: 7px 10px; background: #FEF3C7; color: #92400E; border: none; border-radius: 8px; font-size: 11.5px; font-weight: 700; cursor: pointer; }
.btn-pay-cert-bonus:hover { background: #FDE68A; }
</style>
