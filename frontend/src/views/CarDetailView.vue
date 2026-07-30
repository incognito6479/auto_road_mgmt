<template>
  <AppLayout>

    <!-- Top Action Bar -->
    <div class="page-top">
      <div class="top-left">
        <button class="btn-back" @click="goBack" title="Orqaga">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          Avtomobillar ro'yxatiga qarash
        </button>
        <h2 class="page-main-title">{{ car?.car_name || 'Avtomobil Ma\'lumotlari' }}</h2>
      </div>

      <div v-if="authStore.canEditCars && car" class="header-actions">
        <button class="btn-edit-profile" @click="openEditModal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" style="margin-right: 6px;">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
            <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
          </svg>
          Tahrirlash
        </button>
      </div>
    </div>

    <!-- Loading / Error States -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p class="state-text">Avtomobil ma'lumotlari yuklanmoqda...</p>
    </div>

    <div v-else-if="error" class="state-container state-error">
      <p class="state-text">{{ error }}</p>
      <button class="btn-retry" @click="fetchCarDetail">Qayta urinish</button>
    </div>

    <div v-else-if="car" class="detail-container">

      <!-- Car Header Overview Card -->
      <div class="car-overview-card">
        <div class="car-header-row">
          <div class="car-photo-box" @click="openImageModal(car.image || '/default_car_photo.png')" title="Rasmni kattalashtirish">
            <img :src="car.image || '/default_car_photo.png'" alt="Car" class="car-photo-img" />
          </div>

          <div class="car-header-info">
            <div class="title-status-line">
              <h3 class="car-title-name">{{ car.car_name }}</h3>
              <span class="status-badge" :class="car.status">
                {{ statusText(car.status) }}
              </span>
            </div>
            <div class="plate-number-badge">
              🚘 {{ car.plate_number }}
            </div>
            <p v-if="car.notes" class="car-notes-sub">{{ car.notes }}</p>
          </div>
        </div>
      </div>

      <!-- Detail Grid Section -->
      <div class="detail-grid">

        <!-- Left: Technical Information + Instructor Assignment History -->
        <div class="status-cards-col">
          <div class="info-card">
            <div class="card-header">
              <div class="icon-circle">
                <svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="2" width="20" height="20">
                  <rect x="1" y="3" width="15" height="13"></rect>
                  <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
                  <circle cx="5.5" cy="18.5" r="2.5"></circle>
                  <circle cx="18.5" cy="18.5" r="2.5"></circle>
                </svg>
              </div>
              <h4>Texnik Ma'lumotlar</h4>
            </div>

            <div class="info-list">
              <div class="info-item">
                <span class="item-label">Avtomobil nomi:</span>
                <span class="item-value font-bold">{{ car.car_name }}</span>
              </div>

              <div class="info-item">
                <span class="item-label">Davlat raqami:</span>
                <span class="item-value font-mono font-bold">{{ car.plate_number }}</span>
              </div>

              <div class="info-item">
                <span class="item-label">Ishlab chiqarilgan yili:</span>
                <span class="item-value">{{ car.manufact_year || '-' }}</span>
              </div>

              <div class="info-item">
                <span class="item-label">Filial (Branch):</span>
                <span class="item-value">{{ car.branch_name || car.branch?.name || '-' }}</span>
              </div>

              <div class="info-item">
                <span class="item-label">Biriktirilgan instruktor:</span>
                <span class="item-value font-bold">
                  <span v-if="car.instructor" class="link-value" @click="goUser(car.instructor)">{{ car.instructor_name }}</span>
                  <span v-else>Biriktirilmagan</span>
                </span>
              </div>

              <div class="info-item">
                <span class="item-label">Probeg:</span>
                <span class="item-value">{{ car.mileage ? `${formatNumber(car.mileage)} km` : '-' }}</span>
              </div>

              <div class="info-item">
                <span class="item-label">Status:</span>
                <span class="item-value"><span class="status-chip" :class="car.status">{{ statusText(car.status) }}</span></span>
              </div>
            </div>
          </div>

          <!-- Instructor Assignment History (moved here, under Technical Info) -->
          <div class="info-card">
            <div class="card-header" style="justify-content: space-between;">
              <div style="display: flex; align-items: center; gap: 12px;">
                <div class="icon-circle">
                  <svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="2" width="20" height="20">
                    <circle cx="12" cy="8" r="4"></circle>
                    <path d="M4 21v-1a8 8 0 0 1 16 0v1"></path>
                  </svg>
                </div>
                <h4>Instruktor Biriktirish Tarixi</h4>
              </div>
              <button v-if="authStore.canEditCars" type="button" class="btn-change-instructor" @click="openInstructorModal">
                {{ car.instructor ? "Instruktorni o'zgartirish" : "+ Instruktor qo'shish" }}
              </button>
            </div>

            <div v-if="!car.assignment_history || car.assignment_history.length === 0" class="history-empty">
              Ushbu avtomobilga hali instruktor biriktirilmagan.
            </div>
            <div v-else class="table-scroll"><table class="history-table">
              <thead>
                <tr>
                  <th>Instruktor</th>
                  <th>Biriktirilgan sana</th>
                  <th>Ajratilgan sana</th>
                  <th>Topshirilgandagi moy holati</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="h in car.assignment_history" :key="h.id">
                  <td class="font-bold">
                    <span v-if="h.instructor" class="link-value" @click="goUser(h.instructor)">{{ h.instructor_name || 'Noma\'lum' }}</span>
                    <span v-else>{{ h.instructor_name || 'Noma\'lum' }}</span>
                  </td>
                  <td>{{ formatDateTime(h.assigned_at) }}</td>
                  <td>
                    <span v-if="h.unassigned_at">{{ formatDateTime(h.unassigned_at) }}</span>
                    <span v-else class="current-badge">Hozirgi</span>
                  </td>
                  <td>
                    <template v-if="h.unassigned_at && (h.mileage_at_unassignment != null || h.oil_change_date_at_unassignment || h.oil_change_mileage_at_unassignment != null)">
                      <div v-if="h.mileage_at_unassignment != null" class="oil-snapshot-row">Probeg: {{ formatNumber(h.mileage_at_unassignment) }} km</div>
                      <div v-if="h.oil_change_date_at_unassignment" class="oil-snapshot-row">Moy almashtirilgan: {{ formatDate(h.oil_change_date_at_unassignment) }}</div>
                      <div v-if="h.oil_change_mileage_at_unassignment != null" class="oil-snapshot-row">Almashtirilgandagi probeg: {{ formatNumber(h.oil_change_mileage_at_unassignment) }} km</div>
                    </template>
                    <span v-else class="text-muted">-</span>
                  </td>
                </tr>
              </tbody>
            </table></div>
          </div>
        </div>

        <!-- Right: Insurance Policy & Inspection Cards -->
        <div class="status-cards-col">

          <!-- Oil Change Status Card -->
          <div class="info-card">
            <div class="card-header" style="justify-content: space-between;">
              <div style="display: flex; align-items: center; gap: 12px;">
                <div class="icon-circle icon-amber">
                  <svg viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2" width="20" height="20">
                    <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"></path>
                    <circle cx="12" cy="12" r="4"></circle>
                  </svg>
                </div>
                <h4>Moy Almashtirish Holati</h4>
              </div>
              <button v-if="authStore.canEditCars" type="button" class="btn-change-date" @click="openOilChangeModal">
                O'zgartirish
              </button>
            </div>

            <div class="policy-body">
              <div class="date-row">
                <span>Oxirgi moy almashtirilgan sana:</span>
                <span class="font-bold">{{ formatDate(car.oil_change_date) }}</span>
              </div>
              <div class="date-row">
                <span>Almashtirilgandagi probeg:</span>
                <span class="font-bold">{{ car.oil_change_mileage != null ? `${formatNumber(car.oil_change_mileage)} km` : '-' }}</span>
              </div>
              <div class="date-row">
                <span>Joriy probeg:</span>
                <span class="font-bold">{{ car.mileage != null ? `${formatNumber(car.mileage)} km` : '-' }}</span>
              </div>
              <div class="date-row">
                <span>Almashtirish oralig'i:</span>
                <span class="font-bold">{{ formatNumber(oilChangeIntervalKm) }} km</span>
              </div>
              <template v-if="mileageSinceOilChange !== null">
                <div class="date-row">
                  <span>Moy almashtirilgandan beri yurgan:</span>
                  <span class="font-bold">{{ formatNumber(mileageSinceOilChange) }} km</span>
                </div>
                <div class="days-remaining" :class="mileageUntilNextOilChange <= 0 ? 'days-expired' : (mileageUntilNextOilChange <= 500 ? 'days-warning' : 'days-good')">
                  {{ mileageUntilNextOilChange <= 0
                    ? `Moy almashtirish vaqti keldi! (${formatNumber(Math.abs(mileageUntilNextOilChange))} km oshib ketgan)`
                    : `Keyingi moy almashtirishgacha ${formatNumber(mileageUntilNextOilChange)} km qoldi` }}
                </div>
              </template>
              <p v-else class="wash-hint">Probeg va moy almashtirilgandagi probeg kiritilmagan.</p>
            </div>
          </div>

          <!-- Wash Status Card -->
          <div class="info-card">
            <div class="card-header">
              <div class="icon-circle icon-blue">
                <svg viewBox="0 0 24 24" fill="none" stroke="#0284C7" stroke-width="2" width="20" height="20">
                  <path d="M3 12h18M3 12a9 9 0 0 1 18 0M3 12a9 9 0 0 0 18 0"></path>
                </svg>
              </div>
              <h4>Yuvish Holati</h4>
            </div>

            <div class="policy-body">
              <div class="date-row">
                <span>Oxirgi marta yuvilgan:</span>
                <span class="font-bold">{{ car.last_washed_at ? formatDateTime(car.last_washed_at) : 'Hali yuvilmagan' }}</span>
              </div>

              <button
                v-if="canMarkWashed"
                class="btn-wash-action"
                :disabled="washing"
                @click="markWashed"
              >
                {{ washing ? "Belgilanmoqda..." : "🧼 Yuvilgan deb belgilash" }}
              </button>
              <p v-else-if="authStore.user" class="wash-hint">
                Faqat ushbu avtomobilga biriktirilgan instruktor uni yuvilgan deb belgilashi mumkin.
              </p>
              <p v-if="washError" class="modal-alert modal-alert-error" style="margin-top: 10px;">{{ washError }}</p>
            </div>
          </div>

          <!-- Sug'urta Card -->
          <div class="info-card">
            <div class="card-header" style="justify-content: space-between;">
              <div style="display: flex; align-items: center; gap: 12px;">
                <div class="icon-circle icon-blue">
                  <svg viewBox="0 0 24 24" fill="none" stroke="#0284C7" stroke-width="2" width="20" height="20">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                  </svg>
                </div>
                <h4>Sug'urta Polis Muddati</h4>
              </div>
              <button v-if="authStore.canEditCars" type="button" class="btn-change-date" @click="openQuickDateModal('policy_date', 'Sug\'urta Polis Muddati')">
                O'zgartirish
              </button>
            </div>

            <div class="policy-body">
              <div class="date-row">
                <span>Amal qilish muddati:</span>
                <span class="font-bold">{{ formatDate(car.policy_date) }}</span>
              </div>
              <div v-if="policyDaysRemaining !== null" class="days-remaining" :class="daysClass(policyDaysRemaining)">
                {{ daysRemainingText(policyDaysRemaining) }}
              </div>
            </div>
          </div>

          <!-- Texnik Ko'rik Card -->
          <div class="info-card">
            <div class="card-header" style="justify-content: space-between;">
              <div style="display: flex; align-items: center; gap: 12px;">
                <div class="icon-circle icon-amber">
                  <svg viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2" width="20" height="20">
                    <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
                  </svg>
                </div>
                <h4>Texnik Ko'rik Muddati</h4>
              </div>
              <button v-if="authStore.canEditCars" type="button" class="btn-change-date" @click="openQuickDateModal('tech_inspection_date', 'Texnik Ko\'rik Muddati')">
                O'zgartirish
              </button>
            </div>

            <div class="policy-body">
              <div class="date-row">
                <span>Amal qilish muddati:</span>
                <span class="font-bold">{{ formatDate(car.tech_inspection_date) }}</span>
              </div>
              <div v-if="techDaysRemaining !== null" class="days-remaining" :class="daysClass(techDaysRemaining)">
                {{ daysRemainingText(techDaysRemaining) }}
              </div>
            </div>
          </div>

          <!-- Wash History Card (same width as the column above) -->
          <div class="info-card">
            <div class="card-header">
              <div class="icon-circle icon-blue">
                <svg viewBox="0 0 24 24" fill="none" stroke="#0284C7" stroke-width="2" width="20" height="20">
                  <path d="M3 12h18M3 12a9 9 0 0 1 18 0M3 12a9 9 0 0 0 18 0"></path>
                </svg>
              </div>
              <h4>Yuvish Tarixi</h4>
            </div>

            <div v-if="!car.wash_history || car.wash_history.length === 0" class="history-empty">
              Ushbu avtomobil hali yuvilmagan.
            </div>
            <div v-else class="table-scroll"><table class="history-table">
              <thead>
                <tr>
                  <th>Instruktor</th>
                  <th>Yuvilgan sana va vaqt</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="w in car.wash_history" :key="w.id">
                  <td class="font-bold">
                    <span v-if="w.instructor" class="link-value" @click="goUser(w.instructor)">{{ w.instructor_name || 'Noma\'lum' }}</span>
                    <span v-else>{{ w.instructor_name || 'Noma\'lum' }}</span>
                  </td>
                  <td>{{ formatDateTime(w.washed_at) }}</td>
                </tr>
              </tbody>
            </table></div>
          </div>

        </div>

      </div>

    </div>

    <!-- Edit Car Modal -->
    <dialog ref="carModal" class="modal-dialog">
      <div class="car-modal-header">
        <div class="header-badge-wrap">
          <div class="header-badge-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="2" width="22" height="22">
              <rect x="1" y="3" width="15" height="13"></rect>
              <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
              <circle cx="5.5" cy="18.5" r="2.5"></circle>
              <circle cx="18.5" cy="18.5" r="2.5"></circle>
            </svg>
          </div>
          <div>
            <h3 class="car-modal-title">Avtomobilni Tahrirlash</h3>
            <p class="car-modal-sub">Ma'lumotlarni va rasmni yangilang</p>
          </div>
        </div>
        <button class="car-btn-close" @click="closeModal" title="Yopish">✕</button>
      </div>

      <form @submit.prevent="saveCar" class="car-modal-form">
        <div v-if="modalError" class="modal-alert modal-alert-error">
          <span>{{ modalError }}</span>
        </div>

        <div class="form-group">
          <label class="form-label required">Avtomobil nomi va davlat raqami *</label>
          <input v-model="editForm.car_name" type="text" class="form-input" required placeholder="Masalan: Cobalt 01 A 777 AA" />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Ishlab chiqarilgan yili</label>
            <input v-model="editForm.manufact_year" type="number" class="form-input" placeholder="2022" />
          </div>

          <div class="form-group">
            <label class="form-label">Status</label>
            <select v-model="editForm.status" class="form-input status-select-fixed">
              <option value="available">Mavjud (Bo'sh)</option>
              <option value="repairing">Ta'mirlashda</option>
              <option value="not_available">Mavjud emas</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Biriktirilgan instruktor</label>
            <div class="searchable-select" @click.stop>
              <input
                type="text"
                class="form-input"
                v-model="instructorSearchText"
                @focus="instructorDropdownOpen = true"
                @input="instructorDropdownOpen = true"
                @blur="onInstructorBlur"
                placeholder="Instruktorni qidirish..."
                autocomplete="off"
              />
              <div v-if="instructorDropdownOpen" class="searchable-dropdown">
                <div
                  class="searchable-option"
                  :class="{ selected: !editForm.instructor }"
                  @mousedown.prevent="selectInstructor(null)"
                >Biriktirilmagan</div>
                <div
                  v-for="i in filteredInstructorOptions"
                  :key="i.id"
                  class="searchable-option"
                  :class="{ selected: editForm.instructor === i.id }"
                  @mousedown.prevent="selectInstructor(i)"
                >{{ i.full_name || i.phone }}</div>
                <div v-if="filteredInstructorOptions.length === 0" class="searchable-empty">Instruktor topilmadi</div>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Probeg (km)</label>
            <input v-model="editForm.mileage" type="number" class="form-input" placeholder="45000" min="0" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Moy almashtirilgan sana</label>
            <input v-model="editForm.oil_change_date" type="date" class="form-input" />
          </div>

          <div class="form-group">
            <label class="form-label">Moy almashtirilgandagi probeg (km)</label>
            <input v-model="editForm.oil_change_mileage" type="number" class="form-input" placeholder="42000" min="0" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Moy almashtirish oralig'i (km)</label>
            <input v-model="editForm.oil_change_interval_km" type="number" class="form-input" placeholder="5000" min="0" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Sug'urta muddati</label>
            <input v-model="editForm.policy_date" type="date" class="form-input" />
          </div>

          <div class="form-group">
            <label class="form-label">Texnik ko'rik muddati</label>
            <input v-model="editForm.tech_inspection_date" type="date" class="form-input" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Avtomobil Rasmi (Foto)</label>
          <div style="display: flex; align-items: center; gap: 12px; width: 100%;">
            <img v-if="editForm.existingImage" :src="editForm.existingImage" alt="Current Photo" style="width: 44px; height: 44px; border-radius: 8px; object-fit: cover; border: 1px solid #E5E7EB; flex-shrink: 0;" />
            <input type="file" accept="image/*" class="form-input" style="width: 100%;" @change="onCarFileChange" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Qo'shimcha izoh</label>
          <textarea v-model="editForm.notes" rows="3" class="form-input form-textarea"></textarea>
        </div>

        <div class="car-modal-footer">
          <button type="button" class="btn-cancel" @click="closeModal">Bekor qilish</button>
          <button type="submit" class="btn-submit" :disabled="saving">
            {{ saving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Quick Date Change Modal -->
    <dialog ref="quickDateModal" class="modal-dialog modal-sm-fixed" closedby="any">
      <div class="car-modal-header">
        <div class="header-badge-wrap">
          <div class="header-badge-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="2" width="20" height="20">
              <rect x="3" y="4" width="18" height="18" rx="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
          </div>
          <div>
            <h3 class="car-modal-title">{{ quickDateLabel }}ni o'zgartirish</h3>
            <p class="car-modal-sub">Yangi sanani tanlang</p>
          </div>
        </div>
        <button class="car-btn-close" @click="closeQuickDateModal" title="Yopish">✕</button>
      </div>

      <form @submit.prevent="saveQuickDate" class="car-modal-form">
        <div v-if="quickDateError" class="modal-alert modal-alert-error">
          <span>{{ quickDateError }}</span>
        </div>

        <div class="form-group">
          <label class="form-label required">Yangi sana *</label>
          <input v-model="quickDateValue" type="date" class="form-input" required />
        </div>

        <div class="car-modal-footer">
          <button type="button" class="btn-cancel" @click="closeQuickDateModal">Bekor qilish</button>
          <button type="submit" class="btn-submit" :disabled="quickDateSaving">
            {{ quickDateSaving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Oil Change Info Modal -->
    <dialog ref="oilChangeModal" class="modal-dialog modal-sm-fixed" closedby="any">
      <div class="car-modal-header">
        <div class="header-badge-wrap">
          <div class="header-badge-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="2" width="20" height="20">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"></path>
              <circle cx="12" cy="12" r="4"></circle>
            </svg>
          </div>
          <div>
            <h3 class="car-modal-title">Moy almashtirish ma'lumotlari</h3>
            <p class="car-modal-sub">Barcha moy almashtirish maydonlarini yangilang</p>
          </div>
        </div>
        <button class="car-btn-close" @click="closeOilChangeModal" title="Yopish">✕</button>
      </div>

      <form @submit.prevent="saveOilChangeInfo" class="car-modal-form">
        <div v-if="oilChangeError" class="modal-alert modal-alert-error">
          <span>{{ oilChangeError }}</span>
        </div>

        <div class="form-group">
          <label class="form-label">Joriy probeg (km)</label>
          <input v-model="oilChangeForm.mileage" type="number" class="form-input" placeholder="45000" min="0" />
        </div>

        <div class="form-group">
          <label class="form-label">Moy almashtirilgan sana</label>
          <input v-model="oilChangeForm.oil_change_date" type="date" class="form-input" />
        </div>

        <div class="form-group">
          <label class="form-label">Almashtirilgandagi probeg (km)</label>
          <input v-model="oilChangeForm.oil_change_mileage" type="number" class="form-input" placeholder="42000" min="0" />
        </div>

        <div class="form-group">
          <label class="form-label">Almashtirish oralig'i (km)</label>
          <input v-model="oilChangeForm.oil_change_interval_km" type="number" class="form-input" placeholder="5000" min="0" />
        </div>

        <div class="car-modal-footer">
          <button type="button" class="btn-cancel" @click="closeOilChangeModal">Bekor qilish</button>
          <button type="submit" class="btn-submit" :disabled="oilChangeSaving">
            {{ oilChangeSaving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Instructor Assignment Modal -->
    <dialog ref="instructorModal" class="modal-dialog modal-sm-fixed" closedby="any">
      <div class="car-modal-header">
        <div class="header-badge-wrap">
          <div class="header-badge-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="#2D6A4F" stroke-width="2" width="20" height="20">
              <circle cx="12" cy="8" r="4"></circle>
              <path d="M4 21v-1a8 8 0 0 1 16 0v1"></path>
            </svg>
          </div>
          <div>
            <h3 class="car-modal-title">{{ car?.instructor ? "Instruktorni o'zgartirish" : "Instruktor biriktirish" }}</h3>
            <p class="car-modal-sub">Ushbu avtomobilga instruktor tayinlang</p>
          </div>
        </div>
        <button class="car-btn-close" @click="closeInstructorModal" title="Yopish">✕</button>
      </div>

      <form @submit.prevent="saveInstructorAssignment" class="car-modal-form">
        <div v-if="instructorModalError" class="modal-alert modal-alert-error">
          <span>{{ instructorModalError }}</span>
        </div>

        <div class="form-group">
          <label class="form-label">Instruktor</label>
          <div class="search-select-container">
            <div
              class="search-select-trigger"
              :class="{ 'is-open': instrModalOpen, 'has-selected': selectedInstrModalOption }"
              @click="instrModalOpen = !instrModalOpen"
            >
              <template v-if="selectedInstrModalOption">
                <div class="selected-user-card">
                  <div class="user-avatar-badge avatar-inst">
                    {{ selectedInstrModalOption.first_name?.[0] || 'I' }}
                  </div>
                  <div class="selected-user-details">
                    <span class="selected-user-name">{{ selectedInstrModalOption.full_name || selectedInstrModalOption.phone }}</span>
                    <span class="selected-user-phone">{{ selectedInstrModalOption.phone }}</span>
                  </div>
                  <button type="button" class="btn-remove-selection" @click.stop="selectInstrModalOption(null)" title="Tozalash">✕</button>
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
                <svg class="select-arrow-icon" :class="{ rotate: instrModalOpen }" viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
                  <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd"/>
                </svg>
              </template>
            </div>

            <div v-if="instrModalOpen" class="search-select-dropdown" @click.stop>
              <div class="dropdown-search-wrap">
                <input
                  type="text"
                  v-model="instrModalSearch"
                  placeholder="Ism yoki telefon raqami..."
                  class="dropdown-search-field"
                  autofocus
                  @keydown="onInstrModalKeydown"
                />
              </div>
              <div class="dropdown-options-container">
                <div
                  class="dropdown-option-row option-clear"
                  :class="{ 'is-active': !instrModalForm.instructor }"
                  @click="selectInstrModalOption(null)"
                >
                  <span>&lt; Biriktirilmagan &gt;</span>
                </div>
                <div
                  v-for="(inst, idx) in filteredInstrModalOptions"
                  :key="inst.id"
                  class="dropdown-option-row"
                  :class="{ 'is-active': instrModalForm.instructor === inst.id, 'is-highlighted': instrModalKb.highlightedIndex.value === idx }"
                  @click="selectInstrModalOption(inst)"
                >
                  <div class="opt-avatar avatar-inst">{{ inst.first_name?.[0] || 'I' }}</div>
                  <div class="opt-info">
                    <span class="opt-name">{{ inst.full_name || inst.phone }}</span>
                    <span class="opt-phone">{{ inst.phone }}</span>
                  </div>
                  <span v-if="instrModalForm.instructor === inst.id" class="opt-check">✓</span>
                </div>
                <div v-if="filteredInstrModalOptions.length === 0" class="dropdown-empty">
                  Instruktor topilmadi
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="car-modal-footer">
          <button type="button" class="btn-cancel" @click="closeInstructorModal">Bekor qilish</button>
          <button type="submit" class="btn-submit" :disabled="instrModalSaving">
            {{ instrModalSaving ? 'Saqlanmoqda...' : 'Saqlash' }}
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
import { formatDate, formatNumber } from '@/utils/formatters'
import { useSearchSelectKeyboard } from '@/composables/useSearchSelectKeyboard'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const car = ref(null)
const loading = ref(true)
const error = ref(null)

const carModal = ref(null)
const saving = ref(false)
const modalError = ref(null)
const selectedCarFile = ref(null)

const instructors = ref([])
async function fetchInstructors() {
  try {
    const res = await api.get('/users/', { params: { role: 'instructor', page_size: 1000 } })
    instructors.value = res.data.results || res.data || []
  } catch (err) {
    console.error("Instruktorlarni yuklashda xatolik:", err)
  }
}

const editForm = ref({
  car_name: '',
  plate_number: '',
  manufact_year: '',
  status: 'available',
  instructor: null,
  mileage: null,
  oil_change_date: '',
  oil_change_mileage: null,
  oil_change_interval_km: 5000,
  policy_date: '',
  tech_inspection_date: '',
  notes: '',
  existingImage: null
})

// ── Searchable instructor select ──────────────────────
const instructorSearchText = ref('')
const instructorDropdownOpen = ref(false)
const filteredInstructorOptions = computed(() => {
  const q = instructorSearchText.value.trim().toLowerCase()
  if (!q) return instructors.value
  return instructors.value.filter(i =>
    (i.full_name || '').toLowerCase().includes(q) || (i.phone || '').includes(q)
  )
})
function selectInstructor(i) {
  editForm.value.instructor = i ? i.id : null
  instructorSearchText.value = i ? (i.full_name || i.phone) : ''
  instructorDropdownOpen.value = false
}
function onInstructorBlur() {
  setTimeout(() => { instructorDropdownOpen.value = false }, 150)
}

// ── Dedicated Add/Change Instructor modal ──────────────
const instructorModal = ref(null)
const instrModalForm = ref({ instructor: null })
const instrModalSearch = ref('')
const instrModalOpen = ref(false)
const instrModalSaving = ref(false)
const instrModalError = ref(null)

const selectedInstrModalOption = computed(() => {
  if (!instrModalForm.value.instructor) return null
  return instructors.value.find(i => i.id === instrModalForm.value.instructor) || null
})

const filteredInstrModalOptions = computed(() => {
  const q = instrModalSearch.value.trim().toLowerCase()
  if (!q) return instructors.value
  return instructors.value.filter(i =>
    (i.full_name || '').toLowerCase().includes(q) || (i.phone || '').includes(q)
  )
})

function selectInstrModalOption(i) {
  instrModalForm.value.instructor = i ? i.id : null
  instrModalSearch.value = ''
  instrModalOpen.value = false
}

const instrModalKb = useSearchSelectKeyboard()
function onInstrModalKeydown(e) {
  instrModalKb.onKeydown(e, filteredInstrModalOptions.value, selectInstrModalOption, () => { instrModalOpen.value = false })
}

async function openInstructorModal() {
  instrModalError.value = null
  instrModalSearch.value = ''
  instrModalOpen.value = false
  instrModalForm.value = { instructor: car.value?.instructor || null }
  if (instructors.value.length === 0) await fetchInstructors()
  instructorModal.value?.showModal()
}

function closeInstructorModal() {
  instructorModal.value?.close()
}

async function saveInstructorAssignment() {
  instrModalSaving.value = true
  instrModalError.value = null
  try {
    const res = await api.patch(`/cars/${car.value.id}/`, { instructor: instrModalForm.value.instructor || null })
    car.value = res.data
    closeInstructorModal()
  } catch (err) {
    instrModalError.value = err.response?.data?.detail || "Instruktorni saqlashda xatolik yuz berdi."
  } finally {
    instrModalSaving.value = false
  }
}

// Oil change mileage tracking — service interval (km) is configurable per car
// via car.oil_change_interval_km (defaults to 5000 on the backend).
const mileageSinceOilChange = computed(() => {
  if (!car.value || car.value.mileage == null || car.value.oil_change_mileage == null) return null
  return car.value.mileage - car.value.oil_change_mileage
})

const oilChangeIntervalKm = computed(() => car.value?.oil_change_interval_km || 5000)

const mileageUntilNextOilChange = computed(() => {
  if (mileageSinceOilChange.value === null) return null
  return oilChangeIntervalKm.value - mileageSinceOilChange.value
})

// Only the car's currently assigned instructor (or an admin/superuser) may
// mark it as washed.
const canMarkWashed = computed(() => {
  const user = authStore.user
  if (!user || !car.value) return false
  if (authStore.isAdminOrSuperuser || authStore.isMechanic) return true
  return !!(car.value.instructor && user.id === car.value.instructor)
})

const washing = ref(false)
const washError = ref('')

async function markWashed() {
  if (!car.value) return
  washing.value = true
  washError.value = ''
  try {
    await api.post(`/cars/${car.value.id}/mark_washed/`)
    await fetchCarDetail()
  } catch (err) {
    washError.value = err.response?.data?.detail || "Yuvilgan deb belgilashda xatolik yuz berdi."
  } finally {
    washing.value = false
  }
}

function formatDateTime(dtStr) {
  if (!dtStr) return '-'
  const d = new Date(dtStr)
  if (isNaN(d.getTime())) return dtStr
  return `${d.toLocaleDateString('uz-UZ')} ${d.toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' })}`
}

const imageZoomModal = ref(null)
const zoomedImageUrl = ref('')

function openImageModal(url) {
  if (!url) return
  zoomedImageUrl.value = url
  imageZoomModal.value?.showModal()
}

function onCarFileChange(e) {
  selectedCarFile.value = e.target.files?.[0] || null
}

const policyDaysRemaining = computed(() => {
  if (!car.value?.policy_date) return null
  const target = new Date(car.value.policy_date)
  const today = new Date()
  today.setHours(0,0,0,0)
  const diffTime = target - today
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
})

const techDaysRemaining = computed(() => {
  if (!car.value?.tech_inspection_date) return null
  const target = new Date(car.value.tech_inspection_date)
  const today = new Date()
  today.setHours(0,0,0,0)
  const diffTime = target - today
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
})

function daysRemainingText(days) {
  if (days < 0) return `${Math.abs(days)} kun oldin muddati o'tgan`
  if (days === 0) return "Bugun muddati tugaydi!"
  return `${days} kun qoldi`
}

function daysClass(days) {
  if (days < 0) return 'days-expired'
  if (days <= 15) return 'days-warning'
  return 'days-good'
}

function statusText(st) {
  switch (st) {
    case 'available': return 'Mavjud'
    case 'repairing': return "Ta'mirlashda"
    case 'not_available': return 'Mavjud emas'
    default: return st || '-'
  }
}

async function fetchCarDetail() {
  loading.value = true
  error.value = null
  try {
    const res = await api.get(`/cars/${route.params.id}/`)
    car.value = res.data
  } catch (err) {
    console.error(err)
    error.value = "Avtomobil ma'lumotlarini yuklashda xatolik"
  } finally {
    loading.value = false
  }
}

function openEditModal() {
  modalError.value = null
  selectedCarFile.value = null
  editForm.value = {
    car_name: car.value.car_name || '',
    manufact_year: car.value.manufact_year || '',
    status: car.value.status || 'available',
    instructor: car.value.instructor || null,
    mileage: car.value.mileage ?? null,
    oil_change_date: car.value.oil_change_date || '',
    oil_change_mileage: car.value.oil_change_mileage ?? null,
    oil_change_interval_km: car.value.oil_change_interval_km ?? 5000,
    policy_date: car.value.policy_date || '',
    tech_inspection_date: car.value.tech_inspection_date || '',
    notes: car.value.notes || '',
    existingImage: car.value.image || null,
  }
  instructorSearchText.value = car.value.instructor_name || ''
  instructorDropdownOpen.value = false
  carModal.value?.showModal()
}

function closeModal() {
  carModal.value?.close()
}

async function saveCar() {
  if (!editForm.value.car_name || !editForm.value.car_name.trim()) {
    modalError.value = "Avtomobil nomini kiriting."
    return
  }
  saving.value = true
  modalError.value = null
  try {
    const payload = {
      car_name: editForm.value.car_name.trim(),
      status: editForm.value.status || 'available',
      instructor: editForm.value.instructor || null,
      mileage: editForm.value.mileage !== null && editForm.value.mileage !== '' ? parseInt(editForm.value.mileage, 10) : null,
      oil_change_date: editForm.value.oil_change_date || null,
      oil_change_mileage: editForm.value.oil_change_mileage !== null && editForm.value.oil_change_mileage !== '' ? parseInt(editForm.value.oil_change_mileage, 10) : null,
      oil_change_interval_km: editForm.value.oil_change_interval_km !== null && editForm.value.oil_change_interval_km !== '' ? parseInt(editForm.value.oil_change_interval_km, 10) : 5000,
      manufact_year: editForm.value.manufact_year ? parseInt(editForm.value.manufact_year, 10) : null,
      policy_date: editForm.value.policy_date || null,
      tech_inspection_date: editForm.value.tech_inspection_date || null,
      notes: editForm.value.notes ? editForm.value.notes.trim() : '',
    }

    let res
    if (selectedCarFile.value) {
      const formData = new FormData()
      Object.keys(payload).forEach(k => {
        if (payload[k] !== null && payload[k] !== undefined) {
          formData.append(k, payload[k])
        }
      })
      formData.append('image', selectedCarFile.value)
      res = await api.patch(`/cars/${car.value.id}/`, formData)
    } else {
      res = await api.patch(`/cars/${car.value.id}/`, payload)
    }

    car.value = res.data
    closeModal()
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
      modalError.value = "Saqlashda xatolik yuz berdi"
    }
  } finally {
    saving.value = false
  }
}

function goBack() {
  router.push('/vehicles')
}

function goUser(id) {
  if (!id) return
  router.push(`/users/${id}`)
}

// ── Quick date change (policy_date / tech_inspection_date) ───────────
const quickDateModal = ref(null)
const quickDateField = ref('')
const quickDateLabel = ref('')
const quickDateValue = ref('')
const quickDateSaving = ref(false)
const quickDateError = ref('')

function openQuickDateModal(field, label) {
  quickDateField.value = field
  quickDateLabel.value = label
  quickDateValue.value = car.value?.[field] || ''
  quickDateError.value = ''
  quickDateModal.value?.showModal()
}

function closeQuickDateModal() {
  quickDateModal.value?.close()
}

async function saveQuickDate() {
  if (!quickDateValue.value || !quickDateField.value) {
    quickDateError.value = "Sanani tanlang."
    return
  }
  quickDateSaving.value = true
  quickDateError.value = ''
  try {
    const res = await api.patch(`/cars/${car.value.id}/`, { [quickDateField.value]: quickDateValue.value })
    car.value = res.data
    closeQuickDateModal()
  } catch (err) {
    console.error(err)
    quickDateError.value = err.response?.data?.detail || "Sanani saqlashda xatolik yuz berdi."
  } finally {
    quickDateSaving.value = false
  }
}

// ── Bulk oil-change info edit (date + mileage + interval together) ───
const oilChangeModal = ref(null)
const oilChangeForm = ref({ mileage: null, oil_change_date: '', oil_change_mileage: null, oil_change_interval_km: 5000 })
const oilChangeSaving = ref(false)
const oilChangeError = ref('')

function openOilChangeModal() {
  oilChangeForm.value = {
    mileage: car.value?.mileage ?? null,
    oil_change_date: car.value?.oil_change_date || '',
    oil_change_mileage: car.value?.oil_change_mileage ?? null,
    oil_change_interval_km: car.value?.oil_change_interval_km ?? 5000,
  }
  oilChangeError.value = ''
  oilChangeModal.value?.showModal()
}

function closeOilChangeModal() {
  oilChangeModal.value?.close()
}

async function saveOilChangeInfo() {
  oilChangeSaving.value = true
  oilChangeError.value = ''
  try {
    const payload = {
      mileage: oilChangeForm.value.mileage !== null && oilChangeForm.value.mileage !== ''
        ? parseInt(oilChangeForm.value.mileage, 10) : null,
      oil_change_date: oilChangeForm.value.oil_change_date || null,
      oil_change_mileage: oilChangeForm.value.oil_change_mileage !== null && oilChangeForm.value.oil_change_mileage !== ''
        ? parseInt(oilChangeForm.value.oil_change_mileage, 10) : null,
      oil_change_interval_km: oilChangeForm.value.oil_change_interval_km !== null && oilChangeForm.value.oil_change_interval_km !== ''
        ? parseInt(oilChangeForm.value.oil_change_interval_km, 10) : 5000,
    }
    const res = await api.patch(`/cars/${car.value.id}/`, payload)
    car.value = res.data
    closeOilChangeModal()
  } catch (err) {
    console.error(err)
    oilChangeError.value = err.response?.data?.detail || "Saqlashda xatolik yuz berdi."
  } finally {
    oilChangeSaving.value = false
  }
}

onMounted(() => {
  fetchCarDetail()
  fetchInstructors()
})
</script>

<style scoped>
*, *::before, *::after { box-sizing: border-box; }
.page-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.top-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 16px;
  border-radius: 10px;
  background: white;
  border: 1px solid #E5E7EB;
  font-size: 13.5px;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-back:hover {
  background: #F9FAFB;
  border-color: #D1D5DB;
}
.page-main-title {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
}

.btn-edit-profile {
  display: inline-flex;
  align-items: center;
  padding: 10px 18px;
  border-radius: 10px;
  background: #2D6A4F;
  color: white;
  font-size: 13.5px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: background 0.15s ease;
  box-shadow: 0 4px 12px rgba(45, 106, 79, 0.2);
}
.btn-edit-profile:hover {
  background: #1B4332;
}

.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
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
.state-text {
  margin-top: 12px;
  font-size: 14px;
  color: #6B7280;
}

.car-overview-card {
  background: white;
  border-radius: 16px;
  border: 1px solid #E5E7EB;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.03);
}
.car-header-row {
  display: flex;
  align-items: center;
  gap: 24px;
}
.car-photo-box {
  width: 120px;
  height: 90px;
  border-radius: 12px;
  overflow: hidden;
  background: #F3F4F6;
  border: 1px solid #E5E7EB;
  flex-shrink: 0;
  cursor: pointer;
  transition: transform 0.15s ease;
}
.car-photo-box:hover {
  transform: scale(1.03);
}
.car-photo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.car-header-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.title-status-line {
  display: flex;
  align-items: center;
  gap: 12px;
}
.car-title-name {
  font-size: 22px;
  font-weight: 800;
  color: #111827;
}
.status-badge {
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 20px;
  text-transform: capitalize;
}
.status-badge.available { background: #DCFCE7; color: #15803D; }
.status-badge.in_use { background: #FEF3C7; color: #B45309; }
.status-badge.maintenance { background: #FEE2E2; color: #B91C1C; }

.plate-number-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  background: #F3F4F6;
  border-radius: 8px;
  font-family: monospace;
  font-weight: 700;
  font-size: 15px;
  color: #1F2937;
}
.car-notes-sub {
  font-size: 13px;
  color: #6B7280;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  /* Without this, grid stretches the left "Texnik Ma'lumotlar" card to match
     the much taller right column (4 stacked status cards), leaving a large
     empty gap under its content. Size each column to its own content instead. */
  align-items: start;
}

.info-card {
  background: white;
  border-radius: 16px;
  border: 1px solid #E5E7EB;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.03);
}
.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.card-header h4 {
  font-size: 16px;
  font-weight: 700;
  color: #111827;
}
.icon-circle {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: #ECFDF5;
  display: flex;
  align-items: center;
  justify-content: center;
}
.icon-blue { background: #E0F2FE; }
.icon-amber { background: #FEF3C7; }

.info-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 12px;
  border-bottom: 1px dashed #F3F4F6;
}
.item-label { font-size: 13.5px; color: #6B7280; }
.item-value { font-size: 14px; color: #111827; }
.font-bold { font-weight: 700; }
.link-value { color: #2D6A4F; cursor: pointer; }
.link-value:hover { text-decoration: underline; }
.font-mono { font-family: monospace; }

.status-cards-col {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.policy-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.date-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
}
.days-remaining {
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.days-good { background: #ECFDF5; color: #047857; }
.days-warning { background: #FFFBEB; color: #B45309; }
.days-expired { background: #FEF2F2; color: #B91C1C; }

.btn-change-date {
  padding: 6px 12px;
  background: #F3F4F6;
  color: #374151;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}
.btn-change-date:hover { background: #E5E7EB; color: #111827; }

.modal-sm-fixed { max-width: 400px; height: auto; max-height: none; }

.margin-top { margin-top: 24px; }

.btn-wash-action {
  margin-top: 4px;
  padding: 10px 16px;
  background: #0284C7;
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.15s ease;
}
.btn-wash-action:hover:not(:disabled) { background: #0369A1; }
.btn-wash-action:disabled { opacity: 0.6; cursor: not-allowed; }
.wash-hint { font-size: 12px; color: #9CA3AF; margin-top: 4px; }

.history-empty { text-align: center; padding: 24px 0; color: #9CA3AF; font-size: 13px; }
.table-scroll { overflow-x: auto; }
.history-table { width: 100%; border-collapse: collapse; }
.history-table th { text-align: left; font-size: 11.5px; font-weight: 700; color: #6B7280; padding: 8px 10px; border-bottom: 1px solid #E5E7EB; }
.history-table td { font-size: 13px; color: #1F2937; padding: 10px; border-bottom: 1px solid #F3F4F6; }
.current-badge { display: inline-block; padding: 2px 10px; background: #DCFCE7; color: #15803D; border-radius: 12px; font-size: 11px; font-weight: 700; }
.oil-snapshot-row { font-size: 11.5px; color: #4B5563; white-space: nowrap; }
.text-muted { color: #9CA3AF; }

/* Modal Styles */
.modal-dialog {
  border: none;
  border-radius: 20px;
  padding: 0;
  width: 90%;
  max-width: 640px;
  height: 92vh;
  max-height: 92vh;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  background: white;
  margin: auto;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.modal-dialog::backdrop {
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}
.car-modal-header {
  padding: 20px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #F3F4F6;
}
.header-badge-wrap { display: flex; align-items: center; gap: 12px; }
.header-badge-icon {
  width: 40px; height: 40px; border-radius: 12px; background: #ECFDF5;
  display: flex; align-items: center; justify-content: center;
}
.car-modal-title { font-size: 17px; font-weight: 700; color: #111827; }
.car-modal-sub { font-size: 12px; color: #6B7280; margin-top: 2px; }
.car-btn-close { background: none; border: none; font-size: 18px; color: #9CA3AF; cursor: pointer; }
.car-modal-header { flex-shrink: 0; }
.car-modal-form { padding: 24px; overflow-y: auto; flex: 1; }
.form-group { margin-bottom: 16px; width: 100%; box-sizing: border-box; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; width: 100%; box-sizing: border-box; }
.form-label { display: block; font-size: 12.5px; font-weight: 600; color: #374151; margin-bottom: 6px; }
.form-input {
  width: 100%; box-sizing: border-box; padding: 10px 14px; border: 1.5px solid #E5E7EB;
  border-radius: 10px; font-size: 14px; background: #FAFAFA; color: #111827; outline: none; line-height: 1.4;
}
.form-input:focus { border-color: #2D6A4F; background: white; box-shadow: 0 0 0 3.5px rgba(45,106,79,0.12); }
select.form-input {
  appearance: none; -webkit-appearance: none; -moz-appearance: none;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='%236B7280'><path fill-rule='evenodd' d='M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z' clip-rule='evenodd'/></svg>");
  background-repeat: no-repeat; background-position: right 12px center; background-size: 14px 14px;
  padding-right: 34px; cursor: pointer;
}
.status-select-fixed { height: 42px; }
.car-modal-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; }

/* Searchable instructor select */
.searchable-select { position: relative; }
.searchable-dropdown { position: absolute; top: calc(100% + 4px); left: 0; right: 0; background: white; border: 1.5px solid #E5E7EB; border-radius: 10px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); max-height: 200px; overflow-y: auto; z-index: 20; }
.searchable-option { padding: 9px 14px; font-size: 13.5px; color: #374151; cursor: pointer; }
.searchable-option:hover { background: #F3F4F6; }
.searchable-option.selected { background: #ECFDF5; color: #1B4332; font-weight: 600; }
.searchable-empty { padding: 10px 14px; font-size: 12.5px; color: #9CA3AF; text-align: center; }
.btn-cancel { padding: 10px 18px; border: 1px solid #D1D5DB; background: white; border-radius: 10px; font-weight: 600; font-size: 13px; color: #374151; cursor: pointer; }
.btn-submit { padding: 10px 22px; background: #2D6A4F; color: white; border-radius: 10px; font-weight: 600; font-size: 13.5px; border: none; cursor: pointer; }

/* Instructor assignment button + searchable select (dedicated modal) */
.btn-change-instructor {
  padding: 4px 10px;
  background: #F0FDF4;
  color: #1B4332;
  border: 1px solid #A7F3D0;
  border-radius: 8px;
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-change-instructor:hover { background: #DCFCE7; border-color: #6EE7B7; }

.search-select-container { position: relative; width: 100%; }
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
.search-select-trigger:hover { border-color: #9CA3AF; background: #F9FAFB; }
.search-select-trigger.is-open { border-color: #2D6A4F; box-shadow: 0 0 0 3px rgba(45, 106, 79, 0.12); }
.search-select-trigger.has-selected { padding: 4px 8px; border-color: #A7F3D0; background: #F0FDF4; }
.select-placeholder { display: flex; align-items: center; gap: 8px; font-size: 13.5px; color: #6B7280; }
.select-arrow-icon { color: #6B7280; transition: transform 0.2s ease; }
.select-arrow-icon.rotate { transform: rotate(180deg); }
.selected-user-card { display: flex; align-items: center; gap: 10px; width: 100%; }
.user-avatar-badge { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px; flex-shrink: 0; }
.avatar-inst { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
.selected-user-details { display: flex; flex-direction: column; flex: 1; overflow: hidden; text-align: left; }
.selected-user-name { font-size: 13px; font-weight: 600; color: #111827; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.selected-user-phone { font-size: 11px; color: #6B7280; }
.btn-remove-selection { background: none; border: none; color: #9CA3AF; font-size: 14px; cursor: pointer; padding: 4px 6px; border-radius: 6px; transition: all 0.15s; }
.btn-remove-selection:hover { background: #F3F4F6; color: #EF4444; }
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
}
.dropdown-search-wrap { padding: 2px; }
.dropdown-search-field { width: 100%; padding: 8px 12px; font-size: 13px; border: 1px solid #D1D5DB; border-radius: 8px; outline: none; transition: border-color 0.15s; box-sizing: border-box; }
.dropdown-search-field:focus { border-color: #2D6A4F; }
.dropdown-options-container { max-height: 180px; overflow-y: auto; display: flex; flex-direction: column; gap: 2px; }
.dropdown-option-row { display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 8px; cursor: pointer; transition: background 0.15s; text-align: left; }
.dropdown-option-row:hover { background: #F3F4F6; }
.dropdown-option-row.is-active { background: #ECFDF5; }
.dropdown-option-row.is-highlighted { background: #F3F4F6; }
.option-clear { color: #6B7280; font-weight: 500; font-size: 12.5px; justify-content: center; }
.opt-avatar { width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 11px; flex-shrink: 0; }
.opt-info { display: flex; flex-direction: column; flex: 1; }
.opt-name { font-size: 13px; font-weight: 600; color: #111827; }
.opt-phone { font-size: 11px; color: #6B7280; }
.opt-check { color: #059669; font-weight: 700; font-size: 14px; }
.dropdown-empty { padding: 12px; text-align: center; font-size: 12.5px; color: #9CA3AF; }

/* Image Zoom Modal */
.image-zoom-dialog { border: none; background: transparent; padding: 0; max-width: 90vw; max-height: 90vh; margin: auto; overflow: visible; }
.image-zoom-dialog::backdrop { background: rgba(0, 0, 0, 0.75); backdrop-filter: blur(5px); }
.image-zoom-content { position: relative; display: flex; align-items: center; justify-content: center; }
.image-zoom-close { position: absolute; top: -16px; right: -16px; width: 32px; height: 32px; border-radius: 50%; background: white; color: #111827; font-weight: 700; font-size: 14px; border: none; box-shadow: 0 4px 12px rgba(0,0,0,0.3); cursor: pointer; z-index: 10; display: flex; align-items: center; justify-content: center; }
.zoomed-img { max-width: 85vw; max-height: 85vh; border-radius: 14px; object-fit: contain; box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
</style>
