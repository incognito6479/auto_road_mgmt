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

        <div v-else class="reviews-accordion">
          <div v-for="r in reviews" :key="r.id" class="review-row">
            <div class="review-row-top">
              <span class="review-row-student">{{ r.student_name }}</span>
              <span class="review-row-stars">{{ '★'.repeat(r.rating) }}{{ '☆'.repeat(5 - r.rating) }}</span>
              <span class="review-row-date">{{ formatDate(r.created_at) }}</span>
            </div>
            <p v-if="r.comment" class="review-row-comment">{{ r.comment }}</p>
          </div>
        </div>
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

          <div v-if="pastAssignedCars.length > 0" class="table-wrap" style="margin-top: 14px;">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Avtomobil</th>
                  <th>Biriktirilgan sana</th>
                  <th>Ajratilgan sana</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="h in pastAssignedCars" :key="h.id">
                  <td class="link-value" @click="router.push(`/vehicles/${h.car.id}`)">{{ h.car.car_name }}</td>
                  <td>{{ formatDate(h.assigned_at) }}</td>
                  <td>{{ formatDate(h.unassigned_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </div>

      <!-- Certificates Section — students only get the review flow here -->
      <div class="linked-section" v-if="user.role === 'instructor' && !authStore.isStudent">
        <div class="section-header">
          <h3 class="section-title">Yuklangan Sertifikatlar (so'nggi 5 ta)</h3>
          <span class="count-badge">{{ certificates.length }} ta sertifikat</span>
        </div>

        <div v-if="loadingCertificates" class="state-container">
          <div class="spinner"></div>
        </div>

        <div v-else-if="certificates.length === 0" class="empty-groups">
          <p class="empty-title">Hozircha sertifikat yo'q</p>
          <p class="empty-sub">Ushbu instruktor uchun hali sertifikat yuklanmagan.</p>
        </div>

        <div v-else class="certs-grid-user">
          <div v-for="c in recentCertificates" :key="c.id" class="cert-card-user">
            <img :src="c.image" alt="Sertifikat" class="cert-image-user" @click="openImageModal(c.image)" />
            <div class="cert-meta-user">
              <div class="cert-student-name">{{ c.student_name || '-' }}</div>
              <div class="cert-date-user">{{ formatDate(c.created_at) }}</div>
              <p v-if="c.notes" class="cert-notes-user">{{ c.notes }}</p>
            </div>
            <div v-if="canPayBonus" class="cert-bonus-row-user">
              <span v-if="c.bonus_paid" class="bonus-paid-badge-user">✓ To'landi ({{ formatMoney(c.bonus_amount) }})</span>
              <button v-else type="button" class="btn-pay-cert-bonus-user" @click="openBonusModal(c)">Bonus to'lash</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Payments Section — staff-only, never shown to students -->
      <div class="linked-section" v-if="canSeePayments">
        <div class="section-header">
          <h3 class="section-title">To'lovlar Tarixi (so'nggi 5 ta)</h3>
          <span class="count-badge">Jami: {{ formatMoney(totalPaidToUser) }}</span>
        </div>

        <div v-if="loadingPayments" class="state-container">
          <div class="spinner"></div>
        </div>

        <div v-else-if="userPayments.length === 0" class="empty-groups">
          <p class="empty-title">Hozircha to'lov yo'q</p>
          <p class="empty-sub">Ushbu foydalanuvchiga hali to'lov qilinmagan.</p>
        </div>

        <div v-else class="payments-table-wrap">
          <table class="payments-table">
            <thead>
              <tr>
                <th>Sana &amp; Vaqt</th>
                <th>Turi</th>
                <th>Summa</th>
                <th>Usuli</th>
                <th>Izoh</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in recentPayments" :key="p.id">
                <td class="pay-date">{{ formatDateTime(p.created_at) }}</td>
                <td><span class="pay-status-chip" :class="p.status">{{ paymentStatusText(p.status) }}</span></td>
                <td class="pay-amount">{{ formatMoney(p.amount) }}</td>
                <td class="pay-method">{{ methodText(p.method) }}</td>
                <td class="pay-notes">{{ p.notes || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Linked Students Section — hidden from students -->
      <div class="linked-section" v-if="!authStore.isStudent">
        <div class="section-header">
          <h3 class="section-title">Biriktirilgan O'quvchilar</h3>
          <span class="count-badge">{{ filteredLinkedEnrollments.length }} ta o'quvchi</span>
        </div>

        <div class="students-filter-bar">
          <div class="search-box">
            <svg viewBox="0 0 20 20" fill="none" stroke="#9CA3AF" stroke-width="2" width="16" height="16">
              <circle cx="8.5" cy="8.5" r="5.5"/>
              <line x1="13" y1="13" x2="18" y2="18"/>
            </svg>
            <input
              v-model="studentTableSearch"
              type="text"
              placeholder="O'quvchi ismini kiriting..."
              class="search-input"
            />
          </div>

          <div class="filter-item">
            <label class="filter-label">Guruh:</label>
            <div class="select-wrap">
              <select v-model="studentTableGroupFilter" class="group-filter-select">
                <option value="">Barchasi</option>
                <option v-for="g in linkedGroupOptions" :key="g.id" :value="g.id">{{ g.name }}</option>
              </select>
            </div>
          </div>

          <div class="filter-item">
            <label class="filter-label">Kategoriya:</label>
            <div class="select-wrap">
              <select v-model="studentTableCategoryFilter" class="group-filter-select">
                <option value="">Barchasi</option>
                <option v-for="c in linkedCategoryOptions" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
          </div>

          <div class="filter-item">
            <label class="filter-label">Imtihondan o'tganligi haqida:</label>
            <div class="select-wrap">
              <select v-model="studentTableCertFilter" class="group-filter-select">
                <option value="">Barchasi</option>
                <option value="uploaded">Yuklangan</option>
                <option value="not_uploaded">Yuklanmagan</option>
              </select>
            </div>
          </div>
        </div>

        <div v-if="loadingEnrollments" class="state-container">
          <div class="spinner"></div>
        </div>

        <div v-else-if="filteredLinkedEnrollments.length === 0" class="empty-groups">
          <svg viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="1.5" width="40" height="40">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
          </svg>
          <p class="empty-title">O'quvchilar topilmadi</p>
          <p class="empty-sub">Ushbu xodimga hali birorta o'quvchi biriktirilmagan yoki filtrga mos o'quvchi yo'q.</p>
        </div>

        <div v-else class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>O'quvchi F.I.SH.</th>
                <th>Telefon</th>
                <th>Kategoriya</th>
                <th>Guruh</th>
                <th>Holati</th>
                <th>Dars Kunlari</th>
                <th>Dars Vaqti</th>
                <th>O'quv Joyi</th>
                <th>Agent</th>
                <th>Shartnoma</th>
                <th>To'langan</th>
                <th v-if="showCoordinatorColumn">O'qituvchi</th>
                <th v-if="showInstructorColumn">Instruktor</th>
                <th>Imtihondan o'tganligi haqida</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="e in filteredLinkedEnrollments" :key="e.id" class="table-row" @click="goStudent(e.student)" style="cursor: pointer;">
                <td class="td-name">
                  <div class="student-link">{{ e.student_name }}</div>
                  <div class="student-jshshr">JSHSHR: {{ e.student_jshshr || '-' }}</div>
                </td>
                <td class="td-phone">
                  <div>{{ formatPhone(e.student_phone) }}</div>
                  <div v-if="e.student_phone2" class="td-phone-sub">Qo'shimcha: {{ formatPhone(e.student_phone2) }}</div>
                </td>
                <td><span class="group-badge">{{ e.category_name || '-' }}</span></td>
                <td>
                  {{ e.group_name || '-' }}
                  <div v-if="groupsById[e.group]" class="group-dates">
                    {{ formatDate(groupsById[e.group].started_at) }} — {{ formatDate(groupsById[e.group].ends_at) }}
                  </div>
                </td>
                <td>
                  <span class="status-chip" :class="e.status">
                    {{ statusText(e.status) }}
                  </span>
                </td>
                <td>{{ formatLearningDays(e.learning_days) }}</td>
                <td>{{ e.learning_time || '-' }}</td>
                <td>{{ e.learning_place_name || '-' }}</td>
                <td>{{ e.agent_name || '-' }}</td>
                <td>
                  <span v-if="e.enrolled_free" class="free-chip">Tekin</span>
                  <span v-else>{{ formatMoney(e.enrolled_amount) }}</span>
                </td>
                <td class="text-green">{{ formatMoney(e.paid_amount || 0) }}</td>
                <td v-if="showCoordinatorColumn">{{ e.coordinator_name || '-' }}</td>
                <td v-if="showInstructorColumn">{{ e.instructor_name || '-' }}</td>
                <td @click.stop>
                  <span class="cert-status-chip" :class="studentHasCertificate(e.student) ? 'cert-yes' : 'cert-no'">
                    {{ studentHasCertificate(e.student) ? '✓ Yuklangan' : 'Yuklanmagan' }}
                  </span>
                  <button
                    v-if="!studentHasCertificate(e.student) && authStore.canUploadCertificates"
                    type="button"
                    class="btn-upload-cert"
                    @click="openCertUploadModal(e)"
                  >
                    + Yuklash
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- Edit User Modal -->
    <dialog ref="userModal" class="modal-dialog">
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
            <input v-model="editForm.phone2" type="text" class="form-input" placeholder="+998 90 900 90 90 otasi" />
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
            <input type="file" accept="image/*" class="form-input" style="width: 100%;" @change="onUserFileChange" />
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
    <dialog ref="bonusModal" class="modal-dialog modal-sm" closedby="any">
      <form class="user-modal-form" @submit.prevent="submitCertBonus">
        <div class="user-modal-header">
          <div class="header-badge-wrap">
            <div>
              <h3 class="user-modal-title">Instruktorga bonus to'lash</h3>
            </div>
          </div>
          <button type="button" class="user-btn-close" @click="bonusModal?.close()">✕</button>
        </div>
        <div v-if="bonusError" class="modal-alert modal-alert-error"><span>{{ bonusError }}</span></div>

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

        <div class="user-modal-footer">
          <button type="button" class="btn-cancel" @click="bonusModal?.close()">Bekor qilish</button>
          <button type="submit" class="btn-submit" :disabled="bonusSaving">
            {{ bonusSaving ? 'Saqlanmoqda...' : "To'lash" }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Certificate Upload Modal (for a specific linked student) -->
    <dialog ref="certUploadModal" class="modal-dialog modal-sm" closedby="any">
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
          <input type="file" accept="image/*" class="form-input" @change="onCertUploadFileChange" required />
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

// Instructors see their students' theory teacher; coordinators see the
// student's driving instructor; admin/superuser/mechanic see both.
const showCoordinatorColumn = computed(() => authStore.isInstructor || authStore.isAdminOrSuperuser || authStore.isMechanic)
const showInstructorColumn = computed(() => authStore.isCoordinator || authStore.isAdminOrSuperuser || authStore.isMechanic)

const reviews = ref([])
const loadingReviews = ref(false)

// ── Payments made to this teacher/instructor ──────────────────
// Students must never see staff payment figures, so the whole section is
// gated on the viewer not being a student.
const userPayments = ref([])
const loadingPayments = ref(false)
const canSeePayments = computed(() => !!(authStore.user && !authStore.isStudent))
const totalPaidToUser = computed(() =>
  userPayments.value.reduce((sum, p) => sum + (Number(p.amount) || 0), 0)
)
// The list itself is capped to the last 5 (newest first, per API ordering) —
// the count badge above still reflects the full total.
const recentPayments = computed(() => userPayments.value.slice(0, 5))

async function fetchUserPayments() {
  if (!user.value || !canSeePayments.value) return
  loadingPayments.value = true
  try {
    const res = await api.get('/payments/', { params: { user: user.value.id, page_size: 500 } })
    userPayments.value = res.data.results ? res.data.results : (res.data || [])
  } catch (err) {
    console.error("To'lovlarni yuklashda xatolik:", err)
  } finally {
    loadingPayments.value = false
  }
}

function paymentStatusText(st) {
  switch (st) {
    case 'accepted': return 'Qabul qilingan'
    case 'returned': return 'Qaytarilgan'
    case 'paid': return "To'langan"
    case 'bonus': return 'Bonus'
    case 'bank': return 'Bank'
    case 'bonus_teacher': return "O'qituvchi bonusi"
    default: return st
  }
}

function methodText(m) {
  switch (m) {
    case 'cash': return 'Naqd'
    case 'card': return 'Karta'
    case 'qr_code': return 'QR code'
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

// ── Certificates & bonus payment ──────────────────
const certificates = ref([])
const loadingCertificates = ref(false)
// The list itself is capped to the last 5 (newest first, per API ordering) —
// the count badge above still reflects the full total.
const recentCertificates = computed(() => certificates.value.slice(0, 5))

// Admin/superuser can pay a bonus, but never while viewing their own profile.
const canPayBonus = computed(() => !!(authStore.isAdminOrSuperuser && authStore.user && user.value && authStore.user.id !== user.value.id))

async function fetchCertificates() {
  if (!user.value) return
  loadingCertificates.value = true
  try {
    const res = await api.get('/student-certificates/', { params: { instructor: user.value.id, page_size: 200 } })
    certificates.value = res.data.results ? res.data.results : (res.data || [])
  } catch (err) {
    console.error("Sertifikatlarni yuklashda xatolik:", err)
  } finally {
    loadingCertificates.value = false
  }
}

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
const certUploadTarget = ref(null)
const certUploadFile = ref(null)
const certUploadNotes = ref('')
const certUploadSaving = ref(false)
const certUploadError = ref('')

function openCertUploadModal(enrollment) {
  certUploadTarget.value = enrollment
  certUploadFile.value = null
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
  notes: '',
  password: '',
  passwordConfirm: ''
})

// Formats the phone field as the user types into "+998 90 900 90 90".
// The raw digits are what actually get sent on save.
function onEditPhoneInput(e) {
  editForm.value.phone = formatPhoneInput(e.target.value)
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
const studentTableCertFilter = ref('')

// Distinct groups/categories among this staff member's linked students, for
// the filter dropdowns — no point offering options that would match nothing.
const linkedGroupOptions = computed(() => {
  const map = {}
  enrollments.value.forEach(e => {
    if (e.group && !map[e.group]) map[e.group] = { id: e.group, name: e.group_name || `Guruh #${e.group}` }
  })
  return Object.values(map).sort((a, b) => a.name.localeCompare(b.name))
})

const linkedCategoryOptions = computed(() => {
  const map = {}
  enrollments.value.forEach(e => {
    if (e.category && !map[e.category]) map[e.category] = { id: e.category, name: e.category_name || `#${e.category}` }
  })
  return Object.values(map).sort((a, b) => a.name.localeCompare(b.name))
})

// Whether at least one certificate has been uploaded for this student,
// regardless of which instructor/coordinator it's attributed to.
function studentHasCertificate(studentId) {
  return allStudentCerts.value.some(c => c.student === studentId)
}

const filteredLinkedEnrollments = computed(() => {
  const q = studentTableSearch.value.trim().toLowerCase()
  return enrollments.value.filter(e => {
    if (studentTableGroupFilter.value && e.group !== studentTableGroupFilter.value) return false
    if (studentTableCategoryFilter.value && e.category !== studentTableCategoryFilter.value) return false
    if (studentTableCertFilter.value) {
      const hasCert = studentHasCertificate(e.student)
      if (studentTableCertFilter.value === 'uploaded' && !hasCert) return false
      if (studentTableCertFilter.value === 'not_uploaded' && hasCert) return false
    }
    if (!q) return true
    return (e.student_name || '').toLowerCase().includes(q) || (e.student_phone || '').includes(q)
  })
})

async function fetchUserDetail() {
  loading.value = true
  error.value = null
  try {
    const res = await api.get(`/users/${route.params.id}/`)
    user.value = res.data
    fetchLinkedEnrollments()
    fetchReviews()
    fetchCertificates()
    fetchAllStudentCerts()
    fetchUserPayments()
    fetchGroupsForSchedule()
    fetchInstructorCars()
  } catch (err) {
    error.value = "Foydalanuvchi ma'lumotlarini yuklashda xatolik"
  } finally {
    loading.value = false
  }
}

async function fetchLinkedEnrollments() {
  if (!user.value) return
  loadingEnrollments.value = true
  try {
    // Check role to query either instructor or coordinator
    const paramKey = user.value.role === 'instructor' ? 'instructor' : 'coordinator'
    const res = await api.get('/enrollments/', {
      params: { [paramKey]: user.value.id, page_size: 200 }
    })
    enrollments.value = res.data.results ? res.data.results : res.data
  } catch (err) {
    console.error(err)
  } finally {
    loadingEnrollments.value = false
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

const selectedUserFile = ref(null)
function onUserFileChange(e) {
  selectedUserFile.value = e.target.files?.[0] || null
}

function openEditModal() {
  modalError.value = null
  selectedUserFile.value = null
  if (branchStore.branches.length === 0) branchStore.fetchBranches()
  editForm.value = {
    full_name: user.value.full_name || '',
    phone: formatPhoneInput(user.value.phone),
    phone2: user.value.phone2 || '',
    role: user.value.role || 'instructor',
    branch: user.value.branch ?? null,
    jshshr: user.value.jshshr || '',
    passport_serie: user.value.passport_serie || '',
    passport_number: user.value.passport_number || '',
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
      phone2: editForm.value.phone2 ? editForm.value.phone2.trim() : null,
      role: editForm.value.role,
      branch: editForm.value.branch ?? null,
      jshshr: editForm.value.jshshr ? parseInt(editForm.value.jshshr, 10) : null,
      passport_serie: editForm.value.passport_serie ? editForm.value.passport_serie.trim().toUpperCase() : null,
      passport_number: editForm.value.passport_number ? parseInt(editForm.value.passport_number, 10) : null,
      notes: editForm.value.notes || '',
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

onMounted(() => {
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

.link-value { cursor: pointer; }
.link-value:hover { text-decoration: underline; color: #2D6A4F; }

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

.td-phone-sub {
  font-size: 11.5px;
  color: #6B7280;
  margin-top: 2px;
}

/* Bigger, more legible group start/end dates under the group name */
.group-dates {
  font-size: 12.5px;
  font-weight: 600;
  color: #374151;
  margin-top: 3px;
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

.students-filter-bar {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #F9FAFB;
  border: 1.5px solid #E5E7EB;
  border-radius: 10px;
  padding: 8px 14px;
  width: 260px;
}

.search-input {
  border: none;
  background: transparent;
  outline: none;
  font-size: 13.5px;
  width: 100%;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 12.5px;
  font-weight: 600;
  color: #4B5563;
  white-space: nowrap;
}

.group-filter-select {
  padding: 6px 12px;
  border: 1.5px solid #E5E7EB;
  border-radius: 8px;
  background: #F9FAFB;
  font-size: 12.5px;
  font-weight: 500;
  color: #111827;
  cursor: pointer;
  outline: none;
}

.cert-status-chip {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;

  &.cert-yes { background: #DCFCE7; color: #15803D; }
  &.cert-no { background: #F3F4F6; color: #6B7280; }
}

.btn-upload-cert {
  display: block;
  margin-top: 6px;
  padding: 3px 9px;
  background: #F0FDF4;
  color: #1B4332;
  border: 1px solid #A7F3D0;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-upload-cert:hover { background: #DCFCE7; border-color: #6EE7B7; }

.reviews-accordion {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.review-row {
  background: #F9FAFB;
  border-radius: 10px;
  padding: 12px 16px;
}

.review-row-top {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.review-row-student {
  font-size: 13.5px;
  font-weight: 700;
  color: #111827;
}

.review-row-stars {
  color: #D97706;
  font-size: 13px;
  letter-spacing: 1px;
}

.review-row-date {
  font-size: 11.5px;
  color: #9CA3AF;
  margin-left: auto;
}

.review-row-comment {
  font-size: 13px;
  color: #4B5563;
  margin-top: 6px;
}

.table-wrap {
  overflow-x: auto;
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
  }

  td {
    padding: 12px 16px;
    border-bottom: 1px solid #F3F4F6;
    color: #1F2937;
  }
}

.student-link {
  font-weight: 600;
  color: #2D6A4F;

  &:hover { text-decoration: underline; }
}

.student-jshshr {
  font-size: 11px;
  color: #9CA3AF;
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

.certs-grid-user {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.cert-card-user {
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  overflow: hidden;
  background: #F9FAFB;
}

.cert-image-user {
  width: 100%;
  height: 130px;
  object-fit: cover;
  cursor: pointer;
  display: block;
}

.cert-meta-user { padding: 10px 12px; }
.cert-student-name { font-size: 13px; font-weight: 700; color: #111827; }
.cert-date-user { font-size: 11px; color: #9CA3AF; margin-top: 2px; }
.cert-notes-user { font-size: 12px; color: #4B5563; margin-top: 6px; }

.cert-bonus-row-user {
  padding: 0 12px 12px;
  display: flex;
  align-items: center;
}

.bonus-paid-badge-user {
  font-size: 11.5px;
  font-weight: 700;
  color: #15803D;
  background: #DCFCE7;
  padding: 4px 10px;
  border-radius: 20px;
}

/* ── Payments table (staff-only section) ─────────────────── */
.payments-table-wrap {
  overflow-x: auto;
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
